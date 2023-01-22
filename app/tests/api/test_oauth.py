from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings


def test_get_all_oauth_roles(
        client: TestClient,
        test_db: Session,
        superuser_token_headers: Dict[str, str]
) -> None:

    r = client.get(
        f'{settings.API_V1_STR}/oauth/roles/all',
        headers=superuser_token_headers
    )

    assert 200 <= r.status_code < 300
    assert isinstance(r.json(), list)


def test_get_all_oauth_scopes(
        client: TestClient,
        test_db: Session,
        superuser_token_headers: Dict[str, str]
) -> None:

    r = client.get(
        f'{settings.API_V1_STR}/oauth/scopes/all',
        headers=superuser_token_headers
    )

    assert 200 <= r.status_code < 300
    assert isinstance(r.json(), list)

