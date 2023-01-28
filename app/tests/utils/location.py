from typing import Dict

from fastapi.testclient import TestClient

from app.models import Location
from app.crud import crud_location as crud
from app.core.config import settings


def get_location_by_coords(db, loc_coords: Dict) -> Location:
    return crud.get_location_by_coordinates(
        db,
        loc_coords.get('lat'),
        loc_coords.get('lng')
    )


def create_sample_location_request(client: TestClient) -> Dict[str, str]:

    payload = {
        "lat": 49.24003079548452,
        "lng": 28.480316724096923
    }

    r = client.post(f"{settings.API_V1_STR}/locations/request-info", json=payload)
    return r.json()

