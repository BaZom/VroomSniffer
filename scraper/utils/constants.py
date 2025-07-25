"""
Constants for VroomSniffer scraper anti-detection and bandwidth optimization
"""

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
