"""
Scraper control components for the VroomSniffer UI.
"""
import os
import time
import streamlit as st
import requests
from dotenv import load_dotenv
from ui.components.sound_effects import play_sound
from proxy.manager import ProxyManager, ProxyType

def display_scraper_controls(scheduler_service):
    """
    Display simplified scraper control interface.
    
    Args:
        scheduler_service: Instance of SchedulerService
        
    Returns:
        True if any setting was changed, False otherwise
    """
    st.subheader("Controls")
    
    # Simplified controls layout
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    changed = False
    
    with col1:
        if not scheduler_service.is_scraping_active():
            if st.button("▶️ Start", type="primary", use_container_width=True):
                if st.session_state.url_pool:
                    scheduler_service.start_scraping()
                    # Pre-select first URL using scheduler service
                    random_selection = st.session_state.get('random_url_selection', True)
                    scheduler_service.select_next_url_index(
                        url_count=len(st.session_state.url_pool),
                        random_selection=random_selection,
                        current_run=scheduler_service.get_total_runs()
                    )
                    
                    st.success("Started")
                    play_sound("Vroom 1.mp3")
                    changed = True
                else:
                    st.error("Add URLs first")
        else:
            if st.button("⏹️ Stop", use_container_width=True):
                scheduler_service.stop_scraping()
                st.success("Stopped")
                changed = True
    
    with col2:        # Store previous state to detect changes
        prev_auto_send = st.session_state.get('auto_send_active', False)
        prev_sound_effects = st.session_state.get('sound_effects_enabled', False)
        prev_random_selection = st.session_state.get('random_url_selection', True)
        prev_use_proxy = st.session_state.get('use_proxy', False)
        prev_proxy_type = st.session_state.get('proxy_type', 'NONE')
        
        # Add controls
        with st.expander("Advanced Settings"):
            # Existing settings
            st.session_state.auto_send_active = st.toggle("Auto-send new findings", prev_auto_send)
            st.session_state.sound_effects_enabled = st.toggle("Sound effects", prev_sound_effects)
            st.session_state.random_url_selection = st.toggle("Random URL selection", prev_random_selection)
            
            # Proxy settings
            st.divider()
            st.write("**Proxy settings**")
            st.session_state.use_proxy = st.toggle("Use proxy", prev_use_proxy)
            
            # Only show proxy type selection if use_proxy is enabled
            if st.session_state.use_proxy:
                # IMPORTANT: Only show the two supported proxy types
                proxy_options = {
                    "None": "NONE",
                    "WebShare Residential": "WEBSHARE_RESIDENTIAL"
                }
                st.session_state.proxy_type = st.selectbox(
                    "Proxy type",
                    options=list(proxy_options.keys()),
                    format_func=lambda x: x,
                    index=list(proxy_options.values()).index(prev_proxy_type) if prev_proxy_type in proxy_options.values() else 0
                )
                # Convert display name to enum value
                st.session_state.proxy_type = proxy_options[st.session_state.proxy_type]
                
                # Add verification button for WebShare Residential
                if st.session_state.proxy_type == "WEBSHARE_RESIDENTIAL":
                    st.info("🔄 Using WebShare rotating residential proxies. IP addresses used will be tracked.")
                    
                    if st.button("Verify Proxy"):
                        verify_webshare_proxy()
            else:
                st.session_state.proxy_type = "NONE"
                
        if (prev_auto_send != st.session_state.auto_send_active or 
            prev_sound_effects != st.session_state.sound_effects_enabled or
            prev_random_selection != st.session_state.random_url_selection or
            prev_use_proxy != st.session_state.use_proxy or
            prev_proxy_type != st.session_state.proxy_type):
            changed = True
    
    with col3:
        prev_interval = scheduler_service.get_interval()
        interval = st.number_input(
            "Interval (sec):", 
            min_value=scheduler_service.MIN_INTERVAL, 
            max_value=scheduler_service.MAX_INTERVAL, 
            value=prev_interval,
            step=5
        )
        
        if interval != prev_interval:
            scheduler_service.set_interval(interval)
            changed = True
    
    return changed

def display_scraper_progress(current_url_index, total_urls, scheduler_service):
    """Display improved progress indicators for scraping without duplicate progress bars."""
    
    # Create a clean status display with key information
    status_container = st.status("Scraper Status", expanded=True)
    
    with status_container:
        # Information grid - 2x2 layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Show total runs with unlimited indicator
            total_runs = scheduler_service.get_total_runs() or 0
            st.metric("Total Runs", f"{total_runs}/∞", help="Total scrapes performed / No limit")
        
        with col2:
            # Show URL progress as fraction
            st.metric("URL Progress", f"{current_url_index + 1} of {total_urls}", 
                     help="Current URL being processed / Total URLs")
        
        # Timeline display
        next_scrape_in = max(0, scheduler_service.get_next_scrape_time() - time.time())
        
        # Create a visual timeline display instead of a progress bar
        time_info = f"Next scrape in: {int(next_scrape_in)} seconds" if next_scrape_in > 0 else "Scraping now..."
        
        # Display using emoji indicators
        if next_scrape_in <= 0:
            st.info("⚡ **Scraping active now!**")
        elif next_scrape_in < 5:
            st.info(f"🔜 **Scraping starting in {int(next_scrape_in)} seconds**")
        else:
            st.info(f"⏱️ **Next scrape in {int(next_scrape_in)} seconds**")
            
        # Additional context without progress bars
        proxy_status = "Yes" if st.session_state.get('use_proxy', False) else "No" 
        st.caption(f"**Configuration:** Interval: {scheduler_service.get_interval()} sec | Using proxy: {proxy_status}")
        
    return status_container

def verify_webshare_proxy():
    """Helper function to verify WebShare residential proxy configuration."""
    # Load environment variables
    load_dotenv()
    
    # Check WebShare credentials
    webshare_username = os.getenv("WEBSHARE_USERNAME", "")
    webshare_password = os.getenv("WEBSHARE_PASSWORD", "")
    
    if not webshare_username or not webshare_password:
        st.error("WebShare credentials missing! Add WEBSHARE_USERNAME and WEBSHARE_PASSWORD to your .env file.")
        return
        
    try:
        # Get direct IP first
        direct_response = requests.get("https://httpbin.org/ip", timeout=10)
        direct_ip = direct_response.json().get("origin", "Unknown")
        
        # Get proxy IP
        proxy_manager = ProxyManager(ProxyType.WEBSHARE_RESIDENTIAL)
        proxy_ip = proxy_manager.get_current_ip()
        
        # Compare IPs to check if proxy is working
        if proxy_ip == direct_ip:
            st.warning(f"⚠️ Proxy not working! Both IPs are the same: {direct_ip}")
        else:
            st.success(f"✅ Proxy working! Direct IP: {direct_ip}, Proxy IP: {proxy_ip}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
