from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey

from app.db.base_class import Base
from app.db.utc_convertation import utcnow
from app.components.organizations.models import Organization
from app.components.users.models import User


class ActivityLog(Base):
    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=utcnow())
    updated_at = Column(DateTime, default=utcnow())
    is_active = Column(Boolean, default=True)

    action_type = Column(Integer)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="SET NULL"))
    organization_id = Column(Integer, ForeignKey(Organization.id, ondelete="SET NULL"))

    description = Column(String)
