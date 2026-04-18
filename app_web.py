import streamlit as st
import pandas as pd
import os
from datetime import datetime
import glob

# Page Config
st.set_page_config(page_title="Smart Attendance Dashboard", page_icon="📊", layout="wide")

# Styling
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Smart Attendance & Surveillance Dashboard")
st.sidebar.header("Navigation")

# Helper to load attendance data
def get_attendance_files():
    return sorted(glob.glob("database/Attendance_*.csv"), reverse=True)

def get_surveillance_files():
    return sorted(glob.glob("database/surveillance_logs/Surveillance_*.csv"), reverse=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🕒 Attendance Logs", "🚨 Surveillance Alerts", "📈 Insights"])

with tab1:
    st.header("Daily Attendance Records")
    files = get_attendance_files()
    if files:
        selected_file = st.selectbox("Select Date", files, format_func=lambda x: os.path.basename(x).replace("Attendance_", "").replace(".csv", ""))
        df = pd.read_csv(selected_file)
        
        # Metrics
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Present", len(df))
        with c2:
            st.metric("On Time", len(df[df['Status'] == 'On Time']))
        with c3:
            st.metric("Late", len(df[df['Status'] == 'Late']))
            
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No attendance records found yet.")

with tab2:
    st.header("Surveillance & Safety Logs")
    s_files = get_surveillance_files()
    if s_files:
        selected_s_file = st.selectbox("Select Surveillance Date", s_files, format_func=lambda x: os.path.basename(x).replace("Surveillance_", "").replace(".csv", ""))
        sdf = pd.read_csv(selected_s_file)
        
        # Alerts Metric
        st.error(f"Total Alerts Detected: {len(sdf)}")
        st.dataframe(sdf, use_container_width=True)
        
        # Show Evidence if exists
        st.subheader("Recent Evidence Captures")
        evidence_path = "database/surveillance_logs/evidence/"
        if os.path.exists(evidence_path):
            ev_images = sorted(glob.glob(os.path.join(evidence_path, "*.jpg")), reverse=True)[:5]
            if ev_images:
                cols = st.columns(len(ev_images))
                for i, img in enumerate(ev_images):
                    cols[i].image(img, caption=os.path.basename(img))
            else:
                st.write("No images captured yet.")
    else:
        st.info("No surveillance alerts recorded yet.")

with tab3:
    st.header("System Insights")
    # Aggregate data from all attendance files
    all_attendance_files = get_attendance_files()
    if all_attendance_files:
        all_dfs = [pd.read_csv(f) for f in all_attendance_files]
        master_df = pd.concat(all_dfs)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Attendance by Name")
            chart_data = master_df['Name'].value_counts()
            st.bar_chart(chart_data)
            
        with col2:
            st.subheader("On Time vs Late (All Time)")
            status_data = master_df['Status'].value_counts()
            st.write(status_data)
            # Simple donut chart
            import matplotlib.pyplot as plt
            fig1, ax1 = plt.subplots()
            ax1.pie(status_data, labels=status_data.index, autopct='%1.1f%%', startangle=90, colors=['#2ecc71', '#e74c3c'])
            ax1.axis('equal')
            st.pyplot(fig1)
    else:
        st.info("Insufficient data for insights.")

st.sidebar.markdown("---")
st.sidebar.write("Developed by Antigravity")
st.sidebar.write(f"Last sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
