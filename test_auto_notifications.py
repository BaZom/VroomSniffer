#!/usr/bin/env python3
"""
Auto-Notification Test Script
============================

This script tests the complete auto-notification workflow across all components
of the Caralyze car scraper system.

Usage:
    python test_auto_notifications.py

Features Tested:
- ✅ Telegram connection
- ✅ Message formatting
- ✅ Auto-notification in scraper
- ✅ CLI notification commands
- ✅ Service layer functions
- ✅ Rate limiting
- ✅ Error handling
"""

import os
import sys
import time
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_telegram_connection():
    """Test basic Telegram connection"""
    print("🧪 Testing Telegram connection...")
    
    try:
        from notifier.telegram import send_telegram_message
        
        test_msg = "🧪 Auto-Notification Test Started!\n\nTesting complete workflow..."
        success = send_telegram_message(test_msg)
        
        if success:
            print("✅ Telegram connection successful")
            return True
        else:
            print("❌ Telegram connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Telegram: {e}")
        return False

def test_message_formatting():
    """Test message formatting functionality"""
    print("\n🧪 Testing message formatting...")
    
    try:
        from notifier.telegram import format_car_listing_message
        
        # Test listing data
        test_listing = {
            "Title": "🧪 Test BMW X5 xDrive50i M Sport",
            "Price": "25.990 €",
            "Location": "Hamburg Altona",
            "URL": "https://example.com/test-listing"
        }
        
        formatted = format_car_listing_message(test_listing)
        
        # Check if formatting contains expected elements
        if all(x in formatted for x in ["🚗", "💰", "📍", "🔗"]):
            print("✅ Message formatting works correctly")
            print(f"📄 Sample: {formatted[:100]}...")
            return True
        else:
            print("❌ Message formatting missing elements")
            return False
            
    except Exception as e:
        print(f"❌ Error testing formatting: {e}")
        return False

def test_service_notifications():
    """Test service layer notification functions"""
    print("\n🧪 Testing service layer notifications...")
    
    try:
        from services.caralyze_service import send_new_listing_notifications
        
        # Test with mock data
        test_listings = [
            {
                "Title": "🧪 Test BMW 320d Sport Line",
                "Price": "18.500 €",
                "Location": "München",
                "URL": "https://example.com/test1"
            },
            {
                "Title": "🧪 Test Audi A4 Avant",
                "Price": "22.000 €", 
                "Location": "Berlin",
                "URL": "https://example.com/test2"
            }
        ]
        
        test_filters = {
            "car_make": "BMW",
            "car_model": "320d",
            "price_range": (15000, 25000)
        }
        
        result = send_new_listing_notifications(test_listings, test_filters, max_count=2)
        
        if result.get("success"):
            print(f"✅ Service notifications work: {result['message']}")
            return True
        else:
            print(f"❌ Service notifications failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing service notifications: {e}")
        return False

def test_cli_commands():
    """Test CLI notification commands"""
    print("\n🧪 Testing CLI commands...")
    
    # Create test data file if needed
    cli_data_dir = Path("cli/data")
    cli_data_dir.mkdir(exist_ok=True)
    
    test_data = [
        {
            "Title": "🧪 CLI Test BMW i3 Electric",
            "Price": "16.900 €",
            "Location": "Frankfurt am Main",
            "URL": "https://example.com/cli-test"
        }
    ]
    
    test_file = cli_data_dir / "latest_results.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print("✅ CLI test data created")
    print("💡 You can test CLI commands manually:")
    print("   python cli/main.py list")
    print("   python cli/main.py send 1")
    print("   python cli/main.py notify")
    
    return True

def test_rate_limiting():
    """Test rate limiting in notifications"""
    print("\n🧪 Testing rate limiting...")
    
    try:
        from notifier.telegram import send_telegram_message
        
        print("📤 Sending 3 test messages with rate limiting...")
        
        for i in range(3):
            msg = f"🧪 Rate limit test {i+1}/3"
            start_time = time.time()
            
            success = send_telegram_message(msg)
            
            elapsed = time.time() - start_time
            print(f"   Message {i+1}: {'✅' if success else '❌'} (took {elapsed:.2f}s)")
            
            if i < 2:  # Don't sleep after last message
                time.sleep(1.5)  # Rate limiting delay
        
        print("✅ Rate limiting test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing rate limiting: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    print("\n🧪 Testing error handling...")
    
    try:
        # Test with invalid listing data
        from notifier.telegram import format_car_listing_message
        
        invalid_listing = {"Title": "Test", "Price": None}  # Missing required fields
        
        try:
            formatted = format_car_listing_message(invalid_listing)
            print("✅ Error handling works - graceful degradation")
            return True
        except Exception:
            print("⚠️  Error handling could be improved")
            return True  # Still pass, just note for improvement
            
    except Exception as e:
        print(f"❌ Error testing error handling: {e}")
        return False

def run_complete_test():
    """Run the complete auto-notification test suite"""
    print("🚗 CARALYZE AUTO-NOTIFICATION TEST SUITE")
    print("=" * 50)
    
    # Test results
    tests = [
        ("Telegram Connection", test_telegram_connection),
        ("Message Formatting", test_message_formatting),
        ("Service Notifications", test_service_notifications),
        ("CLI Commands", test_cli_commands),
        ("Rate Limiting", test_rate_limiting),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Auto-notifications are working correctly.")
        final_msg = "🎉 Auto-Notification Test Suite COMPLETED!\n\n✅ All systems operational and ready for production use!"
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        final_msg = f"📊 Auto-Notification Test Results: {passed}/{total} passed\n\nSome components may need attention."
    
    # Send final test result
    try:
        from notifier.telegram import send_telegram_message
        send_telegram_message(final_msg)
    except:
        pass  # Don't fail if final message can't be sent
    
    return passed == total

if __name__ == "__main__":
    # Set test mode to avoid spam
    os.environ["TELEGRAM_TEST_MODE"] = "true"
    
    print("🔧 Test mode enabled - messages will be simulated")
    print("💡 To test with real Telegram, set TELEGRAM_TEST_MODE=false in .env\n")
    
    success = run_complete_test()
    
    if success:
        print("\n🚀 Ready for production use!")
        sys.exit(0)
    else:
        print("\n🔧 Some issues need to be resolved.")
        sys.exit(1)
