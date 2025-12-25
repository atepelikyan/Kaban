from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.deps.deps import db_dependency
from app.models.models import Board, Ticket, User
from app.schemes.schemes import TicketCreate, TicketUpdate

router = APIRouter(prefix="/ticket", tags=["ticket"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_tickets(logged_user: User = Depends(get_current_user)):
    return logged_user.tickets


@router.post("/{board_id}", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    db: db_dependency,
    board_id: int,
    ticket_form: TicketCreate,
    logged_user: User = Depends(get_current_user),
):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Board no found"
        )
    if logged_user != board.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    new_ticket = Ticket(title=ticket_form.title, description=ticket_form.description)

    board.tickets.append(new_ticket)
    db.commit()

    return new_ticket


@router.post("/{ticket_id}/{user_email}", status_code=status.HTTP_201_CREATED)
async def assign_user(
    db: db_dependency,
    ticket_id: int,
    user_email: str,
    logged_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    if logged_user.email != "admin" or logged_user.email != ticket.board.owner.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detaul="User not found"
        )
    ticket.assigned_users.append(user)
    db.commit()

    return ticket


@router.put("/", status_code=status.HTTP_201_CREATED)
async def update_ticket(ticket_id: int, ticket_form: TicketUpdate, db: db_dependency):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no found"
        )
    if ticket_form.title is not None:
        ticket.title = ticket_form.title
    if ticket_form.description is not None:
        ticket.description = ticket_form.description
    ticket.status = ticket_form.status
    db.add(ticket)
    db.commit()

    return ticket


@router.delete("/", status_code=status.HTTP_201_CREATED)
async def delete_ticket(ticket_id: int, db: db_dependency):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no found"
        )
    db.delete(ticket)
    db.commit()

    return "done"


@router.delete("/{ticket_id}/{user_email}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_user(
    db: db_dependency,
    ticket_id: int,
    user_email: str,
    logged_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    if logged_user.email != "admin" or logged_user.email != ticket.board.owner.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detaul="User not found"
        )
    ticket.assigned_users.remove(user)
    db.commit()

    return "done"
