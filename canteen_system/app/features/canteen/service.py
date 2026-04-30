import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Canteen, CrowdRecord
from .ai_service import ai_service

class CanteenService:
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None: return 999999
        R = 6371
        d_lat, d_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2)**2 + math.cos(math.radians(lat1)) * 
             math.cos(math.radians(lat2)) * math.sin(d_lon / 2)**2)
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

    def get_all(self, db: Session):
        return db.query(Canteen).all()

    def get_recommendations_in_range(self, db: Session, start_time: datetime, end_time: datetime, user_lat: float, user_lng: float):
        # 1. ดึงข้อมูล
        results = db.query(Canteen, CrowdRecord).\
            join(CrowdRecord, Canteen.canteen_id == CrowdRecord.canteen_id).\
            filter(CrowdRecord.timestamp >= start_time).\
            filter(CrowdRecord.timestamp <= end_time).all()

        past_results = db.query(CrowdRecord).\
            filter(CrowdRecord.timestamp >= start_time - timedelta(hours=1)).\
            filter(CrowdRecord.timestamp <= end_time - timedelta(hours=1)).all()
        
        past_map = {p.canteen_id: p.people_count for p in past_results}

        canteen_data = {}
        for canteen, record in results:
            if canteen.canteen_id not in canteen_data:
                canteen_data[canteen.canteen_id] = {"canteen": canteen, "people_sum": 0, "count": 0}
            canteen_data[canteen.canteen_id]["people_sum"] += record.people_count
            canteen_data[canteen.canteen_id]["count"] += 1

        # 2. รวบรวมข้อมูลดิบ
        all_canteens = []
        for c_id, data in canteen_data.items():
            canteen = data["canteen"]
            avg_people = data["people_sum"] / data["count"]
            dist_km = self.calculate_distance(user_lat, user_lng, canteen.latitude, canteen.longitude)
            
            past_people = past_map.get(c_id, avg_people)
            if avg_people > past_people * 1.1: 
                trend_status = "กำลังเพิ่มขึ้น"
            elif avg_people < past_people * 0.9: 
                trend_status = "กำลังลดลง"
            else: 
                trend_status = "คงที่"

            ratio = avg_people / canteen.seat_count
            if ratio < 0.4: crowd_level = "น้อย"
            elif ratio < 0.8: crowd_level = "ปานกลาง"
            else: crowd_level = "หนาแน่น"

            all_canteens.append({
                "canteen_id": canteen.canteen_id,
                "name": canteen.name,
                "distance_km": round(dist_km, 3),
                "crowd_level": crowd_level,
                "trend_status": trend_status
            })

        # เรียงลำดับตามระยะทางเบื้องต้น
        sorted_by_dist = sorted(all_canteens, key=lambda x: x['distance_km'])

        # 3. ให้ Gemini ตัดสินใจ (ส่งข้อมูลที่ไม่มี Emoji)
        user_context = {"time": start_time.strftime("%H:%M")}
        gemini_data = [{"name": r["name"], "distance_km": r["distance_km"], "avg_crowd_level": r["crowd_level"], "trend": r["trend_status"]} for r in sorted_by_dist]
        gemini_summary = ai_service.generate_canteen_recommendation(user_context, gemini_data)

        # 4. เตรียมผลลัพธ์ JSON
        final_results = []
        for index, item in enumerate(sorted_by_dist):
            item["rank"] = index + 1
            final_results.append(item)

        return {
            "gemini_summary": gemini_summary,
            "results": final_results
        }
