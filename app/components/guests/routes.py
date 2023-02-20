from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.components import locations, geospatial, zones
from app.components.guests import crud, schemas
from app.core.config import settings
from app.utils import geocoding
from app.utils import sms_sender as sms
from app.utils.time_utils import utc_convert

router = APIRouter(prefix="/guest", tags=["guest-user"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/request-otp")
@limiter.limit("{}/hour".format(settings.OTP_HOUR_RATE_LIMIT))
async def request_otp_code(
    request: Request, phone_number: str, db: Session = Depends(get_db)
) -> Any:

    if not settings.EMAILS_ENABLED:
        raise HTTPException(
            status_code=400, detail="Cannot send an otp code, please try again later."
        )

    guest_user = crud.get_or_create(db, phone_number)

    otp_status = sms.send_otp(
        phone_number=phone_number,
        code_length=6,
        validity_period=settings.OTP_EXPIRE_MINUTES,
        brand_name=settings.PROJECT_NAME,
        source="Location request",
        language="en-US",
    )
    if not otp_status or otp_status["StatusCode"] != 200:
        raise HTTPException(
            status_code=400, detail="Cannot send an otp code, please try again later."
        )

    updated_guest_user = crud.new_otp_request(db, guest_user.id)

    return {
        "status": "success",
        "expiration_minutes": settings.OTP_EXPIRE_MINUTES,
        "expires_at": utc_convert(
            datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        ),
    }


@router.post("/request-location")
async def request_location_info_with_otp(
    request: Request,
    location_request: schemas.LocationRequestOtp,
    db: Session = Depends(get_db),
) -> Any:

    if not settings.EMAILS_ENABLED:
        raise HTTPException(
            status_code=400,
            detail="Cannot verify otp codes at the moment, please try again later.",
        )

    guest_user = crud.get_or_create(db, location_request.phone_number)

    otp_verification = sms.verify_otp(
        location_request.phone_number,
        location_request.otp,
        settings.PROJECT_NAME,
        "Location request",
    )

    if not otp_verification or not otp_verification["Valid"]:
        raise HTTPException(
            status_code=400, detail="Provided otp is not valid or expired"
        )

    existing_location = locations.crud.get_location_by_coordinates(
        db, location_request.lat, location_request.lng
    )

    if existing_location:
        raise HTTPException(
            status_code=400, detail="Review request for this location was already sent."
        )

    restricted_intersection = zones.crud.zones.check_new_point_intersections(
        db=db, lng=location_request.lng, lat=location_request.lat
    )

    if restricted_intersection:
        raise HTTPException(
            status_code=403, detail="Locations in this area are restricted."
        )

    address = geocoding.reverse(location_request.lat, location_request.lng)
    if not address:
        raise HTTPException(
            status_code=400,
            detail="Cannot get the address of this location, please check your coordinates.",
        )

    new_location = locations.crud.create(
        db=db,
        obj_in=locations.schemas.LocationRequest(
            **location_request.dict(),
            **address,
            requested_by=guest_user.id,
        ),
    )

    geo_index = geospatial.crud.geospatial_index.create(
        db=db,
        obj_in=geospatial.schemas.GeospatialRecordCreate(
            **(jsonable_encoder(new_location))
        ),
    )

    if not new_location:
        raise HTTPException(
            status_code=500,
            detail="Encountered an unexpected error, please try again later.",
        )

    return new_location.to_json()
