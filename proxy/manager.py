# Proxy Manager
# -------------
# Manages and rotates IP addresses to avoid being blocked by target websites.

import os
import requests
from dotenv import load_dotenv
from enum import Enum

# Load environment variables
load_dotenv()

class ProxyType(Enum):
    """
    Simplified proxy types supported by VroomSniffer.
    Limited to direct connections and WebShare residential proxies.
    """
    NONE = 0               # Direct connection (no proxy)
    WEBSHARE_RESIDENTIAL = 1  # WebShare rotating residential proxies

class ProxyManager:
    """
    Manages WebShare residential proxy connections for web scraping.
    
    A streamlined proxy manager that supports:
    - Direct connections (NONE): Connect without any proxy
    - WebShare residential proxies (WEBSHARE_RESIDENTIAL): Connect through WebShare's rotating residential proxy service
    
    This simplified implementation focuses on reliability and ease of maintenance.
    """
    
    def __init__(self, proxy_type=ProxyType.NONE):
        """
        Initialize the proxy manager.
        
        Args:
            proxy_type: Type of proxy to use (NONE or WEBSHARE_RESIDENTIAL)
        """
        self.proxy_type = proxy_type
        self.webshare_username = os.getenv("WEBSHARE_USERNAME", "")
        self.webshare_password = os.getenv("WEBSHARE_PASSWORD", "")
        self.webshare_proxy_host = os.getenv("WEBSHARE_PROXY_HOST", "p.webshare.io")
        self.webshare_proxy_port = os.getenv("WEBSHARE_PROXY_PORT", "80")
        
    def get_request_proxies(self):
        """
        Get WebShare residential proxy configuration for the requests library.
        
        Returns:
            dict: Proxy configuration for requests, or None if using direct connection
        """
        if self.proxy_type == ProxyType.NONE:
            return None
        
        # WebShare residential proxy configuration
        proxy_url = f"http://{self.webshare_username}:{self.webshare_password}@{self.webshare_proxy_host}:{self.webshare_proxy_port}"
        return {
            'http': proxy_url,
            'https': proxy_url
        }
        
    def get_playwright_proxy(self):
        """
        Get WebShare residential proxy configuration for Playwright.
        
        Returns:
            dict: Proxy configuration for Playwright, or None if using direct connection
        """
        if self.proxy_type == ProxyType.NONE:
            return None
        
        # WebShare residential proxy configuration for Playwright
        return {
            "server": f"http://{self.webshare_proxy_host}:{self.webshare_proxy_port}",
            "username": self.webshare_username,
            "password": self.webshare_password
        }
        
    def test_connection(self, test_url="https://httpbin.org/ip"):
        """
        Test if the WebShare proxy is working by making a request.
        
        Args:
            test_url: URL to test the connection with
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Direct connections don't need testing
        if self.proxy_type == ProxyType.NONE:
            return True
        
        # Test WebShare residential proxy connection
        try:
            proxies = self.get_request_proxies()
            response = requests.get(test_url, proxies=proxies, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"WebShare proxy connection failed: {str(e)}")
            return False
            
    def get_current_ip(self):
        """
        Get the current IP address used by the connection (direct or WebShare proxy).
        
        Returns:
            str: IP address or error message if retrieval failed
        """
        try:
            # Increased timeout from 10 to 20 seconds
            response = requests.get("https://httpbin.org/ip", 
                                   proxies=self.get_request_proxies(), 
                                   timeout=20)
            
            if response.status_code == 200:
                return response.json().get("origin", "Unknown")
            else:
                return f"Error: Status code {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
            
    @staticmethod
    def create_from_environment():
        """
        Create a proxy manager based on environment variables.
        
        Returns:
            ProxyManager: Configured proxy manager instance with WEBSHARE_RESIDENTIAL or NONE
        """
        load_dotenv()
        
        # Simple ternary to determine proxy type from environment
        proxy_type_str = os.getenv("PROXY_TYPE", "NONE")
        proxy_type = ProxyType.WEBSHARE_RESIDENTIAL if proxy_type_str == "WEBSHARE_RESIDENTIAL" else ProxyType.NONE
            
        return ProxyManager(proxy_type)
