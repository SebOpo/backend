from typing import Optional, List

from sqlalchemy.orm import Session
from shapely import wkt

from app.models.zone import Zone
from app.utils.geocoding import check_intersection


def add_restricted_zone(db: Session, zone_type: int, zone_name: str, bbox: str):

    try:
        db_obj = Zone(
            zone_type=zone_type,
            bounding_box=bbox,
            verbose_name=zone_name
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    except Exception as e:
        print('Zone add exception: {}'.format(e))
        return None


def check_new_point_intersections(db: Session, lng: float, lat: float) -> bool:

    try:
        restricted_zones = db.query(Zone).all()

        for zone in restricted_zones:
            zone_geom = wkt.loads(zone.bounding_box)
            intersection = check_intersection(zone_geom, (lng, lat))
            if intersection:
                return True

        return False

    except Exception as e:
        print('Zone checking exception: {}'.format(e))
        return True


def get_zone_by_verbose_name(db: Session, zone_name: str) -> Zone:
    return db.query(Zone).filter(Zone.verbose_name == zone_name).first()


def get_all_restricted_zones(db: Session) -> List[Zone]:
    return db.query(Zone).all()


def allow_zone(db: Session, zone_id: int) -> Optional[Zone]:
    zone_to_delete = db.query(Zone).get(zone_id)
    if not zone_to_delete:
        return None

    db.delete(zone_to_delete)
    db.commit()
    return zone_to_delete
