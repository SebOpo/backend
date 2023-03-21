from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.components import users
from app.components.organizations import crud
from app.core.config import settings


def test_create_organization(
    client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:
    payload = {"name": "TestOrg"}

    r = client.post(
        f"{settings.API_V1_STR}/organizations/create",
        json=payload,
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300

    created_organization = r.json()
    assert created_organization
    organization = crud.organizations.get(test_db, model_id=created_organization["id"])
    assert organization.name == created_organization["name"]


def test_add_new_organization(
    client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:
    payload = {
        "name": "SampleOrg",
        "emails": ["someemail@test.com", "someotheremail@test.com"],
    }

    r = client.post(
        f"{settings.API_V1_STR}/organizations/add",
        json=payload,
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    # TODO modify this when we have our return value in endpoint
    db_org = crud.organizations.get_by_name(test_db, "SampleOrg")
    assert db_org
    assert db_org.disabled is False
    assert db_org.activated is False


def test_edit_organization(
    client: TestClient,
    test_db: Session,
    superuser_token_headers: Dict[str, str],
    master_organization_id: int,
) -> None:
    payload = {
        "description": "Master organization",
        "website": "https://dim.org",
        "country": "Ukraine",
        "city": "Kiev",
    }

    r = client.put(
        f"{settings.API_V1_STR}/organizations/{master_organization_id}/edit",
        json=payload,
        headers=superuser_token_headers,
    )

    assert 200 <= r.status_code < 300

    response = r.json()
    assert response["website"] == "https://dim.org"
    db_org = crud.organizations.get(test_db, model_id=response["id"])
    assert db_org.activated is True


def test_get_all_organizations(
    client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/organizations/all", headers=superuser_token_headers
    )
    assert 200 <= r.status_code < 300
    assert isinstance(r.json(), list)


def test_get_organization_by_id(
    client: TestClient,
    test_db: Session,
    superuser_token_headers: Dict[str, str],
    master_organization_id: int,
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/organizations/{master_organization_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300

    organization = r.json()
    assert organization["name"] == "DIM"
    assert organization["participants"]


def test_search_organization(
    client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/organizations/search?query=Di",
        headers=superuser_token_headers,
    )

    assert 200 <= r.status_code < 300

    response = r.json()
    assert response[0]["name"] == "DIM"


def test_remove_organization_member(
    client: TestClient,
    test_db: Session,
    superuser_token_headers: Dict[str, str],
    superuser_id: int,
    master_organization_id: int,
) -> None:
    r = client.put(
        f"{settings.API_V1_STR}/organizations/{master_organization_id}/remove?user_id={superuser_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300

    master_user = users.crud.users.get(test_db, model_id=superuser_id)
    assert master_user.organization is None

    # organization = r.json()
    # assert organization["participants"] == []


def test_invite_organization_members(
    client: TestClient,
    test_db: Session,
    superuser_token_headers: Dict[str, str],
    master_organization_id: int,
    superuser_id: int,
) -> None:
    payload = {"emails": [settings.FIRST_SUPERUSER]}

    r = client.put(
        f"{settings.API_V1_STR}/organizations/{master_organization_id}/invite",
        json=payload,
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300

    organization = r.json()
    assert organization["participants"]

    master_user = users.crud.users.get(test_db, model_id=superuser_id)
    assert master_user.organization == master_organization_id


def test_disable_organization(
    client: TestClient,
    test_db: Session,
    superuser_token_headers: Dict[str, str],
    superuser_id: int,
) -> None:
    test_org = crud.organizations.get_by_name(test_db, name="TestOrg")

    r = client.put(
        f"{settings.API_V1_STR}/organizations/toggle-activity/{test_org.id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    disabled_org = r.json()
    assert disabled_org["disabled"]


def test_delete_organization(
    client: TestClient, test_db: Session, superuser_token_headers: Dict[str, str]
) -> None:
    organization_to_delete = crud.organizations.get_by_name(test_db, "TestOrg")

    r = client.delete(
        f"{settings.API_V1_STR}/organizations/{organization_to_delete.id}",
        headers=superuser_token_headers,
    )

    assert r.status_code == 204
