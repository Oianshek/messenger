from typing import List
from pydantic import BaseModel

from schemas.message_schema import Message


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True
