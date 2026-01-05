from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]
