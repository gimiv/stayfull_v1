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

    def infer_smart_defaults(self, country: str, state: str = None, city: str = None) -> Dict:
        """
        Infer currency, tax rate, language from location with state-level accuracy.

        This is the enhanced version of infer_from_location() with:
        - US state-specific hotel tax rates (all 50 states)
        - More comprehensive country currency mappings
        - Better defaults

        Args:
            country: Country name or code
            state: State/province code (e.g., "FL", "CA") - optional
            city: City name - optional

        Returns:
            {
                "currency": "USD",
                "tax_rate": 13.0,  # percentage (not decimal)
                "language": "en"
            }
        """
        # Currency mapping (20+ countries)
        currency_map = {
            'United States': 'USD', 'US': 'USD', 'USA': 'USD',
            'Canada': 'CAD',
            'United Kingdom': 'GBP', 'UK': 'GBP',
            'France': 'EUR', 'Germany': 'EUR', 'Spain': 'EUR',
            'Italy': 'EUR', 'Portugal': 'EUR', 'Netherlands': 'EUR',
            'Belgium': 'EUR', 'Austria': 'EUR', 'Greece': 'EUR',
            'Mexico': 'MXN',
            'Australia': 'AUD',
            'Japan': 'JPY',
            'China': 'CNY',
            'India': 'INR',
            'Brazil': 'BRL',
            'South Africa': 'ZAR',
            'Switzerland': 'CHF',
            'Sweden': 'SEK',
            'Norway': 'NOK',
            'Denmark': 'DKK',
        }

        # US state hotel tax rates (state + local average)
        us_tax_rates = {
            'AL': 10.0, 'AK': 5.0, 'AZ': 10.8, 'AR': 12.6, 'CA': 10.5,
            'CO': 10.4, 'CT': 15.0, 'DE': 8.0, 'FL': 13.0, 'GA': 13.0,
            'HI': 14.4, 'ID': 9.0, 'IL': 11.6, 'IN': 12.0, 'IA': 12.0,
            'KS': 11.3, 'KY': 11.3, 'LA': 14.0, 'ME': 9.5, 'MD': 11.5,
            'MA': 11.7, 'MI': 11.0, 'MN': 13.9, 'MS': 12.2, 'MO': 12.5,
            'MT': 7.0, 'NE': 12.5, 'NV': 13.4, 'NH': 9.0, 'NJ': 13.6,
            'NM': 12.9, 'NY': 14.8, 'NC': 12.8, 'ND': 12.0, 'OH': 14.5,
            'OK': 13.5, 'OR': 11.5, 'PA': 11.4, 'RI': 13.0, 'SC': 12.1,
            'SD': 10.0, 'TN': 15.3, 'TX': 17.0, 'UT': 12.3, 'VT': 10.0,
            'VA': 10.8, 'WA': 15.6, 'WV': 12.0, 'WI': 13.4, 'WY': 10.0
        }

        # Normalize country for lookup
        country_normalized = country
        for key in currency_map.keys():
            if key.lower() in country.lower():
                country_normalized = key
                break

        currency = currency_map.get(country_normalized, 'USD')
        tax_rate = 10.0  # Default

        # US-specific: Use state tax rates
        if country_normalized in ['US', 'USA', 'United States'] and state:
            tax_rate = us_tax_rates.get(state.upper(), 10.0)
        elif country_normalized == 'Canada':
            tax_rate = 13.0  # HST average
        elif country_normalized in ['United Kingdom', 'UK']:
            tax_rate = 20.0  # VAT
        elif country_normalized in ['France', 'Germany', 'Spain', 'Italy']:
            tax_rate = 20.0  # VAT average

        return {
            "currency": currency,
            "tax_rate": tax_rate,  # As percentage (13.0 = 13%)
            "language": "en"  # Default English for MVP
        }
