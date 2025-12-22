from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.deps.deps import get_db
from app.models.models import Ticket, User
from app.schemes.schemes import TicketCreate

router = APIRouter(prefix="ticket", tags=["ticket"])

@router.get("/", status_code=status.HTTP_200_OK)
async def get_tickets(logged_user: User = Depends(get_current_user)):
    return logged_user.tickets

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket_form: TicketCreate, db: Session = Depends(get_db)):
    new_ticket = Ticket(title=ticket_form.title, description=ticket_form.description)