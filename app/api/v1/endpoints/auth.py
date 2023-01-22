from typing import Any
from datetime import timedelta

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.schemas.token import Token
from app.core.config import settings
from app.core.security import create_access_token
from app.api.dependencies import get_db
from app.crud import crud_user as crud
from app.crud import crud_sessions

from app.crud.crud_oauth import roles

router = APIRouter()


@router.post('/login/token', response_model=Token)
async def login_user(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    # Base Oauth2 Form only has 2 fields, username and password, so we are using email here,
    # but passing it as a username.

    user = crud.authenticate(
        db=db,
        email=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    user_role = roles.get_role_by_name(
        db=db,
        role_name=user.role
    )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        subject=user.id,
        scopes=[s.scope for s in user_role.scopes],
        expires_delta=access_token_expires
    )

    # TODO
    # session = crud_sessions.create(db, user_id=user.id, access_token=access_token)

    if not access_token:  # or not session
        raise HTTPException(status_code=500, detail="Cannot authenticate user. Please try again later")

    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }
