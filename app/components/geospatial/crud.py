from typing import List

import pygeohash as pgh
from sqlalchemy.orm import Session

from app.components.geospatial import schemas
from app.components.geospatial.models import GeospatialIndex
from app.core.base_crud import CRUDBase


class CRUDGeospatial(
    CRUDBase[GeospatialIndex, schemas.GeospatialRecordCreate, schemas.GeospatialRecord]
):
    def search_indexes_in_range(
        self, db: Session, lat: float, lng: float
    ) -> List[GeospatialIndex]:

        # You can check the link below to understand the precision levels, for instance 2 is ≤ 1,250km X 625km
        # https://docs.quadrant.io/quadrant-geohash-algorithm

        geohash = pgh.encode(lat, lng, 2)
        query = "{}%".format(geohash)

        return db.query(self.model).filter(self.model.geohash.like(query)).all()

    def search_index_by_location_id(
        self, db: Session, location_id: int
    ) -> GeospatialIndex:
        return (
            db.query(self.model).filter(self.model.location_id == location_id).first()
        )


geospatial_index = CRUDGeospatial(GeospatialIndex)


def create_index(
    db: Session, location_id: int, lat: float, lng: float, status: int
) -> GeospatialIndex:

    db_obj = GeospatialIndex(
        location_id=location_id,
        # here we encode the location to maximum precision (12),
        # so no matter what zoom level we choose, we always have the full geohash string to compare
        geohash=pgh.encode(lat, lng, 12),
        lat=lat,
        lng=lng,
        status=status,
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return db_obj


def search_indexes_in_range(
    db: Session, lat: float, lng: float
) -> List[GeospatialIndex]:

    # Use zoom as precision points?
    # TODO check google api

    # You can check the link below to understand the precision levels, for instance 2 is ≤ 1,250km X 625km
    # https://docs.quadrant.io/quadrant-geohash-algorithm
    geohash = pgh.encode(lat, lng, 2)
    query = "{}%".format(geohash)

    return db.query(GeospatialIndex).filter(GeospatialIndex.geohash.like(query)).all()
