import streamlit as st
import requests

st.set_page_config(page_title="Car Price Prediction Dashboard", layout="centered")

st.title("🚗 AI-Powered Car Price Predictor")
st.write("Enter your vehicle specifications below to estimate its market price instantly.")

# Input fields mapping your 13 model features
col1, col2 = st.columns(2)

with col1:
    feat_1 = st.number_input("Feature 1 (e.g., Age/Condition)", value=1.2)
    year = st.number_input("Manufacturing Year", value=2012.0)
    kms_driven = st.number_input("Kilometers Driven", value=120000.0)
    mileage = st.number_input("Mileage (kmpl)", value=19.7)
    engine = st.number_input("Engine CC", value=796.0)
    power = st.number_input("Max Power (bhp)", value=46.3)
    seats = st.number_input("Seats", value=5.0)

with col2:
    f8 = st.number_input("Transmission / Fuel Code 1", value=0.0)
    f9 = st.number_input("Transmission / Fuel Code 2", value=1.0)
    f10 = st.number_input("Seller Type Code", value=0.0)
    f11 = st.number_input("Owner Code", value=2.0)
    f12 = st.number_input("Brand Code 1", value=10.0)
    f13 = st.number_input("Brand Code 2", value=4.0)

# Live Azure Container App API URL
API_URL = "https://ml-prediction-app.politestone-56ec275d.centralindia.azurecontainerapps.io/predict"

if st.button("Predict Price", type="primary"):
    payload = {
        "features": [feat_1, year, kms_driven, mileage, engine, power, seats, f8, f9, f10, f11, f12, f13]
    }
    
    with st.spinner("Connecting to Azure Cloud Model..."):
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                result = response.json()
                
                # Cleanly extract the prediction value
                predicted_price = result.get("prediction", result)
                
                st.success(f"### Estimated Car Price: ₹ {predicted_price}")
            else:
                st.error(f"Error from API: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")