import datetime
from enum import Enum
import os
import shutil
from typing import Annotated
from fastapi import APIRouter, File, Request, Form, Depends, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_302_FOUND
from passlib.hash import bcrypt
import pymysql
from fastapi.params import Query
from sqlalchemy.orm import Session
from database import get_db
from models import MedicalFile, Patient
from models import ArrhythmiaStatus
from pydantic import BaseModel, EmailStr, StringConstraints, constr
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
import pytz
from fastapi import Path




router = APIRouter()
#security = HTTPBasic()
templates_pages = Jinja2Templates(directory="static/pages")


@router.get("/search_patients", response_class=HTMLResponse)
def search_patients(
    request: Request,
    q: str = "",
    page: int = 1,
    db: Session = Depends(get_db)
    ):

    role = request.session.get("role")
    if not role or role.lower() != "doctor":
        raise HTTPException(status_code=403, detail=f"Access denied: doctors only.")
    
    per_page = 10
    query_str = f"%{q.lower()}%"

    base_query = db.query(Patient).filter(
        Patient.civil_id.like(query_str) |
        Patient.first_name.ilike(query_str) |
        Patient.middle_name.ilike(query_str) |
        Patient.last_name.ilike(query_str)
    )

    total_results = base_query.count()
    start_item = (page - 1) * per_page + 1
    end_item = min(start_item + per_page - 1, total_results)

    patients = base_query.order_by(Patient.first_name).offset((page - 1) * per_page).limit(per_page).all()

    return templates_pages.TemplateResponse("patients_table.html", {
        "request": request,
        "patients": patients,
        "result_count": total_results,
        "page": page,
        "pages": (total_results + per_page - 1) // per_page,  # total pages
        "q": q,  # pass query to maintain state
        "start_item": start_item,
        "end_item": end_item
    })




@router.get("/patient/{patient_id}", response_class=HTMLResponse)
def patient_profile(patient_id: int, request: Request, db: Session = Depends(get_db)):

    role = request.session.get("role")
    if not role or role.lower() != "doctor":
        raise HTTPException(status_code=403, detail=f"Not allowed: Doctors only.")
    
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Check if patient folder exists
    # patient_folder = os.path.join("uploads", str(patient.civil_id))
    file_count = 0
    file_count = db.query(MedicalFile).filter(MedicalFile.patient_id == patient_id).count()

    #if os.path.isdir(patient_folder):
    #    file_count = len([
    #        name for name in os.listdir(patient_folder)
    #        if os.path.isfile(os.path.join(patient_folder, name))
    #    ])

    doctor_id = request.session.get("doctor_id")
    if not doctor_id:
       raise HTTPException(status_code=403, detail="Doctor not identified or not logged in")


    return templates_pages.TemplateResponse("patient_profile.html", {
        "request": request,
        "patient": patient,
        "doctor_id": doctor_id,
        "file_count": file_count
    })





class UpdatePatientField(BaseModel):
    patient_id: int
    prop: str
    value: str

@router.post("/update-patient")
def update_patient_field(request: Request, data: UpdatePatientField, db: Session = Depends(get_db)):

    role = request.session.get("role")
    if not role or role.lower() != "doctor":
        raise HTTPException(status_code=403, detail=f"Not allowed: Doctors only.")

    patient = db.query(Patient).filter(Patient.patient_id == data.patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    allowed_props = {
        "first_name", "middle_name", "last_name", "phone_number",
        "date_of_birth", "email", "address", "arrhythmia_status", "is_active"
    }

    if data.prop not in allowed_props:
        raise HTTPException(status_code=400, detail="Invalid property")

    try:
        # Handle type conversion based on property name
        if data.prop == "is_active":
            val_str = str(data.value).strip().lower()
            if val_str in ['1', 'true']:
                value = True
            elif val_str in ['0', 'false']:
                value = False
            else:
                raise HTTPException(status_code=400, detail="Invalid value for is_active")
        elif data.prop == "date_of_birth":
            value = datetime.strptime(data.value, "%Y-%m-%d").date()
        else:
            value = data.value

        setattr(patient, data.prop, value)
        db.commit()
        return {"status": "success", "updated": {data.prop: value}}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid data: {ve}")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    



class ArrhythmiaStatusEnum(str, Enum):
    normal = 'normal'
    RBBB = 'RBBB'
    APC = 'APC'
    PVC = 'PVC'
    LBBB = 'LBBB'
    unknown = 'unknown'

class CreatePatient(BaseModel):
    civil_id: Annotated[str, StringConstraints(min_length=7, max_length=8)]
    first_name: Annotated[str, StringConstraints(min_length=1, max_length=12)]
    middle_name: Annotated[str, StringConstraints(min_length=1, max_length=12)]
    last_name: Annotated[str, StringConstraints(min_length=1, max_length=12)]
    date_of_birth: date
    phone_number: Annotated[str, StringConstraints(pattern=r"^\d{8}$",min_length=8,max_length=8)]
    email: EmailStr
    address: Annotated[str, StringConstraints(max_length=100)] = ""
    arrhythmia_status: ArrhythmiaStatusEnum = ArrhythmiaStatusEnum.unknown
    is_active: bool = True

@router.post("/create-patient")
def create_patient(request: Request, data: CreatePatient, db: Session = Depends(get_db)):

    role = request.session.get("role")
    if not role or role.lower() != "doctor":
        raise HTTPException(status_code=403, detail=f"Not allowed: Doctors only.")
    
    # Check if patient with same civil_id or email exists (optional but recommended)
    existing = db.query(Patient).filter(
        (Patient.civil_id == data.civil_id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient with this civil ID already exists")

    patient = Patient(
        civil_id=data.civil_id,
        first_name=data.first_name,
        middle_name=data.middle_name,
        last_name=data.last_name,
        date_of_birth=data.date_of_birth,
        phone_number=data.phone_number,
        email=data.email,
        address=data.address,
        arrhythmia_status=data.arrhythmia_status,
        is_active=data.is_active,
        created_at=datetime.now(pytz.timezone("Asia/Muscat")),
        updated_at=datetime.now(pytz.timezone("Asia/Muscat")),
    )

    try:
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return {"status": "success", "patient_id": patient.patient_id}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")






@router.delete("/delete-patient/{patient_id}")
def delete_patient(request: Request, patient_id: int = Path(..., gt=0), db: Session = Depends(get_db)):

    role = request.session.get("role")
    if not role or role.lower() != "doctor":
        raise HTTPException(status_code=403, detail=f"Not allowed: Doctors only.")
    
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
         # Delete all related medical files
        db.query(MedicalFile).filter(MedicalFile.patient_id == patient_id).delete(synchronize_session=False)
        # Delete folder in uploads if exists
        patient_folder = os.path.join("uploads", str(patient.civil_id))
        if os.path.exists(patient_folder) and os.path.isdir(patient_folder):
            shutil.rmtree(patient_folder)
         # Delete patient 
        db.delete(patient)
        db.commit()
        return {"status": "success", "message": f"Patient {patient_id} deleted"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during deletion")
