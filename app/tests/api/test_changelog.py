import logging
from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.components.users import crud as user_crud
from app.utils.populate_db import populate_reports

logger = logging.getLogger(settings.PROJECT_NAME)


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
        f"{settings.API_V1_STR}/changelogs/{added_location['id']}"
    )
    assert 200 <= r.status_code < 300
    location_changelogs = r.json()

    assert location_changelogs
    for log in location_changelogs:
        assert log["new_flags"]


def test_toggle_changelog_visibility(
        client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:

    payload = {
        "lat": "49.2363517942312",
        "lng": "28.46728473547312",
        "street_number": 1,
        "address": "Test changelog visibility",
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
        f"{settings.API_V1_STR}/changelogs/{added_location['id']}"
    )
    assert 200 <= r.status_code < 300
    location_changelogs = r.json()

    r = client.put(
        f"{settings.API_V1_STR}/changelogs/visibility/{location_changelogs[0]['id']}",
        headers=superuser_token_headers
    )

    assert 200 <= r.status_code < 300
    hidden_changelog = r.json()
    assert hidden_changelog["hidden"] is True

    r = client.put(
        f"{settings.API_V1_STR}/changelogs/visibility/{location_changelogs[0]['id']}",
        headers=superuser_token_headers
    )

    assert 200 <= r.status_code < 300
    visible_changelog = r.json()

    assert visible_changelog["hidden"] is False


def test_get_changelogs_by_admin_id(
        client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:

    admin_id = user_crud.users.get_by_email(test_db, email=settings.FIRST_SUPERUSER).id

    r = client.get(f"{settings.API_V1_STR}/changelogs/search/?admin_id={admin_id}")
    assert 200 <= r.status_code < 300
    changelog_list = r.json()
    assert isinstance(changelog_list, list)
    assert len(changelog_list)
    assert changelog_list[0]['user']["id"] == admin_id


def test_get_changelogs_by_org_id(
        client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:

    org_id = user_crud.users.get_by_email(test_db, email=settings.FIRST_SUPERUSER).organization

    r = client.get(f"{settings.API_V1_STR}/changelogs/search/?organization_id={org_id}")
    assert 200 <= r.status_code < 300
    changelog_list = r.json()
    assert isinstance(changelog_list, list)
    assert len(changelog_list)
    assert changelog_list[0]["user"]["organization"] == org_id


def test_get_changelogs_by_query_string(
        client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:

    r = client.get(f"{settings.API_V1_STR}/changelogs/search/?query=visibility")
    assert 200 <= r.status_code < 300
    changelog_list = r.json()
    assert isinstance(changelog_list, list)
    assert len(changelog_list)
    assert changelog_list[0]["location"]["address"] == "Test changelog visibility"
