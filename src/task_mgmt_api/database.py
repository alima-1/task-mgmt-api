from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from sqlalchemy import URL
from collections.abc import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

class Base(DeclarativeBase):
    pass    


def _get_db_credentials():
    user = os.getenv("DB_USER")
    pwd = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT"))
    db = os.getenv("DB_NAME")
    drivername = os.getenv("DB_DRIVER")
    if not user or not pwd:
        raise RuntimeError("Database credentials not set. Set DB_USER and DB_PASSWORD environment variables.")
    return user, pwd, host, port, db, drivername

engine = None
async_session_factory = None

def init_db():
    global engine, async_session_factory
    user, pwd, host, port, db, drivername = _get_db_credentials()
    database_url = URL.create(
        drivername=drivername,
        username=user,
        password=pwd,
        host=host,
        port=port,
        database=db,
    )
    engine = create_async_engine(database_url, echo=True)
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def close_db():
    global engine
    if engine:
        await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    global async_session_factory
    if async_session_factory is None:
        raise RuntimeError("Database session factory is not initialized.")
    async with async_session_factory() as session:
        yield session