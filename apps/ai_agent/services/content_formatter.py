"""
Content Formatter - AI Enhancement of Guest-Facing Text

CRITICAL PATTERN: User controls DATA, AI controls PRESENTATION

User provides:
- Basic room description: "Nice room with view"
- Policy data: {50%, at_booking, on_arrival}

AI generates:
- Enhanced description: "Experience Miami's coastal beauty from your private balcony..."
- Formatted policy: "💳 50% deposit at booking, rest on arrival"

IMPORTANT: Guest-facing text is LOCKED. Users edit structured data only.
"""

from typing import Dict, Optional
from .openai_config import get_openai_client, CONTENT_CONFIG, GPT4O_CONFIG


class ContentFormatter:
    """
    Format user data into polished guest-facing content.

    All formatting is done through GPT-4o to ensure consistent,
    professional tone across all hotels on the platform.
    """

    def __init__(self):
        self.client = get_openai_client()
        self.tone = CONTENT_CONFIG["default_tone"]

    def enhance_room_description(
        self,
        basic_description: str,
        room_type_name: str,
        context: Dict
    ) -> str:
        """
        Transform basic room description into guest-facing content.

        Args:
            basic_description: User's basic input (e.g., "Nice room with view")
            room_type_name: Room type (e.g., "Ocean View Suite")
            context: Additional context:
                - hotel_name: str
                - city: str
                - amenities: list (room amenities)
                - max_occupancy: int

        Returns:
            Enhanced description (3-4 sentences, guest-ready)
        """
        prompt = f"""
Transform this basic room description into polished guest-facing content.

ROOM TYPE: {room_type_name}
BASIC DESCRIPTION: {basic_description}
HOTEL CONTEXT:
- Hotel: {context.get('hotel_name', 'this hotel')}
- Location: {context.get('city', '')}
- Amenities: {', '.join(context.get('amenities', []))}
- Max Occupancy: {context.get('max_occupancy', 2)} guests

TONE: {CONTENT_CONFIG["tone_options"][self.tone]}

REQUIREMENTS:
1. Write {CONTENT_CONFIG["room_description_max_sentences"]} sentences maximum
2. Focus on guest benefits, not just features
3. Be specific and vivid (use sensory details)
4. Include amenities naturally
5. Match the tone: {self.tone}
6. Start with an engaging hook

EXAMPLE INPUT: "Nice room with balcony"
EXAMPLE OUTPUT: "Wake up to ocean breezes on your private balcony overlooking Miami Beach. This spacious suite features modern coastal decor, a king-size bed with premium linens, and a marble bathroom with rain shower. Perfect for couples seeking a romantic getaway, with room for up to 2 guests."

Now write the enhanced description:
"""

        try:
            response = self.client.chat.completions.create(
                model=GPT4O_CONFIG["model"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional hotel copywriter. Write compelling, accurate descriptions that sell rooms without being salesy."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # Some creativity for engaging content
                max_tokens=300
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            # Fallback to basic description if GPT fails
            print(f"Enhancement error: {e}")
            return basic_description

    def format_payment_policy(self, policy_data: Dict) -> str:
        """
        Format payment policy data into guest-facing text.

        Args:
            policy_data: Structured payment policy:
                {
                    "deposit_amount": 50,  # Number
                    "deposit_type": "%",  # "%" or "$"
                    "deposit_timing": "at_booking",  # or "X_days_before"
                    "deposit_days_before": null,  # Only if timing is X_days_before
                    "balance_timing": "on_arrival",  # or "X_days_before"
                    "balance_days_before": null,
                }

        Returns:
            Formatted policy text: "💳 50% deposit at booking, rest on arrival"
        """
        deposit_amount = policy_data.get("deposit_amount", 0)
        deposit_type = policy_data.get("deposit_type", "%")
        deposit_timing = policy_data.get("deposit_timing", "at_booking")
        balance_timing = policy_data.get("balance_timing", "on_arrival")

        # Format deposit amount
        if deposit_type == "%":
            deposit_str = f"{int(deposit_amount)}% deposit"
        else:
            deposit_str = f"${deposit_amount} deposit"

        # Format deposit timing
        if deposit_timing == "at_booking":
            timing_str = "at booking"
        else:
            days = policy_data.get("deposit_days_before", 0)
            timing_str = f"{days} days before arrival"

        # Format balance timing
        if balance_timing == "on_arrival":
            balance_str = "rest on arrival"
        else:
            days = policy_data.get("balance_days_before", 0)
            balance_str = f"rest {days} days before arrival"

        return f"💳 {deposit_str} {timing_str}, {balance_str}"

    def format_cancellation_policy(self, policy_data: Dict) -> str:
        """
        Format cancellation policy into guest-facing text.

        Args:
            policy_data:
                {
                    "free_cancellation_days": 7,  # Days before arrival
                    "penalty_percentage": 100,  # % of total charged
                }

        Returns:
            Formatted policy: "❌ Free cancellation up to 7 days before arrival. After that, 100% of total is charged."
        """
        free_days = policy_data.get("free_cancellation_days", 0)
        penalty = policy_data.get("penalty_percentage", 100)

        if free_days > 0:
            return f"❌ Free cancellation up to {free_days} days before arrival. After that, {int(penalty)}% of total is charged."
        else:
            return f"❌ Non-refundable. {int(penalty)}% charged upon booking."

    def format_checkin_policy(self, checkin_time: str, checkout_time: str) -> str:
        """
        Format check-in/out times into guest-facing text.

        Args:
            checkin_time: Time string (e.g., "15:00", "3:00 PM")
            checkout_time: Time string (e.g., "11:00", "11:00 AM")

        Returns:
            Formatted policy: "🕐 Check-in from 3:00 PM, check-out by 11:00 AM"
        """
        return f"🕐 Check-in from {checkin_time}, check-out by {checkout_time}"

    def format_amenities_list(self, amenities: list) -> str:
        """
        Format amenities list into guest-facing text.

        Args:
            amenities: List of amenity strings

        Returns:
            Formatted list: "✨ Free WiFi • Pool • Fitness Center • Parking"
        """
        if not amenities:
            return ""

        return "✨ " + " • ".join(amenities)

    def enhance_hotel_description(
        self,
        basic_description: str,
        context: Dict
    ) -> str:
        """
        Enhance hotel-level description.

        Args:
            basic_description: Basic hotel description
            context:
                - hotel_name: str
                - city: str
                - country: str
                - amenities: list

        Returns:
            Enhanced description (2-3 paragraphs)
        """
        prompt = f"""
Transform this basic hotel description into engaging guest-facing content.

HOTEL: {context.get('hotel_name', '')}
LOCATION: {context.get('city', '')}, {context.get('country', '')}
BASIC DESCRIPTION: {basic_description}
AMENITIES: {', '.join(context.get('amenities', []))}

TONE: {CONTENT_CONFIG["tone_options"][self.tone]}

REQUIREMENTS:
1. Write 2-3 short paragraphs
2. Lead with what makes this hotel special
3. Describe the guest experience
4. Mention location advantages
5. Weave in amenities naturally
6. Be authentic and specific (no clichés)

EXAMPLE:
"Nestled in the heart of vibrant Miami Beach, our boutique hotel offers a perfect blend of coastal charm and modern luxury. Each morning, wake up to ocean breezes and enjoy breakfast on our sun-drenched terrace.

Designed for both relaxation and adventure, we're just steps from the beach and the city's best restaurants. After a day exploring, unwind by our rooftop pool or retreat to your thoughtfully appointed room.

Whether you're here for romance, family time, or solo exploration, our friendly team is ready to make your Miami experience unforgettable."

Now write the enhanced description:
"""

        try:
            response = self.client.chat.completions.create(
                model=GPT4O_CONFIG["model"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional hotel copywriter. Write authentic, engaging descriptions that connect with guests."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Enhancement error: {e}")
            return basic_description

    def set_tone(self, tone: str):
        """
        Set the tone for content generation.

        Args:
            tone: One of CONTENT_CONFIG["tone_options"] keys
        """
        if tone in CONTENT_CONFIG["tone_options"]:
            self.tone = tone
