from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.deps.deps import get_db
from app.models.models import Board, User
from app.schemes.schemes import UserUpdate

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/", status_code=status.HTTP_200_OK)
async def get_my_boards(logged_user: User = Depends(get_current_user)):
    return logged_user

@router.get("/{user_email}/boards", status_code=status.HTTP_200_OK)
async def get_users_board(user_email: str, logged_user: User = Depends(get_current_user)):
    if logged_user != user_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if logged_user.email != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    return logged_user.boards_assigned

@router.put("/{user_email}")
async def update_user(user_email: str, update_data: UserUpdate, logged_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if logged_user.email != user_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    logged_user.first_name = update_data.first_name
    logged_user.last_name = update_data.last_name

    db.commit()

    return logged_user



@router.delete("/{user_email}/boards/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_board(id: int, user_email:str, logged_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    board = db.query(Board).filter(Board.id == id).first()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    if user not in board.users_assigned:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in the board")
    if logged_user.email != "admin" or logged_user.email != board.owner.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    board.users_assigned.remove(user)