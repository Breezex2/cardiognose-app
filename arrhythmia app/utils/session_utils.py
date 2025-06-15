# session_utils.py
from itsdangerous import URLSafeSerializer, BadSignature
from fastapi import Request

# Use a strong secret key (store in env/config in production)
SECRET_KEY = "n7G4v@8zPqL1mX!eRs2Uw#9KjHt0YfBd"

# Create a signer
session_signer = URLSafeSerializer(SECRET_KEY)

def create_session(data: dict) -> str:
    return session_signer.dumps(data)

def get_session(request: Request) -> dict | None:
    cookie = request.cookies.get("session")
    if not cookie:
        return None
    try:
        return session_signer.loads(cookie)
    except BadSignature:
        return None
