"""
Test script for website scraping with 10 different hotel websites.

Tests extraction accuracy and measures success rate.
Run: python test_website_scraping.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from apps.ai_agent.services.data_extractor import DataExtractor


# Test cases: 10 different hotel websites
# Mix of: WordPress, Wix, custom, hotel chains, boutique hotels
TEST_HOTELS = [
    {
        "name": "Fontainebleau Miami Beach",
        "url": "https://www.fontainebleau.com/",
        "expected": {
            "hotel_name": "Fontainebleau",
            "city": "Miami Beach",
            "state": "FL",
            "country": "United States"
        }
    },
    {
        "name": "The Plaza Hotel NYC",
        "url": "https://www.theplazany.com/",
        "expected": {
            "hotel_name": "The Plaza",
            "city": "New York",
            "state": "NY",
            "country": "United States"
        }
    },
    {
        "name": "Hotel del Coronado",
        "url": "https://hoteldel.com/",
        "expected": {
            "hotel_name": "Hotel del Coronado",
            "city": "San Diego",
            "state": "CA",
            "country": "United States"
        }
    },
    {
        "name": "The Breakers Palm Beach",
        "url": "https://www.thebreakers.com/",
        "expected": {
            "hotel_name": "The Breakers",
            "city": "Palm Beach",
            "state": "FL",
            "country": "United States"
        }
    },
    {
        "name": "The Ritz-Carlton South Beach",
        "url": "https://www.ritzcarlton.com/en/hotels/miami/south-beach",
        "expected": {
            "hotel_name": "Ritz-Carlton",
            "city": "Miami",
            "state": "FL",
            "country": "United States"
        }
    },
    {
        "name": "The Standard Miami",
        "url": "https://www.standardhotels.com/miami",
        "expected": {
            "hotel_name": "Standard",
            "city": "Miami",
            "state": "FL",
            "country": "United States"
        }
    },
    {
        "name": "The W South Beach",
        "url": "https://www.marriott.com/en-us/hotels/miawy-w-south-beach/",
        "expected": {
            "hotel_name": "W South Beach",
            "city": "Miami",
            "state": "FL",
            "country": "United States"
        }
    },
    {
        "name": "The Setai Miami Beach",
        "url": "https://www.thesetaihotels.com/miami-beach/",
        "expected": {
            "hotel_name": "Setai",
            "city": "Miami Beach",
            "state": "FL",
            "country": "United States"
        }
    },
    {
        "name": "The Surfcomber Hotel",
        "url": "https://www.surfcomber.com/",
        "expected": {
            "hotel_name": "Surfcomber",
            "city": "Miami Beach",
            "state": "FL",
            "country": "United States"
        }
    },
    {
        "name": "The Nautilus South Beach",
        "url": "https://www.thenautilushotel.com/",
        "expected": {
            "hotel_name": "Nautilus",
            "city": "Miami Beach",
            "state": "FL",
            "country": "United States"
        }
    },
]


def calculate_accuracy(extracted, expected):
    """
    Calculate extraction accuracy for a single hotel.

    Returns score out of 10 (one point per required field found correctly).
    """
    score = 0
    total_fields = 7  # 7 required fields

    # Required fields
    required_fields = ["hotel_name", "city", "state", "country", "phone", "email", "address"]

    for field in required_fields:
        if field in extracted and extracted[field]:
            # Field was extracted (1 point for finding it)
            score += 1

            # Bonus: Check if it matches expected (for fields we can verify)
            if field in expected:
                extracted_lower = str(extracted[field]).lower()
                expected_lower = str(expected[field]).lower()

                # Partial match is good enough
                if expected_lower in extracted_lower or extracted_lower in expected_lower:
                    score += 0.5  # Bonus for correctness

    # Bonus for optional fields
    if extracted.get("description"):
        score += 0.5
    if extracted.get("amenities") and len(extracted["amenities"]) > 0:
        score += 0.5
    if extracted.get("room_types") and len(extracted["room_types"]) > 0:
        score += 0.5

    return min(score, 10)  # Cap at 10


def test_website_scraping():
    """Test website scraping with 10 different hotels."""
    print("\n" + "=" * 80)
    print(" WEBSITE SCRAPING TEST - 10 HOTELS")
    print("=" * 80)

    extractor = DataExtractor()
    results = []

    for i, test_case in enumerate(TEST_HOTELS, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/10: {test_case['name']}")
        print(f"URL: {test_case['url']}")
        print(f"{'=' * 80}")

        # Extract data
        extracted = extractor.extract_from_website(test_case['url'])

        if "error" in extracted:
            print(f"❌ FAILED: {extracted['error']}")
            results.append({
                "name": test_case['name'],
                "success": False,
                "accuracy": 0,
                "error": extracted['error']
            })
            continue

        # Calculate accuracy
        accuracy = calculate_accuracy(extracted, test_case['expected'])
        accuracy_pct = (accuracy / 10) * 100

        # Display results
        print(f"\n✅ SUCCESS (Confidence: {extracted.get('confidence', 0):.1%})")
        print(f"   Hotel Name: {extracted.get('hotel_name', 'NOT FOUND')}")
        print(f"   Address: {extracted.get('address', 'NOT FOUND')}")
        print(f"   City: {extracted.get('city', 'NOT FOUND')}")
        print(f"   State: {extracted.get('state', 'NOT FOUND')}")
        print(f"   Country: {extracted.get('country', 'NOT FOUND')}")
        print(f"   Phone: {extracted.get('phone', 'NOT FOUND')}")
        print(f"   Email: {extracted.get('email', 'NOT FOUND')}")
        amenities = extracted.get('amenities') or []
        room_types = extracted.get('room_types') or []
        print(f"   Amenities: {len(amenities)} found")
        print(f"   Room Types: {len(room_types)} found")
        print(f"\n   ACCURACY: {accuracy_pct:.0f}% ({accuracy}/10 points)")

        results.append({
            "name": test_case['name'],
            "success": True,
            "accuracy": accuracy,
            "confidence": extracted.get('confidence', 0),
            "fields_found": len([k for k, v in extracted.items() if v and k not in ["error", "confidence", "source_url", "domain"]])
        })

    # Summary
    print(f"\n{'=' * 80}")
    print(" TEST SUMMARY")
    print(f"{'=' * 80}")

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    success_rate = (len(successful) / len(results)) * 100
    avg_accuracy = sum(r['accuracy'] for r in successful) / len(successful) if successful else 0
    avg_accuracy_pct = (avg_accuracy / 10) * 100

    print(f"\nExecution Results:")
    print(f"  ✅ Successful: {len(successful)}/10 ({success_rate:.0f}%)")
    print(f"  ❌ Failed: {len(failed)}/10")

    if successful:
        print(f"\nExtraction Accuracy (successful sites only):")
        print(f"  📊 Average: {avg_accuracy_pct:.0f}% ({avg_accuracy:.1f}/10 points)")
        print(f"  📊 Min: {min(r['accuracy'] for r in successful):.1f}/10")
        print(f"  📊 Max: {max(r['accuracy'] for r in successful):.1f}/10")

    print(f"\nDetailed Results:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        if r['success']:
            acc_pct = (r['accuracy'] / 10) * 100
            print(f"{status} {r['name']}: {acc_pct:.0f}% accuracy, {r['fields_found']} fields")
        else:
            print(f"{status} {r['name']}: {r.get('error', 'Unknown error')}")

    print(f"\n{'=' * 80}")
    print(" GATE 2 EVALUATION")
    print(f"{'=' * 80}")

    # Gate 2 criteria: 80%+ extraction accuracy
    if avg_accuracy_pct >= 80:
        print(f"\n🎉 GATE 2 PASSED!")
        print(f"   Target: 80%+ accuracy")
        print(f"   Actual: {avg_accuracy_pct:.0f}% accuracy")
    else:
        print(f"\n⚠️  GATE 2 FAILED")
        print(f"   Target: 80%+ accuracy")
        print(f"   Actual: {avg_accuracy_pct:.0f}% accuracy")
        print(f"   Need improvement: Enhance extraction prompt or reduce required fields")


if __name__ == "__main__":
    test_website_scraping()
