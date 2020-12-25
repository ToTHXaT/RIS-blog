from datetime import datetime

from fastapi import HTTPException

from ..mock_users import users
from src.schemas.user_schema import UserInfo, UserCreation, UserAuth, UserFullInfo

from asyncpg import connection
from passlib.context import CryptContext
from passlib.exc import UnknownHashError


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)


for i in users:
    i['password'] = pwd_context.encrypt(i['password'])


class UserManager:

    @classmethod
    async def get_by_id(cls, conn: connection, id: int) -> UserInfo:
        try:
            user = await conn.fetchrow('select * from public."User" where id = $1', id)
        except:
            raise HTTPException(400, 'User not found')

        return UserInfo(**dict(user))

    @classmethod
    async def get_by_username(cls, conn: connection, username: str) -> UserInfo:
        try:
            user = await conn.fetchrow('select * from public."User" where username = $1', username)
        except:
            raise HTTPException(400, 'User not found')

        return UserInfo(**dict(user))

    @classmethod
    async def create(cls, conn: connection, _user: UserCreation) -> UserInfo:

        try:
            await conn.execute('insert into public."User_mod" (username, password, full_name) values'
                         '($1, $2, $3)',
                         _user.username, pwd_context.encrypt(_user.password), _user.full_name or 'Anonimus')
        except Exception as e:
            raise HTTPException(400, 'Invalid data for user creation')

        user = await cls.get_by_username(conn, _user.username)

        return UserInfo(**dict(user))

    @classmethod
    async def check_username(cls, conn: connection, username: str) -> bool:

        try:
            num = await conn.fetchval('select count(id) from public."User" where username = $1', (username))
            return not num
        except:
            return False


    @classmethod
    async def authenticate(cls, conn: connection, _user: UserAuth) -> bool:
        try:
            user = await conn.fetchrow('select * from public."User" where username = $1', _user.username)
        except:
            raise HTTPException(400, 'User not found')

        try:
            return pwd_context.verify(_user.password, user['password'])
        except UnknownHashError:
            raise HTTPException(400, 'Wrong credentials')
