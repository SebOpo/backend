from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, validator, root_validator
from typing_extensions import TypedDict

from app.components import reports, geocoding
from app.utils.validators import convert_to_utc


class LocationBase(BaseModel):
    lat: float
    lng: float


class Reports(TypedDict):
    buildingCondition: reports.schemas.BuildingReport
    electricity: reports.schemas.ElectricityReport
    carEntrance: reports.schemas.CarEntranceReport
    water: reports.schemas.WaterReport
    fuelStation: reports.schemas.FuelStationReport
    hospital: reports.schemas.HospitalReport


class LocationCreate(LocationBase):
    street_number: str
    address: str
    city: str
    country: str
    index: int
    region: Optional[str] = None
    reports: Reports


class BulkLocationCreate(LocationCreate):
    index: Optional[int] = None

    @root_validator(pre=True)
    def string_convert(cls, values):
        values["street_number"] = str(values["street_number"])
        return values


class LocationUpdate(BaseModel):
    location_id: int
    street_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    index: Optional[int] = None
    region: Optional[str] = None
    reports: Reports


class LocationRequest(LocationBase, geocoding.schemas.OSMGeocodingResults):
    status: int = 1
    requested_by: int = None


class LocationOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    address: Optional[str] = None
    organization_name: Optional[str] = None
    street_number: Optional[str] = None
    index: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    status: int
    country: Optional[str] = None
    position: Dict
    reports: Optional[Dict] = None
    distance: Optional[int] = None
    reported_by: Optional[int] = None
    report_expires: Optional[datetime] = None

    _utc_datetime = validator(
        "created_at", "updated_at", "report_expires", allow_reuse=True
    )(convert_to_utc)

    class Config:
        orm_mode = True


class PendingLocationSearch(BaseModel):
    date: Optional[Any] = None
    address_query: Optional[str] = None
    # region is going to be an int from the regions table?
    region: Optional[str] = None
    limit: int = 20
    page: int = 1
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None

    @validator("date", pre=True)
    def parse_date(cls, v):
        if not v or isinstance(v, datetime):
            return
        return datetime.fromtimestamp(int(v))

