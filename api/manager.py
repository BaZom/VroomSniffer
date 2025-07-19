"""
API Manager
-----------
Manages different API clients for various car marketplace platforms.
"""
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import logging

from api.mobile_de import MobileDeAPIClient

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported car marketplace platforms."""
    SCRAPER = "scraper"  # Traditional web scraping (eBay Kleinanzeigen, etc.)
    MOBILE_DE = "mobile.de"  # mobile.de API
    
    @classmethod
    def get_display_names(cls) -> Dict[str, str]:
        """Get human-readable display names for platforms."""
        return {
            cls.SCRAPER.value: "Web Scraping (eBay Kleinanzeigen, etc.)",
            cls.MOBILE_DE.value: "mobile.de API"
        }
    
    @classmethod
    def get_platform_choices(cls) -> List[str]:
        """Get list of platform values for CLI choices."""
        return [platform.value for platform in cls]


class APIManager:
    """
    Manages API clients for different car marketplace platforms.
    
    This class provides a unified interface for interacting with different
    marketplace APIs and the traditional web scraping approach.
    """
    
    def __init__(self):
        """Initialize the API manager."""
        self.clients: Dict[str, Any] = {}
        self.active_platform = Platform.SCRAPER.value  # Default to scraping
        
    def configure_mobile_de(self, username: str, password: str, base_url: str = None) -> bool:
        """
        Configure mobile.de API client.
        
        Args:
            username: mobile.de API username
            password: mobile.de API password
            base_url: Optional custom base URL
            
        Returns:
            bool: True if configuration successful, False otherwise
        """
        try:
            client = MobileDeAPIClient(
                username=username,
                password=password,
                base_url=base_url or "https://api.mobile.de"
            )
            
            # Test the connection
            success, message = client.test_connection()
            if success:
                self.clients[Platform.MOBILE_DE.value] = client
                logger.info("mobile.de API client configured successfully")
                return True
            else:
                logger.error(f"mobile.de API configuration failed: {message}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to configure mobile.de API: {str(e)}")
            return False
            
    def set_active_platform(self, platform: str) -> bool:
        """
        Set the active platform for data fetching.
        
        Args:
            platform: Platform identifier (e.g., 'scraper', 'mobile.de')
            
        Returns:
            bool: True if platform is available, False otherwise
        """
        if platform == Platform.SCRAPER.value:
            # Scraper is always available
            self.active_platform = platform
            logger.info(f"Active platform set to: {platform}")
            return True
            
        elif platform == Platform.MOBILE_DE.value:
            if platform in self.clients:
                self.active_platform = platform
                logger.info(f"Active platform set to: {platform}")
                return True
            else:
                logger.warning(f"Platform {platform} not configured")
                return False
                
        else:
            logger.error(f"Unknown platform: {platform}")
            return False
            
    def get_active_platform(self) -> str:
        """Get the currently active platform."""
        return self.active_platform
        
    def is_platform_available(self, platform: str) -> bool:
        """
        Check if a platform is available for use.
        
        Args:
            platform: Platform identifier
            
        Returns:
            bool: True if platform is available
        """
        if platform == Platform.SCRAPER.value:
            return True
        elif platform == Platform.MOBILE_DE.value:
            return platform in self.clients
        else:
            return False
            
    def get_available_platforms(self) -> List[str]:
        """
        Get list of available platforms.
        
        Returns:
            List of platform identifiers that are configured and ready to use
        """
        available = [Platform.SCRAPER.value]  # Scraper always available
        
        # Check API platforms
        if Platform.MOBILE_DE.value in self.clients:
            available.append(Platform.MOBILE_DE.value)
            
        return available
    
    def get_all_supported_platforms(self) -> List[str]:
        """
        Get all platforms that could potentially be supported.
        
        Returns:
            List[str]: List of all platform identifiers, regardless of configuration status
        """
        return [platform.value for platform in Platform]
    
    def get_api_platforms(self) -> List[str]:
        """
        Get only API-based platforms (excludes scraper).
        
        Returns:
            List[str]: List of API platform identifiers
        """
        return [platform.value for platform in Platform if platform != Platform.SCRAPER]
        
    def fetch_listings(self, search_urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch listings using the active platform.
        
        Args:
            search_urls: List of search URLs or parameters
            **kwargs: Additional arguments for the specific platform
            
        Returns:
            List of normalized car listings
        """
        if self.active_platform == Platform.SCRAPER.value:
            return self._fetch_via_scraper(search_urls, **kwargs)
            
        elif self.active_platform == Platform.MOBILE_DE.value:
            return self._fetch_via_mobile_de_api(search_urls, **kwargs)
            
        else:
            raise ValueError(f"Unknown active platform: {self.active_platform}")
            
    def _fetch_via_scraper(self, search_urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch listings using traditional web scraping.
        
        This method delegates to the existing scraper service.
        """
        # Import here to avoid circular imports
        from providers.services_provider import get_scraper_service
        
        scraper_service = get_scraper_service()
        
        # Extract scraper-specific kwargs
        use_proxy = kwargs.get('use_proxy', False)
        proxy_type = kwargs.get('proxy_type', 'NONE')
        
        # Configure scraper with proxy settings
        if use_proxy:
            scraper_service.configure_proxy(proxy_type)
            
        all_listings = []
        
        for url in search_urls:
            try:
                listings = scraper_service.scrape_url(url)
                all_listings.extend(listings)
                logger.info(f"Scraped {len(listings)} listings from {url}")
                
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {str(e)}")
                continue
                
        return all_listings
        
    def _fetch_via_mobile_de_api(self, search_urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch listings using mobile.de API.
        
        Args:
            search_urls: List of mobile.de search URLs to convert to API calls
            **kwargs: Additional API parameters
            
        Returns:
            List of normalized car listings
        """
        if Platform.MOBILE_DE.value not in self.clients:
            raise ValueError("mobile.de API client not configured")
            
        client = self.clients[Platform.MOBILE_DE.value]
        all_listings = []
        
        for search_url in search_urls:
            try:
                # Convert URL to API parameters
                api_params = client.convert_search_url_to_params(search_url)
                
                # Add any additional parameters
                api_params.update(kwargs.get('api_params', {}))
                
                # Make API request
                api_response = client.search_vehicles(api_params)
                
                # Normalize response
                listings = client.normalize_api_response(api_response)
                all_listings.extend(listings)
                
                logger.info(f"Fetched {len(listings)} listings via API for URL: {search_url}")
                
            except Exception as e:
                logger.error(f"Failed to fetch via API for {search_url}: {str(e)}")
                continue
                
        return all_listings
        
    def get_platform_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all platforms.
        
        Returns:
            Dict with platform status information
        """
        status = {}
        
        # Scraper status
        status[Platform.SCRAPER.value] = {
            'available': True,
            'configured': True,
            'type': 'Web Scraping',
            'description': 'Traditional web scraping for eBay Kleinanzeigen and other sites'
        }
        
        # mobile.de API status
        mobile_de_available = Platform.MOBILE_DE.value in self.clients
        status[Platform.MOBILE_DE.value] = {
            'available': mobile_de_available,
            'configured': mobile_de_available,
            'type': 'API',
            'description': 'Official mobile.de API for car listings'
        }
        
        return status
        
    def get_client(self, platform: str) -> Optional[Any]:
        """
        Get the client for a specific platform.
        
        Args:
            platform: Platform identifier
            
        Returns:
            Client instance or None if not available
        """
        return self.clients.get(platform)


# Global API manager instance
api_manager = APIManager()


def get_api_manager() -> APIManager:
    """Get the global API manager instance."""
    return api_manager
