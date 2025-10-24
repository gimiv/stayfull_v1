"""
Main Nora Agent service - orchestrates all AI interactions
"""

from typing import Dict, Optional
from django.contrib.auth.models import User
from apps.ai_agent.models import NoraContext
from apps.core.models import Organization
from .openai_config import get_openai_client, NORA_SYSTEM_PROMPT, GPT4O_CONFIG
from .conversation_engine import OnboardingEngine, OnboardingState
from .intent_detector import IntentDetector, Intent
from .data_extractor import DataExtractor
from .content_formatter import ContentFormatter


class NoraAgent:
    """
    Main orchestrator for Nora AI agent.

    Handles:
    - Conversation management
    - Intent detection
    - Route to appropriate feature handler
    - Context persistence
    """

    def __init__(self, user: User, organization: Organization):
        self.user = user
        self.organization = organization
        self.client = get_openai_client()

        # Get or create Nora context
        self.context, created = NoraContext.objects.get_or_create(
            user=user,
            organization=organization
        )

        # Initialize service components
        self.intent_detector = IntentDetector()
        self.data_extractor = DataExtractor()
        self.content_formatter = ContentFormatter()

    def process_message(self, user_message: str) -> Dict:
        """
        Process a user message and return Nora's response.

        Args:
            user_message: User's text input

        Returns:
            {
                "message": "Nora's response text",
                "data": {...},  # Optional structured data
                "action": "...",  # Optional action to take (e.g., "show_preview")
            }
        """

        # Add user message to context
        self.context.add_message(role="user", content=user_message)

        # Check if awaiting address confirmation
        if self.context.task_state.get("_awaiting_address_confirmation"):
            return self._handle_address_confirmation(user_message)

        # Check if we're in onboarding
        if self.context.active_task == "onboarding":
            return self._handle_onboarding_message(user_message)

        # Otherwise, general conversation
        return self._handle_general_message(user_message)

    def _handle_address_confirmation(self, user_message: str) -> Dict:
        """
        Handle user's response to address confirmation.

        If user confirms (yes, correct, that's right, etc.), show Perplexity data.
        If user denies (no, wrong, incorrect), ask for correct address.
        """
        import logging
        logger = logging.getLogger(__name__)

        # Use GPT-4o to detect if this is a confirmation or denial
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are analyzing user responses to determine if they are confirming or denying. Respond with only 'CONFIRM' or 'DENY' or 'UNCLEAR'."
                    },
                    {
                        "role": "user",
                        "content": f"User was asked if an address is correct. They responded: '{user_message}'. Are they confirming (yes/correct/right) or denying (no/wrong/incorrect)?"
                    }
                ],
                temperature=0.1,
                max_tokens=10
            )

            intent = response.choices[0].message.content.strip().upper()
            logger.info(f"Address confirmation intent: {intent}")

            if "CONFIRM" in intent:
                # User confirmed! Clear flag and show Perplexity description
                self.context.task_state["_awaiting_address_confirmation"] = False

                # Get Perplexity data
                perplexity_data = self.context.task_state.get("_perplexity_pending", {})

                # Move Perplexity data from pending to confirmed
                if perplexity_data:
                    self.context.task_state.update({
                        "general_info": perplexity_data.get("general_info"),
                        "amenities": perplexity_data.get("amenities", []),
                        "unique_features": perplexity_data.get("unique_features"),
                        "target_audience": perplexity_data.get("target_audience"),
                        "price_range": perplexity_data.get("price_range"),
                        "hotel_style": perplexity_data.get("hotel_style"),
                        "notable_facts": perplexity_data.get("notable_facts"),
                    })
                    del self.context.task_state["_perplexity_pending"]

                self.context.save()

                # Generate message with Perplexity description
                general_info = perplexity_data.get("general_info", "")
                amenities = perplexity_data.get("amenities", [])
                amenities_str = ", ".join(amenities[:5]) if amenities else "various amenities"

                message = f"Perfect! Based on my research, here's what I found: {general_info}\n\nKey amenities include: {amenities_str}."

                # Check what's missing for hotel basics
                from apps.ai_agent.services.conversation_engine import OnboardingEngine
                engine = OnboardingEngine(self.context.task_state)
                missing = engine.get_missing_fields()

                # Human-friendly field names
                human_friendly = {
                    'contact_email': 'your email address',
                    'phone': 'a phone number',
                    'website': 'your website',
                    'state': 'the state/province',
                    'country': 'the country',
                    'full_address': 'the full address',
                }

                if missing and 'contact_email' in missing:
                    message += f"\n\nLast thing I need for your property info - what's the best email to reach you at?"
                elif missing:
                    missing_friendly = [human_friendly.get(field, field.replace('_', ' ')) for field in missing]
                    message += f"\n\nI still need {', '.join(missing_friendly)}. Can you share those with me?"
                else:
                    message += "\n\nPerfect! Now let's set up your room types. How many different types of rooms do you have?"

                self.context.add_message(role="assistant", content=message)

                return {
                    "message": message,
                    "data": {"perplexity_confirmed": True},
                    "action": None
                }

            elif "DENY" in intent:
                # User denied - ask for correction
                self.context.task_state["_awaiting_address_confirmation"] = False
                self.context.save()

                message = "No worries! Can you give me the correct address?"
                self.context.add_message(role="assistant", content=message)

                return {
                    "message": message,
                    "data": {},
                    "action": None
                }

            else:
                # Unclear - ask again
                message = "I'm not sure - is that address correct? Just let me know yes or no."
                self.context.add_message(role="assistant", content=message)

                return {
                    "message": message,
                    "data": {},
                    "action": None
                }

        except Exception as e:
            logger.error(f"Error handling address confirmation: {str(e)}", exc_info=True)
            # Fallback to general message handling
            return self._handle_general_message(user_message)

    def _handle_onboarding_message(self, user_message: str) -> Dict:
        """
        Handle message during onboarding flow.

        Args:
            user_message: User's message

        Returns:
            Response dict
        """
        try:
            # Initialize onboarding engine with current state
            engine = OnboardingEngine(self.context.task_state)

            # Detect intent
            intent, confidence = self.intent_detector.detect_intent(
                user_message,
                context={
                    "current_state": engine.current_state.value,
                    "pending_field": "hotel_data"
                }
            )

            # Handle based on intent and current state
            if intent == Intent.PROVIDE_URL:
                return self._handle_website_url(user_message, engine)

            elif intent == Intent.PROVIDE_DATA:
                return self._handle_data_provision(user_message, engine)

            elif intent == Intent.ASK_QUESTION:
                return self._handle_question(user_message, engine)

            elif intent == Intent.EDIT_REQUEST:
                return self._handle_edit_request(user_message, engine)

            elif intent == Intent.CONFIRM and engine.current_state == OnboardingState.REVIEW:
                # User confirmed the review! Set the flag and transition to COMPLETE
                engine.update_field("review_confirmed", True)
                next_state, progress = engine.transition_to_next_state()

                # Save the updated state
                self.context.save()

                # Now complete the onboarding
                return self._complete_onboarding()

            else:
                # Unclear or other intent - ask GPT-4o to clarify
                return self._handle_unclear(user_message, engine)

        except Exception as e:
            return {
                "message": "I'm having trouble processing that. Let's try again - what would you like to tell me?",
                "data": {"error": str(e)},
                "action": None
            }

    def _handle_website_url(self, user_message: str, engine: OnboardingEngine) -> Dict:
        """Handle when user provides a website URL"""
        url = self.intent_detector.extract_url_from_message(user_message)

        if not url:
            return {
                "message": "I couldn't find a valid URL in your message. Could you try again?",
                "data": {},
                "action": None
            }

        # Extract data from website
        extracted_data = self.data_extractor.extract_from_website(url)

        if "error" in extracted_data:
            message = f"I had trouble reading that website: {extracted_data['error']}. No worries! Let's do this manually. What's your hotel's name?"
            self.context.add_message(role="assistant", content=message)
            return {
                "message": message,
                "data": {},
                "action": None
            }

        # Success! Save extracted data to task_state
        for key, value in extracted_data.items():
            if value and key != "error":
                engine.update_field(key, value)

        self.context.update_task_state(self.context.task_state)

        # Generate confirmation message
        confidence_pct = int(extracted_data.get("confidence", 0) * 100)
        message = f"Perfect! I found your hotel: {extracted_data.get('hotel_name', 'your hotel')} in {extracted_data.get('city', '')}. "

        if confidence_pct > 80:
            message += "Great! Let me confirm a few details, then we'll move to room types."
        else:
            message += "I got some info, but let's double-check a few things."

        self.context.add_message(role="assistant", content=message)

        return {
            "message": message,
            "data": {
                "extracted": extracted_data,
                "confidence": confidence_pct,
                "state": engine.get_state_summary()
            },
            "action": "show_extracted_data"
        }

    def _handle_data_provision(self, user_message: str, engine: OnboardingEngine) -> Dict:
        """Handle when user is providing data (answering questions)"""
        # Use GPT-4o to extract structured data from message
        missing_fields = engine.get_missing_fields()

        prompt = f"""
Extract hotel information from this user message.

USER MESSAGE: "{user_message}"

CURRENT ONBOARDING STEP: {engine.current_state.value}
MISSING FIELDS: {', '.join(missing_fields)}

Extract any relevant data and return as JSON. Focus especially on the missing fields.

Important:
- For emails: Look for any email address pattern (user@domain.com)
- For phone: Look for any phone number pattern
- For addresses: Extract city, state/province, and country separately
- State codes like "NH", "CA", "NY" are US states, not countries
- If user provides just an email, extract it as contact_email
- If user provides just a phone, extract it as phone
- Always include the field even if it seems short (e.g., just "john@hotel.com")

Return JSON with these possible fields:
{{
    "hotel_name": "name if mentioned or null",
    "city": "city if mentioned or null",
    "state": "state or province if mentioned or null",
    "country": "country if mentioned or null",
    "contact_email": "email if mentioned or null",
    "phone": "phone if mentioned or null",
    "website": "website URL if mentioned or null"
}}

CRITICAL: If the message contains an email address, you MUST extract it as contact_email.
CRITICAL: Do NOT confuse US states (NH, NY, CA, etc.) with countries. Extract them as "state".
CRITICAL: Use null (not "null" string) for missing data.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a precise data extraction assistant. Extract emails and data accurately. Respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            import json
            import logging
            logger = logging.getLogger(__name__)

            extracted = json.loads(response.choices[0].message.content)
            logger.info(f"📧 Extracted data from '{user_message}': {extracted}")

            # Update task_state with extracted data
            updated_count = 0
            updated_fields = []
            for key, value in extracted.items():
                # More robust null checking
                if value is not None and value != "null" and value != "" and str(value).strip():
                    engine.update_field(key, value)
                    updated_count += 1
                    updated_fields.append(f"{key}={value}")
                    logger.info(f"✅ Updated field: {key} = {value}")
                else:
                    logger.info(f"⏭️ Skipped field: {key} (value was: {value})")

            # Auto-infer country if state is a US state and country is missing
            if extracted.get('state') and not self.context.task_state.get('country'):
                us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
                state_value = str(extracted.get('state', '')).upper()

                if state_value in us_states or len(state_value) == 2:  # 2-letter state code
                    engine.update_field('country', 'United States')
                    engine.update_field('country_code', 'US')
                    updated_count += 1
                    logger.info(f"✅ Auto-inferred country: United States (from state: {state_value})")

            self.context.update_task_state(self.context.task_state)
            logger.info(f"💾 Saved {updated_count} fields: {', '.join(updated_fields) if updated_fields else 'none'}")

            # Check if state is complete
            if engine.is_state_complete(engine.current_state):
                # Move to next state
                next_state, progress = engine.transition_to_next_state()
                self.context.update_task_state(self.context.task_state)
                logger.info(f"🎉 State complete! Moving to: {next_state.value} ({progress}%)")

                message = f"Perfect! ✓ {progress}% complete. "

                if next_state == OnboardingState.ROOM_TYPES:
                    message += "Now let's set up your room types. How many different types of rooms do you have?"
                elif next_state == OnboardingState.POLICIES:
                    message += "Nice! Now for your policies. What's your payment policy? (e.g., 50% deposit at booking)"
                elif next_state == OnboardingState.REVIEW:
                    message += "Almost done! Let me show you a preview of everything."
                elif next_state == OnboardingState.COMPLETE:
                    return self._complete_onboarding()

                self.context.add_message(role="assistant", content=message)

                return {
                    "message": message,
                    "data": {"state": next_state.value, "progress": progress},
                    "action": "update_progress"
                }
            else:
                # Still missing fields in current state
                missing = engine.get_missing_fields()
                logger.warning(f"⚠️ Still missing fields: {missing}")

                # Convert technical field names to human-friendly names
                human_friendly = {
                    'contact_email': 'your email address',
                    'hotel_name': 'your hotel name',
                    'city': 'the city',
                    'state': 'the state/province',
                    'country': 'the country',
                    'phone': 'a phone number',
                    'website': 'your website',
                    'street_address': 'the street address',
                    'full_address': 'the full address',
                }

                # Convert missing field names
                missing_friendly = [human_friendly.get(field, field.replace('_', ' ')) for field in missing]

                # Give more helpful, conversational feedback
                if updated_count > 0:
                    if len(missing_friendly) == 1:
                        # Special cases for common fields
                        if 'email' in missing_friendly[0]:
                            message = "Perfect! Last thing - what's your email address?"
                        elif 'phone' in missing_friendly[0]:
                            message = "Perfect! Last thing - what's your phone number?"
                        else:
                            message = f"Perfect! One more thing - what's {missing_friendly[0]}?"
                    else:
                        message = f"Great! I still need {' and '.join(missing_friendly) if len(missing_friendly) == 2 else ', '.join(missing_friendly[:-1]) + ', and ' + missing_friendly[-1]}. Can you share those with me?"
                else:
                    if len(missing_friendly) == 1:
                        # Special cases for common fields
                        if 'email' in missing_friendly[0]:
                            message = "What's your email address?"
                        elif 'phone' in missing_friendly[0]:
                            message = "What's your phone number?"
                        else:
                            message = f"What's {missing_friendly[0]}?"
                    else:
                        message = f"I need a few more details: {', '.join(missing_friendly)}. Can you help me with those?"

                self.context.add_message(role="assistant", content=message)

                return {
                    "message": message,
                    "data": {"missing": missing, "updated": updated_count},
                    "action": None
                }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Error in data extraction: {str(e)}", exc_info=True)

            # More specific error message
            missing = engine.get_missing_fields()
            if missing:
                message = f"I couldn't quite get that. I still need: {', '.join(missing)}. Could you try providing that again?"
            else:
                message = "Got it! Let's keep going. What else can you tell me?"

            self.context.add_message(role="assistant", content=message)

            return {
                "message": message,
                "data": {"error": str(e), "missing": missing},
                "action": None
            }

    def _handle_question(self, user_message: str, engine: OnboardingEngine) -> Dict:
        """Handle when user asks a question"""
        return self._handle_general_message(user_message)

    def _handle_edit_request(self, user_message: str, engine: OnboardingEngine) -> Dict:
        """Handle when user wants to edit something"""
        message = "Sure! What would you like to change?"
        self.context.add_message(role="assistant", content=message)

        return {
            "message": message,
            "data": {},
            "action": None
        }

    def _handle_unclear(self, user_message: str, engine: OnboardingEngine) -> Dict:
        """Handle unclear intent - ask GPT-4o to respond"""
        return self._handle_general_message(user_message)

    def _complete_onboarding(self) -> Dict:
        """
        Complete onboarding and generate hotel.

        Generates the hotel directly from the onboarding data.
        """
        from .data_generator import DataGenerator
        from django.utils import timezone

        # Log the completion action WITH the data (before it's cleared)
        self.context.add_action("onboarding_completed", self.context.task_state.copy())

        try:
            # Generate hotel from onboarding data
            generator = DataGenerator(user=self.user, organization=self.organization)
            result = generator.generate_hotel_from_onboarding(self.context)

            if not result['success']:
                error_msg = "I encountered an issue creating your hotel. " + ", ".join(result.get('errors', []))
                return {
                    "message": error_msg,
                    "data": {"error": True, "details": result.get('errors', [])},
                    "action": None
                }

            hotel = result['hotel']

            # Mark onboarding as complete
            self.context.task_state['hotel_id'] = str(hotel.id)
            self.context.task_state['onboarding_completed_at'] = timezone.now().isoformat()
            self.context.task_state['progress_percentage'] = 100
            self.context.save()

            # NOW clear the task (hotel is safely in database)
            self.context.complete_task()

            message = f"🎉 Amazing! {hotel.name} is now live! Created {result['stats']['total_rooms']} rooms across {result['stats']['total_room_types']} room types."

            self.context.add_message(role="assistant", content=message)

            # Return success with hotel info
            return {
                "message": message,
                "data": {
                    "onboarding_complete": True,
                    "hotel_id": str(hotel.id),
                    "hotel_slug": hotel.slug,
                    "hotel_name": hotel.name,
                    "stats": result['stats']
                },
                "action": "redirect_to_success"  # Frontend can redirect to success page
            }

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error completing onboarding: {str(e)}", exc_info=True)

            error_msg = "I encountered an unexpected error creating your hotel. Please try again."
            return {
                "message": error_msg,
                "data": {"error": True, "details": str(e)},
                "action": None
            }

    def _handle_general_message(self, user_message: str) -> Dict:
        """
        Handle general conversation (not onboarding-specific).

        Uses GPT-4o with conversation history.
        """
        # Get recent conversation history
        conversation_history = self.context.get_recent_conversation(limit=10)

        # Build messages for GPT-4o
        messages = [
            {"role": "system", "content": NORA_SYSTEM_PROMPT}
        ]

        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        try:
            # Call GPT-4o
            response = self.client.chat.completions.create(
                model=GPT4O_CONFIG["model"],
                messages=messages,
                temperature=GPT4O_CONFIG["temperature"],
                max_tokens=GPT4O_CONFIG["max_tokens"]
            )

            assistant_message = response.choices[0].message.content

            # Save assistant's response to context
            self.context.add_message(role="assistant", content=assistant_message)

            return {
                "message": assistant_message,
                "data": {},
                "action": None
            }

        except Exception as e:
            # Log error and return fallback message
            error_message = "I'm having trouble connecting right now. Your progress is saved - let's continue in a moment."
            return {
                "message": error_message,
                "data": {"error": str(e)},
                "action": "show_error"
            }

    def start_onboarding(self) -> Dict:
        """
        Start the onboarding process.

        Returns initial greeting and first question.
        """
        self.context.set_active_task(
            task="onboarding",
            initial_state={"step": "hotel_basics", "progress_percentage": 0}
        )

        initial_message = (
            "Let's get you going! Can you tell me what the name of your hotel is and what city it's located in?"
        )

        self.context.add_message(role="assistant", content=initial_message)

        return {
            "message": initial_message,
            "data": {"step": "hotel_basics", "progress": 0},
            "action": "show_progress"
        }

    def get_context_summary(self) -> Dict:
        """Get summary of current context (for debugging/monitoring)"""
        return {
            "user": self.user.email,
            "organization": self.organization.name,
            "active_task": self.context.active_task,
            "task_state": self.context.task_state,
            "message_count": len(self.context.conversation_history),
            "last_interaction": self.context.last_interaction_at.isoformat() if self.context.last_interaction_at else None
        }
