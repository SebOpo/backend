import os
from typing import Any, List

import aiofiles
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Security,
    status,
    Response,
    UploadFile,
    File,
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user
from app.components import users, changelogs
from app.components.geospatial import schemas as geo_schemas
from app.components.geospatial.crud import geospatial_index
from app.components.locations import crud, schemas
from app.components.locations.crud import locations
from app.components.zones.crud import zones
from app.core.config import settings
from app.utils import geocoding
from app.utils.bulk_locations import upload_locations

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/add", response_model=schemas.LocationOut)
async def add_new_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: users.models.User = Security(
        get_current_active_user, scopes=["locations:create"]
    ),
) -> Any:
    # Checking if the new location does not intersect with restricted ones.
    restricted_intersection = zones.check_new_point_intersections(
        db=db, lat=location.lat, lng=location.lng
    )
    if restricted_intersection:
        raise HTTPException(
            status_code=403, detail="Locations in this area are restricted"
        )
    # Checking if the new location does not already exist
    existing_location = locations.get_location_by_coordinates(
        db=db, lat=location.lat, lng=location.lng
    )
    if existing_location:
        raise HTTPException(status_code=400, detail="Such location already exists")
    # Creating a location itself
    new_location = locations.create_new_location(
        db=db, location=location, reported_by=current_user
    )
    # Creating a geospatial index
    geo_index = geospatial_index.create(
        db=db,
        obj_in=geo_schemas.GeospatialRecordCreate(**(jsonable_encoder(new_location))),
    )
    # Adding location changelog record
    # TODO fix this weird naming
    changelog = changelogs.crud.changelogs.create(
        db=db,
        obj_in=changelogs.schemas.ChangeLogCreate(
            location_id=new_location.id,
            old_flags={},
            new_flags=new_location.reports,
            submitted_by=current_user.id,
        ),
    )
    # TODO ROLLBACK IF NONE ADDED
    return new_location.to_json()


@router.get("/search")
async def get_location(lat: float, lng: float, db: Session = Depends(get_db)) -> Any:
    location = locations.get_location_by_coordinates(db, lat, lng)

    if not location:
        raise HTTPException(status_code=400, detail="Not found")

    return location.to_json()


@router.post("/cord_search", response_model=List[geo_schemas.GeospatialRecordOut])
async def get_locations_by_coordinates(
    coordinates: schemas.LocationBase, db: Session = Depends(get_db)
) -> Any:
    markers = geospatial_index.search_indexes_in_range(
        db,
        coordinates.lat,
        coordinates.lng,
    )

    return markers


@router.get("/location-info", response_model=schemas.LocationOut)
async def get_location_info(location_id: int, db: Session = Depends(get_db)) -> Any:
    location = locations.get(db=db, model_id=location_id)

    if not location:
        raise HTTPException(status_code=400, detail="Not found")

    return location.to_json()


@router.post("/request-info", response_model=schemas.LocationOut)
async def request_location_review(
    location: schemas.LocationBase, db: Session = Depends(get_db)
) -> Any:
    existing_location = locations.get_location_by_coordinates(
        db, location.lat, location.lng
    )
    if existing_location:
        raise HTTPException(
            status_code=400, detail="Review request for this location was already sent"
        )

    restricted_intersection = zones.check_new_point_intersections(
        db=db, lng=location.lng, lat=location.lat
    )
    if restricted_intersection:
        raise HTTPException(
            status_code=403, detail="Locations in this area are restricted"
        )

    address = geocoding.reverse(location.lat, location.lng)
    if not address:
        raise HTTPException(
            status_code=400,
            detail="Cannot get the address of this location, please check you query",
        )

    new_location = locations.create(
        db=db,
        obj_in=schemas.LocationRequest(
            **location.dict(),
            **address,
        ),
    )

    geo_index = geospatial_index.create(
        db=db,
        obj_in=geo_schemas.GeospatialRecordCreate(**(jsonable_encoder(new_location))),
    )

    return new_location.to_json()


