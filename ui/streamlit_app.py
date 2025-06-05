import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import os
import json
import re
import subprocess
from config.car_models import CAR_MAKES, get_models_for_make
from notifier.whatsapp_pywhatkit import send_whatsapp_message

# Add the parent directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

st.set_page_config(page_title="CarAlyze - Car Listing Monitor", page_icon="🚗", layout="wide")

def get_sidebar_filters():
    st.header("Search Configuration")
    car_make = st.selectbox("Select Car Make", CAR_MAKES)
    car_model = st.selectbox("Select Model", get_models_for_make(car_make))
    price_range = st.slider("Price Range (€)", min_value=1000, max_value=50000, value=(5000, 20000), step=1000)
    year_range = st.slider("Year Range", min_value=2010, max_value=2025, value=(2015, 2025), step=1)
    transmission = st.selectbox("Transmission", ["Any", "Automatic", "Manual"])
    max_mileage = st.number_input("Maximum Mileage (km)", min_value=0, max_value=300000, value=150000, step=10000)
    st.header("Notification Settings")
    enable_notifications = st.toggle("Enable WhatsApp Notifications", value=True)
    notification_interval = 30
    if enable_notifications:
        notification_interval = st.number_input("Notification Interval (minutes)", min_value=5, max_value=1440, value=30)
    return {
        "car_make": car_make,
        "car_model": car_model,
        "price_range": price_range,
        "year_range": year_range,
        "transmission": transmission,
        "max_mileage": max_mileage,
        "enable_notifications": enable_notifications,
        "notification_interval": notification_interval
    }

def run_scraper_and_load_results():
    """Run the scraper as a subprocess and load results from JSON file."""
    listings_data = []
    try:
        result = subprocess.run([
            sys.executable, "-m", "scraper.engine"
        ], cwd=root_dir, capture_output=True, text=True)
        if result.returncode != 0:
            st.error(f"Scraper error: {result.stderr}")
        else:
            json_path = os.path.join(root_dir, "scraper", "latest_results.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    listings_data = json.load(f)
                st.success("Scraping completed successfully!")
            else:
                st.error("No results file found after scraping.")
    except Exception as e:
        st.error(f"Error during scraping: {str(e)}")
    return listings_data

def show_statistics(listings_data):
    st.header("Statistics")
    prices = []
    for item in listings_data:
        price_str = item.get("Price", "").replace(".", "").replace(",", "").replace("€", "").strip()
        match = re.search(r"\d+", price_str)
        if match:
            prices.append(int(match.group()))
    avg_price = int(sum(prices) / len(prices)) if prices else 0
    st.metric("Average Price", f"€{avg_price:,}" if prices else "N/A")
    st.metric("New Listings", f"{len(listings_data)}")
    st.subheader("Price Trend")
    if prices:
        chart_data = pd.DataFrame({
            "index": range(len(prices)),
            "price": prices
        })
        st.line_chart(chart_data.set_index("index"))
    else:
        st.info("No price data to display trend.")

def main():
    # Simple login mask
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("🚗 CarAlyze - Car Listing Monitor")
        st.subheader("Login Required")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            # Only accept admin / caralyze_idea
            if username == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")
        return

    st.title("🚗 CarAlyze - Car Listing Monitor")
    with st.sidebar:
        filters = get_sidebar_filters()
    col1, col2 = st.columns([2, 1])
    listings_data = []
    with col1:
        st.header("Active Listings")
        if st.button("Start Monitoring"):
            with st.spinner("Fetching listings..."):
                listings_data = run_scraper_and_load_results()
        if listings_data:
            st.dataframe(pd.DataFrame(listings_data))
        else:
            st.info("No listings to display. Click 'Start Monitoring' to fetch data.")
    with col2:
        show_statistics(listings_data)

if __name__ == "__main__":
    main()
