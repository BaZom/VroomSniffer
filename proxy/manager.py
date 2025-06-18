# Proxy Manager
# -------------
# Manages and rotates IP addresses to avoid being blocked by target websites.

import os
import random
import requests
from dotenv import load_dotenv
from enum import Enum

# Load environment variables
load_dotenv()

class ProxyType(Enum):
    """Types of proxies supported"""
    NONE = 0
    WEBSHARE_RESIDENTIAL = 1

class ProxyManager:
    """
    Manages WebShare residential proxy connections for web scraping.
    
    Features:
    - WebShare residential proxy support
    - Connection testing
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
        Get proxies dictionary for use with the requests library.
        
        Returns:
            dict: Proxy configuration for requests, or None if no proxy should be used
        """
        if self.proxy_type == ProxyType.NONE:
            return None
            
        if self.proxy_type == ProxyType.WEBSHARE_RESIDENTIAL:
            proxy_url = f"http://{self.webshare_username}:{self.webshare_password}@{self.webshare_proxy_host}:{self.webshare_proxy_port}"
            return {
                'http': proxy_url,
                'https': proxy_url
            }
            
        return None
        
    def get_playwright_proxy(self):
        """
        Get proxy configuration for Playwright.
        
        Returns:
            dict: Proxy configuration for Playwright, or None if no proxy should be used
        """
        if self.proxy_type == ProxyType.NONE:
            return None
            
        if self.proxy_type == ProxyType.WEBSHARE_RESIDENTIAL:
            return {
                "server": f"http://{self.webshare_proxy_host}:{self.webshare_proxy_port}",
                "username": self.webshare_username,
                "password": self.webshare_password
            }
            
        return None
        
    def test_connection(self, test_url="https://httpbin.org/ip"):
        """
        Test if the proxy is working by making a request.
        
        Args:
            test_url: URL to test the connection with
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.proxy_type == ProxyType.NONE:
            return True
            
        try:
            proxies = self.get_request_proxies()
            response = requests.get(test_url, proxies=proxies, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Proxy connection test failed: {str(e)}")
            return False
            
    def get_current_ip(self):
        """
        Get the current IP address used by the connection (with or without proxy).
        
        Returns:
            str: IP address or error message if retrieval failed
        """
        try:
            proxies = self.get_request_proxies()
            response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
            if response.status_code == 200:
                ip_data = response.json()
                return ip_data.get("origin", "Unknown")
            else:
                return f"Error: Status code {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
            
    @staticmethod
    def create_from_environment():
        """
        Create a proxy manager based on environment variables.
        
        Returns:
            ProxyManager: Configured proxy manager instance
        """
        load_dotenv()
        
        proxy_type_str = os.getenv("PROXY_TYPE", "NONE")
        
        try:
            if proxy_type_str == "WEBSHARE_RESIDENTIAL":
                proxy_type = ProxyType.WEBSHARE_RESIDENTIAL
            else:
                proxy_type = ProxyType.NONE
        except:
            proxy_type = ProxyType.NONE
            
        return ProxyManager(proxy_type)
