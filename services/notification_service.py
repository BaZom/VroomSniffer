"""
NotificationService - Handles sending notifications about listings.
Responsible for sending listings via Telegram and managing notification formats.
"""
import time
from notifier.telegram import send_telegram_message, format_car_listing_message

class NotificationService:
    """Service for sending notifications about listings"""
    
    def __init__(self, telegram_send=None, telegram_format=None):
        """
        Initialize with optional Telegram dependencies
        
        Args:
            telegram_send: Function to send Telegram message
            telegram_format: Function to format car listing message
        """
        if telegram_send and telegram_format:
            self.send_telegram_message = telegram_send
            self.format_car_listing_message = telegram_format
        else:
            # Default to standard Telegram functions
            self.send_telegram_message = send_telegram_message
            self.format_car_listing_message = format_car_listing_message
    
    def manual_send_listings(self, listings, parse_mode="HTML", retry_on_network_error=True):
        """
        Send listings to Telegram, retrying once on network error
        
        Args:
            listings: List of listing dictionaries to send
            parse_mode: Telegram parse mode (default "HTML")
            retry_on_network_error: Whether to retry on network errors
            
        Returns:
            tuple: (success_count, failed_list)
        """
        success_count = 0
        failed = []
        
        # Process listings in batches to avoid rate limiting issues
        batch_size = 15  # Process 15 at a time
        delay_between_msgs = 3  # 3 seconds between messages
        longer_delay_between_batches = 10  # 10 seconds between batches
        
        total_listings = len(listings)
        
        for batch_start in range(0, total_listings, batch_size):
            batch_end = min(batch_start + batch_size, total_listings)
            batch = listings[batch_start:batch_end]
            
            # Process this batch
            for i, listing in enumerate(batch):
                formatted_msg = self.format_car_listing_message(listing)
                success, error = self.send_telegram_message(formatted_msg, parse_mode=parse_mode)
                
                # Retry once if network error
                if not success and error and ("ConnectionResetError" in error or "Connection aborted" in error) and retry_on_network_error:
                    time.sleep(2)
                    success, error = self.send_telegram_message(formatted_msg, parse_mode=parse_mode)
                
                if success:
                    success_count += 1
                else:
                    failed.append({
                        'index': batch_start + i + 1,
                        'title': listing.get('Title', 'Unknown'),
                        'error': error
                    })
                
                # Add delay between messages (except for the last one in the batch)
                if i < len(batch) - 1:
                    time.sleep(delay_between_msgs)
            
            # Add a longer pause between batches (except after the last batch)
            if batch_end < total_listings:
                print(f"[*] Processed {batch_end}/{total_listings} listings. Pausing to avoid rate limits...")
                time.sleep(longer_delay_between_batches)
        
        return success_count, failed
    
    def send_listing(self, listing):
        """
        Send a single listing via Telegram
        
        Args:
            listing: Dictionary with listing information
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        formatted_msg = self.format_car_listing_message(listing)
        success, _ = self.send_telegram_message(formatted_msg)
        return success
    
    def send_multiple_listings(self, listings, delay_seconds=1.5):
        """
        Send multiple listings via Telegram
        
        Args:
            listings: List of dictionaries with listing information
            delay_seconds: Delay between messages to avoid rate limiting
            
        Returns:
            int: Number of successfully sent messages
        """
        success_count = 0
        for i, listing in enumerate(listings):
            success = self.send_listing(listing)
            if success:
                success_count += 1
                
            # Add delay between messages, except for the last one
            if i < len(listings) - 1:
                time.sleep(delay_seconds)
                
        return success_count
    
    def send_summary_notification(self, listings, search_keyword="", max_preview=3):
        """
        Send a summary notification about listings
        
        Args:
            listings: List of dictionaries with listing information
            search_keyword: Optional search keyword used to filter the listings
            max_preview: Maximum number of listings to show in the preview (not used)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        # Create summary message
        if search_keyword:
            summary_msg = f"🔍 <b>Search Results for '{search_keyword}'</b>\n\n"
        else:
            summary_msg = f"🚗 <b>Latest Car Scraping Results</b>\n\n"
        
        summary_msg += f"📊 Found {len(listings)} listings\n"
        
        summary_msg += f"\n💡 Use CLI to explore: 'python cli/main.py list'"
        
        # Send the message
        success, _ = self.send_telegram_message(summary_msg)
        return success
