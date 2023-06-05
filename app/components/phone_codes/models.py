from sqlalchemy import Column, Integer, String, DateTime, Boolean

from app.db.base_class import Base
from app.db.utc_convertation import utcnow


class PhoneCode(Base):
    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=utcnow())
    updated_at = Column(DateTime, default=utcnow())

    country_code = Column(String, nullable=False)
    verbose_name = Column(String, nullable=False)

    phone_code = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
