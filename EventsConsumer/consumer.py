import os
import asyncio
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer

load_dotenv()

async def consume(kafka_topic, loop, kafka_bootstrap_servers, kafka_consumer_group):
    print(f"Consuming messages from topic: {kafka_topic}")
    consumer = AIOKafkaConsumer(
        kafka_topic, 
        loop=loop, 
        bootstrap_servers=kafka_bootstrap_servers, 
        group_id=kafka_consumer_group
    )
    await consumer.start()
    try:
        async for msg in consumer:
            print(f"Consumed message: {msg}")
    finally:
        await consumer.stop()

async def consumer():
    print("[INFO] Starting consumer...[CTRL+C to stop]")     
    await asyncio.gather(
        consume(
            os.getenv("KAFKA_TOPIC_PIZZA"), 
            asyncio.get_running_loop(),
            "localhost:9093", 
            "1"
        ),
        consume(
            os.getenv("KAFKA_TOPIC_CHECKOUT"), 
            asyncio.get_running_loop(),
            "localhost:9093", 
            "1"
        )
    )

asyncio.run(consumer()) 