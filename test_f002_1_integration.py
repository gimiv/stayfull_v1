#!/usr/bin/env python
"""
F-002.1 Integration Test - Verify All P0 Features

Tests:
1. Google Places Integration
2. Website Scraping
3. Smart Defaults
4. AI Content Enhancement

This is a simplified test to verify the integration works.
Full quality audit requires human testing with screenshots/video.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.ai_agent.services.google_places_service import GooglePlacesService
from apps.ai_agent.services.data_extractor import DataExtractor
from apps.ai_agent.services.content_formatter import ContentFormatter


def print_header(title):
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}\n")


def test_google_places():
    """Test Google Places integration"""
    print_header("TEST 1: Google Places Integration")

    service = GooglePlacesService()

    # Test hotel lookup
    print("Testing: Plaza Hotel, New York, NY")
    result = service.search_hotel("The Plaza Hotel", "New York", "NY")

    if result:
        print(f"✅ SUCCESS")
        print(f"   Name: {result.get('name')}")
        print(f"   Address: {result.get('address')}")
        print(f"   Phone: {result.get('phone')}")
        print(f"   GPS: {result.get('location')}")

        # Test timezone
        if result.get('location'):
            lat = result['location'].get('lat')
            lng = result['location'].get('lng')
            tz = service.infer_timezone_from_location(lat, lng)
            print(f"   Timezone: {tz}")

        return True
    else:
        print("❌ FAILED - Could not find hotel")
        return False


def test_website_scraping():
    """Test website scraping"""
    print_header("TEST 2: Website Scraping")

    extractor = DataExtractor()

    # Test with a real hotel website
    print("Testing: https://www.thebreakers.com/")
    result = extractor.extract_from_website("https://www.thebreakers.com/")

    if "error" in result:
        print(f"❌ FAILED: {result['error']}")
        return False

    print(f"✅ SUCCESS")
    print(f"   Hotel: {result.get('hotel_name')}")
    print(f"   City: {result.get('city')}")
    print(f"   State: {result.get('state')}")
    print(f"   Country: {result.get('country')}")
    print(f"   Confidence: {result.get('confidence', 0):.1%}")

    # Count fields
    fields_found = len([k for k, v in result.items() if v and k not in ["error", "confidence", "source_url", "domain"]])
    print(f"   Fields extracted: {fields_found}")

    # Accept confidence >= 0.5 (50%) or >= 50 (if returned as percentage)
    confidence = result.get('confidence', 0)
    return confidence >= 0.5


def test_smart_defaults():
    """Test smart defaults"""
    print_header("TEST 3: Smart Defaults")

    extractor = DataExtractor()

    # Test US states
    print("Testing: Florida (FL)")
    defaults = extractor.infer_smart_defaults("United States", "FL", "Miami")
    print(f"✅ Currency: {defaults.get('currency')}")
    print(f"✅ Tax Rate: {defaults.get('tax_rate')}%")
    print(f"✅ Language: {defaults.get('language')}")

    if defaults.get('currency') == 'USD' and defaults.get('tax_rate') == 13.0:
        print("\n✅ SUCCESS - Smart defaults working correctly")
        return True
    else:
        print("\n❌ FAILED - Incorrect defaults")
        return False


def test_content_enhancement():
    """Test AI content enhancement"""
    print_header("TEST 4: AI Content Enhancement")

    formatter = ContentFormatter()

    # Test 1: Generate hotel description
    print("Test 4.1: Generate Hotel Description")
    print("Input: 'Sunset Villa', 'Miami Beach', 'FL'")

    description = formatter.generate_hotel_description(
        hotel_name="Sunset Villa",
        city="Miami Beach",
        state="FL"
    )

    print(f"\nGenerated:\n{description}\n")

    if len(description) > 50:
        print("✅ SUCCESS - Hotel description generated")
    else:
        print("❌ FAILED - Description too short")
        return False

    # Test 2: Enhance room description
    print("\nTest 4.2: Enhance Room Description")
    print("Input: 'Nice room with ocean view'")

    enhanced = formatter.enhance_room_description(
        basic_description="Nice room with ocean view",
        room_type_name="Ocean View Suite",
        context={
            'hotel_name': 'Sunset Villa',
            'city': 'Miami Beach',
            'amenities': ['WiFi', 'Pool', 'Spa'],
            'max_occupancy': 2
        }
    )

    print(f"\nEnhanced:\n{enhanced}\n")

    if len(enhanced) > len("Nice room with ocean view"):
        print("✅ SUCCESS - Room description enhanced")
        return True
    else:
        print("❌ FAILED - Enhancement didn't work")
        return False


def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*80)
    print(" F-002.1 INTEGRATION TEST SUITE")
    print("="*80)

    results = []

    # Run all tests
    results.append(("Google Places Integration", test_google_places()))
    results.append(("Website Scraping", test_website_scraping()))
    results.append(("Smart Defaults", test_smart_defaults()))
    results.append(("AI Content Enhancement", test_content_enhancement()))

    # Summary
    print_header("TEST RESULTS SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n{'='*80}")
    print(f" RESULTS: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'='*80}")

    if passed == total:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("\nF-002.1 P0 Features Status:")
        print("✅ Google Places Integration - Working")
        print("✅ Website Scraping - Working")
        print("✅ Smart Defaults - Working")
        print("✅ AI Content Enhancement - Working")
        print("\n🚀 READY FOR PRODUCTION")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - needs fixing")

    return passed == total


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
