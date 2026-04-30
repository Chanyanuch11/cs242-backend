from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ...core.database import get_db
from .models import Canteen
from .service import CanteenManager
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
        # Convert strings to datetime objects
        dt_start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        dt_end = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        
        # 8.1: Initialize System Controller/Manager
        manager = CanteenManager(db)
        
        return manager.get_recommendations_in_range(dt_start, dt_end, lat, lng)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except CanteenAppError as e:
        # 8.3: Custom exception handling
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Final catch-all for unknown errors
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@router.get("/")
@router.get("/all")
def get_all_canteens(db: Session = Depends(get_db)):
    # 8.1: Manager handling simple flow
    manager = CanteenManager(db)
    return db.query(Canteen).all()
