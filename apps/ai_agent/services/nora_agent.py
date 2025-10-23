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

        # Check if we're in onboarding
        if self.context.active_task == "onboarding":
            return self._handle_onboarding_message(user_message)

        # Otherwise, general conversation
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
        prompt = f"""
Extract hotel information from this user message.

USER MESSAGE: "{user_message}"

CURRENT ONBOARDING STEP: {engine.current_state.value}
MISSING FIELDS: {', '.join(engine.get_missing_fields())}

Extract any relevant data and return as JSON:
{{
    "hotel_name": "name if mentioned",
    "city": "city if mentioned",
    "country": "country if mentioned",
    "contact_email": "email if mentioned",
    "phone": "phone if mentioned",
    ... any other relevant fields
}}

Only include fields that are clearly stated. Use null for missing data.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant. Respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            import json
            extracted = json.loads(response.choices[0].message.content)

            # Update task_state with extracted data
            updated_count = 0
            for key, value in extracted.items():
                if value and value != "null":
                    engine.update_field(key, value)
                    updated_count += 1

            self.context.update_task_state(self.context.task_state)

            # Check if state is complete
            if engine.is_state_complete(engine.current_state):
                # Move to next state
                next_state, progress = engine.transition_to_next_state()
                self.context.update_task_state(self.context.task_state)

                message = f"Great! ✓ {progress}% complete. "

                if next_state == OnboardingState.ROOM_TYPES:
                    message += "Now let's set up your room types. How many types of rooms do you have?"
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
                message = f"Got it! Still need: {', '.join(missing)}. What else can you tell me?"

                self.context.add_message(role="assistant", content=message)

                return {
                    "message": message,
                    "data": {"missing": missing},
                    "action": None
                }

        except Exception as e:
            return {
                "message": "Got it! Let's keep going. What else can you tell me?",
                "data": {},
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
        """Complete onboarding and generate hotel"""
        self.context.complete_task()
        self.context.add_action("onboarding_completed", self.context.task_state)

        message = "🎉 Amazing! Your hotel is ready. Let's launch it!"

        self.context.add_message(role="assistant", content=message)

        return {
            "message": message,
            "data": {"onboarding_complete": True},
            "action": "complete_onboarding"
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
            "Ready? Let's build your hotel! Do you have a website I can look at? "
            "If you do, I can extract most of the info we need and save us time!"
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
