from app.db.db import Base, engine
from app.models.models import User


def init_models():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_models()