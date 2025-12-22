from datetime import datetime, timedelta, timezone
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
from app.db.db import SessionLocal
from app.deps.deps import get_db
from app.models.models import User

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

TIME_EXPIRE_MINUTES = 30
SECRET_KEY = "aralavara"
ALGORITHM = "HS256"

def get_user(user_email, db: Session = Depends(get_db)):
    return db.query(User).filter(User.email == user_email).first()

def hash_password(password):
    return pwd_context.hash(password)

def validate_password(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)

def create_user_token(payload: dict, expire_minute=TIME_EXPIRE_MINUTES):
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minute)
    payload.update({"exp" : expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_decoded = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    user_email = user_decoded.get("sub")
    user = db.query(User).filter(User.email == user_email).first()

    return user