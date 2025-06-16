"""
StatisticsService - Handles listing analysis and statistics.
Responsible for extracting prices, calculating statistics and providing search functionality.
"""
import re
import pandas as pd
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
        
    def calculate_statistics(self, listings):
        """
        Calculate basic statistics from a list of listings.
        
        Args:
            listings: List of car listing dictionaries
            
        Returns:
            Dictionary with statistics
        """
        # Extract prices
        prices = self.extract_prices(listings)
        
        # Calculate statistics
        total_count = len(listings)
        avg_price = sum(prices) / len(prices) if prices else 0
        median_price = sorted(prices)[len(prices)//2] if prices else 0
        
        return {
            'avg_price': avg_price,
            'median_price': median_price,
            'total_count': total_count,
            'prices': prices
        }
    
    def create_price_distribution_chart(self, prices, bins=20):
        """
        Create price distribution chart data.
        
        Args:
            prices: List of numeric prices
            bins: Number of bins for histogram
            
        Returns:
            DataFrame with price ranges and counts
        """
        df_prices = pd.DataFrame({"Price": prices})
        
        # Create bins for better visualization
        hist_data = pd.cut(df_prices["Price"], bins=bins, include_lowest=True)
        hist_counts = hist_data.value_counts().sort_index()
        
        # Convert to chart-friendly format
        chart_data = pd.DataFrame({
            'Price Range': [f"€{int(interval.left):,}-€{int(interval.right):,}" for interval in hist_counts.index],
            'Count': hist_counts.values
        })
        
        return chart_data
    
    def analyze_locations(self, listings):
        """
        Analyze location distribution in listings.
        
        Args:
            listings: List of car listing dictionaries
            
        Returns:
            Dictionary mapping locations to counts
        """
        locations = {}
        for listing in listings:
            location = listing.get("Location", "Unknown")
            locations[location] = locations.get(location, 0) + 1
        
        return locations
    
    def categorize_prices(self, prices):
        """
        Categorize prices into budget ranges.
        
        Args:
            prices: List of numeric prices
            
        Returns:
            Dictionary with counts by category
        """
        low_price = len([p for p in prices if p < 10000])
        mid_price = len([p for p in prices if 10000 <= p < 25000])
        high_price = len([p for p in prices if p >= 25000])
        
        return {
            'low': low_price,
            'mid': mid_price,
            'high': high_price
        }
