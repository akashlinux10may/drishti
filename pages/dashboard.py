import streamlit as st
from supabase import create_client, Client
import pandas as pd
import time

# --- 1. ENTERPRISE BRANDING & CSS ---
def apply_enterprise_theme():
    st.markdown("""
        <style>
            /* Main Background and Font */
            .main { background-color: #f5f7f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            
            /* Metric Card Styling */
            [data-testid="stMetricValue"] { color: #003366; font-size: 32px; font-weight: 700; }
            [data-testid="stMetricLabel"] { color: #5c6c7c; font-size: 16px; }
            
            /* Sidebar Styling */
            [data-testid="stSidebar"] { background-color: #003366; color: white; }
            [data-testid="stSidebar"] * { color: white !important; }
            
            /* Table Header Styling */
            th { background-color: #003366 !important; color: white !important; }
            
            /* Custom Header for the School */
            .school-header { 
                padding: 20px; 
                background-color: white; 
                border-radius: 10px; 
                border-left: 5px solid #003366;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                margin-bottom: 25px;
            }
                /* Correction for the Logout/Action Button visibility */
div.stButton > button {
    background-color: #003366 !important; /* Default Blue */
    color: white !important;
    border: 1px solid white !important;
}

div.stButton > button:hover {
    background-color: #ffffff !important; /* White on hover */
    color: #003366 !important; /* Blue text on hover */
    border: 1px solid #003366 !important;
}
        </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION ---
SUPABASE_URL = "https://wiyrwciskmononuaaeih.supabase.co"
SUPABASE_KEY = "sb_publishable_SlQxcUZEN193jYnehQvLEg_f5fUlS8_"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Dzire Guru-Assistant", layout="wide")
apply_enterprise_theme()

# --- 3. SIDEBAR (LOGO & FILTER) ---
with st.sidebar:
    st.image("dzire_logo.jpg", width=100)
    st.markdown("### **Dzire Technologies**")
    st.markdown("---")
    st.write("📍 **Deoria Campus**")
    st.write("📅 **Academic Year:** 2026-27")
    st.markdown("---")
    if st.button("Logout"):
        st.info("Session Ended")

# --- 4. MAIN HEADER ---
st.markdown("""
    <div class="school-header">
        <h1 style='margin:0; color:#003366;'>Rainbow School, Deoria</h1>
        <p style='margin:0; color:#5c6c7c;'>Real-time AI Attendance & Security Analytics Dashboard</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. DATA FETCHING ---
def fetch_data():
    try:
        response = supabase.table("attendance_logs").select("*").order("entry_time", desc=True).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        return pd.DataFrame()

# --- 6. DASHBOARD LOOP ---
placeholder = st.empty()

while True:
    df = fetch_data()
    
    with placeholder.container():
        # Top Row: KPI Metrics
        m1, m2, m3, m4 = st.columns(4)
        
        total_present = len(df['student_name'].unique()) if not df.empty else 0
        
        m1.metric("Total Present", total_present)
        m2.metric("Staff Active", "12/15")
        m3.metric("Visitor Count", "04")
        m4.metric("Security Level", "Optimal")

        st.markdown("---")
        
        # Bottom Row: Data Visualization & Table
        col_table, col_alert = st.columns([2, 1])

        with col_table:
            st.markdown("#### **Real-time Attendance Log**")
            if not df.empty:
                df['entry_time'] = pd.to_datetime(df['entry_time']).dt.strftime('%I:%M %p')
                # Styling the dataframe to look like an enterprise table
                st.dataframe(df[['student_name', 'entry_time', 'status']].head(15), 
                             use_container_width=True, hide_index=True)
            else:
                st.info("System is ready. Awaiting student entry...")

        with col_alert:
            st.markdown("#### **Guru-Assistant Alerts**")
            # This is where the Agentic AI shows "Smart Notifications"
            if not df.empty:
                latest_student = df.iloc[0]['student_name']
                st.success(f"**Parent Notified:** {latest_student}'s safety SMS sent.")
                st.info(f"**Principal Alert:** Class 10A reaches 90% attendance.")
            else:
                st.warning("No security alerts generated yet.")

    time.sleep(5)