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
from models import MedicalFile, Patient, User
from models import ArrhythmiaStatus
from pydantic import BaseModel, EmailStr, StringConstraints, constr, field_validator
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
import pytz
from fastapi import Path




router = APIRouter()
templates_pages = Jinja2Templates(directory="static/pages")



@router.get("/search_users", response_class=HTMLResponse)
def search_users(
    request: Request,
    q: str = "",
    page: int = 1,
    db: Session = Depends(get_db)
    ):
    
    role = request.session.get("role")
    if not role or role.lower() != "admin":
        raise HTTPException(status_code=403, detail=f"Access denied: Admins only.")
    
    per_page = 10
    query_str = f"%{q.lower()}%"

    base_query = db.query(User).filter(
        User.username.ilike(query_str) |
        User.fullname.ilike(query_str)
    )

    total_results = base_query.count()
    start_item = (page - 1) * per_page + 1
    end_item = min(start_item + per_page - 1, total_results)

    users = base_query.order_by(User.fullname).offset((page - 1) * per_page).limit(per_page).all()

    return templates_pages.TemplateResponse("users_table.html", {
        "request": request,
        "users": users,
        "result_count": total_results,
        "page": page,
        "pages": (total_results + per_page - 1) // per_page,  # total pages
        "q": q,  # pass query to maintain state
        "start_item": start_item,
        "end_item": end_item
    })




@router.get("/user/{user_id}", response_class=HTMLResponse)
def user_profile(user_id: int, request: Request, db: Session = Depends(get_db)):
    role = request.session.get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admins only.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates_pages.TemplateResponse("user_profile.html", {
        "request": request,
        "user": user,
    })




# Password validation logic (same as used earlier)
def validate_password(password: str):
    if not (8 <= len(password) <= 50):
        raise ValueError("Password must be between 8 and 50 characters.")
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit.")
    if not all(c.isalnum() or c in "@$!%*?&" for c in password):
        raise ValueError("Password contains invalid characters.")

    return password



class UpdateUserField(BaseModel):
    user_id: int
    prop: str
    value: str

@router.post("/update-user")
def update_user_field(request: Request, data: UpdateUserField, db: Session = Depends(get_db)):

    role = request.session.get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admins only.")
    
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    allowed_props = {
        "fullname", "email", "password", "role", "is_active", "address", "phone_number", "date_of_birth"
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
        elif data.prop == "password":
            # Authorization Logic
            is_self = (user.username == request.session.get("username"))
            is_target_doctor = (user.role.value == "doctor")
            is_target_admin = (user.role.value == "admin")

            if request.session.get("username") == "admin":
                # Super admin: can change anyone
                pass
            elif is_self or is_target_doctor:
                if is_target_admin and not is_self:
                    raise HTTPException(status_code=403, detail="You cannot change password for other admins.")
            else:
                raise HTTPException(status_code=403, detail="Unauthorized action")
    
            validate_password(data.value)
            value = bcrypt.hash(data.value)
        else:
            value = data.value

        setattr(user, data.prop, value)
        db.commit()
        return {"status": "success", "updated": {data.prop: value}}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid data: {ve}")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    


class Role(str, Enum):
    admin = 'admin'
    doctor = 'doctor'

PasswordStr = Annotated[str, StringConstraints(min_length=8, max_length=50)]
UsernameStr = Annotated[str, StringConstraints(min_length=3, max_length=20, pattern=r"^[A-Za-z0-9_]+$")]
FullNameStr = Annotated[str, StringConstraints(min_length=1, max_length=50, pattern=r"^[A-Za-z\s.]+$")]
PhoneNumberStr = Annotated[str, StringConstraints(pattern=r"^\d{8}$", min_length=8, max_length=8)]
AddressStr = Annotated[str, StringConstraints(max_length=255)]

class CreateUser(BaseModel):
    username: UsernameStr
    password: PasswordStr
    fullname: FullNameStr
    date_of_birth: date
    phone_number: PhoneNumberStr
    email: EmailStr
    address: AddressStr = ""
    role: Role = Role.doctor
    is_active: bool = True

    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        if not all(c.isalnum() or c in "@$!%*?&" for c in v):
            raise ValueError("Password contains invalid characters.")
        return v
    

@router.post("/create-user")
def create_patient(request: Request, data: CreateUser, db: Session = Depends(get_db)):

    role = request.session.get("role")
    if not role or role.lower() != "admin":
        raise HTTPException(status_code=403, detail=f"Not allowed: Admin only.")
    
    # Check if user with same username or email exists
    existing = db.query(User).filter(
        (User.username == data.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this username already exists")
    
    hashed_password = bcrypt.hash(data.password)

    user = User(
        username = data.username,
        fullname = data.fullname,
        email = data.email,
        password = hashed_password,
        role = data.role,
        is_active = data.is_active,
        created_at = datetime.now(pytz.timezone("Asia/Muscat")),
        address = data.address,
        phone_number = data.phone_number,
        date_of_birth = data.date_of_birth
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"status": "success", "user_id": user.id}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")






@router.delete("/delete-user/{user_id}")
def delete_user(request: Request, user_id: int = Path(..., gt=0), db: Session = Depends(get_db)):

    role = request.session.get("role")
    if not role or role.lower() != "admin":
        raise HTTPException(status_code=403, detail=f"Not allowed: Admin only.")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Error: User not found")
    
    if (user.username == "admin"):
        raise HTTPException(status_code=403, detail=f"Not allowed: You can't delete the main admin account.")
    
    if (user.username == request.session.get("username")):
        raise HTTPException(status_code=403, detail=f"Not allowed: You can't delete your own account.")

    try:
         # Delete user 
        db.delete(user)
        db.commit()
        return {"status": "success", "message": f"User {user_id} deleted"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during deletion")
