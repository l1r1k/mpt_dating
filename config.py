from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

TG_API=os.getenv('TG_API')
DB_HOST=os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')
DB_USER=os.getenv('DB_USER')
DB_PASS=os.getenv('DB_PASS')
DB_NAME=os.getenv('DB_NAME')

CONNECTION_STRING=f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

async_angine = create_async_engine(CONNECTION_STRING)

session_factory = async_sessionmaker(async_angine)