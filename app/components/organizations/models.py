from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.db.utc_convertation import utcnow


class Organization(Base):

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=utcnow())

    name = Column(String, nullable=False, unique=True)
    website = Column(String)
    description = Column(String)
    # leader = Column(Integer, ForeignKey("user.id"))
    participants = relationship("User")
