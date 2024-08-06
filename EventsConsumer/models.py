from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(String, primary_key=True)
    order_time = Column(TIMESTAMP)

class Pizza(Base):
    __tablename__ = 'pizzas'
    pizza_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50))
    pizza_size = Column(String(10))
    pizza_type = Column(String(50))
    quantity = Column(Integer)

class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50))
    name = Column(String(100))
    address = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    total_cost = Column(DECIMAL(10, 2))
    checkout_time = Column(TIMESTAMP)
    order_time = Column(TIMESTAMP)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))

class Header(Base):
    __tablename__ = 'headers'
    header_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50))
    client_ip = Column(String(45))
    host = Column(String(50))
    user_agent = Column(String(200))
    accept = Column(String(200))
    accept_language = Column(String(50))
    accept_encoding = Column(String(50))
    content_type = Column(String(50))
    content_length = Column(Integer)
    origin = Column(String(100))
    connection = Column(String(20))
    referer = Column(String(100))
    upgrade_insecure_requests = Column(Boolean)
    sec_fetch_dest = Column(String(20))
    sec_fetch_mode = Column(String(20))
    sec_fetch_site = Column(String(20))
    sec_fetch_user = Column(String(10))
    priority = Column(String(10))
