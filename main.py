import streamlit as st

st.set_page_config(page_title="Dzire Drishti AI Portal", layout="wide")

# Custom CSS for Mobile App Feel
st.markdown("""
    <style>
        .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #003366; color: white; }
        [data-testid="stSidebar"] { background-color: #003366; }
        .main-header { text-align: center; color: #003366; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Dzire Technologies</h1>", unsafe_allow_html=True)
st.image("dzire_logo.jpg", width=100)

st.info("Welcome to the Guru-Assistant Ecosystem. Please use the sidebar to navigate.")

col1, col2 = st.columns(2)
with col1:
    if st.button("📸 Launch Attendance"):
        st.switch_page("pages/cloud.py")
with col2:
    if st.button("📊 View Dashboard"):
        st.switch_page("pages/dashboard.py")