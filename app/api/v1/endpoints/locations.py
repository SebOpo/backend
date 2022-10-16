from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Body, Security

from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user
from app import schemas, models
from app.crud import crud_location as crud
from app.crud import crud_changelogs as logs_crud

router = APIRouter()


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
async def get_locations_by_coordinates(coordinates: schemas.LocationSearch, db: Session = Depends(get_db)) -> Any:
    locations = crud.get_locations_in_range(db, coordinates.lat, coordinates.lng)

    return [location.to_json() for location in locations]


@router.get('/changelogs')
async def get_location_changelogs(location_id: int, db: Session = Depends(get_db)) -> Any:
    logs = logs_crud.get_changelogs(db, location_id)

    return logs


@router.post('/request-info')
async def request_location_review(location: schemas.LocationCreate, db: Session = Depends(get_db)) -> Any:
    existing_location = crud.get_location_by_coordinates(db, location.lat, location.lng)

    if existing_location:
        raise HTTPException(status_code=400, detail="Review request for this location was already sent")

    location_to_review = crud.create_location_review_request(db, obj_in=location)

    if not location_to_review:
        raise HTTPException(status_code=500, detail="Cannot connect to the database, please try again")

    return location_to_review.to_json()


@router.get('/pending-count')
async def get_pending_locations_count(db: Session = Depends(get_db),
                                      current_user=Security(get_current_active_user, scopes=['locations:view'])) -> Any:

    return {"count": crud.get_locations_awaiting_reports_count(db)}


@router.get('/location-requests', response_model=List[schemas.LocationOut])
async def get_requested_locations(page: int = 1,
                                  limit: int = 20,
                                  db: Session = Depends(get_db),
                                  current_user: models.User = Security(get_current_active_user,
                                                                       scopes=['locations:view'])) -> Any:
    locations = crud.get_locations_awaiting_reports(db, limit, page - 1)

    return [location.to_json() for location in locations]


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


@router.get('/assigned-locations', response_model=List[schemas.LocationAdmin])
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
