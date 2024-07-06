from sqlalchemy import create_engine
from datetime import datetime, time
from dotenv import load_dotenv
import pandas as pd
import psycopg2
import random
import os

df = pd.read_excel('Data Model - Pizza Sales.xlsx')
uniq_pizza = df[['pizza_id', 'pizza_name', 'pizza_size', 'pizza_category', 'unit_price']].drop_duplicates()
sorted_uniq_pizza_df = uniq_pizza.sort_values(by=['pizza_id'])

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT')
)

engine = create_engine(
    f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}'
)

# Connect to the engine
conn = engine.connect()

sorted_uniq_pizza_df.to_sql('pizza', con=conn, if_exists='replace', index=False)