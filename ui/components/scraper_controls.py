"""
Scraper control components for the VroomSniffer UI.
"""
import streamlit as st
from ui.components.sound_effects import play_sound

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
        
        st.session_state.auto_send_active = st.checkbox(
            "📤 Auto-send to Telegram", 
            value=st.session_state.get('auto_send_active', False)
        )
        
        st.session_state.sound_effects_enabled = st.checkbox(
            "🔊 Sound Effects", 
            value=st.session_state.get('sound_effects_enabled', False),
            help="Enable/disable sound effects for scraping events"
        )
        
        # Add random URL selection toggle
        st.session_state.random_url_selection = st.checkbox(
            "🎲 Random URL Selection", 
            value=st.session_state.get('random_url_selection', True),
            help="Select URLs randomly instead of sequentially"
        )
        if (prev_auto_send != st.session_state.auto_send_active or 
            prev_sound_effects != st.session_state.sound_effects_enabled or
            prev_random_selection != st.session_state.random_url_selection):
            changed = True
    
    with col3:
        prev_interval = scheduler_service.get_interval()
        interval = st.number_input(
            "Interval (sec):", 
            min_value=scheduler_service.MIN_INTERVAL, 
            max_value=scheduler_service.MAX_INTERVAL, 
            value=prev_interval,
            step=30
        )
        
        # Update scheduler service with new interval if changed
        if interval != prev_interval:
            scheduler_service.set_interval(interval)
            changed = True
            
    return changed

def display_scraper_progress(scheduler_service):
    """
    Display simplified scraper progress information.
    
    Args:
        scheduler_service: Instance of SchedulerService
    """
    if not scheduler_service.is_scraping_active():
        return
        
    # Create a unique key for this container to avoid duplication
    with st.container():
        # Use a simpler separator
        st.divider()
        
        # Show minimal status information
        total_runs = scheduler_service.get_total_runs()
        time_until_next = scheduler_service.get_time_until_next_scrape()
        progress = scheduler_service.get_progress_percentage()
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if time_until_next > 0:
                st.progress(progress, text=f"Next: {int(time_until_next)}s")
            else:
                st.progress(1.0, text="Ready to scrape")
        with col2:
            st.metric("Total runs", total_runs)
