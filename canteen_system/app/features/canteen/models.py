from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
import datetime
from ...core.database import Base

class Canteen(Base):
    __tablename__ = "canteens"
    
    canteen_id = Column(Integer, primary_key=True, index=True)
    _name = Column("name", String, index=True)
    _location = Column("location", String)
    _latitude = Column("latitude", Float)
    _longitude = Column("longitude", Float)
    _seat_count = Column("seat_count", Integer)
    opening_hours = Column(String)
    
    records = relationship("CrowdRecord", back_populates="canteen")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_state()

    @property
    def name(self): return self._name
    @name.setter
    def name(self, value): self._name = value

    @property
    def location(self): return self._location
    @location.setter
    def location(self, value): self._location = value

    @property
    def latitude(self): return self._latitude
    @latitude.setter
    def latitude(self, value): self._latitude = value

    @property
    def longitude(self): return self._longitude
    @longitude.setter
    def longitude(self, value): self._longitude = value

    @property
    def seat_count(self): return self._seat_count
    @seat_count.setter
    def seat_count(self, value):
        if value is not None and value < 0:
            raise ValueError("Seat count cannot be negative")
        self._seat_count = value

    # Business Logic
    def calculate_occupancy_status(self, current_people: int) -> str:
        if not self._seat_count or self._seat_count == 0:
            return "ไม่ทราบสถานะ (ไม่มีข้อมูลที่นั่ง)"
        util = (current_people / self._seat_count) * 100
        if util > 100: return "หนาแน่นมาก (เกินความจุ)"
        elif util > 80: return "หนาแน่น"
        elif util > 40: return "ปานกลาง"
        else: return "น้อย"

    def validate_state(self):
        if self._seat_count is not None and self._seat_count < 0:
            raise ValueError("Initial seat count must be positive")


class CrowdRecord(Base):
    __tablename__ = "crowd_records"
    
    record_id = Column(Integer, primary_key=True, index=True)
    canteen_id = Column(Integer, ForeignKey("canteens.canteen_id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    _people_count = Column("people_count", Integer)
    crowd_level = Column(String)
    
    canteen = relationship("Canteen", back_populates="records")

    @property
    def people_count(self): return self._people_count
    @people_count.setter
    def people_count(self, value):
        if value < 0: raise ValueError("People count cannot be negative")
        self._people_count = value
