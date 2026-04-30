import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Canteen, CrowdRecord
from .ai_service import ai_service
from ...core.exceptions import CanteenNotFoundError, InvalidDataError

class CanteenManager:
    """
    Manager class responsible for controlling the flow of canteen data
    and applying business rules (8.1 Requirement).
    """
    
    def __init__(self, db_session: Session):
        # 8.1: Instance attribute
        self._db = db_session

    @property
    def db(self):
        """Getter for database session (Encapsulation)"""
        return self._db

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Standard haversine formula for distance calculation."""
        if any(v is None for v in [lat1, lon1, lat2, lon2]):
            return 999999
        R = 6371
        d_lat, d_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2)**2 + math.cos(math.radians(lat1)) * 
             math.cos(math.radians(lat2)) * math.sin(d_lon / 2)**2)
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

    def get_recommendations_in_range(self, start_time: datetime, end_time: datetime, user_lat: float, user_lng: float):
        """
        Main complex business logic method (8.1 Requirement).
        Orchestrates data retrieval, distance calculation, and AI summary.
        """
        # 8.3: Input validation
        if user_lat < -90 or user_lat > 90 or user_lng < -180 or user_lng > 180:
            raise InvalidDataError("Invalid GPS coordinates provided.")

        # 1. ดึงข้อมูล
        results = self._db.query(Canteen, CrowdRecord).\
            join(CrowdRecord, Canteen.canteen_id == CrowdRecord.canteen_id).\
            filter(CrowdRecord.timestamp >= start_time).\
            filter(CrowdRecord.timestamp <= end_time).all()

        if not results:
            return {"gemini_summary": "ไม่พบข้อมูลในช่วงเวลาที่ระบุ", "results": []}

        past_results = self._db.query(CrowdRecord).\
            filter(CrowdRecord.timestamp >= start_time - timedelta(hours=1)).\
            filter(CrowdRecord.timestamp <= end_time - timedelta(hours=1)).all()
        
        past_map = {p.canteen_id: p.people_count for p in past_results}

        canteen_data = {}
        for canteen, record in results:
            if canteen.canteen_id not in canteen_data:
                canteen_data[canteen.canteen_id] = {"canteen": canteen, "people_sum": 0, "count": 0}
            canteen_data[canteen.canteen_id]["people_sum"] += record.people_count
            canteen_data[canteen.canteen_id]["count"] += 1

        all_canteens = []
        for c_id, data in canteen_data.items():
            canteen = data["canteen"]
            avg_people = int(data["people_sum"] / data["count"])
            dist_km = self.calculate_distance(user_lat, user_lng, canteen.latitude, canteen.longitude)
            
            # --- [8.1: Using Method from Model] ---
            # ใช้ Logic ที่อยู่ในคลาส Canteen โดยตรง
            status_desc = canteen.calculate_occupancy_status(avg_people)
            
            past_people = past_map.get(c_id, avg_people)
            if avg_people > past_people * 1.1: trend = "กำลังเพิ่มขึ้น"
            elif avg_people < past_people * 0.9: trend = "กำลังลดลง"
            else: trend = "คงที่"

            all_canteens.append({
                "canteen_id": canteen.canteen_id,
                "name": canteen.name,
                "distance_km": round(dist_km, 3),
                "crowd_level": status_desc, # ใช้ข้อมูลจาก Business Logic ใน Model
                "trend_status": trend
            })

        # เรียงลำดับตามระยะทาง
        sorted_by_dist = sorted(all_canteens, key=lambda x: x['distance_km'])

        # 4. เรียก Gemini สรุป
        user_context = {"time": start_time.strftime("%H:%M")}
        gemini_data = [{"name": r["name"], "distance_km": r["distance_km"], "avg_crowd_level": r["crowd_level"], "trend": r["trend_status"]} for r in sorted_by_dist]
        gemini_summary = ai_service.generate_canteen_recommendation(user_context, gemini_data)

        for index, item in enumerate(sorted_by_dist):
            item["rank"] = index + 1

        return {
            "gemini_summary": gemini_summary,
            "results": sorted_by_dist
        }
