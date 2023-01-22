from typing import Dict, Optional

from pydantic import BaseModel, validator


class GeospatialRecord(BaseModel):

    id: int
    location_id: int
    lat: float
    lng: float
    position: Optional[Dict]
    status: int

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
