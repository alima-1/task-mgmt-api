import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()


class Base(DeclarativeBase):
    pass


def _get_db_credentials():
    user = os.getenv("DB_USER")
    pwd = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT", "5432"))
    db = os.getenv("DB_NAME")
    drivername = os.getenv("DB_DRIVER")
    if not user or not pwd:
        raise RuntimeError(
            "Database credentials not set. Set DB_USER and DB_PASSWORD "
            "environment variables."
        )
    return user, pwd, host, port, db, drivername


def enable_ssl_mode():
    mode = os.getenv("DB_SSLMODE")
    return mode


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
    engine = create_async_engine(
        database_url,
        echo=True,
        connect_args={"ssl": True} if enable_ssl_mode() == "require" else {},
    )
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
