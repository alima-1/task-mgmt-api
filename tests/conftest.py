from dotenv import load_dotenv
import os
from sqlalchemy import URL
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport

from src.task_mgmt_api.main import app
from src.task_mgmt_api.database import Base, get_session


load_dotenv()
TEST_DB_URL = URL.create(
    drivername=os.environ["TEST_DB_DRIVER"],
    username=os.environ["TEST_DB_USER"],
    password=os.environ["TEST_DB_PASSWORD"],
    host=os.environ["TEST_DB_HOST"],
    port=os.environ["TEST_DB_PORT"],
    database=os.environ["TEST_DB_NAME"]
) 
assert "test" in str(TEST_DB_URL), "Test database URL must contain 'test' to prevent accidental use of production database."  

engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
async_session = async_sessionmaker(bind=engine,expire_on_commit=False) 

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def async_session():
    async with async_session() as session:
        yield session 

@pytest_asyncio.fixture
async def override_session(async_session):
    async def override_get_session():
        yield async_session
    app.dependency_overrides[get_session] = override_get_session
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client(override_session):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http/test"
    ) as clt:
        yield clt


