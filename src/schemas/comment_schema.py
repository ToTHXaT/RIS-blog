from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field

from .user_schema import UserInfo


class Comment(BaseModel):
    content: str
    article_id: int


class CommentCreation(Comment):
    pass


class CommentUpdate(BaseModel):
    id: int
    content: str


class CommentInfo(Comment):
    id: int
    added: datetime
    user: UserInfo

