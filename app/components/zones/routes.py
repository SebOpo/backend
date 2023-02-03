from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Security, status, Response
from sqlalchemy.orm import Session

from app.components.zones import schemas, crud
from app.api.dependencies import get_db, get_current_active_user
from app.utils import geocoding

router = APIRouter()


@router.post("/restrict")
async def restrict_zone(
    zone: schemas.ZoneBase,
    db: Session = Depends(get_db),
    current_user=Security(get_current_active_user, scopes=["zones:create"]),
) -> Any:

    existing_zone = crud.zones.get_zone_by_verbose_name(
        db,
        zone.verbose_name
    )
    if existing_zone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Such zone already exists"
        )

    geom = geocoding.get_bounding_box_by_region_name(zone.verbose_name)
    restricted_zone = crud.zones.create(
        db=db,
        obj_in=schemas.ZoneCreate(
            **zone.dict(),
            bounding_box=str(geom)
        )
    )

    return restricted_zone


@router.delete("/allow")
async def allow_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Security(get_current_active_user, scopes=["zones:edit"]),
) -> Any:

    result = crud.zones.delete(
        db=db,
        model_id=zone_id
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/zones")
async def get_restricted_zones(
    db: Session = Depends(get_db),
    current_user=Security(get_current_active_user, scopes=["zones:get"]),
) -> Any:

    zones = crud.zones.get_all(db)
    return zones
