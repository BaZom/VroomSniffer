"""
Resource blocking utilities for bandwidth optimization
"""

from playwright.sync_api import Route, Request
from .bandwidth_tracker import BandwidthTracker
from .constants import BLOCKED_RESOURCE_TYPES, ESSENTIAL_RESOURCES, BLOCKED_URL_KEYWORDS


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
