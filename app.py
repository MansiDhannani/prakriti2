import streamlit as st
import pandas as pd
import httpx
import os

# Set page configuration
st.set_page_config(page_title="EcoValue India", page_icon="🌿", layout="wide")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")

def fetch_data(endpoint):
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{API_URL}/{endpoint}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return None

data = fetch_data("ecosystems")
regions = fetch_data("regions")

st.title("🌿 EcoValue India")

# Sidebar for user inputs
st.sidebar.header("Dashboard Controls")

mode = st.sidebar.radio("Analysis Mode", ["Custom Calculator", "Parcel Explorer (CSV)"])

if mode == "Custom Calculator":
    if not data or not regions:
        st.error("⚠️ Backend API unreachable.")
    else:
        eco_keys = list(data.keys())
        selected_key = st.sidebar.selectbox("Ecosystem Type", eco_keys, format_func=lambda x: data[x]['name'])
        area = st.sidebar.number_input("Area (Ha)", min_value=1, value=100)
        selected_region = st.sidebar.selectbox("Region", list(regions.keys()), format_func=lambda x: x.replace('_', ' ').title())

        if st.sidebar.button("Run Analysis"):
            with st.spinner("Calculating..."):
                res = httpx.post(f"{API_URL}/valuate", json={"ecosystem_type": selected_key, "area_hectares": area, "region": selected_region}).json()
                
                st.subheader(f"📊 Results: {res['ecosystem_name']}")
                c1, c2 = st.columns(2)
                c1.metric("Annual Value", f"₹{res['annual_value_mid']:,.0f}")
                c2.metric("10-Year NPV", f"₹{res['npv']:,.0f}")
                
                # AI Insight Section
                ai_res = httpx.post(f"{API_URL}/report/narrative", json={"valuation_result": res}).json()
                st.info(f"🤖 **AI Insight:** {ai_res['narrative']}")
                
                st.bar_chart(pd.DataFrame(res['services']).set_index("service_name")["total_for_area"])

elif mode == "Parcel Explorer (CSV)":
    parcels = fetch_data("parcels")
    if parcels:
        p_id = st.sidebar.selectbox("Select Parcel ID", [p['Parcel_ID'] for p in parcels])
        p_data = fetch_data(f"parcel/{p_id}")
        
        if not p_data:
            st.error(f"Could not load data for Parcel {p_id}")
            st.stop()
        
        st.subheader(f"📍 Parcel {p_id} Analysis ({p_data['State']})")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Environmental ROI", f"{p_data['Environmental_ROI']:.2f}x")
        m2.metric("Financial ROI", f"{p_data['Financial_ROI']:.2f}x")
        m3.metric("Carbon Stored", f"{p_data['Carbon_Tons_per_Ha'] * p_data['Area_Hectares']:,.0f} Tons")

        st.write("### Ecosystem vs Development NPV")
        chart_data = pd.DataFrame({
            "Type": ["Environment", "Development"],
            "NPV (INR)": [p_data["NPV_Environment_INR"], p_data["NPV_Development_INR"]]
        })
        st.bar_chart(chart_data.set_index("Type"))
        st.table(pd.DataFrame([p_data]).T.rename(columns={0: "Value"}))