from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.db.utc_convertation import utcnow


class Organization(Base):

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=utcnow())
    updated_at = Column(DateTime, default=utcnow())

    name = Column(String, nullable=False, unique=True)
    website = Column(String)
    description = Column(String)
    address = Column(String)
    country = Column(String)
    city = Column(String)
    logo_url = Column(String)

    activated = Column(Boolean, default=False)
    disabled = Column(Boolean, default=False)
    disabled_for = Column(String)

    participants = relationship("User")
