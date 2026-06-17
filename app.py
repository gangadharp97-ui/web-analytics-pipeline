import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set up page configuration
st.set_page_config(page_title="Web Clickstream Analytics", layout="wide")

st.title("🌐 Digital Clickstream & User Behavior Analytics Engine")
st.markdown("---")

# Load the processed dataset
processed_path = 'data/processed/clickstream_clean.csv'

if not os.path.exists(processed_path):
    st.error("⚠️ Processed data file not found! Please run your ETL scripts first.")
else:
    df = pd.read_csv(processed_path)
    
    # ----------------------------------------------------
    # 📊 SIDEBAR FILTER PANEL
    # ----------------------------------------------------
    st.sidebar.header("Filter Analytics Matrix")
    selected_device = st.sidebar.multiselect(
        "Device Type:",
        options=df['device'].unique(),
        default=df['device'].unique()
    )
    
    selected_source = st.sidebar.multiselect(
        "Traffic Source:",
        options=df['traffic_source'].unique(),
        default=df['traffic_source'].unique()
    )
    
    # Apply user filters to the dataframe
    filtered_df = df[
        (df['device'].isin(selected_device)) & 
        (df['traffic_source'].isin(selected_source))
    ]

    # ----------------------------------------------------
    # 💎 EXPERT KPI HIGH-LEVEL METRICS
    # ----------------------------------------------------
    total_traffic = len(filtered_df)
    total_sessions = filtered_df['session_id'].nunique()
    
    # Calculate Advanced Bounce Rate Metric
    session_steps = filtered_df.groupby('session_id')['session_step_sequence'].max()
    bounced_sessions = sum(session_steps == 1)
    bounce_rate = (bounced_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Calculate Cart Abandonment Rate Metric
    cart_sessions = filtered_df[filtered_df['url_path'] == '/cart']['session_id'].nunique()
    purchase_sessions = filtered_df[filtered_df['url_path'] == '/checkout_success']['session_id'].nunique()
    abandonment_rate = ((cart_sessions - purchase_sessions) / cart_sessions * 100) if cart_sessions > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Click Traffic", f"{total_traffic:,}")
    col2.metric("Unique Sessions", f"{total_sessions:,}")
    col3.metric("Bounce Rate", f"{bounce_rate:.1f}%")
    col4.metric("Cart Abandonment", f"{abandonment_rate:.1f}%")
    
    st.markdown("---")

    # ----------------------------------------------------
    # 📈 CHARTS AND VISUALIZATIONS ROW
    # ----------------------------------------------------
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("🛒 User Conversion Funnel Drop-off")
        
        # Define the linear sequence of our e-commerce funnel steps
        funnel_stages = ['/home', '/product_list', '/cart', '/checkout_success']
        funnel_counts = []
        
        for stage in funnel_stages:
            unique_users = filtered_df[filtered_df['url_path'] == stage]['user_id'].nunique()
            funnel_counts.append(unique_users)
            
        funnel_data = pd.DataFrame({
            "Stage": ["1. Home Page", "2. Product Discovery", "3. Added to Cart", "4. Successful Checkout"],
            "Unique Users": funnel_counts
        })
        
        fig_funnel = px.funnel(funnel_data, x='Unique Users', y='Stage', color_discrete_sequence=['#a78bfa'])
        st.plotly_chart(fig_funnel, use_container_width=True)

    with right_col:
        st.subheader("📣 Traffic Attribution Mix")
        source_counts = filtered_df.groupby('traffic_source')['session_id'].nunique().reset_index()
        source_counts.columns = ['Traffic Source', 'Sessions']
        
        fig_pie = px.pie(source_counts, values='Sessions', names='Traffic Source', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)