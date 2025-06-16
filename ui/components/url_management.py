"""
URL pool management interface components for VroomSniffer UI.
"""
import streamlit as st
from ui.components.ui_components import display_url_list

def display_url_management(url_pool_service, scheduler_service):
    """
    Display and handle URL management interface.
    
    Args:
        url_pool_service: Instance of UrlPoolService
        scheduler_service: Instance of SchedulerService
    
    Returns:
        True if URL pool was modified, False otherwise
    """
    st.subheader("🔧 URL Management")
    
    # URL input
    new_url = st.text_input("Enter search URL:", placeholder="https://marketplace-url.com/search...")
    
    # URL management buttons
    col1, col2, col3, col4 = st.columns(4)
    modified = False
    
    with col1:
        if st.button("Add URL", type="primary", use_container_width=True):
            built_url = url_pool_service.build_search_url_from_custom(new_url)
            if built_url and built_url not in st.session_state.url_pool:
                st.session_state.url_pool.append(built_url)
                url_pool_service.add_url_to_storage(built_url)
                st.success("✅ URL added!")
                modified = True
            elif built_url in st.session_state.url_pool:
                st.warning("⚠️ URL already exists")
            else:
                st.error("❌ Invalid URL (must start with http:// or https://)")
    
    with col2:
        if st.button("Load Saved URLs", use_container_width=True):
            saved_urls = url_pool_service.load_saved_urls()
            if not saved_urls:
                st.info("📭 No URLs found in storage")
            else:
                added_count = 0
                for url in saved_urls:
                    # Validate saved URLs before adding
                    if url.startswith(('http://', 'https://')) and url not in st.session_state.url_pool:
                        st.session_state.url_pool.append(url)
                        added_count += 1
                        
                if added_count > 0:
                    st.success(f"✅ Loaded {added_count} URLs!")
                    modified = True
                else:
                    st.info("ℹ️ No new URLs to load")
    
    with col3:
        if st.button("Clear Pool", use_container_width=True):
            st.session_state.url_pool = []
            scheduler_service.stop_scraping()  # Use scheduler service instead of session state
            st.success("✅ Pool cleared!")
            modified = True
    
    with col4:
        if st.button("Clear Storage", use_container_width=True):
            if url_pool_service.clear_url_storage():
                st.success("✅ Storage cleared!")
                modified = True
            else:
                st.error("❌ Failed to clear storage")
    
    # Display current URL pool with remove functionality
    if st.session_state.url_pool:
        st.subheader(f"📋 Current URL Pool ({len(st.session_state.url_pool)} URLs)")
        
        for i, url in enumerate(st.session_state.url_pool):
            col1, col2 = st.columns([4, 1])
            with col1:
                # Show URL with truncation for long URLs
                display_url = url if len(url) <= 60 else f"{url[:60]}..."
                  # Highlight the next URL to be scraped
                if (scheduler_service.is_scraping_active() and 
                    scheduler_service.is_next_url_selected() and 
                    i == scheduler_service.get_next_url_index()):
                    st.markdown(f'<div class="next-url">🎯 NEXT: {i+1}. {display_url}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="url-item">{i+1}. {display_url}</div>', unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"remove_{i}", help="Remove from pool"):
                    st.session_state.url_pool.pop(i)
                    return True  # URL pool modified
    else:
        st.info("📭 No URLs in pool. Add some URLs to get started!")
    
    return modified
