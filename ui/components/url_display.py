"""
URL display components for the VroomSniffer UI.
This module contains improved components for URL display with better NEXT indicators.
"""
import streamlit as st

def display_url_list_improved(urls, url_pool_service=None, next_url_index=None, is_scraping_active=False, is_next_url_selected=False):
    """
    Display a list of URLs with clear highlighting for the next URL and metadata.
    
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
    
    # Skip displaying a separate next URL indicator as it will be shown in the expanders
    
    # Now display all URLs
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
        
        # Get bandwidth stats if available
        bandwidth_stats = None
        if url_pool_service and hasattr(url_pool_service, 'storage_service'):
            bandwidth_stats = url_pool_service.storage_service.get_bandwidth_stats_for_url(url)
        
        # Create simple title with minimal indicator for the next URL
        title_prefix = "→ " if highlight_url else ""
        expander_title = f"{title_prefix}{i+1}. {display_url}"
            
        # Create an expander for each URL with details
        with st.expander(expander_title, expanded=highlight_url):
            # Put description and actions in the layout
            if description:
                st.markdown(f"**Description:** {description}")
            
            # Description input field
            new_description = st.text_input(
                "Description",
                value=description,
                key=f"desc_{i}_{url[-10:]}"
            )
            
            # Use a horizontal layout for buttons and stats
            btn1, btn2, btn3, stats1, stats2, stats3 = st.columns([1.2, 1.2, 1.2, 0.8, 0.8, 0.8])
            
            with btn1:
                if st.button("💾 Save Description", key=f"save_{i}_{url[-10:]}", help="Save the description for this URL"):
                    if url_pool_service and url_pool_service.update_url_description(url, new_description):
                        st.success("✓")
                        modified = True
            
            with btn2:
                if st.button("🔄 Remove from Pool", key=f"remove_pool_{i}_{url[-10:]}", 
                           help="Remove URL from current session only (temporary)"):
                    removed_index = i
                    modified = True
                    st.info("Removed")
            
            with btn3:
                if st.button("🗑️ Delete Permanently", key=f"delete_{i}_{url[-10:]}", 
                          type="primary", help="Delete URL permanently from storage"):
                    if url_pool_service and url_pool_service.remove_url_from_storage(url):
                        removed_index = i
                        modified = True
                        st.warning("Deleted")
            
            # Stats in the same row to avoid nesting
            with stats1:
                st.metric("Runs", run_count)
            
            with stats2:
                st.metric("New", total_listings, help="Total count of unique new listings found")
                
            with stats3:
                if bandwidth_stats:
                    st.metric("BW", f"{bandwidth_stats['latest_bandwidth_kb']} KB", 
                             help=f"Bandwidth: Avg {bandwidth_stats['average_bandwidth_kb']} KB, Efficiency {bandwidth_stats['latest_efficiency']}%")
                else:
                    st.metric("BW", "N/A", help="No bandwidth data available")
                
            if last_run:
                st.caption(f"Last run: {last_run}")
            if bandwidth_stats:
                st.caption(f"Efficiency: {bandwidth_stats['latest_efficiency']}% blocked, {bandwidth_stats['total_scrapes']} scrapes")
    
    return modified, removed_index
