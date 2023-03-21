from sqlalchemy import Column, Integer, String, DateTime

from app.db.base_class import Base
from app.db.utc_convertation import utcnow


class Zone(Base):
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=utcnow())

    zone_type = Column(Integer, nullable=False)
    bounding_box = Column(String)
    verbose_name = Column(String)
