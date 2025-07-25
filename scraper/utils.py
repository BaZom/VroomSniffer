"""
Anti-blocking and bandwidth optimization utilities for VroomSniffer scraper
"""

import random
import time
from typing import Dict, List, Tuple, Any
from playwright.sync_api import Page, BrowserContext, Route, Request
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# ULTRA-AGGRESSIVE blocking for maximum bandwidth savings (target: minimal KB)
BLOCKED_RESOURCE_TYPES = [
    'stylesheet',   # Block ALL CSS files (the 440 KB CSS file must be blocked!)
    'image',        # Block all images (biggest bandwidth saver)
    'font',         # Block fonts 
    'media',        # Block video/audio files
    'script',       # Block ALL JavaScript
    'websocket',    # Block websocket connections
    'eventsource',  # Block server-sent events
    'texttrack',    # Block subtitle tracks
    'manifest',     # Block web app manifests
    'other',        # Block miscellaneous resources
]

# Essential CSS to ALLOW (minimal whitelist) - BLOCK ALL CSS for maximum bandwidth savings
ESSENTIAL_RESOURCES = [
    # Block ALL CSS - we only need HTML content for scraping
    # 'marketplace.com/static/css/all.css',  # DISABLED - typically large files
]

# ULTRA-AGGRESSIVE URL blocking 
BLOCKED_URL_KEYWORDS = [
    # Google ads and analytics (AGGRESSIVE BLOCKING)
    'doubleclick.net', 'googlesyndication', 'adservice.google', 'google-analytics', 'googletagmanager',
    'google.com/g/collect', 'sgtm-legacy', 'gtm=', 'tid=G-', 'googleadservices.com', 'googletag',
    # Social media tracking
    'facebook.net', 'facebook.com', 'connect.facebook.net', 'twitter.com', 'instagram.com',
    # Ad networks (EXTENSIVE BLOCKING)
    'ads.', 'tracking', 'pixel', 'adnxs.com', 'amazon-adsystem.com', 'adsystem.amazon',
    'criteo.com', 'outbrain.com', 'taboola.com', 'adform.net', 'rubiconproject.com', 'pubmatic.com',
    'openx.net', 'bidswitch.net', 'mathtag.com', 'scorecardresearch.com', 'moatads.com', 'casalemedia.com',
    'adition.com', 'bidr.io', 'adscale.de', 'adspirit.de', 'adserver', 'adclick', 'banner', 'promo',
    # Common marketplace tracking and ads (ENHANCED)
    'trackjs.com', 'speedcurve.com', 'hotjar.com', 'cdn-cgi', 'mouseflow', 'amplitude',
    'cloudflareinsights.com', 'cdn.jsdelivr.net/npm/hotjar', 'cdn.segment.com', 'cdn.optimizely.com',
    'cdn.mouseflow.com', 'cdn.amplitude.com', 'cdn.plausible.io', 'cdn.matomo.cloud', 'cdn.datadoghq.com',
    # Common ad-block detection and tracking scripts
    'adblock-detection', 'ads.obj', 'prebid', 'gdpr/api/consent', 'liberty-js', 'liberty-experimental',
    # Analytics and data collection (EXTENSIVE)
    'collect?v=2', 'server.sgtm', 'tracking/', 'analytics', 'telemetry', 'metrics',
    # Video/Media (BANDWIDTH HEAVY)
    'youtube.com/embed', 'vimeo.com', 'youtu.be', 'video', 'mp4', 'webm', 'avi',
    # CDN assets that aren't essential (AGGRESSIVE)
    'cdnjs.cloudflare.com', 'unpkg.com', 'jsdelivr.net', 'bootstrapcdn.com',
    # Chat/Support widgets (NON-ESSENTIAL)
    'chat', 'support', 'intercom', 'zendesk', 'freshchat', 'tawk.to',
    # Marketing/Analytics tools (AGGRESSIVE BLOCKING)
    'segment.com', 'mixpanel.com', 'heap.com', 'fullstory.com', 'logrocket.com',
]


