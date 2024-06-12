import os
import time
import json
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from aiokafka import AIOKafkaProducer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Body, status
from fastapi.responses import HTMLResponse, RedirectResponse
from config import loop, KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, KAFKA_CONSUMER_GROUP

app = FastAPI()
load_dotenv()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory=".")
pizza_df = None

def get_all_pizza_costs():
    global pizza_df
    engine = create_engine(
        f'postgresql://{os.getenv("POSTGRES_USER")}:'
        f'{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:'
        f'{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}'
    )

    # Connect to the engine
    conn = engine.connect()

    # Query the database
    pizza_df = pd.read_sql("SELECT * FROM pizza", conn)
    
def convert_pizza_string(pizza_string):
    pizza_orders = pizza_string.split('&')
    order_time = int(time.time())
    pizzas = []
    pizza = {"order_time": order_time}
    for order in pizza_orders:
        key, value = order.split('=')
        pizza['_'.join(key.split('_')[:-1]) if key.split('_')[-1].isnumeric() else key] = value
        if len(pizza) == 3:
            pizzas.append(pizza)
            pizza = {"order_time": order_time}

    return pizzas

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get('/final_order', response_class=HTMLResponse)
async def final_order(request: Request):
    
    return templates.TemplateResponse("final_order.html", {"request": request})

@app.post("/first_order")
async def create_order(request: Request, pizzas: str = Body(...)):
    
    pizzas = convert_pizza_string(pizzas)
    
    producer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        print(f"Sending message: {pizzas}")
        value_json = json.dumps(pizzas).encode('utf-8')
        await producer.send_and_wait(topic="pizza_events", value=value_json)
    finally:
        await producer.stop()
    
    # Redirect the user to the final order page
    redirect_url = request.url_for('final_order')
    
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.post("/checkout")
async def create_order(checkout: str = Body(...)):
    print(checkout)
    
    checkouts = {c.split('=')[0]: c.split('=')[1] for c in checkout.split('&')}
    checkouts['checkout_time'] = int(time.time())
    
    producer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        print(f"Sending message: {checkouts}")
        value_json = json.dumps(checkouts).encode('utf-8')
        await producer.send_and_wait(topic="checkout_events", value=value_json)
    finally:
        await producer.stop()
    
    # Redirect the user to the final order page
    return {"message": "Order received successfully"}

@app.get("/pizza-cost/{pizza_type}/{pizza_size}")
async def get_pizza_cost(pizza_type: str, pizza_size: str):
    print(pizza_type, pizza_size)
    cost = 100.0
    try:
        cost = pizza_df[
            pizza_df['pizza_name'].str.contains(pizza_type) & 
            pizza_df['pizza_size'].str.contains(pizza_size[0].upper())
        ]['unit_price'].values[0]
    except Exception as e:
        print("Invalid pizza type or size. Defaulting to 100")
    
    print(cost)
    return {"cost": float(cost)}

get_all_pizza_costs()