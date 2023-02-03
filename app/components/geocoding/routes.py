import logging
from typing import Any

from fastapi import APIRouter, Security

from app.api.dependencies import get_current_active_user
from app.components.geocoding import schemas, enums
from app.core.config import settings
from app.utils import geocoding

router = APIRouter()
logger = logging.getLogger(settings.PROJECT_NAME)


@router.get("/reverse")
async def reverse_geocode_location(
    lat: float,
    lng: float,
    geocoder: enums.GeocoderEnum = "osm",
    current_user=Security(get_current_active_user, scopes=["locations:view"]),
) -> Any:

    address_info = geocoding.reverse(lat=lat, lng=lng, geocoding_service=geocoder)

    logger.debug("Geocoding results : {}".format(address_info))

    return schemas.OSMGeocodingResults(**address_info)
