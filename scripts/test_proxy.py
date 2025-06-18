#!/usr/bin/env python3
"""
WebShare Proxy Test Script
-------------------------
This script tests your WebShare proxy configuration to ensure it's working correctly.
"""
import sys
import os
import json
import requests
from pathlib import Path

# Add the parent directory to the path so we can import project modules
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from proxy.manager import ProxyManager, ProxyType
from dotenv import load_dotenv

def test_proxy_connection(proxy_type_str="WEBSHARE_RESIDENTIAL"):
    """
    Test a proxy connection to verify configuration
    
    Args:
        proxy_type_str: Type of proxy to test (NONE or WEBSHARE_RESIDENTIAL)
    """
    # Load environment variables
    load_dotenv()
    
    try:
        # Create proxy manager
        proxy_type = ProxyType[proxy_type_str]
        proxy_manager = ProxyManager(proxy_type)
        
        print(f"[*] Testing proxy connection with type: {proxy_type.name}")
        print(f"[*] Using proxy server: {proxy_manager.webshare_proxy_host}:{proxy_manager.webshare_proxy_port}")
        
        # Test connection
        test_url = "https://httpbin.org/ip"
        proxies = proxy_manager.get_request_proxies()
        
        print(f"[*] Connecting to {test_url} via proxy...")
        
        # First check connection without proxy to get baseline
        try:
            direct_response = requests.get("https://httpbin.org/ip", timeout=10)
            direct_ip = direct_response.json().get("origin", "Unknown")
            print(f"[+] Your direct IP address is: {direct_ip}")
        except Exception as e:
            print(f"[!] Could not determine direct IP: {str(e)}")
            direct_ip = "Unknown"
            
        # Test with proxy
        try:
            if proxy_type == ProxyType.NONE:
                print("[!] No proxy selected. Using direct connection.")
                return True
                
            response = requests.get(test_url, proxies=proxies, timeout=10)
            if response.status_code == 200:
                proxy_ip = response.json().get("origin", "Unknown")
                print(f"[+] Connection successful!")
                print(f"[+] Your IP through the proxy is: {proxy_ip}")
                
                # Verify the IP is different
                if direct_ip != proxy_ip and direct_ip != "Unknown" and proxy_ip != "Unknown":
                    print("[+] Proxy is working correctly! Your IP was masked.")
                else:
                    print("[!] Warning: Proxy IP is the same as direct IP or could not be determined.")
                    
                return True
            else:
                print(f"[!] Connection failed with status code: {response.status_code}")
                print(f"[!] Response: {response.text}")
                return False
        except Exception as e:
            print(f"[!] Proxy connection test failed: {str(e)}")
            print("[!] Please check your proxy configuration in .env file")
            return False
    except Exception as e:
        print(f"[!] Error setting up proxy manager: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test WebShare proxy connection")
    parser.add_argument(
        "--proxy-type",
        type=str,
        choices=[pt.name for pt in ProxyType],
        default="WEBSHARE_RESIDENTIAL",
        help="Type of proxy to test"
    )
    args = parser.parse_args()
    
    result = test_proxy_connection(args.proxy_type)
    
    if result:
        print("\n[+] Proxy test completed successfully!")
    else:
        print("\n[!] Proxy test failed. Please check your configuration.")
