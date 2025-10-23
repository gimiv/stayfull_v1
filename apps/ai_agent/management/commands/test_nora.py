"""
Management command to test Nora AI Agent OpenAI connection.

Usage:
    python manage.py test_nora

This will:
1. Check if OPENAI_API_KEY is set
2. Initialize the OpenAI client
3. Send a test message to Nora
4. Display the response
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import Organization
from apps.ai_agent.services.nora_agent import NoraAgent
from apps.ai_agent.services.openai_config import get_openai_client
import os


class Command(BaseCommand):
    help = "Test Nora AI Agent OpenAI connection"

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Testing Nora AI Agent - OpenAI Connection"))
        self.stdout.write("=" * 60 + "\n")

        # Step 1: Check API key
        self.stdout.write("1. Checking OPENAI_API_KEY...")
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            self.stdout.write(self.style.ERROR("   ✗ OPENAI_API_KEY not found in environment"))
            self.stdout.write("\n   Please add your OpenAI API key to .env file:")
            self.stdout.write("   OPENAI_API_KEY=sk-...")
            self.stdout.write("\n   For development, you can use a trial key.")
            return

        self.stdout.write(self.style.SUCCESS(f"   ✓ API key found (starts with: {api_key[:7]}...)"))

        # Step 2: Initialize client
        self.stdout.write("\n2. Initializing OpenAI client...")
        try:
            client = get_openai_client()
            self.stdout.write(self.style.SUCCESS("   ✓ Client initialized successfully"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ Failed to initialize client: {e}"))
            return

        # Step 3: Test basic API call
        self.stdout.write("\n3. Testing basic GPT-4o API call...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello in one short sentence."}
                ],
                max_tokens=50
            )
            message = response.choices[0].message.content
            self.stdout.write(self.style.SUCCESS(f"   ✓ API call successful"))
            self.stdout.write(f"   Response: \"{message}\"")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ API call failed: {e}"))
            return

        # Step 4: Test with Nora Agent
        self.stdout.write("\n4. Testing Nora Agent integration...")

        # Get or create test user and organization
        try:
            user, _ = User.objects.get_or_create(
                username="nora_test_user",
                defaults={
                    "email": "test@nora.local",
                    "first_name": "Test",
                    "last_name": "User"
                }
            )

            org, _ = Organization.objects.get_or_create(
                slug="nora-test-org",
                defaults={
                    "name": "Nora Test Organization",
                    "type": "independent",
                    "contact_email": "test@nora.local"
                }
            )

            self.stdout.write(self.style.SUCCESS("   ✓ Test user and organization ready"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ Failed to create test data: {e}"))
            return

        # Initialize Nora and send test message
        try:
            agent = NoraAgent(user=user, organization=org)
            self.stdout.write(self.style.SUCCESS("   ✓ Nora agent initialized"))

            test_message = "Hi Nora! This is a test message. Please respond briefly."
            self.stdout.write(f"\n   Sending: \"{test_message}\"")

            response = agent.process_message(test_message)

            self.stdout.write(self.style.SUCCESS("   ✓ Message processed successfully"))
            self.stdout.write(f"\n   Nora's response:")
            self.stdout.write(f"   \"{response['message']}\"")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ✗ Nora agent test failed: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc())
            return

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✓ All tests passed! Nora is ready to go."))
        self.stdout.write("=" * 60 + "\n")
