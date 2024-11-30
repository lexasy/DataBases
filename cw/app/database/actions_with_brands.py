from database.connect import create_connection, close_connection
from schemas.brand import Brand
import asyncio

async def get_all_brands():
    conn = await create_connection()
    try:
        query = """
            SELECT name FROM brand
        """
        brands = await conn.fetch(query)
        result = [brand['name'] for brand in brands]
        return result
    finally:
        await close_connection(conn)

async def add_new_brand(brand: Brand):
    conn = await create_connection()
    try:
        query = """
            INSERT INTO brand (name, description) VALUES ($1, $2)
        """
        await conn.execute(query, brand.name, brand.description)
    finally:
        await close_connection(conn)

# asyncio.run(get_all_brands())