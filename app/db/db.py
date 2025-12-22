from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

db_url = "postgresql+psycopg2://postgres:bibishun666@localhost:5432/kaban"
engine = create_engine(db_url)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()