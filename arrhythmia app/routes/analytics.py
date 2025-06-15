# routes/analytics.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models import Patient
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates_pages = Jinja2Templates(directory="static/pages")

@router.get("/api/patient-status")
def get_patient_status(request: Request, db: Session = Depends(get_db)):
    role = request.session.get("role")
    if not role or role.lower() != "doctor":
        raise HTTPException(status_code=403, detail="Not allowed: Doctors only.")

    patients = db.query(Patient).all()
    
    result = []
    for patient in patients:
        # Ensure date_of_birth is formatted as a string
        dob_str = patient.date_of_birth.strftime("%Y-%m-%d") if patient.date_of_birth else None
        
        # Ensure arrhythmia_status is the string value of the enum
        status_str = patient.arrhythmia_status.value if patient.arrhythmia_status else "unknown"
        
        # For the chart, we want 'normal' and 'abnormal' classifications.
        # Let's map the existing statuses to 'Normal' or 'Abnormal'
        # chart_status = "Normal" if status_str == "normal" else "Abnormal"

        result.append({"dob": dob_str, "status": status_str})
        
    return JSONResponse(content=result)

@router.get("/analytics", response_class=HTMLResponse)
def analytics_page(request: Request, db: Session = Depends(get_db)):
    role = request.session.get("role")
    if not role or role.lower() != "doctor":
        raise HTTPException(status_code=403, detail="Not allowed: Doctors only.")
    # Use templates_pages which is typically configured to look in static/pages
    return templates_pages.TemplateResponse("analytics.html", {"request": request})