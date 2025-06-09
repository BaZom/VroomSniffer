import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import os
import json
import re
import subprocess
from datetime import datetime
import time

# Add the parent directory to the path so we can import from local modules
sys.path.append(str(Path(__file__).parent.parent))

from config.car_models import CAR_MAKES, get_models_for_make
from notifier.telegram import send_telegram_message, format_car_listing_message
from services.caralyze_service import (
    get_filter_key,
    load_json_dict,
    save_json_dict,
    run_scraper_and_load_results,
    get_listings_for_filter,
    extract_prices
)

def build_search_url_ui(filters):
    """
    Build a Kleinanzeigen search URL from the given filter dictionary.
    Returns the URL as a string.
    """
    base_url = "https://www.kleinanzeigen.de/s-autos/"
    price_path = ""
    if filters.get("price_range"):
        min_price, max_price = filters["price_range"]
        price_path = f"preis:{min_price}:{max_price}/"
    make = filters.get("car_make", "").lower()
    model = filters.get("car_model", "").lower()
    make_model_path = ""
    if make and model:
        make_model_path = f"{make}-{model}/"
    elif make:
        make_model_path = f"{make}/"
    url = base_url + price_path + make_model_path + "k0c216"
    params = []
    if filters.get("year_range"):
        params.append(f"autos.ez_i:{filters['year_range'][0]},{filters['year_range'][1]}")
    if filters.get("max_mileage"):
        params.append(f"autos.km_i:,{filters['max_mileage']}")
    if filters.get("transmission") and filters['transmission'].lower() != "any":
        params.append(f"autos.shift_s:{filters['transmission'].lower()}")
    if params:
        url += "+" + "+".join(params)
    return url

def show_statistics(listings_data, show_trend=True):
    """
    Display statistics and (optionally) a price trend chart for the given listings.
    Returns (average_price, count).
    """
    if show_trend:
        st.header("Statistics")
    prices = []
    for item in listings_data:
        price_str = item.get("Price", "").replace(".", "").replace(",", "").replace("€", "").strip()
        import re
        match = re.search(r"\d+", price_str)
        if match:
            prices.append(int(match.group()))
    avg_price = int(sum(prices) / len(prices)) if prices else 0
    if show_trend:
        st.metric("Average Price", f"€{avg_price:,}" if prices else "N/A")
        st.metric("Total Listings", f"{len(listings_data)}")
        st.subheader("Price Trend")
        if prices:
            chart_data = pd.DataFrame({
                "index": range(len(prices)),
                "price": prices
            })
            st.line_chart(chart_data.set_index("index"))
        else:
            st.info("No price data to display trend.")
    return avg_price, len(listings_data)

st.set_page_config(page_title="CarAlyze - Car Listing Monitor", page_icon="🚗", layout="wide")

def get_sidebar_filters():
    """
    Render the sidebar UI for filter and notification settings.
    Returns a dictionary of all selected filter values.
    """
    st.header("Search Configuration")
    custom_url = st.text_input("Enter custom search URL (optional)")
    st.markdown("If you provide a URL, it will be used for scraping. Otherwise, the filters below will be used.")
    
    car_make = st.selectbox("Select Car Make", CAR_MAKES)
    models = ["(Any)"] + get_models_for_make(car_make)
    car_model = st.selectbox("Select Model", models)
    if car_model == "(Any)":
        car_model = ""
    
    price_range = st.slider("Price Range (€)", min_value=1000, max_value=50000, value=(5000, 20000), step=1000)
    year_range = st.slider("Year Range", min_value=2010, max_value=2025, value=(2015, 2025), step=1)
    transmission = st.selectbox("Transmission", ["Any", "Automatic", "Manual"])
    max_mileage = st.number_input("Maximum Mileage (km)", min_value=0, max_value=300000, value=150000, step=10000)
    
    st.header("Telegram Settings")
    auto_send = st.checkbox(
        "📲 Auto-send new listings", 
        value=False,
        help="Automatically send new listings to Telegram when found"
    )
    
    st.header("Auto-Monitoring")
    auto_monitor = st.checkbox(
        "🔄 Auto-run scraper every 5 minutes", 
        value=False,
        help="Automatically run the scraper every 5 minutes to check for new listings"
    )
    
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

