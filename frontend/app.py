import streamlit as st
from google.cloud import firestore
import pandas as pd
import plotly.express as px

# Connect to Database
db = firestore.Client()

st.set_page_config(page_title="Smart Dustbin IoT", layout="wide")
st.title("♻️ IoT Smart Dustbin Monitor")

# Fetch Data from Firestore
try:
    docs = db.collection('waste_logs').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(50).stream()
    data = [doc.to_dict() for doc in docs]
except Exception as e:
    st.error(f"Database Error: {e}")
    data = []

if data:
    df = pd.DataFrame(data)
    
    # Top KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items Sorted", len(df))
    
    # Count recyclables safely
    recycle_count = len(df[df['bin'] == 'Recycle']) if 'bin' in df.columns else 0
    general_count = len(df[df['bin'] == 'General']) if 'bin' in df.columns else 0
    
    col2.metric("Recyclables", recycle_count)
    col3.metric("General Waste", general_count)

    st.divider()

    # Charts
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Detected Materials")
        if 'class' in df.columns:
            fig_pie = px.pie(df, names='class', title='Distribution of Waste Types', hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        st.subheader("Bin Usage")
        if 'bin' in df.columns:
            fig_bar = px.bar(df, x='bin', color='bin', title="Recycle vs General Count")
            st.plotly_chart(fig_bar, use_container_width=True)

    # Live Data Table
    st.subheader("Live Activity Log")
    st.dataframe(df)
else:
    st.info("Waiting for data... Run your simulation script!")
