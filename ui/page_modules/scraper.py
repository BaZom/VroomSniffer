import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import time
import datetime
import random

# Add the parent directory to the path so we can import from local modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.caralyze_service import get_listings_for_filter, manual_send_listings
from notifier.telegram import send_telegram_message, format_car_listing_message
from ui.telegram_controls import telegram_test_button

def build_search_url_from_custom(custom_url):
    """Simple function to validate and return custom URL."""
    if custom_url and custom_url.strip():
        return custom_url.strip()
    return ""

def show_scraper_page(all_old_path, latest_new_path, root_dir):
    """Simple multi-URL scraper with URL pool and dashboard."""    # Clean minimal styling
    st.markdown("""
    <style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Simple clean styling */
    .main-header {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
        border: 1px solid #dee2e6;
    }
    
    .status-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .timer-display {
        background: #f8f9fa;
        border: 2px solid #007bff;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        font-size: 1.3em;
        font-weight: bold;
        color: #007bff;
        margin: 1rem 0;
    }
    
    .url-item {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        font-family: monospace;
        font-size: 0.9em;
    }
    
    .next-url {
        background: #e8f5e8;
        border: 2px solid #28a745;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        font-weight: bold;
        font-family: monospace;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🚗 CarAlyze Multi-URL Scraper</h1>
        <p>Intelligent car listing monitoring with randomized execution and auto-notifications</p>
    </div>
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
    if 'total_runs' not in st.session_state:
        st.session_state.total_runs = 0
    if 'latest_results' not in st.session_state:
        st.session_state.latest_results = {}

    # 1. URL Input Section
    st.subheader("URL Pool Management")
    
    with st.container():
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        
        url_input = st.text_area(
            "Enter URLs (one per line)",
            placeholder="https://www.kleinanzeigen.de/s-autos/c216\nhttps://www.kleinanzeigen.de/s-autos/c216l9442\nhttps://www.kleinanzeigen.de/s-autos/c216l9443",
            help="Paste multiple URLs, each on a new line",
            height=100
        )
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if st.button("Add URLs to Pool", type="primary", use_container_width=True):
                if url_input.strip():
                    new_urls = [url.strip() for url in url_input.strip().split('\n') if url.strip()]
                    added_count = 0
                    
                    for url in new_urls:
                        if url not in st.session_state.url_pool:
                            st.session_state.url_pool.append(url)
                            added_count += 1
                    
                    if added_count > 0:
                        st.success(f"Added {added_count} new URLs to pool")
                        st.rerun()
                    else:
                        st.warning("All URLs already in pool")
                else:
                    st.warning("Please enter at least one URL")
        
        with col2:
            if st.button("Clear Pool", use_container_width=True):
                st.session_state.url_pool = []
                st.session_state.current_url_index = 0
                st.success("URL pool cleared")
                st.rerun()
        
        with col3:
            telegram_test_button()
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. URL Pool Display
    if st.session_state.url_pool:
        st.subheader(f"URL Pool ({len(st.session_state.url_pool)} URLs)")
        
        with st.container():
            for i, url in enumerate(st.session_state.url_pool):
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    # Highlight the current URL that will be scraped next
                    if i == st.session_state.current_url_index:
                        st.markdown(f"""
                        <div class="next-url">
                            <strong>▶ {i+1}. {url[:80]}{'...' if len(url) > 80 else ''}</strong> (Next)
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="url-item">
                            {i+1}. {url[:80]}{'...' if len(url) > 80 else ''}
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("Remove", key=f"remove_{i}", help="Remove this URL", use_container_width=True):
                        st.session_state.url_pool.pop(i)
                        # Adjust current index if needed
                        if st.session_state.current_url_index >= len(st.session_state.url_pool):
                            st.session_state.current_url_index = 0
                        st.rerun()
    else:
        st.info("URL pool is empty. Add URLs above to start.")
        return

    st.divider()

    # 3. Dashboard
    st.subheader("Control Dashboard")
    
    with st.container():
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        
        # Dashboard controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Interval setting
            st.session_state.interval_seconds = st.number_input(
                "Interval (seconds)",
                min_value=30,
                max_value=1800,
                value=st.session_state.interval_seconds,
                step=30,
                help="Time between scraping each URL"
            )
            
            # Show readable format
            minutes = st.session_state.interval_seconds // 60
            seconds = st.session_state.interval_seconds % 60
            if minutes > 0:
                time_display = f"= {minutes}m" + (f" {seconds}s" if seconds > 0 else "")
            else:
                time_display = f"= {seconds}s"
            st.caption(time_display)
        
        with col2:
            # Auto-send toggle
            st.session_state.auto_send_active = st.checkbox(
                "Auto-send to Telegram",
                value=st.session_state.auto_send_active,
                help="Automatically send new listings to Telegram"
            )
        
        with col3:
            # Start/Stop scraping
            if not st.session_state.scraping_active:
                if st.button("Start Auto Scraping", type="primary", use_container_width=True):
                    st.session_state.scraping_active = True
                    st.session_state.last_scrape_time = 0  # Reset timer
                    # Randomize starting URL
                    st.session_state.current_url_index = random.randint(0, len(st.session_state.url_pool) - 1)
                    st.success("Auto scraping started!")
                    st.rerun()
            else:
                if st.button("Stop Auto Scraping", type="secondary", use_container_width=True):
                    st.session_state.scraping_active = False
                    st.info("Auto scraping stopped")
                    st.rerun()
        
        with col4:
            # Manual test
            if st.button("Test Current URL", use_container_width=True):
                if st.session_state.url_pool:
                    current_url = st.session_state.url_pool[st.session_state.current_url_index]
                    _test_single_url(current_url, all_old_path, latest_new_path, root_dir)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()

    # 4. Status Dashboard
    if st.session_state.scraping_active:
        _show_scraping_status(all_old_path, latest_new_path, root_dir)
    else:
        # Show current status when not active
        st.subheader("System Status")
        
        with st.container():
            st.markdown('<div class="status-card">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", "STOPPED")
            
            with col2:
                if st.session_state.url_pool:
                    next_url = st.session_state.url_pool[st.session_state.current_url_index]
                    st.metric("Next URL", f"#{st.session_state.current_url_index + 1}")
                    st.caption(f"{next_url[:40]}{'...' if len(next_url) > 40 else ''}")
            
            with col3:
                st.metric("Total Runs", st.session_state.total_runs)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # 5. Results Display
    if st.session_state.latest_results:
        _show_latest_results()

def _test_single_url(url, all_old_path, latest_new_path, root_dir):
    """Test a single URL."""
    st.info(f"Testing: {url[:50]}...")
    
    try:
        filters = {"custom_url": url}
        
        all_listings, new_listings = get_listings_for_filter(
            filters, all_old_path, latest_new_path, build_search_url_from_custom, root_dir
        )
        
        if all_listings:
            st.success(f"Found {len(all_listings)} total listings")
            if new_listings:
                st.info(f"{len(new_listings)} new listings detected")
            else:
                st.info("No new listings (all cached)")
        else:
            st.warning("No listings found")
            
    except Exception as e:
        st.error(f"Test failed: {str(e)}")

def _show_scraping_status(all_old_path, latest_new_path, root_dir):
    """Show active scraping status with enhanced timer and progress."""
    st.subheader("Active Scraping Status")
    current_time = time.time()
    time_since_last = current_time - st.session_state.last_scrape_time

    if time_since_last >= st.session_state.interval_seconds:
        # Time to scrape next URL
        st.session_state.last_scrape_time = current_time
        current_url = st.session_state.url_pool[st.session_state.current_url_index]
        st.session_state.total_runs += 1
        st.info(f"Scraping URL #{st.session_state.current_url_index + 1} (Run #{st.session_state.total_runs})")
        
        try:
            filters = {"custom_url": current_url}
            all_listings, new_listings = get_listings_for_filter(
                filters, all_old_path, latest_new_path, build_search_url_from_custom, root_dir
            )
            
            # Store results
            st.session_state.latest_results = {
                'url': current_url,
                'url_index': st.session_state.current_url_index,
                'timestamp': current_time,
                'all_listings': all_listings or [],
                'new_listings': new_listings or [],
                'run_number': st.session_state.total_runs
            }
            
            if new_listings:
                st.success(f"Found {len(new_listings)} new listings!")
                if st.session_state.auto_send_active:
                    st.info(f"Auto-sending {len(new_listings)} listings to Telegram...")
                    _send_listings_to_telegram(new_listings)
            else:
                if all_listings:
                    st.info(f"No new listings ({len(all_listings)} cached)")
                else:
                    st.warning("No listings found")
        except Exception as e:
            st.error(f"Scraping failed: {str(e)}")
        
        # Move to next URL (with randomization)
        _move_to_next_url()
        time.sleep(2)
        st.rerun()
    else:
        # Show enhanced countdown and progress
        remaining = st.session_state.interval_seconds - int(time_since_last)
        progress = (st.session_state.interval_seconds - remaining) / st.session_state.interval_seconds
        
        if remaining >= 60:
            mins = remaining // 60
            secs = remaining % 60
            countdown = f"{mins:02d}:{secs:02d}"
            countdown_text = f"{mins}m {secs}s"
        else:
            countdown = f"00:{remaining:02d}"
            countdown_text = f"{remaining}s"
        
        st.markdown(f"""
        <div class="timer-display">
            <h2>⏰ Next scrape in: {countdown}</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.8; font-size: 0.9em;">
                Auto-scraping active • {len(st.session_state.url_pool)} URLs in pool
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="status-card">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                next_url = st.session_state.url_pool[st.session_state.current_url_index]
                st.metric("Next URL", f"#{st.session_state.current_url_index + 1}")
                st.caption(f"{next_url[:50]}{'...' if len(next_url) > 50 else ''}")
            with col2:
                st.metric("Total Runs", st.session_state.total_runs)
                st.caption(f"Interval: {st.session_state.interval_seconds}s")
            with col3:
                st.metric("Progress", f"{int(progress * 100)}%")
                st.caption(f"Remaining: {countdown_text}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.progress(progress, text=f"Time progress: {int(progress * 100)}%")
        time.sleep(1)
        st.rerun()

def _move_to_next_url():
    """Move to next URL with randomization."""
    if len(st.session_state.url_pool) > 1:
        # Create list of available indices (excluding current)
        available_indices = [i for i in range(len(st.session_state.url_pool)) if i != st.session_state.current_url_index]
        
        # Randomly select next URL
        if available_indices:
            st.session_state.current_url_index = random.choice(available_indices)
        else:
            # Fallback to next in sequence
            st.session_state.current_url_index = (st.session_state.current_url_index + 1) % len(st.session_state.url_pool)
    else:
        # Only one URL, keep it
        st.session_state.current_url_index = 0

def _show_latest_results():
    """Show the latest scraping results with enhanced table display."""
    st.subheader("Latest Scraping Results")
    
    results = st.session_state.latest_results
    
    # Results summary
    with st.container():
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            new_count = len(results.get('new_listings', []))
            st.metric("New Listings", new_count)
        
        with col2:
            total_count = len(results.get('all_listings', []))
            st.metric("Total Found", total_count)
        
        with col3:
            url_num = results.get('url_index', 0) + 1
            st.metric("From URL", f"#{url_num}")
        
        with col4:
            timestamp = results.get('timestamp', 0)
            if timestamp > 0:
                time_str = datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
                st.metric("Last Scrape", time_str)
        
        # Show URL that was scraped
        scraped_url = results.get('url', '')
        if scraped_url:
            st.text(f"Source: {scraped_url}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show new listings in table format
    new_listings = results.get('new_listings', [])
    if new_listings:
        st.subheader(f"New Listings Table ({len(new_listings)} items)")
        
        # Create table data
        table_data = []
        for i, listing in enumerate(new_listings):
            table_data.append({
                '#': i + 1,
                'Title': listing.get('Title', 'Unknown')[:60] + ('...' if len(listing.get('Title', '')) > 60 else ''),
                'Price': listing.get('Price', 'N/A'),
                'Location': listing.get('Location', 'N/A'),
                'Year': listing.get('Year', 'N/A'),
                'KM': listing.get('KM', 'N/A'),
                'Fuel': listing.get('Fuel', 'N/A'),
                'URL': listing.get('URL', '')
            })
        
        # Create DataFrame
        df = pd.DataFrame(table_data)
        
        # Display table with custom styling
        st.markdown('<div class="results-table">', unsafe_allow_html=True)
        
        # Configure column display
        column_config = {
            "#": st.column_config.NumberColumn("No.", width="small"),
            "Title": st.column_config.TextColumn("Title", width="large"),
            "Price": st.column_config.TextColumn("Price", width="small"),
            "Location": st.column_config.TextColumn("Location", width="medium"),
            "Year": st.column_config.TextColumn("Year", width="small"),
            "KM": st.column_config.TextColumn("KM", width="small"),
            "Fuel": st.column_config.TextColumn("Fuel", width="small"),
            "URL": st.column_config.LinkColumn("Link", width="small")
        }
        
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True,
            column_config=column_config,
            height=400
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{len(new_listings)} new listings found**")
        
        with col2:
            if st.button("Send to Telegram", type="primary", use_container_width=True):
                _send_listings_to_telegram(new_listings)
        
        with col3:
            if st.button("Export CSV", use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"car_listings_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    else:
        st.info("No new listings found in the last scrape.")

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
