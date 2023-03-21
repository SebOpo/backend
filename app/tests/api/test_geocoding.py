from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import settings


def test_reverse_geocode(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    sample_coords = {"lat": "49.2363517942551", "lng": "28.46728473547535"}

    r = client.get(
        f"{settings.API_V1_STR}/geocode/reverse?lat={sample_coords.get('lat')}&lng={sample_coords.get('lng')}",
        headers=superuser_token_headers,
    )

    assert 200 <= r.status_code < 300
    geocoded_location = r.json()
    assert "street_number" in geocoded_location
    assert "address" in geocoded_location
    assert "index" in geocoded_location
