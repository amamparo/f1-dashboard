import os
import shutil
import sqlite3
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from esm_fullstack_challenge import __version__
from esm_fullstack_challenge.config import CORS_ORIGINS, DB_FILE
from esm_fullstack_challenge.db.init_auth import init_users_table
from esm_fullstack_challenge.auth import get_current_user
from esm_fullstack_challenge.routers import (
    basic_router, dashboard_router, drivers_router, races_router,
)
from esm_fullstack_challenge.routers.auth import auth_router
from esm_fullstack_challenge.routers.users import users_router

BUNDLED_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.db')


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(DB_FILE) and os.path.exists(BUNDLED_DB):
        db_dir = os.path.dirname(DB_FILE)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        shutil.copy(BUNDLED_DB, DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    try:
        init_users_table(conn)
    finally:
        conn.close()
    yield


app = FastAPI(title="F1 DATA API", version=__version__, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS.split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        'name': app.title,
        'version': app.version,
    }


@app.get("/ping")
def ping():
    return {"ping": "pong"}


auth_deps = [Depends(get_current_user)]

app.include_router(auth_router, prefix='/auth', tags=['Auth'])
app.include_router(users_router, prefix='/users', tags=['Users'], dependencies=auth_deps)
app.include_router(basic_router, prefix='', tags=['Basic'], dependencies=auth_deps)
app.include_router(drivers_router, prefix='/drivers', tags=['Drivers'], dependencies=auth_deps)
app.include_router(races_router, prefix='/races', tags=['Races'], dependencies=auth_deps)
app.include_router(dashboard_router, prefix='/dashboard', tags=['Dashboard'], dependencies=auth_deps)
