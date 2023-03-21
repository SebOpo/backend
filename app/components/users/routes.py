from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Security, status, Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user
from app.components import organizations, changelogs, activity_logs, oauth
from app.components.users import schemas, models, crud
from app.core.config import settings
from app.utils.email_sender import send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=schemas.UserOut)
async def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_active_user: models.User = Security(
        get_current_active_user, scopes=["users:create"]
    ),
) -> Any:
    existing_user = crud.users.get_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User exists")

    new_user = crud.create(db, obj_in=user, role="aid_worker")

    if not new_user:
        raise HTTPException(
            status_code=500, detail="Cannot connect to db, please try again later"
        )

    # TODO EMAIL CONFIRMATION

    return new_user


@router.post("/invite", response_model=schemas.UserOut)
async def generate_invite_link(
    user: schemas.UserInvite,
    db: Session = Depends(get_db),
    current_active_user: models.User = Security(
        get_current_active_user, scopes=["users:create"]
    ),
) -> Any:
    # if user.email == settings.TEST_USER_EMAIL:
    #     raise HTTPException(status_code=400, detail='This email is reserved.')

    existing_user = crud.users.get_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User exists")

    new_user = crud.create_invite(
        db,
        obj_in=user,
        organization=organizations.crud.organizations.get(
            db, model_id=user.organization
        ),
        role_name="aid_worker",
    )

    if not new_user:
        raise HTTPException(
            status_code=500, detail="Cannot connect to db, please try again later"
        )

    if settings.EMAILS_ENABLED:
        send_email(
            to_addresses=[new_user.email],
            template_type="invite",
            link="{}/registration/?access_token={}".format(
                settings.DOMAIN_ADDRESS, new_user.registration_token
            ),
        )

    # TODO CHECK EMAIL STATUS
    # TODO REMOVE TOKEN FROM RESPONSE ( used for testing )

    return new_user


@router.get("/verify", response_model=schemas.UserOut)
async def verify_access_token(access_token: str, db: Session = Depends(get_db)) -> Any:
    invited_user = crud.users.verify_registration_token(db, access_token)
    if not invited_user:
        raise HTTPException(
            status_code=400, detail="Token is either not valid or expired."
        )
    return invited_user


@router.post("/confirm-registration", response_model=schemas.UserOut)
async def confirm_user_registration(
    access_token: str, user: schemas.UserCreate, db: Session = Depends(get_db)
) -> Any:
    new_user = crud.users.confirm_registration(
        db, access_token=access_token, obj_in=user
    )

    if not new_user:
        raise HTTPException(
            status_code=400,
            detail="Cannot create a new user. Please ask for invite link once more",
        )

    return new_user


@router.get("/me", response_model=schemas.UserOut)
async def get_me(
    current_user: models.User = Security(get_current_active_user, scopes=["users:me"])
) -> Any:
    return current_user


@router.put("/info", response_model=schemas.UserOut)
async def patch_user_info(
    updated_info: schemas.UserBase,
    current_user: models.User = Security(
        get_current_active_user, scopes=["users:edit"]
    ),
    db: Session = Depends(get_db),
) -> Any:
    updated_user = crud.users.update_info(
        db, obj_in=updated_info, user_email=current_user.email
    )

    return updated_user


@router.put("/password", response_model=schemas.UserOut)
async def change_user_password(
    updated_info: schemas.UserPasswordUpdate,
    current_user: models.User = Security(
        get_current_active_user, scopes=["users:edit"]
    ),
    db: Session = Depends(get_db),
) -> Any:
    updated_user = crud.users.update_password(
        db,
        user_email=current_user.email,
        old_password=updated_info.old_password,
        new_password=updated_info.new_password,
    )
    if not updated_user:
        raise HTTPException(
            status_code=400, detail="The provided password was incorrect."
        )

    return updated_user


@router.put("/password-reset")
async def reset_user_password(user_email: str, db: Session = Depends(get_db)) -> Any:
    user = crud.users.reset_password(db, user_email)
    if not user:
        raise HTTPException(status_code=400, detail="No such user.")

    if settings.EMAILS_ENABLED:
        send_email(
            [user.email],
            "password-renewal",
            link="{}/password-reset/?access_token={}".format(
                settings.DOMAIN_ADDRESS, user.password_renewal_token
            ),
        )

    # TODO CHECK FOR EMAIL STATUS
    # TODO REMOVE TOKEN FROM RESPONSE (used for testing)
    return user.password_renewal_token


@router.put("/confirm-reset")
async def confirm_user_password_reset(
    renewal_data: schemas.UserPasswordRenewal, db: Session = Depends(get_db)
) -> Any:
    user = crud.users.confirm_password_reset(
        db, renewal_data.access_token, renewal_data.new_password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="The token is either not valid or expired"
        )

    return Response(status_code=status.HTTP_200_OK)


@router.put("/toggle-activity", response_model=schemas.UserOut)
async def toggle_user_activity(
    user_id: int,
    current_user: models.User = Security(
        get_current_active_user, scopes=["users:disable"]
    ),
    db: Session = Depends(get_db),
) -> Any:
    user = crud.users.get(db, model_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")

    if (
        current_user.role != "platform_administrator"
        and current_user.organization != user.organization
    ):
        raise HTTPException(status_code=403, detail="Not allowed")

    updated_user = crud.users.toggle_user_is_active(db, user)
    # TODO return the number of updated changelogs.
    updated_changelogs = changelogs.crud.changelogs.bulk_toggle_changelog_visibility(
        db, visible=updated_user.is_active, user_id=updated_user.id
    )
    # TODO Find a smarter way to write descriptions
    activity_log = activity_logs.crud.logs.create(
        db,
        obj_in=activity_logs.schemas.ActivityLogBase(
            user_id=current_user.id,
            organization_id=user.organization,
            action_type=4,
            description=f'{user.email} was {"unblocked" if updated_user.is_active else "blocked"} by {current_user.email}',
        ),
    )

    return updated_user


@router.put("/change-role", response_model=schemas.UserOut)
async def change_user_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user=Security(get_current_active_user, scopes=["users:roles"]),
) -> Any:
    user = crud.users.get(db, model_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")

    new_role = oauth.crud.roles.get(db, model_id=role_id)
    user_role = oauth.crud.roles.get_role_by_name(db, role_name=user.role)
    current_user_role = oauth.crud.roles.get_role_by_name(
        db, role_name=current_user.role
    )
    if not new_role:
        raise HTTPException(status_code=400, detail="Bad params")

    if (
        new_role.authority > current_user_role.authority
        or user_role.authority > current_user_role.authority
    ):
        raise HTTPException(status_code=403, detail="Not allowed")

    changed_user = crud.users.change_user_role(db, user=user, new_role=new_role)
    # What happens to the logged in users? How do we force him to relogin?
    return changed_user


# TODO do we need this? Is the edit permission right for such operation (reserved route for tests)
@router.delete("/delete-me")
async def delete_me(
    current_user: models.User = Security(
        get_current_active_user, scopes=["users:edit"]
    ),
    db: Session = Depends(get_db),
) -> Any:
    deleted_user = crud.users.delete(db, model_id=current_user.id)

    if deleted_user:
        raise HTTPException(status_code=400, detail="Cannot perform such action")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
