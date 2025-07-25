"""
Listings finding utilities for VroomSniffer scraper
"""

from typing import List
from playwright.sync_api import Page


class ListingsFinder:
    """Handles finding listings on the page with multiple selector fallbacks"""
    
    def __init__(self, page: Page):
        self.page = page
    
    def find_listings(self) -> List:
        """Find listings using multiple selector strategies"""
        listings = []
        
        # Primary selector
        try:
            self.page.wait_for_selector(".aditem", timeout=15000)
            listings = self.page.query_selector_all(".aditem")
            if listings:
                print(f"[*] Found {len(listings)} listings")
                return listings
        except Exception:
            print(f"[!] No listings found with .aditem selector, trying alternatives...")
        
        # Alternative selectors
        alternative_selectors = [
            "[data-testid='result-item']",
            ".ad-listitem", 
            ".aditem-main",
            ".result-item"
        ]
        
        for selector in alternative_selectors:
            try:
                self.page.wait_for_selector(selector, timeout=10000)
                listings = self.page.query_selector_all(selector)
                if listings:
                    print(f"[*] Found {len(listings)} listings with selector: {selector}")
                    return listings
            except Exception:
                continue
        
        if not listings:
            print("[!] No listings found with any selector - possibly no results for this search")
        
        return listings
