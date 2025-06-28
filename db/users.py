from uuid import UUID
import bcrypt
from pydantic import BaseModel

from db.table import UserDB

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: UUID
    username: str

    class Config:
        from_attributes = True

def create(db, username: str, password: str) -> UserResponse:
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = UserDB(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(id=new_user.id, username=new_user.username)

def verify(db, username: str, password: str):
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        return user
    return None

def get_by_username(db, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()
