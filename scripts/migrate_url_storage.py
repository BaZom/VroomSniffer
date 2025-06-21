#!/usr/bin/env python3
"""
Migration Script for URL Storage Format
--------------------------------------
Converts the old URL storage format (simple list) to the new enhanced format
with metadata and statistics tracking.
"""
import json
import time
from pathlib import Path

def migrate_url_storage():
    """Migrate the URL storage from old format to new format with metadata"""
    # Path to the URL storage file
    storage_path = Path(__file__).parent.parent / "storage" / "saved_urls.json"
    
    if not storage_path.exists():
        print("[!] URL storage file not found. Nothing to migrate.")
        return
    
    # Load existing data
    with open(storage_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("[!] Error decoding JSON from storage file.")
            return
    
    # Check if migration is needed
    if 'url_data' in data:
        print("[*] URL storage already in new format. No migration needed.")
        return
    
    # Extract URLs
    urls = data.get('urls', [])
    if not urls:
        print("[!] No URLs found in storage file.")
        return
    
    # Create new data structure
    url_data = {}
    for url in urls:
        url_data[url] = {
            'description': '',
            'stats': {
                'run_count': 0,
                'total_listings': 0,
                'last_run': None
            }
        }
    
    # Create new storage data
    new_data = {
        'url_data': url_data,
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Create backup of original file
    backup_path = storage_path.with_suffix('.json.bak')
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] Created backup of original file at {backup_path}")
    except Exception as e:
        print(f"[!] Failed to create backup: {e}")
        return
    
    # Save new data
    try:
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"[+] Successfully migrated {len(urls)} URLs to new format.")
    except Exception as e:
        print(f"[!] Failed to save migrated data: {e}")
        return

if __name__ == "__main__":
    print("[*] Starting URL storage format migration...")
    migrate_url_storage()
    print("[*] Migration complete.")
