import enum
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    first_name: str = Field(min_length=2, max_length=20)
    last_name: str = Field(min_length=2, max_length=25)
    email: str
    # email: EmailStr
    password: str

class UserUpdate(BaseModel):
    first_name: str = Field(min_length=2, max_length=20)
    last_name: str = Field(min_length=2, max_length=25)
    # email: EmailStr

class BoardCreate(BaseModel):
    title: str
    description: str

class BoardDelete(BaseModel):
    id: int    

class BoardUpdate(BaseModel):
    title: str
    description: str

class TicketStatus(enum.Enum):
    to_do = "to do"
    in_progress = "in progress"
    done = "done"

class TicketCreate(BaseModel):
    title: str
    description: str
    status: TicketStatus = TicketStatus.to_do