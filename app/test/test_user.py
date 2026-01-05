import pytest
from fastapi import status
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import Board, Ticket, User
from .utils import (
    Base,
    TestingSessionLocal,
    engine,
    override_get_current_user,
    override_get_db,
    client,
)
from app.main import app


@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    user = User(
        id=666, first_name="John", last_name="Doe", email="johndoe", hashed_pwd="1234"
    )
    board = Board(id=1, title="test board", description="test description")
    ticket = Ticket(id=1, title="test ticket", description="still a test ticket")
    board.owner = user
    board.tickets.append(ticket)
    user.boards_assigned.append(board)
    user.tickets.append(ticket)
    db.add_all([user, board, ticket])
    db.commit()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    yield db

    db.close()


def test_get_user_boards():
    response = client.get("/user/johndoe/boards")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_update_user():
    updated_user = {"first_name": "Ben", "last_name": "Dover"}
    response = client.put("/user/johndoe", json=updated_user)

    assert response.json().get("first_name") == "Ben"
    assert response.json().get("last_name") == "Dover"


def test_delete_user_board():
    response = client.delete("/user/johndoe/boards/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_user():
    response = client.delete("/user/johndoe")

    assert response.status_code == status.HTTP_204_NO_CONTENT
