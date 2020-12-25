from fastapi import HTTPException
from asyncpg import connection

import json

from ..schemas.article_schema import *
from ..schemas.user_schema import UserInfo


class ArticleManager:

    @classmethod
    async def add_article(cls, conn: connection, article: ArticleCreation, user: UserInfo) -> int:
        async with conn.transaction():
            try:
                s = await conn.fetchrow(
                    'insert into public."Article" (title, content, user_id) values ($1, $2, $3) returning id',
                    article.title, article.content, user.id)

                if not s['id']:
                    raise Exception()
            except:
                raise HTTPException(400, 'Bad info')

            try:
                tags = await conn.fetch('select id, name, description from public."Tag" where name = ANY($1::text[])',
                                        article.tags)
                print(tags)
                tags = list(dict(i) for i in tags)
                print(tags)

                for tag in tags:
                    t = await conn.fetchrow(
                        'insert into public."Article_Tag" (article_id, tag_id) values ($1, $2) returning article_id',
                        s['id'], tag.get('id')
                    )

                    if not t['article_id']:
                        raise Exception()
            except Exception as e:
                raise e
                raise HTTPException(400, 'Tags are incorrect')

        return s['id']

    @classmethod
    async def upd_article(cls, conn: connection, article_upd: ArticleUpdate) -> ArticleInfo:

        article = await cls.get_article_by_id(conn, article_upd.id)

        async with conn.transaction():
            res = await conn.fetchval('update public."Article" set'
                                '  title = $1, content = $2, is_private = $3'
                                '  where id = $4 returning id',
                                article_upd.title, article_upd.content, article_upd.is_private, article_upd.id)

            if not res:
                raise HTTPException(400, 'Not updated')

            to_add_tags = list(i for i in article_upd.tags if i not in article.tags)

            to_add_tags = await conn.fetch('select id from public."Tag" where name = ANY($1::text[])',
                                           to_add_tags)

            to_add_tags = list(i['id'] for i in to_add_tags)

            for i in to_add_tags:
                if not await conn.fetchval(
                    'insert into public."Article_Tag" (article_id, tag_id) values ($1, $2) returning article_id',
                    article_upd.id, i
                ):
                    raise HTTPException(400, "Error adding tags")

            to_del_tags = list(i for i in article.tags if i not in article_upd.tags)

            to_del_tags = await conn.fetch('select id from public."Tag" where name = ANY($1::text[])',
                                           to_del_tags)

            to_del_tags = list(i['id'] for i in to_del_tags)

            for i in to_del_tags:
                if not await conn.fetchval(
                    'delete from public."Article_Tag" where article_id = $1 and tag_id = $2 returning article_id',
                    article_upd.id, i
                ):
                    raise HTTPException(400, 'Error deleting tags')

        return await cls.get_article_by_id(conn, article_upd.id)

    @classmethod
    async def del_article(cls, conn: connection, article_id: int) -> int:
        try:
            return await conn.fetchval('delete from public."Article" where id = $1 returning id', article_id)
        except:
            raise HTTPException(400, 'Cant delete article')

    @classmethod
    async def get_article_by_id(cls, conn: connection, article_id: int):
        try:

            article = await conn.fetchrow('select * from public."Article" where id = $1', article_id)

            if not article:
                raise Exception()

            article = dict(article)

            tags = await conn.fetch('select * from public."Tag" '
                                    'where id in '
                                    '(select tag_id from public."Article_Tag" '
                                    'where article_id = $1)', article_id)

            tags = list(i['name'] for i in tags)

            article['tags'] = tags

            user = await conn.fetchrow('select * from public."User" where id = $1', article.get('user_id'))

            article['author'] = UserInfo(**dict(user))

            return ArticleInfo(**article)
        except:
            raise HTTPException(400, "Bad request")

    @classmethod
    async def get_my_articles(cls, conn: connection, user_id: int, *, limit: int = 10, offset: int = 0) -> List[
        ArticleInfo]:
        try:
            articles = await conn.fetch('''select to_json(r) from ( select art.*,
            json_build_object(
                'id', usr.id,
                'full_name', usr.full_name,
                'username', usr.username,
                'is_active', usr.is_active,
                'is_super', usr.is_super,
                'registered', usr.registered
            )             as author,
            json_agg(tg.name) as tags
                from public."Article" art
                join public."User" usr on art.user_id = usr.id
                join public."Article_Tag" a_t on art.id = a_t.article_id
                join public."Tag" tg on a_t.tag_id = tg.id
                where art.user_id = $1
            group by art.id, usr.id
            order by art.modified desc
            limit $2 offset $3) r''', user_id, limit, offset)

            from pprint import pprint

            l = [json.loads(i['to_json']) for i in articles]

            return l
        except:
            raise HTTPException(400, 'Nothin here')

    @classmethod
    async def get_articles(cls, conn: connection, *, limit: int = 10, offset: int = 0) -> List[ArticleInfo]:
        try:
            articles = await conn.fetch('''select to_json(r) from ( select art.*,
            json_build_object(
                'id', usr.id,
                'full_name', usr.full_name,
                'username', usr.username,
                'is_active', usr.is_active,
                'is_super', usr.is_super,
                'registered', usr.registered
            )             as author,
            json_agg(tg.name) as tags
                from public."Article" art
                join public."User" usr on art.user_id = usr.id
                join public."Article_Tag" a_t on art.id = a_t.article_id
                join public."Tag" tg on a_t.tag_id = tg.id
            group by art.id, usr.id
            order by art.modified desc
            limit $1 offset $2) r''', limit, offset)

            from pprint import pprint

            l = [json.loads(i['to_json']) for i in articles]

            return l
        except:
            raise HTTPException(400, 'Nothin here')
