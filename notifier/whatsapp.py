# WhatsApp Notifier
# -----------------
# Sends messages using Twilio WhatsApp API.
# You need a Twilio trial account and verified recipient number.

from twilio.rest import Client
import os

# Load environment variables from .env file if it exists
load_dotenv = True
if load_dotenv:
    from dotenv import load_dotenv
    load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_SID")
AUTH_TOKEN = os.getenv("TWILIO_TOKEN")
FROM = "+4917660353704"
TO = os.getenv("WHATSAPP_TO")

print(ACCOUNT_SID, AUTH_TOKEN, FROM, TO)

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_whatsapp_message(text):
    message = client.messages.create(
        body="Hello from your WhatsApp notifier! I am bot message.",
        from_=FROM,
        to=TO
    )
    print(f"[+] Sent WhatsApp message: SID {message.sid}")

if __name__ == "__main__":
    try:
        send_whatsapp_message("Test message from WhatsApp notifier!")
    except Exception as e:
        print(f"[!] Error sending WhatsApp message: {e}")
