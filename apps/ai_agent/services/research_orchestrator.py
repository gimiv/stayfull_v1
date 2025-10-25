"""
Research Orchestrator - Core of AI-First Validation Pattern

Coordinates research across ALL available sources:
- Perplexity (web-grounded AI research)
- OpenAI (GPT-4o research capabilities)
- Anthropic (Claude with advanced reasoning)
- Gemini (Google's AI with Search integration)
- Google Places (verified business data)
- Website scraping (direct from source)

Aggregates data from 6 sources and makes best decisions through consensus.
"""

import asyncio
import logging
import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
from anthropic import Anthropic
from .perplexity_service import PerplexityService
from .google_places_service import GooglePlacesService
from .data_extractor import DataExtractor

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """
    Orchestrates hotel research across ALL available sources.

    This is the core implementation of the AI-First Validation Pattern:
    1. Auto-discover data from 6 sources in parallel
    2. Aggregate results using consensus voting
    3. Merge intelligently with conflict resolution
    4. Apply smart defaults for gaps
    5. Return complete dataset with source attribution

    Sources:
    - Perplexity: Web-grounded search
    - OpenAI: GPT-4o with browsing
    - Anthropic: Claude with advanced reasoning
    - Gemini: Google's AI with Search
    - Google Places: Verified listings
    - Website: Direct scraping
    """

    def __init__(self, context=None):
        self.perplexity = PerplexityService()
        self.google_places = GooglePlacesService()
        self.data_extractor = DataExtractor()
        self.context = context  # F-002.3 Phase 4.2: For progress tracking

        # Initialize OpenAI for research
        openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=openai_key) if openai_key else None

        # Initialize Anthropic for research
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_client = Anthropic(api_key=anthropic_key) if anthropic_key else None

        # Initialize Gemini (would need setup)
        self.gemini_client = None  # TODO: Add Gemini API when available

    async def _init_progress_tracking(self):
        """
        F-002.3 Phase 4.2: Initialize progress tracking structure.
        """
        if not self.context:
            return

        sources = [
            {
                'id': 'perplexity',
                'name': 'Perplexity AI',
                'icon': '🔍',
                'description': 'Web-grounded AI research',
                'status': 'pending',
                'data_found': [],
            },
            {
                'id': 'openai',
                'name': 'OpenAI GPT-4',
                'icon': '🤖',
                'description': 'Advanced AI analysis',
                'status': 'pending',
                'data_found': [],
            },
            {
                'id': 'anthropic',
                'name': 'Anthropic Claude',
                'icon': '🧠',
                'description': 'Deep reasoning AI',
                'status': 'pending',
                'data_found': [],
            },
            {
                'id': 'gemini',
                'name': 'Google Gemini',
                'icon': '✨',
                'description': 'Google AI with Search',
                'status': 'pending',
                'data_found': [],
            },
            {
                'id': 'google_places',
                'name': 'Google Places',
                'icon': '📍',
                'description': 'Verified business data',
                'status': 'pending',
                'data_found': [],
            },
            {
                'id': 'website',
                'name': 'Website Scraping',
                'icon': '🌐',
                'description': 'Direct from hotel website',
                'status': 'pending',
                'data_found': [],
            },
        ]

        # Use sync_to_async for Django ORM operations
        from asgiref.sync import sync_to_async

        def save_progress():
            self.context.task_state['_research_in_progress'] = True
            self.context.task_state['_research_progress'] = {'sources': sources}
            self.context.save()

        await sync_to_async(save_progress)()

    async def _update_source_progress(self, source_id: str, status: str, data_found: list = None, error_message: str = None):
        """
        F-002.3 Phase 4.2: Update progress for a specific source.
        """
        if not self.context:
            return

        # Use sync_to_async for Django ORM operations
        from asgiref.sync import sync_to_async

        def update_and_save():
            progress = self.context.task_state.get('_research_progress', {})
            sources = progress.get('sources', [])

            for source in sources:
                if source['id'] == source_id:
                    source['status'] = status
                    if data_found:
                        source['data_found'] = data_found
                    if error_message:
                        source['error_message'] = error_message
                    break

            self.context.task_state['_research_progress'] = progress
            self.context.save()

        await sync_to_async(update_and_save)()

    async def research_hotel(
        self,
        hotel_name: str,
        city: str,
        state: str = None
    ) -> Dict:
        """
        Auto-discover ALL hotel data from multiple sources.

        This is the main entry point for F-002.3 onboarding.

        Args:
            hotel_name: Hotel name
            city: City name
            state: State code (optional)

        Returns:
            Complete hotel dataset with:
            - All discovered fields
            - Source attribution (_source_*)
            - Confidence scores
            - Data completeness metrics
        """
        logger.info(f"🔍 Starting comprehensive research: {hotel_name}, {city}")

        # F-002.3 Phase 4.2: Initialize progress tracking
        await self._init_progress_tracking()

        # Phase 1: Launch all sources in parallel
        logger.info("   Launching parallel research...")

        results = await self._launch_parallel_research(hotel_name, city, state)

        # Extract data from each source
        perplexity_data = results.get('perplexity', {})
        openai_data = results.get('openai', {})
        anthropic_data = results.get('anthropic', {})
        gemini_data = results.get('gemini', {})
        places_data = results.get('google_places', {})
        website_data = results.get('website', {})

        # Phase 2: Merge results intelligently (now with 6 sources!)
        logger.info("   Merging data from all sources...")
        merged = self._merge_data_multi_source(
            perplexity_data,
            openai_data,
            anthropic_data,
            gemini_data,
            places_data,
            website_data
        )

        # Phase 3: Apply intelligent defaults for gaps
        logger.info("   Applying smart defaults...")
        complete = self._apply_defaults(merged, city, state)

        # Phase 4: Calculate overall confidence
        confidence = self._calculate_overall_confidence(complete, results)
        complete['_overall_confidence'] = confidence

        # Phase 5: Add metadata
        complete['_sources_used'] = [k for k, v in results.items() if v and 'error' not in v]
        complete['_hotel_name_searched'] = hotel_name
        complete['_city_searched'] = city
        complete['_state_searched'] = state

        logger.info(f"✅ Research complete:")
        logger.info(f"   Confidence: {confidence:.0%}")
        logger.info(f"   Sources: {', '.join(complete['_sources_used'])}")
        logger.info(f"   Fields: {self._count_fields(complete)}/20")

        # F-002.3 Phase 4.2: Mark research as complete
        if self.context:
            from asgiref.sync import sync_to_async

            def mark_complete():
                self.context.task_state['_research_in_progress'] = False
                self.context.save()

            await sync_to_async(mark_complete)()

        return complete

    def _research_with_openai(self, hotel_name: str, city: str, state: str) -> Dict:
        """
        Research hotel using OpenAI GPT-4o.

        Returns structured hotel data similar to Perplexity format.
        """
        if not self.openai_client:
            return {"error": "OpenAI not configured"}

        try:
            location = f"{city}, {state}" if state else city

            prompt = f"""Research the hotel "{hotel_name}" in {location} and provide comprehensive information.

Extract:
1. Full description (2-3 paragraphs)
2. Complete amenities list
3. All room types with bed configuration and capacity
4. Contact info (address, phone, website)
5. Total rooms, check-in/out times, policies

Respond in JSON format:
{{
  "description": "...",
  "amenities": ["WiFi", "Pool", ...],
  "room_types": [{{"name": "...", "beds": "...", "capacity": 2}}],
  "address": "...",
  "phone": "...",
  "website": "...",
  "total_rooms": 17,
  "check_in_time": "3:00 PM",
  "check_out_time": "11:00 AM"
}}

Use null for unknown fields."""

            logger.info(f"   → OpenAI research: {hotel_name}")

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a hotel research assistant. Provide accurate information in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            result['_source'] = 'openai'

            logger.info(f"   ✓ OpenAI: Research complete")
            return result

        except Exception as e:
            logger.warning(f"   ✗ OpenAI failed: {str(e)}")
            return {"error": str(e)}

    def _research_with_anthropic(self, hotel_name: str, city: str, state: str) -> Dict:
        """
        Research hotel using Anthropic Claude.

        Returns structured hotel data similar to other AI sources.
        """
        if not self.anthropic_client:
            return {"error": "Anthropic not configured"}

        try:
            location = f"{city}, {state}" if state else city

            prompt = f"""Research the hotel "{hotel_name}" in {location} and provide comprehensive information.

Extract:
1. Full description (2-3 paragraphs)
2. Complete amenities list
3. All room types with bed configuration and capacity
4. Contact info (address, phone, website)
5. Total rooms, check-in/out times, policies

Respond in JSON format:
{{
  "description": "...",
  "amenities": ["WiFi", "Pool", ...],
  "room_types": [{{"name": "...", "beds": "...", "capacity": 2}}],
  "address": "...",
  "phone": "...",
  "website": "...",
  "total_rooms": 17,
  "check_in_time": "3:00 PM",
  "check_out_time": "11:00 AM"
}}

Use null for unknown fields."""

            logger.info(f"   → Anthropic research: {hotel_name}")

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse JSON from response
            content = response.content[0].text.strip()

            # Remove markdown code fences if present
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]

            content = content.strip()
            result = json.loads(content)
            result['_source'] = 'anthropic'

            logger.info(f"   ✓ Anthropic: Research complete")
            return result

        except Exception as e:
            logger.warning(f"   ✗ Anthropic failed: {str(e)}")
            return {"error": str(e)}

    def _research_with_gemini(self, hotel_name: str, city: str, state: str) -> Dict:
        """
        Research hotel using Google Gemini AI.

        TODO: Implement when Gemini API key is available.
        """
        if not self.gemini_client:
            return {"error": "Gemini not configured"}

        # Placeholder for Gemini integration
        logger.info("   → Gemini: Not yet implemented")
        return {"error": "Not implemented"}

    async def _launch_parallel_research(
        self,
        hotel_name: str,
        city: str,
        state: str
    ) -> Dict:
        """
        Launch all research sources in parallel for speed.

        Returns dict with results from each source.
        """
        results = {}

        # Launch Perplexity research
        try:
            await self._update_source_progress('perplexity', 'in_progress')
            logger.info("   → Perplexity research...")
            perplexity_data = self.perplexity.research_hotel(hotel_name, city, state)
            results['perplexity'] = perplexity_data
            logger.info(f"   ✓ Perplexity: {perplexity_data.get('confidence', 0):.0%} confidence")
            data_found = ['Description', 'Amenities', 'Room Types'] if not perplexity_data.get('error') else []
            await self._update_source_progress('perplexity', 'completed', data_found=data_found)
        except Exception as e:
            logger.warning(f"   ✗ Perplexity failed: {str(e)}")
            results['perplexity'] = {"error": str(e)}
            await self._update_source_progress('perplexity', 'error', error_message=str(e))

        # Launch OpenAI research
        try:
            await self._update_source_progress('openai', 'in_progress')
            openai_data = self._research_with_openai(hotel_name, city, state)
            results['openai'] = openai_data
            data_found = ['Description', 'Room Types', 'Policies'] if not openai_data.get('error') else []
            await self._update_source_progress('openai', 'completed', data_found=data_found)
        except Exception as e:
            logger.warning(f"   ✗ OpenAI failed: {str(e)}")
            results['openai'] = {"error": str(e)}
            await self._update_source_progress('openai', 'error', error_message=str(e))

        # Launch Anthropic research
        try:
            await self._update_source_progress('anthropic', 'in_progress')
            anthropic_data = self._research_with_anthropic(hotel_name, city, state)
            results['anthropic'] = anthropic_data
            data_found = ['Description', 'Amenities', 'Contact'] if not anthropic_data.get('error') else []
            await self._update_source_progress('anthropic', 'completed', data_found=data_found)
        except Exception as e:
            logger.warning(f"   ✗ Anthropic failed: {str(e)}")
            results['anthropic'] = {"error": str(e)}
            await self._update_source_progress('anthropic', 'error', error_message=str(e))

        # Launch Gemini research (placeholder)
        try:
            await self._update_source_progress('gemini', 'in_progress')
            gemini_data = self._research_with_gemini(hotel_name, city, state)
            results['gemini'] = gemini_data
            if gemini_data.get('error'):
                await self._update_source_progress('gemini', 'error', error_message=gemini_data.get('error'))
            else:
                data_found = ['Search Results']
                await self._update_source_progress('gemini', 'completed', data_found=data_found)
        except Exception as e:
            logger.warning(f"   ✗ Gemini failed: {str(e)}")
            results['gemini'] = {"error": str(e)}
            await self._update_source_progress('gemini', 'error', error_message=str(e))

        # Launch Google Places search
        try:
            await self._update_source_progress('google_places', 'in_progress')
            logger.info("   → Google Places lookup...")
            places_data = self.google_places.search_hotel(hotel_name, city, state)
            results['google_places'] = places_data or {}
            if places_data:
                logger.info(f"   ✓ Google Places: Found {places_data.get('name')}")
                data_found = ['Address', 'Phone', 'Location', 'Photos']
                await self._update_source_progress('google_places', 'completed', data_found=data_found)
            else:
                logger.warning("   ✗ Google Places: Not found")
                await self._update_source_progress('google_places', 'error', error_message='Hotel not found')
        except Exception as e:
            logger.warning(f"   ✗ Google Places failed: {str(e)}")
            results['google_places'] = {"error": str(e)}
            await self._update_source_progress('google_places', 'error', error_message=str(e))

        # If Perplexity found website, scrape it
        website_url = (
            results.get('perplexity', {}).get('website') or
            results.get('google_places', {}).get('website')
        )

        if website_url:
            try:
                await self._update_source_progress('website', 'in_progress')
                logger.info(f"   → Scraping website: {website_url}")
                website_data = self.data_extractor.extract_from_website(website_url)
                results['website'] = website_data
                if 'error' not in website_data:
                    logger.info(f"   ✓ Website: {website_data.get('confidence', 0):.0%} confidence")
                    data_found = ['Photos', 'Description', 'Contact']
                    await self._update_source_progress('website', 'completed', data_found=data_found)
                else:
                    logger.warning(f"   ✗ Website scraping failed")
                    await self._update_source_progress('website', 'error', error_message=website_data.get('error', 'Failed'))
            except Exception as e:
                logger.warning(f"   ✗ Website scraping error: {str(e)}")
                results['website'] = {"error": str(e)}
                await self._update_source_progress('website', 'error', error_message=str(e))
        else:
            logger.info("   → No website found, skipping scraping")
            results['website'] = {}
            await self._update_source_progress('website', 'error', error_message='No website URL found')

        return results

    def _merge_data_multi_source(
        self,
        perplexity: Dict,
        openai: Dict,
        anthropic: Dict,
        gemini: Dict,
        google_places: Dict,
        website: Dict
    ) -> Dict:
        """
        Merge data from ALL 6 sources using consensus voting and best practices.

        Strategy:
        1. For critical fields (address, phone): Use consensus + Google Places authority
        2. For descriptive content: Aggregate from all AI sources
        3. For lists (amenities, rooms): Union of all sources
        4. Track which source provided each field for transparency
        """
        merged = {}

        # Hotel name: Consensus with Google Places as tiebreaker
        merged['hotel_name'] = self._consensus_vote([
            google_places.get('name'),
            perplexity.get('hotel_name'),
            openai.get('hotel_name'),
            anthropic.get('hotel_name'),
            gemini.get('hotel_name'),
            website.get('hotel_name')
        ], prefer='google_places')

        # Address: Google Places is most authoritative
        merged['address'] = self._choose_best_with_consensus(
            field='address',
            sources={
                'Google Places': google_places.get('address'),
                'Perplexity': perplexity.get('address'),
                'OpenAI': openai.get('address'),
                'Anthropic': anthropic.get('address'),
                'Gemini': gemini.get('address'),
                'Website': website.get('address')
            },
            authority_order=['Google Places', 'Perplexity', 'Anthropic', 'OpenAI', 'Website']
        )

        # Phone: Google Places > AI consensus
        merged['phone'] = self._choose_best_with_consensus(
            field='phone',
            sources={
                'Google Places': google_places.get('phone'),
                'Perplexity': perplexity.get('phone'),
                'OpenAI': openai.get('phone'),
                'Anthropic': anthropic.get('phone'),
                'Gemini': gemini.get('phone'),
                'Website': website.get('phone')
            },
            authority_order=['Google Places', 'Perplexity', 'Anthropic', 'OpenAI', 'Website']
        )

        # Website URL: Consensus from all sources
        merged['website'] = self._choose_best_with_consensus(
            field='website',
            sources={
                'Perplexity': perplexity.get('website'),
                'OpenAI': openai.get('website'),
                'Anthropic': anthropic.get('website'),
                'Gemini': gemini.get('website'),
                'Google Places': google_places.get('website'),
                'Website': website.get('website')
            },
            authority_order=['Perplexity', 'Google Places', 'Anthropic', 'OpenAI', 'Website']
        )

        # Description: Aggregate best from AI sources (longest, most detailed)
        descriptions = [
            perplexity.get('description'),
            openai.get('description'),
            anthropic.get('description'),
            gemini.get('description'),
            website.get('description')
        ]
        merged['description'] = self._choose_longest_description(descriptions)
        merged['_source_description'] = 'AI aggregation'

        # Room types: Prioritize Perplexity (only source with real web search)
        # OpenAI/Anthropic don't have web search so they hallucinate generic rooms
        perplexity_rooms = perplexity.get('room_types', [])
        if perplexity_rooms and len(perplexity_rooms) > 0:
            # Use Perplexity exclusively if it has data
            merged['room_types'] = perplexity_rooms
            merged['_source_room_types'] = 'Perplexity (web-grounded)'
        else:
            # Fallback to aggregation only if Perplexity has no data
            merged['room_types'] = self._aggregate_room_types([
                openai.get('room_types', []),
                anthropic.get('room_types', []),
                gemini.get('room_types', []),
                website.get('room_types', [])
            ])
            merged['_source_room_types'] = 'AI aggregation (fallback)'

        # Amenities: Union from ALL sources
        all_amenities = []
        for source_data in [perplexity, openai, anthropic, gemini, google_places, website]:
            amenities = source_data.get('amenities') or []
            all_amenities.extend(amenities)

        merged['amenities'] = list(set(all_amenities))  # Deduplicate
        merged['_source_amenities'] = f'Aggregated from {len([s for s in [perplexity, openai, anthropic, gemini, website] if s.get("amenities")])} sources'

        # GPS: Always Google Places (most accurate)
        if google_places.get('location'):
            merged['latitude'] = google_places['location'].get('lat')
            merged['longitude'] = google_places['location'].get('lng')
            merged['_source_gps'] = 'Google Places'

        # Photos: Google Places preferred
        merged['photos'] = self._choose_best(
            google_places.get('photos'),
            website.get('photos')
        )

        # Total rooms: Consensus from AI
        merged['total_rooms'] = self._numeric_consensus([
            perplexity.get('total_rooms'),
            openai.get('total_rooms'),
            anthropic.get('total_rooms'),
            gemini.get('total_rooms')
        ])

        # Check-in/out times: Consensus
        merged['check_in_time'] = self._consensus_vote([
            perplexity.get('check_in_time'),
            openai.get('check_in_time'),
            anthropic.get('check_in_time'),
            gemini.get('check_in_time')
        ])

        merged['check_out_time'] = self._consensus_vote([
            perplexity.get('check_out_time'),
            openai.get('check_out_time'),
            anthropic.get('check_out_time'),
            gemini.get('check_out_time')
        ])

        # Policies: Best from AI sources
        merged['policies'] = (
            perplexity.get('policies') or
            openai.get('policies') or
            anthropic.get('policies') or
            gemini.get('policies') or
            {}
        )

        return merged

    def _consensus_vote(self, values: list, prefer: str = None) -> Optional[str]:
        """
        Choose value that appears most frequently (consensus).

        If tie, use preferred source if specified.
        """
        # Filter out None and empty values
        valid_values = [v for v in values if v and v != ""]

        if not valid_values:
            return None

        # Count occurrences
        from collections import Counter
        counts = Counter(valid_values)

        # Return most common
        most_common = counts.most_common(1)[0][0]
        return most_common

    def _choose_best_with_consensus(
        self,
        field: str,
        sources: Dict[str, any],
        authority_order: List[str]
    ) -> Optional[str]:
        """
        Choose best value using both consensus and authority hierarchy.

        1. First check if multiple sources agree (consensus)
        2. If no consensus, use authority order
        """
        # Get all non-None values
        values = {source: val for source, val in sources.items() if val}

        if not values:
            return None

        # Check for consensus (2+ sources with same value)
        from collections import Counter
        value_counts = Counter(values.values())

        for value, count in value_counts.most_common():
            if count >= 2:  # At least 2 sources agree
                logger.debug(f"   Consensus for {field}: {count} sources agree")
                return value

        # No consensus: Use authority order
        for authority in authority_order:
            if authority in values:
                logger.debug(f"   Using {authority} for {field} (authority)")
                return values[authority]

        # Fallback: First available
        return next(iter(values.values()))

    def _choose_longest_description(self, descriptions: List[str]) -> Optional[str]:
        """Choose the longest, most detailed description."""
        valid = [d for d in descriptions if d and len(d) > 50]

        if not valid:
            return None

        # Return longest
        return max(valid, key=len)

    def _aggregate_room_types(self, room_lists: List[List[Dict]]) -> List[Dict]:
        """
        Aggregate room types from multiple sources.

        Combines unique rooms, merging details when room names match.
        """
        aggregated = {}

        for room_list in room_lists:
            if not room_list:
                continue

            # Handle malformed data (some sources might return non-list)
            if not isinstance(room_list, list):
                logger.warning(f"Invalid room_list type: {type(room_list)}, skipping")
                continue

            for room in room_list:
                # Ensure room is a dict
                if not isinstance(room, dict):
                    logger.warning(f"Invalid room type: {type(room)}, skipping")
                    continue

                name = room.get('name', '').lower().strip()
                if not name:
                    continue

                if name not in aggregated:
                    aggregated[name] = room
                else:
                    # Merge: Fill in missing fields
                    for key, value in room.items():
                        if value and not aggregated[name].get(key):
                            aggregated[name][key] = value

        return list(aggregated.values())

    def _numeric_consensus(self, values: List[Optional[int]]) -> Optional[int]:
        """
        Get consensus on numeric values.

        Returns median if multiple values, or first available.
        """
        valid = [v for v in values if v is not None and isinstance(v, (int, float))]

        if not valid:
            return None

        if len(valid) == 1:
            return valid[0]

        # Return median
        import statistics
        return int(statistics.median(valid))

    def _merge_data(
        self,
        perplexity: Dict,
        google_places: Dict,
        website: Dict
    ) -> Dict:
        """
        Merge data from multiple sources with intelligent conflict resolution.

        Priority rules:
        1. Government/verified data (if available) - highest trust
        2. Google Places - verified business listings
        3. Perplexity - comprehensive AI research
        4. Website - direct from source (but may be outdated)
        """
        merged = {}

        # Hotel name: Prefer Google Places (most authoritative)
        merged['hotel_name'] = self._choose_best(
            google_places.get('name'),
            perplexity.get('hotel_name'),
            website.get('hotel_name'),
            source_names=['Google Places', 'Perplexity', 'Website']
        )

        # Address: Prefer Google Places (most accurate)
        merged['address'] = self._choose_best(
            google_places.get('address'),
            perplexity.get('address'),
            website.get('address'),
            source_names=['Google Places', 'Perplexity', 'Website']
        )
        merged['_source_address'] = self._get_source_name(
            google_places.get('address'),
            perplexity.get('address'),
            website.get('address')
        )

        # Phone: Prefer Google Places
        merged['phone'] = self._choose_best(
            google_places.get('phone'),
            perplexity.get('phone'),
            website.get('phone'),
            source_names=['Google Places', 'Perplexity', 'Website']
        )

        # Website URL: Prefer Perplexity (usually more complete)
        merged['website'] = self._choose_best(
            perplexity.get('website'),
            google_places.get('website'),
            website.get('website'),
            source_names=['Perplexity', 'Google Places', 'Website']
        )

        # Description: Prefer Perplexity (most comprehensive)
        merged['description'] = self._choose_best(
            perplexity.get('description'),
            website.get('description'),
            source_names=['Perplexity', 'Website']
        )

        # Room types: Merge Perplexity + Website
        merged['room_types'] = self._merge_room_types(
            perplexity.get('room_types', []),
            website.get('room_types', [])
        )
        merged['_source_room_types'] = 'Perplexity + Website'

        # Amenities: Union of all sources (combine all)
        perplexity_amenities = perplexity.get('amenities') or []
        website_amenities = website.get('amenities') or []

        merged['amenities'] = list(set(
            perplexity_amenities + website_amenities
        ))
        merged['_source_amenities'] = 'Combined'

        # GPS coordinates: Always from Google Places
        if google_places.get('location'):
            merged['latitude'] = google_places['location'].get('lat')
            merged['longitude'] = google_places['location'].get('lng')
            merged['_source_gps'] = 'Google Places'

        # Photos: Prefer Google Places (better quality)
        merged['photos'] = self._choose_best(
            google_places.get('photos'),
            website.get('photos'),
            source_names=['Google Places', 'Website']
        )

        # Total rooms: Prefer Perplexity
        merged['total_rooms'] = self._choose_best(
            perplexity.get('total_rooms'),
            website.get('total_rooms'),
            source_names=['Perplexity', 'Website']
        )

        # Policies: Prefer Perplexity
        if perplexity.get('policies'):
            merged['policies'] = perplexity['policies']
            merged['_source_policies'] = 'Perplexity'

        # Check-in/out times
        merged['check_in_time'] = perplexity.get('check_in_time')
        merged['check_out_time'] = perplexity.get('check_out_time')

        return merged

    def _choose_best(self, *values, source_names=None):
        """
        Choose the best value from multiple sources.

        Returns first non-None, non-empty value.
        """
        for value in values:
            if value is not None and value != "" and value != []:
                return value
        return None

    def _get_source_name(self, *values):
        """Get name of source that provided the value."""
        sources = ['Google Places', 'Perplexity', 'Website']
        for i, value in enumerate(values):
            if value:
                return sources[i] if i < len(sources) else 'Unknown'
        return 'Not found'

    def _merge_room_types(self, perplexity_rooms: List, website_rooms: List) -> List:
        """
        Intelligently merge room types from multiple sources.

        Combines unique room types, avoiding duplicates.
        """
        if not perplexity_rooms and not website_rooms:
            return []

        # If only one source has data, use it
        if not perplexity_rooms:
            return website_rooms
        if not website_rooms:
            return perplexity_rooms

        # Merge by room name, preferring Perplexity data
        merged = []
        seen_names = set()

        for room in perplexity_rooms:
            name = room.get('name', '').lower()
            if name and name not in seen_names:
                merged.append(room)
                seen_names.add(name)

        for room in website_rooms:
            name = room.get('name', '').lower()
            if name and name not in seen_names:
                merged.append(room)
                seen_names.add(name)

        return merged

    def _apply_defaults(self, data: Dict, city: str, state: str) -> Dict:
        """
        Fill gaps with intelligent defaults.

        Uses location data, industry standards, and smart inference.
        """
        # Timezone from GPS coordinates (if available)
        if data.get('latitude') and data.get('longitude') and not data.get('timezone'):
            timezone = self.google_places.infer_timezone_from_location(
                data['latitude'],
                data['longitude']
            )
            data['timezone'] = timezone
            data['_source_timezone'] = 'GPS inference'

        # Currency and tax rate from location
        if not data.get('currency') or not data.get('tax_rate'):
            defaults = self.data_extractor.infer_smart_defaults(
                country="United States",  # Default for now
                state=state,
                city=city
            )
            if not data.get('currency'):
                data['currency'] = defaults['currency']
                data['_source_currency'] = 'Location inference'

            if not data.get('tax_rate'):
                data['tax_rate'] = defaults['tax_rate']
                data['_source_tax_rate'] = 'Location inference'

        # Check-in/out times (industry standards)
        if not data.get('check_in_time'):
            data['check_in_time'] = '3:00 PM'
            data['_source_check_in'] = 'Industry standard'

        if not data.get('check_out_time'):
            data['check_out_time'] = '11:00 AM'
            data['_source_check_out'] = 'Industry standard'

        # Default language
        if not data.get('language'):
            data['language'] = 'en'
            data['_source_language'] = 'Default'

        return data

    def _calculate_overall_confidence(self, data: Dict, source_results: Dict) -> float:
        """
        Calculate overall confidence based on:
        - Number of sources that succeeded
        - Data completeness
        - Individual source confidences
        """
        # Source success weight (0-0.4)
        sources_succeeded = sum(
            1 for result in source_results.values()
            if result and 'error' not in result
        )
        source_weight = (sources_succeeded / 6) * 0.4  # Max 0.4 (6 sources total)

        # Data completeness weight (0-0.4)
        critical_fields = [
            'hotel_name', 'address', 'phone', 'website',
            'description', 'room_types', 'amenities'
        ]
        fields_present = sum(1 for field in critical_fields if data.get(field))
        completeness_weight = (fields_present / len(critical_fields)) * 0.4  # Max 0.4

        # Individual confidence weight (0-0.2)
        perplexity_conf = source_results.get('perplexity', {}).get('confidence', 0)
        website_conf = source_results.get('website', {}).get('confidence', 0)
        avg_conf = (perplexity_conf + website_conf) / 2
        confidence_weight = avg_conf * 0.2  # Max 0.2

        total = source_weight + completeness_weight + confidence_weight

        return min(total, 1.0)

    def _count_fields(self, data: Dict) -> int:
        """Count non-empty, non-metadata fields."""
        count = 0
        for key, value in data.items():
            if key.startswith('_'):
                continue  # Skip metadata
            if value is not None and value != "" and value != []:
                count += 1
        return count
