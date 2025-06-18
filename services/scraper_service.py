"""
ScraperService - Handles running the scraper and processing results.
Responsible for executing the scraper and managing its results.
"""
import sys
import json
import subprocess
from pathlib import Path
from services.storage_service import StorageService

class ScraperService:
    """Service for scraper execution and results handling"""
    
    def __init__(self, storage_service=None, url_pool_service=None, use_proxy=False, proxy_type=None):
        """
        Initialize with optional service dependencies
        
        Args:
            storage_service: Optional StorageService instance
            url_pool_service: Optional UrlPoolService instance
            use_proxy: Whether to use proxies for scraping
            proxy_type: Optional specific proxy type to use
        """
        if storage_service:
            self.storage_service = storage_service
        else:
            self.storage_service = StorageService()
            
        if url_pool_service:
            self.url_pool_service = url_pool_service
        else:
            # Import here to avoid circular imports
            from services.url_pool_service import UrlPoolService
            self.url_pool_service = UrlPoolService()
        
        self.root_dir = Path(__file__).parent.parent
        self.use_proxy = use_proxy
        self.proxy_type = proxy_type
    
    def run_scraper_and_load_results(self, filters, build_search_url_ui, root_dir=None):
        """
        Run the marketplace scraper engine as a subprocess with the given filters
        
        Args:
            filters: Dictionary containing search filters or custom_url
            build_search_url_ui: Function to build search URL from filters
            root_dir: Optional root directory path
            
        Returns:
            list: Scraped listings
        """
        if root_dir:
            self.root_dir = Path(root_dir)
            
        listings_data = []
        try:
            if filters and filters.get("custom_url"):
                url = filters["custom_url"]
                print(f"[DEBUG] Using custom URL: {url}")
            else:
                url = build_search_url_ui(filters)
                print(f"[DEBUG] Generated URL from filters: {url}")
                print(f"[DEBUG] Filters used: {filters}")
                
            # Check IP before scraping if using proxy
            direct_ip = "Unknown"
            proxy_ip = None
            proxy_manager = None
            proxy_type = None
            
            # Import necessary modules here to avoid circular imports
            import requests
            from proxy.manager import ProxyManager, ProxyType
                
            # Create a proxy manager and get IP
            try:
                # Get direct IP regardless of proxy settings
                try:
                    direct_response = requests.get("https://httpbin.org/ip", timeout=10)
                    direct_ip = direct_response.json().get("origin", "Unknown")
                    print(f"[IP INFO] Your direct IP: {direct_ip}")
                except Exception as e:
                    print(f"[IP INFO ERROR] Failed to get direct IP: {str(e)}")
                    direct_ip = "Unknown"
                
                # Handle proxy if enabled
                if self.use_proxy:
                    proxy_type = ProxyType.WEBSHARE_RESIDENTIAL if self.proxy_type == "WEBSHARE_RESIDENTIAL" else ProxyType.NONE
                    proxy_manager = ProxyManager(proxy_type)
                    
                    # Get proxy IP if using proxy
                    if proxy_type != ProxyType.NONE:
                        try:
                            proxy_ip = proxy_manager.get_current_ip()
                            print(f"[IP INFO] Scraping with WebShare IP: {proxy_ip}")
                            if proxy_ip == direct_ip:
                                print("[WARNING] Proxy IP is same as direct IP - proxy might not be working!")
                        except Exception as e:
                            print(f"[IP INFO ERROR] Failed to get proxy IP: {str(e)}")
                            proxy_ip = "Unknown"
            except Exception as e:
                print(f"[IP INFO ERROR] Failed to check IP information: {str(e)}")
            
            args = [sys.executable, str(self.root_dir / "scraper" / "engine.py"), "--url", url]
            
            # Add proxy arguments if needed
            if self.use_proxy:
                args.append("--use-proxy")
                if self.proxy_type:
                    args.extend(["--proxy-type", self.proxy_type])
            
            result = subprocess.run(
                args,
                cwd=self.root_dir, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                json_path = self.root_dir / "storage" / "latest_results.json"
                if json_path.exists():
                    with open(json_path, "r", encoding="utf-8") as f:
                        listings_data = json.load(f)
                        if not listings_data:
                            print(f"[INFO] No listings found for search URL: {url}")
                else:
                    print(f"[WARNING] Scraper completed but no results file found")
                    listings_data = []
                
                # Track the IP used for this URL
                active_ip = proxy_ip if proxy_ip and self.use_proxy and proxy_type != ProxyType.NONE else direct_ip
                is_proxy = proxy_ip is not None and self.use_proxy and proxy_type != ProxyType.NONE
                try:
                    self.storage_service.track_ip_for_url(url, active_ip, is_proxy)
                    print(f"[IP TRACKING] Tracked {'proxy' if is_proxy else 'direct'} IP {active_ip} for URL: {url}")
                except Exception as e:
                    print(f"[IP TRACKING ERROR] Failed to track IP: {str(e)}")
            else:
                print(f"[WARNING] Scraper failed: {result.stderr}")
                print(f"[WARNING] Search URL was: {url}")
                # Don't raise error, return empty list to continue with cached data
                listings_data = []
        except Exception as e:
            print(f"[WARNING] Scraping error: {str(e)}")
            print(f"[WARNING] Search URL was: {url if 'url' in locals() else 'Unknown'}")
            # Don't raise error, return empty list to continue with cached data
            listings_data = []
            
        return listings_data
    
    def get_listings_for_filter(self, filters, build_search_url_ui, all_old_path=None, latest_new_path=None, root_dir=None, progress_callback=None):
        """
        Get all listings and new listings by running the scraper and comparing with cached listings
        
        Args:
            filters: Dictionary containing search filters (or custom_url)
            build_search_url_ui: Function to build search URL from filters
            all_old_path: Optional override for all results path
            latest_new_path: Optional override for new results path
            root_dir: Optional root directory path
            progress_callback: Optional callback function for progress updates
                               callback(step, message, progress_value)
            
        Returns:
            tuple: (all_listings, new_listings)
        """
        # Use provided paths or default from storage service
        all_old_path = all_old_path or self.storage_service.all_old_path
        latest_new_path = latest_new_path or self.storage_service.latest_new_path
        
        if root_dir:
            self.root_dir = Path(root_dir)
        
        # Get the scraper URL
        scraper_url = ""
        if filters and filters.get("custom_url"):
            scraper_url = filters["custom_url"]
        else:
            scraper_url = build_search_url_ui(filters)
        
        # Update progress if callback provided
        if progress_callback:
            progress_callback("init", "Initializing scraper...", 0.3)
            
        # Run scraper to get fresh listings
        listings_data = self.run_scraper_and_load_results(filters, build_search_url_ui, self.root_dir)
        
        # Update progress if callback provided
        if progress_callback:
            progress_callback("scrape", "Data retrieved from source", 0.6)
        
        # Add source URL to each listing
        for listing in listings_data:
            listing["source_url"] = scraper_url
        
        # Load existing cached listings (URL-based)
        cached_listings = self.storage_service.load_cache(all_old_path)
        
        # Identify new listings by URL
        new_listings = []
        all_listings = []
        
        for listing in listings_data:
            url = listing.get("URL")
            if not url:
                continue  # Skip listings without URL
                
            if url not in cached_listings:
                # This is a new listing
                new_listings.append(listing)
                cached_listings[url] = listing
            
            all_listings.append(listing)
            
        # Update URL statistics if scraper URL is in our URL pool
        # Only count NEW listings, not all scraped listings
        if scraper_url:
            run_successful = len(listings_data) > 0
            self.url_pool_service.update_url_stats(
                scraper_url,
                run_successful=run_successful,
                listings_count=len(new_listings)  # Count only NEW listings
            )
        
        for listing in listings_data:
            url = listing.get("URL")
            if not url:
                continue  # Skip listings without URL
                
            if url not in cached_listings:
                # This is a new listing
                new_listings.append(listing)
                cached_listings[url] = listing
            
            all_listings.append(listing)
        
        # Save updated cache
        self.storage_service.save_cache(cached_listings, all_old_path)
        
        # Save new listings for this run
        new_listings_dict = {listing["URL"]: listing for listing in new_listings if listing.get("URL")}
        self.storage_service.save_cache(new_listings_dict, latest_new_path)
        
        # Final progress update if callback provided
        if progress_callback:
            progress_callback("complete", f"Found {len(all_listings)} listings ({len(new_listings)} new)", 1.0)
        
        return all_listings, new_listings
