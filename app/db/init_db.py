from sqlalchemy.orm import Session

from app.crud import crud_user as crud
from app.crud import crud_organizations as org_crud
from app.models import User
from app.core.config import settings
from app.models import oauth
from app.crud.crud_oauth import scopes, roles
from app import schemas


AID_WORKER_SCOPES = [
    "users:me",
    "users:edit",
    "locations:view",
    "locations:edit"
]


def init_db(db: Session) -> User:

    for default_scope in oauth.default_scopes:
        scopes.get_or_create_scope(
            db=db,
            scope=schemas.OauthScope(
               module=default_scope.split(':')[0],
               scope=default_scope
            )
        )

    admin_scopes = scopes.get_all(db)

    roles.get_or_create_role(
        db=db,
        role=schemas.OauthRole(
            verbose_name="platform_administrator"
        ),
        scope_list=admin_scopes
    )

    aid_worker_scopes = []

    for s in AID_WORKER_SCOPES:
        scope = scopes.get_scope_by_scope_string(
            db=db,
            scope_string=s
        )
        aid_worker_scopes.append(scope)

    roles.get_or_create_role(
        db=db,
        role=schemas.OauthRole(
            verbose_name="aid_worker",
        ),
        scope_list=aid_worker_scopes
    )

    # creating the "DIM" organization
    organization = org_crud.get_by_name(db, "DIM")
    if not organization:
        organization = org_crud.create(db, obj_in=schemas.OrganizationBase(name="DIM"))

    # creating first superuser
    user = crud.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        new_user = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            organization=organization.id
        )
        user = crud.create(db, obj_in=new_user, role="platform_administrator")

    return user
