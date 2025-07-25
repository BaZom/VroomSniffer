#!/usr/bin/env python3
"""
File Structure Display Script
----------------------------
Shows the clean structure of the new separate tracking files.
"""

import json
from pathlib import Path

def show_file_structure():
    """Display the structure of both tracking files"""
    storage_dir = Path(__file__).parent.parent / "storage"
    
    print("=" * 60)
    print("📁 VROOMSNIFFER TRACKING FILE STRUCTURE")
    print("=" * 60)
    
    # Show IP Tracking file structure
    ip_file = storage_dir / "ip_tracking.json"
    if ip_file.exists():
        print("\n📊 IP_TRACKING.JSON - Clean IP/URL mapping")
        print("-" * 50)
        with open(ip_file) as f:
            data = json.load(f)
            
        print("Structure:")
        print("  ├── url_ip_mapping/")
        print("  │   ├── [URL1]/")
        print("  │   │   ├── ip: 'IP_ADDRESS'")
        print("  │   │   ├── first_used: 'timestamp'")
        print("  │   │   ├── last_used: 'timestamp'")
        print("  │   │   ├── is_proxy: true/false")
        print("  │   │   ├── use_count: number")
        print("  │   │   ├── success_count: number")
        print("  │   │   └── total_listings: number")
        print("  │   └── [URL2]/ ...")
        print("  └── last_updated: 'timestamp'")
        
        url_count = len(data.get('url_ip_mapping', {}))
        print(f"\n📈 Contains: {url_count} tracked URLs")
    
    # Show Detection Events file structure  
    events_file = storage_dir / "detection_events.json"
    if events_file.exists():
        print("\n🚨 DETECTION_EVENTS.JSON - All detection events")
        print("-" * 50)
        with open(events_file) as f:
            data = json.load(f)
            
        print("Structure:")
        print("  ├── detection_events/")
        print("  │   ├── [Event1]/")
        print("  │   │   ├── timestamp: 'when'")
        print("  │   │   ├── detection_type: 'warning|blocked|normal'")
        print("  │   │   ├── page_title: 'page title'")
        print("  │   │   ├── success: true/false")
        print("  │   │   ├── listings_found: number")
        print("  │   │   ├── url: 'which URL had the issue'")
        print("  │   │   ├── ip: 'which IP had the issue'")
        print("  │   │   └── is_proxy: true/false")
        print("  │   └── [Event2]/ ...")
        print("  └── last_updated: 'timestamp'")
        
        event_count = len(data.get('detection_events', []))
        print(f"\n🚨 Contains: {event_count} detection events")
    else:
        print("\n🚨 DETECTION_EVENTS.JSON - Not created yet")
        print("-" * 50)
        print("This file will be created when first detection event occurs")
        print("(warnings, blocks, captchas, etc.)")
    
    print("\n" + "=" * 60)
    print("✅ BENEFITS OF SEPARATE FILES:")
    print("   • ip_tracking.json: Clean IP/URL performance data")
    print("   • detection_events.json: Focused security monitoring")
    print("   • Easier to read and analyze")
    print("   • Better file organization")
    print("=" * 60)

if __name__ == "__main__":
    show_file_structure()
