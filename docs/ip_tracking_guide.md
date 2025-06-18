# IP Tracking with VroomSniffer

VroomSniffer now tracks the IP addresses used to access each URL, helping you monitor your scraping activities and proxy usage.

## Overview

Every time a URL is scraped, VroomSniffer records:
- The IP address used (either direct or proxy)
- Whether it was a direct connection or through a proxy
- Timestamp of first and last usage
- How many times that IP has been used for the same URL

This information is stored in `storage/ip_tracking.json`.

## Viewing IP Tracking Information

You can view your IP tracking information using the CLI diagnostics command:

```bash
python cli/main.py diagnostics --show-ip-tracking
```

This command displays:
- A summary of your tracked URLs
- For each URL, a list of IPs used (both direct and proxy)
- Usage timestamps and counts

## Benefits of IP Tracking

1. **Monitor Proxy Rotation**: Verify that your proxy provider is actually rotating IPs
2. **Track Blocking Risk**: If you repeatedly use the same IP for a URL, you might be at risk of being blocked
3. **Audit Usage**: Keep track of your scraping activities over time

## How It Works

The IP tracking system automatically:
1. Records your direct IP before each scrape
2. Records the proxy IP when using proxy mode
3. Stores this information in `storage/ip_tracking.json`
4. Updates existing records to track repeated use of the same IP

## Storage Format

The IP tracking data is stored as a JSON file with this structure:

```json
{
  "url_ip_mapping": {
    "https://example.com/cars": [
      {
        "ip": "123.45.67.89",
        "first_used": "2025-06-19 14:30:10",
        "last_used": "2025-06-19 16:45:22",
        "is_proxy": false,
        "use_count": 3
      },
      {
        "ip": "98.76.54.32",
        "first_used": "2025-06-19 15:30:10",
        "last_used": "2025-06-19 15:30:10",
        "is_proxy": true,
        "use_count": 1
      }
    ]
  },
  "last_updated": "2025-06-19 16:45:22"
}
```
