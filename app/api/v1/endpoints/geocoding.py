from typing import Any
import logging

from fastapi import APIRouter, Security

from app import schemas, models
from app.api.dependencies import get_current_active_user
from app.utils import geocoding
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(settings.PROJECT_NAME)


@router.get('/reverse')
async def reverse_geocode_location(
        lat: float,
        lng: float,
        geocoder: schemas.GeocoderEnum = "osm",
        current_user: models.User = Security(
            get_current_active_user,
            scopes=['locations:view']
        )
) -> Any:

    address_info = geocoding.reverse(
        lat=lat,
        lng=lng,
        geocoding_service=geocoder
    )

    logger.debug('Geocoding results : {}'.format(address_info))

    return schemas.OSMGeocodingResults(**address_info)
