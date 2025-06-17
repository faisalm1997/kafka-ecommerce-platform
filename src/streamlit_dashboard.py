import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from kafka import KafkaConsumer
from kafka.errors import KafkaTimeoutError
import threading
from collections import deque
from config import config

# Configure Streamlit 
st.set_page_config(
    page_title="Ecommerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DashboardDataCollector:
    def __init__(self):
        self.events = deque(maxlen=1000)  # Keep last 1000 events
        self.running = False
        self.consumer = None
        
    def start_collecting(self):
        """Start collecting data from Kafka in a separate thread"""
        if not self.running:
            self.running = True
            self.consumer = KafkaConsumer(
                config.kafka.topic_name,
                bootstrap_servers=config.kafka.bootstrap_servers,
                group_id='dashboard-consumer',
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                consumer_timeout_ms=1000
            )
            
            thread = threading.Thread(target=self._collect_data)
            thread.daemon = True
            thread.start()
    
    def _collect_data(self):
        """Collect data from Kafka"""
        while self.running:
            try:
                for message in self.consumer:
                    if not self.running:
                        break
                    self.events.append(message.value)
            except KafkaTimeoutError:
                continue
            except Exception as e:
                st.error(f"Error collecting data: {e}")
                time.sleep(5)
    
    def stop_collecting(self):
        """Stop collecting data"""
        self.running = False
        if self.consumer:
            self.consumer.close()
    
    def get_recent_events(self, minutes=10):
        """Get events from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_events = []
        
        for event in self.events:
            event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))
            if event_time >= cutoff_time:
                recent_events.append(event)
        
        return recent_events

# Initialize data collector
@st.cache_resource
def get_data_collector():
    collector = DashboardDataCollector()
    collector.start_collecting()
    return collector

def create_metrics_dashboard(events):
    """Create metrics dashboard"""
    if not events:
        st.warning("No recent events to display")
        return
    
    # Calculate metrics
    total_events = len(events)
    orders = [e for e in events if e['event_type'] == 'order_placed']
    page_views = [e for e in events if e['event_type'] == 'page_view']
    cart_actions = [e for e in events if e['event_type'] in ['add_to_cart', 'remove_from_cart']]
    
    total_revenue = sum(e.get('order', {}).get('total_amount', 0) for e in orders)
    avg_order_value = total_revenue / len(orders) if orders else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", total_events)
    
    with col2:
        st.metric("Orders", len(orders))
    
    with col3:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    with col4:
        st.metric("Avg Order Value", f"${avg_order_value:.2f}")

def create_charts(events):
    """Create various charts"""
    if not events:
        return
    
    # Events over time
    df = pd.DataFrame(events)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['minute'] = df['timestamp'].dt.floor('min')
    
    # Event types over time
    event_counts = df.groupby(['minute', 'event_type']).size().reset_index(name='count')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Events Over Time")
        if not event_counts.empty:
            fig = px.line(event_counts, x='minute', y='count', color='event_type',
                         title="Event Types Over Time")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Event Type Distribution")
        event_type_counts = df['event_type'].value_counts()
        fig = px.pie(values=event_type_counts.values, names=event_type_counts.index,
                    title="Event Type Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Revenue by category (for orders)
    orders_df = df[df['event_type'] == 'order_placed'].copy()
    if not orders_df.empty:
        orders_df['category'] = orders_df['product'].apply(lambda x: x.get('category', 'Unknown'))
        orders_df['revenue'] = orders_df['order'].apply(lambda x: x.get('total_amount', 0))
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Revenue by Category")
            category_revenue = orders_df.groupby('category')['revenue'].sum().reset_index()
            fig = px.bar(category_revenue, x='category', y='revenue',
                        title="Revenue by Product Category")
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            st.subheader("Top Countries by Activity")
            orders_df['country'] = orders_df['customer'].apply(lambda x: x.get('country', 'Unknown'))
            country_counts = orders_df['country'].value_counts().head(10)
            fig = px.bar(x=country_counts.index, y=country_counts.values,
                        title="Top Countries by Orders")
            st.plotly_chart(fig, use_container_width=True)

def main():
    st.title("🛍️ Real-time Ecommerce Analytics")
    st.sidebar.title("Dashboard Controls")
    
    # Get data collector
    collector = get_data_collector()
    
    # Sidebar controls
    time_window = st.sidebar.selectbox(
        "Select Time Window",
        [5, 10, 15, 30, 60],
        index=1,
        format_func=lambda x: f"Last {x} minutes"
    )
    
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
    
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 30, 5)
    
    # Manual refresh button
    if st.sidebar.button("Refresh Now"):
        st.rerun()
    
    # Get recent events
    events = collector.get_recent_events(minutes=time_window)
    
    # Display dashboard
    create_metrics_dashboard(events)
    
    st.divider()
    
    create_charts(events)
    
    # Recent events table
    st.subheader("Recent Events")
    if events:
        # Show last 10 events
        recent_events = sorted(events, key=lambda x: x['timestamp'], reverse=True)[:10]
        
        events_data = []
        for event in recent_events:
            events_data.append({
                'Timestamp': event['timestamp'],
                'Event Type': event['event_type'],
                'Customer': event['customer']['name'],
                'Product': event['product']['name'],
                'Amount': event.get('order', {}).get('total_amount', 'N/A')
            })
        
        st.dataframe(pd.DataFrame(events_data), use_container_width=True)
    else:
        st.info("No recent events to display")
    
    # Auto refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()