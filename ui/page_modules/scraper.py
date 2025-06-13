import streamlit as st
import sys
from pathlib import Path
import time
import random

# Add the parent directory to the path so we can import from local modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.caralyze_service import get_listings_for_filter, manual_send_listings
from notifier.telegram import send_telegram_message, format_car_listing_message

def build_search_url_from_custom(custom_url):
    """Simple function to validate and return custom URL."""
    if custom_url and custom_url.strip():
        return custom_url.strip()
    return ""

def _show_system_status():
    """Display system status."""
    st.subheader("📊 Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "🟢 ACTIVE" if st.session_state.scraping_active else "🔴 STOPPED"
        st.markdown(f'<div class="status-metric">{status}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="status-metric">🔗 {len(st.session_state.url_pool)} URLs</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="status-metric">🔄 {st.session_state.total_runs} Runs</div>', unsafe_allow_html=True)

def _display_url_pool():
    """Display current URL pool."""
    if st.session_state.url_pool:
        st.subheader(f"🔗 URL Pool ({len(st.session_state.url_pool)} URLs)")
        
        for i, url in enumerate(st.session_state.url_pool):
            if (st.session_state.scraping_active and 
                hasattr(st.session_state, 'next_url_index') and 
                i == st.session_state.next_url_index):
                st.markdown(f'<div class="next-url">🎯 NEXT: {url}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="url-item">{i+1}. {url}</div>', unsafe_allow_html=True)
    else:
        st.info("No URLs in pool. Add URLs to start scraping.")

def _display_scrape_results(results):
    """Display scraping results."""
    if not results:
        return
        
    # Only show results once per scrape
    result_timestamp = results.get('timestamp', 0)
    if 'last_displayed_result' not in st.session_state:
        st.session_state.last_displayed_result = 0
    
    if result_timestamp <= st.session_state.last_displayed_result:
        return
    
    st.session_state.last_displayed_result = result_timestamp
    
    st.subheader("📊 Results")
    
    with st.container():
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        
        new_listings = results.get('new_listings', [])
        scraped_url = results.get('url', '')
        url_num = results.get('url_index', 0) + 1
        
        st.write(f"**🔗 URL #{url_num}:** {scraped_url}")
        
        if new_listings:
            st.write(f"**✅ Result:** {len(new_listings)} new listings found")
        else:
            st.write(f"**🔍 Result:** No new listings found")
        
        st.markdown('</div>', unsafe_allow_html=True)

def _send_listings_to_telegram(listings):
    """Send listings to Telegram."""
    try:
        success_count, failed = manual_send_listings(
            listings,
            send_telegram_message=send_telegram_message,
            format_car_listing_message=format_car_listing_message,
            parse_mode="HTML",
            retry_on_network_error=True
        )
        
        if success_count > 0:
            st.success(f"Sent {success_count}/{len(listings)} listings to Telegram")
        
        if failed:
            st.error(f"Failed to send {len(failed)} listings")
            
    except Exception as e:
        st.error(f"Telegram sending failed: {str(e)}")

def show_scraper_page(all_old_path, latest_new_path, root_dir):
    """Multi-URL scraper with clean interface."""
      # Minimal styling
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .status-metric {
        background-color: #f8f8f8;
        border: 1px solid #cccccc;
        border-radius: 6px;
        padding: 0.5rem;
        text-align: center;
        font-size: 0.85em;
        font-weight: bold;
        margin: 0.2rem;
    }
    
    .status-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .url-item {
        background-color: #f8f8f8;
        border: 1px solid #cccccc;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        font-family: monospace;
        font-size: 0.9em;
        color: #333333;
    }
    
    .next-url {
        background-color: #e8e8e8;
        border: 2px solid #666666;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        font-weight: bold;
        font-family: monospace;
        font-size: 0.9em;
        color: #333333;
    }
    
    .stButton > button {
        height: 2.5rem !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
        min-width: 120px !important;
        margin: 0.2rem 0 !important;
        border-radius: 6px !important;
        border: 1px solid #cccccc !important;
        background-color: white !important;
        color: #333333 !important;
    }
    
    .stButton > button:hover {
        background-color: #f0f0f0 !important;
        border-color: #999999 !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #666666 !important;
        color: white !important;
        border-color: #666666 !important;
    }
      .stButton > button[kind="primary"]:hover {
        background-color: #555555 !important;
        border-color: #555555 !important;
    }
    
    /* Divider styling */
    hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 1.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'url_pool' not in st.session_state:
        st.session_state.url_pool = []
    if 'scraping_active' not in st.session_state:
        st.session_state.scraping_active = False
    if 'auto_send_active' not in st.session_state:
        st.session_state.auto_send_active = False
    if 'interval_seconds' not in st.session_state:
        st.session_state.interval_seconds = 60
    if 'last_scrape_time' not in st.session_state:
        st.session_state.last_scrape_time = 0
    if 'current_url_index' not in st.session_state:
        st.session_state.current_url_index = 0
    if 'next_url_index' not in st.session_state:
        st.session_state.next_url_index = 0
    if 'total_runs' not in st.session_state:
        st.session_state.total_runs = 0
    if 'latest_results' not in st.session_state:
        st.session_state.latest_results = {}

    # Pre-select next URL when scraping starts
    if st.session_state.scraping_active and st.session_state.url_pool:
        if ('next_url_selected' not in st.session_state or 
            st.session_state.next_url_index >= len(st.session_state.url_pool)):
            if len(st.session_state.url_pool) > 1:
                st.session_state.next_url_index = random.randint(0, len(st.session_state.url_pool) - 1)
            else:
                st.session_state.next_url_index = 0
            st.session_state.next_url_selected = True    # System Status
    _show_system_status()
    
    st.divider()
      # URL Management
    st.subheader("🔧 URL Management")
    
    new_url = st.text_input("Enter search URL:", placeholder="https://www.ebay-kleinanzeigen.de/...")
    
    # Adjacent buttons for Add URL and Clear Pool
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add URL", type="primary", use_container_width=True):
            built_url = build_search_url_from_custom(new_url)
            if built_url and built_url not in st.session_state.url_pool:
                st.session_state.url_pool.append(built_url)
                st.success("✅ URL added!")
                st.rerun()
            elif built_url in st.session_state.url_pool:
                st.warning("⚠️ URL already exists")
            else:
                st.error("❌ Invalid URL")
    
    with col2:
        if st.button("Clear Pool", use_container_width=True):
            st.session_state.url_pool = []
            st.session_state.scraping_active = False
            st.success("🧹 Pool cleared!")
            st.rerun()# URL Pool
    _display_url_pool()
    
    st.divider()
      # Controls
    st.subheader("⚙️ Controls")
    
    # Adjacent buttons for Start/Stop and Auto-send toggle
    col1, col2, col3 = st.columns([1.5, 1.5, 2])
    
    with col1:
        if not st.session_state.scraping_active:
            if st.button("▶️ Start", type="primary", use_container_width=True):
                if st.session_state.url_pool:
                    st.session_state.scraping_active = True
                    st.session_state.last_scrape_time = 0
                    
                    # Pre-select first URL
                    if len(st.session_state.url_pool) > 1:
                        st.session_state.next_url_index = random.randint(0, len(st.session_state.url_pool) - 1)
                    else:
                        st.session_state.next_url_index = 0
                    st.session_state.next_url_selected = True
                    
                    st.success("🚀 Started!")
                    st.rerun()
                else:
                    st.error("Add URLs first")
        else:
            if st.button("⏹️ Stop", use_container_width=True):
                st.session_state.scraping_active = False
                st.success("⏹️ Stopped!")
                st.rerun()
    
    with col2:
        st.session_state.auto_send_active = st.checkbox("📤 Auto-send to Telegram", value=st.session_state.auto_send_active)
    
    with col3:
        st.session_state.interval_seconds = st.number_input(
            "Interval (sec):", 
            min_value=30, 
            max_value=3600, 
            value=st.session_state.interval_seconds,
            step=30
        )

    # Active Scraping Logic
    if st.session_state.scraping_active and st.session_state.url_pool:
        if time.time() - st.session_state.last_scrape_time >= st.session_state.interval_seconds:
            current_time = time.time()
            
            # Use pre-selected URL
            if hasattr(st.session_state, 'next_url_index') and st.session_state.next_url_index < len(st.session_state.url_pool):
                current_url_index = st.session_state.next_url_index
            else:
                current_url_index = 0
            
            current_url = st.session_state.url_pool[current_url_index]
            
            with st.spinner(f"🔍 Scraping URL #{current_url_index + 1}..."):
                try:
                    filters = {"custom_url": current_url}
                    
                    results = get_listings_for_filter(
                        filters,
                        all_old_path, 
                        latest_new_path,
                        build_search_url_from_custom,
                        root_dir
                    )
                    
                    all_listings, new_listings = results
                    
                    st.session_state.latest_results = {
                        'all_listings': all_listings,
                        'new_listings': new_listings,
                        'timestamp': current_time,
                        'url': current_url,
                        'url_index': current_url_index
                    }
                    
                    # Auto-send if enabled
                    if st.session_state.auto_send_active and new_listings:
                        _send_listings_to_telegram(new_listings)
                    
                    # Update counters
                    st.session_state.total_runs += 1
                    st.session_state.last_scrape_time = current_time
                    st.session_state.current_url_index = current_url_index
                    
                    # Pre-select next URL
                    if len(st.session_state.url_pool) > 1:
                        st.session_state.next_url_index = random.randint(0, len(st.session_state.url_pool) - 1)
                    else:
                        st.session_state.next_url_index = 0
                    st.session_state.next_url_selected = True
                      # Show results
                    if new_listings:
                        st.success(f"✅ Found {len(new_listings)} new listings!")
                    else:
                        st.info("🔍 No new listings found")
                    
                except Exception as e:
                    st.error(f"❌ Scraping failed: {str(e)}")
                    st.session_state.last_scrape_time = current_time

    # Show Results Section
    if st.session_state.latest_results:
        st.divider()

    # Display Results
    _display_scrape_results(st.session_state.latest_results)
    
    # Progress Display
    if st.session_state.scraping_active:
        time_until_next = st.session_state.interval_seconds - (time.time() - st.session_state.last_scrape_time)
        if time_until_next > 0:
            progress = 1.0 - (time_until_next / st.session_state.interval_seconds)
            progress_container = st.empty()
            progress_container.progress(progress, text=f"⏰ Next scrape in {int(time_until_next)} seconds")
        else:
            ready_container = st.empty()
            ready_container.progress(1.0, text="🔍 Ready to scrape...")
        
        # Auto-refresh
        time.sleep(2)
        st.rerun()
    else:
        st.empty()