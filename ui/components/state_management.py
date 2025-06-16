"""
Session state management for the VroomSniffer UI.
This module helps manage state consistently across pages.
"""
import streamlit as st

def initialize_navigation_state():
    """Initialize navigation state if not already present."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Home"

def initialize_scraper_state(url_pool_service):
    """Initialize scraper-related session state."""
    if 'url_pool' not in st.session_state:
        st.session_state.url_pool = []
        # Load saved URLs on first initialization
        saved_urls = url_pool_service.load_saved_urls()
        st.session_state.url_pool.extend(saved_urls)
    
    if 'auto_send_active' not in st.session_state:
        st.session_state.auto_send_active = False
    
    if 'latest_results' not in st.session_state:
        st.session_state.latest_results = {}
    
    if 'sound_effects_enabled' not in st.session_state:
        st.session_state.sound_effects_enabled = False

def initialize_cache_state():
    """Initialize cache-related session state."""
    if 'current_filtered_listings' not in st.session_state:
        st.session_state.current_filtered_listings = None
    
    if 'confirm_clear_cache' not in st.session_state:
        st.session_state.confirm_clear_cache = False
    
    if 'confirm_clear_all' not in st.session_state:
        st.session_state.confirm_clear_all = False

def clear_cache_state():
    """Clear cache-related session state."""
    # Clear any cached session state data
    for key in list(st.session_state.keys()):
        if 'cache' in key.lower():
            del st.session_state[key]

def navigate_to(page):
    """Navigate to the specified page."""
    st.session_state.current_page = page
    st.rerun()

def set_scraper_state(scraping_active=None, interval=None):
    """Update scraper state variables."""
    if scraping_active is not None:
        st.session_state.scraping_active = scraping_active
    
    if interval is not None:
        st.session_state.interval = interval
