"""
SchedulerService - Handles scheduling of scraping jobs.
Responsible for managing intervals, scheduling, and t    def get_time_until_next_scrape(self):aping operations.
"""
import time
import random
from pathlib import Path

class SchedulerService:
    """Service for scheduling and managing scraper timing"""
    
    DEFAULT_INTERVAL = 60  # Default interval in seconds
    MIN_INTERVAL = 5       # Minimum allowed interval
    MAX_INTERVAL = 3600    # Maximum allowed interval (1 hour)
    
    def __init__(self):
        """Initialize with default values"""
        self.interval_seconds = self.DEFAULT_INTERVAL
        self.last_scrape_time = 0
        self.scraping_active = False
        self.next_url_index = 0
        self.next_url_selected = False
        self.total_runs = 0
        # New shuffled URL tracking for fair random selection
        self.shuffled_indices = []
        self.current_shuffle_position = 0
    
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
        
    def set_total_runs(self, runs):
        """
        Set the total number of scraper runs (for synchronization with UI)
        
        Args:
            runs: The new run count to set
            
        Returns:
            int: The updated run count
        """
        self.total_runs = runs
        return self.total_runs
        
    def get_next_scrape_time(self):
        """
        Calculate the timestamp of the next scheduled scrape
        
        Returns:
            float: Unix timestamp of the next scrape time
        """
        if not self.scraping_active:
            return 0
        
        return self.last_scrape_time + self.interval_seconds
    
    # Simplified method to support display in UI
    def get_max_runs(self):
        """
        For UI display compatibility - always returns None for unlimited runs
        """
        return None
        
    def get_time_until_next_scrape(self):
        """
        Check if the scraper has reached its maximum number of runs
        
        Returns:
            bool: True if max runs reached, False otherwise or if unlimited
        """
        if self.max_runs <= 0:  # 0 or negative means unlimited
            return False
        return self.total_runs >= self.max_runs
    
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
        
    def select_next_url_index(self, url_count, random_selection=True, current_run=None):
        """
        Select the next URL index to scrape with improved fair random selection
        
        Args:
            url_count: Number of URLs in the pool
            random_selection: Whether to select randomly (True) or sequentially (False)
            current_run: Current run number for sequential selection (used for cycling through URLs)
            
        Returns:
            int: The selected URL index
        """
        if url_count <= 0:
            self.next_url_index = 0
        elif url_count == 1:
            self.next_url_index = 0
        elif random_selection:
            # New approach: Fair random selection ensuring all URLs are used once before repeating
            if not self.shuffled_indices or self.current_shuffle_position >= len(self.shuffled_indices):
                # Create shuffled list of all URL indices
                self.shuffled_indices = list(range(url_count))
                random.shuffle(self.shuffled_indices)
                self.current_shuffle_position = 0
                print(f"[SHUFFLE] New randomized URL order: {[i+1 for i in self.shuffled_indices]}")
            
            # Pick next URL from shuffled list
            self.next_url_index = self.shuffled_indices[self.current_shuffle_position]
            self.current_shuffle_position += 1
            
            # Progress tracking
            progress = f"({self.current_shuffle_position}/{url_count})"
            remaining_in_round = url_count - self.current_shuffle_position
            print(f"[FAIR RANDOM] Selected URL index {self.next_url_index + 1} {progress} - {remaining_in_round} URLs left in this round")
            
        else:
            # Sequential selection based on run number
            if current_run is not None:
                self.next_url_index = current_run % url_count
            else:
                # Just increment by 1 and wrap around
                self.next_url_index = (self.next_url_index + 1) % url_count
                
        self.next_url_selected = True
        return self.next_url_index
    
    def get_next_url_index(self):
        """Get the index of the next URL to scrape"""
        return self.next_url_index
    
    def is_next_url_selected(self):
        """Check if the next URL has been selected"""
        return self.next_url_selected
