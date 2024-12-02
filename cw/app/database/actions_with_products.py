from database.connect import create_connection, close_connection
from schemas.appliance import Appliance
import asyncio

async def get_all_products():
    conn = await create_connection()
    try:
        # Достаем данные из вьюшки
        query = """
            SELECT appliance_id, appliance_name, brand_name, category_name, price, stock, address
            FROM appliance_with_shop
        """
        products = await conn.fetch(query)
        result = [tuple(product) for product in products]
        return result
    finally:
        await close_connection(conn)

async def add_new_product(appliance: Appliance):
    conn = await create_connection()
    try:
        brand_id_query = """
            SELECT brand_id FROM brand WHERE name = $1
        """
        brand_id = await conn.fetchrow(brand_id_query, appliance.brand)
        category_id_query = """
            SELECT category_id FROM category WHERE name = $1
        """
        category_id = await conn.fetchrow(category_id_query, appliance.category)
        appliance_query = """
            INSERT INTO appliance (name, brand_id, category_id, price, description) VALUES ($1, $2, $3, $4, $5)
        """
        await conn.execute(appliance_query, appliance.name, brand_id['brand_id'], category_id['category_id'], appliance.price, appliance.description)
        shop_id_query = """
            SELECT shop_id FROM shop WHERE address = $1
        """
        shop_id = await conn.fetchrow(shop_id_query, appliance.shop)
        appliance_id_query = """
            SELECT appliance_id FROM appliance WHERE name = $1 AND brand_id = $2
        """
        appliance_id = await conn.fetchrow(appliance_id_query, appliance.name, brand_id['brand_id'])
        query = """
            INSERT INTO stock (appliance_id, shop_id, stock) VALUES ($1, $2, $3)
        """
        await conn.execute(query, appliance_id['appliance_id'], shop_id['shop_id'], appliance.stock)
    finally:
        await close_connection(conn)

async def rmv_appliance(appliance_id: int):
    conn = await create_connection()
    try:
        query_stock = """
            DELETE FROM stock WHERE appliance_id = $1
        """
        await conn.execute(query_stock, appliance_id)
        query = """
            DELETE FROM appliance WHERE appliance_id = $1
        """
        await conn.execute(query, appliance_id)
    finally:
        await close_connection(conn)


# asyncio.run(get_all_products())