"""
Reusable UI components for the VroomSniffer UI.
"""
import streamlit as st

def display_url_list(urls, url_pool_service=None, next_url_index=None, is_scraping_active=False, is_next_url_selected=False):
    """
    Display a list of URLs with highlighting for the next URL and metadata.
    
    Args:
        urls: List of URLs to display
        url_pool_service: UrlPoolService instance to get URL metadata
        next_url_index: Index of next URL to be processed (optional)
        is_scraping_active: Whether scraping is currently active
        is_next_url_selected: Whether next URL has been selected
        
    Returns:
        tuple: (modified, removed_url_index) - whether URL pool was modified and index of removed URL
    """
    if not urls:
        st.info("No URLs in pool. Add URLs to start scraping.")
        return False, None
    
    # Get URL metadata if service is provided
    url_data = {}
    if url_pool_service:
        url_data = url_pool_service.get_url_data()
    
    modified = False
    removed_index = None
        
    for i, url in enumerate(urls):
        # Determine if this URL should be highlighted
        highlight_url = (is_scraping_active and 
                       is_next_url_selected and 
                       i == next_url_index)
        
        # Truncate long URLs for display
        display_url = url if len(url) <= 60 else f"{url[:60]}..."
        
        # Get metadata if available
        description = ""
        run_count = 0
        total_listings = 0
        last_run = ""
        
        if url in url_data:
            description = url_data[url].get('description', '')
            stats = url_data[url].get('stats', {})
            run_count = stats.get('run_count', 0)
            total_listings = stats.get('total_listings', 0)
            last_run = stats.get('last_run', '')
        
        # Create an expander for each URL with details
        with st.expander(f"{i+1}. {display_url}", expanded=highlight_url):
            # URL info
            col1, col2 = st.columns([3, 1])
            with col1:
                if description:
                    st.markdown(f"**Description:** {description}")
                
                # Add description input field
                new_description = st.text_input(
                    "Enter or update description",
                    value=description,
                    key=f"desc_{i}_{url[-10:]}"  # Create unique key
                )
                
                # Control buttons row with save description button, remove from pool, and remove from storage
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                
                # Save button for description
                with btn_col1:
                    if st.button("Save Description", key=f"save_{i}_{url[-10:]}"):
                        if url_pool_service and new_description != description:
                            if url_pool_service.update_url_description(url, new_description):
                                # More visible success feedback
                                st.success("✅ Description saved successfully!", icon="✅")
                                modified = True
                            else:
                                st.error("❌ Failed to update description")
                
                # Remove from pool button (only removes from current session)
                with btn_col2:
                    if st.button("🔄 Remove from Pool", key=f"remove_pool_{i}_{url[-10:]}", 
                               type="secondary", help="Remove this URL from current pool only (temporary)"):
                        removed_index = i
                        modified = True
                        st.warning(f"✅ URL removed from pool: {display_url}")
                
                # Remove permanently button (removes from JSON storage)
                with btn_col3:
                    if st.button("🗑️ Delete Permanently", key=f"remove_storage_{i}_{url[-10:]}", 
                               type="secondary", help="Remove this URL permanently from saved storage"):
                        if url_pool_service:
                            url_pool_service.remove_url_from_storage(url)
                            removed_index = i
                            modified = True
                            st.error(f"🗑️ URL permanently deleted: {display_url}")
            
            with col2:
                # Stats display
                st.metric("Runs", run_count)
                st.metric("Total Listings", total_listings)
                if last_run:
                    st.caption(f"Last run: {last_run}")
        
        # Also display URL with highlight if needed (outside expander)
        if highlight_url:
            st.markdown(f'<div class="next-url">🎯 NEXT: {i+1}. {display_url}</div>', 
                       unsafe_allow_html=True)
    
    return modified, removed_index

def display_status_card(title, message):
    """
    Display a status card with title and message.
    
    Args:
        title: Title text for the status card
        message: Message text for the status card
    """
    st.markdown('<div class="status-card">', unsafe_allow_html=True)
    st.write(f"**{title}**")
    st.write(message)
    st.markdown('</div>', unsafe_allow_html=True)

def display_scrape_results(results):
    """
    Display scraping results in a standardized format.
    
    Args:
        results: Dictionary with scraping results
    """
    if not results:
        return
        
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

def create_action_buttons(actions):
    """
    Create a row of action buttons.
    
    Args:
        actions: List of dicts with 'label', 'callback', and optional 'primary' (bool)
                 and 'args' (list) keys
    """
    columns = st.columns(len(actions))
    results = []
    
    for i, action in enumerate(actions):
        with columns[i]:
            label = action.get('label', '')
            callback = action.get('callback', None)
            is_primary = action.get('primary', False)
            args = action.get('args', [])
            key = action.get('key', f"action_{i}")
            help_text = action.get('help', None)
            container_width = action.get('use_container_width', True)
            
            button_type = "primary" if is_primary else "secondary"
            
            if callback:
                clicked = st.button(
                    label, 
                    key=key,
                    type=button_type, 
                    help=help_text,
                    use_container_width=container_width
                )
                
                if clicked:
                    if args:
                        result = callback(*args)
                    else:
                        result = callback()
                    results.append(result)
            else:
                clicked = st.button(
                    label, 
                    key=key,
                    type=button_type, 
                    help=help_text,
                    use_container_width=container_width
                )
                results.append(clicked)
    
    return results

def show_error_message(message, exception=None):
    """
    Show an error message with optional exception details.
    
    Args:
        message: Main error message to display
        exception: Optional exception object for details
    """
    st.error(f"❌ {message}")
    
    if exception and st.session_state.get('debug_mode', False):
        with st.expander("Error Details"):
            st.code(str(exception))

def show_success_message(message):
    """Show a success message."""
    st.success(f"✅ {message}")

def show_info_message(message):
    """Show an info message."""
    st.info(f"ℹ️ {message}")
