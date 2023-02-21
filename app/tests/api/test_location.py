from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.components.geospatial import crud as geo_crud
from app.components.locations.crud import locations
from app.components.locations.models import Location
from app.utils.populate_db import populate_reports


def test_add_new_location(
    client: TestClient,
    test_db: Session,
    superuser_token_headers: Dict[str, str],
) -> None:

    payload = {
        "lat": "49.2363517942551",
        "lng": "28.46728473547535",
        "street_number": "Test street",
        "address": "Test address",
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
    location = locations.get(db=test_db, model_id=added_location["id"])
    assert location.status == 3
    assert added_location["address"] == location.address
    geo_record = geo_crud.geospatial_index.search_index_by_location_id(test_db, location_id=location.id)
    assert geo_record.geohash


def test_request_location_info(
    client: TestClient, test_db: Session, sample_location_coordinates: Dict[str, str]
) -> None:

    r = client.post(
        f"{settings.API_V1_STR}/locations/request-info",
        json=sample_location_coordinates,
    )
    assert 200 <= r.status_code < 300

    requested_location = r.json()
    location = locations.get(db=test_db, model_id=requested_location["id"])
    assert location.status == 1
    assert requested_location["address"] == location.address
    geospatial_record = geo_crud.geospatial_index.search_index_by_location_id(
        test_db, location_id=location.id
    )
    assert geospatial_record
    assert geospatial_record.geohash
    #
    # location_crud.delete_location(test_db, location_id=location.id)


def test_get_location_by_coords(client: TestClient, test_db: Session) -> None:

    r = client.get(
        f"{settings.API_V1_STR}/locations/search?lat=49.24003079548452&lng=28.480316724096923"
    )
    assert 200 <= r.status_code < 300

    requested_location = r.json()
    assert requested_location
    #
    # location_crud.delete_location(test_db, location_id=sample_location["id"])


def test_pending_location_count(
    client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:

    r = client.get(
        f"{settings.API_V1_STR}/locations/pending-count",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300

    location_count = r.json()
    assert "count" in location_count
    assert location_count["count"] > 0

    # location_crud.delete_location(test_db, location_id=sample_location["id"])


def test_get_pending_locations(
    client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:

    # TODO testing with the user geolocation?
    r = client.get(
        f"{settings.API_V1_STR}/locations/location-requests",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300

    pending_locations = r.json()
    assert isinstance(pending_locations, list)
    assert len(pending_locations) > 0


def test_assign_location(
    client: TestClient,
    test_db: Session,
    superuser_token_headers: Dict[str, str],
    superuser_id: int,
    location: Location,
) -> None:

    r = client.put(
        f"{settings.API_V1_STR}/locations/assign-location?location_id={location.id}",
        headers=superuser_token_headers,
    )

    assert 200 <= r.status_code < 300
    assigned_location = r.json()

    assert assigned_location["reported_by"] == superuser_id
    assert assigned_location["status"] == 1

    # location_crud.delete_location(test_db, location_id=location.id)


def test_get_assigned_locations(
    client: TestClient,
    test_db: Session,
    superuser_token_headers: Dict[str, str],
    superuser_id: int,
    location: Location,
) -> None:

    r = client.get(
        f"{settings.API_V1_STR}/locations/assigned-locations",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    assigned_locations = r.json()

    # Checking that all the received locations are actually assigned to the same user
    for location in assigned_locations:
        assert location["reported_by"] == superuser_id
        assert location["status"] == 1

    # location_crud.delete_location(test_db, location_id=sample_location["id"])


def test_remove_assigned_location(
    client: TestClient,
    test_db: Session,
    superuser_token_headers: Dict[str, str],
    location: Location,
) -> None:

    r = client.put(
        f"{settings.API_V1_STR}/locations/assign-location?location_id={location.id}",
        headers=superuser_token_headers,
    )

    r = client.put(
        f"{settings.API_V1_STR}/locations/remove-assignment?location_id={location.id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300

    pending_location = r.json()
    assert pending_location["reported_by"] is None
    assert pending_location["report_expires"] is None


def test_submit_location_report(
    client: TestClient,
    test_db: Session,
    superuser_token_headers: Dict[str, str],
    location: Location,
    superuser_id: int,
) -> None:

    r = client.get(
        f"{settings.API_V1_STR}/locations/location-requests",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    pending_locations = r.json()
    assert pending_locations

    random_reports = {
        "reports": populate_reports(),
        "location_id": location.id
    }

    r = client.put(
        f"{settings.API_V1_STR}/locations/submit-report",
        json=random_reports,
        headers=superuser_token_headers,
    )

    assert 200 <= r.status_code < 300

    reported_location = r.json()
    assert reported_location
    assert reported_location["status"] == 3
    assert reported_location["reports"]
    assert reported_location["reported_by"] == superuser_id
    assert reported_location["report_expires"] is None

    # location_crud.delete_location(test_db, location_id=sample_location['id'])


def test_get_location_info(
    client: TestClient, test_db: Session, location: Location
) -> None:

    r = client.get(
        f"{settings.API_V1_STR}/locations/location-info?location_id={location.id}"
    )
    assert 200 <= r.status_code < 300
    requested_location = r.json()

    assert requested_location
    assert requested_location["reports"]
    assert requested_location["status"] == 3


def test_request_location_without_valid_address(
    client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:

    # create a sample location somewhere near Lviv
    payload = {"lat": 50.0111909, "lng": 24.0506995}
    r = client.post(f"{settings.API_V1_STR}/locations/request-info", json=payload)
    assert 200 <= r.status_code < 300

    requested_location = r.json()
    assert requested_location["address"] is None
    assert requested_location["street_number"] is None

    # submit the reports with the updated location data
    random_reports = {
        "reports": populate_reports(),
        "location_id": requested_location["id"],
        "street_number": "1",
        "address": "Test street"
    }

    r = client.put(
        f"{settings.API_V1_STR}/locations/submit-report",
        json=random_reports,
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300

    updated_location = r.json()
    assert updated_location["address"] == "Test street"
    assert updated_location["street_number"] == "1"
    assert updated_location["status"] == 3


def test_get_recent_location_reports(
        client: TestClient, test_db: Session
) -> None:

    r = client.get(f'{settings.API_V1_STR}/locations/recent-reports')
    assert 200 <= r.status_code < 300

    recent_reports = r.json()
    assert isinstance(recent_reports, list)
    assert len(recent_reports) <= 10
