from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field

from .user_schema import UserInfo


class Article(BaseModel):
    title: str
    content: str
    tags: List[str]


class ArticleCreation(Article):
    pass


class ArticleInfo(Article):
    id: int
    published: datetime
    modified: datetime
    author: UserInfo


class ArticleUpdate(Article):
    id: int
    title: str
    content: str
    tags: List[str]
    is_private: bool