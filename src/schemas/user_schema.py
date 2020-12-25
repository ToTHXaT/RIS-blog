from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    username: str = Field(..., max_length=128)


class UserAuth(User):
    password: str = Field(..., max_length=128)


class UserCreation(UserAuth):
    full_name: Optional[str]


class UserInfo(User):
    id: int
    full_name: str
    registered: datetime
    is_super: bool
    is_active: bool


class UserFullInfo(UserInfo):
    password: str = Field(..., max_length=128)
