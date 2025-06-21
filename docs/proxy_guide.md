# WebShare Residential Proxies Guide for VroomSniffer

This guide explains how to set up and use WebShare rotating residential proxies with VroomSniffer to improve scraping reliability and avoid blocking.

## What are WebShare Rotating Residential Proxies?

WebShare's rotating residential proxies provide several benefits for web scraping:

- **IP Rotation**: Each request goes through a different residential IP address
- **Avoid Blocking**: Residential IPs are less likely to be detected as bots
- **Simple Setup**: Basic username/password authentication

## Setup Guide

### 1. Create WebShare Account and Subscribe

1. Sign up at [WebShare.io](https://www.webshare.io/)
2. Subscribe to a residential proxy plan
3. Note your proxy credentials (username and password)
4. Check the dashboard for your proxy endpoint details (usually `p.webshare.io` port `80`)

### 2. Configure Environment Variables

Create a `.env` file in your project root by copying `.env.proxy.example`:

```bash
# WebShare Proxy Configuration
PROXY_TYPE=WEBSHARE_RESIDENTIAL
WEBSHARE_USERNAME=your_webshare_username
WEBSHARE_PASSWORD=your_webshare_password
WEBSHARE_PROXY_HOST=p.webshare.io
WEBSHARE_PROXY_PORT=80

# Telegram Configuration (if used)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 3. Using WebShare Proxies in VroomSniffer

#### Via Command Line

To use proxies when scraping with the CLI:

```bash
# For a single scrape:
python -m cli.main run "https://example-marketplace.com/search" --use-proxy --proxy-type WEBSHARE_RESIDENTIAL

# For scheduled scraping:
python -m cli.main schedule "https://example-marketplace.com/search" --use-proxy --proxy-type WEBSHARE_RESIDENTIAL --interval 120 --runs 5
```

#### Via the Web UI

1. Open the Streamlit UI: `streamlit run ui/streamlit_app.py`
2. Navigate to the Scraper page
3. Click "Advanced Settings" to expand the settings panel
4. Toggle "Use proxy" to ON
5. Select "WebShare Residential" from the proxy type dropdown

## Testing Your Proxy Connection

You can test if your proxy is working correctly using the included test script:

```bash
python scripts/verify_proxy.py
```

This script will:
1. Check your current IP without a proxy
2. Try connecting through your WebShare proxy
3. Verify the IP changed (confirming proxy is working)
4. Provide detailed feedback on proxy status

## Common Issues

1. **Authentication Errors**: Make sure your WebShare username and password are correct in the `.env` file
2. **Connection Timeouts**: WebShare may limit requests per minute - try longer intervals between scraping runs
3. **No IP Change**: If the script shows your IP didn't change, check your WebShare dashboard to make sure your account is active

## Additional Information

- WebShare Documentation: [https://proxy.webshare.io/documentation](https://proxy.webshare.io/documentation)
- ProxyManager Implementation: See `proxy/manager.py` in your project
- Proxy-specific Configuration: See `.env.proxy.example` for configuration options
