import logging

from shapely import wkt
from sqlalchemy.orm import Session

from app.components.zones import schemas, models
from app.components.zones.models import Zone
from app.core.base_crud import CRUDBase
from app.core.config import settings
from app.utils.geocoding import check_intersection

logger = logging.getLogger(settings.PROJECT_NAME)


class CRUDZones(CRUDBase[models.Zone, schemas.ZoneBase, schemas.ZoneOut]):
    def check_new_point_intersections(
        self, db: Session, lng: float, lat: float
    ) -> bool:
        try:
            restricted_zones = db.query(self.model).all()

            for zone in restricted_zones:
                zone_geom = wkt.loads(zone.bounding_box)
                intersection = check_intersection(zone_geom, (lng, lat))
                if intersection:
                    return True

            return False

        except Exception as e:
            logger.error("Zone checking exception: {}".format(e))
            return True

    def get_zone_by_verbose_name(self, db: Session, zone_name: str) -> Zone:
        return db.query(self.model).filter(self.model.verbose_name == zone_name).first()


zones = CRUDZones(Zone)
