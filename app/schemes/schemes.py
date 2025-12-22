from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class BoardCreate(BaseModel):
    title: str
    description: str

class BoardDelete(BaseModel):
    id: int    