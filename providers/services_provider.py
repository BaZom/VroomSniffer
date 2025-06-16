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

def get_scraper_service():
    """Get or create the scraper service instance."""
    global _scraper_service
    if _scraper_service is None:
        _scraper_service = ScraperService(get_storage_service())
    return _scraper_service

def get_scheduler_service():
    """Get or create the scheduler service instance."""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service
