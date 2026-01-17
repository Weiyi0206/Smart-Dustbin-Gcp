import streamlit as st
from google.cloud import firestore
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="EcoSort Dashboard",
    layout="wide",
    page_icon="♻️",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Global Font & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Card Style for Metrics - Adaptive to Dark/Light Mode */
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05); /* Transparent white for glass effect */
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Chart Containers */
    .stPlotlyChart {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        padding: 15px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-weight: 700;
    }
    
    /* Custom Divider */
    hr {
        margin-top: 2rem;
        margin-bottom: 2rem;
        border: 0;
        border-top: 1px solid rgba(128, 128, 128, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- FIRESTORE CONNECTION ---
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
    """Fetches records from Firestore"""
    if db is None: return []
    try:
        docs = db.collection('waste_logs').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(2000).stream()
        data = []
        for doc in docs:
            d = doc.to_dict()
            if 'timestamp' in d and d['timestamp'] is not None:
                d['timestamp'] = d['timestamp'].replace(tzinfo=None)
            data.append(d)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

# --- SIDEBAR ---
with st.sidebar:
    st.title("♻️ EcoSort")
    st.markdown("**Smart City Edition v1.0**")
    st.divider()
    
    # Date Filter
    st.subheader("📅 Timeframe")
    
    raw_data = get_data()
    if not raw_data:
        st.warning("No data found.")
        st.stop()
        
    df = pd.DataFrame(raw_data)
    if not df.empty and 'timestamp' in df.columns:
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()
    else:
        min_date = datetime.now().date()
        max_date = datetime.now().date()
    
    date_range = st.date_input("Filter Date", [min_date, max_date], min_value=min_date, max_value=max_date)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Material Filter
    st.subheader("🔍 Categories")
    if 'class' in df.columns:
        all_classes = ['All'] + sorted(list(df['class'].unique()))
    else:
        all_classes = ['All']
    selected_class = st.selectbox("Select Material", all_classes)
    
    st.divider()
    if st.button("🔄 Refresh Data", type="secondary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- DATA PRE-PROCESSING ---
# Filter Data
mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
if selected_class != 'All':
    mask = mask & (df['class'] == selected_class)
filtered_df = df.loc[mask]

# Calculate Deltas (Today vs Yesterday)
today = datetime.now().date()
yesterday = today - timedelta(days=1)
week = today - timedelta(days=7)

df_today = df[df['timestamp'].dt.date == today]
df_yesterday = df[df['timestamp'].dt.date == yesterday]
df_week = df[df['timestamp'].dt.date >= week]

count_today = len(df_today)
count_yesterday = len(df_yesterday)
delta_count = count_today - count_yesterday
delta_week = len(df_week) 

recycle_today = len(df_today[df_today['bin'] == 'Recycle'])
recycle_yesterday = len(df_yesterday[df_yesterday['bin'] == 'Recycle'])

# --- MAIN DASHBOARD ---
st.title("♻️ EcoSort Dashboard")
st.markdown(f"Analytics View: **{start_date}** to **{end_date}**")
st.markdown("---")

# === ROW 1: SMART METRICS ===
col1, col2, col3, col4 = st.columns(4)

total_count = len(filtered_df)
recycle_count = len(filtered_df[filtered_df['bin'] == 'Recycle'])
efficiency = (recycle_count / total_count * 100) if total_count > 0 else 0

with col1:
    st.metric(label="Processed Today", value=f"{count_today:,}", delta=f"{delta_count} vs yesterday")

with col2:
    st.metric(label="Total Processed", value=f"{total_count:,}", delta=f"{delta_week} this week")

with col3:
    st.metric(label="Recycling Rate", value=f"{efficiency:.1f}%")

with col4:
    # Carbon Saved (0.5kg CO2 per item)
    co2 = recycle_count * 0.5
    st.metric(label="Carbon Offset", value=f"{co2:.1f} kg")

# === ROW 2: ADVANCED ANALYTICS ===
st.subheader("📊 Waste Analytics")
c1, c2 = st.columns([1, 1])
COLOR_RECYCLE = '#10B981' # Emerald 500
COLOR_GENERAL = '#F59E0B' # Amber 500
COLOR_MAP = {'Recycle': COLOR_RECYCLE, 'General': COLOR_GENERAL}

with c1:
    # Top Items Bar Chart
    if not filtered_df.empty:
        top_items = filtered_df['class'].value_counts().head(10).reset_index()
        top_items.columns = ['Item', 'Count']
        fig_bar = px.bar(
            top_items, 
            x='Count', 
            y='Item', 
            orientation='h',
            color='Count',
            color_continuous_scale='Teal',
            title="Top 10 Waste Categories"
        )
        fig_bar.update_layout(
            yaxis={'categoryorder':'total ascending'}, 
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data available.")

with c2:
    # Sunburst Chart
    if not filtered_df.empty:
        fig_sun = px.sunburst(
            filtered_df, 
            path=['bin', 'class'], 
            color='bin',
            color_discrete_map=COLOR_MAP,
            height=400,
            title="Bin Composition"
        )
        fig_sun.update_layout(
            margin=dict(t=30, l=0, r=0, b=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_sun, use_container_width=True)
    else:
        st.info("No data available for the selected period.")

# === ROW 3: TEMPORAL TRENDS ===
st.subheader("📈 Temporal Trends")

tab1, tab2 = st.tabs(["Activity Heatmap", "Waste Generation Over Time"])

with tab1:
    if not filtered_df.empty:
        hm_df = filtered_df.copy()
        hm_df['Day'] = hm_df['timestamp'].dt.day_name()
        hm_df['Hour'] = hm_df['timestamp'].dt.hour
        
        heatmap_data = hm_df.groupby(['Day', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            heatmap_data, x='Hour', y='Day', z='Count',
            nbinsx=24, category_orders={'Day': days_order},
            color_continuous_scale='Tealgrn',
            title="Peak Usage Heatmap"
        )
        fig_heat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("No data for heatmap.")

with tab2:
    # Group by Hour
    timeline_df = filtered_df.copy()
    timeline_df['hour'] = timeline_df['timestamp'].dt.floor('h')
    hourly_counts = timeline_df.groupby(['hour', 'bin']).size().reset_index(name='count')
    
    if not hourly_counts.empty:
        fig_time = px.area(hourly_counts, x='hour', y='count', color='bin', 
                           color_discrete_map={'Recycle': '#00CC96', 'General': '#EF553B'})
        fig_time.update_layout(
            xaxis_title="Time", 
            yaxis_title="Items Count", 
            hovermode="x unified",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("Not enough data for timeline.")

# === ROW 4: DATA EXPORT ===
with st.expander("📂 View Raw Data & Export"):
    st.dataframe(filtered_df, use_container_width=True)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV Report",
        data=csv,
        file_name=f'ecosort_report_{start_date}_{end_date}.csv',
        mime='text/csv'
    )