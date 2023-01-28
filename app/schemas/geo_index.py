from typing import Dict, Optional

from pydantic import BaseModel, validator, root_validator
import pygeohash as pgh


class GeospatialRecord(BaseModel):
    lat: float
    lng: float
    status: int
    location_id: int


class GeospatialRecordCreate(GeospatialRecord):
    geohash: str

    @root_validator(pre=True)
    def convert_id(cls, values):
        """
        Because we do not create any geospatial indexes explicitly, it is easier to pass a mapping of a newly created
        location to this schema is a mapping. Because the mapped location os an orm object, its location id is just an
        "id" of the location model. We convert it here to correctly pass it to the create method.
        :param values: Initial passed values
        :return: the converted and ready to create payload.
        """
        values['location_id'] = values['id']
        return values

    @root_validator(pre=True)
    def make_geohash(cls, values):
        values['geohash'] = pgh.encode(values['lat'], values['lng'], 12)
        return values


class GeospatialRecordOut(GeospatialRecord):
    id: int
    position: Optional[Dict]

    @validator('position', pre=True, always=True)
    def set_position(cls, v: Dict, values: Dict):
        """
        The whole reason why this validator exists is to transform the lat and lng values into a format that is
        understandable by our JS Map provider without conversion on the frontend. All the markers there are presented
        as the "position" dictionary. The only problem with this approach is that we are duplicating the coordinates and
        cannot declare them as private attributes like - _lat or _lng because at this level pydantic won't show them.
        I am trying to find a better approach, like an __init__ method or a root validator, but for now, it is working
        like this.

        :param v: the position property. though we do not use it anywhere, it is required so we can pass our next param.
        :param values: the values of our pydantic model presented as json dict
        :return:
        """
        return {
            "lat": values.get('lat'),
            "lng": values.get('lng')
        }

    class Config:
        orm_mode = True
