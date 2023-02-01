from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, validator
from typing_extensions import TypedDict

from app.components import reports, geocoding
from app.utils.validators import convert_to_utc


# TODO LocationOut class with typed dict position (check to_json location method)


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
    reports: Reports


class LocationUpdate(BaseModel):
    location_id: int
    street_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    index: Optional[int] = None
    reports: Reports


class LocationRequest(LocationBase, geocoding.OSMGeocodingResults):
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


# TODO convert to dataclasses with default vals
class LocationReports(BaseModel):
    location_id: int
    street_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    index: Optional[int] = None
    buildingCondition: reports.schemas.BuildingReport
    electricity: reports.schemas.ElectricityReport
    carEntrance: reports.schemas.CarEntranceReport
    water: reports.schemas.WaterReport
    fuelStation: reports.schemas.FuelStationReport
    hospital: reports.schemas.HospitalReport
