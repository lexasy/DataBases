from database.connect import create_connection, close_connection

async def create_customer_table():
    """CUSTOMER TABLE"""
    conn = await create_connection()
    try:
        query_customer = """
            CREATE TABLE IF NOT EXISTS customer (
                customer_id bigint generated always as identity primary key,
                password varchar(100) not null check(length(password) >= 3),
                customer_login varchar(150) not null check(length(customer_login) >= 3),
                email varchar(100),
                rights varchar(10) not null
            )
        """
        await conn.execute(query_customer)
    finally:
        await close_connection(conn)

async def create_brand_table():
    """BRAND TABLE"""
    conn = await create_connection()
    try:
        query_brand = """
            CREATE TABLE IF NOT EXISTS brand (
                brand_id bigint generated always as identity primary key,
                name varchar(100) not null,
                description text
            )
        """
        await conn.execute(query_brand)
    finally:
        await close_connection(conn)

async def create_category_table():
    """CATEGORY TABLE"""
    conn = await create_connection()
    try:
        query_category = """
            CREATE TABLE IF NOT EXISTS category (
                category_id bigint generated always as identity primary key,
                name varchar(100) not null,
                description text
            )
        """
        await conn.execute(query_category)
    finally:
        await close_connection(conn)

async def create_appliance_table():
    """APPLIANCE TABLE"""
    conn = await create_connection()
    try:
        query_appliance = """
            CREATE TABLE IF NOT EXISTS appliance (
                appliance_id bigint generated always as identity primary key,
                name varchar(100) not null,
                brand_id bigint not null references brand(brand_id),
                category_id bigint not null references category(category_id),
                price float not null,
                description text
            )
        """
        await conn.execute(query_appliance)
    finally:
        await close_connection(conn)

async def create_shop_table():
    """SHOP TABLE"""
    conn = await create_connection();
    try:
        query_shop = """
            CREATE TABLE IF NOT EXISTS shop (
                shop_id bigint generated always as identity primary key,
                address text not null
            )
        """
        await conn.execute(query_shop)
    finally:
        await close_connection(conn)

async def create_order_table():
    """ORDER TABLE"""
    conn = await create_connection()
    try:
        query_order = """
            CREATE TABLE IF NOT EXISTS basket (
                bakset_id bigint generated always as identity primary key,
                customer_id bigint not null references customer(customer_id),
                date date not null,
                status varchar(10) not null
            )
        """
        await conn.execute(query_order)
    finally:
        await close_connection(conn)

async def create_appliance_pool_table():
    """APPLIANCE POOL TABLE"""
    conn = await create_connection()
    try:
        query_appliance_pool = """
            CREATE TABLE IF NOT EXISTS appliance_pool (
                appliance_id bigint not null references appliance(appliance_id),
                order_id bigint not null references basket(basket_id),
                quantity bigint not null
            )
        """
        await conn.execute(query_appliance_pool)
    finally:
        await close_connection(conn)

async def create_stock_table():
    """STOCK TABLE"""
    conn = await create_connection()
    try:
        query_stock = """
            CREATE TABLE IF NOT EXISTS stock (
                appliance_id bigint not null references appliance(appliance_id),
                shop_id bigint not null references shop(shop_id),
                stock bigint not null
            )
        """
        await conn.execute(query_stock)
    finally:
        await close_connection(conn)

async def tables_create():
    await create_customer_table()
    await create_brand_table()
    await create_category_table()
    await create_appliance_table()
    await create_shop_table()
    await create_order_table()
    await create_appliance_pool_table()
    await create_stock_table()
