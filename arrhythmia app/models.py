from datetime import datetime, timezone
import enum
import pytz
from sqlalchemy import Column, Integer, String, Boolean, Date, Enum, DateTime, Text
from database import Base

class ArrhythmiaStatus(enum.Enum):
    normal = 'normal'
    RBBB = 'RBBB'
    APC = 'APC'
    PVC = 'PVC'
    LBBB = 'LBBB'
    unknown = 'unknown'

# Patient table model
class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    civil_id = Column(String(8), index=True)
    first_name = Column(String(100))
    middle_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(Date)
    phone_number = Column(String(20))
    email = Column(String(100))
    address = Column(String(255))
    arrhythmia_status = Column(Enum(ArrhythmiaStatus), default=ArrhythmiaStatus.unknown)
    is_active = Column(Boolean)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone("Asia/Muscat")))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone("Asia/Muscat")))

class MedicalFile(Base):
    __tablename__ = 'medical_files'

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(255), nullable=False)
    note = Column(String(255))
    status = Column(Enum(ArrhythmiaStatus), default=ArrhythmiaStatus.unknown)
    doctor_id = Column(Integer, nullable=False)
    patient_id = Column(Integer, nullable=False)
    uploaded_date = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone("Asia/Muscat")))
    updated_date = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone("Asia/Muscat")))
    test_result = Column(Text)

class UserRole(enum.Enum):
    admin = "admin"
    doctor = "doctor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    fullname = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True, unique=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone("Asia/Muscat")))
    address = Column(String(255), nullable=False)
    phone_number = Column(String(8), nullable=False)
    date_of_birth = Column(Date)

    