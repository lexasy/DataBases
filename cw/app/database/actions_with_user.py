from passlib.context import CryptContext
from database.connect import create_connection, close_connection
from schemas.user import User

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def get_user(username: str):
    conn = await create_connection()
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id bigint generated always as identity primary key,
                username varchar(150) not null check (length(username) >= 3),
                password varchar(100) not null,
                rights varchar(10)               
            )
        ''')
        user = await conn.fetchrow('SELECT username, password FROM users WHERE username = $1', username)
        return user
    finally:
        await close_connection(conn)

async def create_user(user: User):
    conn = await create_connection()
    try:
        hashed_password = bcrypt_context.hash(user.password)
        await conn.execute('INSERT INTO users (username, password, rights) VALUES ($1, $2, $3)', user.username, hashed_password, 'user')
    finally:
        await close_connection(conn)

async def authentificate_user(user: User):
    db_user = await get_user(user.username)
    if not db_user or not bcrypt_context.verify(user.password, db_user['password']):
        return None
    return db_user['username']