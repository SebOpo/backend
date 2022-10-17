from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Interval
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.base_class import Base

status_list = {
    1: "Awaiting review",
    2: "Awaiting approval",
    3: "Approved"
}


class Location(Base):

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    report_expires = Column(DateTime)
    reported_by = Column(Integer, ForeignKey('user.id', ondelete="SET NULL"))
    status = Column(Integer, default=1)

    address = Column(String, nullable=False, unique=True)
    city = Column(String)
    country = Column(String)
    index = Column(Integer, nullable=False)
    lat = Column(Float)
    lng = Column(Float)
    reports = Column(JSONB) # Should we create a separate table for this??

    def to_json(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "address": self.address,
            "index": self.index,
            "city": self.city,
            "status": self.status,
            "country": self.country,
            "position": {
              "lat": self.lat, "lng": self.lng
            },
            "reported_by": self.reported_by,
            "report_expires": self.report_expires,
            "reports": self.reports
        }


