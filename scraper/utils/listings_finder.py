"""
Listings finding utilities for VroomSniffer scraper
"""

from typing import List, Optional, Tuple
import concurrent.futures
from playwright.sync_api import Page


class ListingsFinder:
    """Handles finding listings on the page with multiple selector fallbacks"""
    
    def __init__(self, page: Page):
        self.page = page
    
    def find_listings(self) -> List:
        """Find listings using immediate DOM check first, then fast fallbacks"""
        selectors = [
            ".aditem",
            "[data-testid='result-item']",
            ".ad-listitem", 
            ".aditem-main",
            ".result-item"
        ]
        
        print("[*] Checking DOM immediately for listings...")
        
        # FIRST: Try immediate DOM check (no waiting) - this works for most pages
        for selector in selectors:
            elements = self.page.query_selector_all(selector)
            if elements:
                print(f"[*] Found {len(elements)} listings immediately with selector: {selector}")
                return elements
        
        print("[*] No immediate listings found, trying with short waits...")
        
        # SECOND: If nothing found immediately, try with very short waits
        short_timeout = 2000  # Reduced from 3000 to 2 seconds
        
        for selector in selectors:
            try:
                # Quick check with short timeout
                self.page.wait_for_selector(selector, timeout=short_timeout)
                elements = self.page.query_selector_all(selector)
                if elements:
                    print(f"[*] Found {len(elements)} listings with selector: {selector}")
                    return elements
            except Exception:
                # Failed quickly, try next selector
                continue
        
        # If we get here, no selector found any listings after ~10 seconds total (5 selectors × 2s each)
        print("[!] No listings found with any selector - possibly no results for this search")
        return []
