from typing import Optional, Dict
from datetime import datetime

from pydantic import BaseModel, validator

from app.schemas import report
from app.schemas.validators import convert_to_utc

# TODO LocationOut class with typed dict position (check to_json location method)


class LocationBase(BaseModel):
    address: Optional[str] = None
    street_number: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    index: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class LocationCreate(LocationBase):
    lat: float
    lng: float


class LocationSearch(LocationBase):
    lat: Dict
    lng: Dict


class TestLocationSearch(BaseModel):
    lat: float
    lng: float
    zoom: Optional[int]


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

    _utc_datetime = validator('created_at', 'updated_at', 'report_expires', allow_reuse=True)(convert_to_utc)

    class Config:
        orm_mode = True


# TODO convert to dataclasses with default vals
class LocationReports(BaseModel):
    location_id: int
    street_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    index: Optional[int] = None
    buildingCondition: report.BuildingReport
    electricity: report.ElectricityReport
    carEntrance: report.CarEntranceReport
    water: report.WaterReport
    fuelStation: report.FuelStationReport
    hospital: report.HospitalReport

