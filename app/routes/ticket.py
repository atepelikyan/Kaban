from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.deps.deps import get_db
from app.models.models import Board, Ticket, User
from app.schemes.schemes import TicketCreate, TicketUpdate

router = APIRouter(prefix="ticket", tags=["ticket"])

@router.get("/", status_code=status.HTTP_200_OK)
async def get_tickets(logged_user: User = Depends(get_current_user)):
    return logged_user.tickets

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ticket(board_id: int, ticket_form: TicketCreate, db: Session = Depends(get_db)):
    new_ticket = Ticket(title=ticket_form.title, description=ticket_form.description)
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board no found")
    
    board.tickets.append(new_ticket)

    return new_ticket

@router.put("/", status_code=status.HTTP_201_CREATED)
async def update_ticket(ticket_id: int, ticket_form: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no found")
    if ticket_form.title is not None:
        ticket.title = ticket_form.title
    if ticket_form.description is not None:
        ticket.description = ticket_form.description
    ticket.status = ticket_form.status
    
    db.commit()

    return ticket

@router.delete("/", status_code=status.HTTP_201_CREATED)
async def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no found")
    db.delete(ticket)
    db.commit()
    

    return "done"