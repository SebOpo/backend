from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.utils.populate_db import populate_reports


def test_get_location_changelogs(
    client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:

    payload = {
        "lat": "49.2363517942444",
        "lng": "28.46728473547444",
        "street_number": 1,
        "address": "Test changelog",
        "city": "Test city",
        "country": "Ukraine",
        "index": 21000,
        "reports": populate_reports(),
    }

    r = client.post(
        f"{settings.API_V1_STR}/locations/add",
        json=payload,
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    added_location = r.json()

    r = client.get(
        f"{settings.API_V1_STR}/locations/changelogs?location_id={added_location['id']}"
    )
    assert 200 <= r.status_code < 300
    location_changelogs = r.json()

    assert location_changelogs
    for log in location_changelogs:
        assert log["new_flags"]

