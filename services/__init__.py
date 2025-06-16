"""
Services initialization module for VroomSniffer Car Scraper.
This module provides access to all service classes.
"""

# Import all services for easy access
from services.storage_service import StorageService
from services.url_pool_service import UrlPoolService
from services.statistics_service import StatisticsService
from services.notification_service import NotificationService
from services.scraper_service import ScraperService
from services.scheduler_service import SchedulerService

# Export all classes
__all__ = [
    'StorageService',
    'UrlPoolService',
    'StatisticsService', 
    'NotificationService',
    'ScraperService',
    'SchedulerService'
]
