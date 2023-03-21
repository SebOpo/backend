from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Report(Base):
    id = Column(Integer, primary_key=True, index=True)

    verbose_name = Column(String, nullable=False, unique=True)
    options = relationship("ReportOption")


class ReportOption(Base):
    id = Column(Integer, primary_key=True, index=True)
    verbose_name = Column(String)
    report_id = Column(Integer, ForeignKey("report.id"))
