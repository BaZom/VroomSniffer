import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import json
import re
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
    """Build a Kleinanzeigen search URL from the given filter dictionary."""
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
    """Display statistics and optionally a price trend chart."""
    prices = []
    for item in listings_data:
        price_str = item.get("Price", "").replace(".", "").replace(",", "").replace("€", "").strip()
        match = re.search(r"\d+", price_str)
        if match:
            prices.append(int(match.group()))
    avg_price = int(sum(prices) / len(prices)) if prices else 0
    
    if show_trend and prices:
        st.metric("Average Price", f"€{avg_price:,}")
        st.metric("Total Listings", f"{len(listings_data)}")
        chart_data = pd.DataFrame({"index": range(len(prices)), "price": prices})
        st.line_chart(chart_data.set_index("index"))
    
    return avg_price, len(listings_data)

st.set_page_config(page_title="CarAlyze - Car Monitor", page_icon="🚗", layout="wide")

def get_sidebar_filters():
    """Render the sidebar UI for filter and settings."""
    st.header("🔍 Search Filters")
    
    # Custom URL option
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
      # Price and specs
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

def _manual_send_listings(listings):
    """Send listings manually to Telegram"""
    if not listings:
        st.warning("No listings to send")
        return
    
    with st.spinner(f"Sending {len(listings)} listings..."):
        success_count = 0
        for i, listing in enumerate(listings):
            formatted_msg = format_car_listing_message(listing)
            if send_telegram_message(formatted_msg):
                success_count += 1
            if i < len(listings) - 1:
                time.sleep(1.5)  # Rate limiting
        
        if success_count > 0:
            st.success(f"✅ Sent {success_count}/{len(listings)} listings!")
        else:
            st.error("❌ Failed to send listings")

def _display_results(new_listings, all_listings):
    """Display monitoring results in organized sections"""
    st.header("📊 Results")
    
    # Results summary
    col_summary1, col_summary2 = st.columns(2)
    with col_summary1:
        st.metric("🆕 New Listings", len(new_listings))
    with col_summary2:
        st.metric("📋 Total Listings", len(all_listings))
    
    # New listings section
    if new_listings:
        st.subheader("🆕 New Listings")
        avg_new, _ = show_statistics(new_listings, show_trend=False)
        st.info(f"Average price: €{avg_new:,}")
        
        df_new = pd.DataFrame(new_listings)
        df_new.insert(0, 'No.', range(1, len(df_new) + 1))
        st.dataframe(df_new, hide_index=True, use_container_width=True)
        
        # Manual send button
        if st.button("📤 Send New Listings Manually", type="primary"):
            _manual_send_listings(new_listings)
    else:
        st.info("No new listings found")
    
    # All listings section
    if all_listings:
        with st.expander("📋 All Listings & Analytics", expanded=False):
            show_statistics(all_listings, show_trend=True)
            df_all = pd.DataFrame(all_listings)
            df_all.insert(0, 'No.', range(1, len(df_all) + 1))
            st.dataframe(df_all, hide_index=True, use_container_width=True)

