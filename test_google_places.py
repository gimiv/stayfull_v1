"""
Test script for GooglePlacesService with 5 real hotels.
Run: python test_google_places.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from apps.ai_agent.services.google_places_service import GooglePlacesService


def test_hotel(service, hotel_name, city, state=None):
    """Test searching for a hotel."""
    print(f"\n{'='*70}")
    print(f"TEST: {hotel_name}, {city} {state or ''}")
    print(f"{'='*70}")

    result = service.search_hotel(hotel_name, city, state)

    if result:
        print(f"✅ SUCCESS!")
        print(f"   Name: {result.get('name')}")
        print(f"   Address: {result.get('address')}")
        print(f"   Phone: {result.get('phone')}")
        print(f"   Website: {result.get('website')}")
        print(f"   Location: {result.get('location')}")
        print(f"   Photos: {len(result.get('photos', []))} available")
        print(f"   Rating: {result.get('rating')} ({result.get('user_ratings_total')} reviews)")
        print(f"   Status: {result.get('business_status')}")

        # Test timezone lookup
        if result.get('location'):
            lat = result['location'].get('lat')
            lng = result['location'].get('lng')
            if lat and lng:
                timezone = service.infer_timezone_from_location(lat, lng)
                print(f"   Timezone: {timezone}")

        return True
    else:
        print(f"❌ FAILED - Hotel not found")
        return False


def main():
    """Test GooglePlacesService with 5 different hotels."""
    print("\n" + "=" * 70)
    print(" GOOGLE PLACES SERVICE - TEST SUITE")
    print("=" * 70)

    service = GooglePlacesService()

    if not service.client:
        print("\n❌ CRITICAL: Google Places client not initialized!")
        print("   Please check GOOGLE_PLACES_API_KEY in .env")
        return

    # Test cases: 5 different hotels in different cities
    test_cases = [
        ("Fontainebleau", "Miami Beach", "FL"),
        ("The Plaza Hotel", "New York", "NY"),
        ("Hotel del Coronado", "San Diego", "CA"),
        ("The Venetian", "Las Vegas", "NV"),
        ("The Breakers", "Palm Beach", "FL"),
    ]

    results = []

    for hotel_name, city, state in test_cases:
        success = test_hotel(service, hotel_name, city, state)
        results.append((hotel_name, success))

    # Summary
    print(f"\n{'='*70}")
    print(" TEST SUMMARY")
    print(f"{'='*70}")

    success_count = sum(1 for _, success in results if success)
    total_count = len(results)

    for hotel_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {hotel_name}")

    print(f"\n{'='*70}")
    print(f" RESULTS: {success_count}/{total_count} tests passed ({success_count/total_count*100:.0f}%)")
    print(f"{'='*70}")

    if success_count >= 4:  # 80%+ success rate
        print("\n🎉 GATE 1 PASSED: Google Places integration working!")
    else:
        print("\n⚠️  GATE 1 FAILED: Need at least 4/5 tests passing")


if __name__ == "__main__":
    main()
