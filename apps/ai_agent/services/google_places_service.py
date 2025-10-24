"""
Google Places API integration for hotel data enrichment.

Provides:
- Hotel search by name + location
- Detailed place information (address, phone, GPS, photos)
- Timezone inference from coordinates
- Photo downloading

Used by NoraAgent to automatically enrich hotel data during onboarding.
"""

import os
import logging
import requests
import googlemaps
from typing import Dict, Optional, List
from django.conf import settings

logger = logging.getLogger(__name__)


class GooglePlacesService:
    """
    Google Places API integration for hotel data enrichment.

    Capabilities:
    - Search for hotels by name + location
    - Get detailed place information
    - Extract photos
    - Validate addresses
    - Infer timezone from GPS coordinates
    """

    def __init__(self):
        """Initialize Google Places client with API key from settings."""
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")

        if not api_key:
            logger.warning(
                "GOOGLE_PLACES_API_KEY not set. Google Places features will be disabled."
            )
            self.client = None
        else:
            self.client = googlemaps.Client(key=api_key)

    def search_hotel(
        self, hotel_name: str, city: str, state: str = None
    ) -> Optional[Dict]:
        """
        Search for hotel on Google Places.

        Args:
            hotel_name: "Sunset Villa"
            city: "Miami"
            state: "FL" (optional, improves accuracy)

        Returns:
            {
                "place_id": "ChIJ...",
                "name": "Sunset Villa",
                "address": "123 Ocean Drive, Miami, FL 33139",
                "phone": "+1 305-555-1234",
                "website": "https://sunsetvilla.com",
                "location": {"lat": 25.7617, "lng": -80.1918},
                "photos": ["photo_reference_1", "photo_reference_2", ...],
                "rating": 4.5,
                "user_ratings_total": 245,
                "business_status": "OPERATIONAL",
                "types": ["lodging", "hotel"],
                "opening_hours": {...}
            }

            Returns None if:
            - Hotel not found
            - API error
            - Client not initialized
        """
        if not self.client:
            logger.warning("Google Places client not initialized. Skipping search.")
            return None

        # Build search query
        query = f"{hotel_name}, {city}"
        if state:
            query += f", {state}"

        try:
            logger.info(f"Searching Google Places for: {query}")

            # Text search for the hotel
            result = self.client.places(query=query, type="lodging")

            if not result.get("results"):
                logger.info(f"No results found for: {query}")
                return None

            # Get first result (most relevant)
            place = result["results"][0]
            place_id = place["place_id"]

            logger.info(f"Found place_id: {place_id}")

            # Get detailed information
            details = self.client.place(
                place_id=place_id,
                fields=[
                    "name",
                    "formatted_address",
                    "international_phone_number",
                    "website",
                    "geometry",
                    "photo",
                    "rating",
                    "user_ratings_total",
                    "business_status",
                    "type",
                    "opening_hours",
                ],
            )

            place_details = details.get("result", {})

            # Extract photo references
            photos = []
            if place_details.get("photos"):
                photos = [
                    p["photo_reference"]
                    for p in place_details.get("photos", [])[:10]
                ]

            enriched_data = {
                "place_id": place_id,
                "name": place_details.get("name"),
                "address": place_details.get("formatted_address"),
                "phone": place_details.get("international_phone_number"),
                "website": place_details.get("website"),
                "location": place_details.get("geometry", {}).get("location", {}),
                "photos": photos,
                "rating": place_details.get("rating"),
                "user_ratings_total": place_details.get("user_ratings_total"),
                "business_status": place_details.get("business_status"),
                "types": place_details.get("types", []),
                "opening_hours": place_details.get("opening_hours", {}),
            }

            logger.info(
                f"Successfully enriched hotel data: {enriched_data.get('name')} - "
                f"{enriched_data.get('address')}"
            )

            return enriched_data

        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Google Places API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error searching Google Places: {str(e)}", exc_info=True
            )
            return None

    def infer_timezone_from_location(self, lat: float, lng: float) -> str:
        """
        Get timezone from GPS coordinates.

        Args:
            lat: Latitude (e.g., 25.7617)
            lng: Longitude (e.g., -80.1918)

        Returns:
            Timezone ID (e.g., "America/New_York")
            Defaults to "America/New_York" if API fails
        """
        if not self.client:
            logger.warning("Google Places client not initialized. Using default timezone.")
            return "America/New_York"

        try:
            logger.info(f"Looking up timezone for coordinates: {lat}, {lng}")

            result = self.client.timezone(location=(lat, lng))
            timezone_id = result.get("timeZoneId", "America/New_York")

            logger.info(f"Timezone found: {timezone_id}")

            return timezone_id

        except Exception as e:
            logger.error(f"Timezone lookup error: {str(e)}")
            return "America/New_York"  # Sensible default

    def download_photo(self, photo_reference: str, max_width: int = 1200) -> Optional[bytes]:
        """
        Download a photo from Google Places.

        Args:
            photo_reference: Photo reference from search_hotel() results
            max_width: Maximum width in pixels (default 1200)

        Returns:
            Image bytes (JPEG) or None if download fails
        """
        if not self.client:
            logger.warning("Google Places client not initialized. Cannot download photo.")
            return None

        try:
            # Note: googlemaps library doesn't have direct photo method
            # Use raw API call
            api_key = os.getenv("GOOGLE_PLACES_API_KEY")
            url = "https://maps.googleapis.com/maps/api/place/photo"
            params = {
                "photo_reference": photo_reference,
                "maxwidth": max_width,
                "key": api_key,
            }

            logger.info(f"Downloading photo: {photo_reference[:20]}...")

            response = requests.get(url, params=params)
            response.raise_for_status()

            logger.info(f"Photo downloaded successfully ({len(response.content)} bytes)")

            return response.content

        except requests.RequestException as e:
            logger.error(f"Photo download error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading photo: {str(e)}", exc_info=True)
            return None
