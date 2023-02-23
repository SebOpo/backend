from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING

from sqlalchemy.orm import Session

from app.components import oauth
from app.components.users.models import User
from app.components.users.schemas import UserCreate, UserBase, UserInvite
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.base_crud import CRUDBase

if TYPE_CHECKING:
    from app.components import organizations


class CRUDUser(
    CRUDBase[User, UserCreate, UserBase]
):

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(self.model).filter(self.model.email == email).first()

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:

        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def update_info(
            self, db: Session, *, obj_in: UserBase, user_email: str
    ) -> Optional[User]:
        user = self.get_by_email(db, email=user_email)
        if not user:
            return None

        data_to_update = obj_in.dict(exclude_unset=True)
        for field in data_to_update:
            setattr(user, field, data_to_update[field])

        db.commit()
        db.refresh(user)
        return user

    def verify_registration_token(self, db: Session, access_token: str) -> Optional[User]:
        invited_user = (
            db.query(self.model).filter(self.model.registration_token == access_token).first()
        )

        if not invited_user or datetime.now() > invited_user.registration_token_expires:
            return None

        return invited_user

    def confirm_registration(
            self, db: Session, *, access_token: str, obj_in: UserCreate
    ) -> Optional[User]:

        invited_user = self.verify_registration_token(db, access_token)
        if not invited_user:
            return None

        invited_user.registration_token = None
        invited_user.registration_token_expires = None
        invited_user.full_name = obj_in.full_name
        invited_user.username = obj_in.username
        invited_user.hashed_password = get_password_hash(obj_in.password)
        invited_user.is_active = True
        invited_user.email_confirmed = True

        db.commit()
        db.refresh(invited_user)
        return invited_user

    def confirm_password_reset(
            self, db: Session, renewal_token: str, new_password: str
    ) -> Optional[User]:

        user = db.query(self.model).filter(self.model.password_renewal_token == renewal_token).first()

        if not user or datetime.now() > user.password_renewal_token_expires:
            return None

        user.hashed_password = get_password_hash(new_password)
        user.password_renewal_token = None
        user.password_renewal_token_expires = None

        db.commit()
        db.refresh(user)
        return user

    def update_password(
            self, db: Session, user_email: str, old_password: str, new_password: str
    ) -> Optional[User]:

        user = self.authenticate(db, email=user_email, password=old_password)
        if not user:
            return None

        user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user

    def reset_password(self, db: Session, user_email: str) -> Optional[User]:

        user = self.get_by_email(db, email=user_email)
        if not user:
            return None

        user.password_renewal_token = create_access_token(
            subject=user_email, scopes=["users:me"]
        )
        user.password_renewal_token_expires = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        db.commit()
        db.refresh(user)
        return user


    def toggle_user_is_active(self, db: Session, user: User) -> User:
        user.is_active = not user.is_active
        db.commit()
        db.refresh(user)
        return user


users = CRUDUser(User)


def create(db: Session, *, obj_in: UserCreate, role: str) -> Optional[User]:

    user_role = oauth.crud.roles.get_role_by_name(db, role)

    if not user_role:
        return None

    db_obj = User(
        email=obj_in.email,
        username=obj_in.username,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        role=user_role.verbose_name,
        organization=obj_in.organization,
        email_confirmed=True,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_invite(
    db: Session,
    *,
    obj_in: UserInvite,
    organization: "organizations.models.Organization",
    role_name: str
) -> Optional[User]:

    user_role = oauth.crud.roles.get_role_by_name(db=db, role_name=role_name)
    if not user_role:
        return None
    if not organization:
        return None

    db_obj = User(
        email=obj_in.email,
        organization=organization.id,
        is_active=False,
        role=user_role.verbose_name,
        registration_token=create_access_token(
            subject=obj_in.email, scopes=["users:confirm"]
        ),
        registration_token_expires=datetime.now()
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
