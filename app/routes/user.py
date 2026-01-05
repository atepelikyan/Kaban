from fastapi import APIRouter, HTTPException, status
from app.deps.deps import db_dependency, user_dependency
from app.models.models import Board, User
from app.schemes.schemes import UserUpdate

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/all_user", status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency):
    return db.query(User).all()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_my_boards(logged_user: user_dependency):
    return logged_user


@router.get("/{user_email}/boards", status_code=status.HTTP_200_OK)
async def get_users_board(
    user_email: str, logged_user: user_dependency, db: db_dependency
):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if logged_user.email != user_email and logged_user.email != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return user.boards_assigned


@router.put("/{user_email}")
async def update_user(
    db: db_dependency,
    user_email: str,
    update_data: UserUpdate,
    logged_user: user_dependency,
):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if logged_user.email != user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    user.first_name = update_data.first_name
    user.last_name = update_data.last_name
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_email}/boards/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_board(
    db: db_dependency,
    id: int,
    user_email: str,
    logged_user: user_dependency,
):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    board = db.query(Board).filter(Board.id == id).first()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Board not found"
        )
    if user not in board.users_assigned:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found in the board"
        )
    if logged_user.email != "admin" and logged_user.email != board.owner.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    board.users_assigned.remove(user)
    db.commit()


@router.delete("/{user_email}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user_email: str, logged_user: user_dependency):
    if logged_user.email != "admin" and logged_user.email != user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            stattus_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()
