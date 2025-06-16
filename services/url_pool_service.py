"""
UrlPoolService - Handles management of URL pools for scraping.
Responsible for saving, loading, adding and removing URLs from storage.
"""
import json
import time
from pathlib import Path

class UrlPoolService:
    """Service for managing URL pools for scraping"""
    
    def __init__(self, url_storage_path=None):
        """Initialize with configurable file path"""
        if url_storage_path:
            self.url_storage_path = url_storage_path
        else:
            self.url_storage_path = str(Path(__file__).parent.parent / "storage" / "saved_urls.json")
    
    def get_url_storage_path(self):
        """Get the path for URL storage file"""
        return self.url_storage_path
        
    def load_saved_urls(self):
        """
        Load saved URLs from storage
        
        Returns:
            list: Saved URLs or empty list if none found
        """
        try:
            url_file = Path(self.url_storage_path)
            if url_file.exists():
                with open(url_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('urls', [])
        except Exception as e:
            pass
        return []
    
    def save_urls_to_storage(self, urls):
        """
        Save URLs to storage file
        
        Args:
            urls: List of URLs to save
            
        Returns:
            bool: True if successfully saved
        """
        try:
            url_file = Path(self.url_storage_path)
            url_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'urls': urls,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(url_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            return False
    
    def add_url_to_storage(self, url):
        """
        Add a single URL to storage
        
        Args:
            url: URL to add
            
        Returns:
            bool: True if successfully added or already exists
        """
        saved_urls = self.load_saved_urls()
        if url not in saved_urls:
            saved_urls.append(url)
            return self.save_urls_to_storage(saved_urls)
        return True
    
    def remove_url_from_storage(self, url):
        """
        Remove a URL from storage
        
        Args:
            url: URL to remove
            
        Returns:
            bool: True if successfully removed or didn't exist
        """
        saved_urls = self.load_saved_urls()
        if url in saved_urls:
            saved_urls.remove(url)
            return self.save_urls_to_storage(saved_urls)
        return True
    
    def clear_url_storage(self):
        """
        Clear all URLs from storage
        
        Returns:
            bool: True if successfully cleared
        """
        try:
            return self.save_urls_to_storage([])
        except Exception:
            return False
            
    def build_search_url_from_custom(self, custom_url):
        """
        Validate and return custom URL only if it's a proper HTTP/HTTPS URL
        
        Args:
            custom_url: URL to validate
            
        Returns:
            str: Validated URL or empty string
        """
        if custom_url and custom_url.strip():
            url = custom_url.strip()
            # Basic URL validation
            if url.startswith(('http://', 'https://')) and '.' in url:
                return url
        return ""
    
    def select_url(self, index=None, random_selection=False):
        """
        Select a URL from the saved pool
        
        Args:
            index: Index of URL to select (for sequential selection)
            random_selection: Whether to select randomly
            
        Returns:
            str: Selected URL or empty string if none available
        """
        urls = self.load_saved_urls()
        if not urls:
            return ""
        
        if random_selection:
            import random
            random.seed()  # Re-seed for true randomness
            return random.choice(urls)
        
        # Sequential selection
        if index is None or index < 0 or index >= len(urls):
            index = 0
        return urls[index]
    
    def select_url_batch(self, batch_size=1, random_selection=False, start_index=0):
        """
        Select multiple URLs from the saved pool
        
        Args:
            batch_size: Number of URLs to select
            random_selection: Whether to select randomly
            start_index: Starting index for sequential selection
            
        Returns:
            list: Selected URLs
        """
        urls = self.load_saved_urls()
        if not urls or batch_size <= 0:
            return []
            
        if random_selection:
            import random
            random.seed()  # Re-seed for true randomness
            # Sample with replacement if batch size is larger than available URLs
            if batch_size >= len(urls):
                return urls
            else:
                return random.sample(urls, batch_size)
        
        # Sequential selection
        result = []
        index = start_index % len(urls) if urls else 0
        
        for _ in range(batch_size):
            result.append(urls[index])
            index = (index + 1) % len(urls)
            
        return result
