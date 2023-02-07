from sqlalchemy.orm import Session

from app.components import oauth, users, organizations
from app.core.config import settings

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
    "locations:view",
    "locations:edit",
    "locations:create",
    "organizations:view",
    "organizations:edit",
    "oauth:read",
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

    oauth.crud.roles.get_or_create_role(
        db=db,
        role=oauth.schemas.OauthRole(verbose_name="platform_administrator"),
        scope_list=admin_scopes,
    )

    org_leader_scopes = []

    for s in ORGANIZATIONAL_LEADER_SCOPES:
        scope = oauth.crud.scopes.get_scope_by_scope_string(db=db, scope_string=s)
        org_leader_scopes.append(scope)

    org_leader_role = oauth.crud.roles.get_or_create_role(
        db=db,
        role=oauth.schemas.OauthRole(
            verbose_name="organizational_leader",
        ),
        scope_list=org_leader_scopes
    )

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

    # creating first superuser
    user = users.crud.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        new_user = users.schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            organization=organization.id,
        )
        user = users.crud.create(db, obj_in=new_user, role="platform_administrator")

    return user
