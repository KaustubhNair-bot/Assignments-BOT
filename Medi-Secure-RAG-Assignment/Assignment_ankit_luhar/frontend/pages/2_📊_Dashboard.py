import streamlit as st

st.set_page_config(page_title="Dashboard", page_icon="📊")

if 'access_token' not in st.session_state or not st.session_state.access_token:
    st.warning("Please login first.")
    st.stop()

st.title("📊 System Dashboard")


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Cases Indexed", value="4,999")

with col2:
    st.metric(label="Active Users", value="12")

with col3:
    st.metric(label="Searches Today", value="154")

st.markdown("### Case Distribution by Specialty")

# Mock data for chart
import pandas as pd
chart_data = pd.DataFrame(
    {
        "Specialty": ["Cardiology", "Neurology", "Pulmonology", "General Medicine", "Endocrinology", "Orthopedics"],
        "Cases": [120, 85, 95, 200, 60, 45]
    }
).set_index("Specialty")

st.bar_chart(chart_data)

st.markdown("### Recent Activity")
st.code("""
[INFO] User 'admin' searched for 'cardiac arrest'
[INFO] User 'dr_smith' searched for 'pediatric pneumonia'
[INFO] Data update triggered by 'admin'
""")
