from sqlalchemy import create_engine
from datetime import datetime, time
from dotenv import load_dotenv
import pandas as pd
import psycopg2
import random
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, ".env")

print(env_path)
print('Generating tables...')
df = pd.read_excel('Data Model - Pizza Sales.xlsx')
uniq_pizza = df[
        ['pizza_id', 'pizza_name', 'pizza_size', 'pizza_category', 'unit_price']
    ].drop_duplicates()
sorted_uniq_pizza_df = uniq_pizza.sort_values(by=['pizza_id'])

load_dotenv(dotenv_path=env_path)

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

# Store number of orders data
df['order_date'] = df['order_date'].astype(str)
df['order_time'] = df['order_time'].astype(str)

df['order_datetime'] = pd.to_datetime(df['order_date'] + ' ' + df['order_time'])
df['order_hour'] = df['order_datetime'].dt.hour

df['order_weekday'] = df['order_datetime'].dt.day_name()

orders_per_hour_weekday = df.groupby(['order_hour', 'order_weekday']).size().reset_index(name='order_count')

orders_per_hour_weekday['original_order_count'] = orders_per_hour_weekday['order_count']

order_multiplier = round(random.uniform(1, 6), 6)
orders_per_hour_weekday['order_count'] = orders_per_hour_weekday['original_order_count'] * order_multiplier

orders_per_hour_weekday.to_sql('orders_per_hour', con=conn, if_exists='replace', index=False)

print('Tables generated successfully!')