class BandwidthTracker:
    """Track actual bandwidth usage during scraping"""
    
    def __init__(self):
        self.total_bytes = 0
        self.request_count = 0
        self.blocked_count = 0
        self.request_details = []
        
    def record_allowed_request(self, resource_type: str, url: str, actual_size: int = None):
        """Record an allowed request with actual measured bandwidth"""
        if actual_size is not None:
            # Use actual measured size
            size_bytes = actual_size
        else:
            # No fallback estimates needed - we measure everything via response listener  
            # This will be updated with real size when response arrives
            size_bytes = 0  # Placeholder, will be updated with actual size
            
        self.total_bytes += size_bytes
        self.request_count += 1
        
        # Store details for debugging and size updates
        self.request_details.append({
            'type': resource_type,
            'size': size_bytes,
            'url': url,  # Store full URL for accurate matching
            'display_url': url[:50] + '...' if len(url) > 50 else url,
            'measured': actual_size is not None
        })
        
    def record_blocked_request(self):
        """Record a blocked request"""
        self.blocked_count += 1
        
    def get_bandwidth_summary(self) -> dict:
        """Get bandwidth usage summary"""
        total_kb = round(self.total_bytes / 1024, 2)
        total_mb = round(self.total_bytes / (1024 * 1024), 3)
        
        return {
            'total_bytes': self.total_bytes,
            'total_kb': total_kb,
            'total_mb': total_mb,
            'requests_allowed': self.request_count,
            'requests_blocked': self.blocked_count
        }
        
    def print_bandwidth_report(self):
        """Print a clean bandwidth usage report"""
        summary = self.get_bandwidth_summary()
        total_requests = summary['requests_allowed'] + summary['requests_blocked']
        
        if total_requests > 0:
            blocked_percentage = (summary['requests_blocked'] / total_requests) * 100
        else:
            blocked_percentage = 0
            
        print(f"\n💰 BANDWIDTH USAGE SUMMARY:")
        print(f"   📊 Data transferred: {summary['total_kb']} KB ({summary['total_mb']} MB)")
        print(f"   📈 Requests: {summary['requests_allowed']} allowed, {summary['requests_blocked']} blocked")
        print(f"   ⚡ Efficiency: {blocked_percentage:.1f}% of requests blocked")
        
        # Show breakdown of request details
        if self.request_details:
            print(f"\n📋 Request Details:")
            for detail in self.request_details:
                size_display = f"{detail['size']} bytes" if detail['size'] > 0 else "measuring..."
                display_url = detail.get('display_url', detail['url'][:50] + '...' if len(detail['url']) > 50 else detail['url'])
                print(f"   {detail['type']}: {size_display} - {display_url}")
    
    def update_request_size(self, url: str, actual_size: int):
        """Update a previously recorded request with actual measured size"""
        try:
            # Find the most recent request detail that matches this URL (handle redirects)
            for detail in reversed(self.request_details):  # Check from most recent
                if detail['url'] == url:  # Exact match first
                    self._update_detail_size(detail, actual_size)
                    break
                # Handle redirects: check if this could be a redirect from the recorded URL
                elif self._is_likely_redirect(detail['url'], url):
                    self._update_detail_size(detail, actual_size)
                    break
        except Exception:
            # Silently handle errors
            pass
    
    def _update_detail_size(self, detail: dict, actual_size: int):
        """Helper to update a request detail with new size"""
        old_size = detail['size']
        detail['size'] = actual_size
        detail['measured'] = True
        
        # Update total bytes
        self.total_bytes = self.total_bytes - old_size + actual_size
        
    def _is_likely_redirect(self, original_url: str, response_url: str) -> bool:
        """Check if response_url is likely a redirect from original_url"""
        try:
            # Handle common redirect patterns
            # Example: 'example-marketplace.com' to 'marketplace.com'
            from urllib.parse import urlparse
            orig_domain = urlparse(original_url).netloc.lower()
            resp_domain = urlparse(response_url).netloc.lower()
            
            # Check if it's a subdomain to main domain redirect
            if orig_domain != resp_domain:
                # Extract root domain for comparison
                orig_parts = orig_domain.split('.')
                resp_parts = resp_domain.split('.')
                if len(orig_parts) >= 2 and len(resp_parts) >= 2:
                    orig_root = '.'.join(orig_parts[-2:])
                    resp_root = '.'.join(resp_parts[-2:])
                    return orig_root == resp_root
            
            return False
        except Exception:
            return False

