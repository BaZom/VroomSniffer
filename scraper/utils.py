"""
Anti-blocking and bandwidth optimization utilities for VroomSniffer scraper
"""

import random
import time
from typing import Dict, List, Tuple, Any
from playwright.sync_api import Page, BrowserContext, Route, Request

# Block ad/tracking domains AND images for maximum bandwidth savings
BLOCKED_RESOURCE_TYPES = ['image', 'font']  # Block images and fonts (CSS needed for functionality)
BLOCKED_URL_KEYWORDS = [
    # Google ads and analytics
    'doubleclick.net', 'googlesyndication', 'adservice.google', 'google-analytics', 'googletagmanager',
    'google.com/g/collect', 'sgtm-legacy', 'gtm=', 'tid=G-',
    # Social media tracking
    'facebook.net', 'facebook.com', 'connect.facebook.net',
    # Ad networks
    'ads.', 'tracking', 'pixel', 'adnxs.com', 'amazon-adsystem.com',
    'criteo.com', 'outbrain.com', 'taboola.com', 'adform.net', 'rubiconproject.com', 'pubmatic.com',
    'openx.net', 'bidswitch.net', 'mathtag.com', 'scorecardresearch.com', 'moatads.com', 'casalemedia.com',
    'adition.com', 'bidr.io', 'adscale.de', 'adspirit.de', 'adserver', 'adclick', 'banner', 'promo',
    # eBay Kleinanzeigen specific tracking and ads
    'trackjs.com', 'speedcurve.com', 'hotjar.com', 'cdn-cgi',
    'cloudflareinsights.com', 'cdn.jsdelivr.net/npm/hotjar', 'cdn.segment.com', 'cdn.optimizely.com',
    'cdn.mouseflow.com', 'cdn.amplitude.com', 'cdn.plausible.io', 'cdn.matomo.cloud', 'cdn.datadoghq.com',
    # eBay Kleinanzeigen ad-block detection and tracking scripts
    'adblock-detection', 'ads.obj', 'prebid', 'gdpr/api/consent',
    # Analytics and data collection
    'collect?v=2', 'server.sgtm', 'tracking/', 'analytics'
]


