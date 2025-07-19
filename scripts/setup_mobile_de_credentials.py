#!/usr/bin/env python3
"""
Mobile.de API Credential Setup Script
------------------------------------
Helper script to programmatically configure mobile.de API credentials.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv
from getpass import getpass

def setup_credentials():
    """Interactive setup of mobile.de API credentials."""
    print("🔧 Mobile.de API Credential Setup")
    print("=" * 40)
    
    # Find or create .env file
    env_file = find_dotenv()
    if not env_file:
        env_file = Path.cwd() / ".env"
        env_file.touch()
        print(f"📄 Created .env file: {env_file}")
    else:
        print(f"📄 Using existing .env file: {env_file}")
    
    # Load existing values
    load_dotenv(env_file)
    current_username = os.getenv("MOBILE_DE_API_USERNAME", "")
    current_base_url = os.getenv("MOBILE_DE_API_BASE_URL", "https://api.mobile.de")
    
    print("\n📞 Contact mobile.de for API access:")
    print("   Phone: 030 81097-500 (Business line)")
    print("   Email: service@team.mobile.de")
    print("   Hours: Monday-Friday, 8:00-18:00")
    
    print("\n📝 Enter your mobile.de API credentials:")
    
    # Get username
    if current_username:
        username = input(f"Username [{current_username}]: ").strip()
        if not username:
            username = current_username
    else:
        username = input("Username: ").strip()
    
    if not username:
        print("❌ Username is required!")
        return False
    
    # Get password (hidden input)
    password = getpass("Password: ")
    if not password:
        print("❌ Password is required!")
        return False
    
    # Get base URL
    base_url = input(f"API Base URL [{current_base_url}]: ").strip()
    if not base_url:
        base_url = current_base_url
    
    # Save to .env file
    try:
        set_key(env_file, "MOBILE_DE_API_USERNAME", username)
        set_key(env_file, "MOBILE_DE_API_PASSWORD", password)
        set_key(env_file, "MOBILE_DE_API_BASE_URL", base_url)
        
        print("✅ Credentials saved successfully!")
        
        # Test connection
        print("\n🧪 Testing connection...")
        
        # Add project root to path for imports
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from api.manager import get_api_manager
        
        api_manager = get_api_manager()
        success = api_manager.configure_mobile_de(username, password, base_url)
        
        if success:
            print("✅ Connection test successful!")
            print("\n🎉 Setup complete! You can now use --platform mobile.de")
            return True
        else:
            print("❌ Connection test failed. Please check your credentials.")
            return False
            
    except Exception as e:
        print(f"❌ Failed to save credentials: {str(e)}")
        return False

def clear_credentials():
    """Clear stored mobile.de API credentials."""
    env_file = find_dotenv()
    if not env_file:
        print("📄 No .env file found")
        return
    
    try:
        set_key(env_file, "MOBILE_DE_API_USERNAME", "")
        set_key(env_file, "MOBILE_DE_API_PASSWORD", "")
        set_key(env_file, "MOBILE_DE_API_BASE_URL", "https://api.mobile.de")
        print("✅ Credentials cleared!")
        
    except Exception as e:
        print(f"❌ Failed to clear credentials: {str(e)}")

def show_status():
    """Show current credential status."""
    load_dotenv()
    
    username = os.getenv("MOBILE_DE_API_USERNAME", "")
    base_url = os.getenv("MOBILE_DE_API_BASE_URL", "https://api.mobile.de")
    
    print("📊 Current Status:")
    print(f"   Username: {'✅ Configured' if username else '❌ Not set'}")
    print(f"   Password: {'✅ Configured' if os.getenv('MOBILE_DE_API_PASSWORD') else '❌ Not set'}")
    print(f"   Base URL: {base_url}")
    
    if username and os.getenv("MOBILE_DE_API_PASSWORD"):
        print("   Status: ✅ Ready for mobile.de API")
    else:
        print("   Status: ⚠️  Credentials needed")

def main():
    """Main credential management interface."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup_credentials()
        elif command == "clear":
            clear_credentials()
        elif command == "status":
            show_status()
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
    else:
        show_help()

def show_help():
    """Show help information."""
    print("""
🔧 Mobile.de API Credential Manager

Usage:
    python scripts/setup_mobile_de_credentials.py <command>

Commands:
    setup    - Interactive credential setup
    clear    - Clear stored credentials  
    status   - Show current status

Examples:
    python scripts/setup_mobile_de_credentials.py setup
    python scripts/setup_mobile_de_credentials.py status
    """)

if __name__ == "__main__":
    main()
