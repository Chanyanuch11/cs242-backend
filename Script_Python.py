import pandas as pd

# ──────────────────────────────────────────
# 1. Load
# ──────────────────────────────────────────
df = pd.read_csv('crowdrecord_3months.csv', encoding='utf-8-sig')
print(f"Shape: {df.shape}")
print(df.head())

# ──────────────────────────────────────────
# 2. ตรวจสอบ Missing
# ──────────────────────────────────────────
print("\n=== Missing Values ===")
print(df.isnull().sum())

# ──────────────────────────────────────────
# 3. Clean Missing
# ──────────────────────────────────────────

# timestamp ที่หายไป → ลบทิ้ง (ไม่สามารถเดาเวลาได้)
df = df.dropna(subset=['timestamp'])

# canteenID / ชื่อโรงอาหาร ที่หายไป → เติมด้วย forward fill
# (สมมติข้อมูลเรียงตาม canteen เดิมต่อเนื่องกัน)
df['canteenID'] = df['canteenID'].ffill()
# peopleCount ที่หายไป → เติมด้วย mean ของแต่ละ canteen
df['peopleCount'] = df.groupby('canteenID')['peopleCount'].transform(lambda x: x.fillna(x.mean()))

# ──────────────────────────────────────────
# 4. ตรวจสอบอีกครั้ง
# ──────────────────────────────────────────
print("\n=== Missing After Clean ===")
print(df.isnull().sum())

# ──────────────────────────────────────────
# 5. Export
# ──────────────────────────────────────────
df.to_csv('crowdrecord_cleaned.csv', index=False, encoding='utf-8-sig')
print("\nSaved → crowdrecord_cleaned.csv")