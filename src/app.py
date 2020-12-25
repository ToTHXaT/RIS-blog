from pprint import pprint
from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import asyncpg

from .api import api
from .auth import auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
        'http://localhost:5000',
        'http://localhost:8000',
        'http://qeyn.site:80'
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


pool: asyncpg.pool


@app.on_event('startup')
async def set_pools():
    global pool
    print("Creating pool")
    pool = await asyncpg.create_pool(min_size=2, max_size=5, max_inactive_connection_lifetime=300,
                                     user='dev', password='1234', database='RIS-blog', host='127.0.0.1')
    print("Created pool")


@app.on_event('shutdown')
async def shutdown():
    global pool
    print("Closing pool")
    await pool.close()
    print("Closed pool")


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    try:
        request.state.db = await pool.acquire()
        response = await call_next(request)
    finally:
        await pool.release(request.state.db)
    return response


app.include_router(api, prefix='/api', tags=['api'])
app.include_router(auth, prefix='/auth', tags=['auth'])

