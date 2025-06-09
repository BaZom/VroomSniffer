# Telegram Notifier
# -----------------
# Sends messages using Telegram Bot API.
# You need to create a bot via @BotFather and get your bot token.
# Also need your chat ID where messages will be sent.

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TEST_MODE = os.getenv("TELEGRAM_TEST_MODE", "false").lower() == "true"

def send_telegram_message(text):
    """
    Send a message via Telegram Bot API
    
    Args:
        text (str): Message text to send
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("[!] Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured")
        print("[!] Please set these environment variables or add them to .env file")
        return False
    
    # Test mode - simulate sending without actually connecting
    if TEST_MODE:
        print(f"[TEST MODE] Would send Telegram message to {CHAT_ID}:")
        print(f"[TEST MODE] Message: {text}")
        print(f"[+] Telegram message sent successfully (test mode)")
        return True
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'  # Enable HTML formatting
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print(f"[+] Sent Telegram message successfully")
            return True
        else:
            print(f"[!] Telegram API error: {result.get('description', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[!] Error sending Telegram message: {e}")
        return False
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return False

def format_car_listing_message(listing):
    """
    Format a car listing for Telegram message
    
    Args:
        listing (dict): Car listing data
        
    Returns:
        str: Formatted message text
    """
    title = listing.get("Title", "Unknown")
    price = listing.get("Price", "Unknown")
    location = listing.get("Location", "Unknown")
    url = listing.get("URL", "")
    
    message = f"""🚗 <b>New Car Listing</b>

<b>{title}</b>
💰 {price}
📍 {location}

🔗 <a href="{url}">View Listing</a>"""
    
    return message

if __name__ == "__main__":
    # Test the Telegram notifier
    test_message = "🚗 Test message from Caralyze Car Scraper!"
    success = send_telegram_message(test_message)
    
    if success:
        print("[+] Telegram notifier test successful!")
    else:
        print("[!] Telegram notifier test failed!")
