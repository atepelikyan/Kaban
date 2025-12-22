from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_user_token, get_current_user, get_user, hash_password, validate_password
from app.models.models import Board, User
from app.deps.deps import get_db
from app.schemes.schemes import BoardCreate, BoardDelete, UserCreate

app = FastAPI()

@app.get("/")
async def main():
    return "Welcome to kaban!"

@app.post("/registration")
async def registration(form_data: UserCreate, db: Session = Depends(get_db)):
    if get_user(form_data.email, db):
        raise HTTPException(status_code=409, detail="the user is already registrated")
    
    hashed_password = hash_password(form_data.password)
    new_user = User(first_name=form_data.first_name, last_name=form_data.last_name, email=form_data.email, hashed_pwd=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"User" : new_user}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(form_data.username, db)
    if not user or not validate_password(form_data.password, user.hashed_pwd):
        raise HTTPException(status_code=401, detail="bad credentials")
    token = create_user_token(payload={"sub" : form_data.username})

    return {"access_token" : token, "token_type": "bearer"}

@app.get("/me")
async def current_user(user: User = Depends(get_current_user)):
    return user

@app.get("/get_board/{board_id}")
async def get_board(board_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=400, detail="Board not present")
    if user not in board.users_assigned:
        raise HTTPException(status_code=403, detail="Not enough privelages")
    
    return board

@app.post("/create_board")
async def create_board(board: BoardCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    new_board = Board(title=board.title, description=board.description)
    new_board.owner = user
    new_board.users_assigned.append(user)
    db.add(new_board)
    db.commit()
    db.refresh(new_board)

    return new_board

@app.delete("/delete_board/{board_id}")
async def delete_board(board_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=400, detail="Board not present")
    if board.owner.email != user.email:
        raise HTTPException(status_code=403, detail="Not enough privelages")
    db.delete(board)
    db.commit()

    return "done"
    
@app.post("/add_user/{board_id}")
async def add_user(board_id: int, user_email: str, curren_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if current_user != board.owner:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    board.users_assigned.append(user)

    return board


#uvicorn, imports, service, repository, add router