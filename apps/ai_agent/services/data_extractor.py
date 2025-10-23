"""
Data Extractor - Website Scraping and Data Extraction

Extracts hotel information from user's own website using:
1. BeautifulSoup for HTML parsing
2. GPT-4o for intelligent data extraction and cleanup
3. Smart defaults based on location data

IMPORTANT: Only scrapes user's own website (ethical boundary)
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
from urllib.parse import urlparse

from .openai_config import get_openai_client, GPT4O_CONFIG


class DataExtractor:
    """
    Extract hotel data from website URLs.

    Usage:
        extractor = DataExtractor()
        data = extractor.extract_from_website("https://example-hotel.com")
    """

    def __init__(self):
        self.client = get_openai_client()

    def extract_from_website(self, url: str) -> Dict:
        """
        Extract hotel data from website URL.

        Args:
            url: Hotel website URL (user's own website)

        Returns:
            Dict with extracted data:
            {
                "hotel_name": str,
                "address": str,
                "city": str,
                "country": str,
                "zip_code": str,
                "phone": str,
                "email": str,
                "description": str,
                "amenities": list,
                "room_types": list,  # Basic room type names
                "confidence": float,  # 0-1, extraction confidence
                "raw_text": str,  # For debugging
            }
        """
        try:
            # Step 1: Fetch and parse HTML
            html_content = self._fetch_html(url)
            if not html_content:
                return {"error": "Could not fetch website", "confidence": 0.0}

            # Step 2: Extract clean text
            clean_text = self._extract_clean_text(html_content)
            if not clean_text or len(clean_text) < 100:
                return {"error": "Website has insufficient content", "confidence": 0.0}

            # Step 3: Use GPT-4o to extract structured data
            extracted_data = self._extract_with_gpt(clean_text, url)

            # Step 4: Add domain info
            extracted_data["source_url"] = url
            extracted_data["domain"] = urlparse(url).netloc

            return extracted_data

        except Exception as e:
            return {
                "error": f"Extraction failed: {str(e)}",
                "confidence": 0.0
            }

    def _fetch_html(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch HTML content from URL.

        Args:
            url: Website URL
            timeout: Request timeout in seconds

        Returns:
            HTML content or None if failed
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            headers = {
                'User-Agent': 'Stayfull Hotel Setup Bot/1.0 (Website data extraction for hotel onboarding)'
            }

            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            return response.text

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _extract_clean_text(self, html_content: str) -> str:
        """
        Extract clean text from HTML.

        Args:
            html_content: Raw HTML

        Returns:
            Clean text content
        """
        soup = BeautifulSoup(html_content, 'lxml')

        # Remove script, style, and other non-content tags
        for element in soup(['script', 'style', 'meta', 'link', 'noscript']):
            element.decompose()

        # Get text
        text = soup.get_text(separator='\n', strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = '\n'.join(lines)

        # Limit to reasonable length for GPT-4o (avoid token limits)
        max_chars = 8000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Content truncated...]"

        return text

    def _extract_with_gpt(self, text: str, url: str) -> Dict:
        """
        Use GPT-4o to extract structured data from website text.

        Args:
            text: Clean website text
            url: Original URL

        Returns:
            Dict with extracted hotel data
        """
        prompt = f"""
You are a data extraction expert. Extract hotel information from this website content.

WEBSITE URL: {url}

WEBSITE CONTENT:
{text}

Extract the following information in JSON format:
{{
    "hotel_name": "Exact hotel name (required)",
    "address": "Street address if found",
    "city": "City name (required)",
    "country": "Country name (required)",
    "zip_code": "Postal/ZIP code if found",
    "phone": "Phone number if found",
    "email": "Contact email if found",
    "description": "Brief hotel description (1-2 sentences)",
    "amenities": ["List of amenities mentioned"],
    "room_types": ["List of room type names mentioned"],
    "confidence": 0.0-1.0 (how confident are you in this extraction?)
}}

RULES:
1. Only extract information that is clearly stated on the website
2. For missing fields, use null
3. Be conservative - don't guess
4. confidence should reflect how clearly the information was stated
5. hotel_name, city, country are required - set confidence to 0 if these are missing

Respond ONLY with valid JSON, no other text.
"""

        try:
            response = self.client.chat.completions.create(
                model=GPT4O_CONFIG["model"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise data extraction assistant. You always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            import json
            extracted = json.loads(response.choices[0].message.content)

            # Ensure required fields exist
            extracted.setdefault("hotel_name", None)
            extracted.setdefault("city", None)
            extracted.setdefault("country", None)
            extracted.setdefault("confidence", 0.0)
            extracted.setdefault("amenities", [])
            extracted.setdefault("room_types", [])

            return extracted

        except Exception as e:
            print(f"GPT extraction error: {e}")
            return {
                "error": f"GPT extraction failed: {str(e)}",
                "confidence": 0.0
            }

    def infer_from_location(self, city: str, country: str, zip_code: Optional[str] = None) -> Dict:
        """
        Infer smart defaults based on location.

        Args:
            city: City name
            country: Country name
            zip_code: Optional postal code

        Returns:
            Dict with location-based defaults:
            {
                "currency": str,
                "timezone": str,
                "language": str,
                "tax_rate": float (estimated),
            }
        """
        # Simple country-based defaults
        # In production, could use Google Places API or similar

        defaults = {
            "currency": "USD",
            "timezone": "America/New_York",
            "language": "en",
            "tax_rate": 0.10,  # 10% default
        }

        # Country-specific overrides
        country_lower = country.lower()

        if "united states" in country_lower or "usa" in country_lower or "us" in country_lower:
            defaults["currency"] = "USD"
            defaults["tax_rate"] = 0.10  # Varies by state, this is just default

        elif "united kingdom" in country_lower or "uk" in country_lower:
            defaults["currency"] = "GBP"
            defaults["timezone"] = "Europe/London"
            defaults["tax_rate"] = 0.20  # VAT

        elif "canada" in country_lower:
            defaults["currency"] = "CAD"
            defaults["timezone"] = "America/Toronto"
            defaults["tax_rate"] = 0.13  # HST/GST varies by province

        elif "australia" in country_lower:
            defaults["currency"] = "AUD"
            defaults["timezone"] = "Australia/Sydney"
            defaults["tax_rate"] = 0.10  # GST

        elif "france" in country_lower:
            defaults["currency"] = "EUR"
            defaults["timezone"] = "Europe/Paris"
            defaults["tax_rate"] = 0.20  # TVA

        elif "germany" in country_lower:
            defaults["currency"] = "EUR"
            defaults["timezone"] = "Europe/Berlin"
            defaults["tax_rate"] = 0.19  # MwSt

        elif "spain" in country_lower:
            defaults["currency"] = "EUR"
            defaults["timezone"] = "Europe/Madrid"
            defaults["tax_rate"] = 0.21  # IVA

        elif "mexico" in country_lower:
            defaults["currency"] = "MXN"
            defaults["timezone"] = "America/Mexico_City"
            defaults["tax_rate"] = 0.16  # IVA

        # Add detected location
        defaults["detected_city"] = city
        defaults["detected_country"] = country

        return defaults
