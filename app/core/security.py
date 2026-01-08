from datetime import datetime, timedelta, timezone
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

TIME_EXPIRE_MINUTES = 30

ALGORITHM = "HS256"


def get_user(user_email, db: Session = Depends(get_db)):
    return db.query(User).filter(User.email == user_email).first()


def hash_password(password):
    return pwd_context.hash(password)


def validate_password(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)


def create_user_token(payload: dict, key=SECRET_KEY, expire_minute=TIME_EXPIRE_MINUTES):
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minute)
    payload.update({"exp": expire})
    token = jwt.encode(to_encode, key, algorithm=ALGORITHM)

    return token


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), key=SECRET_KEY
):
    user_decoded = jwt.decode(token, key, algorithms=ALGORITHM)
    user_email = user_decoded.get("sub")
    user = db.query(User).filter(User.email == user_email).first()

    return user
