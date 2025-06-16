"""
SchedulerService - Handles scheduling of scraping jobs.
Responsible for managing intervals, scheduling, and timing of scraping operations.
"""
import time
from pathlib import Path

class SchedulerService:
    """Service for scheduling and managing scraper timing"""
    
    DEFAULT_INTERVAL = 60  # Default interval in seconds
    MIN_INTERVAL = 30      # Minimum allowed interval
    MAX_INTERVAL = 3600    # Maximum allowed interval (1 hour)
    
    def __init__(self):
        """Initialize with default values"""
        self.interval_seconds = self.DEFAULT_INTERVAL
        self.last_scrape_time = 0
        self.scraping_active = False
        self.next_url_index = 0
        self.next_url_selected = False
        self.total_runs = 0
    
    def set_interval(self, seconds):
        """
        Set the scraping interval in seconds
        
        Args:
            seconds: Interval in seconds (will be constrained to min/max values)
            
        Returns:
            int: The actual interval set (might be adjusted to fit constraints)
        """
        # Constrain to min/max values
        if seconds < self.MIN_INTERVAL:
            seconds = self.MIN_INTERVAL
        elif seconds > self.MAX_INTERVAL:
            seconds = self.MAX_INTERVAL
            
        self.interval_seconds = seconds
        return self.interval_seconds
    
    def get_interval(self):
        """Get the current interval in seconds"""
        return self.interval_seconds
    
    def is_time_to_scrape(self):
        """
        Check if it's time to perform another scrape
        
        Returns:
            bool: True if enough time has elapsed since the last scrape
        """
        if not self.scraping_active:
            return False
            
        elapsed = time.time() - self.last_scrape_time
        return elapsed >= self.interval_seconds
    
    def start_scraping(self):
        """
        Start the scraper
        
        Returns:
            bool: True if successfully started
        """
        self.scraping_active = True
        self.last_scrape_time = 0  # Force immediate first scrape
        self.next_url_selected = False
        return True
    
    def stop_scraping(self):
        """
        Stop the scraper
        
        Returns:
            bool: True if successfully stopped
        """
        self.scraping_active = False
        return True
    
    def is_scraping_active(self):
        """Check if scraping is currently active"""
        return self.scraping_active
    
    def record_scrape(self):
        """
        Record that a scrape has occurred
        
        Returns:
            int: The updated total run count
        """
        self.last_scrape_time = time.time()
        self.total_runs += 1
        return self.total_runs
    
    def get_total_runs(self):
        """Get the total number of scraper runs"""
        return self.total_runs
    
    def set_total_runs(self, count):
        """Set the total number of scraper runs (for loading from state)"""
        self.total_runs = count
        return self.total_runs
        
    def get_time_until_next_scrape(self):
        """
        Calculate time remaining until the next scrape
        
        Returns:
            float: Seconds until next scrape, or 0 if it's time to scrape now
        """
        if not self.scraping_active:
            return 0
            
        elapsed = time.time() - self.last_scrape_time
        remaining = self.interval_seconds - elapsed
        return max(0, remaining)
    
    def get_progress_percentage(self):
        """
        Calculate progress as percentage toward next scrape
        
        Returns:
            float: Progress from 0.0 to 1.0
        """
        if not self.scraping_active or self.interval_seconds == 0:
            return 0.0
            
        remaining = self.get_time_until_next_scrape()
        progress = 1.0 - (remaining / self.interval_seconds)
        return max(0.0, min(1.0, progress))  # Constrain between 0 and 1
    
    def select_next_url_index(self, url_count):
        """
        Select the next URL index to scrape
        
        Args:
            url_count: Number of URLs in the pool
            
        Returns:
            int: The selected URL index
        """
        import random
        
        if url_count <= 0:
            self.next_url_index = 0
        elif url_count == 1:
            self.next_url_index = 0
        else:
            # Pick a random URL, but avoid picking the same one twice in a row
            current = self.next_url_index
            self.next_url_index = random.randint(0, url_count - 1)
            
            # If we got the same index and there are multiple URLs, try once more
            if self.next_url_index == current and url_count > 1:
                self.next_url_index = random.randint(0, url_count - 1)
                
        self.next_url_selected = True
        return self.next_url_index
    
    def get_next_url_index(self):
        """Get the index of the next URL to scrape"""
        return self.next_url_index
    
    def is_next_url_selected(self):
        """Check if the next URL has been selected"""
        return self.next_url_selected
