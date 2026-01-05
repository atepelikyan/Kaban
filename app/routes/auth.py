from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import (
    create_user_token,
    get_user,
    hash_password,
    validate_password,
)
from app.deps.deps import db_dependency, user_dependency
from app.models.models import User
from app.schemes.schemes import UserCreate

router = APIRouter(prefix="/auth", tags=["authorization"])


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(form_data: UserCreate, db: db_dependency):
    if get_user(form_data.email, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="the user is already registrated",
        )

    hashed_password = hash_password(form_data.password)
    new_user = User(
        first_name=form_data.first_name,
        last_name=form_data.last_name,
        email=form_data.email,
        hashed_pwd=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"User": new_user}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username, db)
    if not user or not validate_password(form_data.password, user.hashed_pwd):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="bad credentials"
        )
    token = create_user_token(payload={"sub": form_data.username})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", status_code=status.HTTP_200_OK)
async def current_user(user: user_dependency):
    return user
