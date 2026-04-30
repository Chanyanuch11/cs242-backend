from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# ใช้ URL จาก Settings Class
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency เพื่อใช้ใน FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
