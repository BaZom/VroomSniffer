#!/usr/bin/env python3
"""
IP Rotation Testing Script
--------------------------
Test script to verify that WebShare is actually rotating IP addresses.
"""

import sys
from pathlib import Path
import time

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from proxy.manager import ProxyManager, ProxyType
from colorama import Fore, Style, Back, init

# Initialize colorama
init(autoreset=True)


def test_ip_rotation(num_requests=5, delay_seconds=2):
    """
    Test IP rotation by making multiple requests and checking if different IPs are assigned.
    
    Args:
        num_requests: Number of requests to make
        delay_seconds: Delay between requests
    """
    print(f"\n{Back.BLUE}{Fore.WHITE} ===== IP Rotation Test ===== {Style.RESET_ALL}")
    
    # Test direct connection first
    print(f"\n{Fore.CYAN}Testing Direct Connection:{Style.RESET_ALL}")
    direct_manager = ProxyManager(ProxyType.NONE)
    direct_ip = direct_manager.get_actual_ip()
    print(f"Direct IP: {Fore.GREEN}{direct_ip}{Style.RESET_ALL}")
    
    # Test WebShare proxy rotation
    print(f"\n{Fore.CYAN}Testing WebShare Proxy Rotation:{Style.RESET_ALL}")
    proxy_manager = ProxyManager.create_from_environment()
    
    if proxy_manager.proxy_type != ProxyType.WEBSHARE_RESIDENTIAL:
        print(f"{Fore.RED}Error: PROXY_TYPE is not set to WEBSHARE_RESIDENTIAL in .env file{Style.RESET_ALL}")
        print(f"Current proxy type: {proxy_manager.proxy_type}")
        return
    
    if not proxy_manager.test_connection():
        print(f"{Fore.RED}Error: WebShare credentials not configured properly{Style.RESET_ALL}")
        return
    
    print(f"Making {num_requests} requests with {delay_seconds}s delay...")
    print(f"WebShare endpoint: {proxy_manager.webshare_proxy_host}:{proxy_manager.webshare_proxy_port}")
    
    ips_seen = []
    
    for i in range(num_requests):
        print(f"\n{Fore.YELLOW}Request #{i+1}:{Style.RESET_ALL}")
        
        # Get IP through WebShare proxy
        actual_ip = proxy_manager.get_actual_ip()
        ips_seen.append(actual_ip)
        
        print(f"  IP: {Fore.MAGENTA}{actual_ip}{Style.RESET_ALL}")
        
        # Check if this is a new IP
        if ips_seen.count(actual_ip) == 1:
            print(f"  {Fore.GREEN}✓ New IP{Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}⚠ Repeated IP (seen {ips_seen.count(actual_ip)} times){Style.RESET_ALL}")
        
        if i < num_requests - 1:  # Don't wait after the last request
            print(f"  Waiting {delay_seconds}s...")
            time.sleep(delay_seconds)
    
    # Summary
    unique_ips = list(set(ips_seen))
    print(f"\n{Back.GREEN}{Fore.WHITE} ===== Test Summary ===== {Style.RESET_ALL}")
    print(f"Total requests: {len(ips_seen)}")
    print(f"Unique IPs: {len(unique_ips)}")
    print(f"Rotation rate: {len(unique_ips)/len(ips_seen)*100:.1f}%")
    
    if len(unique_ips) == len(ips_seen):
        print(f"{Fore.GREEN}✓ Perfect rotation - every request used a different IP{Style.RESET_ALL}")
    elif len(unique_ips) > len(ips_seen) * 0.7:
        print(f"{Fore.YELLOW}⚠ Good rotation - most requests used different IPs{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}⚠ Poor rotation - many repeated IPs detected{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}IPs used:{Style.RESET_ALL}")
    for i, ip in enumerate(unique_ips, 1):
        count = ips_seen.count(ip)
        print(f"  {i}. {ip} (used {count} time{'s' if count > 1 else ''})")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test WebShare IP rotation")
    parser.add_argument("--requests", type=int, default=5, help="Number of requests to make (default: 5)")
    parser.add_argument("--delay", type=int, default=2, help="Delay between requests in seconds (default: 2)")
    
    args = parser.parse_args()
    
    test_ip_rotation(args.requests, args.delay)
