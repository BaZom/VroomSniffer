"""
VroomSniffer scraper utilities package

This package contains anti-detection, bandwidth optimization, and scraping utilities
organized into focused modules for better maintainability.
"""

# Import all constants
from .constants import (
    BLOCKED_RESOURCE_TYPES,
    ESSENTIAL_RESOURCES,
    BLOCKED_URL_KEYWORDS
)

# Import all utility classes
from .bandwidth_tracker import BandwidthTracker
from .resource_blocker import ResourceBlocker
from .anti_detection import AntiDetection
from .page_navigator import PageNavigator
from .listings_finder import ListingsFinder

# Make everything available at package level
__all__ = [
    # Constants
    'BLOCKED_RESOURCE_TYPES',
    'ESSENTIAL_RESOURCES', 
    'BLOCKED_URL_KEYWORDS',
    
    # Classes
    'BandwidthTracker',
    'ResourceBlocker',
    'AntiDetection',
    'PageNavigator',
    'ListingsFinder'
]
