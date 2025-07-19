#!/usr/bin/env python3
"""
Mobile.de API Connection Tester
------------------------------
Test mobile.de API connection and credentials.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.manager import get_api_manager
from api.mobile_de import MobileDeAPIClient

def test_connection():
    """Test mobile.de API connection."""
    print("🧪 Mobile.de API Connection Test")
    print("=" * 35)
    
    # Load environment variables
    load_dotenv()
    
    username = os.getenv("MOBILE_DE_API_USERNAME")
    password = os.getenv("MOBILE_DE_API_PASSWORD") 
    base_url = os.getenv("MOBILE_DE_API_BASE_URL", "https://api.mobile.de")
    
    # Check credentials
    if not username or not password:
        print("❌ Credentials not found!")
        print("\nPlease configure credentials using one of these methods:")
        print("1. python scripts/setup_mobile_de_credentials.py setup")
        print("2. Use the Streamlit UI")
        print("3. Set environment variables manually")
        return False
    
    print(f"📡 Testing connection to: {base_url}")
    print(f"👤 Username: {username}")
    print(f"🔑 Password: {'*' * len(password)}")
    
    try:
        # Test via API manager
        print("\n🔧 Testing via API Manager...")
        api_manager = get_api_manager()
        success = api_manager.configure_mobile_de(username, password, base_url)
        
        if success:
            print("✅ API Manager configuration successful!")
        else:
            print("❌ API Manager configuration failed!")
            return False
        
        # Test direct client connection
        print("\n🔧 Testing direct client connection...")
        client = MobileDeAPIClient(username, password, base_url)
        success, message = client.test_connection()
        
        if success:
            print(f"✅ {message}")
            print("\n🎉 All tests passed! mobile.de API is ready to use.")
            return True
        else:
            print(f"❌ {message}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

def test_url_conversion():
    """Test URL to API parameter conversion."""
    print("\n🔄 Testing URL Conversion...")
    
    # Load environment 
    load_dotenv()
    username = os.getenv("MOBILE_DE_API_USERNAME")
    password = os.getenv("MOBILE_DE_API_PASSWORD")
    base_url = os.getenv("MOBILE_DE_API_BASE_URL", "https://api.mobile.de")
    
    if not username or not password:
        print("❌ Credentials needed for URL conversion test")
        return False
    
    try:
        client = MobileDeAPIClient(username, password, base_url)
        
        # Test URL
        test_url = "https://mobile.de/search?makeId=1900&modelId=19&minPrice=10000&maxPrice=30000&zipcode=10115&radius=50"
        print(f"Test URL: {test_url}")
        
        params = client.convert_search_url_to_params(test_url)
        print(f"Converted parameters: {params}")
        
        if params:
            print("✅ URL conversion successful!")
            return True
        else:
            print("❌ URL conversion failed!")
            return False
            
    except Exception as e:
        print(f"❌ URL conversion test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        test_url_conversion()
    
    print(f"\n{'✅ All tests passed!' if success else '❌ Tests failed!'}")
