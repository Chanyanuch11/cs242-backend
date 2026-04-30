import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Canteen, CrowdRecord

class CanteenService:
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """ คำนวณระยะทางแบบ Haversine (หน่วย: กิโลเมตร) """
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return 999999
        
        R = 6371  # รัศมีของโลก (กิโลเมตร)
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2) * math.sin(d_lat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2) * math.sin(d_lon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_all(self, db: Session):
        return db.query(Canteen).all()

    def get_recommendations_in_range(self, db: Session, start_time: datetime, end_time: datetime, user_lat: float, user_lng: float):
        results = db.query(Canteen, CrowdRecord).\
            join(CrowdRecord, Canteen.canteen_id == CrowdRecord.canteen_id).\
            filter(CrowdRecord.timestamp >= start_time).\
            filter(CrowdRecord.timestamp <= end_time).\
            all()

        canteen_data = {}
        for canteen, record in results:
            if canteen.canteen_id not in canteen_data:
                canteen_data[canteen.canteen_id] = {
                    "canteen": canteen,
                    "people_sum": 0,
                    "count": 0
                }
            canteen_data[canteen.canteen_id]["people_sum"] += record.people_count
            canteen_data[canteen.canteen_id]["count"] += 1

        recommendations = []
        for c_id, data in canteen_data.items():
            canteen = data["canteen"]
            avg_people = data["people_sum"] / data["count"]
            
            ratio = avg_people / canteen.seat_count
            level = "Low" if ratio < 0.4 else "Medium" if ratio < 0.8 else "High"

            # คำนวณระยะทางเป็นกิโลเมตร
            distance_km = self.calculate_distance(user_lat, user_lng, canteen.latitude, canteen.longitude)
            
            recommendations.append({
                "canteen_id": canteen.canteen_id,
                "name": canteen.name,
                "location": canteen.location,
                "distance_km": round(distance_km, 3), # ปัดเศษ 3 ตำแหน่ง (เมตร)
                "avg_crowd_level": level
            })

        level_map = {"Low": 1, "Medium": 2, "High": 3}
        return sorted(recommendations, key=lambda x: (level_map.get(x['avg_crowd_level'], 99), x['distance_km']))
