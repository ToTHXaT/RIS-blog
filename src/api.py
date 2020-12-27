from typing import *
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from random import randint

from asyncpg import connection
from .managers.article_manager import ArticleManager
from .managers.comment_manager import CommentManager
from .schemas.comment_schema import CommentInfo, CommentUpdate, CommentCreation

from src.schemas.article_schema import ArticleCreation, ArticleUpdate, ArticleInfo
from src.schemas.user_schema import UserInfo
from .auth import get_current_user


api = APIRouter()


async def random_number() -> int:
    return randint(0, 100)


@api.get("/")
async def index(request: Request):
    print(await request.state.db.fetch('select * from public."User"'))
    return None


@api.get("/tags/get", response_model=List[str])
async def get_tags(request: Request):
    return await ArticleManager.get_tags(request.state.db)


@api.get("/articles/get", response_model=List[ArticleInfo])
async def get_articles(request: Request, limit: Optional[int] = 10, offset: Optional[int] = 0):
    return await ArticleManager.get_articles(request.state.db, limit=limit, offset=offset)


@api.get("/articles/len", response_model=int)
async def get_articles__len(request: Request):
    return await ArticleManager.get_articles__len(request.state.db)


@api.get("/articles/get/my", response_model=List[ArticleInfo])
async def get_articles(request: Request,
                       user: UserInfo = Depends(get_current_user),
                       limit: Optional[int] = 10, offset: Optional[int] = 0):
    return await ArticleManager.get_my_articles(request.state.db, user.id, limit=limit, offset=offset)


@api.get("/articles/len/my", response_model=int)
async def get_articles(request: Request, user: UserInfo = Depends(get_current_user)):
    return await ArticleManager.get_my_articles__len(request.state.db, user.id)


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


@api.delete("/article/del", response_model=int)
async def del_article(article_id: int, request: Request, user: UserInfo = Depends(get_current_user)):
    article = await ArticleManager.get_article_by_id(request.state.db, article_id)
    if article.author.id == user.id:
        return await ArticleManager.del_article(request.state.db, article_id)
    else:
        raise HTTPException(400, 'Permissoin denied')


@api.get("/comments/get", response_model=List[CommentInfo])
async def get_comments(request: Request, article_id: int, limit: Optional[int] = 10, offset: Optional[int] = 0):
    return await CommentManager.get_comments_of_article(request.state.db, article_id, limit=limit, offset=offset)


@api.put("/comment/upd", response_model=CommentInfo)
async def upd_articles_comment(request: Request, comment_upd: CommentUpdate, user: UserInfo = Depends(get_current_user)):
    comment = await CommentManager.get_comment_by_id(request.state.db, comment_upd.id)

    if comment.user.id == user.id:
        return await CommentManager.upd_comment_of_article(request.state.db, comment_upd)
    else:
        raise HTTPException(400, 'Permission denied')


@api.post("/comment/add", response_model=CommentInfo)
async def get_comments(request: Request, comment: CommentCreation, user: UserInfo = Depends(get_current_user)):
    return await CommentManager.add_comment(request.state.db, comment, user)


@api.delete("/comment/del", response_model=int)
async def del_comment(request: Request, comment_id: int, user: UserInfo = Depends(get_current_user)):
    comment = await CommentManager.get_comment_by_id(request.state.db, comment_id)

    if comment.user.id == user.id:
        return await CommentManager.del_comment(request.state.db, comment_id)
    else:
        raise HTTPException(400, 'Permission denied')

