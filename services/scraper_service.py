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
        # Track consecutive proxy failures for fallback logic
        self.consecutive_proxy_failures = 0
        self.max_proxy_failures = 3  # After 3 failures, switch to direct mode temporarily
    
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
            from proxy.manager import ProxyManager, ProxyType                # Create a proxy manager and get direct IP only
            try:
                # Get direct IP regardless of proxy settings - we'll get actual proxy IP after scraping
                try:
                    direct_response = requests.get("https://httpbin.org/ip", timeout=10)
                    direct_ip = direct_response.json().get("origin", "Unknown")
                    print(f"[IP INFO] Your direct IP: {direct_ip}")
                except Exception as e:
                    print(f"[IP INFO ERROR] Failed to get direct IP: {str(e)}")
                    direct_ip = "Unknown"
                
                # Log proxy usage intent but don't check proxy IP yet to avoid confusion
                if self.use_proxy and self.proxy_type == "WEBSHARE_RESIDENTIAL":
                    print(f"[IP INFO] Will use WebShare residential proxy for scraping")
            except Exception as e:
                print(f"[IP INFO ERROR] Failed to check IP information: {str(e)}")
            
            # Determine if we should use proxy for this attempt
            current_use_proxy = self.use_proxy
            current_proxy_type = self.proxy_type
            
            # If we've had too many consecutive proxy failures, temporarily use direct mode
            if self.consecutive_proxy_failures >= self.max_proxy_failures:
                if self.use_proxy:
                    print(f"[PROXY FALLBACK] Too many proxy failures ({self.consecutive_proxy_failures}) - temporarily using direct connection")
                current_use_proxy = False
                current_proxy_type = None
            
            args = [sys.executable, str(self.root_dir / "scraper" / "engine.py"), "--url", url]
            
            # Add proxy arguments if needed
            if current_use_proxy:
                args.append("--use-proxy")
                if current_proxy_type:
                    args.extend(["--proxy-type", current_proxy_type])
            
            result = subprocess.run(
                args,
                cwd=self.root_dir, capture_output=True, text=True
            )
            
            # Check for proxy failure when proxy was explicitly requested
            if result.returncode != 0:
                error_output = result.stderr or result.stdout
                print(f"[ERROR] Scraper failed with return code {result.returncode}")
                print(f"[ERROR OUTPUT] {error_output}")
                return []
            
            if result.returncode == 0:
                # Check if this was a proxy failure (empty results + proxy failure message)
                output_text = result.stdout
                if current_use_proxy and "❌ PROXY FAILURE:" in output_text:
                    self.consecutive_proxy_failures += 1
                    print(f"❌ PROXY FAILURE #{self.consecutive_proxy_failures}: Proxy not working for this URL")
                    
                    if self.consecutive_proxy_failures < self.max_proxy_failures:
                        print(f"[*] Will try next URL with proxy ({self.consecutive_proxy_failures}/{self.max_proxy_failures} failures)")
                    else:
                        print(f"[FALLBACK] Will switch to direct mode after {self.max_proxy_failures} failures")
                    return []  # Return empty to try next URL
                
                # Reset failure counter on successful scrape
                if self.consecutive_proxy_failures > 0:
                    print(f"[SUCCESS] Proxy working again - resetting failure counter")
                    self.consecutive_proxy_failures = 0
                
                json_path = self.root_dir / "storage" / "latest_results.json"
                if json_path.exists():
                    with open(json_path, "r", encoding="utf-8") as f:
                        listings_data = json.load(f)
                        if not listings_data:
                            print(f"[INFO] No listings found for search URL: {url}")
                else:
                    print(f"[WARNING] Scraper completed but no results file found")
                    listings_data = []
                
                # Extract the actual IP used and bandwidth info from the scraper output
                actual_ip = None
                is_proxy = False
                bandwidth_kb = None
                requests_allowed = None
                requests_blocked = None
                
                # Look for the actual IP, proxy status, and bandwidth info in the scraper's output
                output_lines = result.stdout.split("\n")
                for line in output_lines:
                    if "[*] Scraping completed using IP:" in line:
                        parts = line.split("using IP:")
                        if len(parts) > 1:
                            actual_ip = parts[1].strip()
                    elif "[*] Used proxy:" in line:
                        if "Yes" in line:
                            is_proxy = True
                    elif "📊 Data transferred:" in line:
                        # Extract bandwidth info: "📊 Data transferred: 68.36 KB (0.067 MB)"
                        try:
                            parts = line.split(":")
                            if len(parts) > 1:
                                bandwidth_part = parts[1].strip()
                                if "KB" in bandwidth_part:
                                    bandwidth_kb = float(bandwidth_part.split("KB")[0].strip())
                        except:
                            pass
                    elif "📈 Requests:" in line:
                        # Extract request info: "📈 Requests: 2 allowed, 56 blocked"
                        try:
                            parts = line.split(":")
                            if len(parts) > 1:
                                requests_part = parts[1].strip()
                                if "allowed" in requests_part and "blocked" in requests_part:
                                    allowed_part = requests_part.split("allowed")[0].strip()
                                    blocked_part = requests_part.split("blocked")[0].split(",")[-1].strip()
                                    requests_allowed = int(allowed_part)
                                    requests_blocked = int(blocked_part)
                        except:
                            pass
                
                # If we couldn't find the IP in output, use direct_ip as fallback
                if not actual_ip:
                    actual_ip = direct_ip
                    
                # Display bandwidth information if available
                if bandwidth_kb is not None:
                    print(f"[BANDWIDTH] Used {bandwidth_kb} KB for scraping")
                    if requests_allowed is not None and requests_blocked is not None:
                        total_requests = requests_allowed + requests_blocked
                        efficiency = (requests_blocked / total_requests * 100) if total_requests > 0 else 0
                        print(f"[BANDWIDTH] Efficiency: {requests_allowed} allowed, {requests_blocked} blocked ({efficiency:.1f}% blocked)")
                    
                # Clearly log the actual IP that was used
                print(f"[IP INFO] ACTUAL IP used for scraping: {actual_ip}{' (via proxy)' if is_proxy else ' (direct)'}")
                
                # Track this IP in storage with clear indication it's the ACTUAL scraping IP
                try:
                    self.storage_service.track_ip_for_url(url, actual_ip, is_proxy)
                    print(f"[IP TRACKING] Tracked {is_proxy and 'proxy' or 'direct'} IP {actual_ip} for URL: {url}")
                except Exception as e:
                    print(f"[IP TRACKING ERROR] Failed to track IP: {str(e)}")
                
                # Track bandwidth information if available
                if bandwidth_kb is not None and requests_allowed is not None and requests_blocked is not None:
                    try:
                        self.storage_service.track_bandwidth_for_url(url, bandwidth_kb, requests_allowed, requests_blocked, is_proxy)
                        print(f"[BANDWIDTH TRACKING] Saved bandwidth stats: {bandwidth_kb} KB, {requests_allowed} allowed, {requests_blocked} blocked")
                    except Exception as e:
                        print(f"[BANDWIDTH TRACKING ERROR] Failed to track bandwidth: {str(e)}")
                
                # We've already handled IP tracking in the code above, so we don't need to do anything here
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
        
        # Update progress with more detailed steps if callback provided
        if progress_callback:
            progress_callback("init", "Initializing scraper...", 0.1)
            
        # Run scraper to get fresh listings
        listings_data = self.run_scraper_and_load_results(filters, build_search_url_ui, self.root_dir)
        
        # Update progress if callback provided
        if progress_callback:
            progress_callback("parse", "Processing listings data", 0.7)
        
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
