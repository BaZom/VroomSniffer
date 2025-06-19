import streamlit as st
import sys
import json
import time
from pathlib import Path

# Add the parent directory to the path so we can import from local modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import services via the provider pattern
from providers.services_provider import (
    get_storage_service,
    get_url_pool_service,
    get_scraper_service,
    get_notification_service,
    get_scheduler_service
)

# Import UI components
from ui.components.sound_effects import play_sound
from ui.components.ui_components import display_scrape_results
from ui.components.metrics import display_metrics_row
from ui.components.state_management import initialize_scraper_state
from ui.components.styles import get_main_styles
from ui.components.telegram_controls import send_listings_to_telegram
from ui.components.url_management import display_url_management
from ui.components.scraper_controls import display_scraper_controls, display_scraper_progress

# Initialize services via the provider
storage_service = get_storage_service()
notification_service = get_notification_service()
url_pool_service = get_url_pool_service()
scheduler_service = get_scheduler_service()

# We'll initialize scraper_service with proxy settings from session state when needed

def _show_system_status():
    """Display simplified system status."""
    st.subheader("System Status")
    
    # Get minimal data
    try:
        import os
        
        # Get cache stats from session state paths
        all_old_path = st.session_state.get('all_old_path')
        latest_new_path = st.session_state.get('latest_new_path')
        
        total_listings = 0
        recent_additions = 0
        
        if all_old_path and os.path.exists(all_old_path):
            stats = storage_service.get_cache_stats(all_old_path)
            total_listings = stats.get('total_listings', 0)
        
        if latest_new_path and os.path.exists(latest_new_path):
            recent_data = storage_service.load_cache(latest_new_path)
            recent_additions = len(recent_data) if recent_data else 0
            
    except Exception:
        total_listings = 0
        recent_additions = 0

    # Simplified metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Listings", total_listings)
    with col2:
        st.metric("Recent New", recent_additions)
    with col3:
        st.metric("Runs", scheduler_service.get_total_runs())
        
    # Simple status message
    status = "Active" if scheduler_service.is_scraping_active() else "Stopped"
    st.caption(f"Status: {status} | URLs: {len(st.session_state.url_pool)}")

