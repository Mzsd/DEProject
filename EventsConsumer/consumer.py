import os
import json
import redis
import asyncio
from models import Base
from dotenv import load_dotenv
from sql_inserter import save_to_db
from sqlalchemy import create_engine
from aiokafka import AIOKafkaConsumer
from sqlalchemy.orm import sessionmaker
from mongo_inserter import save_to_mongo


async def consume(kafka_topic, loop, kafka_bootstrap_servers, kafka_consumer_group):
    print(f"Consuming messages from topic: {kafka_topic}")
    consumer = AIOKafkaConsumer(
        kafka_topic, 
        loop=loop, 
        bootstrap_servers=kafka_bootstrap_servers, 
        group_id=kafka_consumer_group,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    await consumer.start()
    try:
        async for msg in consumer:
            # Pretty print the consumed message
            print(f"\nConsumed {kafka_topic} message with order_id: {msg.value['order_id']}")
            save_to_mongo(msg.value, "pizza_orders_db", kafka_topic, MONGO_URI)
            save_to_db(session, msg.value, kafka_topic)
            print(f"Saved {kafka_topic} message to database with order_id: {msg.value['order_id']}")
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


if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(parent_dir, ".env")
    load_dotenv(dotenv_path=env_path)
    
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres123")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")

    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    MONGO_USERNAME = os.getenv("MONGO_USERNAME", "root")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "root")
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    
    MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

    redis_pool = redis.ConnectionPool(host='localhost', port=7521, db=0)
    
    asyncio.run(consumer())