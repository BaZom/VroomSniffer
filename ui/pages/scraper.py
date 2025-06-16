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
scraper_service = get_scraper_service()
url_pool_service = get_url_pool_service()
scheduler_service = get_scheduler_service()

def _show_system_status():
    """Display system status with clean metrics layout matching home page."""
    st.subheader("📊 System Status")
    
    # Get actual data
    try:
        import os
        
        # Get cache stats from session state paths
        all_old_path = st.session_state.get('all_old_path')
        latest_new_path = st.session_state.get('latest_new_path')
        
        # Storage service already initialized at module level
        total_listings = 0
        recent_additions = 0
        cache_size_mb = 0
        
        if all_old_path and os.path.exists(all_old_path):
            stats = storage_service.get_cache_stats(all_old_path)
            total_listings = stats.get('total_listings', 0)
            cache_size_mb = stats.get('cache_size_mb', 0)
        
        if latest_new_path and os.path.exists(latest_new_path):
            recent_data = storage_service.load_cache(latest_new_path)
            recent_additions = len(recent_data) if recent_data else 0
            
    except Exception:
        total_listings = 0
        recent_additions = 0
        cache_size_mb = 0

    # Use metrics component
    metrics_data = [
        {'label': 'Total Listings', 'value': total_listings},
        {'label': 'Recent Additions', 'value': recent_additions},
        {'label': 'Cache Size', 'value': f"{cache_size_mb} MB" if cache_size_mb > 0 else "< 0.01 MB"},
        {'label': 'Total Runs', 'value': scheduler_service.get_total_runs()}
    ]
    
    display_metrics_row(metrics_data, 4)
    
    # Status message
    status_text = "🟢 ACTIVE" if scheduler_service.is_scraping_active() else "🔴 STOPPED"
    scraper_info = f"Scraper: {status_text} | URLs: {len(st.session_state.url_pool)} | Runs: {scheduler_service.get_total_runs()}"
    if scheduler_service.is_scraping_active():
        st.info(f"🚀 {scraper_info}")
    else:
        st.warning(f"⏸️ {scraper_info}")

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
            scheduler_service.select_next_url_index(len(st.session_state.url_pool))
    
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
            
            with st.spinner(f"🔍 Scraping URL #{current_url_index + 1}..."):
                try:
                    filters = {"custom_url": current_url}
                    
                    # Use our ScraperService instance from the module level
                    results = scraper_service.get_listings_for_filter(
                        filters,
                        url_pool_service.build_search_url_from_custom,
                        all_old_path, 
                        latest_new_path,
                        root_dir
                    )
                    
                    all_listings, new_listings = results
                    
                    # Play sound immediately when new listings are found
                    if new_listings:
                        play_sound("Sniff1.wav")
                    
                    st.session_state.latest_results = {
                        'all_listings': all_listings,
                        'new_listings': new_listings,
                        'timestamp': current_time,
                        'url': current_url,
                        'url_index': current_url_index
                    }
                    
                    # Auto-send if enabled
                    if st.session_state.auto_send_active and new_listings:
                        send_listings_to_telegram(notification_service, new_listings)
                    
                    # Update counters using scheduler service
                    total_runs = scheduler_service.record_scrape()
                    st.session_state.total_runs = total_runs  # Keep UI in sync
                    
                    # Pre-select next URL using scheduler service
                    scheduler_service.select_next_url_index(len(st.session_state.url_pool))
                    
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
    display_scrape_results(st.session_state.latest_results)
      
    # Progress Display using component
    display_scraper_progress(scheduler_service)
        
    # Auto-refresh if scraping is active
    if scheduler_service.is_scraping_active():
        time.sleep(2)
        st.rerun()
    else:
        st.empty()
