from typing import *
from uuid import uuid4
from datetime import datetime, timedelta
from ..mock_users import sessions
from fastapi import HTTPException

from asyncpg import connection

from ..schemas.user_schema import UserInfo
from ..config import TOKEN_EXPIRE_TIME


class SessionManager:

    @classmethod
    async def add_session(cls, conn: connection, user_id: int) -> str:
        token = uuid4().hex

        try:
            s = await conn.execute('insert into public."Session" (token, expires, user_id) values ($1, $2, $3)',
                               token, datetime.now() + timedelta(seconds=TOKEN_EXPIRE_TIME), user_id)
        except:
            raise HTTPException(400, 'Cant create new session')

        return token

    @classmethod
    async def del_session(cls, conn: connection, token: str):

        try:
            s = await conn.execute('delete from public."Session" where token = $1', token)
            print(s)
        except:
            raise HTTPException(400, 'Not authenticated')

        if int(s.split()[1]) == 0:
            raise HTTPException(400, 'Not authenticated')


    @classmethod
    async def get_user(cls, conn: connection, token: str) -> UserInfo:
        try:
            user = await conn.fetchrow('select * from public."User" '
                                        'where id in '
                                        '(select user_id from public."Session" where token = $1 and NOW() < expires)',
                                        token)

            if not user:
                raise Exception()
        except:
            raise HTTPException(400, 'Not authenticated')

        return UserInfo(**dict(user))
