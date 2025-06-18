"""
Services provider for the VroomSniffer application.
This module helps initialize and manage service instances consistently across the application.
"""
from services.storage_service import StorageService
from services.url_pool_service import UrlPoolService
from services.scraper_service import ScraperService
from services.notification_service import NotificationService
from services.scheduler_service import SchedulerService
from services.statistics_service import StatisticsService

# Singleton instances for services
_storage_service = None
_url_pool_service = None
_statistics_service = None
_notification_service = None
_scraper_service = None
_scheduler_service = None

def get_storage_service():
    """Get or create the storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service

def get_url_pool_service():
    """Get or create the URL pool service instance."""
    global _url_pool_service
    if _url_pool_service is None:
        _url_pool_service = UrlPoolService()
    return _url_pool_service

def get_statistics_service():
    """Get or create the statistics service instance."""
    global _statistics_service
    if _statistics_service is None:
        _statistics_service = StatisticsService(get_storage_service())
    return _statistics_service

def get_notification_service():
    """Get or create the notification service instance."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service

def get_scraper_service(use_proxy=False, proxy_type=None):
    """
    Get or create the scraper service instance.
    
    Args:
        use_proxy: Whether to use proxies for scraping
        proxy_type: Optional specific proxy type to use
        
    Returns:
        ScraperService: The scraper service instance
    """
    global _scraper_service
    if _scraper_service is None or use_proxy:  # Always create new instance when proxy settings change
        _scraper_service = ScraperService(
            get_storage_service(),
            get_url_pool_service(),
            use_proxy=use_proxy,
            proxy_type=proxy_type
        )
        
        # Log proxy information if using proxy
        if use_proxy and proxy_type:
            from proxy.manager import ProxyManager, ProxyType
            try:
                proxy_type_enum = ProxyType[proxy_type]
                proxy_manager = ProxyManager(proxy_type_enum)
                print(f"[*] Using proxy type: {proxy_type}")
                
                # Get and print direct IP first
                direct_manager = ProxyManager(ProxyType.NONE)
                direct_ip = direct_manager.get_current_ip()
                print(f"[*] Your direct IP address: {direct_ip}")
                
                # Get and print proxy IP
                proxy_ip = proxy_manager.get_current_ip()
                print(f"[*] Your IP through WebShare proxy: {proxy_ip}")
                
                # Verify proxy is working
                if proxy_ip == direct_ip:
                    print("[!] WARNING: Proxy IP is the same as direct IP. Proxy might not be working correctly.")
                elif "Error" in proxy_ip:
                    print("[!] WARNING: Could not confirm proxy IP. Proxy might not be working correctly.")
                else:
                    print("[+] Proxy confirmed working - your IP is masked.")
            except Exception as e:
                print(f"[!] Error checking proxy configuration: {str(e)}")
    
    return _scraper_service

def get_scheduler_service():
    """Get or create the scheduler service instance."""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service
