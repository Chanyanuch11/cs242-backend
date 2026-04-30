import pandas as pd
import sys
import os
from datetime import datetime

# เพิ่ม Path เพื่อให้เรียกใช้โมดูลใน app ได้
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, init_db
from app.models.models import Canteen, CrowdRecord

def run_import(file_path):
    # 1. เริ่มต้น Database (สร้าง Table ถ้ายังไม่มี)
    print("Initializing Database...")
    init_db()
    db = SessionLocal()

    try:
        # 2. อ่านไฟล์ CSV ด้วย Pandas
        print(f"Reading {file_path}...")
        df = pd.read_csv(file_path)

        # 3. Clean ข้อมูล
        # แปลง timestamp เป็น datetime object (รองรับรูปแบบ 1/1/2026 8:30)
        df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)
        
        # ตรวจสอบ ID โรงอาหารที่มีในไฟล์
        unique_canteen_ids = df['canteenID'].unique()
        
        # 4. สร้างโรงอาหารเริ่มต้น (ถ้ายังไม่มีใน DB)
        for c_id in unique_canteen_ids:
            c_id_int = int(c_id)
            exists = db.query(Canteen).filter(Canteen.canteen_id == c_id_int).first()
            if not exists:
                new_canteen = Canteen(
                    canteen_id=c_id_int,
                    name=f"Canteen {c_id}",
                    seat_count=100, # ค่าสมมติ
                    location="Main Campus",
                    opening_hours="07:00-19:00"
                )
                db.add(new_canteen)
        db.commit()

        # 5. นำเข้าข้อมูล CrowdRecord
        print(f"Importing {len(df)} records...")
        records_to_add = []
        for _, row in df.iterrows():
            # คำนวณ Crowd Level เบื้องต้น (สมมติจาก 100 ที่นั่ง)
            people = int(row['peopleCount'])
            level = "Low"
            if people > 80: level = "High"
            elif people > 40: level = "Medium"

            record = CrowdRecord(
                record_id=int(row['recordID']),
                canteen_id=int(row['canteenID']),
                timestamp=row['timestamp'],
                people_count=people,
                crowd_level=level
            )
            records_to_add.append(record)
            
            # บันทึกเป็นชุด (Batch) เพื่อความเร็ว
            if len(records_to_add) >= 500:
                db.bulk_save_objects(records_to_add)
                db.commit()
                records_to_add = []

        # บันทึกส่วนที่เหลือ
        if records_to_add:
            db.bulk_save_objects(records_to_add)
            db.commit()

        print("Import completed successfully!")

    except Exception as e:
        print(f"Error during import: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    csv_file = "/Users/lloyd/Desktop/ben/cs242/crowdrecord_3months.csv"
    run_import(csv_file)
