from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CanteenBase(BaseModel):
    canteen_id: int
    name: str
    location: str
    latitude: Optional[float]
    longitude: Optional[float]

class CanteenRecommendationResponse(BaseModel):
    canteen_id: int
    name: str
    location: str
    distance: float
    people_count: int
    crowd_level: str
    timestamp: datetime
