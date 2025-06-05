# Configuration Loader
# --------------------
# Loads environment variables from a .env file (used for API keys, tokens, etc.)

from dotenv import load_dotenv
import os

# Load from .env into environment
load_dotenv()

# Example usage
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
WHATSAPP_TO = os.getenv("WHATSAPP_TO")
