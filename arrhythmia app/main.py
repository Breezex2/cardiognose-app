# main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routes.auth import router as auth_router
from routes.user import router as user_router
from routes.patient import router as patient_router
from routes.medical_file import router as medical_file
from routes.dl_model import router as dl_model
from routes.analytics import router as analytics_router
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="v@#7H!p9z$W1k2Lm3XyZ4Q8rBn^Tu$e&GdHsJ0A6oPfCl9EkM") 
#app.add_middleware(SessionMiddleware, secret_key="v@#7H!p9z$W1k2Lm3XyZ4Q8rBn^Tu$e%GdHsJ0A6oPfCl9EkM") 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],  # Or specify your frontend URL like ["http://localhost:3000"]
    allow_credentials=True,  # This is crucial for sessions/cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the uploads folder to serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Correctly mount the jscharting directory within static
app.mount("/static/jscharting", StaticFiles(directory="static/jscharting"), name="jscharting")

templates = Jinja2Templates(directory="templates")
templates_pages = Jinja2Templates(directory="static/pages")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/login")

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(medical_file)
app.include_router(dl_model)
app.include_router(analytics_router)
