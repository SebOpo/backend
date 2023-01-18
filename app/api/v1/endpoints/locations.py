from typing import Any, List
import os

from fastapi import APIRouter, Depends, HTTPException, Security, status, Response, UploadFile, File

import aiofiles

from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user
from app import schemas, models
from app.crud import crud_location as crud
from app.crud import crud_changelogs as logs_crud
from app.crud import crud_geospatial as geo_crud
from app.crud import crud_zones as zone_crud
from app.utils import geocoding
from app.core.config import settings
from app.utils.bulk_locations import upload_locations

router = APIRouter()


# TODO REMOVE ROUTE
@router.post('/create')
async def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)) -> Any:

    new_location = crud.create_location(db, obj_in=location)

    if not new_location:
        raise HTTPException(status_code=400, detail="Cannot create a location")

    return new_location.to_json()


@router.get('/search')
async def get_location(lat: float, lng: float, db: Session = Depends(get_db)) -> Any:

    location = crud.get_location_by_coordinates(db, lat, lng)

    if not location:
        raise HTTPException(status_code=400, detail="Not found")

    return location.to_json()


@router.post('/cord_search')
async def get_locations_by_coordinates(coordinates: schemas.TestLocationSearch, db: Session = Depends(get_db)) -> Any:

    # locations = crud.get_locations_in_range(db, coordinates.lat, coordinates.lng)
    #
    # return [location.to_json() for location in locations]

    markers = geo_crud.search_indexes_in_range(db, coordinates.lat, coordinates.lng, coordinates.zoom)

    print(f"Markers : {len(markers)}")

    return [marker.to_json() for marker in markers]


@router.get('/location-info', response_model=schemas.LocationOut)
async def get_location_info(location_id: int, db: Session = Depends(get_db)) -> Any:

    location = crud.get_location_by_id(db, location_id)

    if not location:
        raise HTTPException(status_code=400, detail="Not found")

    return location.to_json()


@router.get('/changelogs', response_model=List[schemas.ChangelogOut])
async def get_location_changelogs(location_id: int, db: Session = Depends(get_db)) -> Any:

    logs = logs_crud.get_changelogs(db, location_id)

    return logs


@router.post('/request-info')
async def request_location_review(
        location: schemas.LocationCreate,
        db: Session = Depends(get_db)
) -> Any:

    existing_location = crud.get_location_by_coordinates(db, location.lat, location.lng)
    if existing_location:
        raise HTTPException(
            status_code=400,
            detail="Review request for this location was already sent"
        )

    address = geocoding.reverse(location.lat, location.lng)
    if not address:
        raise HTTPException(status_code=400, detail="Cannot get the address of this location, please check you query")

    restricted_intersection = zone_crud.check_new_point_intersections(db, location.lng, location.lat)
    if restricted_intersection:
        raise HTTPException(status_code=403, detail="Locations in this area are restricted")

    location_to_review = crud.create_location_review_request(
        db,
        address=address,
        lat=location.lat,
        lng=location.lng
    )
    if not location_to_review:
        raise HTTPException(status_code=500, detail="Cannot connect to the database, please try again")

    return location_to_review.to_json()


# @router.post('/request-info')
# async def request_location_review(location: schemas.LocationCreate, db: Session = Depends(get_db)) -> Any:
#
#     existing_location = crud.get_location_by_coordinates(db, location.lat, location.lng)
#
#     if existing_location:
#         raise HTTPException(status_code=400, detail="Review request for this location was already sent")
#
#     location_to_review = crud.create_location_review_request(db, obj_in=location)
#
#     if not location_to_review:
#         raise HTTPException(status_code=500, detail="Cannot connect to the database, please try again")
#
#     return location_to_review.to_json()


@router.get('/pending-count')
async def get_pending_locations_count(db: Session = Depends(get_db),
                                      current_user=Security(get_current_active_user,
                                                            scopes=['locations:view'])) -> Any:

    return {
        "count": crud.get_locations_awaiting_reports_count(db)
    }


