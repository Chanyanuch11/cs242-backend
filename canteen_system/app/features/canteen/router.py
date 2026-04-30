from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ...core.database import SessionLocal
from .service import CanteenService

router = APIRouter(prefix="/canteens", tags=["Canteens"])
service = CanteenService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/all")
async def get_all(db: Session = Depends(get_db)):
    return service.get_all(db)

@router.get("/recommend")
async def recommend(
    lat: float,
    lng: float,
    start_time: Optional[str] = Query(None, description="Format: YYYY-MM-DD HH:MM"),
    end_time: Optional[str] = Query(None, description="Format: YYYY-MM-DD HH:MM"),
    db: Session = Depends(get_db)
):
    """
    GET ค้นหาโรงอาหารที่ว่างที่สุดในช่วงเวลา [start_time - end_time]
    และเรียงตามความว่างเฉลี่ย + ระยะทาง
    """
    # จัดการเรื่องเวลา
    try:
        if start_time and end_time:
            t_start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
            t_end = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        else:
            # ถ้าไม่ส่งมา ให้ใช้ช่วงเวลาปัจจุบัน +/- 30 นาที
            now = datetime(2026, 1, 1, 12, 0) # ตัวอย่างเวลาใน data
            t_start = now - timedelta(minutes=30)
            t_end = now + timedelta(minutes=30)
            
        if t_start > t_end:
            raise HTTPException(status_code=400, detail="start_time must be before end_time")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use YYYY-MM-DD HH:MM")

    return service.get_recommendations_in_range(db, t_start, t_end, lat, lng)
