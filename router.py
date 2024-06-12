import json
from config import loop, KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, KAFKA_CONSUMER_GROUP
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer 
from fastapi import APIRouter
from schema import Message

route = APIRouter()

@route.post("/create_message", response_model=Message)
async def send(message: Message):
    producer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        print(f"Sending message: {message}")
        value_json = json.dumps(message.__dict__).encode('utf-8')
        await producer.send_and_wait(topic=KAFKA_TOPIC, value=value_json)
    finally:
        await producer.stop()
        
async def consume():
    consumer = AIOKafkaConsumer(KAFKA_TOPIC, loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, group_id=KAFKA_CONSUMER_GROUP)
    await consumer.start()
    try:
        async for msg in consumer:
            print(f"Consumed message: {msg}")
    finally:
        await consumer.stop()