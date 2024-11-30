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
                price bigint not null,
                quantity_in_stock bigint not null,
                description text
            )
        """
        await conn.execute(query_appliance)
    finally:
        await close_connection(conn)

async def create_reservation_table():
    """RESERVATION TABLE"""
    conn = await create_connection();
    try:
        query_reservation = """
            CREATE TABLE IF NOT EXISTS reservation (
                reservation_id bigint generated always as identity primary key,
                customer_id bigint not null references customer(customer_id),
                appliance_id bigint not null references appliance(appliance_id),
                reservation_date date not null,
                days_of_reservation bigint not null
            )
        """
        await conn.execute(query_reservation)
    finally:
        await close_connection(conn)

async def tables_create():
    await create_customer_table()
    await create_brand_table()
    await create_category_table()
    await create_appliance_table()
    await create_reservation_table()

