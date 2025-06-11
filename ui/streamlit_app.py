import streamlit as st
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from local modules
sys.path.append(str(Path(__file__).parent.parent))

# Import page modules
from ui.page_modules.home import show_home_page
from ui.page_modules.scraper import show_scraper_page
from ui.page_modules.data_storage import show_data_storage_page
from ui.page_modules.playground import show_playground_page

def main():
    """Main multi-page Streamlit application."""
    st.set_page_config(
        page_title="CarAlyze - Car Monitor", 
        page_icon="🚗", 
        layout="wide",
        initial_sidebar_state="expanded"
    )      # Clean CSS styling
    clean_css = """    <style>
    /* Hide Streamlit's default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-1d391kg {padding-top: 1rem;}
    
    /* Clean styling */
    .main > div {
        padding: 2rem;
        max-width: 1200px;
    }
    
    /* Simple button styling */
    .stButton > button {
        border-radius: 5px;
        border: 1px solid #ddd;
        padding: 0.5rem 1rem;
    }
    
    /* Clean text input */
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    </style>
    """
    st.markdown(clean_css, unsafe_allow_html=True)
    
    # Setup paths
    root_dir = Path(__file__).parent.parent
    listings_dir = root_dir / "storage" / "listings"
    listings_dir.mkdir(parents=True, exist_ok=True)
    all_old_path = listings_dir / "all_old_results.json"
    latest_new_path = listings_dir / "latest_new_results.json"    # Initialize page state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Home"
      # Clean sidebar navigation
    with st.sidebar:
        st.title("CarAlyze")
        st.caption("Car Monitoring System")
        st.divider()
        
        # Simple navigation buttons
        pages = [
            ("Home", "🏠 Home"),
            ("Scraper", "🔍 Scraper"),
            ("Data Storage", "📊 Data Storage"),
            ("Playground", "🎮 Playground")
        ]
        
        for page_name, page_key in pages:
            is_current = st.session_state.current_page == page_key
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True, 
                        type="primary" if is_current else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.divider()
        st.caption("CarAlyze v2.0")
    
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
