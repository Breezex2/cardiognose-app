import datetime
import os
import shutil
from fastapi import APIRouter, File, Form, Depends, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import MedicalFile, Patient
from models import ArrhythmiaStatus
from pydantic import BaseModel
from datetime import datetime
import pytz


router = APIRouter()
#security = HTTPBasic()
#templates_pages = Jinja2Templates(directory="static/pages")


@router.post("/uploadMedicalFile")
async def upload_file(
    file: UploadFile = File(...),
    patient_civil_id: int = Form(...),
    patient_id: int = Form(...),
    doctor_id: int = Form(...), 
    db: Session = Depends(get_db)  # inject the DB session
):
    patient_folder = os.path.join("uploads", str(patient_civil_id))
    os.makedirs(patient_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = os.path.splitext(file.filename)[1]
    new_filename = f"{timestamp}{extension}"
    file_path = os.path.join(patient_folder, new_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Count files in folder
        file_count = len([
            name for name in os.listdir(patient_folder)
            if os.path.isfile(os.path.join(patient_folder, name))
        ])

        # Get patient_id from civil ID
        #patient = db.query(Patient).filter(Patient.civil_id == patient_civil_id).first()
        #if not patient:
        #    return JSONResponse(content={"error": "Patient not found"}, status_code=404)

        # Save new medical file record
        new_file_record = MedicalFile(
            file_path=file_path,
            note=None,
            status= ArrhythmiaStatus.unknown, 
            doctor_id=doctor_id,
            patient_id=patient_id,
            test_result= "Not tested yet"
        )
        db.add(new_file_record)
        db.commit()

        return JSONResponse(content={
            "message": "File uploaded and record saved",
            "patient_id": patient_id,
            "file_count": file_count
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    


@router.get("/getMedicalFiles/{patient_id}", response_class=JSONResponse)
def get_medical_files_by_patient_id(patient_id: int, db: Session = Depends(get_db)):
    files = db.query(MedicalFile).filter(MedicalFile.patient_id == patient_id).order_by(MedicalFile.uploaded_date.desc()).all()

    file_data = [
        {
            "id": file.id,
            "file_path": file.file_path,
            "note": file.note,
            "status": file.status.value if hasattr(file.status, "value") else file.status,
            "doctor_id": file.doctor_id,
            "patient_id": file.patient_id,
            "uploaded_date": file.uploaded_date.strftime("%d %b %Y | %I:%M %p") if file.uploaded_date else None,
            "updated_date": file.updated_date.strftime("%d %b %Y | %I:%M %p") if file.updated_date else None,
            "test_result": file.test_result
        }
        for file in files
    ]

    return JSONResponse(content={"patient_id": patient_id, "files": file_data})




@router.post("/deleteMedicalFile", response_class=JSONResponse)
def delete_medical_file(
    file_id: int = Form(...),
    patient_id: int = Form(...),
    db: Session = Depends(get_db)
):
    file_record = db.query(MedicalFile).filter(MedicalFile.id == file_id).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to delete file: {e}"})

    db.delete(file_record)
    db.commit()

    file_count = db.query(MedicalFile).filter(MedicalFile.patient_id == patient_id).count()

    return JSONResponse(content={
        "message": "File deleted successfully",
        "file_id": file_id,
        "file_count": file_count
    })




class UpdateMedicalNote(BaseModel):
    file_id: int
    note: str
    patient_id: int

@router.post("/update-medicalfile-note")
def update_medical_file_note(data: UpdateMedicalNote, db: Session = Depends(get_db)):
    file = db.query(MedicalFile).filter(MedicalFile.id == data.file_id).first()

    if not file:
        raise HTTPException(status_code=404, detail="Medical file not found")

    file.note = data.note
    file.updated_date = datetime.now(pytz.timezone("Asia/Muscat"))

    db.commit()

    return {"message": "Note updated successfully"}





@router.get("/get-images/{patient_id}/{medical_file_path:path}")
async def get_images(patient_id: str, medical_file_path: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    medical_file_name_with_ext = os.path.basename(medical_file_path)
    medical_file_name = os.path.splitext(medical_file_name_with_ext)[0]
    folder_path = f"uploads/{patient.civil_id}/{medical_file_name}"
    
    if not os.path.exists(folder_path):
        return JSONResponse(content={"status": False, "data": f"Folder not found: {folder_path}"})

    image_files = [f for f in os.listdir(folder_path) if f.endswith(".png")]
    image_urls = [f"/{folder_path}/{img}" for img in image_files]

    return JSONResponse(content={
        "status": True,
        "images": image_urls,
        "folder": folder_path
    })