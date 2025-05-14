import os
from faker import Faker
from tqdm import tqdm
import numpy as np
import pandas as pd
from random import randint
from sqlalchemy import create_engine, inspect

# Если есть таблица в бд, то генерить не будем
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

table_name = 'appliance'
inspector = inspect(engine)

fake = Faker('ru_RU')

RECORDS = 5000000
CHUNK_SIZE = 500000
CHUNKS = RECORDS // CHUNK_SIZE

brands = ['Toshiba', 'Indesit', 'Samsung', 'Haier', 'LG', 'Bosch', 'Siemens']
names = [
    'Духовой шкаф', 'Бензопила', 'Микроволновка', 'Блендер', 'Мясорубка',
    'Мультиварка', 'Дрель', 'Шуруповерт', 'Гайковерт', 'Хлебопечка', 'Фен',
    'Холодильник', 'Пылесос', 'Посудомоечня машина', 'Кондиционер', 'Вентилятор',
    'Утюг', 'Швейная машина', 'Тостер', 'Аэрогриль', 'Обувная электросушилка',
    'Обогреватель', 'Углошлифовальная машина', 'Плоскошлифовальная машина'
]

directory = 'data'


def main():
    if not os.path.exists(directory):
        os.makedirs(directory)
    for i in tqdm(range(CHUNKS)):
        data = {
            'id': range(i * CHUNK_SIZE + 1, (i + 1) * CHUNK_SIZE + 1),
            'name': np.random.choice(names, CHUNK_SIZE),
            'brand': np.random.choice(brands, CHUNK_SIZE),
            'price': [randint(5000, 200000) for _ in range(CHUNK_SIZE)],
            'saler_name': [fake.name() for _ in range(CHUNK_SIZE)],
            'city': [fake.city() for _ in range(CHUNK_SIZE)],
            'publishing_date': [fake.date_between(start_date='-2y', end_date='today') for _ in range(CHUNK_SIZE)]
        }
        df = pd.DataFrame(data)
        df.to_csv(f'{directory}/data{i + 1}.csv', index=False)

if __name__ == "__main__" and not inspector.has_table(table_name):
    main()