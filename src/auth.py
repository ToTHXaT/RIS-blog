from typing import Optional

from fastapi.security.api_key import APIKeyCookie
from fastapi import Security, APIRouter, Response, Request, Depends
from fastapi.exceptions import HTTPException

from src.schemas.user_schema import UserInfo, UserAuth, UserCreation

from .managers.user_manager import UserManager
from .managers.session_manager import SessionManager

from .config import API_KEY_NAME, TOKEN_EXPIRE_TIME

api_key = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


async def get_current_user(request: Request, token: Optional[str] = Security(api_key)):
    user = await SessionManager.get_user(request.state.db, token)

    return user

auth = APIRouter()


@auth.get('/me')
async def me(user: UserInfo = Depends(get_current_user)):
    return user.dict()


@auth.post('/login')
async def login(user_auth: UserAuth, response: Response, request: Request):

    if not await UserManager.authenticate(request.state.db, user_auth):
        raise HTTPException(status_code=400, detail='Invalid credentials')

    user = await UserManager.get_by_username(request.state.db, user_auth.username)

    token = await SessionManager.add_session(request.state.db, user.id)

    response.set_cookie(key=API_KEY_NAME, value=token, max_age=TOKEN_EXPIRE_TIME)

    return user


@auth.post('/signup')
async def signup(request: Request, user_creation: UserCreation, response: Response):

    user = await UserManager.create(request.state.db, user_creation)

    token = await SessionManager.add_session(request.state.db, user.id)

    response.set_cookie(key=API_KEY_NAME, value=token, max_age=TOKEN_EXPIRE_TIME)

    return user


@auth.post('/logout')
async def logout(response: Response, request: Request, token: Optional[str] = Security(api_key)):

    await SessionManager.del_session(request.state.db, token)
    response.delete_cookie(key='token')
    return {'success': True}







