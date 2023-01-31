import logging
from datetime import datetime, timedelta
from typing import List, Any, Optional, Dict

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.components import users
from app.components.changelogs.crud import create_changelog
from app.components.geospatial.crud import create_index
from app.components.geospatial.models import GeospatialIndex
from app.components.locations import schemas
from app.components.locations.models import Location
from app.core.base_crud import CRUDBase
from app.core.config import settings

logger = logging.getLogger(settings.PROJECT_NAME)


class CRUDLocation(
    CRUDBase[Location, schemas.LocationRequest, schemas.LocationReports]
):
    def create_new_location(
        self,
        db: Session,
        *,
        location: schemas.LocationCreate,
        reported_by: users.models.User
    ) -> Location:

        try:
            db_obj = self.model(**(jsonable_encoder(location)))
            db_obj.status = 3
            db_obj.reported_by = reported_by.id
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

        except Exception as e:
            logger.error(
                "Cannot add a new location. Error: {}, Payload: {}".format(e, location)
            )
            raise HTTPException(
                status_code=500, detail="Cannot add a new location at the moment."
            )

        return db_obj

    def get_location_by_coordinates(
        self, db: Session, lat: float, lng: float
    ) -> Location:
        return (
            db.query(self.model)
            .filter(self.model.lat == lat, self.model.lng == lng)
            .first()
        )

    def get_locations_awaiting_reports_count(self, db: Session) -> int:
        return (
            db.query(self.model)
            .filter(self.model.status == 1, self.model.reported_by == None)
            .count()
        )

    def get_locations_awaiting_reports(
        self, db: Session, limit: int = 20, skip: int = 0
    ) -> List[Location]:
        return (
            db.query(self.model)
            .filter(self.model.status == 1, self.model.reported_by == None)
            .order_by(desc(self.model.created_at))
            .limit(limit)
            .offset(skip * limit)
            .all()
        )

    def assign_report(
        self, db: Session, user_id: int, location_id: int
    ) -> Optional[Location]:
        location = db.query(self.model).get(location_id)

        if location.reported_by:
            return None

        location.reported_by = user_id
        location.report_expires = datetime.now() + timedelta(days=1)

        user = db.query(users.models.User).get(user_id)
        user.last_activity = datetime.now()

        db.commit()
        db.refresh(location)
        return location

    def remove_assignment(
        self, db: Session, location_id: int, user: users.models.User
    ) -> Optional[Location]:
        location = db.query(self.model).get(location_id)

        if location.reported_by != user.id or not location.reported_by:
            return None

        location.reported_by = None
        location.report_expires = None

        user.last_activity = datetime.now()

        db.commit()
        db.refresh(location)
        return location

    def get_user_assigned_locations(self, db: Session, user_id: int) -> List[Location]:
        return (
            db.query(self.model)
            .filter(self.model.reported_by == user_id, self.model.status == 1)
            .all()
        )


locations = CRUDLocation(Location)


def submit_location_reports(
    db: Session, *, obj_in: schemas.LocationReports, user_id: int
) -> Any:
    location = db.query(Location).get(obj_in.location_id)

    if not location:
        return None

    # if not location.address:
    if obj_in.address:
        location.address = obj_in.address

    # if not location.street_number:
    if obj_in.street_number:
        location.street_number = obj_in.street_number

    if obj_in.city:
        location.city = obj_in.city

    if obj_in.index:
        location.index = obj_in.index

    reports = {
        "buildingCondition": obj_in.buildingCondition,
        "electricity": obj_in.electricity,
        "carEntrance": obj_in.carEntrance,
        "water": obj_in.water,
        "fuelStation": obj_in.fuelStation,
        "hospital": obj_in.hospital,
    }

    old_reports = location.reports
    new_reports = reports

    location.reports = reports

    # TODO confirmation for this?

    # update location record
    location.status = 3
    location.report_expires = None
    location.reported_by = user_id

    # update
    index_record = (
        db.query(GeospatialIndex)
        .filter(GeospatialIndex.location_id == obj_in.location_id)
        .first()
    )
    index_record.status = 3

    user = db.query(users.models.User).get(user_id)
    user.last_activity = datetime.now()

    db.commit()
    db.refresh(location)

    changelog = create_changelog(
        db, location_id=location.id, old_object=old_reports, new_object=new_reports
    )

    # TODO rollback strategy if no changelog was created

    return location


def get_activity_feed(db: Session, records: int = 10) -> List[Location]:
    return (
        db.query(Location)
        .filter(Location.status == 3)
        .order_by(desc(Location.created_at))
        .limit(records)
    )


def bulk_insert_locations(db: Session, locations: List[Dict]) -> Dict:
    added_locations = []
    exceptions = []

    reporting_user = (
        db.query(users.models.User)
        .filter(users.models.User.email == settings.FIRST_SUPERUSER)
        .first()
    )

    for location in locations:
        try:
            db_obj = Location(
                address=location.get("address"),
                index=location.get("postcode"),
                lat=location.get("lat"),
                lng=location.get("lng"),
                country=location.get("country"),
                city=location.get("city"),
                status=3,
                reports=location.get("reports"),
                street_number=location.get("street_number", None),
            )

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

            index = create_index(
                db,
                location_id=db_obj.id,
                lat=db_obj.lat,
                lng=db_obj.lng,
                status=db_obj.status,
            )

            submit_location_reports(
                db,
                obj_in=schemas.LocationReports(
                    location_id=db_obj.id, **location.get("reports")
                ),
                user_id=reporting_user.id,
            )
            added_locations.append(db_obj)

        except Exception as e:
            print(e)
            exceptions.append(
                {"location": location, "code": "DATABASE_ERROR", "detail": e}
            )

    return {"added": added_locations, "unprocessed": exceptions}


def drop_locations(db: Session):
    try:
        db.query(Location).delete()
        db.commit()
        return None

    except Exception as e:
        print(e)
        return
