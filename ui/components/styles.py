"""
Centralized styles for the VroomSniffer UI.
This module contains CSS styles for consistent UI appearance.
"""
import streamlit as st

def get_main_styles():
    """Return the main CSS styles for the application."""
    return """
    <style>
    /* VroomSniffer Color Palette:
    - Midnight Blue: #123C5A (primary)
    - Vibrant Orange: #F57C00 (accent/CTA)
    - Euro Green: #4CAF50 (success/deals)
    - Ice Blue: #D7E9F7 (backgrounds)
    - Graphite Gray: #333333 (text)
    - Soft Gray: #F4F4F4 (light backgrounds)
    */
    
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
        background-color: #F4F4F4;
    }
    
    .main .block-container {
        background-color: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(18, 60, 90, 0.15);
        margin: 1rem auto;
        border: 1px solid #D7E9F7;
    }
    
    /* Sidebar styling - Darker background */
    [data-testid="stSidebar"] {
        background-color: #123C5A !important;
    }
    
    [data-testid="stSidebar"] > div {
        background-color: #123C5A !important;
    }
    
    /* Sidebar text colors */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p {
        color: #D7E9F7 !important;
    }
    
    [data-testid="stSidebar"] .stCaption {
        color: #D7E9F7 !important;
        opacity: 0.8;
    }
    
    /* Sidebar buttons - White background for inactive buttons */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #ffffff !important;
        color: #123C5A !important;
        border: 1px solid #D7E9F7 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #D7E9F7 !important;
        border-color: #123C5A !important;
        color: #123C5A !important;
    }
    
    /* Active button styling - Orange for active buttons */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #F57C00 !important;
        color: #ffffff !important;
        border-color: #F57C00 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background-color: #E06500 !important;
        border-color: #E06500 !important;
    }
    
    /* Main content button styling */
    .stButton > button {
        border-radius: 6px;
        border: 1px solid #123C5A;
        background-color: white !important;
        color: #333333 !important;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #D7E9F7 !important;
        border-color: #123C5A !important;
        color: #123C5A !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: white !important;
        color: #F57C00 !important;
        border-color: #F57C00 !important;
        font-weight: 600 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #D7E9F7 !important;
        border-color: #F57C00 !important;
        color: #F57C00 !important;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #D7E9F7;
        background-color: white;
        color: #333333;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #123C5A;
        box-shadow: 0 0 0 1px #123C5A;
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background-color: #D7E9F7 !important;
        border: 1px solid #123C5A !important;
        border-radius: 6px !important;
        padding: 1rem !important;
    }
    
    /* Success/Info/Warning/Error styling */
    .stSuccess {
        background-color: #E8F5E8 !important;
        border-left: 4px solid #4CAF50 !important;
        color: #333333 !important;
    }
    
    .stInfo {
        background-color: #D7E9F7 !important;
        border-left: 4px solid #123C5A !important;
        color: #333333 !important;
    }
    
    .stWarning {
        background-color: #FFF3E0 !important;
        border-left: 4px solid #F57C00 !important;
        color: #333333 !important;
    }
    
    .stError {
        background-color: #FFEBEE !important;
        border-left: 4px solid #F44336 !important;
        color: #333333 !important;
    }
    
    /* Metrics styling - no boxes, just text */
    [data-testid="metric-container"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0.5rem !important;
        box-shadow: none !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #333333 !important;
    }
    
    /* Divider */
    hr {
        border-color: #D7E9F7;
    }
    
    /* Divider */
    hr {
        border-color: #e0e0e0;
    }
    </style>
    """

def get_scraper_styles():
    """Return the CSS styles for the scraper page."""
    return """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Simple text styling - no boxes */
    
    .status-card {
        background-color: white;
        border: 1px solid #D7E9F7;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(18, 60, 90, 0.1);
    }
    
    .url-item {
        background-color: #F4F4F4;
        border: 1px solid #D7E9F7;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        font-family: monospace;
        font-size: 0.9em;
        color: #333333;
    }
    
    .next-url {
        background-color: #D7E9F7;
        border: 2px solid #F57C00;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        font-weight: bold;
        font-family: monospace;
        font-size: 0.9em;
        color: #123C5A;
    }
    
    .stButton > button {
        height: 2.5rem !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
        min-width: 120px !important;
        margin: 0.2rem 0 !important;
        border-radius: 6px !important;
        border: 1px solid #123C5A !important;
        background-color: white !important;
        color: #333333 !important;
    }
    
    .stButton > button:hover {
        background-color: #D7E9F7 !important;
        border-color: #123C5A !important;
        color: #123C5A !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: white !important;
        color: #F57C00 !important;
        border-color: #F57C00 !important;
        font-weight: 600 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #D7E9F7 !important;
        border-color: #F57C00 !important;
        color: #F57C00 !important;
    }
    
    /* Divider styling */
    hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 1.5rem 0;
    }
    </style>
    """

def apply_main_styles():
    """Apply the main application styles."""
    st.markdown(get_main_styles(), unsafe_allow_html=True)

def apply_scraper_styles():
    """Apply the scraper page styles."""
    st.markdown(get_scraper_styles(), unsafe_allow_html=True)
