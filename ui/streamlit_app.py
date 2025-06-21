import streamlit as st
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from local modules
sys.path.append(str(Path(__file__).parent.parent))

# Import page modules
from ui.pages.home import show_home_page
from ui.pages.scraper import show_scraper_page
from ui.pages.data_storage import show_data_storage_page
from ui.pages.playground import show_playground_page

# Import components
from ui.components.styles import get_main_styles
from ui.components.state_management import initialize_navigation_state, navigate_to

def main():
    """Main multi-page Streamlit application."""
    st.set_page_config(
        page_title="VroomSniffer - Car Monitor", 
        page_icon="🚗", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply centralized styles
    st.markdown(get_main_styles(), unsafe_allow_html=True)
    
    # Setup paths - use the same storage directory as scraper and CLI
    root_dir = Path(__file__).parent.parent
    storage_dir = root_dir / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    all_old_path = storage_dir / "all_old_results.json"
    latest_new_path = storage_dir / "latest_new_results.json"
    
    # Initialize navigation state
    initialize_navigation_state()
    
    # Sidebar navigation
    with st.sidebar:
        # Add VroomSniffer logo
        try:
            st.image("ui/resources/logo6.png", width=200)
        except:
            # Fallback if logo not found
            st.title("VroomSniffer")
        
        st.divider()
        
        # Navigation buttons
        if st.button("🏠 Home", key="nav_home", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "🏠 Home" else "secondary"):
            navigate_to("🏠 Home")
            
        if st.button("🔍 Scraper", key="nav_scraper", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "🔍 Scraper" else "secondary"):
            navigate_to("🔍 Scraper")
            
        if st.button("📊 Data Storage", key="nav_data", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "📊 Data Storage" else "secondary"):
            navigate_to("📊 Data Storage")
            
        if st.button("🎮 Playground", key="nav_playground", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "🎮 Playground" else "secondary"):
            navigate_to("🎮 Playground")
        
        st.divider()
        st.caption("VroomSniffer v1.0")
    
    # Page routing
    if st.session_state.current_page == "🏠 Home":
        show_home_page(all_old_path, latest_new_path)
    elif st.session_state.current_page == "🔍 Scraper":
        show_scraper_page(all_old_path, latest_new_path, root_dir)
    elif st.session_state.current_page == "📊 Data Storage":
        show_data_storage_page(all_old_path, latest_new_path)
    elif st.session_state.current_page == "🎮 Playground":
        show_playground_page(all_old_path, latest_new_path, root_dir)

if __name__ == "__main__":
    main()