def show_scraper_page(all_old_path, latest_new_path, root_dir):
    """Multi-URL scraper with clean interface."""
    
    # Store paths in session state for status function
    st.session_state.all_old_path = all_old_path
    st.session_state.latest_new_path = latest_new_path
    
    # Apply centralized styles from components
    st.markdown(get_main_styles(), unsafe_allow_html=True)
    
    # Use the state management component for consistent initialization
    initialize_scraper_state(url_pool_service)
    
    # Additional state specific to this page
    if 'scraping_active' not in st.session_state:
        st.session_state.scraping_active = scheduler_service.is_scraping_active()
        
    # Synchronize session state with scheduler service
    if 'scheduler_initialized' not in st.session_state:
        # This is the first time loading - get default values from scheduler
        st.session_state.scheduler_initialized = True
    elif 'total_runs' in st.session_state:
        # This is a reload - set scheduler state from session
        scheduler_service.set_total_runs(st.session_state.total_runs)
      # Let scheduler handle next URL selection
    if scheduler_service.is_scraping_active() and st.session_state.url_pool:
        if not scheduler_service.is_next_url_selected() or scheduler_service.get_next_url_index() >= len(st.session_state.url_pool):
            # Use random or sequential selection based on user preference
            random_selection = st.session_state.get('random_url_selection', True)
            scheduler_service.select_next_url_index(
                url_count=len(st.session_state.url_pool),
                random_selection=random_selection,
                current_run=scheduler_service.get_total_runs()
            )
    
    # System Status
    _show_system_status()
    
    st.divider()
    
    # URL Management using component
    url_pool_modified = display_url_management(url_pool_service, scheduler_service)
    if url_pool_modified:
        st.rerun()  # Refresh the UI if URLs were modified
    
    st.divider()
    
    # Controls using component
    controls_changed = display_scraper_controls(scheduler_service)
    if controls_changed:
        st.rerun()  # Refresh the UI if controls were changed
    
    # Active Scraping Logic
    if scheduler_service.is_scraping_active() and st.session_state.url_pool:
        if scheduler_service.is_time_to_scrape():
            current_time = time.time()
            
            # Use pre-selected URL from scheduler
            next_url_index = scheduler_service.get_next_url_index()
            if next_url_index < len(st.session_state.url_pool):
                current_url_index = next_url_index
            else:
                current_url_index = 0
            
            current_url = st.session_state.url_pool[current_url_index]
            
            # Create a SINGLE status container to avoid multiple Streamlit element updates
            scrape_container_placeholder = st.container()
            
            # Get URL description if available
            url_description = ""
            url_data = url_pool_service.get_url_data()
            if current_url in url_data:
                url_description = url_data[current_url].get('description', '')
                
            # Scraping phase - create a cleaner header
            scrape_header = f"URL #{current_url_index + 1} of {len(st.session_state.url_pool)}: {current_url[:50]}..."
            if url_description:
                scrape_header = f"{url_description} - {scrape_header}"
                
            # Create the status container once - this avoids the blank page issue
            with scrape_container_placeholder:
                scrape_container = st.status(f"🔍 Scraping {scrape_header}", expanded=True)
                # Add initial message inside container
                with scrape_container:
                    st.caption("🔄 Initializing scraper...")
            
            # Define filters for the current URL
            filters = {"custom_url": current_url}
            
            try:
                # Define enhanced progress callback - uses status updates instead of progress bar
                def scraper_progress_callback(step, message, progress_value):
                    # Add more detailed and user-friendly progress messages
                    if step == "init":
                        icon = "🔄"
                        message = "Setting up scraper..."
                    elif step == "navigate":
                        icon = "🌐"
                        message = "Navigating to page..."
                    elif step == "wait":
                        icon = "⏳"
                        message = "Waiting for content to load..."
                    elif step == "parse":
                        icon = "📋"
                        message = "Extracting listings..."
                    elif step == "scrape":
                        icon = "🔍"
                        message = "Processing data..."
                    elif step == "complete":
                        icon = "✅"
                        message = "Scraping complete!"
                    else:
                        icon = "🔍"
                    
                    # Update the status with step information instead of progress bar
                    with scrape_container:
                        st.caption(f"{icon} {message} ({int(progress_value * 100)}%)")
                
                # Show initial status
                with scrape_container:
                    st.caption("🔄 Initializing scraper...")
                
                # Initialize scraper service with proxy settings from session state
                use_proxy = st.session_state.get('use_proxy', False)
                proxy_type = st.session_state.get('proxy_type', 'NONE')
                scraper_service = get_scraper_service(use_proxy=use_proxy, proxy_type=proxy_type)
                
                # Log proxy settings for debugging
                import requests
                from proxy.manager import ProxyManager, ProxyType
                
                # Show IP information status in UI
                with scrape_container:
                    st.subheader("IP Information")
                    ip_col1, ip_col2 = st.columns(2)
                    
                    # Get direct IP for comparison
                    direct_ip = "Unknown"
                    try:
                        direct_response = requests.get("https://httpbin.org/ip", timeout=10)
                        direct_ip = direct_response.json().get("origin", "Unknown")
                        with ip_col1:
                            st.info(f"Your direct IP: {direct_ip}")
                    except:
                        with ip_col1:
                            st.error("Couldn't retrieve direct IP")
                    
                    # Display proxy information if using proxy
                    if use_proxy:
                        print(f"[INFO] Using proxy: {proxy_type}")
                        
                        if proxy_type == "WEBSHARE_RESIDENTIAL":
                            # Make it clear we're waiting for the actual IP
                            with ip_col2:
                                st.info(f"⏳ WebShare proxy will be used. ACTUAL IP will be shown after scraping completes.")
                        else:
                            with ip_col2:
                                st.warning("Unknown proxy type")
                    else:
                        print("[INFO] Not using proxy")
                        with ip_col2:
                            st.warning("⚠️ Not using proxy - direct IP will be used")
                
                # Use our ScraperService instance with proxy settings
                results = scraper_service.get_listings_for_filter(
                    filters,
                    url_pool_service.build_search_url_from_custom,
                    all_old_path, 
                    latest_new_path,
                    root_dir,
                    progress_callback=scraper_progress_callback
                )
                
                # Unpack results - now it includes used_ip and is_proxy_used
                all_listings, new_listings = results
                
                # Try to get the actual IP used for scraping from ip_tracking.json
                import json
                from pathlib import Path
                
                try:
                    ip_tracking_path = Path(__file__).parent.parent.parent / "storage" / "ip_tracking.json"
                    if ip_tracking_path.exists():
                        with open(ip_tracking_path, "r", encoding="utf-8") as f:
                            tracking_data = json.load(f)
                            
                            # Check if we have data for the current URL
                            if current_url in tracking_data.get("url_ip_mapping", {}):
                                ip_entries = tracking_data["url_ip_mapping"][current_url]
                                if ip_entries:
                                    # Get the most recent IP entry (should be the one we just used)
                                    latest_entry = max(ip_entries, key=lambda x: x.get("last_used", ""))
                                    used_ip = latest_entry.get("ip", "Unknown")
                                    is_proxy_used = latest_entry.get("is_proxy", False)
                                    last_used = latest_entry.get("last_used", "Unknown time")
                                    
                                    # Create a prominent success message showing the IP that was ACTUALLY used
                                    st.success(f"✅ Scraping completed using {'WebShare proxy' if is_proxy_used else 'direct'} IP: **{used_ip}**")
                                    
                                    # Update the detailed IP display with CLEAR labeling
                                    with scrape_container:
                                        st.subheader("IP Information")
                                        ip_col1, ip_col2 = st.columns(2)
                                        
                                        with ip_col1:
                                            st.info(f"Your direct IP: {direct_ip}")
                                        
                                        with ip_col2:
                                            if is_proxy_used:
                                                st.success(f"✅ ACTUAL WebShare IP used: {used_ip}")
                                            else:
                                                st.warning(f"⚠️ DIRECT IP used: {used_ip}")
                                                
                                        st.caption(f"Last scrape time: {last_used}")
                except Exception as e:
                    print(f"[UI ERROR] Could not retrieve IP tracking info: {str(e)}")
                
                # Simplified status updates - no progress bar
                if all_listings:
                    source_info = f"URL #{current_url_index + 1}"
                    if url_description:
                        source_info = f"{url_description}"
                    
                    # Update container with completion message
                    with scrape_container_placeholder:
                        st.success(f"✅ Found {len(all_listings)} listings ({len(new_listings)} new)")
                    
                    # Update status container with completion info
                    with scrape_container:
                        st.caption("✅ Scraping complete!")
                else:
                    # Show warning with no results
                    with scrape_container_placeholder:
                        st.warning(f"⚠️ No listings found")
                    
                    # Update status container with completion info
                    with scrape_container:
                        st.caption("✅ Scraping complete - no listings found")
                
                # Play sound when new listings are found
                if new_listings:
                    play_sound("Sniff1.wav")
                
                st.session_state.latest_results = {
                    'all_listings': all_listings,
                    'new_listings': new_listings,
                    'timestamp': current_time,
                    'url': current_url,
                    'url_index': current_url_index,
                    'url_description': url_description
                }
                
                # Auto-send if enabled (simplified)
                if st.session_state.auto_send_active and new_listings:
                    # Create message container
                    message_container = st.container()
                    
                    # Update status
                    with message_container:
                        st.info(f"Sending {len(new_listings)} notifications...")
                    
                    # Add source URL information for notifications
                    for listing in new_listings:
                        if 'source_url' not in listing:
                            listing['source_url'] = current_url
                            
                    # Create message progress bar
                    message_progress = st.empty()
                    
                    # Send notifications
                    success_count = send_listings_to_telegram(
                        notification_service, 
                        new_listings, 
                        progress_container=message_progress,
                        source_description=url_description
                    )
                    
                    # Update the status message
                    with message_container:
                        if success_count > 0:
                            st.success(f"Sent {success_count} notifications")
                        else:
                            st.error(f"Failed to send")
                        
                # Simple results display
                if all_listings:
                    # Create a consistent results container
                    results_container = st.container()
                    with results_container:
                        # Add collapsible section for listings
                        with st.expander("See results"):
                            display_scrape_results({
                                'all_listings': all_listings,
                                'new_listings': new_listings
                            })
                
                # Update counters using scheduler service
                total_runs = scheduler_service.record_scrape()
                st.session_state.total_runs = total_runs  # Keep UI in sync
                
                # Pre-select next URL using scheduler service with user's selection mode
                random_selection = st.session_state.get('random_url_selection', True)
                scheduler_service.select_next_url_index(
                    url_count=len(st.session_state.url_pool),
                    random_selection=random_selection,
                    current_run=total_runs
                )
                
            except Exception as e:
                # Handle errors in a consistent container
                with scrape_container_placeholder:
                    st.error(f"❌ Scraping failed: {str(e)}")
                st.session_state.last_scrape_time = current_time

    # Display active scraper status and timer
    if scheduler_service.is_scraping_active():
        # Create a dedicated container for a minimal timer without progress duplication
        timer_container = st.container()
        with timer_container:
            # We'll only show a simple "next scrape" timer here without duplicating the progress metrics
            next_scrape_in = max(0, scheduler_service.get_next_scrape_time() - time.time())
            if next_scrape_in <= 0:
                st.caption("⏱️ Preparing next scrape...")
            else:
                st.caption(f"⏱️ Next scrape in {int(next_scrape_in)} seconds")
        
        # Auto-refresh if scraping is active
        time.sleep(1)  # Reduced refresh time for more responsive UI
        st.rerun()
