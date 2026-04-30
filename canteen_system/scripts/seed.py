import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, engine, Base
from app.features.canteen.models import Canteen, CrowdRecord

def seed_from_excel(excel_path, csv_path):
    print(f"📖 Reading Canteen data from {excel_path}...")
    df_canteen = pd.read_excel(excel_path, skiprows=1)
    
    print("🧹 Cleaning and Re-seeding Database with Real Coordinates...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. นำเข้าข้อมูลโรงอาหารจาก Excel
        canteen_map = {}
        for _, row in df_canteen.iterrows():
            c_id = int(row['canteenId'])
            name = str(row['ชื่อ'])
            capacity = int(row['ที่นั่ง'])
            hours = str(row['เวลาเปิดปิด'])
            
            # แยกพิกัดจากคอลัมน์ "ที่ตั้ง"
            location_str = str(row['ที่ตั้ง'])
            try:
                lat_str, lng_str = location_str.split(',')
                lat = float(lat_str.strip())
                lng = float(lng_str.strip())
            except Exception:
                print(f"⚠️ Warning: Could not parse coordinates for {name}: {location_str}")
                lat, lng = 0.0, 0.0

            canteen = Canteen(
                canteen_id=c_id,
                name=name,
                seat_count=capacity,
                latitude=lat,
                longitude=lng,
                location=location_str, # เก็บตัวเต็มไว้ใน location ด้วย
                opening_hours=hours
            )
            db.add(canteen)
            canteen_map[c_id] = capacity
        
        db.commit()
        print(f"✅ Loaded {len(canteen_map)} canteens with REAL coordinates.")

        # 2. นำเข้า Crowd Data จาก CSV
        print(f"⌛ Importing Crowd Records...")
        df_crowd = pd.read_csv(csv_path, encoding='utf-8-sig')

        count = 0
        records_to_add = []
        for _, row in df_crowd.iterrows():
            c_id = int(row['canteenID'])
            capacity = canteen_map.get(c_id, 100)
            
            try:
                ts_dt = datetime.strptime(str(row['timestamp']), "%d/%m/%Y %H:%M")
            except ValueError:
                ts_dt = datetime.strptime(str(row['timestamp']), "%m/%d/%Y %H:%M")

            people = int(row['peopleCount'])
            ratio = people / capacity
            level = "Low" if ratio < 0.4 else "Medium" if ratio < 0.8 else "High"

            record = CrowdRecord(
                record_id=int(row['recordID']),
                canteen_id=c_id,
                timestamp=ts_dt,
                people_count=people,
                crowd_level=level
            )
            records_to_add.append(record)
            
            if len(records_to_add) >= 500:
                db.bulk_save_objects(records_to_add)
                db.commit()
                records_to_add = []
                count += 500

        if records_to_add:
            db.bulk_save_objects(records_to_add)
            db.commit()
            count += len(records_to_add)

        print(f"✅ Seeding successful: {count} crowd records imported.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    EXCEL_FILE = "/Users/lloyd/Desktop/ben/cs242/Canteen.xlsx"
    CSV_FILE = "/Users/lloyd/Desktop/ben/cs242/crowdrecord_3months.csv"
    seed_from_excel(EXCEL_FILE, CSV_FILE)
