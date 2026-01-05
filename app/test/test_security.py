from app.db.session import get_db
from app.main import app
from unittest.mock import MagicMock
import pytest
from sqlalchemy import text
from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_user_token,
    get_current_user,
    hash_password,
    validate_password,
)
from app.models.models import User
from jose import jwt

from app.test.utils import TestingSessionLocal, engine, Base


@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    user = User(
        id=666, first_name="John", last_name="Doe", email="johndoe", hashed_pwd="1234"
    )
    db = TestingSessionLocal()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user

    yield db

    db.close()


@pytest.fixture
def test_user():
    user = User(first_name="admin", last_name="admin", email="admin", hashed_pwd="1234")

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute((text("DELETE FROM users;")))
        connection.commit()


@pytest.fixture()
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close


def test_get_user(test_user):
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == test_user.email).first()

    assert user.email == test_user.email


def test_hash_pwd():
    pwd = "aralavara"
    hashed_pwd = hash_password(pwd)
    assert pwd != hashed_pwd
    assert validate_password(pwd, hashed_pwd)
    assert validate_password("lavaralav", hashed_pwd) is False


def test_validate_pwd():
    pwd = "aralavara"
    hashed_pwd = hash_password(pwd)

    assert validate_password(pwd, hashed_pwd)
    assert validate_password("bad password", hashed_pwd) is False
    assert validate_password("Aralavara", hashed_pwd) is False


def test_create_user_token():
    payload = {"sub": "hopar"}
    token = create_user_token(payload)

    payload_decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload_decoded.get("sub") == "hopar"
    assert payload_decoded.get("sub") != "HoPaR"
    assert payload_decoded is not None
    assert "exp" in payload


def test_get_current_user():
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.email = "testuser"

    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    encode = {"sub": "testuser", "id": 1, "role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = get_current_user(db=mock_db, token=token)
    assert user.email == mock_user.email
