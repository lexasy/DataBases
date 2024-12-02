from database.connect import create_connection, close_connection
from schemas.appliance import Appliance
import asyncio

async def get_all_products():
    conn = await create_connection()
    try:
        query = """
            SELECT appliance_id, appliance.name, brand.name, category.name, price, quantity_in_stock 
            FROM appliance JOIN brand using(brand_id)
            JOIN category using(category_id);
        """
        products = await conn.fetch(query)
        result = [tuple(product) for product in products]
        return result
    finally:
        await close_connection(conn)

async def add_new_product(appliance: Appliance):
    conn = await create_connection()
    try:
        brand_query = """
            SELECT brand_id FROM brand WHERE name = $1
        """
        brand_id = await conn.fetchrow(brand_query, appliance.brand)
        category_query = """
            SELECT category_id FROM category WHERE name = $1
        """
        category_id = await conn.fetchrow(category_query, appliance.category)
        query = """
            INSERT INTO appliance (name, brand_id, category_id, price, quantity_in_stock, description) VALUES ($1, $2, $3, $4, $5, $6)
        """
        await conn.execute(query, appliance.name, brand_id['brand_id'], category_id['category_id'], appliance.price, appliance.quantity_in_stock, appliance.description)
    finally:
        await close_connection(conn)

async def rmv_appliance(appliance_id: int):
    conn = await create_connection()
    try:
        query = """
            DELETE FROM appliance WHERE appliance_id = $1
        """
        await conn.execute(query, appliance_id)
    finally:
        await close_connection(conn)


# asyncio.run(get_all_products())