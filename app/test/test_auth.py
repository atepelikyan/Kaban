from fastapi import status
import pytest
from app.core.security import validate_password
from app.db.db import Base
from app.db.session import get_db
from app.test.utils import TestingSessionLocal, override_get_db, engine, client
from app.main import app


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    app.dependency_overrides[get_db] = lambda: db

    yield

    db.close()


@pytest.fixture()
def test_user_data():
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe",
        "password": "1234",
    }

    return user_data


def test_registration(test_user_data):
    response = client.post("/auth/registration", json=test_user_data)
    elements = response.json().get("User")

    assert response.status_code == status.HTTP_201_CREATED
    assert elements.get("first_name") == "John"
    assert elements.get("last_name") == "Doe"
    assert elements.get("email") == "johndoe"
    assert validate_password("1234", elements.get("hashed_pwd"))


def test_login(test_user_data):
    registration_response = client.post("/auth/registration", json=test_user_data)
    user_login_data = {
        "username": registration_response.json().get("User").get("email"),
        "password": test_user_data.get("password"),
    }
    response = client.post("/auth/login", data=user_login_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json().get("token_type") == "bearer"
