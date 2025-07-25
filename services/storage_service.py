"""
StorageService - Handles all cache and listing storage operations.
Responsible for loading, saving, and managing listings in storage files.
"""
import json
import re
from pathlib import Path
from datetime import datetime

class StorageService:
    """Service for handling all storage operations"""
    
    def __init__(self, all_old_path=None, latest_new_path=None):
        """Initialize with configurable file paths"""
        self.all_old_path = all_old_path or str(Path(__file__).parent.parent / "storage" / "all_old_results.json")
        self.latest_new_path = latest_new_path or str(Path(__file__).parent.parent / "storage" / "latest_new_results.json")
        self.ip_tracking_path = str(Path(__file__).parent.parent / "storage" / "ip_tracking.json")
        self.detection_events_path = str(Path(__file__).parent.parent / "storage" / "detection_events.json")
        self.bandwidth_tracking_path = str(Path(__file__).parent.parent / "storage" / "bandwidth_tracking.json")
    
    def load_cache(self, cache_path=None):
        """
        Load cached listings as URL-indexed dictionary
        
        Args:
            cache_path: Path to the cache file (uses self.all_old_path if not provided)
            
        Returns:
            dict: URL-indexed cache of listings
        """
        path = cache_path or self.all_old_path
        
        if Path(path).exists():
            try:
                # Check if file is empty first
                if Path(path).stat().st_size == 0:
                    return {}
                    
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Handle both old filter-based format and new URL-based format
                    if isinstance(data, dict) and data:
                        first_key = next(iter(data.keys()))
                        if first_key.startswith('http'):
                            return data  # Already URL-based
                        # Convert old format to URL-based
                        url_cache = {}
                        for filter_listings in data.values():
                            if isinstance(filter_listings, list):
                                for listing in filter_listings:
                                    if listing.get("URL"):
                                        url_cache[listing["URL"]] = listing
                        return url_cache
                    elif isinstance(data, list):
                        # Handle list format (legacy)
                        url_cache = {}
                        for listing in data:
                            if listing.get("URL"):
                                url_cache[listing["URL"]] = listing
                        return url_cache
                    return {}
            except (json.JSONDecodeError, Exception):
                # If file is corrupted or empty, return empty dict
                return {}
        return {}
    
    def save_cache(self, cache_dict, cache_path=None):
        """
        Save URL-indexed cache dictionary
        
        Args:
            cache_dict: Dictionary of URL-indexed listings
            cache_path: Path to save cache (uses self.all_old_path if not provided)
        """
        path = cache_path or self.all_old_path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache_dict, f, ensure_ascii=False, indent=2)
    
    def is_listing_cached(self, url, cache_path=None):
        """
        Check if a listing URL exists in cache
        
        Args:
            url: URL to check
            cache_path: Path to check in (uses self.all_old_path if not provided)
            
        Returns:
            bool: True if URL exists in cache
        """
        path = cache_path or self.all_old_path
        cache = self.load_cache(path)
        return url in cache
    
    def add_listing_to_cache(self, listing, cache_path=None):
        """
        Add a single listing to cache
        
        Args:
            listing: Listing dictionary to add
            cache_path: Path to add to (uses self.all_old_path if not provided)
            
        Returns:
            bool: True if successfully added
        """
        path = cache_path or self.all_old_path
        url = listing.get("URL")
        if not url:
            return False
        
        cache = self.load_cache(path)
        cache[url] = listing
        self.save_cache(cache, path)
        return True
    
    def remove_listing_from_cache(self, url, cache_path=None):
        """
        Remove a listing from cache by URL
        
        Args:
            url: URL to remove
            cache_path: Path to remove from (uses self.all_old_path if not provided)
            
        Returns:
            bool: True if successfully removed
        """
        path = cache_path or self.all_old_path
        cache = self.load_cache(path)
        if url in cache:
            del cache[url]
            self.save_cache(cache, path)
            return True
        return False
    
    def get_cached_listing(self, url, cache_path=None):
        """
        Get a specific listing from cache by URL
        
        Args:
            url: URL to retrieve
            cache_path: Path to retrieve from (uses self.all_old_path if not provided)
            
        Returns:
            dict: Listing data if found, None otherwise
        """
        path = cache_path or self.all_old_path
        cache = self.load_cache(path)
        return cache.get(url)
    
    def get_all_cached_listings(self, cache_path=None):
        """
        Get all cached listings as a list
        
        Args:
            cache_path: Path to retrieve from (uses self.all_old_path if not provided)
            
        Returns:
            list: All listings in cache
        """
        path = cache_path or self.all_old_path
        cache = self.load_cache(path)
        return list(cache.values())
    
    def clear_cache(self, cache_path=None):
        """
        Clear all cached listings
        
        Args:
            cache_path: Path to clear (uses self.all_old_path if not provided)
            
        Returns:
            bool: True if successfully cleared
        """
        path = cache_path or self.all_old_path
        self.save_cache({}, path)
        return True
    
    def get_cache_stats(self, cache_path=None):
        """
        Get cache statistics
        
        Args:
            cache_path: Path to get stats for (uses self.all_old_path if not provided)
            
        Returns:
            dict: Cache statistics
        """
        path = cache_path or self.all_old_path
        try:
            cache = self.load_cache(path)
            
            # Calculate file size if cache file exists
            file_size = 0
            if Path(path).exists():
                file_size = Path(path).stat().st_size
            
            return {
                "total_listings": len(cache),
                "urls": list(cache.keys()),
                "cache_size": file_size,
                "cache_size_mb": round(file_size / (1024 * 1024), 2) if file_size > 0 else 0
            }
        except Exception as e:
            # Return default stats if anything goes wrong
            return {
                "total_listings": 0,
                "urls": [],
                "cache_size": 0,
                "cache_size_mb": 0
            }
    
    def remove_listings_by_ids(self, listing_urls, cache_path=None):
        """
        Remove multiple listings from cache by their URLs
        
        Args:
            listing_urls: List of URLs to remove
            cache_path: Path to remove from (uses self.all_old_path if not provided)
            
        Returns:
            int: Number of listings removed
        """
        path = cache_path or self.all_old_path
        cache = self.load_cache(path)
        removed_count = 0
        
        for url in listing_urls:
            if url in cache:
                del cache[url]
                removed_count += 1
        
        self.save_cache(cache, path)
        return removed_count
    
    def clear_all_caches(self, root_dir=None):
        """
        Clear all cache files and remove old listings
        
        Args:
            root_dir: Root directory of the project (optional)
            
        Returns:
            dict: Summary of what was cleared
        """
        if root_dir is None:
            root_dir = Path(__file__).parent.parent
        else:
            root_dir = Path(root_dir)
        
        cleared_files = []
        errors = []
        
        # List of cache files to clear
        cache_files = [
            "storage/all_old_results.json",
            "storage/latest_new_results.json",
            "storage/latest_results.json"
        ]
        
        for cache_file in cache_files:
            file_path = root_dir / cache_file
            try:
                if file_path.exists():
                    # Clear the file by writing empty dict or list
                    if "latest_results.json" in cache_file:
                        # This is scraped results, write empty list
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump([], f, ensure_ascii=False, indent=2)
                    else:
                        # This is cache file, write empty dict
                        self.save_cache({}, str(file_path))
                    cleared_files.append(str(file_path))
            except Exception as e:
                errors.append(f"Error clearing {file_path}: {str(e)}")
        
        return {
            "cleared_files": cleared_files,
            "errors": errors,
            "total_cleared": len(cleared_files),
            "message": f"Successfully cleared {len(cleared_files)} cache files"
        }
    
    def get_listings_by_search_criteria(self, search_term=None, min_price=None, max_price=None, cache_path=None):
        """
        Search cached listings by criteria
        
        Args:
            search_term: Search in title/location (optional)
            min_price: Minimum price filter (optional) 
            max_price: Maximum price filter (optional)
            cache_path: Path to cache file (uses self.all_old_path if not provided)
            
        Returns:
            list: Filtered listings
        """
        path = cache_path or self.all_old_path
        cache = self.load_cache(path)
        listings = list(cache.values())
        
        if not listings:
            return []
        
        filtered = listings
        
        # Filter by search term
        if search_term:
            search_term = search_term.lower()
            filtered = [l for l in filtered if 
                       search_term in l.get("Title", "").lower() or 
                       search_term in l.get("Location", "").lower()]
        
        # Filter by price range
        if min_price is not None or max_price is not None:
            price_filtered = []
            for listing in filtered:
                price_str = listing.get("Price", "").replace(".", "").replace(",", "").replace("€", "").strip()
                match = re.search(r"\d+", price_str)
                if match:
                    price = int(match.group())
                    if min_price is not None and price < min_price:
                        continue
                    if max_price is not None and price > max_price:
                        continue
                    price_filtered.append(listing)
            filtered = price_filtered
        
        return filtered
    
    def track_ip_for_url(self, url, ip, is_proxy=False, ip_tracking_path=None):
        """
        Track IP address used for a specific URL
        
        Args:
            url: The URL being accessed
            ip: The IP address used to access the URL
            is_proxy: Whether this IP is a proxy IP (True) or direct IP (False)
            ip_tracking_path: Path to IP tracking file (optional)
            
        Returns:
            dict: Updated tracking data
        """
        path = ip_tracking_path or self.ip_tracking_path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data or create new structure
        try:
            if Path(path).exists():
                with open(path, "r", encoding="utf-8") as f:
                    tracking_data = json.load(f)
            else:
                tracking_data = {"url_ip_mapping": {}, "last_updated": ""}
        except json.JSONDecodeError:
            tracking_data = {"url_ip_mapping": {}, "last_updated": ""}
        
        # Ensure url_ip_mapping exists
        if "url_ip_mapping" not in tracking_data:
            tracking_data["url_ip_mapping"] = {}
        
        # Add or update the entry for this URL
        if url not in tracking_data["url_ip_mapping"]:
            tracking_data["url_ip_mapping"][url] = []
        
        # Add new IP entry with timestamp and proxy info
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if the same IP has been used before for this URL to avoid duplicates
        for entry in tracking_data["url_ip_mapping"][url]:
            if entry.get("ip") == ip and entry.get("is_proxy") == is_proxy:
                # Update the existing entry with new timestamp
                entry["last_used"] = timestamp
                entry["use_count"] = entry.get("use_count", 1) + 1
                break
        else:  # This else belongs to the for loop (executes if no break)
            # Add new IP entry
            tracking_data["url_ip_mapping"][url].append({
                "ip": ip,
                "first_used": timestamp,
                "last_used": timestamp,
                "is_proxy": is_proxy,
                "use_count": 1
            })
        
        # Update last updated timestamp
        tracking_data["last_updated"] = timestamp
        
        # Save updated data
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tracking_data, f, ensure_ascii=False, indent=2)
            
        return tracking_data
    
    def get_ip_history_for_url(self, url, ip_tracking_path=None):
        """
        Get IP history for a specific URL
        
        Args:
            url: The URL to get history for
            ip_tracking_path: Path to IP tracking file (optional)
            
        Returns:
            list: List of IP entries for the URL or empty list if not found
        """
        path = ip_tracking_path or self.ip_tracking_path
        
        try:
            if Path(path).exists():
                with open(path, "r", encoding="utf-8") as f:
                    tracking_data = json.load(f)
                    return tracking_data.get("url_ip_mapping", {}).get(url, [])
            return []
        except (json.JSONDecodeError, Exception):
            return []
    
    def get_all_ip_tracking_data(self, ip_tracking_path=None):
        """
        Get all IP tracking data
        
        Args:
            ip_tracking_path: Path to IP tracking file (optional)
            
        Returns:
            dict: Complete IP tracking data or empty structure if not found
        """
        path = ip_tracking_path or self.ip_tracking_path
        
        try:
            if Path(path).exists():
                with open(path, "r", encoding="utf-8") as f:
                    tracking_data = json.load(f)
                    return tracking_data
            return {"url_ip_mapping": {}, "last_updated": ""}
        except (json.JSONDecodeError, Exception):
            return {"url_ip_mapping": {}, "last_updated": ""}
    
    def track_bandwidth_for_url(self, url, bandwidth_kb, requests_allowed, requests_blocked, is_proxy=False):
        """
        Track bandwidth usage for a specific URL
        
        Args:
            url: The URL being accessed
            bandwidth_kb: Bandwidth used in KB
            requests_allowed: Number of requests allowed
            requests_blocked: Number of requests blocked
            is_proxy: Whether proxy was used
        """
        path = self.bandwidth_tracking_path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data or create new structure
        try:
            if Path(path).exists():
                with open(path, "r", encoding="utf-8") as f:
                    tracking_data = json.load(f)
            else:
                tracking_data = {"url_bandwidth_mapping": {}}
        except json.JSONDecodeError:
            tracking_data = {"url_bandwidth_mapping": {}}
        
        # Ensure url_bandwidth_mapping exists
        if "url_bandwidth_mapping" not in tracking_data:
            tracking_data["url_bandwidth_mapping"] = {}
        
        # Add or update the entry for this URL
        if url not in tracking_data["url_bandwidth_mapping"]:
            tracking_data["url_bandwidth_mapping"][url] = []
        
        # Add new bandwidth entry with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        efficiency = (requests_blocked / (requests_allowed + requests_blocked) * 100) if (requests_allowed + requests_blocked) > 0 else 0
        
        entry = {
            "timestamp": timestamp,
            "bandwidth_kb": bandwidth_kb,
            "requests_allowed": requests_allowed,
            "requests_blocked": requests_blocked,
            "efficiency_percent": round(efficiency, 1),
            "is_proxy": is_proxy
        }
        
        tracking_data["url_bandwidth_mapping"][url].append(entry)
        
        # Keep only last 10 entries per URL to avoid file bloat
        if len(tracking_data["url_bandwidth_mapping"][url]) > 10:
            tracking_data["url_bandwidth_mapping"][url] = tracking_data["url_bandwidth_mapping"][url][-10:]
        
        # Save updated data
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(tracking_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Warning: Could not save bandwidth tracking: {e}")
    
    def get_bandwidth_stats_for_url(self, url):
        """
        Get bandwidth statistics for a specific URL
        
        Args:
            url: The URL to get stats for
            
        Returns:
            dict: Bandwidth statistics or None if no data
        """
        path = self.bandwidth_tracking_path
        
        try:
            if Path(path).exists():
                with open(path, "r", encoding="utf-8") as f:
                    tracking_data = json.load(f)
                    
                url_data = tracking_data.get("url_bandwidth_mapping", {}).get(url, [])
                if url_data:
                    latest = url_data[-1]  # Get most recent entry
                    avg_bandwidth = sum(entry["bandwidth_kb"] for entry in url_data) / len(url_data)
                    avg_efficiency = sum(entry["efficiency_percent"] for entry in url_data) / len(url_data)
                    
                    return {
                        "latest_bandwidth_kb": latest["bandwidth_kb"],
                        "latest_efficiency": latest["efficiency_percent"],
                        "average_bandwidth_kb": round(avg_bandwidth, 2),
                        "average_efficiency": round(avg_efficiency, 1),
                        "total_scrapes": len(url_data),
                        "last_scraped": latest["timestamp"]
                    }
        except Exception:
            pass
        
        return None
    
    def track_detection_event(self, url, ip, is_proxy=False, detection_type=None, page_title=None, 
                            success=True, listings_found=0, response_time=None, trigger_indicator=None, ip_tracking_path=None):
        """
        Enhanced IP tracking with detection events stored in separate files
        
        Args:
            url: The URL being accessed
            ip: The IP address used (generic identifier like "WEBSHARE_RESIDENTIAL_PROXY")
            is_proxy: Whether this IP is a proxy IP
            detection_type: Type of detection ('captcha', 'blocked', 'normal', 'warning')
            page_title: Page title for detection analysis
            success: Whether scraping was successful
            listings_found: Number of listings found (0 could indicate blocking)
            response_time: Page load time in seconds
            trigger_indicator: Specific indicator that triggered the detection (e.g., 'title_contains:captcha')
            ip_tracking_path: Path to IP tracking file (optional)
        """
        # Handle IP tracking in ip_tracking.json (clean, no detection events)
        self._track_ip_mapping(url, ip, is_proxy, success, listings_found, ip_tracking_path)
        
        # Handle detection events in separate detection_events.json
        if detection_type and detection_type != 'normal':
            # Get real IP for detection events only
            real_ip = self._get_real_ip_for_detection_event(ip, is_proxy)
            self._track_detection_event_separate(url, real_ip, is_proxy, detection_type, page_title, 
                                               success, listings_found, response_time, trigger_indicator)
    
    def _track_ip_mapping(self, url, ip, is_proxy, success, listings_found, ip_tracking_path=None):
        """Track IP usage for URLs without detection events (clean file)"""
        path = ip_tracking_path or self.ip_tracking_path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        try:
            if Path(path).exists():
                with open(path, "r", encoding="utf-8") as f:
                    tracking_data = json.load(f)
            else:
                tracking_data = {"url_ip_mapping": {}, "last_updated": ""}
        except json.JSONDecodeError:
            tracking_data = {"url_ip_mapping": {}, "last_updated": ""}
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update URL-IP mapping
        if url not in tracking_data["url_ip_mapping"]:
            tracking_data["url_ip_mapping"][url] = []
        
        # Find or create IP entry
        ip_entry = None
        for entry in tracking_data["url_ip_mapping"][url]:
            if entry["ip"] == ip:
                ip_entry = entry
                break
        
        if ip_entry is None:
            ip_entry = {
                "ip": ip,
                "first_used": current_time,
                "last_used": current_time,
                "is_proxy": is_proxy,
                "use_count": 1,
                "success_count": 1 if success else 0,
                "total_listings": listings_found
            }
            tracking_data["url_ip_mapping"][url].append(ip_entry)
        else:
            ip_entry["last_used"] = current_time
            ip_entry["use_count"] += 1
            if success:
                ip_entry["success_count"] = ip_entry.get("success_count", 0) + 1
            ip_entry["total_listings"] = ip_entry.get("total_listings", 0) + listings_found
        
        # Update metadata
        tracking_data["last_updated"] = current_time
        
        # Save updated data
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tracking_data, f, ensure_ascii=False, indent=2)
    
    def _track_detection_event_separate(self, url, ip, is_proxy, detection_type, page_title, 
                                      success, listings_found, response_time, trigger_indicator=None):
        """Track detection events in separate file"""
        Path(self.detection_events_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing detection events
        try:
            if Path(self.detection_events_path).exists():
                with open(self.detection_events_path, "r", encoding="utf-8") as f:
                    events_data = json.load(f)
            else:
                events_data = {"detection_events": [], "last_updated": ""}
        except json.JSONDecodeError:
            events_data = {"detection_events": [], "last_updated": ""}
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create detection event
        detection_event = {
            "timestamp": current_time,
            "detection_type": detection_type,
            "page_title": page_title,
            "success": success,
            "listings_found": listings_found,
            "response_time": response_time,
            "url": url,
            "ip": ip,
            "is_proxy": is_proxy,
            "trigger_indicator": trigger_indicator
        }
        
        # Add to events list
        events_data["detection_events"].append(detection_event)
        
        # Keep only last 1000 events to prevent file bloat
        if len(events_data["detection_events"]) > 1000:
            events_data["detection_events"] = events_data["detection_events"][-1000:]
        
        # Update metadata
        events_data["last_updated"] = current_time
        
        # Save detection events
        with open(self.detection_events_path, "w", encoding="utf-8") as f:
            json.dump(events_data, f, ensure_ascii=False, indent=2)
    
    def _get_real_ip_for_detection_event(self, original_ip, is_proxy):
        """Get real IP address for detection events only"""
        try:
            print(f"[*] Getting real IP for detection event (was: {original_ip})...")
            
            # Import proxy manager to get real IP
            from proxy.manager import ProxyManager
            
            # Try to get real IP using proxy manager's method
            if is_proxy:
                # For proxy connections, create a proxy manager instance to get actual IP
                proxy_manager = ProxyManager.create_from_environment()
                if proxy_manager:
                    real_ip = proxy_manager.get_actual_ip()
                    if real_ip and real_ip != "Unknown":
                        print(f"[*] Real IP for detection event: {real_ip}")
                        return real_ip
            else:
                # For direct connections, use static method to get IP
                real_ip = ProxyManager.get_current_ip()
                if real_ip and real_ip != "Unknown":
                    print(f"[*] Real IP for detection event: {real_ip}")
                    return real_ip
            
            # Fallback to original identifier if real IP cannot be obtained
            print(f"[WARNING] Could not get real IP, using identifier: {original_ip}")
            return original_ip
            
        except Exception as e:
            print(f"[WARNING] Error getting real IP for detection event: {str(e)}")
            return original_ip