def _display_results(new_listings, all_listings, filters):
    """Helper function to display monitoring results"""
    st.header("📊 Results")
    
    # New listings section
    st.subheader("🆕 New Listings")
    if new_listings:
        avg_new, count_new = show_statistics(new_listings, show_trend=False)
        st.info(f"Found {count_new} new listings • Avg: €{avg_new:,}")
        
        df_new = pd.DataFrame(new_listings)
        df_new.insert(0, 'No.', range(1, len(df_new) + 1))
        st.dataframe(df_new, hide_index=True, use_container_width=True)
        
        # Telegram controls for new listings
        if new_listings:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📤 Send New Listings"):
                    _manual_send_listings(new_listings)
            
            with col_b:
                if filters.get("auto_send"):
                    st.success("✅ Auto-sent enabled")
                else:
                    st.info("⏸️ Auto-send disabled")
    else:
        st.info("No new listings found")
    
    # All listings section (collapsed by default)
    if all_listings:
        with st.expander(f"📈 All Listings Insights ({len(all_listings)} total)"):
            show_statistics(all_listings, show_trend=True)
            
            df_all = pd.DataFrame(all_listings)
            df_all.insert(0, 'No.', range(1, len(df_all) + 1))
            st.dataframe(df_all, hide_index=True, use_container_width=True)

def _manual_send_listings(listings):
    """Helper function to manually send listings"""
    with st.spinner(f"Sending {len(listings)} listings..."):
        success_count = 0
        for i, listing in enumerate(listings):
            formatted_msg = format_car_listing_message(listing)
            success = send_telegram_message(formatted_msg)
            if success:
                success_count += 1
            
            # Rate limiting
            if i < len(listings) - 1:
                time.sleep(1.5)
        
        if success_count > 0:
            st.success(f"✅ Sent {success_count}/{len(listings)} listings!")
        else:
            st.error("❌ Failed to send listings")

