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
        initial_sidebar_state="expanded"    )
      # Simplified CSS - focusing on essential styling only
    clean_css = """
    <style>
    /* Hide Streamlit's default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide Streamlit's automatic navigation links */
    [data-testid="stSidebarNavLink"] {
        display: none !important;
    }
    
    /* Background and main styling */
    .stApp {
        background-color: #f0f0f0;
    }
    
    .main .block-container {
        background-color: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        margin: 1rem auto;
        border: 1px solid #d0d0d0;
    }
    
    /* Sidebar styling - simplified and focused */
    [data-testid="stSidebar"] {
        background-color: #404040 !important;
    }
    
    [data-testid="stSidebar"] > div {
        background-color: #404040 !important;
    }
    
    /* Sidebar text colors */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p {
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] .stCaption {
        color: #b0b0b0 !important;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #505050 !important;
        color: #ffffff !important;
        border-color: #666666 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #606060 !important;
        border-color: #777777 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #777777 !important;
        color: #ffffff !important;
        border-color: #999999 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background-color: #888888 !important;
        border-color: #aaaaaa !important;
    }
    
    /* Main content button styling */
    .stButton > button {
        border-radius: 6px;
        border: 1px solid #666666;
        background-color: white;
        color: #333333;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #f8f8f8;
        border-color: #333333;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #333333;
        color: white;
        border-color: #333333;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #555555;
        border-color: #555555;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #cccccc;
        background-color: white;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #666666;
        box-shadow: 0 0 0 1px #666666;
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background-color: #f8f8f8 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 6px !important;
        padding: 1rem !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #333333 !important;
    }
    
    /* Divider */
    hr {
        border-color: #e0e0e0;
    }
    </style>
    """
    st.markdown(clean_css, unsafe_allow_html=True)
    
    # Setup paths
    root_dir = Path(__file__).parent.parent
    listings_dir = root_dir / "storage" / "listings"
    listings_dir.mkdir(parents=True, exist_ok=True)
    all_old_path = listings_dir / "all_old_results.json"
    latest_new_path = listings_dir / "latest_new_results.json"    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Home"
    
    # Sidebar navigation
    with st.sidebar:
        st.title("CarAlyze")
        st.caption("Car Monitoring System")
        st.divider()
        
        # Navigation buttons
        if st.button("🏠 Home", key="nav_home", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "🏠 Home" else "secondary"):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
            
        if st.button("🔍 Scraper", key="nav_scraper", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "� Scraper" else "secondary"):
            st.session_state.current_page = "🔍 Scraper"
            st.rerun()
            
        if st.button("📊 Data Storage", key="nav_data", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "📊 Data Storage" else "secondary"):
            st.session_state.current_page = "📊 Data Storage"
            st.rerun()
            
        if st.button("🎮 Playground", key="nav_playground", use_container_width=True, 
                    type="primary" if st.session_state.current_page == "🎮 Playground" else "secondary"):
            st.session_state.current_page = "🎮 Playground"
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
