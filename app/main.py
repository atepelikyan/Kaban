from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_user_token, get_current_user, get_user, hash_password, validate_password
from app.models.models import Board, User
from app.deps.deps import get_db
from app.schemes.schemes import BoardCreate, BoardDelete, BoardUpdate, UserCreate

app = FastAPI()

@app.get("/")
async def main():
    return "Welcome to kaban!"
    
#uvicorn, imports, service, repository, add router
#tickets - create, get, update, delete, assign to, see one, see all, see your, see assigned to someone, mark