@router.get('/location-requests', response_model=List[schemas.LocationOut])
async def get_requested_locations(page: int = 1,
                                  limit: int = 20,
                                  user_lat: float = None,
                                  user_lng: float = None,
                                  db: Session = Depends(get_db),
                                  current_user: models.User = Security(get_current_active_user,
                                                                       scopes=['locations:view'])) -> Any:

    locations = crud.get_locations_awaiting_reports(db, limit, page - 1)

    return [location.to_json(user_lat, user_lng) for location in locations]


@router.put('/assign-location')
async def assign_location_report(location_id: int,
                                 db: Session = Depends(get_db),
                                 current_user: models.User = Security(get_current_active_user,
                                                                      scopes=['locations:edit'])) -> Any:

    location = crud.assign_report(db, current_user.id, location_id)
    if not location:
        raise HTTPException(status_code=400, detail="Location is already assigned")

    return location.to_json()


@router.put('/remove-assignment')
async def remove_report_assignment(location_id: int,
                                   db: Session = Depends(get_db),
                                   current_user: models.User = Security(get_current_active_user,
                                                                        scopes=['locations:edit'])) -> Any:
    location = crud.remove_assignment(db, location_id, current_user.id)
    if not location:
        raise HTTPException(status_code=400, detail="This location was already dismissed or does not belong to you")

    return location.to_json()


@router.get('/assigned-locations', response_model=List[schemas.LocationOut])
async def get_user_assigned_locations(db: Session = Depends(get_db),
                                      current_user: models.User = Security(get_current_active_user,
                                                                           scopes=['locations:view'])) -> Any:

    locations = crud.get_user_assigned_locations(db, current_user.id)
    return [location.to_json() for location in locations]


@router.put('/submit-report')
async def submit_location_report(reports: schemas.LocationReports,
                                 db: Session = Depends(get_db),
                                 current_user: models.User = Security(get_current_active_user,
                                                                      scopes=['locations:edit'])) -> Any:

    location = crud.submit_location_reports(db, obj_in=reports, user_id=current_user.id)

    if not location:
        raise HTTPException(status_code=400, detail='Cannot find the requested location')

    return location.to_json()


@router.delete('/remove-location')
async def remove_location(location_id: int,
                          db: Session = Depends(get_db),
                          current_user: models.User = Security(get_current_active_user,
                                                               scopes=['locations:delete'])) -> Any:

    # TODO place to archive?
    location = crud.delete_location(db, location_id=location_id)

    if location:
        raise HTTPException(status_code=400, detail='Cannot perform such operation')

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/recent-reports', response_model=List[schemas.LocationOut])
async def get_activity_feed(
        records: int = 10,
        db: Session = Depends(get_db)
) -> Any:

    locations = crud.get_activity_feed(db, records)

    return [location.to_json() for location in locations]


@router.post('/bulk-add')
async def bulk_add_locations(
    sheet_type: int,
    file: UploadFile = File(...),
    # current_user: models.User = Security(get_current_active_user,
    #                                      scopes=['locations:delete'])
) -> Any:

    if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        raise HTTPException(status_code=400, detail="Unsupported file format. Please verify what you are sending.")

    filepath = "app/datasets/{}".format(file.filename)

    if not os.path.exists('app/datasets'):
        os.makedirs('app/datasets')

    async with aiofiles.open(filepath, 'wb') as file_object:
        content = await file.read()
        await file_object.write(content)

    locations = await upload_locations(filepath, "excel")
    os.remove(filepath)

    return locations

    # filepath = f"app/datasets/{file.filename}"
    #
    # if not os.path.exists('app/datasets'):
    #     os.makedirs('app/datasets')
    #
    # async with aiofiles.open(filepath, "wb") as file_object:
    #     content = await file.read()
    #     await file_object.write(content)
    #
    # op_status = bulk_create(spreadsheet_path=filepath, sheet_type=sheet_type)
    #
    # if not op_status:
    #     raise HTTPException(status_code=400, detail=op_status)
    #
    # return Response(status_code=status.HTTP_201_CREATED)


# TODO REMOVE ENDPOINT ( TESTING ONLY )
@router.delete('/bulk-delete')
async def delete_all_locations(
        db: Session = Depends(get_db),
        current_user: models.User = Security(get_current_active_user,
                                             scopes=['locations:delete'])
) -> Any:

    if settings.ENV_TYPE != "test":
        raise HTTPException(status_code=403, detail="This endpoint is restricted.")

    crud.drop_locations(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
