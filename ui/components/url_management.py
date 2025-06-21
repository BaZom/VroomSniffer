"""
URL pool management interface components for VroomSniffer UI.
"""
import streamlit as st
from ui.components.url_display import display_url_list_improved as display_url_list

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
    
    # URL input section with description
    col1, col2 = st.columns([3, 1])
    with col1:
        new_url = st.text_input("Enter search URL:", placeholder="https://marketplace-url.com/search...")
    with col2:
        new_description = st.text_input("Description (optional):", placeholder="BMW from 2000...")
    
    # URL management explanation
    st.caption("Note: The URL Pool is temporary and exists only in the current session. The Storage File permanently saves URLs between sessions.")
    
    # URL management buttons
    col1, col2, col3, col4 = st.columns(4)
    modified = False
    
    with col1:
        if st.button("Add URL", type="primary", use_container_width=True):
            built_url = url_pool_service.build_search_url_from_custom(new_url)
            if built_url and built_url not in st.session_state.url_pool:
                st.session_state.url_pool.append(built_url)
                url_pool_service.add_url_to_storage(built_url, description=new_description)
                st.success("✅ URL added!")
                modified = True
            elif built_url in st.session_state.url_pool:
                # Update description if it's provided
                if new_description:
                    url_pool_service.update_url_description(built_url, new_description)
                    st.success("✅ URL already exists. Description updated!")
                else:
                    st.warning("⚠️ URL already exists")
            else:
                st.error("❌ Invalid URL (must start with http:// or https://)")
    
    with col2:
        if st.button("Load All Saved URLs", use_container_width=True, help="Replaces current URL pool with all URLs from storage"):
            saved_urls = url_pool_service.load_saved_urls()
            if not saved_urls:
                st.info("📭 No URLs found in storage")
            else:
                # Clear existing pool and load all URLs from storage
                st.session_state.url_pool = []
                added_count = 0
                
                for url in saved_urls:
                    # Validate saved URLs before adding
                    if url.startswith(('http://', 'https://')):
                        st.session_state.url_pool.append(url)
                        added_count += 1
                        
                if added_count > 0:
                    st.success(f"✅ Loaded {added_count} URLs from storage!")
                    modified = True
                else:
                    st.info("ℹ️ No URLs found in storage")
    
    with col3:
        if st.button("Clear Pool Only", use_container_width=True, 
                   help="Clear URLs from current pool only (won't delete from storage)"):
            st.session_state.url_pool = []
            scheduler_service.stop_scraping()  # Use scheduler service instead of session state
            st.success("✅ Pool cleared! URLs still in storage file.")
            modified = True
    
    with col4:
        if st.button("Clear Storage File", use_container_width=True,
                   help="Clear all URLs from the saved_urls.json file permanently"):
            if url_pool_service.clear_url_storage():
                st.success("✅ Storage file cleared!")
                modified = True
            else:
                st.error("❌ Failed to clear storage")
                
    # Display current URL pool with remove functionality
    if st.session_state.url_pool:
        st.subheader(f"URLs ({len(st.session_state.url_pool)})")
        
        # Use the enhanced URL list display component
        url_list_modified, removed_index = display_url_list(
            st.session_state.url_pool, 
            url_pool_service=url_pool_service,
            next_url_index=scheduler_service.get_next_url_index() if scheduler_service.is_next_url_selected() else None,
            is_scraping_active=scheduler_service.is_scraping_active(),
            is_next_url_selected=scheduler_service.is_next_url_selected()
        )
        
        # Handle URL removal if one was removed
        if url_list_modified:
            modified = True
            
            if removed_index is not None:
                # Remove the URL from the session state pool
                st.session_state.url_pool.pop(removed_index)
                st.rerun()  # Rerun the app to refresh the UI with updated pool
    else:
        st.info("📭 No URLs in pool. Add some URLs to get started!")
    
    return modified
