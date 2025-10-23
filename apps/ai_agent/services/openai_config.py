"""
OpenAI API configuration for Nora
"""

import os
from openai import OpenAI
from django.conf import settings

# Initialize OpenAI client
client = None


def get_openai_client() -> OpenAI:
    """
    Get or create OpenAI client instance.

    Uses API key from environment variable OPENAI_API_KEY.
    For development, you can use a trial key.
    For production, use the production key provided by the user.
    """
    global client

    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it in your .env file or environment."
            )

        client = OpenAI(api_key=api_key)

    return client


# System prompt for Nora
NORA_SYSTEM_PROMPT = """
You are Nora, an enthusiastic AI co-worker helping hotel owners
set up and manage their properties on Stayfull.

Personality:
- Enthusiastic but professional
- Clear and concise
- Encouraging and supportive
- Never robotic or corporate

Communication Style:
- Short messages (1-3 sentences)
- One question at a time
- Use ✓ for confirmations
- Use emoji sparingly (💳 ❌ ✨)
- "Great!" "Perfect!" "Got it!" for acknowledgments

Your Job:
- Guide users through 10-minute hotel setup
- Extract maximum info from minimum input
- Always show preview of guest-facing content
- Help with any PMS operation they need

Remember:
- User controls DATA, you control PRESENTATION
- Never let users edit AI-formatted guest text
- Always validate business rules
- Be proactive and helpful
"""


# Voice configuration
VOICE_CONFIG = {
    "model": "whisper-1",  # For speech-to-text
    "tts_model": "tts-1",  # For text-to-speech
    "tts_voice": "nova",  # Female, clear, professional
    "tts_speed": 1.0,  # Normal pace
}


# GPT-4o configuration
GPT4O_CONFIG = {
    "model": "gpt-4o",
    "temperature": 0.7,  # Some creativity for content generation
    "max_tokens": 1000,  # Limit response length
}


# Content formatting configuration
CONTENT_CONFIG = {
    "room_description_max_sentences": 4,
    "policy_max_sentences": 2,
    "tone_options": {
        "enthusiastic": "Enthusiastic but professional",
        "professional": "Professional and calm",
        "casual": "Casual and friendly",
    },
    "default_tone": "enthusiastic",
}
