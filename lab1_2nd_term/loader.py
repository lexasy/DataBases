import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.types import BigInteger, Text, TIMESTAMP, DATE
import os

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

csv_folder = 'data'
table_name = 'appliance'

inspector = inspect(engine)

if not inspector.has_table(table_name):
    for filename in os.listdir(csv_folder):
        file_path = os.path.join(csv_folder, filename)
        df = pd.read_csv(file_path)
        dtype = {
            'id': BigInteger(),
            'name': Text(),
            'brand': Text(),
            'price': BigInteger(),
            'saler_name': Text(),
            'city': Text(),
            'publishing_date': DATE()
        }
        df.to_sql(table_name, engine, if_exists='append', index=False, dtype=dtype)
        print(f'Файл {filename} успешно загружен.')
