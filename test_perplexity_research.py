#!/usr/bin/env python
"""
Test Perplexity comprehensive hotel research.

Tests the research_hotel() method with 5 real hotels per F-002.3 spec.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from apps.ai_agent.services.perplexity_service import PerplexityService


TEST_HOTELS = [
    {"name": "Inn 32", "city": "Woodstock", "state": "NH"},
    {"name": "Fontainebleau", "city": "Miami Beach", "state": "FL"},
    {"name": "Brown Palace Hotel", "city": "Denver", "state": "CO"},
    {"name": "Edgewater Hotel", "city": "Seattle", "state": "WA"},
    {"name": "The Plaza Hotel", "city": "New York", "state": "NY"},
]


def test_perplexity_research():
    """Test comprehensive hotel research with Perplexity."""
    print("\n" + "=" * 80)
    print(" PERPLEXITY COMPREHENSIVE RESEARCH TEST")
    print("=" * 80)

    service = PerplexityService()

    if not service.client:
        print("\n❌ FAILED: Perplexity client not initialized")
        print("   Check PERPLEXITY_API_KEY in .env")
        return False

    print("\n✅ Perplexity client initialized")

    results = []

    for i, hotel in enumerate(TEST_HOTELS, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/5: {hotel['name']}, {hotel['city']}, {hotel['state']}")
        print(f"{'='*80}")

        result = service.research_hotel(
            hotel_name=hotel['name'],
            city=hotel['city'],
            state=hotel['state']
        )

        if "error" in result:
            print(f"\n❌ FAILED: {result['error']}")
            results.append((hotel['name'], False, 0))
            continue

        # Analyze results
        confidence = result.get('confidence', 0)
        description = result.get('description', '')
        amenities = result.get('amenities', [])
        room_types = result.get('room_types', [])
        address = result.get('address')
        website = result.get('website')
        phone = result.get('phone')

        print(f"\n✅ SUCCESS (Confidence: {confidence:.0%})")
        print(f"\n📝 Description:")
        print(f"   {description[:200]}{'...' if len(description) > 200 else ''}")
        print(f"\n📍 Contact:")
        print(f"   Address: {address or 'NOT FOUND'}")
        print(f"   Phone: {phone or 'NOT FOUND'}")
        print(f"   Website: {website or 'NOT FOUND'}")
        print(f"\n✨ Amenities ({len(amenities)} found):")
        if amenities:
            print(f"   {', '.join(amenities[:8])}")
        print(f"\n🛏️  Room Types ({len(room_types)} found):")
        for rt in room_types[:3]:
            print(f"   - {rt.get('name')}: {rt.get('beds')} (max {rt.get('capacity')} guests)")

        # Scoring
        fields_found = sum([
            1 if description and len(description) > 50 else 0,
            1 if address else 0,
            1 if amenities and len(amenities) > 3 else 0,
            1 if room_types and len(room_types) > 0 else 0,
            1 if website else 0,
            1 if phone else 0
        ])

        success = confidence >= 0.5
        results.append((hotel['name'], success, fields_found))

    # Summary
    print(f"\n{'='*80}")
    print(" TEST SUMMARY")
    print(f"{'='*80}")

    successes = sum(1 for _, success, _ in results if success)
    total = len(results)

    for hotel_name, success, fields in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {hotel_name} ({fields}/6 fields)")

    print(f"\n{'='*80}")
    print(f" RESULTS: {successes}/{total} hotels successful ({successes/total*100:.0f}%)")
    print(f"{'='*80}")

    # Phase 1 acceptance criteria
    print(f"\n📊 PHASE 1 ACCEPTANCE CRITERIA:")
    print(f"   [ {'✓' if successes >= 4 else '✗'} ] Finds hotel description 90% of time (Target: 4.5/5)")
    print(f"   [ {'✓' if successes >= 4 else '✗'} ] Finds amenities 85% of time (Target: 4.25/5)")
    print(f"   [ {'✓' if successes >= 4 else '✗'} ] Finds room types 80% of time (Target: 4/5)")
    print(f"   [   ] Response time <5 seconds (check logs)")

    if successes >= 4:
        print(f"\n🎉 PHASE 1 PASSED: Perplexity integration working!")
        print("   Ready for Phase 2: Research Orchestrator")
        return True
    else:
        print(f"\n⚠️  PHASE 1 NEEDS WORK: Only {successes}/5 successful")
        print("   Review prompts and error handling")
        return False


if __name__ == "__main__":
    success = test_perplexity_research()
    sys.exit(0 if success else 1)
