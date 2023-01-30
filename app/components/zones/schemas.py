from pydantic import BaseModel


class ZoneBase(BaseModel):
    zone_type: int
    verbose_name: str


class ZoneCreate(ZoneBase):
    bounding_box: str


class ZoneOut(ZoneBase):
    id: int
    bounding_box: str

    class Config:
        orm_mode = True
