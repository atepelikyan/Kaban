import pytest
from fastapi import status
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import Board, User
from .utils import Base, engine, app, TestingSessionLocal, client


@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    user = User(
        id=666, first_name="John", last_name="Doe", email="johndoe", hashed_pwd="1234"
    )
    board = Board(id=1, title="test board", description="test description")
    board.owner = user
    user.boards_assigned.append(board)
    db = TestingSessionLocal()
    db.add(board)
    db.commit()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user

    yield db

    db.close()


def test_add_ticket():
    ticket = {"title": "test ticket", "description": "test description"}
    response = client.post("/ticket", json=ticket, params={"board_id": "1"})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get("board_id") == 1
    assert response.json().get("title") == "test ticket"
    assert response.json().get("description") == "test description"
    assert response.json().get("id") == 1
    assert response.json().get("status") == "to do"


def test_assign_user_to_ticket():
    ticket = {"title": "test ticket", "description": "test description"}
    client.post("/ticket", json=ticket, params={"board_id": "1"})
    response = client.post("/ticket/1/johndoe")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get("board_id") == 1
    assert response.json().get("title") == "test ticket"
    assert response.json().get("description") == "test description"
    assert response.json().get("id") == 1
    assert response.json().get("status") == "to do"


def test_ticket_update():
    ticket = {"title": "test ticket", "description": "test description"}
    client.post("/ticket", json=ticket, params={"board_id": "1"})
    updated_ticket = {
        "title": "updated ticket",
        "description": "updated description",
        "status": "done",
    }
    response = client.put("/ticket/1", json=updated_ticket)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get("title") == updated_ticket.get("title")
    assert response.json().get("description") == updated_ticket.get("description")
    assert response.json().get("status") == updated_ticket.get("status")


def test_ticket_delete():
    ticket = {"title": "test ticket", "description": "test description"}
    client.post("/ticket", json=ticket, params={"board_id": "1"})
    response = client.delete("/ticket/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_ticket_user_unassign():
    ticket = {"title": "test ticket", "description": "test description"}
    client.post("/ticket", json=ticket, params={"board_id": "1"})
    client.post("/ticket/1/johndoe")
    response = client.delete("/ticket/1/johndoe")

    assert response.status_code == status.HTTP_204_NO_CONTENT
