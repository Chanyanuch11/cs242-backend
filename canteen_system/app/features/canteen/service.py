import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Canteen, CrowdRecord
from .ai_service import ai_service
from ...core.exceptions import CanteenNotFoundError, InvalidDataError

class Recommender:
    """
    Class Recommender (UML Match)
    """
    
    def __init__(self, db_session: Session, engineId: str = "Gemini-Flash-1.5"):
        # UML Attribute
        self._engineId = engineId
        self._db = db_session

    @property
    def engineId(self):
        return self._engineId

    # --- [UML Method Alias] ---
    def recommendCanteen(self, start_time: datetime, end_time: datetime, user_lat: float, user_lng: float):
        """CamelCase alias for UML match"""
        return self.recommend_canteen(start_time, end_time, user_lat, user_lng)

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        if any(v is None for v in [lat1, lon1, lat2, lon2]):
            return 999999
        R = 6371
        d_lat, d_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2)**2 + math.cos(math.radians(lat1)) * 
             math.cos(math.radians(lat2)) * math.sin(d_lon / 2)**2)
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

    def recommend_canteen(self, start_time: datetime, end_time: datetime, user_lat: float, user_lng: float):
        if user_lat < -90 or user_lat > 90 or user_lng < -180 or user_lng > 180:
            raise InvalidDataError("Invalid GPS coordinates.")

        from sqlalchemy import extract
        start_hour = start_time.hour
        end_hour = end_time.hour

        results = self._db.query(Canteen, CrowdRecord).\
            join(CrowdRecord, Canteen.canteen_id == CrowdRecord.canteen_id).\
            filter(extract('hour', CrowdRecord.timestamp) >= start_hour).\
            filter(extract('hour', CrowdRecord.timestamp) <= end_hour).all()

        if not results:
            return {"gemini_summary": "ไม่พบข้อมูลในช่วงเวลานี้", "results": []}

        past_hour = (start_hour - 1) % 24
        past_results = self._db.query(CrowdRecord).\
            filter(extract('hour', CrowdRecord.timestamp) == past_hour).all()
        
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
            
            status_desc = canteen.calculate_occupancy_status(avg_people)
            
            past_people = past_map.get(c_id, avg_people)
            trend = "คงที่"
            if avg_people > past_people * 1.1: trend = "กำลังเพิ่มขึ้น"
            elif avg_people < past_people * 0.9: trend = "กำลังลดลง"

            all_canteens.append({
                "canteen_id": canteen.canteen_id,
                "name": canteen.name,
                "distance_km": round(dist_km, 3),
                "crowd_level": status_desc,
                "trend_status": trend
            })

        sorted_by_dist = sorted(all_canteens, key=lambda x: x['distance_km'])

        user_context = {"time": start_time.strftime("%H:%M")}
        gemini_data = [{"name": r["name"], "distance_km": r["distance_km"], "avg_crowd_level": r["crowd_level"], "trend": r["trend_status"]} for r in sorted_by_dist]
        gemini_summary = ai_service.generate_canteen_recommendation(user_context, gemini_data)

        for index, item in enumerate(sorted_by_dist):
            item["rank"] = index + 1

        return {
            "recommenderEngine": self._engineId,
            "gemini_summary": gemini_summary,
            "results": sorted_by_dist
        }
