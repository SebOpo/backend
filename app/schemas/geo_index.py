from pydantic import BaseModel, validator


class GeospatialRecord(BaseModel):

    id: int
    geohash: str
    location_id: int
    position = validator()

    class Config:
        orm_mode = True