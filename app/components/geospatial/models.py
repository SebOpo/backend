from sqlalchemy import Column, ForeignKey, Integer, String, Float

from app.db.base_class import Base


class GeospatialIndex(Base):
    id = Column(Integer, primary_key=True)

    geohash = Column(String, index=True)
    location_id = Column(Integer, ForeignKey("location.id", ondelete="CASCADE"))

    lat = Column(Float)
    lng = Column(Float)
    status = Column(Integer)

    # Removed this in favor of a pydantic validator. Subject to remove in the next version.
    # def to_json(self):
    #     return {
    #         "position": {
    #             "lat": self.lat,
    #             "lng": self.lng
    #         },
    #         "status": self.status,
    #         "location_id": self.location_id
    #     }
