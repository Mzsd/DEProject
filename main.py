import os
import time
import json
import uuid
import redis
import hashlib
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

# Create a global Redis connection pool
r = redis.Redis(host='localhost', port=7521, decode_responses=True)
conn = r.ping()
if conn:
    print("[+] Connected to Redis")
else:
    print("[-] Could not connect to Redis")

pizza_df = None
# Postcode data - should be in realtime using google api
postcodes_df = pd.read_csv("postcode_latlong.csv")

### HELPER FUNCTIONS
#
#
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
    
def fetch_pizza_cost(pizza_type, pizza_size):
    cost = 100.0
    try:
        cost = pizza_df[
            pizza_df['pizza_name'].str.contains(pizza_type) & 
            pizza_df['pizza_size'].str.contains(pizza_size[0].upper())
        ]['unit_price'].values[0]
    except Exception as e:
        print("Invalid pizza type or size. Defaulting to 100")
    
    return float(cost)

def convert_pizza_string(pizza_string):
    pizza_orders = pizza_string.split('&')
    pizzas = []
    pizza = dict()
    for order in pizza_orders:
        key, value = order.split('=')
        pizza['_'.join(key.split('_')[:-1]) if key.split('_')[-1].isnumeric() else key] = value
        if len(pizza) == 3:
            pizzas.append(pizza)
            pizza = dict()

    return pizzas

def fetch_total_cost(pizzas):
    total_cost = 0
    for pizza in pizzas:
        total_cost += int(pizza["quantity"]) * fetch_pizza_cost(pizza['pizza_type'].replace("-", " ").title().replace("And", "and"), pizza['pizza_size'])
    return total_cost
#
#
### HELPER FUNCTIONS - END

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get('/final_order', response_class=HTMLResponse)
async def final_order(request: Request):
    pizzas = json.loads(r.get(request.query_params['token']))['pizzas']
    print(pizzas)
    total_cost = fetch_total_cost(pizzas)
    return templates.TemplateResponse("final_order.html", {"request": request, "total_cost": total_cost})

@app.post("/first_order")
async def create_order(request: Request, pizzas: str = Body(...)):
    print(pizzas)
    pizzas = convert_pizza_string(pizzas)
    
    order_id = str(uuid.uuid4())
    order_time = int(time.time())

    order_details = {
        "order_id": order_id,
        "order_time": order_time,
        "pizzas": pizzas,
        "client_ip": request.client.host,
        "headers": dict(request.headers)
    }

    producer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        print(f"Sending message: {order_details}")
        value_json = json.dumps(order_details).encode('utf-8')
        await producer.send_and_wait(topic="pizza_events", value=value_json)
    finally:
        await producer.stop()

    # Encode pizzas string to safely include it in the URL
    order_token = str(uuid.uuid4())
    
    # Merge order_token with order_id and generate a hash of that
    merged_id = str([order_token, order_id, order_time])
    hashed_id = hashlib.sha256(merged_id.encode()).hexdigest()
    redis_pool = redis.ConnectionPool(host='localhost', port=7521, db=0)
    r = redis.Redis(connection_pool=redis_pool)
    r.set(hashed_id, json.dumps(order_details))
    
    # Redirect the user to the final order page
    redirect_url = str(request.url_for('final_order')) + f"?token={hashed_id}"
    
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@app.post("/checkout")
async def create_order(checkout: str = Body(...)):
    print(checkout)
    
    checkouts = {c.split('=')[0]: c.split('=')[1] for c in checkout.split('&')}
    checkouts['checkout_time'] = int(time.time())
    checkouts['address'] = checkouts['address'].replace("+", " ")
    
    order_details = json.loads(r.get(checkouts['token']))
    pizzas = order_details['pizzas']
    
    print(checkouts)
    
    if pizzas:
        checkouts['total_cost'] = fetch_total_cost(pizzas)
        checkouts['order_id'] = order_details['order_id']
        checkouts['order_time'] = order_details['order_time']
        checkouts['latitude'] = postcodes_df[postcodes_df['postcode'] == checkouts['address']]['latitude'].values[0]
        checkouts['longitude'] = postcodes_df[postcodes_df['postcode'] == checkouts['address']]['longitude'].values[0]
        
        r.delete(checkouts['token'])
        del checkouts['token']
        
        producer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
        await producer.start()
        try:
            print(f"Sending message: {checkouts}")
            value_json = json.dumps(checkouts).encode('utf-8')
            await producer.send_and_wait(topic="checkout_events", value=value_json)
        finally:
            await producer.stop()

        return {"message": "Order Placed Successfully!"}
    
    return {"message": "Invalid order or order Expired!"}

@app.get("/pizza-cost/{pizza_type}/{pizza_size}")
async def get_pizza_cost(pizza_type: str, pizza_size: str):
    print(pizza_type, pizza_size)
    cost = fetch_pizza_cost(pizza_type, pizza_size)
    print(cost)
    return {"cost": cost}


get_all_pizza_costs()