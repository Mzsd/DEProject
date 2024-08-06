import os
import pymongo
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh


# Load environment variables
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path=env_path)

st.set_page_config(
    page_title="Pizza Takeway Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

col = st.columns((1.5, 4.5, 2), gap='medium')

with st.sidebar:
    st.title('🏂 Pizza Takeaway Dashboard')
    
@st.cache_resource(ttl=1)
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

client = init_connection()

@st.cache_data(ttl=1)
def get_data(db_name, collection_name):
    db = client[db_name]
    collection = db[collection_name]
    items = collection.find()
    items = list(items)  # make hashable for st.cache_data
    return items

db = "pizza_orders_db"
collections = [os.getenv("KAFKA_TOPIC_PIZZA"), os.getenv("KAFKA_TOPIC_CHECKOUT")]

pizza_orders = get_data(db, os.getenv("KAFKA_TOPIC_PIZZA"))
checkout_orders = get_data(db, os.getenv("KAFKA_TOPIC_CHECKOUT"))

# Convert to DataFrame for easier manipulation
pizza_orders_df = pd.DataFrame(pizza_orders)
checkout_orders_df = pd.DataFrame(checkout_orders)

# Get pizza df connected with pizza_orders_df with order_id
pizzas = []
for item in pizza_orders:
    pizzas_per_order = item.get('pizzas', [])
    for pizza in pizzas_per_order:
        pizza['order_id'] = item.get('order_id')
    pizzas += pizzas_per_order

pizza_df = pd.DataFrame(pizzas)

with col[0]:
    # Display summary statistics
    st.markdown("#### Today's 🍕 Orders")
    st.metric(label="Pizza Orders", value=len(pizza_orders_df))#, delta=first_state_delta)
    st.metric(label="Successful Checkout Orders", value=len(checkout_orders_df))#, delta=first_state_delta)
    
if not checkout_orders_df.empty:
    
    # Count number of same latitude and longitude
    lat_long_counts = checkout_orders_df[['latitude', 'longitude']].groupby(['latitude', 'longitude']).size().reset_index(name='size')
    lat_long_counts['size'] = lat_long_counts['size'] * 5
    
    with col[1]:

        # Display a map of the data
        st.map(lat_long_counts, size='size')
            
        # Visualize pizza types ordered
        st.subheader('Pizza Types Ordered')
        pizza_types = pizza_orders_df.explode('pizzas')['pizzas'].apply(lambda x: x['pizza_type'])
        pizza_type_counts = pizza_types.value_counts().reset_index()
        pizza_type_counts.columns = ['pizza_type', 'count']
        pizza_type_chart = alt.Chart(pizza_type_counts).mark_bar().encode(
            x=alt.X('pizza_type', axis=alt.Axis(labelAngle=0)),
            y='count'
        )
        st.altair_chart(pizza_type_chart, use_container_width=True)