class ResourceBlocker:
    """Handles resource blocking for bandwidth optimization"""
    
    def __init__(self):
        self.resource_stats = {}
        self.blocked_count = 0
        self.allowed_count = 0
    
    def create_handler(self):
        """Create a request handler for Playwright route interception"""
        def handle_request(route: Route, request: Request):
            resource_type = request.resource_type
            url = request.url
            
            # Track resource statistics
            if resource_type not in self.resource_stats:
                self.resource_stats[resource_type] = {'total': 0, 'blocked': 0, 'examples': []}
            self.resource_stats[resource_type]['total'] += 1
            
            # Add examples of URLs for each resource type (max 3)
            if len(self.resource_stats[resource_type]['examples']) < 3:
                example_url = url[:80] + '...' if len(url) > 80 else url
                self.resource_stats[resource_type]['examples'].append(example_url)
            
            # Determine if resource should be blocked
            should_block = self._should_block_resource(resource_type, url)
            
            if should_block:
                self.resource_stats[resource_type]['blocked'] += 1
                self.blocked_count += 1
                route.abort()
            else:
                self.allowed_count += 1
                route.continue_()
        
        return handle_request
    
    def _should_block_resource(self, resource_type: str, url: str) -> bool:
        """Determine if a resource should be blocked"""
        # Block by resource type
        if resource_type in BLOCKED_RESOURCE_TYPES:
            return True
        
        # Block by URL keywords
        url_lower = url.lower()
        for keyword in BLOCKED_URL_KEYWORDS:
            if keyword in url_lower:
                return True
        
        return False
    
    def print_statistics(self):
        """Print detailed resource blocking statistics"""
        if not self.resource_stats:
            return
        
        print(f"[*] Total requests allowed: {self.allowed_count}")
        print(f"[*] Total requests blocked: {self.blocked_count}")
        
        print("\n📊 RESOURCE TYPE STATISTICS:")
        print("-" * 40)
        for resource_type, stats in self.resource_stats.items():
            blocked_pct = (stats['blocked'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   {resource_type.ljust(15)}: {stats['total']:3d} total, {stats['blocked']:3d} blocked ({blocked_pct:.1f}%)")
            for example in stats.get('examples', []):
                print(f"      Example: {example}")
        
        self._print_optimization_opportunities()
    
    def _print_optimization_opportunities(self):
        """Print bandwidth optimization opportunities"""
        print("\n💡 BANDWIDTH OPTIMIZATION OPPORTUNITIES:")
        print("-" * 40)
        high_count_types = [rt for rt, stats in self.resource_stats.items() 
                           if stats['total'] >= 5 and stats['blocked'] == 0]
        
        for resource_type in high_count_types:
            count = self.resource_stats[resource_type]['total']
            if resource_type in ['image', 'font', 'stylesheet', 'media']:
                print(f"   Consider blocking '{resource_type}' ({count} requests) for bandwidth savings")
            elif resource_type == 'script' and count > 20:
                print(f"   Consider selective blocking of '{resource_type}' ({count} requests) - check if ads/tracking")


class AntiDetection:
    """Handles anti-detection techniques"""
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Get a random user agent to avoid detection"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0"
        ]
        return random.choice(user_agents)
    
    @staticmethod
    def add_human_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add a random delay to appear more human-like"""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"[*] Waiting {delay:.1f}s before navigation...")
        time.sleep(delay)
    
    @staticmethod
    def setup_context(context: BrowserContext):
        """Configure browser context for anti-detection"""
        # Set realistic viewport
        context.set_viewport_size({"width": 1920, "height": 1080})


class PageNavigator:
    """Handles page navigation with error handling and fallbacks"""
    
    def __init__(self, page: Page):
        self.page = page
    
    def navigate_to_url(self, url: str, timeout: int = 40000) -> bool:
        """Navigate to URL with robust error handling"""
        print(f"[*] Navigating to marketplace search page: {url}")
        
        try:
            # Use 'domcontentloaded' first for faster initial load
            self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            print("[*] Page initial DOM loaded, waiting for content...")
            
            # Then wait for network to quiet down
            try:
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except Exception as wait_error:
                print(f"[!] Network idle wait timed out: {str(wait_error)}")
                print("[*] Continuing anyway as the page content may be usable...")
            
            return True
            
        except Exception as e:
            print(f"[!] Navigation error: {str(e)}")
            print("[*] Trying again with a longer timeout and relaxed conditions...")
            
            try:
                # Try again with a longer timeout and relaxed wait_until condition
                self.page.goto(url, wait_until="load", timeout=60000)
                return True
            except Exception as e2:
                print(f"[!] Second navigation attempt failed: {str(e2)}")
                return False
    
    def check_for_no_results(self) -> bool:
        """Check if the page shows 'no results' message"""
        no_results_selectors = [
            "text=Keine Anzeigen gefunden",
            "text=Es wurden keine Anzeigen gefunden", 
            ".messagebox--alert",
            ".search-results-error",
            "[data-testid='no-results']"
        ]
        
        for selector in no_results_selectors:
            try:
                if self.page.locator(selector).is_visible(timeout=2000):
                    print(f"[!] No results found for this search")
                    return True
            except:
                continue
        
        return False
    
    def debug_page_content(self):
        """Print debug information about the page content"""
        try:
            title = self.page.title()
            print(f"[DEBUG] Page title: {title}")
            
            # Check if we've been blocked or got a CAPTCHA
            if "captcha" in title.lower() or "blocked" in title.lower():
                print("[WARNING] Possible CAPTCHA or blocking detected")
                return
            
            # Check if page contains expected content
            content = self.page.content()
            if "Autos" in content and "von" in content:
                print("[DEBUG] Page contains car listings content")
                
                # Debug article elements
                all_article_elements = self.page.query_selector_all("article")
                print(f"[DEBUG] Found {len(all_article_elements)} article elements")
                
                # Sample first few articles
                for i, article in enumerate(all_article_elements[:3]):
                    try:
                        text = article.inner_text()[:100]
                        print(f"[DEBUG] Article {i+1}: {text}")
                    except:
                        print(f"[DEBUG] Article {i+1}: Could not get text")
                
                # Check for price elements
                price_elements = self.page.query_selector_all("*:has-text('€')")
                print(f"[DEBUG] Found {len(price_elements)} elements with €")
            else:
                print("[DEBUG] Page does not contain expected car listings content")
                
        except Exception as e:
            print(f"[DEBUG] Could not get page title: {str(e)}")


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
        except:
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
            except:
                continue
        
        if not listings:
            print("[!] No listings found with any selector - possibly no results for this search")
        
        return listings
