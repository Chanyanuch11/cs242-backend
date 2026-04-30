from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
import datetime
from ...core.database import Base

class Canteen(Base):
    __tablename__ = "canteens"
    canteen_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    seat_count = Column(Integer)
    opening_hours = Column(String)
    
    records = relationship("CrowdRecord", back_populates="canteen")

class CrowdRecord(Base):
    __tablename__ = "crowd_records"
    record_id = Column(Integer, primary_key=True, index=True)
    canteen_id = Column(Integer, ForeignKey("canteens.canteen_id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    people_count = Column(Integer)
    crowd_level = Column(String)
    
    canteen = relationship("Canteen", back_populates="records")
