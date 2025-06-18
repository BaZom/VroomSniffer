"""
CLI Utilities Module
-------------------
Common utility functions for the VroomSniffer CLI.
"""
from typing import Dict, List, Optional, Any, Union, Callable
import json
from pathlib import Path
import sys
import time
from functools import wraps
from tqdm import tqdm

# Add the parent directory to the path so we can import from project modules
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import services
from providers.services_provider import (
    get_storage_service,
    get_notification_service,
    get_scraper_service,
    get_scheduler_service,
    get_url_pool_service,
    get_statistics_service
)

class CLIError(Exception):
    """Custom exception for CLI-specific errors."""
    pass


class Services:
    """Container for all service instances used by the CLI."""
    def __init__(self, use_proxy=False, proxy_type=None):
        self.storage_service = get_storage_service()
        self.notification_service = get_notification_service()
        self.scraper_service = get_scraper_service(use_proxy=use_proxy, proxy_type=proxy_type)
        self.scheduler_service = get_scheduler_service()
        self.url_pool_service = get_url_pool_service()
        self.statistics_service = get_statistics_service()
        
        # Cache common paths
        self._cached_paths = {}
        self.init_paths()
        
    def init_paths(self) -> None:
        """Initialize common file paths."""
        storage_dir = Path(self.storage_service.all_old_path).parent
        self._cached_paths = {
            "latest_results": str(storage_dir / "latest_results.json"),
            "all_old": self.storage_service.all_old_path,
            "latest_new": self.storage_service.latest_new_path,
            "saved_urls": str(project_root / "storage" / "saved_urls.json")
        }
    
    def get_path(self, key: str) -> str:
        """Get a path by key."""
        return self._cached_paths.get(key, "")


def get_services(use_proxy=False, proxy_type=None) -> Services:
    """
    Create and return a Services instance.
    
    Args:
        use_proxy: Whether to use proxies for scraping
        proxy_type: Optional specific proxy type to use
        
    Returns:
        Services: Configured Services instance
    """
    return Services(use_proxy=use_proxy, proxy_type=proxy_type)


def check_listings_exist(services: Services, file_path: Optional[str] = None) -> bool:
    """
    Check if listings exist and print error if not.
    
    Args:
        services: Services instance
        file_path: Path to file containing listings, defaults to all_old_path
        
    Returns:
        bool: True if listings exist, False otherwise
    """
    if file_path is None:
        file_path = services.get_path("all_old")
        
    listings = services.storage_service.get_all_cached_listings(file_path)
    if not listings:
        print("[!] No listings found. Run 'python cli/main.py run <url>' first.")
        return False
    return True


def load_saved_urls(services: Services) -> List[str]:
    """
    Load saved URLs from saved_urls.json
    
    Args:
        services: Services instance
        
    Returns:
        list: List of saved URLs, or empty list if none found
    """
    saved_urls_path = Path(services.get_path("saved_urls"))
    
    if not saved_urls_path.exists():
        print(f"[!] No saved URLs found at {saved_urls_path}")
        return []
    
    try:
        with open(saved_urls_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Extract URLs from url_data object instead of urls array
            url_data = data.get("url_data", {})
            urls = list(url_data.keys()) if url_data else []
            
            if not urls:
                print("[!] No URLs found in saved_urls.json")
                return []
                
            print(f"[*] Loaded {len(urls)} URLs from saved_urls.json")
            return urls
    except (json.JSONDecodeError, Exception) as e:
        print(f"[!] Error loading saved URLs: {str(e)}")
        return []


def with_tqdm(func: Callable) -> Callable:
    """
    Decorator to handle tqdm availability for progress bars.
    
    Args:
        func: Function to decorate
        
    Returns:
        Wrapped function that handles tqdm
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            kwargs['tqdm_module'] = tqdm
        except NameError:
            kwargs['tqdm_module'] = None
            print("[!] tqdm package not found. Install it for progress bars: pip install tqdm")
        return func(*args, **kwargs)
    return wrapper
