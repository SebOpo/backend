from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base_class import Base
from app.db.utc_convertation import utcnow


class ChangeLog(Base):

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=utcnow())
    location_id = Column(Integer, ForeignKey("location.id", ondelete="CASCADE"))
    action_type = Column(Integer, nullable=False)

    old_flags = Column(JSONB, nullable=True)
    new_flags = Column(JSONB, nullable=True)
