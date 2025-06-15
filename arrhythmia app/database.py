from sqlalchemy import create_engine, Column, String, Integer, Boolean, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from urllib.parse import quote_plus


# DB Settings
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = quote_plus("asala@2025")
DB_NAME = "arrhythmia_app_db"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
