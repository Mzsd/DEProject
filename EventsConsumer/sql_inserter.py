from models import Order, Pizza, Customer, Header
from dotenv import load_dotenv
from datetime import datetime
import time
import os


def save_to_db(session, data, event_type):
    #DEBUG
    start_time = time.time()
    
    load_dotenv()

    if event_type == os.getenv("KAFKA_TOPIC_PIZZA"):
        order = Order(
            order_id=data['order_id'],
            order_time=datetime.fromtimestamp(data['order_time']),
        )
        session.add(order)
        session.commit()
        
        for pizza in data['pizzas']:
            pizza_record = Pizza(
                order_id=data['order_id'],
                pizza_size=pizza['pizza_size'],
                pizza_type=pizza['pizza_type'],
                quantity=int(pizza['quantity'])
            )
            session.add(pizza_record)

        headers = data['headers']
        header = Header(
            order_id=data['order_id'],
            client_ip=data['client_ip'],
            host=headers['host'],
            user_agent=headers.get('user-agent', ''),
            accept=headers.get('accept'),
            accept_language=headers.get('accept-language'),
            accept_encoding=headers.get('accept-encoding'),
            content_type=headers.get('content-type'),
            content_length=int(headers.get('content-length', 0)),
            origin=headers.get('origin'),
            connection=headers.get('connection'),
            referer=headers.get('referer'),
            upgrade_insecure_requests=headers.get('upgrade-insecure-requests') == '1',
            sec_fetch_dest=headers.get('sec-fetch-dest'),
            sec_fetch_mode=headers.get('sec-fetch-mode'),
            sec_fetch_site=headers.get('sec-fetch-site'),
            sec_fetch_user=headers.get('sec-fetch-user'),
            priority=headers.get('priority')
        )
        session.add(header)

    elif event_type == os.getenv("KAFKA_TOPIC_CHECKOUT"):
        customer = Customer(
            order_id=data['order_id'],
            name=data['name'].replace('+', ' '),
            address=data['address'],
            email=data['email'].replace('%40', '@'),
            phone=data['phone'],
            total_cost=float(data['total_cost']),
            checkout_time=datetime.fromtimestamp(data['checkout_time']),
            order_time=datetime.fromtimestamp(data['order_time']),
            latitude=float(data['latitude']),
            longitude=float(data['longitude'])
        )
        session.add(customer)

    session.commit()
    
    print("Time to complete the transaction: ", time.time() - start_time)