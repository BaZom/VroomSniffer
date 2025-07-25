"""
Anti-detection utilities for VroomSniffer scraper
"""

import random
import time
from typing import Dict


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