def main():
    """Main Streamlit application"""
    st.title("🚗 CarAlyze - Smart Car Monitor")
    st.caption("Real-time car listing monitoring with Telegram notifications")
    
    # Initialize session state
    if 'last_auto_run' not in st.session_state:
        st.session_state.last_auto_run = 0
    if 'auto_run_count' not in st.session_state:
        st.session_state.auto_run_count = 0
    
    # Sidebar filters
    with st.sidebar:
        filters = get_sidebar_filters()
    
    # Setup paths
    root_dir = Path(__file__).parent.parent
    listings_dir = root_dir / "storage" / "listings"
    listings_dir.mkdir(parents=True, exist_ok=True)
    all_old_path = listings_dir / "all_old_results.json"
    latest_new_path = listings_dir / "latest_new_results.json"
    
    # Main layout with 3 columns
    col1, col2, col3 = st.columns([2, 1, 1])
    
    # ================== COLUMN 1: Search & Results ==================
    with col1:
        st.header("🔍 Search Configuration")
        
        # Show search URL
        if filters.get("custom_url"):
            st.code(filters["custom_url"], language="text")
        else:
            search_url = build_search_url_ui(filters)
            st.code(search_url, language="text")
        
        # Manual monitoring button
        if st.button("🔍 Run Manual Check", type="primary", use_container_width=True):
            with st.spinner("Checking for listings..."):
                all_listings, new_listings = get_listings_for_filter(
                    filters, all_old_path, latest_new_path, build_search_url_ui, root_dir
                )
            
            # Auto-send if enabled
            if filters.get("auto_send") and new_listings:
                st.info(f"📱 Auto-sending {len(new_listings)} listings...")
                _manual_send_listings(new_listings)
            
            # Display results
            _display_results(new_listings, all_listings)
        
        # Load and display cached results
        else:
            try:
                all_dict = load_json_dict(all_old_path)
                new_dict = load_json_dict(latest_new_path)
                filter_key = get_filter_key(filters)
                cached_all = all_dict.get(filter_key, [])
                cached_new = new_dict.get(filter_key, [])
                
                if cached_all or cached_new:
                    st.info("📋 Showing cached results (click 'Run Manual Check' for fresh data)")
                    _display_results(cached_new, cached_all)
                else:
                    st.info("💡 Click 'Run Manual Check' to start monitoring")
            except:
                st.info("💡 Click 'Run Manual Check' to start monitoring")
    
    # ================== COLUMN 2: Auto-Monitoring ==================
    with col2:
        st.header("🔄 Auto-Monitor")
        
        if filters.get("auto_monitor"):
            # Real-time countdown system
            current_time = time.time()
            time_since_last = current_time - st.session_state.last_auto_run
            
            # Placeholders for real-time updates
            status_placeholder = st.empty()
            countdown_placeholder = st.empty()
            progress_placeholder = st.empty()
            
            if time_since_last >= 60:  # 1 minute = 60 seconds
                # Time to run auto-monitoring
                st.session_state.last_auto_run = current_time
                st.session_state.auto_run_count += 1
                
                status_placeholder.success(f"🚀 Auto-run #{st.session_state.auto_run_count}")
                
                with st.spinner("Auto-monitoring..."):
                    all_listings, new_listings = get_listings_for_filter(
                        filters, all_old_path, latest_new_path, build_search_url_ui, root_dir
                    )
                
                if new_listings:
                    st.success(f"✅ Found {len(new_listings)} new listings!")
                    
                    # Auto-send if enabled
                    if filters.get("auto_send"):
                        st.info("📱 Auto-sending...")
                        _manual_send_listings(new_listings)
                else:
                    st.info("No new listings found")
                
                # Reset timer for next cycle
                st.session_state.last_auto_run = time.time()
                time.sleep(2)
                st.rerun()
            
            else:                # Show real-time countdown
                remaining_seconds = 60 - int(time_since_last)
                minutes = remaining_seconds // 60
                seconds = remaining_seconds % 60
                
                status_placeholder.success("✅ **ACTIVE**")
                countdown_placeholder.metric(
                    "⏱️ Next Check", 
                    f"{minutes:02d}:{seconds:02d}",
                    help="Updates in real-time"
                )
                  # Progress bar
                progress = (60 - remaining_seconds) / 60
                progress_placeholder.progress(progress, text=f"{int(progress * 100)}% complete")
                
                # Run history
                if st.session_state.auto_run_count > 0:
                    st.caption(f"Completed: {st.session_state.auto_run_count} runs")
                
                # Auto-refresh every 2 seconds for smooth countdown
                time.sleep(2)
                st.rerun()
        
        else:
            st.warning("⏸️ **DISABLED**")
            st.info("✅ Enable in sidebar to activate")
            st.caption("💡 Auto-monitoring will check for listings every 1 minute")
    
    # ================== COLUMN 3: Telegram Controls ==================
    with col3:
        st.header("📱 Telegram")
        
        # Status indicators
        if filters.get("auto_send"):
            st.success("✅ **AUTO-SEND ON**")
        else:
            st.info("⏸️ Manual mode")
        
        # Test connection
        if st.button("🧪 Test", use_container_width=True):
            success = send_telegram_message("🚗 Test from CarAlyze!")
            if success:
                st.success("✅ Connected!")
            else:
                st.error("❌ Connection failed!")
        
        # Quick stats
        st.subheader("📊 Quick Stats")
        try:
            all_dict = load_json_dict(all_old_path)
            new_dict = load_json_dict(latest_new_path)
            filter_key = get_filter_key(filters)
            total = len(all_dict.get(filter_key, []))
            new_count = len(new_dict.get(filter_key, []))
            
            st.metric("Total", total)
            st.metric("New", new_count)
            
            if new_count > 0:
                if st.button("📤 Send New", use_container_width=True):
                    _manual_send_listings(new_dict.get(filter_key, []))
        except:
            st.metric("Total", "0")
            st.metric("New", "0")

if __name__ == "__main__":
    main()