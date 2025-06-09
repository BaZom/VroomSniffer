#!/usr/bin/env python3
"""
Test script for auto-monitoring functionality
"""

import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from services.caralyze_service import get_listings_for_filter
from notifier.telegram import send_telegram_message, format_car_listing_message

def test_auto_monitoring():
    """Test the auto-monitoring functionality"""
    
    print("🚗 Testing Auto-Monitoring Functionality")
    print("=" * 50)
    
    # Test filters (similar to what UI would use)
    test_filters = {
        "custom_url": "",
        "car_make": "BMW",
        "car_model": "",
        "price_range": (5000, 20000),
        "year_range": (2015, 2025),
        "transmission": "Any",
        "max_mileage": 150000,
        "auto_send": True,
        "auto_monitor": True
    }
    
    # Paths
    root_dir = Path(__file__).parent
    listings_dir = root_dir / "storage" / "listings"
    listings_dir.mkdir(parents=True, exist_ok=True)
    all_old_path = listings_dir / "all_old_results.json"
    latest_new_path = listings_dir / "latest_new_results.json"
    
    def build_test_search_url(filters):
        """Test URL builder"""
        base_url = "https://www.kleinanzeigen.de/s-autos/"
        price_path = ""
        if filters.get("price_range"):
            min_price, max_price = filters["price_range"]
            price_path = f"preis:{min_price}:{max_price}/"
        make = filters.get("car_make", "").lower()
        return base_url + price_path + make + "/k0c216"
    
    # Simulate auto-monitoring cycle
    for cycle in range(3):
        print(f"\n🔄 Auto-monitoring cycle #{cycle + 1}")
        print(f"⏰ Time: {time.strftime('%H:%M:%S')}")
        
        try:
            # Run scraper
            print("📡 Fetching listings...")
            all_listings, new_listings = get_listings_for_filter(
                test_filters, all_old_path, latest_new_path, build_test_search_url, root_dir
            )
            
            print(f"📊 Results: {len(all_listings)} total, {len(new_listings)} new")
            
            # Test auto-send
            if new_listings and test_filters.get("auto_send"):
                print(f"📱 Auto-sending {len(new_listings)} listings...")
                
                for i, listing in enumerate(new_listings[:2]):  # Limit to 2 for testing
                    formatted_msg = format_car_listing_message(listing)
                    success = send_telegram_message(formatted_msg)
                    print(f"  📤 Listing {i+1}: {'✅' if success else '❌'}")
                    
                    if i < len(new_listings[:2]) - 1:
                        time.sleep(1)  # Rate limiting
            
            else:
                print("📵 No new listings or auto-send disabled")
            
        except Exception as e:
            print(f"❌ Error in cycle {cycle + 1}: {e}")
        
        # Wait before next cycle (shortened for testing)
        if cycle < 2:
            print(f"⏳ Waiting 30 seconds before next cycle...")
            time.sleep(30)
    
    print("\n✅ Auto-monitoring test completed!")
    print("🎯 Check your Telegram for any sent messages")

if __name__ == "__main__":
    test_auto_monitoring()
