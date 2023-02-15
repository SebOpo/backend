import geopy.distance
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, backref

from app.components.guests.models import GuestUser
from app.db.base_class import Base
from app.db.utc_convertation import utcnow

status_list = {1: "Awaiting review", 2: "Awaiting approval", 3: "Approved"}


class Location(Base):

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=utcnow())
    updated_at = Column(DateTime, default=utcnow())

    requested_by = Column(
        Integer,
        ForeignKey(GuestUser.id, ondelete="SET NULL"),
        nullable=True,
    )

    report_expires = Column(DateTime)
    reported_by = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"))
    status = Column(Integer, default=1)

    address = Column(String)
    street_number = Column(String)
    city = Column(String)
    country = Column(String)
    index = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)
    reports = Column(JSONB)  # Should we create a separate table for this??
    changelogs = relationship("ChangeLog", lazy="joined", backref=backref("location"))

    reported_by_model = relationship("User", foreign_keys="Location.reported_by")

    def calculate_distance(self, user_lat, user_lng):
        geolocation_coords = (user_lat, user_lng)
        location_coords = (self.lat, self.lng)

        return geopy.distance.geodesic(geolocation_coords, location_coords).km

    def to_json(self, user_lat=None, user_lng=None):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "address": self.address,
            "index": self.index,
            "city": self.city,
            "status": self.status,
            "country": self.country,
            "position": {"lat": self.lat, "lng": self.lng},
            "street_number": self.street_number,
            "distance": self.calculate_distance(user_lat, user_lng)
            if user_lat and user_lng
            else None,
            "reported_by": self.reported_by,
            "organization_name": self.reported_by_model.organization_model.name
            if self.reported_by
            else None,
            "report_expires": self.report_expires,
            "reports": self.reports,
        }