class ResourceBlocker:
    """Handles resource blocking for bandwidth optimization"""
    
    def __init__(self):
        self.resource_stats = {}
        self.blocked_count = 0
        self.allowed_count = 0
        self.bandwidth_tracker = BandwidthTracker()
    
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
                self.bandwidth_tracker.record_blocked_request()
                route.abort()
            else:
                self.allowed_count += 1
                # Record with initial estimate - will be updated with actual size via response listener
                self.bandwidth_tracker.record_allowed_request(resource_type, url, None)
                route.continue_()
        
        return handle_request
    
    def _should_block_resource(self, resource_type: str, url: str) -> bool:
        """Determine if a resource should be blocked - ULTRA-AGGRESSIVE APPROACH"""
        
        # STEP 1: Block all resources in the blocked types list
        if resource_type in BLOCKED_RESOURCE_TYPES:
            return True
        
        # STEP 2: For scripts and stylesheets, use WHITELIST approach (block everything except essentials)
        if resource_type in ['script', 'stylesheet']:
            # Check if this is an essential resource we need to keep
            for essential in ESSENTIAL_RESOURCES:
                if essential in url:
                    return False  # Allow essential resources
            # Block ALL other scripts and stylesheets
            return True
        
        # STEP 3: Block by URL keywords (tracking, ads, etc.)
        url_lower = url.lower()
        for keyword in BLOCKED_URL_KEYWORDS:
            if keyword in url_lower:
                return True
        
        # STEP 4: Allow only document and essential XHR requests
        if resource_type in ['document', 'xhr', 'fetch']:
            return False
        
        # STEP 5: Block everything else by default (aggressive approach)
        return True
    
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
        self.bandwidth_tracker.print_bandwidth_report()
    
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
        """Get a random user agent to avoid detection - Enhanced pool"""
        user_agents = [
            # Chrome Windows (most common)
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            
            # Chrome macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Apple M1 Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            
            # Firefox Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            
            # Firefox macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            
            # Safari macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            
            # Edge Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
        return random.choice(user_agents)
    
    @staticmethod
    def add_human_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add a random delay to appear more human-like"""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"[*] Waiting {delay:.1f}s before navigation...")
        time.sleep(delay)
    
    @staticmethod
    def setup_context(context):
        """Configure browser context for anti-detection (legacy method - use get_browser_context_options instead)"""
        # This method is kept for compatibility but enhanced context setup
        # is now handled in get_browser_context_options()
        viewport = AntiDetection.get_random_viewport()
        context.set_viewport_size(viewport)
    
    @staticmethod
    def get_random_viewport() -> dict:
        """Get a random realistic viewport size"""
        viewports = [
            {"width": 1920, "height": 1080},  # Full HD (most common)
            {"width": 1366, "height": 768},   # Common laptop
            {"width": 1536, "height": 864},   # Scaled display
            {"width": 1440, "height": 900},   # MacBook Air
            {"width": 1600, "height": 900},   # 16:9 widescreen
            {"width": 1280, "height": 720},   # HD
        ]
        return random.choice(viewports)
    
    @staticmethod
    def get_browser_context_options() -> dict:
        """Get randomized browser context options for fingerprinting protection"""
        viewport = AntiDetection.get_random_viewport()
        
        return {
            "user_agent": AntiDetection.get_random_user_agent(),
            "viewport": viewport,
            "screen": {
                "width": viewport["width"],
                "height": viewport["height"]
            },
            "device_scale_factor": random.choice([1, 1.25, 1.5, 2]),
            "is_mobile": False,
            "has_touch": False,
            "locale": random.choice(["en-US", "en-GB", "de-DE", "en-CA"]),
            "timezone_id": random.choice([
                "Europe/Berlin", "America/New_York", "Europe/London", 
                "America/Los_Angeles", "Europe/Paris"
            ]),
            "permissions": ["geolocation"],
            "color_scheme": random.choice(["light", "dark"]),
            "reduced_motion": random.choice(["reduce", "no-preference"])
        }
    
    @staticmethod
    def add_fingerprint_protection(page):
        """Add JavaScript to protect against browser fingerprinting"""
        # WebRTC leak protection
        page.add_init_script("""
            // Disable WebRTC to prevent IP leaks
            Object.defineProperty(navigator, 'mediaDevices', {
                get: () => undefined
            });
            
            // Spoof canvas fingerprinting
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                if (type === 'image/png' || type === 'image/jpeg') {
                    // Add random noise to canvas fingerprinting
                    const context = this.getContext('2d');
                    if (context) {
                        const imageData = context.getImageData(0, 0, this.width, this.height);
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] += Math.floor(Math.random() * 2); // Add noise
                        }
                        context.putImageData(imageData, 0, 0);
                    }
                }
                return originalToDataURL.apply(this, arguments);
            };
            
            // Spoof WebGL fingerprinting
            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
                    return 'Intel Inc.';
                }
                if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                    return 'Intel Iris Pro OpenGL Engine';
                }
                return originalGetParameter.apply(this, arguments);
            };
            
            // Spoof navigator properties
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 4
            });
            
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
        """)

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
