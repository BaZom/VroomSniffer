"""
Reusable UI components for the VroomSniffer UI.
"""
import streamlit as st

def display_url_list(urls, next_url_index=None, is_scraping_active=False, is_next_url_selected=False):
    """
    Display a list of URLs with highlighting for the next URL.
    
    Args:
        urls: List of URLs to display
        next_url_index: Index of next URL to be processed (optional)
        is_scraping_active: Whether scraping is currently active
        is_next_url_selected: Whether next URL has been selected
    """
    if not urls:
        st.info("No URLs in pool. Add URLs to start scraping.")
        return
        
    for i, url in enumerate(urls):
        # Determine if this URL should be highlighted
        highlight_url = (is_scraping_active and 
                       is_next_url_selected and 
                       i == next_url_index)
        
        # Truncate long URLs for display
        display_url = url if len(url) <= 60 else f"{url[:60]}..."
        
        if highlight_url:
            st.markdown(f'<div class="next-url">🎯 NEXT: {i+1}. {display_url}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="url-item">{i+1}. {display_url}</div>', 
                       unsafe_allow_html=True)

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
