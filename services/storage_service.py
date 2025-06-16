"""
StorageService - Handles all cache and listing storage operations.
Responsible for loading, saving, and managing listings in storage files.
"""
import json
import re
from pathlib import Path

class StorageService:
    """Service for handling all storage operations"""
    
    def __init__(self, all_old_path=None, latest_new_path=None):
        """Initialize with configurable file paths"""
        self.all_old_path = all_old_path or str(Path(__file__).parent.parent / "storage" / "all_old_results.json")
        self.latest_new_path = latest_new_path or str(Path(__file__).parent.parent / "storage" / "latest_new_results.json")
    
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
