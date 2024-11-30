import os
import asyncpg
import asyncio
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

async def create_connection() -> asyncpg.Connection:
    try:
        connection = await asyncpg.connect(**DB_CONFIG)
    except ConnectionError as e:
        return None
    return connection

async def close_connection(connection: asyncpg.Connection):
    await connection.close()

