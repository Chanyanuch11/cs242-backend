from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
import datetime
from ...core.database import Base

class User:
    """
    Class User (UML Behavior Implemented)
    """
    def __init__(self, userId: int, name: str):
        self._userId = userId
        self._name = name
        self._last_recommendation = None
    
    @property
    def userId(self): return self._userId
    @property
    def name(self): return self._name

    # UML Methods Implemented
    def searchCanteen(self, recommender, startTime, endTime, lat, lng):
        """
        Calls the recommender engine to find suitable canteens.
        Demonstrates interaction between classes.
        """
        self._last_recommendation = recommender.recommendCanteen(startTime, endTime, lat, lng)
        return self._last_recommendation

    def viewRecommendation(self):
        """Returns the summary text from the last search."""
        if not self._last_recommendation:
            return "ยังไม่มีข้อมูลการแนะนำ โปรดค้นหาก่อน"
        return self._last_recommendation.get("gemini_summary")

    def viewCanteenDetail(self, canteen):
        """Calls Canteen's method to view specific info."""
        return canteen.getDetail()


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

    # --- [UML Attributes (CamelCase)] ---
    @property
    def canteenId(self): return self.canteen_id
    
    @property
    def name(self): return self._name
    @name.setter
    def name(self, value): self._name = value

    @property
    def location(self): return self._location
    @location.setter
    def location(self, value): self._location = value

    @property
    def seatCount(self): return self._seat_count
    @seatCount.setter
    def seatCount(self, value):
        if value is not None and value < 0: raise ValueError("Invalid seat count")
        self._seat_count = value

    @property
    def openingHours(self): return self.opening_hours
    @openingHours.setter
    def openingHours(self, value): self.opening_hours = value

    # Helper properties for code logic
    @property
    def latitude(self): return self._latitude
    @property
    def longitude(self): return self._longitude

    # --- [UML Methods] ---
    def getDetail(self):
        return f"{self._name} at {self._location}"

    def addCanteen(self, db_session):
        db_session.add(self)
        db_session.commit()

    # Business Logic
    def calculate_occupancy_status(self, current_people: int) -> str:
        if not self._seat_count or self._seat_count == 0: return "น้อย"
        util = (current_people / self._seat_count) * 100
        if util > 80: return "หนาแน่น"
        elif util > 40: return "ปานกลาง"
        else: return "น้อย"

    def validate_state(self):
        if self._seat_count is not None and self._seat_count < 0:
            raise ValueError("State Validation Error")


class CrowdRecord(Base):
    __tablename__ = "crowd_records"
    
    record_id = Column(Integer, primary_key=True, index=True)
    canteen_id = Column(Integer, ForeignKey("canteens.canteen_id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    _people_count = Column("people_count", Integer)
    _crowd_level = Column("crowd_level", String)
    
    canteen = relationship("Canteen", back_populates="records")

    # --- [UML Attributes (CamelCase)] ---
    @property
    def recordId(self): return self.record_id
    
    @property
    def canteenId(self): return self.canteen_id

    @property
    def peopleCount(self): return self._people_count
    @peopleCount.setter
    def peopleCount(self, value): self._people_count = value

    @property
    def crowdLevel(self): return self._crowd_level
    @crowdLevel.setter
    def crowdLevel(self, value): self._crowd_level = value

    # Helper for logic
    @property
    def people_count(self): return self._people_count

    # --- [UML Methods] ---
    def saveRecord(self, db_session):
        db_session.add(self)
        db_session.commit()

    @staticmethod
    def getRecordByTime(db_session, start, end):
        return db_session.query(CrowdRecord).filter(CrowdRecord.timestamp.between(start, end)).all()
