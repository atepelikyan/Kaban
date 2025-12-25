from app.db.db import Base, engine
from app.models.models import User, Ticket, Board, user_ticket, board_user


def init_models():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_models()
