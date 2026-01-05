from app.core.security import get_current_user
from app.db.db import Base
from app.db.session import get_db
from .utils import engine, TestingSessionLocal, client
from app.models.models import Board, User
import pytest
from app.main import app
from fastapi import status


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


def test_board_add():
    response = client.post(
        "/board", json={"title": "testboard", "description": "still a testboard"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get("title") == "testboard"


def test_board_by_id_found():
    client.post(
        "/board", json={"title": "testboard", "description": "still a testboard"}
    )
    response = client.get("/board/1")

    assert response.status_code == status.HTTP_200_OK


def test_board_by_id_not_found():
    response = client.get("/board/1")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_board_delete():
    client.post(
        "/board", json={"title": "testboard", "description": "still a testboard"}
    )
    response = client.delete("/board/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_board_update():
    client.post(
        "/board", json={"title": "testboard", "description": "still a testboard"}
    )
    response = client.put(
        "/board/1",
        json={
            "title": "updated testboard",
            "description": "still a testboard, yet, an updated one",
        },
    )

    assert response.status_code == status.HTTP_200_OK


def test_board_user_assign(setup_and_teardown):
    db = setup_and_teardown
    client.post(
        "/board", json={"title": "testboard", "description": "still a testboard"}
    )
    user_query = client.post(
        "/auth/registration",
        json={
            "first_name": "Ben",
            "last_name": "Dover",
            "email": "bendover",
            "password": "4321",
        },
    )
    user = (
        db.query(User)
        .filter(User.email == user_query.json().get("User").get("email"))
        .first()
    )
    response = client.post("/board/1/users/?user_email=bendover")
    board = db.query(Board).filter(Board.id == response.json().get("id")).first()

    assert response.status_code == status.HTTP_200_OK
    assert user in board.users_assigned
