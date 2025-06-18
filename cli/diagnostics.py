"""
CLI Diagnostics - Utilities for displaying diagnostic information
"""
import json
from pathlib import Path
import argparse

def display_ip_tracking():
    """Display IP tracking information from the IP tracking file"""
    ip_tracking_path = Path(__file__).parent.parent / "storage" / "ip_tracking.json"
    
    if not ip_tracking_path.exists():
        print("[ERROR] IP tracking file not found. No tracking data available.")
        return
    
    try:
        with open(ip_tracking_path, "r", encoding="utf-8") as f:
            tracking_data = json.load(f)
            
        if not tracking_data.get("url_ip_mapping"):
            print("[INFO] No IP tracking data available yet.")
            return
        
        print("\n===== IP Tracking Information =====")
        print(f"Last Updated: {tracking_data.get('last_updated', 'Unknown')}")
        print(f"URLs Tracked: {len(tracking_data.get('url_ip_mapping', {}))}")
        print("==================================\n")
        
        for url, ip_entries in tracking_data.get("url_ip_mapping", {}).items():
            print(f"\nURL: {url}")
            print("-" * 80)
            
            direct_ips = [entry for entry in ip_entries if not entry.get("is_proxy")]
            proxy_ips = [entry for entry in ip_entries if entry.get("is_proxy")]
            
            if direct_ips:
                print("Direct IPs:")
                for entry in direct_ips:
                    print(f"  - {entry.get('ip', 'Unknown')}")
                    print(f"    First used: {entry.get('first_used', 'Unknown')}")
                    print(f"    Last used: {entry.get('last_used', 'Unknown')}")
                    print(f"    Use count: {entry.get('use_count', 0)}")
            
            if proxy_ips:
                print("\nProxy IPs:")
                for entry in proxy_ips:
                    print(f"  - {entry.get('ip', 'Unknown')}")
                    print(f"    First used: {entry.get('first_used', 'Unknown')}")
                    print(f"    Last used: {entry.get('last_used', 'Unknown')}")
                    print(f"    Use count: {entry.get('use_count', 0)}")
            
            print()
    
    except json.JSONDecodeError:
        print("[ERROR] IP tracking file is corrupted or empty.")
    except Exception as e:
        print(f"[ERROR] Failed to display IP tracking information: {str(e)}")

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
