from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.deps.deps import get_db
from app.models.models import Board, User
from app.schemes.schemes import BoardCreate, BoardUpdate

router = APIRouter(prefix="/board", tags=["board"])

@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_boards(logged_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if logged_user.first_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    boards = db.query(Board).all()

    return boards

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_board(board: BoardCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    new_board = Board(title=board.title, description=board.description)
    new_board.owner = user
    new_board.users_assigned.append(user)
    db.add(new_board)
    db.commit()
    db.refresh(new_board)

    return new_board

@router.get("/{board_id}", status_code=status.HTTP_200_OK)
async def get_board(board_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Board not present")
    if user not in board.users_assigned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    return board

@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(board_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Board not present")
    if board.owner.email != user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    db.delete(board)
    db.commit()

    return "done"

@router.put("/{board_id}", status_code=status.HTTP_200_OK)
async def update_user(board_id: int, board_update: BoardUpdate, logged_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    if logged_user.email != board.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    board.title = board_update.title
    board.description = board_update.description

    return board
    
    
@router.post("/{board_id}/users", status_code=status.HTTP_200_OK)
async def add_user_to_board(board_id: int, user_email: str, logged_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    if logged_user != board.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    board.users_assigned.append(user)

    return board