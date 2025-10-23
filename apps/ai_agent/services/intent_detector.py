"""
Intent Detector - Classify User Messages

Determines what the user wants Nora to do based on their message.

Intents:
- PROVIDE_DATA: User is answering a question (providing hotel data)
- ASK_QUESTION: User is asking for clarification
- REQUEST_HELP: User needs assistance
- PROVIDE_URL: User is providing a website URL
- CONFIRM: User is confirming/agreeing
- REJECT: User is disagreeing/declining
- EDIT_REQUEST: User wants to change something
- NAVIGATE: User wants to go to different step
"""

from enum import Enum
from typing import Dict, Tuple
import re
from .openai_config import get_openai_client


class Intent(Enum):
    """User message intents"""
    PROVIDE_DATA = "provide_data"
    ASK_QUESTION = "ask_question"
    REQUEST_HELP = "request_help"
    PROVIDE_URL = "provide_url"
    CONFIRM = "confirm"
    REJECT = "reject"
    EDIT_REQUEST = "edit_request"
    NAVIGATE = "navigate"
    UNCLEAR = "unclear"


class IntentDetector:
    """
    Detect user intent from messages.

    Uses a combination of:
    1. Pattern matching (fast, for obvious cases)
    2. GPT-4o classification (for ambiguous cases)
    """

    # URL regex pattern
    URL_PATTERN = re.compile(
        r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'
        r'(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
    )

    # Confirmation patterns
    CONFIRM_PATTERNS = [
        r'\byes\b', r'\byep\b', r'\byeah\b', r'\bsure\b',
        r'\bok\b', r'\bokay\b', r'\bcorrect\b', r'\bright\b',
        r'\bagree\b', r'\bconfirm\b', r'\bapprove\b',
        r'^✓', r'^👍'
    ]

    # Rejection patterns
    REJECT_PATTERNS = [
        r'\bno\b', r'\bnope\b', r'\bnah\b', r'\bnot\b',
        r'\bwrong\b', r'\bincorrect\b', r'\bdisagree\b',
        r'\bcancel\b', r'\bskip\b',
        r'^✗', r'^❌', r'^👎'
    ]

    # Question patterns
    QUESTION_PATTERNS = [
        r'\?$',  # Ends with ?
        r'\bwhat\b', r'\bwhy\b', r'\bhow\b', r'\bwhen\b',
        r'\bwhere\b', r'\bwho\b', r'\bwhich\b',
        r'\bcan i\b', r'\bcan you\b', r'\bshould i\b'
    ]

    # Edit request patterns
    EDIT_PATTERNS = [
        r'\bchange\b', r'\bedit\b', r'\bupdate\b', r'\bmodify\b',
        r'\bfix\b', r'\bcorrect\b', r'\bredo\b', r'\bgo back\b'
    ]

    # Help request patterns
    HELP_PATTERNS = [
        r'\bhelp\b', r'\bstuck\b', r'\bconfused\b',
        r'\bdon\'t understand\b', r'\bexplain\b'
    ]

    def __init__(self):
        self.client = get_openai_client()

    def detect_intent(
        self,
        message: str,
        context: Dict = None
    ) -> Tuple[Intent, float]:
        """
        Detect user intent from message.

        Args:
            message: User's message text
            context: Optional context:
                - current_state: Current onboarding state
                - last_question: Last question Nora asked
                - pending_field: Field Nora is waiting for

        Returns:
            Tuple of (Intent, confidence 0-1)
        """
        message_lower = message.lower().strip()

        # Fast pattern matching first
        pattern_result = self._pattern_match(message_lower)
        if pattern_result:
            return pattern_result

        # Fall back to GPT-4o for ambiguous cases
        return self._classify_with_gpt(message, context or {})

    def _pattern_match(self, message: str) -> Tuple[Intent, float]:
        """
        Fast pattern-based intent detection.

        Args:
            message: Lowercase message text

        Returns:
            Tuple of (Intent, confidence) or None if no match
        """
        # Check for URL
        if self.URL_PATTERN.search(message):
            return (Intent.PROVIDE_URL, 0.95)

        # Check for confirmation
        for pattern in self.CONFIRM_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return (Intent.CONFIRM, 0.90)

        # Check for rejection
        for pattern in self.REJECT_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return (Intent.REJECT, 0.90)

        # Check for questions
        for pattern in self.QUESTION_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return (Intent.ASK_QUESTION, 0.85)

        # Check for edit requests
        for pattern in self.EDIT_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return (Intent.EDIT_REQUEST, 0.85)

        # Check for help
        for pattern in self.HELP_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return (Intent.REQUEST_HELP, 0.90)

        # No pattern match
        return None

    def _classify_with_gpt(self, message: str, context: Dict) -> Tuple[Intent, float]:
        """
        Use GPT-4o to classify intent for ambiguous messages.

        Args:
            message: User message
            context: Conversation context

        Returns:
            Tuple of (Intent, confidence)
        """
        prompt = f"""
Classify the user's intent from this message.

USER MESSAGE: "{message}"

CONTEXT:
- Current onboarding step: {context.get('current_state', 'unknown')}
- Last question asked: {context.get('last_question', 'none')}
- Waiting for: {context.get('pending_field', 'user response')}

POSSIBLE INTENTS:
1. provide_data - User is providing requested information (hotel name, address, etc.)
2. ask_question - User is asking for clarification or help
3. confirm - User is agreeing/confirming
4. reject - User is disagreeing/declining
5. edit_request - User wants to change something
6. navigate - User wants to go to different step
7. unclear - Cannot determine intent

Respond with JSON:
{{
    "intent": "one of the intents above",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intent classification assistant. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low for consistent classification
                max_tokens=150,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)

            # Map string to enum
            intent_str = result.get("intent", "unclear")
            confidence = result.get("confidence", 0.5)

            try:
                intent = Intent(intent_str)
            except ValueError:
                intent = Intent.UNCLEAR

            return (intent, confidence)

        except Exception as e:
            print(f"GPT classification error: {e}")
            # Default to PROVIDE_DATA for unknown messages
            # (assume user is answering the question)
            return (Intent.PROVIDE_DATA, 0.5)

    def extract_url_from_message(self, message: str) -> str:
        """
        Extract URL from message if present.

        Args:
            message: User message

        Returns:
            URL string or None
        """
        match = self.URL_PATTERN.search(message)
        if match:
            return match.group(0)
        return None
