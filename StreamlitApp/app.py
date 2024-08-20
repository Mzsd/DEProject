import os
import pymongo
import pandas as pd
import altair as alt
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from dotenv import load_dotenv


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

col = st.columns((0.2, 0.78, 0.02), gap='small')

with st.sidebar:
    st.title('🏂 Pizza Takeaway Dashboard')
    st.session_state.time_filter = st.selectbox("Select Time Period", ["Daily", "Monthly", "Yearly", "All time"])
        
@st.cache_resource()
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

client = init_connection()

def get_data(db_name, collection_name):
    db = client[db_name]
    collection = db[collection_name]
    items = collection.find()
    items = list(items)  # make hashable for st.cache_data
    return items

db = "pizza_orders_db"
collections = [os.getenv("KAFKA_TOPIC_PIZZA"), os.getenv("KAFKA_TOPIC_CHECKOUT")]

def filter_data_by_time(df, time_filter):
    now = datetime.now()
    if time_filter == "Daily":
        start_time = now - timedelta(days=1)
    elif time_filter == "Monthly":
        start_time = now - timedelta(days=30)
    elif time_filter == "Yearly":
        start_time = now - timedelta(days=365)
    else:
        return df  # All time, no filtering

    return df[df['order_time'] >= start_time]

def get_recent_data(time_filter):
    # print("Getting recent data")
    pizza_orders = get_data(db, os.getenv("KAFKA_TOPIC_PIZZA"))
    checkout_orders = get_data(db, os.getenv("KAFKA_TOPIC_CHECKOUT"))

    # Convert to DataFrame for easier manipulation
    pizza_orders_df = pd.DataFrame(pizza_orders)
    checkout_orders_df = pd.DataFrame(checkout_orders)

    # Filter data based on time period
    pizza_orders_df['order_time'] = pizza_orders_df['order_time'].apply(lambda x : datetime.fromtimestamp(x))
    checkout_orders_df['order_time'] = checkout_orders_df['order_time'].apply(lambda x : datetime.fromtimestamp(x))
    
    pizza_orders_df = filter_data_by_time(pizza_orders_df, time_filter)
    checkout_orders_df = filter_data_by_time(checkout_orders_df, time_filter)

    # Get pizza df connected with pizza_orders_df with order_id
    pizzas = []
    for item in pizza_orders_df.to_dict('records'):
        pizzas_per_order = item.get('pizzas', [])
        for pizza in pizzas_per_order:
            pizza['order_id'] = item.get('order_id')
        pizzas += pizzas_per_order

    pizza_df = pd.DataFrame(pizzas)
    
    return pizza_orders_df, checkout_orders_df, pizza_df

@st.fragment(run_every=1)
def show_latest_orders_data():
    pizza_orders_df, checkout_orders_df, pizza_df = get_recent_data(st.session_state.time_filter)
    st.metric(label="Pizza Orders", value=len(pizza_orders_df))
    st.metric(label="Successful Checkout Orders", value=len(checkout_orders_df))
    
    # Calculate and display revenue with formatting
    total_revenue = sum(checkout_orders_df['total_cost'])
    if total_revenue >= 1_000_000:
        revenue_display = f"£{total_revenue / 1_000_000:.3f}m"
    else:
        revenue_display = f"£{total_revenue:,.1f}"
    
    st.metric(label="Revenue", value=revenue_display)
    
    return pizza_orders_df, checkout_orders_df, pizza_df

with col[0]:
    # Display summary statistics
    if st.session_state.time_filter == "Daily":
        st.markdown("#### Today's 🍕 Orders Metrics")
    elif st.session_state.time_filter == "Monthly":
        st.markdown("#### Monthly 🍕 Orders Metrics")
    elif st.session_state.time_filter == "Yearly":
        st.markdown("#### Yearly 🍕 Orders")
    else:
        st.markdown("#### All-time 🍕 Orders")
    # st.markdown("#### Today's 🍕 Orders")
    pizza_orders_df, checkout_orders_df, pizza_df = show_latest_orders_data()

    
    
if not checkout_orders_df.empty:
    # Count number of same latitude and longitude
    lat_long_counts = checkout_orders_df[['latitude', 'longitude']].groupby(['latitude', 'longitude']).size().reset_index(name='size')
    lat_long_counts['color'] = lat_long_counts['size'].apply(lambda x: (
            int(x / sum(lat_long_counts['size']) * 255), 
            255,
            255 - int(x / sum(lat_long_counts['size']) * 255)
        )
    )
    lat_long_counts['size'] = 250
    print(lat_long_counts)
    with col[1]:
        # Display a map of the data
        st.map(lat_long_counts, color='color', size='size')

        # Visualize pizza types ordered
        # st.subheader('Pizza Types Ordered')
        # pizza_types = pizza_orders_df.explode('pizzas')['pizzas'].apply(lambda x: x['pizza_type'])
        # pizza_type_counts = pizza_types.value_counts().reset_index()
        # pizza_type_counts.columns = ['pizza_type', 'count']
        # pizza_type_chart = alt.Chart(pizza_type_counts).mark_bar().encode(
        #     x=alt.X('pizza_type', axis=alt.Axis(labelAngle=0)),
        #     y='count'
        # )
        # st.altair_chart(pizza_type_chart, use_container_width=True)

        # Display a pie chart of pizza types ordered
        st.subheader("Pizza Types Ordered")
        pizza_types = pizza_orders_df.explode('pizzas')['pizzas'].apply(lambda x: x['pizza_type'])
        pizza_type_counts = pizza_types.value_counts().reset_index()
        pizza_type_counts.columns = ['pizza_type', 'count']
        fig = px.pie(pizza_type_counts, names='pizza_type', values='count', title='Distribution of Pizza Types Ordered')
        st.plotly_chart(fig)
