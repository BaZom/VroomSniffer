"""
API Configuration UI Components
------------------------------
Components for configuring API credentials and settings.
"""
import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

def display_api_configuration():
    """Display API configuration interface."""
    st.subheader("🔧 API Configuration")
    
    # Load environment variables
    env_file = find_dotenv()
    if not env_file:
        # Create .env file if it doesn't exist
        env_file = Path.cwd() / ".env"
        env_file.touch()
        
    load_dotenv(env_file)
    
    with st.expander("Mobile.de API Settings"):
        st.write("**Configure mobile.de API credentials**")
        st.info("Contact mobile.de support for API access: 030 81097-500 or service@team.mobile.de")
        
        # Current credentials
        current_username = os.getenv("MOBILE_DE_API_USERNAME", "")
        current_password = os.getenv("MOBILE_DE_API_PASSWORD", "")
        current_base_url = os.getenv("MOBILE_DE_API_BASE_URL", "https://api.mobile.de")
        
        # Input fields
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "API Username",
                value=current_username,
                help="Your mobile.de API username"
            )
            
        with col2:
            password = st.text_input(
                "API Password",
                value=current_password,
                type="password",
                help="Your mobile.de API password"
            )
            
        base_url = st.text_input(
            "API Base URL",
            value=current_base_url,
            help="mobile.de API base URL (default: https://api.mobile.de)"
        )
        
        # Buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Credentials", use_container_width=True):
                try:
                    # Save to .env file
                    set_key(env_file, "MOBILE_DE_API_USERNAME", username)
                    set_key(env_file, "MOBILE_DE_API_PASSWORD", password)
                    set_key(env_file, "MOBILE_DE_API_BASE_URL", base_url)
                    
                    # Update environment variables in current session
                    os.environ["MOBILE_DE_API_USERNAME"] = username
                    os.environ["MOBILE_DE_API_PASSWORD"] = password
                    os.environ["MOBILE_DE_API_BASE_URL"] = base_url
                    
                    st.success("✅ Credentials saved successfully!")
                    
                    # Try to configure the API client
                    if username and password:
                        from api.manager import get_api_manager
                        api_manager = get_api_manager()
                        success = api_manager.configure_mobile_de(username, password, base_url)
                        
                        if success:
                            st.success("✅ mobile.de API configured successfully!")
                        else:
                            st.error("❌ Failed to configure mobile.de API. Check credentials.")
                    
                except Exception as e:
                    st.error(f"❌ Failed to save credentials: {str(e)}")
        
        with col2:
            if st.button("🧪 Test Connection", use_container_width=True):
                if not username or not password:
                    st.warning("⚠️ Please enter username and password first")
                else:
                    try:
                        from api.manager import get_api_manager
                        api_manager = get_api_manager()
                        
                        # Configure and test
                        success = api_manager.configure_mobile_de(username, password, base_url)
                        
                        if success:
                            st.success("✅ Connection test successful!")
                        else:
                            st.error("❌ Connection test failed. Check credentials and API access.")
                            
                    except Exception as e:
                        st.error(f"❌ Connection test failed: {str(e)}")
        
        with col3:
            if st.button("🗑️ Clear Credentials", use_container_width=True):
                try:
                    # Remove from .env file
                    set_key(env_file, "MOBILE_DE_API_USERNAME", "")
                    set_key(env_file, "MOBILE_DE_API_PASSWORD", "")
                    set_key(env_file, "MOBILE_DE_API_BASE_URL", "https://api.mobile.de")
                    
                    # Clear from current session
                    os.environ.pop("MOBILE_DE_API_USERNAME", None)
                    os.environ.pop("MOBILE_DE_API_PASSWORD", None)
                    os.environ["MOBILE_DE_API_BASE_URL"] = "https://api.mobile.de"
                    
                    st.success("✅ Credentials cleared!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Failed to clear credentials: {str(e)}")
        
        # Show current status
        st.divider()
        st.write("**Current Status:**")
        
        from api.manager import get_api_manager
        api_manager = get_api_manager()
        platform_status = api_manager.get_platform_status()
        
        mobile_de_status = platform_status.get("mobile.de", {})
        if mobile_de_status.get("available", False):
            st.success("✅ mobile.de API: Configured and ready")
        else:
            st.warning("⚠️ mobile.de API: Not configured")
            
        scraper_status = platform_status.get("scraper", {})
        if scraper_status.get("available", False):
            st.success("✅ Web Scraper: Available")


def auto_configure_api_from_env():
    """Auto-configure API clients from environment variables."""
    try:
        # Load environment variables
        load_dotenv()
        
        username = os.getenv("MOBILE_DE_API_USERNAME")
        password = os.getenv("MOBILE_DE_API_PASSWORD")
        base_url = os.getenv("MOBILE_DE_API_BASE_URL", "https://api.mobile.de")
        
        if username and password:
            from api.manager import get_api_manager
            api_manager = get_api_manager()
            
            # Check if already configured by checking status
            status = api_manager.get_platform_status()
            if not status.get("mobile.de", {}).get("configured", False):
                success = api_manager.configure_mobile_de(username, password, base_url)
                return success
            else:
                return True  # Already configured
        
        return False
        
    except Exception as e:
        # Don't show error in UI during auto-configuration
        # st.error(f"Failed to auto-configure API: {str(e)}")
        return False