@router.get("/pending-count")
async def get_pending_locations_count(
    db: Session = Depends(get_db),
    current_user=Security(get_current_active_user, scopes=["locations:view"]),
) -> Any:
    return {"count": locations.get_locations_awaiting_reports_count(db)}


@router.get("/location-requests", response_model=List[schemas.LocationOut])
async def get_requested_locations(
    search_params: schemas.PendingLocationSearch = Depends(),
    db: Session = Depends(get_db),
    current_user=Security(get_current_active_user, scopes=["locations:view"]),
) -> Any:
    location_list = locations.get_locations_awaiting_reports(
        db, **search_params.dict(exclude={"user_lat", "user_lng"})
    )

    return [
        location.to_json(search_params.user_lat, search_params.user_lng)
        for location in location_list
    ]


@router.put("/assign-location")
async def assign_location_report(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: users.models.User = Security(
        get_current_active_user, scopes=["locations:edit"]
    ),
) -> Any:
    location = locations.assign_report(
        db, user_id=current_user.id, location_id=location_id
    )
    if not location:
        raise HTTPException(status_code=400, detail="Location is already assigned")

    return location.to_json()


@router.put("/remove-assignment")
async def remove_report_assignment(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: users.models.User = Security(
        get_current_active_user, scopes=["locations:edit"]
    ),
) -> Any:
    location = locations.remove_assignment(
        db, location_id=location_id, user=current_user
    )
    if not location:
        raise HTTPException(
            status_code=400,
            detail="This location was already dismissed or does not belong to you",
        )

    return location.to_json()


@router.get("/assigned-locations", response_model=List[schemas.LocationOut])
async def get_user_assigned_locations(
    db: Session = Depends(get_db),
    current_user: users.models.User = Security(
        get_current_active_user, scopes=["locations:view"]
    ),
) -> Any:
    location_list = locations.get_user_assigned_locations(db, user_id=current_user.id)
    return [location.to_json() for location in location_list]


@router.put("/submit-report")
async def submit_location_report(
    reports: schemas.LocationUpdate,
    db: Session = Depends(get_db),
    current_user: users.models.User = Security(
        get_current_active_user, scopes=["locations:edit"]
    ),
) -> Any:
    location = crud.locations.submit_location_reports(
        db, obj_in=reports, user=current_user
    )

    if not location:
        raise HTTPException(
            status_code=400, detail="Cannot find the requested location"
        )

    return location.to_json()


@router.delete("/remove-location")
async def remove_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user=Security(get_current_active_user, scopes=["locations:delete"]),
) -> Any:
    # TODO place to archive?
    location = locations.delete(db=db, model_id=location_id)

    if location:
        raise HTTPException(status_code=400, detail="Cannot perform such operation")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/recent-reports", response_model=List[schemas.LocationOut])
async def get_activity_feed(records: int = 10, db: Session = Depends(get_db)) -> Any:
    location_list = crud.locations.get_activity_feed(db, records)

    return [location.to_json() for location in location_list]


@router.post("/bulk-add")
async def bulk_add_locations(
    file: UploadFile = File(...),
    # current_user: models.User = Security(get_current_active_user,
    #                                      scopes=['locations:delete'])
) -> Any:
    if (
        file.content_type
        != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please verify what you are sending.",
        )

    filepath = "app/datasets/{}".format(file.filename)

    if not os.path.exists("app/datasets"):
        os.makedirs("app/datasets")

    async with aiofiles.open(filepath, "wb") as file_object:
        content = await file.read()
        await file_object.write(content)

    location_list = await upload_locations(filepath, "excel")
    os.remove(filepath)

    return location_list


# TODO REMOVE ENDPOINT ( TESTING ONLY )
@router.delete("/bulk-delete")
async def delete_all_locations(
    db: Session = Depends(get_db),
    current_user=Security(get_current_active_user, scopes=["locations:delete"]),
) -> Any:
    if settings.ENV_TYPE != "test":
        raise HTTPException(status_code=403, detail="This endpoint is restricted.")

    crud.locations.drop_locations(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
