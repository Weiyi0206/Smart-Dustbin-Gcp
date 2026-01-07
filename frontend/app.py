import streamlit as st
from google.cloud import firestore
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(
    page_title="EcoSort Analytics",
    layout="wide",
    page_icon="♻️",
    initial_sidebar_state="expanded"
)

# --- FIRESTORE CONNECTION ---
# Caching the connection to avoid re-initializing on every run
@st.cache_resource
def get_db():
    try:
        return firestore.Client()
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

db = get_db()

# --- HELPER FUNCTIONS ---
def get_data():
    """Fetches the last 1000 records from Firestore"""
    if db is None:
        return []
    
    docs = db.collection('waste_logs').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1000).stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        # Convert Firestore Timestamp to Python Datetime
        if 'timestamp' in d and d['timestamp'] is not None:
            d['timestamp'] = d['timestamp'].replace(tzinfo=None) # Make naive for pandas
        data.append(d)
    return data

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3299/3299908.png", width=80)
    st.title("EcoSort")
    st.markdown("Smart Waste Management")
    st.divider()
    
    st.subheader("⚙️ Controls")
    if st.button("🔄 Refresh Data", width='stretch'):
        st.rerun()
        
    st.subheader("🔍 Filters")

raw_data = get_data()

if not raw_data:
    st.warning("Waiting for data... Run your simulation script!")
    st.stop()

df = pd.DataFrame(raw_data)

# Sidebar Filters
min_date = df['timestamp'].min().date()
max_date = df['timestamp'].max().date()

try:
    start_date, end_date = st.sidebar.date_input(
        "Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
except ValueError:
    start_date, end_date = min_date, max_date

all_classes = ['All'] + sorted(list(df['class'].unique()))
selected_class = st.sidebar.selectbox("Material Type", all_classes)

# Apply Filters
mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
if selected_class != 'All':
    mask = mask & (df['class'] == selected_class)
    
filtered_df = df.loc[mask]

# --- MAIN DASHBOARD ---
st.title("♻️ Dashboard Overview")
st.markdown(f"**{len(filtered_df)}** waste items analyzed from **{start_date}** to **{end_date}**")

# TABS
tab1, tab2 = st.tabs(["📊 Live Monitor", "📈 Deep Analytics"])

# === TAB 1: LIVE MONITOR ===
with tab1:
    # Top KPIS
    total_count = len(filtered_df)
    recycle_count = len(filtered_df[filtered_df['bin'] == 'Recycle'])
    
    # Calculate Efficiency
    efficiency = (recycle_count / total_count * 100) if total_count > 0 else 0
    
    # Carbon Footprint (0.5kg CO2 saved per recycled item - illustrative)
    carbon_saved = recycle_count * 0.5 
    
    # Most Common Item
    if not filtered_df.empty:
        most_common = filtered_df['class'].mode()[0]
    else:
        most_common = "N/A"

    # KPI Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Items", f"{total_count}", delta="Processed")
    kpi2.metric("Recycling Rate", f"{efficiency:.1f}%", delta="Target: 80%")
    kpi3.metric("Carbon Saved", f"{carbon_saved:.1f} kg", delta="Est. CO2")
    kpi4.metric("Top Material", most_common.title())

    st.markdown("---")

    # Visuals Row 1
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Recent Activity")
        # Styled Dataframe
        display_df = filtered_df[['timestamp', 'class', 'bin', 'device_id']].head(10).copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(
            display_df,
            width='stretch',
            column_config={
                "timestamp": "Time",
                "class": "Material",
                "bin": st.column_config.TextColumn("Bin", help="Recycle or General"),
                "device_id": "Device"
            },
            hide_index=True
        )

    with c2:
        st.subheader("Efficiency Gauge")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = efficiency,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#00CC96"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 50], 'color': "#f8f9fa"},
                    {'range': [50, 80], 'color': "#e9ecef"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80}}))
        
        fig_gauge.update_layout(height=300, margin=dict(l=20,r=20,t=20,b=20), paper_bgcolor="rgba(0,0,0,0)", font={'family': "Inter"})
        st.plotly_chart(fig_gauge, use_container_width=True)

# === TAB 2: DEEP ANALYTICS ===
with tab2:
    st.markdown("### 📈 Historical Trends & Insights")
    
    # 1. Timeline & Composition
    row2_c1, row2_c2 = st.columns([2, 1])
    
    with row2_c1:
        st.subheader("Waste Generation Over Time")
        # Group by Hour
        timeline_df = filtered_df.copy()
        timeline_df['hour'] = timeline_df['timestamp'].dt.floor('h')
        hourly_counts = timeline_df.groupby(['hour', 'bin']).size().reset_index(name='count')
        
        if not hourly_counts.empty:
            fig_time = px.area(hourly_counts, x='hour', y='count', color='bin', 
                               color_discrete_map={'Recycle': '#00CC96', 'General': '#EF553B'},
                               template="plotly_white")
            fig_time.update_layout(xaxis_title="Time", yaxis_title="Items Count", hovermode="x unified")
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("Not enough data for timeline.")

    with row2_c2:
        st.subheader("Material Composition")
        fig_pie = px.pie(filtered_df, names='class', hole=0.5, 
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # 2. Advanced Analytics: Heatmap & Bar Chart
    row3_c1, row3_c2 = st.columns(2)
    
    with row3_c1:
        st.subheader("🔥 Activity Heatmap")
        # Heatmap: Day of Week vs Hour
        heatmap_df = filtered_df.copy()
        heatmap_df['day_name'] = heatmap_df['timestamp'].dt.day_name()
        heatmap_df['hour'] = heatmap_df['timestamp'].dt.hour
        
        # Order days
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_df.groupby(['day_name', 'hour']).size().reset_index(name='count')
        
        if not heatmap_data.empty:
            fig_heat = px.density_heatmap(heatmap_data, x='hour', y='day_name', z='count',
                                          nbinsx=24, category_orders={'day_name': days_order},
                                          color_continuous_scale='Viridis',
                                          template="plotly_white")
            fig_heat.update_layout(xaxis_title="Hour of Day", yaxis_title="Day of Week")
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Insufficient data for heatmap.")

    with row3_c2:
        st.subheader("📊 Bin Accuracy by Material")
        # Stacked bar chart to show if items are going to the right bin
        # Assuming 'class' determines the bin, but here we show actual bin distribution per class
        fig_bar = px.histogram(filtered_df, x='class', color='bin', 
                               color_discrete_map={'Recycle': '#00CC96', 'General': '#EF553B'},
                               barmode='group', template="plotly_white")
        fig_bar.update_layout(xaxis_title="Material Type", yaxis_title="Count")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Export
    st.markdown("---")
    col_export, _ = st.columns([1, 3])
    with col_export:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Report (CSV)",
            data=csv,
            file_name=f'waste_report_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
            width='stretch'
        )