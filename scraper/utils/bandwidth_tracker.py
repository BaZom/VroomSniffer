"""
Bandwidth tracking utilities for VroomSniffer scraper
"""

from typing import Dict, List


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
