from typing import List
from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.db import Base

from app.schemes.schemes import TicketStatus

user_ticket = Table(
    "users_tickets",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("ticket_id", ForeignKey("tickets.id"), primary_key=True),
)

board_user = Table(
    "boards_users",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("board_id", ForeignKey("boards.id"), primary_key=True),
)


class BaseModel(Base):
    __allow_unmapped__ = True
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)


class User(BaseModel):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String, nullable=False)
    tickets: Mapped[List["Ticket"]] = relationship(
        back_populates="assigned_users", secondary="users_tickets", cascade="delete"
    )
    boards_owned: Mapped[List["Board"]] = relationship(
        back_populates="owner", cascade="delete"
    )
    boards_assigned: Mapped[List["Board"]] = relationship(
        back_populates="users_assigned", secondary="boards_users"
    )


class Ticket(BaseModel):
    __tablename__ = "tickets"

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus), default=TicketStatus.to_do
    )
    assigned_users: Mapped[List["User"]] = relationship(
        back_populates="tickets", secondary="users_tickets", cascade="delete"
    )
    board: Mapped["Board"] = relationship(back_populates="tickets")
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"))


class Board(BaseModel):
    __tablename__ = "boards"

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    tickets: Mapped[List["Ticket"]] = relationship(
        back_populates="board", cascade="delete"
    )
    owner: Mapped[User] = relationship(back_populates="boards_owned")
    owned_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    users_assigned: Mapped[List["User"]] = relationship(
        back_populates="boards_assigned", secondary="boards_users", cascade="delete"
    )
