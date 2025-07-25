"""
Page navigation utilities with detection and error handling
"""

from typing import Dict, List
from playwright.sync_api import Page
from colorama import Fore, Style


class PageNavigator:
    """Handles page navigation with error handling and fallbacks"""
    
    def __init__(self, page: Page):
        self.page = page
    
    def navigate_to_url(self, url: str, timeout: int = 10000) -> bool:
        """Navigate to URL with robust error handling"""
        print(f"[*] Navigating to marketplace search page: {url}")
        
        try:
            # Use 'domcontentloaded' first for faster initial load
            self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            print("[*] Page initial DOM loaded, waiting for content...")
            
            # Then wait for network to quiet down (reduced timeout)
            try:
                self.page.wait_for_load_state("networkidle", timeout=8000)
            except Exception as wait_error:
                print(f"[!] Network idle wait timed out: {str(wait_error)}")
                print("[*] Continuing anyway as the page content may be usable...")
            
            return True
            
        except Exception as e:
            print(f"[!] Navigation error: {str(e)}")
            print("[*] Trying again with a longer timeout and relaxed conditions...")
            
            try:
                # Try again with shorter timeout for faster failure
                self.page.goto(url, wait_until="load", timeout=15000)
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
            except Exception:
                continue
        
        return False
    
    def debug_page_content(self):
        """Print debug information about the page content and return detection info"""
        detection_info = {
            'detection_type': 'normal',
            'page_title': '',
            'blocked': False,
            'trigger_indicator': None
        }
        
        try:
            title = self.page.title()
            url = self.page.url
            detection_info['page_title'] = title
            
            # Enhanced detection patterns
            blocking_indicators = [
                "captcha", "blocked", "bot", "robot", "verification", 
                "suspicious", "unusual traffic", "access denied",
                "cloudflare", "security check", "human verification"
            ]
            
            title_lower = title.lower()
            
            # Find specific blocking indicator in title
            found_indicator = None
            for indicator in blocking_indicators:
                if indicator in title_lower:
                    found_indicator = indicator
                    break
            
            if found_indicator:
                detection_info['detection_type'] = 'blocked'
                detection_info['blocked'] = True
                detection_info['trigger_indicator'] = f"title_contains:{found_indicator}"
                print(f"{Fore.RED}[DETECTION WARNING] Possible blocking detected:{Style.RESET_ALL}")
                print(f"  Page title: {title}")
                print(f"  Trigger: {found_indicator}")
                print(f"  URL: {url}")
                print(f"  🚨 Consider upgrading anti-detection measures!")
                return detection_info
            
            # Check page content for blocking indicators
            content = self.page.content()
            content_lower = content.lower()
            
            # Look for common blocking messages in content
            content_blocking_indicators = [
                "access to this page has been denied",
                "your request has been blocked",
                "unusual traffic from your computer",
                "prove you're not a robot",
                "security check",
                "cloudflare ray id"
            ]
            
            # Find specific content blocking indicator
            found_content_indicator = None
            for indicator in content_blocking_indicators:
                if indicator in content_lower:
                    found_content_indicator = indicator
                    break
            
            if found_content_indicator:
                detection_info['detection_type'] = 'content_blocked'
                detection_info['blocked'] = True
                detection_info['trigger_indicator'] = f"content_contains:{found_content_indicator}"
                print(f"{Fore.RED}[CONTENT BLOCKING] Blocking detected in page content{Style.RESET_ALL}")
                print(f"  Trigger: {found_content_indicator}")
                return detection_info
                
            # DYNAMIC CONTENT VALIDATION based on URL
            expected_content = self._extract_expected_content_from_url(url)
            missing_content = self._validate_expected_content(content, content_lower, title, expected_content)
            
            if not missing_content:
                # All expected content found
                detection_info['detection_type'] = 'normal'
            else:
                # Check if it's a genuine "no results" vs. blocking
                no_results_indicators = [
                    "keine ergebnisse", "no results", "0 ergebnisse",
                    "nothing found", "kein treffer"
                ]
                
                genuine_no_results = any(indicator in content_lower for indicator in no_results_indicators)
                
                if genuine_no_results:
                    # Find which no-results indicator was found
                    found_no_results = None
                    for indicator in no_results_indicators:
                        if indicator in content_lower:
                            found_no_results = indicator
                            break
                    detection_info['detection_type'] = 'no_results'
                    detection_info['trigger_indicator'] = f"no_results_contains:{found_no_results}"
                else:
                    detection_info['detection_type'] = 'warning'
                    detection_info['trigger_indicator'] = f"warning:{','.join(missing_content)}"
                    print(f"{Fore.YELLOW}[CONTENT WARNING] Page lacks expected content based on URL{Style.RESET_ALL}")
                    print(f"  This might indicate soft blocking or altered page structure")
                    print(f"  Page title: {title}")
                    print(f"  Expected but missing: {', '.join(missing_content)}")
                    print(f"  URL indicators: {expected_content}")
                
        except Exception as e:
            print(f"[WARNING] Could not analyze page content: {str(e)}")
            detection_info['detection_type'] = 'error'
            detection_info['trigger_indicator'] = f"error:{str(e)[:50]}"
        
        return detection_info

    def _extract_expected_content_from_url(self, url):
        """Extract expected content words from URL parameters and path"""
        expected = {
            'categories': [],
            'brands': [],
            'models': [],
            'filters': [],
            'seller_types': []
        }
        
        # Always expect "Autos" for car category URLs
        if "/s-autos/" in url:
            expected['categories'].append("Autos")
        
        # Extract seller type (anbieter)
        if "anbieter:privat" in url:
            expected['seller_types'].extend(["privat", "von privat"])
        elif "anbieter:haendler" in url:
            expected['seller_types'].extend(["Händler", "von Händler"])
        
        # Extract car brands from URL path
        url_parts = url.split('/')
        for part in url_parts:
            if part in ['bmw', 'mercedes', 'audi', 'volkswagen', 'vw', 'seat', 'kia', 'hyundai']:
                expected['brands'].append(part.upper() if part == 'bmw' else part.title())
        
        # Extract models from URL (after brand or in search terms)
        model_indicators = ['golf', 'x1', 'a3', 'a5', 'q3', '320', 'cla', 'arona', 'tucson', 'sportage', 'mercedes-a']
        for model in model_indicators:
            if model in url.lower():
                model_clean = model.replace('-', ' ').title()
                expected['models'].append(model_clean)
        
        # Extract price filters
        if "preis:" in url:
            expected['filters'].extend(["Preis", "€", "von", "bis"])
        
        # Extract transmission filter
        if "automatik" in url:
            expected['filters'].append("Automatik")
        
        # Extract fuel type filters
        if "benzin" in url:
            expected['filters'].append("Benzin")
        if "diesel" in url:
            expected['filters'].append("Diesel")
        if "hybrid" in url:
            expected['filters'].append("Hybrid")
            
        return expected
    
    def _validate_expected_content(self, content, content_lower, title, expected_content):
        """Validate that expected content from URL is present on the page"""
        missing_content = []
        
        # Check categories (most important)
        for category in expected_content['categories']:
            if category.lower() not in content_lower:
                missing_content.append(f"missing_{category}")
        
        # Check seller types (important for filter UI)
        seller_found = False
        for seller_type in expected_content['seller_types']:
            if seller_type.lower() in content_lower:
                seller_found = True
                break
        if expected_content['seller_types'] and not seller_found:
            missing_content.append("missing_seller_filter")
        
        # Check that basic filter words are present (indicates filter UI loaded)
        filter_words_found = 0
        for filter_word in expected_content['filters']:
            if filter_word.lower() in content_lower:
                filter_words_found += 1
        
        # If we expect filters but find none, that's suspicious
        if expected_content['filters'] and filter_words_found == 0:
            missing_content.append("missing_all_filters")
        elif expected_content['filters'] and filter_words_found < len(expected_content['filters']) * 0.3:
            missing_content.append("missing_most_filters")
        
        # Check brands (less critical - might not appear if no results)
        brand_found = False
        for brand in expected_content['brands']:
            if brand.lower() in content_lower or brand.lower() in title.lower():
                brand_found = True
                break
        # Only flag missing brand if we have other content (not a complete failure)
        if expected_content['brands'] and not brand_found and len(missing_content) == 0:
            missing_content.append("missing_brand_context")
        
        # Check basic page structure
        if title == "":
            missing_content.append("empty_title")
            
        return missing_content

    @staticmethod
    def analyze_url_for_expected_content(url):
        """
        Static method to analyze a URL and return what content should be expected.
        Useful for previewing detection logic for new URLs.
        """
        print(f"\n🔍 ANALYZING URL FOR EXPECTED CONTENT:")
        print(f"URL: {url}")
        
        # Use the static extraction logic directly
        expected = {
            'categories': [],
            'brands': [],
            'models': [],
            'filters': [],
            'seller_types': []
        }
        
        # Always expect "Autos" for car category URLs
        if "/s-autos/" in url:
            expected['categories'].append("Autos")
        
        # Extract seller type (anbieter)
        if "anbieter:privat" in url:
            expected['seller_types'].extend(["privat", "von privat"])
        elif "anbieter:haendler" in url:
            expected['seller_types'].extend(["Händler", "von Händler"])
        
        # Extract car brands from URL path
        url_parts = url.split('/')
        for part in url_parts:
            if part in ['bmw', 'mercedes', 'audi', 'volkswagen', 'vw', 'seat', 'kia', 'hyundai']:
                expected['brands'].append(part.upper() if part == 'bmw' else part.title())
        
        # Extract models from URL (after brand or in search terms)
        model_indicators = ['golf', 'x1', 'a3', 'a5', 'q3', '320', 'cla', 'arona', 'tucson', 'sportage', 'mercedes-a']
        for model in model_indicators:
            if model in url.lower():
                model_clean = model.replace('-', ' ').title()
                expected['models'].append(model_clean)
        
        # Extract price filters
        if "preis:" in url:
            expected['filters'].extend(["Preis", "€", "von", "bis"])
        
        # Extract transmission filter
        if "automatik" in url:
            expected['filters'].append("Automatik")
        
        # Extract fuel type filters
        if "benzin" in url:
            expected['filters'].append("Benzin")
        if "diesel" in url:
            expected['filters'].append("Diesel")
        if "hybrid" in url:
            expected['filters'].append("Hybrid")
        
        print(f"\n📋 EXPECTED CONTENT BREAKDOWN:")
        print(f"  🏷️  Categories: {expected['categories']}")
        print(f"  🚗 Brands: {expected['brands']}")  
        print(f"  📝 Models: {expected['models']}")
        print(f"  🔧 Filters: {expected['filters']}")
        print(f"  👤 Seller Types: {expected['seller_types']}")
        
        print(f"\n✅ PAGE SHOULD CONTAIN:")
        all_expected_words = []
        all_expected_words.extend(expected['categories'])
        all_expected_words.extend(expected['brands'])
        all_expected_words.extend(expected['models'])
        all_expected_words.extend(expected['filters'])
        all_expected_words.extend(expected['seller_types'])
        
        for word in set(all_expected_words):
            print(f"  • '{word}'")
            
        print(f"\n🚨 WILL TRIGGER WARNING IF MISSING:")
        print(f"  • Any category words (most critical)")
        print(f"  • Seller filter UI ('von privat', 'Händler')")
        print(f"  • Filter words if >70% missing")
        print(f"  • Empty page title")
        
        return expected
