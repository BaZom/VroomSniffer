import streamlit as st
from config.car_models import CAR_MAKES, get_models_for_make

def get_sidebar_filters():
    """Render the sidebar UI for filter and settings."""
    st.header("🔍 Search Filters")
    # Custom URL option (single-line input)
    custom_url = st.text_input("Custom Search URL (optional)")
    if custom_url:
        st.info("✅ Using custom URL")
    else:
        st.info("ℹ️ Using filters below")
    # Car filters
    st.subheader("Vehicle Filters")
    car_make = st.selectbox("Car Make", CAR_MAKES)
    models = ["(Any)"] + get_models_for_make(car_make)
    car_model = st.selectbox("Model", models)
    if car_model == "(Any)":
        car_model = ""
    price_range = st.slider("Price Range (€)", 1000, 50000, (5000, 20000), 1000)
    year_range = st.slider("Year Range", 2010, 2025, (2015, 2025))
    transmission = st.selectbox("Transmission", ["Any", "Automatic", "Manual"])
    max_mileage = st.number_input("Max Mileage (km)", 0, 300000, 150000, 10000)
    # Automation settings
    st.header("🤖 Automation")
    auto_monitor = st.checkbox(
        "🔄 Auto-monitor (1min)", 
        value=False,
        help="Automatically check for new listings every 1 minute"
    )
    auto_send = st.checkbox(
        "📲 Auto-send to Telegram", 
        value=False,
        help="Automatically send new listings to Telegram"
    )
    # Visual feedback
    if auto_monitor and auto_send:
        st.success("🚀 Full automation enabled! (1min)")
    elif auto_monitor:
        st.info("🔄 Monitoring enabled (1min)")
    elif auto_send:
        st.warning("📲 Auto-send needs monitoring")
    else:
        st.info("⏸️ Manual mode")
    return {
        "custom_url": custom_url.strip(),
        "car_make": car_make,
        "car_model": car_model,
        "price_range": price_range,
        "year_range": year_range,
        "transmission": transmission,
        "max_mileage": max_mileage,
        "auto_send": auto_send,
        "auto_monitor": auto_monitor
    }
