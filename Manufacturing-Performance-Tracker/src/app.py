"""
Enterprise Analytics Dashboard
Streamlit-based real-time analytics interface.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(
    page_title="Enterprise Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=300)
def load_data():
    """Load and cache enterprise data"""
    dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
    data = pd.DataFrame({
        'date': dates,
        'revenue': np.random.normal(100000, 15000, len(dates)).cumsum() / 1000,
        'users': np.random.normal(5000, 500, len(dates)).astype(int),
        'transactions': np.random.normal(2000, 300, len(dates)).astype(int),
        'satisfaction': np.random.uniform(4.0, 5.0, len(dates)).round(2),
        'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], len(dates)),
        'product_line': np.random.choice(['Enterprise', 'SMB', 'Startup', 'Government'], len(dates))
    })
    return data

def create_kpi_card(label, value, delta=None, prefix="", suffix=""):
    """Create a styled KPI metric card"""
    delta_str = f"{delta:+.1f}%" if delta is not None else None
    st.metric(
        label=label,
        value=f"{prefix}{value:,.2f}{suffix}",
        delta=delta_str
    )

def main():
    st.sidebar.title("🎛️ Dashboard Controls")
    st.sidebar.markdown("---")
    
    date_range = st.sidebar.date_input(
        "Analysis Period",
        value=(datetime.now() - timedelta(days=90), datetime.now())
    )
    
    selected_region = st.sidebar.multiselect(
        "Regions",
        ['North', 'South', 'East', 'West', 'Central'],
        default=['North', 'South', 'East', 'West', 'Central']
    )
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Main Dashboard
    st.title("📊 Enterprise Analytics Dashboard")
    st.markdown("---")
    
    data = load_data()
    filtered_data = data[data['region'].isin(selected_region)]
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        create_kpi_card("Total Revenue", filtered_data['revenue'].iloc[-1], 12.4, "$", "K")
    with col2:
        create_kpi_card("Active Users", filtered_data['users'].iloc[-1], 8.1, "", "")
    with col3:
        create_kpi_card("Transactions", filtered_data['transactions'].iloc[-1], -2.3, "", "")
    with col4:
        create_kpi_card("CSAT Score", filtered_data['satisfaction'].iloc[-1], 0.5, "", "/5")
    
    st.markdown("---")
    
    # Charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Revenue Trend")
        fig = px.area(filtered_data, x='date', y='revenue', color='region',
                      title='Revenue by Region')
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("👥 User Distribution")
        fig = px.pie(filtered_data, values='users', names='product_line',
                     title='Users by Product Line')
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    with st.expander("📋 View Raw Data"):
        st.dataframe(filtered_data.tail(50), use_container_width=True)
        csv = filtered_data.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "analytics_data.csv")

if __name__ == "__main__":
    main()
