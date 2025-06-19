"""
CLI Diagnostics - Utilities for displaying diagnostic information
"""
import json
from pathlib import Path
import argparse
from cli.utils import print_info, print_error, print_success, print_warning
from colorama import Fore, Style, Back

def display_ip_tracking():
    """Display IP tracking information from the IP tracking file"""
    ip_tracking_path = Path(__file__).parent.parent / "storage" / "ip_tracking.json"
    
    if not ip_tracking_path.exists():
        print_error("IP tracking file not found. No tracking data available.")
        return
    
    try:
        with open(ip_tracking_path, "r", encoding="utf-8") as f:
            tracking_data = json.load(f)
            
        if not tracking_data.get("url_ip_mapping"):
            print_info("No IP tracking data available yet.")
            return
        
        print(f"\n{Back.BLUE}{Fore.WHITE} ===== IP Tracking Information ===== {Style.RESET_ALL}")
        print(f"{Fore.CYAN}Last Updated:{Style.RESET_ALL} {tracking_data.get('last_updated', 'Unknown')}")
        print(f"{Fore.CYAN}URLs Tracked:{Style.RESET_ALL} {len(tracking_data.get('url_ip_mapping', {}))}")
        print(f"{Back.BLUE}{Fore.WHITE} ================================== {Style.RESET_ALL}\n")
        
        for url, ip_entries in tracking_data.get("url_ip_mapping", {}).items():
            print(f"\n{Fore.YELLOW}URL:{Style.RESET_ALL} {url}")
            print(f"{Fore.YELLOW}{'-' * 80}{Style.RESET_ALL}")
            
            direct_ips = [entry for entry in ip_entries if not entry.get("is_proxy")]
            proxy_ips = [entry for entry in ip_entries if entry.get("is_proxy")]
            
            if direct_ips:
                print(f"{Fore.GREEN}Direct IPs ({len(direct_ips)}):{Style.RESET_ALL}")
                for entry in direct_ips:
                    print(f"  {Fore.GREEN}•{Style.RESET_ALL} {entry.get('ip', 'Unknown')}")
                    print(f"    {Fore.CYAN}First used:{Style.RESET_ALL} {entry.get('first_used', 'Unknown')}")
                    print(f"    {Fore.CYAN}Last used:{Style.RESET_ALL} {entry.get('last_used', 'Unknown')}")
                    print(f"    {Fore.CYAN}Use count:{Style.RESET_ALL} {entry.get('use_count', 0)}")
            
            if proxy_ips:
                print(f"\n{Fore.MAGENTA}Proxy IPs ({len(proxy_ips)}):{Style.RESET_ALL}")
                for entry in proxy_ips:
                    print(f"  {Fore.MAGENTA}•{Style.RESET_ALL} {entry.get('ip', 'Unknown')}")
                    print(f"    {Fore.CYAN}First used:{Style.RESET_ALL} {entry.get('first_used', 'Unknown')}")
                    print(f"    {Fore.CYAN}Last used:{Style.RESET_ALL} {entry.get('last_used', 'Unknown')}")
                    print(f"    {Fore.CYAN}Use count:{Style.RESET_ALL} {entry.get('use_count', 0)}")
            
            print()
    
    except json.JSONDecodeError:
        print_error("IP tracking file is corrupted or empty.")
    except Exception as e:
        print_error(f"Failed to display IP tracking information: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="VroomSniffer Diagnostics Utilities")
    parser.add_argument("--show-ip-tracking", action="store_true", help="Display IP tracking information")
    
    args = parser.parse_args()
    
    if args.show_ip_tracking:
        display_ip_tracking()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
