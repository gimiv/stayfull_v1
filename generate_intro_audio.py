"""
One-time script to generate Nora's intro audio and save it as a static file.

✅ ALREADY GENERATED: The intro audio file exists at:
   apps/ai_agent/static/ai_agent/audio/nora-intro.mp3 (600 KB)

Only run this script again if you:
1. Change the intro message text
2. Want to use a different voice
3. Need to regenerate the audio for any reason

After running, remember to:
   python manage.py collectstatic --noinput
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.ai_agent.services.voice_handler import VoiceHandler

# The intro message
intro_message = """Hi there! I'm Nora, your AI co-worker at Stayfull. I'm here to help you get your hotel online in just 10 minutes. Here's what we'll do together: First, I'll gather your hotel's basic information. Then, we'll set up your rooms and pricing. Finally, I'll help you create professional policies and descriptions. The best part? You can talk to me anytime - whether it's for onboarding, daily operations, or just questions about how things work. Ready to get started? Let's build something amazing together!"""

# Generate audio
print("Generating intro audio...")
voice_handler = VoiceHandler()
audio_bytes = voice_handler.generate_voice(intro_message)

# Save to static directory
output_path = 'apps/ai_agent/static/ai_agent/audio/nora-intro.mp3'
with open(output_path, 'wb') as f:
    f.write(audio_bytes)

print(f"✅ Intro audio saved to: {output_path}")
print(f"   File size: {len(audio_bytes) / 1024:.2f} KB")
