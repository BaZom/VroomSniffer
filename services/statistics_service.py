"""
StatisticsService - Handles listing analysis and statistics.
Responsible for extracting prices, calculating statistics and providing search functionality.
"""
import re
from pathlib import Path

class StatisticsService:
    """Service for analyzing listings and generating statistics"""
    
    def __init__(self, storage_service=None):
        """
        Initialize with optional StorageService dependency
        
        Args:
            storage_service: Optional StorageService instance
        """
        if storage_service:
            self.storage_service = storage_service
        else:
            # Import here to avoid circular imports
            from services.storage_service import StorageService
            self.storage_service = StorageService()
    
    def extract_prices(self, listings):
        """
        Extract prices from listings for statistics
        
        Args:
            listings: List of listing dictionaries
            
        Returns:
            list: Extracted prices as integers
        """
        prices = []
        for item in listings:
            price_str = item.get("Price", "").replace(".", "").replace(",", "").replace("€", "").strip()
            match = re.search(r"\d+", price_str)
            if match:
                prices.append(int(match.group()))
        return prices
    
    def show_statistics(self, listings_data):
        """
        Calculate statistics for listings (average price, count, price list)
        
        Args:
            listings_data: List of listing dictionaries
            
        Returns:
            tuple: (avg_price, listings_count, price_list)
        """
        prices = self.extract_prices(listings_data)
        avg_price = int(sum(prices) / len(prices)) if prices else 0
        return avg_price, len(listings_data), prices
    
    def get_listings_by_search_criteria(self, search_term=None, min_price=None, max_price=None, cache_path=None):
        """
        Search cached listings by criteria (delegates to storage_service)
        
        Args:
            search_term: Search in title/location (optional)
            min_price: Minimum price filter (optional) 
            max_price: Maximum price filter (optional)
            cache_path: Path to cache file
            
        Returns:
            list: Filtered listings
        """
        return self.storage_service.get_listings_by_search_criteria(
            search_term=search_term,
            min_price=min_price,
            max_price=max_price,
            cache_path=cache_path
        )
