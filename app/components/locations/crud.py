import logging
from datetime import datetime, timedelta
from typing import List, Any, Optional, Dict

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.components import users, changelogs
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

    def submit_location_reports(
        self, db: Session, obj_in: schemas.LocationUpdate, user: users.models.User
    ) -> Any:
        location = self.get(db, model_id=obj_in.location_id)
        if not location:
            return None
        old_reports = location.reports
        location_data = jsonable_encoder(location)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in location_data:
            if field in update_data:
                setattr(location, field, update_data[field])

        location.status = 3
        location.report_expires = None
        location.reported_by = user.id
        user.last_activity = datetime.utcnow()

        index_record = (
            db.query(GeospatialIndex)
                .filter(GeospatialIndex.location_id == obj_in.location_id)
                .first()
        )
        index_record.status = 3

        db.commit()
        db.refresh(location)

        # TODO fix this weird naming
        changelog = changelogs.crud.changelogs.create(
            db=db,
            obj_in=changelogs.schemas.ChangeLogCreate(
                location_id=location.id,
                old_flags=old_reports,
                new_flags=obj_in.reports,
                submitted_by=user.id
            )
        )

        return location

    def get_activity_feed(self, db: Session, records: int = 10) -> List[Location]:
        return (
            db.query(self.model)
                .filter(self.model.status == 3)
                .order_by(desc(self.model.created_at))
                .limit(records)
        )

    def bulk_insert_locations(self, db: Session, location_list: List[Dict]) -> Dict:
        from app.components.geospatial.crud import geospatial_index
        from app.components.geospatial.schemas import GeospatialRecordCreate
        added_locations = []
        exceptions = []

        reporting_user = (
            db.query(users.models.User)
                .filter(users.models.User.email == settings.FIRST_SUPERUSER)
                .first()
        )

        for location in location_list:
            try:
                db_obj = self.create_new_location(
                    db=db,
                    location=schemas.BulkLocationCreate(**location),
                    reported_by=reporting_user
                )

                index = geospatial_index.create(
                    db=db,
                    obj_in=GeospatialRecordCreate(**(jsonable_encoder(db_obj)))
                )

                self.submit_location_reports(
                    db,
                    obj_in=schemas.LocationUpdate(
                        location_id=db_obj.id, reports=db_obj.reports
                    ),
                    user=reporting_user,
                )
                added_locations.append(db_obj)

            except Exception as e:
                print(e)
                exceptions.append(
                    {"location": location, "code": "DATABASE_ERROR", "detail": e}
                )

        return {"added": added_locations, "unprocessed": exceptions}

    def drop_locations(self, db: Session):
        try:
            db.query(self.model).delete()
            db.commit()
            return None

        except Exception as e:
            print(e)
            return


locations = CRUDLocation(Location)
