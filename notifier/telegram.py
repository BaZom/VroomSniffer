# Telegram Notifier
# -----------------
# Sends messages using Telegram Bot API.

import requests
import os
from dotenv import load_dotenv

# Load environment variables on import
load_dotenv()

def _get_telegram_config():
    """Get fresh Telegram configuration from environment variables"""
    # Reload environment variables to pick up any changes
    load_dotenv(override=True)
    
    return {
        'bot_token': os.getenv("TELEGRAM_BOT_TOKEN"),
        'chat_id': os.getenv("TELEGRAM_CHAT_ID")
    }

def send_telegram_message(text, parse_mode=None):
    """
    Send a message via Telegram Bot API
    
    Args:
        text (str): Message text to send
        parse_mode (str, optional): Telegram parse mode (e.g., 'HTML', 'MarkdownV2')
        
    Returns:
        bool: True if message sent successfully, False otherwise
        str: Error message if failed, else None
    """
    # Get fresh configuration each time
    config = _get_telegram_config()
    bot_token = config['bot_token']
    chat_id = config['chat_id']
    
    if not bot_token or not chat_id:
        return False, "[!] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text  # Use the actual message text
        # Do not set 'parse_mode' for plain text
    }
    if parse_mode:
        payload['parse_mode'] = parse_mode
    
    try:
        response = requests.post(url, data=payload)
        try:
            result = response.json()
        except Exception:
            result = response.text
        if response.status_code != 200:
            # Return the actual result (dict) for proper error handling
            return False, result
        if isinstance(result, dict) and result.get('ok'):
            return True, None
        else:
            # Return the actual result (dict) for proper error handling
            return False, result
    except requests.exceptions.RequestException as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def format_car_listing_message(listing, search_description=None):
    """
    Format a car listing for Telegram message
    
    Args:
        listing (dict): Car listing data
        search_description (str, optional): Description of the search URL/filter
        
    Returns:
        str: Formatted message text
    """
    title = listing.get("Title", "Unknown")
    price = listing.get("Price", "Unknown")
    location = listing.get("Location", "Unknown")
    url = listing.get("URL", "")
    source_url = listing.get("source_url", "")
    
    # Try to get URL description from listing, or use provided search_description
    if not search_description and source_url:
        # Import here to avoid circular imports
        from services.url_pool_service import UrlPoolService
        url_service = UrlPoolService()
        url_data = url_service.get_url_data()
        
        if source_url in url_data and url_data[source_url].get('description'):
            search_description = url_data[source_url]['description']
    
    header = "🚗 <b>New Car Listing</b>"
    if search_description:
        header += f"\n<b>{search_description}</b>"
    
    message = f"""{header}

<b>{title}</b>
💰 {price}
📍 {location}

🔗 <a href="{url}">View Listing</a>"""
    
    return message

if __name__ == "__main__":
    # Test the Telegram notifier
    test_message = "🚗 Test message from VroomSniffer Car Scraper!"
    success, error = send_telegram_message(test_message)
    
    if success:
        print("[+] Telegram notifier test successful!")
    else:
        print(f"[!] Telegram notifier test failed: {error}")
