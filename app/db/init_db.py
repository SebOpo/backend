import os

from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.components import oauth, users, organizations
from app.core.config import settings


load_dotenv()

# TODO REWORK THIS SCRIPT

AID_WORKER_SCOPES = [
    "users:me",
    "users:edit",
    "locations:view",
    "locations:edit",
    "locations:create",
]


ORGANIZATIONAL_LEADER_SCOPES = [
    "users:me",
    "users:edit",
    "users:disable",
    "users:roles",
    "locations:view",
    "locations:edit",
    "locations:create",
    "organizations:view",
    "organizations:edit",
    "oauth:read",
    "changelogs:edit"
]


def init_db(db: Session) -> users.models.User:

    for default_scope in oauth.models.default_scopes:
        oauth.crud.scopes.get_or_create_scope(
            db=db,
            scope=oauth.schemas.OauthScope(
                module=default_scope.split(":")[0], scope=default_scope
            ),
        )

    admin_scopes = oauth.crud.scopes.get_all(db)

    admin_role = oauth.crud.roles.get_or_create_role(
        db=db,
        role=oauth.schemas.OauthRole(verbose_name="platform_administrator", authority=10),
        scope_list=admin_scopes,
    )

    admin_role.scopes = admin_scopes
    db.commit()

    org_leader_scopes = []

    for s in ORGANIZATIONAL_LEADER_SCOPES:
        scope = oauth.crud.scopes.get_scope_by_scope_string(db=db, scope_string=s)
        org_leader_scopes.append(scope)

    org_leader_role = oauth.crud.roles.get_or_create_role(
        db=db,
        role=oauth.schemas.OauthRole(
            verbose_name="organizational_leader",
            authority=2
        ),
        scope_list=org_leader_scopes
    )

    # TODO refactor.
    org_leader_role.scopes = org_leader_scopes
    db.commit()

    aid_worker_scopes = []

    for s in AID_WORKER_SCOPES:
        scope = oauth.crud.scopes.get_scope_by_scope_string(db=db, scope_string=s)
        aid_worker_scopes.append(scope)

    aid_worker_role = oauth.crud.roles.get_or_create_role(
        db=db,
        role=oauth.schemas.OauthRole(
            verbose_name="aid_worker",
            authority=1
        ),
        scope_list=aid_worker_scopes,
    )

    # TODO refactor this.
    aid_worker_role.scopes = aid_worker_scopes
    db.commit()

    # creating the "DIM" organization
    organization = organizations.crud.organizations.get_by_name(db, "DIM")
    if not organization:
        organization = organizations.crud.organizations.create(
            db,
            obj_in=organizations.schemas.OrganizationBase(name="DIM"),
        )

    # TODO find a way to remove this
    organization.disabled = False
    organization.activated = True
    db.commit()

    # creating first superuser
    user = users.crud.users.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        new_user = users.schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            organization=organization.id,
        )
        user = users.crud.create(db, obj_in=new_user, role="platform_administrator")

    if settings.ENV_TYPE == "test":
        aid_worker_user = users.crud.users.get_by_email(db, email=os.getenv("TEST_AID_WORKER_EMAIL"))
        if not aid_worker_user:
            new_aid_worker = users.schemas.UserCreate(
                email=os.getenv("TEST_AID_WORKER_EMAIL"),
                password=os.getenv("TEST_AID_WORKER_PASSWORD"),
                organization=organization.id
            )
            aid_worker = users.crud.create(db, obj_in=new_aid_worker, role="aid_worker")
        organizational_leader_user = users.crud.users.get_by_email(
            db, email=os.getenv("TEST_ORGANIZATIONAL_LEADER_EMAIL")
        )
        if not organizational_leader_user:
            new_organizational_leader = users.schemas.UserCreate(
                email=os.getenv("TEST_ORGANIZATIONAL_LEADER_EMAIL"),
                password=os.getenv("TEST_ORGANIZATIONAL_LEADER_PASSWORD"),
                organization=organization.id
            )
            organizational_leader = users.crud.create(
                db, obj_in=new_organizational_leader, role="organizational_leader"
            )

    return user
