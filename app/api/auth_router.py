from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_db
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.auth_schema import Token
from app.services.auth_service import register_new_user, authenticate_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    new_user = register_new_user(db, user_in)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return authenticate_user(db, form_data.username, form_data.password)