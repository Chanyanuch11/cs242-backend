from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ...core.database import get_db
from .models import Canteen
from .service import Recommender
from ...core.exceptions import CanteenAppError

router = APIRouter()

@router.get("/recommend")
def get_recommendations(
    lat: float = Query(..., description="Latitude of user"),
    lng: float = Query(..., description="Longitude of user"),
    start_time: str = Query("2026-01-01 12:00", description="Start time (YYYY-MM-DD HH:MM)"),
    end_time: str = Query("2026-01-01 13:00", description="End time (YYYY-MM-DD HH:MM)"),
    db: Session = Depends(get_db)
):
    try:
        dt_start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        dt_end = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        
        # 8.1: Initialize System Controller (UML: Recommender)
        recommender = Recommender(db)
        
        # UML Method Match
        return recommender.recommendCanteen(dt_start, dt_end, lat, lng)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except CanteenAppError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
@router.get("/all")
def get_all_canteens(db: Session = Depends(get_db)):
    """UML: Simple flow to get all data"""
    return db.query(Canteen).all()
