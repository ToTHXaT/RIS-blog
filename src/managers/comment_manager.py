from typing import *
from fastapi import HTTPException
from asyncpg import connection

import json

from ..schemas.comment_schema import *


class CommentManager:

    @classmethod
    async def get_comments_of_article(cls, conn: connection, article_id: int, *,
                                      limit: Optional[int] = 10, offset: Optional[int] = 0) -> List[CommentInfo]:
        try:
            comments = await conn.fetch(
                '''select to_json(r) from ( select cm.*, 
                json_build_object(
                        'id', usr.id,
                        'full_name', usr.full_name,
                        'username', usr.username,
                        'is_active', usr.is_active,
                        'is_super', usr.is_super,
                        'registered', usr.registered
                    ) as user
                from public."Comment" cm
                join public."User" usr on cm.user_id = usr.id
                where article_id = $1 
                order by cm.added desc
                limit $2 offset $3) r
                ''', article_id, limit, offset)

            comments = [json.loads(i['to_json']) for i in comments]

            return comments
        except Exception as e:
            raise HTTPException(400, 'Cant get comments')

    @classmethod
    async def upd_comment_of_article(cls, conn: connection, comment: CommentUpdate) -> CommentInfo:
        async with conn.transaction():
            try:
                comment_id = await conn.fetchval(
                    '''update public."Comment"
                    set content = $1, added = NOW()
                    where id = $2 returning id''', comment.content, comment.id)

                return await cls.get_comment_by_id(conn, comment_id)

            except Exception as e:
                raise HTTPException(400, 'Cant update comment')

    @classmethod
    async def get_comment_by_id(cls, conn: connection, comment_id) -> CommentInfo:
        try:
            comments = await conn.fetchrow(
                '''select to_json(r) from ( select cm.*, 
                json_build_object(
                        'id', usr.id,
                        'full_name', usr.full_name,
                        'username', usr.username,
                        'is_active', usr.is_active,
                        'is_super', usr.is_super,
                        'registered', usr.registered
                    ) as user
                from public."Comment" cm
                join public."User" usr on cm.user_id = usr.id
                where cm.id = $1 
                order by cm.added
                limit 1) r
                ''', comment_id)

            comments = json.loads(comments['to_json'])

            if not comments:
                raise Exception('There is no such comment')

            return CommentInfo(**comments)
        except Exception as e:
            raise HTTPException(400, 'There is no such comment')

    @classmethod
    async def add_comment(cls, conn: connection, comment: CommentCreation, user: UserInfo) -> CommentInfo:
        async with conn.transaction():
            try:
                comment_id = await conn.fetchval('''
                insert into public."Comment" (content, article_id, user_id) values ($1, $2, $3) returning id
                ''', comment.content, comment.article_id, user.id)

                return await cls.get_comment_by_id(conn, comment_id)
            except:
                raise HTTPException(400, 'Cant add comment')

    @classmethod
    async def del_comment(cls, conn: connection, comment_id: int) -> int:
        async with conn.transaction():
            try:
                return await conn.fetchval('''delete from public."Comment" where id = $1 returning id''', comment_id)
            except:
                raise HTTPException(400, 'Cant delete comment')