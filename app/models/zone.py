from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.db.utc_convertation import utcnow

from app.db.base_class import Base


class Zone(Base):

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=utcnow())

    zone_type = Column(Integer, nullable=False)
    bounding_box = Column(String)
    verbose_name = Column(String)
