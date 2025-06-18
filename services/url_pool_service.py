"""
UrlPoolService - Handles management of URL pools for scraping.
Responsible for saving, loading, adding and removing URLs from storage.
"""
import json
import time
import random
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
        Load saved URLs from storage (backwards compatible)
        
        Returns:
            list: Saved URLs or empty list if none found
        """
        try:
            url_file = Path(self.url_storage_path)
            if url_file.exists():
                with open(url_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both old and new format
                    if 'urls' in data:
                        # Old format - simple list
                        return data.get('urls', [])
                    elif 'url_data' in data:
                        # New format - return just the URLs as a list
                        return list(data.get('url_data', {}).keys())
        except Exception as e:
            pass
        return []
    
    def _load_saved_url_data(self):
        """
        Load saved URL data with metadata from storage
        
        Returns:
            dict: URL data dictionary or empty dict if none found
        """
        try:
            url_file = Path(self.url_storage_path)
            if url_file.exists():
                with open(url_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'url_data' in data:
                        # New format
                        return data.get('url_data', {})
                    elif 'urls' in data:
                        # Legacy format - convert it
                        urls = data.get('urls', [])
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
                        return url_data
        except Exception as e:
            pass
        return {}
    
    def save_urls_to_storage(self, urls_data):
        """
        Save URLs to storage file
        
        Args:
            urls_data: List of URLs or dict of URL data to save
            
        Returns:
            bool: True if successfully saved
        """
        try:
            url_file = Path(self.url_storage_path)
            url_file.parent.mkdir(parents=True, exist_ok=True)
            
            # If the input is a simple list of URLs, convert to enhanced format
            if isinstance(urls_data, list):
                # Try to preserve existing metadata if available
                existing_url_data = self._load_saved_url_data()
                url_dict = {}
                
                for url in urls_data:
                    if url in existing_url_data:
                        url_dict[url] = existing_url_data[url]
                    else:
                        url_dict[url] = {
                            'description': '',
                            'stats': {
                                'run_count': 0,
                                'total_listings': 0,
                                'last_run': None
                            }
                        }
                
                # Final data structure
                data = {
                    'url_data': url_dict,
                    'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                # Input is already in the enhanced format
                data = {
                    'url_data': urls_data,
                    'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            with open(url_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            return False
    
    def add_url_to_storage(self, url, description=''):
        """
        Add a single URL to storage
        
        Args:
            url: URL to add
            description: Optional description for the URL
            
        Returns:
            bool: True if successfully added or already exists
        """
        url_data = self._load_saved_url_data()
        
        if url not in url_data:
            url_data[url] = {
                'description': description,
                'stats': {
                    'run_count': 0,
                    'total_listings': 0,
                    'last_run': None
                }
            }
            return self.save_urls_to_storage(url_data)
        elif description and not url_data[url].get('description'):
            # Update description if provided and current one is empty
            url_data[url]['description'] = description
            return self.save_urls_to_storage(url_data)
            
        return True  # Already exists
    
    def remove_url_from_storage(self, url):
        """
        Remove a URL from storage
        
        Args:
            url: URL to remove
            
        Returns:
            bool: True if successfully removed or didn't exist
        """
        try:
            url_data = self._load_saved_url_data()
            if url in url_data:
                del url_data[url]
                return self.save_urls_to_storage(url_data)
            return True  # URL didn't exist in storage
        except Exception as e:
            print(f"Error removing URL from storage: {e}")
            return False
    
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
    
    def get_url_data(self):
        """
        Get the complete URL data including metadata and statistics
        
        Returns:
            dict: Dictionary of URLs with their metadata and statistics
        """
        return self._load_saved_url_data()
    
    def update_url_description(self, url, description):
        """
        Update the description for a specific URL
        
        Args:
            url: The URL to update
            description: New description text
            
        Returns:
            bool: True if successful, False otherwise
        """
        url_data = self._load_saved_url_data()
        
        if url in url_data:
            url_data[url]['description'] = description
            return self.save_urls_to_storage(url_data)
        
        return False
    
    def update_url_stats(self, url, run_successful=False, listings_count=0):
        """
        Update statistics for a URL after it's been used in a scraper run
        
        Args:
            url: The URL that was scraped
            run_successful: Whether the scrape run was successful
            listings_count: Number of listings found
            
        Returns:
            bool: True if successful, False otherwise
        """
        url_data = self._load_saved_url_data()
        
        if url in url_data:
            # Create stats object if it doesn't exist
            if 'stats' not in url_data[url]:
                url_data[url]['stats'] = {
                    'run_count': 0,
                    'total_listings': 0,
                    'last_run': None
                }
                
            # Update statistics
            if run_successful:
                url_data[url]['stats']['run_count'] = url_data[url]['stats'].get('run_count', 0) + 1
                url_data[url]['stats']['total_listings'] = url_data[url]['stats'].get('total_listings', 0) + listings_count
                
            # Update last run timestamp
            url_data[url]['stats']['last_run'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            return self.save_urls_to_storage(url_data)
        
        return False
        
    def add_url_with_metadata(self, url, description=''):
        """
        Add a URL with description to the storage
        
        Args:
            url: URL to add
            description: Optional description for the URL
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not url.startswith(('http://', 'https://')):
            return False
            
        url_data = self._load_saved_url_data()
        
        if url not in url_data:
            url_data[url] = {
                'description': description,
                'stats': {
                    'run_count': 0,
                    'total_listings': 0,
                    'last_run': None
                }
            }
            
            return self.save_urls_to_storage(url_data)
            
        return False
