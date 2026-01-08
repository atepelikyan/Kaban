from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import User
from app.db.db import Base
from app.main import app


SQLALCHEMY_DATABASE_URL = "sqlite:///app/testdb.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return User(
        id=666, first_name="John", last_name="Doe", email="johndoe", hashed_pwd="1234"
    )


client = TestClient(app)
