from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db.database import get_db
from auth.jwt_handler import create_access_token
from db.users import (
    UserResponse,
    TokenResponse,
    create,
    get_by_username,
    verify,
)
from datetime import timedelta

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/login", response_model=TokenResponse)
def login_route(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_by_username(db, form_data.username)
    if user is None or not verify(db, form_data.username, form_data.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token_data = {"sub": user.username}
    token = create_access_token(token_data, expires_delta=timedelta(minutes=30))
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_route(user_name: str, password: str, db: Session = Depends(get_db)):
    if get_by_username(db, user_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    return create(db, user_name, password)
