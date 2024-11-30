from database.connect import create_connection, close_connection
from schemas.category import Category
import asyncio

async def get_all_categories():
    conn = await create_connection()
    try:
        query = """
            SELECT name FROM category
        """
        categories = await conn.fetch(query)
        result = [category['name'] for category in categories]
        return result
    finally:
        await close_connection(conn)

async def add_new_category(category: Category):
    conn = await create_connection()
    try:
        query = """
            INSERT INTO category (name, description) VALUES ($1, $2)
        """
        await conn.execute(query, category.name, category.description)
    finally:
        await close_connection(conn)

# asyncio.run(get_all_categories())