#!/usr/bin/env python3
"""
WebShare Proxy Verification Tool

This script verifies that the WebShare proxy is properly configured and working.
It checks:
1. Environment variables are set
2. Connection can be established
3. IP is masked correctly
"""

import sys
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from proxy.manager import ProxyManager, ProxyType

def verify_proxy_setup():
    """Verify that the WebShare proxy is properly configured."""
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    webshare_username = os.getenv("WEBSHARE_USERNAME")
    webshare_password = os.getenv("WEBSHARE_PASSWORD")
    webshare_host = os.getenv("WEBSHARE_PROXY_HOST", "p.webshare.io")
    webshare_port = os.getenv("WEBSHARE_PROXY_PORT", "80")
    
    if not webshare_username or not webshare_password:
        print("❌ Missing WebShare credentials!")
        print("Please set WEBSHARE_USERNAME and WEBSHARE_PASSWORD in your .env file.")
        print("Create a .env file in the project root directory if one doesn't exist.")
        return False
    
    # Check direct IP
    try:
        direct_response = requests.get("https://httpbin.org/ip", timeout=10)
        direct_ip = direct_response.json().get("origin", "Unknown")
        print(f"✅ Direct IP connection successful: {direct_ip}")
    except Exception as e:
        print(f"❌ Failed to get direct IP: {str(e)}")
        return False
    
    # Initialize proxy manager
    proxy_manager = ProxyManager(ProxyType.WEBSHARE_RESIDENTIAL)
    
    # Test proxy connection
    if not proxy_manager.test_connection():
        print("❌ WebShare proxy connection failed!")
        print("Please check your credentials and network connection.")
        return False
    
    # Get proxy IP
    try:
        proxy_ip = proxy_manager.get_current_ip()
        print(f"✅ WebShare proxy IP: {proxy_ip}")
        
        if proxy_ip == direct_ip:
            print("⚠️ Warning: Proxy IP is the same as direct IP!")
            print("This suggests the proxy is not working correctly.")
            return False
        else:
            print("✅ Success! Your IP is properly masked by the WebShare proxy.")
            return True
    except Exception as e:
        print(f"❌ Failed to get proxy IP: {str(e)}")
        return False

if __name__ == "__main__":
    print("==== WebShare Proxy Verification ====")
    success = verify_proxy_setup()
    
    if success:
        print("\n✅ WebShare proxy is properly configured and working!")
        sys.exit(0)
    else:
        print("\n❌ WebShare proxy verification failed!")
        sys.exit(1)
