from typing import List, Optional

from sqlalchemy.orm import Session

from app import schemas
from app.crud.base import CRUDBase
from app.models.oauth import OauthRole, OauthScope


class CRUDScopes(CRUDBase[OauthScope, schemas.OauthScope, schemas.OauthScope]):
    def get_or_create_scope(
        self, db: Session, *, scope: schemas.OauthScope
    ) -> OauthScope:
        existing_scope = self.get_scope_by_scope_string(db, scope.scope)
        if existing_scope:
            return existing_scope

        db_object = OauthScope(module=scope.module, scope=scope.scope)

        db.add(db_object)
        db.commit()
        db.refresh(db_object)
        return db_object

    def get_scope_by_scope_string(self, db: Session, scope_string: str) -> OauthScope:
        return db.query(self.model).filter(self.model.scope == scope_string).first()

    def get_by_multi_id(self, db: Session, ids: List[int]):
        return db.query(self.model).filter(self.model.id.in_(ids)).all()


class CRUDRoles(CRUDBase[OauthRole, schemas.OauthRoleCreate, schemas.OauthRoleCreate]):
    def get_or_create_role(
        self, db: Session, *, role: schemas.OauthRole, scope_list: List[OauthScope]
    ) -> OauthRole:
        existing_role = self.get_role_by_name(db, role_name=role.verbose_name)
        if existing_role:
            return existing_role

        db_object = OauthRole(verbose_name=role.verbose_name)
        db_object.scopes.extend(scope_list)

        db.add(db_object)
        db.commit()
        db.refresh(db_object)
        return db_object

    def get_role_by_name(self, db: Session, role_name: str) -> OauthRole:
        return db.query(self.model).filter(self.model.verbose_name == role_name).first()

    def patch(
        self,
        db: Session,
        *,
        role: OauthRole,
        scope_list: List[OauthScope],
        name: str = None,
    ) -> Optional[OauthRole]:

        role.verbose_name = name if name else role.verbose_name
        role.scopes = scope_list
        db.commit()
        db.refresh(role)
        return role


scopes = CRUDScopes(OauthScope)
roles = CRUDRoles(OauthRole)
