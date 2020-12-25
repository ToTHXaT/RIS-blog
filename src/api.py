from typing import *
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from random import randint

from asyncpg import connection
from .managers.article_manager import ArticleManager

from src.schemas.article_schema import ArticleCreation, ArticleUpdate, ArticleInfo
from src.schemas.user_schema import UserInfo
from .auth import get_current_user


api = APIRouter()


articles = [
    {'id': 1, 'title': 'hello',  'body': 'hello ob', 'pub_date': datetime.now()},
    {'id': 2, 'title': 'hello2', 'body': 'hello ob', 'pub_date': datetime.now()},
    {'id': 3, 'title': 'hello3', 'body': 'hello ob', 'pub_date': datetime.now()},
    {'id': 4, 'title': 'hello4', 'body': 'hello ob', 'pub_date': datetime.now()},
    {'id': 5, 'title': 'hello5', 'body': 'hello ob', 'pub_date': datetime.now()},
]


async def random_number() -> int:
    return randint(0, 100)


@api.get("/")
async def index(request: Request):
    print(await request.state.db.fetch('select * from public."User"'))
    return None


@api.get("/articles/get", response_model=List[ArticleInfo])
async def get_articles(request: Request, limit: Optional[int] = 10, offset: Optional[int] = 0):
    return await ArticleManager.get_articles(request.state.db, limit=limit, offset=offset)


@api.get("/articles/get/my", response_model=List[ArticleInfo])
async def get_articles(request: Request,
                       user: UserInfo = Depends(get_current_user),
                       limit: Optional[int] = 10, offset: Optional[int] = 0):
    return await ArticleManager.get_my_articles(request.state.db, user.id, limit=limit, offset=offset)


@api.get("/article/get/", response_model=ArticleInfo)
async def get_article(request: Request, id: int):
    return await ArticleManager.get_article_by_id(request.state.db, id)


@api.post("/article/add")
async def add_article(request: Request, article: ArticleCreation, user: UserInfo = Depends(get_current_user)):
    article_id = await ArticleManager.add_article(request.state.db, article, user)

    return await ArticleManager.get_article_by_id(request.state.db, article_id)


@api.put("/article/upd")
async def upd_article(request: Request, article_upd: ArticleUpdate, user: UserInfo = Depends(get_current_user)):
    article = await ArticleManager.get_article_by_id(request.state.db, article_upd.id)
    if article.author.id == user.id:
        return await ArticleManager.upd_article(request.state.db, article_upd)
    else:
        raise HTTPException(400, 'Permission denied')



@api.post("/article/del", response_model=int)
async def del_article(article_id: int, request: Request, user: UserInfo = Depends(get_current_user)):
    article = await ArticleManager.get_article_by_id(request.state.db, article_id)
    if article.author.id == user.id:
        return await ArticleManager.del_article(request.state.db, article_id)
    else:
        raise HTTPException(400, 'Permissoin denied')
