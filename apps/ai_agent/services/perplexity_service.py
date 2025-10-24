"""
Perplexity AI Service - Web-Grounded Hotel Research

Uses Perplexity's API to search the web for detailed hotel information,
amenities, unique features, and current details.
"""

import os
import json
from openai import OpenAI
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PerplexityService:
    """
    Service for researching hotels using Perplexity AI.

    Perplexity provides web-grounded responses with real-time information
    about hotels, including amenities, reviews, and unique features.
    """

    def __init__(self):
        """Initialize Perplexity client (uses OpenAI-compatible API)"""
        api_key = os.getenv("PERPLEXITY_API_KEY")

        if not api_key:
            logger.warning("PERPLEXITY_API_KEY not found in environment")
            self.client = None
        else:
            # Perplexity uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )

    def get_hotel_information(
        self,
        hotel_name: str,
        location: Optional[str] = None
    ) -> Dict:
        """
        Research hotel information using Perplexity's web search.

        Args:
            hotel_name: Name of the hotel
            location: Optional location (city, country)

        Returns:
            Dict with hotel information:
            {
                "general_info": "Brief description",
                "amenities": ["amenity1", "amenity2", ...],
                "unique_features": "What makes this hotel special",
                "target_audience": "Who this hotel is for",
                "price_range": "Budget/Mid-range/Luxury",
                "sources": ["url1", "url2", ...]
            }
        """
        if not self.client:
            logger.warning("Perplexity client not initialized")
            return {"error": "Perplexity API not configured"}

        try:
            # Build search query
            query = f"{hotel_name}"
            if location:
                query += f" in {location}"

            # Prompt for structured hotel information
            prompt = f"""Research the hotel "{query}" and provide detailed information in the following JSON format:

{{
    "general_info": "2-3 sentence description of the hotel, its style, and atmosphere",
    "amenities": ["list of key amenities like pool, spa, restaurant, gym, etc."],
    "unique_features": "What makes this hotel special or different from competitors",
    "target_audience": "Who is this hotel best suited for (business travelers, families, couples, luxury seekers, etc.)",
    "price_range": "Budget/Mid-range/Upscale/Luxury",
    "hotel_style": "Boutique/Chain/Resort/Business/Historic/Modern/etc.",
    "notable_facts": "Any interesting facts, awards, or recognition"
}}

Focus on factual, current information. If you can't find specific information, use null."""

            logger.info(f"🔍 Researching hotel with Perplexity: {query}")

            # Call Perplexity API (using sonar model for web search)
            response = self.client.chat.completions.create(
                model="sonar",  # Web-grounded model (new unified Sonar)
                messages=[
                    {
                        "role": "system",
                        "content": "You are a hotel research assistant. Provide accurate, factual information about hotels based on web search results. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Low temperature for factual responses
                max_tokens=1000
            )

            # Parse response (strip markdown code fences if present)
            content = response.choices[0].message.content.strip()

            # Remove markdown code fences if present
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            elif content.startswith('```'):
                content = content[3:]  # Remove ```

            if content.endswith('```'):
                content = content[:-3]  # Remove trailing ```

            content = content.strip()

            result = json.loads(content)

            logger.info(f"✅ Perplexity research complete for {hotel_name}")
            logger.info(f"   General info: {result.get('general_info', 'N/A')[:100]}...")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Perplexity JSON response: {e}")
            logger.error(f"   Raw response: {response.choices[0].message.content if 'response' in locals() else 'N/A'}")
            return {
                "error": "Failed to parse response",
                "raw_response": response.choices[0].message.content if 'response' in locals() else None
            }
        except Exception as e:
            logger.error(f"❌ Perplexity API error: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def research_hotel(
        self,
        hotel_name: str,
        city: str,
        state: str = None
    ) -> Dict:
        """
        Comprehensive hotel research for F-002.3 AI-First Onboarding.

        This is the primary method for auto-discovery of hotel data.

        Args:
            hotel_name: Hotel name (e.g., "Inn 32")
            city: City (e.g., "Woodstock")
            state: State code (e.g., "NH")

        Returns:
            {
                "description": "Full 2-3 paragraph hotel description",
                "amenities": ["WiFi", "Pool", "Parking", ...],
                "room_types": [
                    {
                        "name": "Standard Queen",
                        "beds": "1 Queen",
                        "capacity": 2,
                        "description": "Basic room description"
                    },
                    ...
                ],
                "website": "https://...",
                "address": "Full street address",
                "phone": "(603) 555-1234",
                "total_rooms": 17,
                "check_in_time": "3:00 PM",
                "check_out_time": "11:00 AM",
                "policies": {
                    "cancellation": "...",
                    "payment": "..."
                },
                "confidence": 0.85,
                "_source": "perplexity"
            }
        """
        if not self.client:
            logger.warning("Perplexity client not initialized")
            return {"error": "Perplexity API not configured", "confidence": 0.0}

        try:
            # Build location string
            location = f"{city}, {state}" if state else city
            query = f"{hotel_name} in {location}"

            # Comprehensive research prompt
            prompt = f"""Research the hotel "{hotel_name}" in {location} and provide COMPLETE information.

Search the web thoroughly and extract:

1. **Description**: Write a detailed 2-3 paragraph description covering:
   - Hotel style and atmosphere
   - Location advantages
   - Target audience
   - What makes it special

2. **Room Types**: List ALL room categories with:
   - Exact room type name (e.g., "Standard Queen", "Deluxe King")
   - Bed configuration (e.g., "1 Queen", "2 Twins", "1 King")
   - Maximum capacity (number of guests)
   - Brief description of the room

3. **Amenities**: Complete list including:
   - Property amenities (pool, gym, spa, restaurant, bar, parking)
   - Room amenities (WiFi, TV, coffee maker)
   - Services (breakfast, room service, concierge)

4. **Contact & Logistics**:
   - Full street address with zip code
   - Phone number
   - Website URL
   - Total number of rooms/units
   - Check-in time
   - Check-out time

5. **Policies**:
   - Cancellation policy
   - Payment policy
   - Pet policy (if applicable)

Respond in this EXACT JSON format:
{{
  "description": "Multi-paragraph description...",
  "amenities": ["WiFi", "Pool", "Parking", "Restaurant", ...],
  "room_types": [
    {{
      "name": "Standard Queen",
      "beds": "1 Queen",
      "capacity": 2,
      "description": "Cozy room with..."
    }}
  ],
  "website": "https://...",
  "address": "123 Main St, City, ST 12345",
  "phone": "(xxx) xxx-xxxx",
  "total_rooms": 17,
  "check_in_time": "3:00 PM",
  "check_out_time": "11:00 AM",
  "policies": {{
    "cancellation": "...",
    "payment": "..."
  }}
}}

IMPORTANT: Use null for fields you cannot find. Be thorough - search multiple sources."""

            logger.info(f"🔍 Comprehensive research: {query}")

            # Call Perplexity with sonar model
            response = self.client.chat.completions.create(
                model="sonar",  # Web-grounded search
                messages=[
                    {
                        "role": "system",
                        "content": "You are a hotel research specialist. Search the web thoroughly and provide accurate, comprehensive information in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Very low for factual data
                max_tokens=2500
            )

            # Parse response
            content = response.choices[0].message.content.strip()

            # Remove markdown code fences
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]

            content = content.strip()
            result = json.loads(content)

            # Calculate confidence based on data completeness
            confidence = self._calculate_confidence(result)
            result['confidence'] = confidence
            result['_source'] = 'perplexity'

            # Log results
            amenities = result.get('amenities') or []
            room_types = result.get('room_types') or []

            logger.info(f"✅ Perplexity research complete:")
            logger.info(f"   Hotel: {hotel_name}")
            logger.info(f"   Address: {result.get('address', 'NOT FOUND')}")
            logger.info(f"   Amenities: {len(amenities)} found")
            logger.info(f"   Room types: {len(room_types)} found")
            logger.info(f"   Confidence: {confidence:.0%}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error: {str(e)}")
            if 'response' in locals():
                logger.error(f"   Raw: {response.choices[0].message.content[:200]}")
            return {"error": "Failed to parse response", "confidence": 0.0}

        except Exception as e:
            logger.error(f"❌ Perplexity research failed: {str(e)}", exc_info=True)
            return {"error": str(e), "confidence": 0.0}

    def _calculate_confidence(self, data: Dict) -> float:
        """
        Calculate confidence score based on data completeness.

        Returns 0.0 to 1.0
        """
        score = 0.0

        # Critical fields (30 points each)
        if data.get('address'):
            score += 0.30
        if data.get('room_types') and len(data['room_types']) > 0:
            score += 0.30

        # Important fields (10 points each)
        if data.get('description') and len(data['description']) > 50:
            score += 0.10
        if data.get('amenities') and len(data['amenities']) > 3:
            score += 0.10
        if data.get('website'):
            score += 0.10
        if data.get('phone'):
            score += 0.10

        return min(score, 1.0)

    def get_hotel_description(
        self,
        hotel_name: str,
        location: Optional[str] = None,
        target_length: str = "medium"
    ) -> str:
        """
        Get a guest-facing description of the hotel.

        Args:
            hotel_name: Name of the hotel
            location: Optional location
            target_length: "short" (1-2 sentences), "medium" (3-4 sentences), "long" (paragraph)

        Returns:
            Formatted description suitable for guest-facing content
        """
        if not self.client:
            return f"{hotel_name} - A quality hotel providing comfortable accommodations."

        try:
            query = f"{hotel_name}"
            if location:
                query += f" in {location}"

            length_instructions = {
                "short": "1-2 engaging sentences",
                "medium": "3-4 well-crafted sentences",
                "long": "A full paragraph (5-6 sentences)"
            }

            prompt = f"""Write a compelling, guest-facing description for "{query}".

Requirements:
- Length: {length_instructions.get(target_length, 'medium')}
- Tone: Enthusiastic but professional
- Focus: Highlight what makes this hotel special
- Include: Key amenities, atmosphere, location benefits
- Avoid: Generic phrases, over-promises

Write the description as plain text (not JSON)."""

            logger.info(f"📝 Generating description for {hotel_name}")

            response = self.client.chat.completions.create(
                model="sonar",  # Web-grounded model (new unified Sonar)
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert hotel copywriter. Write compelling, accurate descriptions based on web research."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # Slightly higher for creative writing
                max_tokens=500
            )

            description = response.choices[0].message.content.strip()
            logger.info(f"✅ Description generated: {description[:100]}...")

            return description

        except Exception as e:
            logger.error(f"❌ Error generating description: {str(e)}")
            return f"{hotel_name} offers comfortable accommodations and quality service in {location or 'a prime location'}."