def main():
    """
    Main entry point for the Streamlit app.
    """
    st.title("🚗 CarAlyze - Car Listing Monitor")
    
    # Setup paths
    root_dir = Path(__file__).parent.parent
    listings_dir = Path(root_dir) / "storage" / "listings"
    listings_dir.mkdir(parents=True, exist_ok=True)
    all_old_path = listings_dir / "all_old_results.json"
    latest_new_path = listings_dir / "latest_new_results.json"
    
    # Create main layout with sidebar
    with st.sidebar:
        filters = get_sidebar_filters()
    
    # Create three columns for better layout
    col1, col2, col3 = st.columns([2, 1, 1])
    
    # ================== COLUMN 1: Main Content ==================
    with col1:
        st.header("🔍 Search Configuration")
        
        # Show search URL
        if filters.get("custom_url"):
            st.info("Using custom search URL:")
            st.code(filters["custom_url"], language="text")
        else:
            search_url = build_search_url_ui(filters)
            st.info("Kleinanzeigen search URL:")
            st.code(search_url, language="text")
        
        # Manual monitoring button
        if st.button("🔍 Run Manual Check", use_container_width=True):
            with st.spinner("Manual check: Fetching listings..."):
                all_listings, new_listings = get_listings_for_filter(
                    filters, all_old_path, latest_new_path, build_search_url_ui, root_dir
                )
            
            # Show results immediately
            _display_results(new_listings, all_listings, filters)
        
        # Load and display cached results if available
        else:
            try:
                all_dict = load_json_dict(all_old_path)
                new_dict = load_json_dict(latest_new_path)
                filter_key = get_filter_key(filters)
                cached_all = all_dict.get(filter_key, [])
                cached_new = new_dict.get(filter_key, [])
                
                if cached_new or cached_all:
                    st.caption("📁 Showing cached results from last run")
                    _display_results(cached_new, cached_all, filters)
                else:
                    st.info("💡 Click 'Run Manual Check' to start monitoring")
            except:
                st.info("💡 Click 'Run Manual Check' to start monitoring")
    
    # ================== COLUMN 2: Auto-Monitoring Status ==================
    with col2:
        st.header("🔄 Auto-Monitor")
        
        if filters.get("auto_monitor"):
            # Initialize session state
            if 'last_auto_run' not in st.session_state:
                st.session_state.last_auto_run = 0
            if 'auto_run_count' not in st.session_state:
                st.session_state.auto_run_count = 0
            
            # Real-time countdown display
            current_time = time.time()
            time_since_last = current_time - st.session_state.last_auto_run
            
            # Create placeholders for real-time updates
            status_placeholder = st.empty()
            countdown_placeholder = st.empty()
            progress_placeholder = st.empty()
            
            # Check if it's time for auto-run
            if time_since_last >= 300:  # 5 minutes
                status_placeholder.success("🚀 **AUTO-RUN TRIGGERED!**")
                
                st.session_state.last_auto_run = current_time
                st.session_state.auto_run_count += 1
                
                # Run auto-monitoring
                with st.spinner(f"Auto-run #{st.session_state.auto_run_count}..."):
                    all_listings, new_listings = get_listings_for_filter(
                        filters, all_old_path, latest_new_path, build_search_url_ui, root_dir
                    )
                
                # Show auto-run results
                if new_listings:
                    st.success(f"🎉 Found {len(new_listings)} new!")
                    
                    # Auto-send if enabled
                    if filters.get("auto_send"):
                        with st.spinner("📱 Auto-sending..."):
                            for i, listing in enumerate(new_listings):
                                formatted_msg = format_car_listing_message(listing)
                                send_telegram_message(formatted_msg)
                                if i < len(new_listings) - 1:
                                    time.sleep(1.5)
                        st.success(f"✅ Sent {len(new_listings)} listings!")
                else:
                    st.info("🔍 No new listings found")
                
                # Display results in main column
                with col1:
                    _display_results(new_listings, all_listings, filters)
            
            else:
                # Show countdown with real-time updates
                remaining_seconds = 300 - int(time_since_last)
                minutes = remaining_seconds // 60
                seconds = remaining_seconds % 60
                
                status_placeholder.info("✅ **AUTO-MONITORING ACTIVE**")
                countdown_placeholder.metric(
                    "⏱️ Next Check In:", 
                    f"{minutes:02d}:{seconds:02d}",
                    help="Updates every 5 seconds"
                )
                
                # Progress bar
                progress = (300 - remaining_seconds) / 300
                progress_placeholder.progress(progress, text=f"Progress: {int(progress * 100)}%")
                
                # Show run history
                if st.session_state.auto_run_count > 0:
                    st.caption(f"✅ Completed runs: {st.session_state.auto_run_count}")
                
                # Auto-refresh every 5 seconds for real-time countdown
                time.sleep(5)
                st.rerun()
        
        else:
            st.warning("⏸️ **AUTO-MONITORING OFF**")
            st.caption("✅ Enable in sidebar to activate automatic monitoring")
            st.info("💡 **How to enable:**\n1. Check the sidebar checkbox\n2. Watch real-time countdown\n3. Get automatic notifications")
    
    # ================== COLUMN 3: Telegram Controls ==================
    with col3:
        st.header("📱 Telegram")
        
        # Auto-send status
        if filters.get("auto_send"):
            st.success("✅ **AUTO-SEND ON**")
            st.caption("New listings sent automatically")
        else:
            st.info("⏸️ **AUTO-SEND OFF**")
            st.caption("Manual sending only")
        
        # Test connection
        if st.button("🧪 Test Connection", use_container_width=True):
            success = send_telegram_message("🚗 Test from Caralyze!")
            if success:
                st.success("✅ Connected!")
            else:
                st.error("❌ Failed!")
        
        # Manual send controls (only show if we have data)
        try:
            # Load existing data for manual controls
            all_dict = load_json_dict(all_old_path)
            new_dict = load_json_dict(latest_new_path)
            filter_key = get_filter_key(filters)
            cached_new = new_dict.get(filter_key, [])
            
            if cached_new:
                st.caption(f"📊 {len(cached_new)} new listings available")
                if st.button("📤 Send New", use_container_width=True):
                    _manual_send_listings(cached_new)
            else:
                st.caption("📊 No new listings")
        except:
            st.caption("📊 Run monitoring first")
        
        # Quick stats
        st.subheader("📈 Quick Stats")
        try:
            all_dict = load_json_dict(all_old_path)
            filter_key = get_filter_key(filters)
            total_listings = len(all_dict.get(filter_key, []))
            st.metric("Total Listings", total_listings)
        except:
            st.metric("Total Listings", "0")

if __name__ == "__main__":
    main()
