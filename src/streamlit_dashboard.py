import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import boto3
import pycountry
import os
import dotenv
from dotenv import load_dotenv

load_dotenv()

# Configure Streamlit 
st.set_page_config(
    page_title="Ecommerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
alt.themes.enable("dark")

# Check for s3 path 
dashboard_file_path = os.getenv('DASHBOARD_FILE_PATH')
if not dashboard_file_path:
    st.error("DASHBOARD_FILE_PATH environment variable is not set. Please set it to the S3 path of the dashboard data file.")
    st.stop()

# Load data from S3 bucket
s3_client = boto3.client('s3')
df_dashboard = pd.read_csv(dashboard_file_path)

# Show loaded dataframe 
st.write("Data loaded from S3:")
st.dataframe(df_dashboard)
    
# Display basic statistics
st.subheader("Basic Statistics")
st.write("Total Orders:", df_dashboard['order_id'].nunique())
st.write("Total Customers:", df_dashboard['customer_id'].nunique())
st.write("Total Products:", df_dashboard['product_id'].nunique())
st.write("Total Revenue:", df_dashboard['price'].sum())
st.write("Average Order Value:", df_dashboard.groupby('order_id')['price'].sum().mean())

col1, col2 = st.columns(2)

# Display top 10 products by revenue
with col1:
    st.subheader("Top 10 Products by Revenue")
    top_products = df_dashboard.groupby('product_id').agg({'price': 'sum'}).reset_index()
    top_products = top_products.sort_values(by='price', ascending=False).head(10)
    st.bar_chart(top_products.set_index('product_id'), use_container_width=True)  

# Display top 10 customers by total spend
with col2:
    st.subheader("Top 10 Customers by Total Spend")
    top_customers = df_dashboard.groupby('customer_id').agg({'price': 'sum'}).reset_index()
    top_customers = top_customers.sort_values(by='price', ascending=False).head(10)
    st.bar_chart(top_customers.set_index('customer_id'), use_container_width=True)

col3, col4 = st.columns(2)
# Display order status distribution
with col3:
    st.subheader("Order Status Distribution")
    status_counts = df_dashboard['status'].value_counts().reset_index()
    status_counts.columns = ['order_status', 'count']  
    status_chart = alt.Chart(status_counts).mark_bar().encode(
        x=alt.X('order_status:N', title='Order Status'),
        y=alt.Y('count:Q', title='Count'),
        color=alt.value("#1f77b4") 
    ).properties(
        title='Order Status Distribution'
    )
    st.altair_chart(status_chart, use_container_width=True) 

# Display orders by country 

with col4:
    st.subheader("Orders by Country (Table)")
    country_counts = df_dashboard['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    st.dataframe(country_counts)

# Download data as csv 

st.sidebar.download_button(
    label="Download data as CSV",
    data=df_dashboard.to_csv(index=False),
    file_name='dashboard_data.csv',
    mime='text/csv'
)