#!/usr/bin/env python
"""
Complete end-to-end onboarding test including database verification
"""

import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth import get_user_model
from apps.ai_agent.services.nora_agent import NoraAgent
from apps.ai_agent.models import NoraContext
from apps.core.models import Organization
from apps.hotels.models import Hotel, RoomType, Room

User = get_user_model()

def print_header(title):
    print(f"\n{'='*80}")
    print(f"{title.center(80)}")
    print(f"{'='*80}\n")

def test_complete_onboarding():
    """Test complete onboarding including database creation"""

    print_header("COMPLETE END-TO-END ONBOARDING TEST")

    # Setup test user
    user = User.objects.get(email='demo@example.com')
    staff = user.staff_positions.first()
    organization = staff.organization

    # Clear existing data
    NoraContext.objects.filter(user=user, organization=organization).delete()
    Hotel.objects.filter(organization=organization).delete()

    print(f"✓ Test user: {user.email}")
    print(f"✓ Organization: {organization.name}\n")

    # Initialize agent
    agent = NoraAgent(user=user, organization=organization)

    # Step 1: Start onboarding
    print_header("STEP 1: Start Onboarding")
    response = agent.start_onboarding()
    print(f"Nora: {response['message']}\n")

    # Step 2: Provide hotel info
    print_header("STEP 2: Hotel Information")
    response = agent.process_message("The Inn at Woodstock, North Woodstock, NH")
    print(f"Nora: {response['message']}\n")

    # Step 3: Email
    response = agent.process_message("info@innwoodstock.com")
    print(f"Nora: {response['message']}\n")

    # Step 4: Room types
    print_header("STEP 3: Room Types")
    response = agent.process_message("We have 3 room types: Standard Queen at $150, Deluxe King at $200, and Suite at $350")
    print(f"Nora: {response['message']}\n")

    # Step 5: Policies
    print_header("STEP 4: Policies")
    response = agent.process_message("50% deposit at booking, rest on arrival")
    print(f"Nora: {response['message']}\n")

    response = agent.process_message("Free cancellation up to 48 hours before check-in")
    print(f"Nora: {response['message']}\n")

    response = agent.process_message("Check-in at 3 PM, check-out at 11 AM")
    print(f"Nora: {response['message']}\n")

    # Check current state
    print_header("CURRENT STATE CHECK")
    print(f"Current step: {agent.context.task_state.get('step')}")
    print(f"Progress: {agent.context.task_state.get('progress_percentage')}%")

    # Check if we need to complete onboarding
    from apps.ai_agent.services.conversation_engine import OnboardingEngine
    engine = OnboardingEngine(agent.context.task_state)

    if engine.current_state.value == 'review':
        print("\n✓ Reached REVIEW state - ready to complete onboarding")

        # Try to complete onboarding
        print_header("STEP 5: Complete Onboarding")

        # Check if there's a complete_onboarding method
        try:
            # Simulate confirmation
            response = agent.process_message("Yes, looks good! Let's complete it.")
            print(f"Nora: {response['message']}\n")
        except Exception as e:
            print(f"Note: {str(e)}")
            print("Attempting to trigger completion manually...\n")

            # Try to call complete onboarding directly via views
            from apps.ai_agent import views
            from django.test import RequestFactory
            from django.contrib.sessions.middleware import SessionMiddleware

            factory = RequestFactory()
            request = factory.post('/nora/api/complete-onboarding/')
            request.user = user

            # Add session
            middleware = SessionMiddleware(lambda x: None)
            middleware.process_request(request)
            request.session.save()

            try:
                response = views.complete_onboarding(request)
                print(f"Complete onboarding response: {response.status_code}")
            except Exception as e:
                print(f"Error completing onboarding: {str(e)}")

    # Step 6: Verify database
    print_header("DATABASE VERIFICATION")

    # Check if hotel was created
    hotels = Hotel.objects.filter(organization=organization)
    print(f"Hotels in database: {hotels.count()}")

    if hotels.exists():
        hotel = hotels.first()
        print(f"\n✓ Hotel Created:")
        print(f"  Name: {hotel.name}")
        print(f"  Slug: {hotel.slug}")
        print(f"  Organization: {hotel.organization.name}")

        # Check room types
        room_types = RoomType.objects.filter(hotel=hotel)
        print(f"\n✓ Room Types: {room_types.count()}")
        for rt in room_types:
            print(f"  - {rt.name}: ${rt.base_price}/night")

        # Check rooms
        rooms = Room.objects.filter(hotel=hotel)
        print(f"\n✓ Rooms: {rooms.count()}")
        for rt in room_types:
            count = rooms.filter(room_type=rt).count()
            print(f"  - {rt.name}: {count} rooms")
    else:
        print("❌ No hotel created yet")
        print("\nThis might be expected if:")
        print("  1. Onboarding requires explicit confirmation")
        print("  2. Complete onboarding endpoint hasn't been called")
        print("  3. Flow is still in review stage")

    # Final state dump
    print_header("FINAL TASK STATE")
    print(json.dumps(agent.context.task_state, indent=2, default=str))

    print_header("TEST COMPLETE")

if __name__ == "__main__":
    test_complete_onboarding()
