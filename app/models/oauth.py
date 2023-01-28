from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

# TODO CHANGE THE VIEW PERMISSION TO READ
default_scopes = {
    "users:me",
    "users:create",
    "users:edit",
    "users:delete",
    "users:roles",
    "locations:view",
    "locations:create",
    "locations:edit",
    "locations:delete",
    "organizations:create",
    "organizations:view",
    "organizations:edit",
    "organizations:delete",
    "oauth:read",
    "oauth:create",
    "oauth:edit",
    "oauth:delete",
    "zones:create",
    "zones:edit",
    "zones:get"
}


association_table = Table(
    "role_scopes",
    Base.metadata,
    Column("role_id", ForeignKey("OauthRole.id"), primary_key=True),
    Column("scope_id", ForeignKey("OauthScope.id"), primary_key=True)
)


class OauthRole(Base):
    __tablename__ = "OauthRole"
    id = Column(Integer, primary_key=True, index=True)
    verbose_name = Column(String, nullable=False, unique=True)
    scopes = relationship(
        "OauthScope", secondary=association_table, back_populates="roles"
    )


class OauthScope(Base):
    __tablename__ = "OauthScope"
    id = Column(Integer, primary_key=True, index=True)
    module = Column(String, nullable=False)
    scope = Column(String, nullable=False, unique=True)
    is_default = Column(Boolean)
    roles = relationship(
        "OauthRole", secondary=association_table, back_populates="scopes"
    )
