from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_302_FOUND
from passlib.hash import bcrypt
from utils.session_utils import create_session, get_session
import pymysql
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from starlette.status import HTTP_302_FOUND
from sqlalchemy.orm import Session
from models import User 
from database import get_db

router = APIRouter()
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")

# DB Settings (change accordingly)
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "asala@2025"
DB_NAME = "arrhythmia_app_db"

def get_user_password(username: str):
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()
            if user:
                return user["password"]
            return None
    finally:
        connection.close()

def verify_credentials(username: str, password: str) -> bool:
    hashed_password = get_user_password(username)
    if not hashed_password:
        return False
    return bcrypt.verify(password, hashed_password)


@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    # Show login page
    return templates.TemplateResponse("login.html", {"request": request, "error": None})




@router.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: str = Form(None),
    db: Session = Depends(get_db)
):
    if not username or not password:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "All fields are required."
        })

    if len(password) < 8:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Password must be at least 8 characters long."
        })

    # Check credentials
    user = db.query(User).filter_by(username=username).first()

    if (user.is_active == 0):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Your account is inactive. Please contact the administrator"
        })

    if user and bcrypt.verify(password, user.password):
        request.session["doctor_id"] = user.id
        request.session["username"] = user.username
        request.session["role"] = user.role.value

        #response = RedirectResponse(url="/index", status_code=HTTP_302_FOUND)
        # Redirect based on role
        redirect_url = "/admin_index" if user.role.value == "admin" else "/index"
        response = RedirectResponse(url=redirect_url, status_code=HTTP_302_FOUND)

        if remember_me == "on":
            response.set_cookie(
                key="remember_me",
                value="1",
                max_age=60 * 60 * 24 * 7,
                httponly=True
            )
        return response

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Invalid username or password"
    })
    

# Basic HTTP Basic dependency for protected routes
def authenticate(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    if not verify_credentials(credentials.username, credentials.password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@router.get("/logout")
def logout(request: Request):
    request.session.clear()  # This clears all session data
    return RedirectResponse(url="/login", status_code=302)

@router.get("/protected")
def protected_route(username: str = Depends(authenticate)):
    return {"message": f"Welcome, {username}!"}


@router.get("/index", response_class=HTMLResponse)
def index(request: Request):
    username = request.session.get("username")
    role = request.session.get("role")

    if not username or role != "doctor":
        return RedirectResponse(url="/logout")
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "user": username
    })


@router.get("/admin_index", response_class=HTMLResponse)
def index(request: Request):
    username = request.session.get("username")
    role = request.session.get("role")

    if not username or role != "admin":
        return RedirectResponse(url="/logout")

    return templates.TemplateResponse("admin_index.html", {
        "request": request,
        "user": username
    })




# Password validation logic
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


class ChangePasswordRequest(BaseModel):
    new_password: str

@router.post("/change-password")
def change_password(request: Request, data: ChangePasswordRequest, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        validate_password(data.new_password)
        hashed_password = bcrypt.hash(data.new_password)
        user.password = hashed_password
        db.commit()

        return {"status": "success", "message": "Password updated successfully."}
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
