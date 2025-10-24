"""
End-to-End Integration Tests for F-002 Nora AI Onboarding Agent

Tests the complete onboarding flow from welcome → conversation → hotel generation.
"""

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from apps.core.models import Organization
from apps.staff.models import Staff
from apps.hotels.models import Hotel
from apps.ai_agent.models import NoraContext

User = get_user_model()


@pytest.mark.django_db
class TestOnboardingIntegration:
    """End-to-end onboarding flow tests"""

    def setup_method(self):
        """Set up test client and user"""
        self.client = Client()

        # Create user
        self.user = User.objects.create_user(
            username='testowner',
            email='owner@testhotel.com',
            password='testpass123'
        )

        # Create organization
        self.org = Organization.objects.create(
            name='Test Hotel Inc',
            slug='test-hotel-inc'
        )

        # Create staff relationship
        from django.utils import timezone
        Staff.objects.create(
            user=self.user,
            organization=self.org,
            role='owner',
            department='Management',
            hired_at=timezone.now().date()
        )

        # Log in
        self.client.login(username='testowner', password='testpass123')

    def test_welcome_page_loads(self):
        """Test that welcome page renders correctly"""
        response = self.client.get('/nora/welcome/')

        assert response.status_code == 200
        assert b'Meet Nora' in response.content
        assert b'Play Me First' in response.content
        assert b"Let's Go, Nora!" in response.content

    def test_start_onboarding_creates_context(self):
        """Test that starting onboarding creates NoraContext"""
        # Ensure no context exists
        assert NoraContext.objects.filter(user=self.user).count() == 0

        # Start onboarding
        response = self.client.post('/nora/api/start-onboarding/')

        assert response.status_code == 200

        # Verify context created
        context = NoraContext.objects.get(user=self.user)
        assert context.active_task == 'onboarding'
        # task_state may be empty on creation - just verify it exists
        assert isinstance(context.task_state, dict)

    def test_chat_page_loads_after_start(self):
        """Test that chat page is accessible after starting onboarding"""
        # Start onboarding first
        self.client.post('/nora/api/start-onboarding/')

        # Access chat
        response = self.client.get('/nora/chat/')

        assert response.status_code == 200
        assert b'Nora AI Assistant' in response.content or b'nora' in response.content.lower()

    @pytest.mark.slow
    def test_full_onboarding_to_hotel_creation(self):
        """
        Test complete flow: welcome → start → data entry → hotel creation

        This is a comprehensive integration test that verifies:
        1. Onboarding initialization
        2. NoraContext creation and state management
        3. Data generation service
        4. Hotel/RoomType/Room record creation
        """
        # 1. Start onboarding
        response = self.client.post('/nora/api/start-onboarding/')
        assert response.status_code == 200

        # 2. Get context
        context = NoraContext.objects.get(user=self.user)

        # 3. Simulate onboarding data collection
        # (In real scenario, this would be done through conversation)
        context.task_state = {
            'state': 'COMPLETE',
            'field_values': {
                # Hotel basics
                'hotel_name': 'Integration Test Hotel',
                'address': '123 Test Street',
                'city': 'Test City',
                'state': 'CA',
                'zip_code': '90210',
                'country': 'United States',
                'phone': '+1-555-TEST',
                'email': 'test@integration.com',
                'timezone': 'America/Los_Angeles',
                'currency': 'USD',

                # Room types
                'num_room_types': 1,
                'room_type_1_name': 'Test Suite',
                'room_type_1_base_price': 150.00,
                'room_type_1_max_occupancy': 2,
                'room_type_1_beds': '1 King',
                'room_type_1_amenities': ['WiFi', 'TV'],
                'room_type_1_quantity': 5,

                'room_number_start': 101
            }
        }
        context.save()

        # 4. Trigger hotel generation
        response = self.client.post('/nora/api/complete-onboarding/')

        # 5. Verify response
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'hotel_id' in data
        assert 'hotel_slug' in data

        # 6. Verify hotel created
        hotel = Hotel.objects.get(id=data['hotel_id'])
        assert hotel.name == 'Integration Test Hotel'
        assert hotel.organization == self.org
        assert hotel.total_rooms == 5

        # 7. Verify room types created
        room_types = hotel.room_types.all()
        assert room_types.count() == 1
        assert room_types.first().name == 'Test Suite'
        assert room_types.first().base_price == 150.00

        # 8. Verify rooms created
        rooms = hotel.rooms.all()
        assert rooms.count() == 5
        room_numbers = sorted([int(r.room_number) for r in rooms])
        assert room_numbers == [101, 102, 103, 104, 105]

        # 9. Verify context updated
        context.refresh_from_db()
        assert context.active_task == 'completed_onboarding'
        assert context.task_state['hotel_id'] == str(hotel.id)

    def test_success_page_after_completion(self):
        """Test that success page displays correctly after onboarding"""
        # Set up completed onboarding
        context, created = NoraContext.objects.get_or_create(
            user=self.user,
            organization=self.org
        )

        # Create a hotel
        hotel = Hotel.objects.create(
            organization=self.org,
            name='Success Test Hotel',
            slug='success-test-hotel',
            type='independent',
            address={'city': 'Test City'},
            contact={'email': 'test@test.com'},
            timezone='America/New_York',
            currency='USD',
            languages=['en'],
            check_in_time='15:00:00',
            check_out_time='11:00:00',
            total_rooms=10
        )

        # Update context with hotel_id
        context.task_state['hotel_id'] = str(hotel.id)
        context.save()

        # Access success page
        response = self.client.get('/nora/success/')

        assert response.status_code == 200
        assert b'Your hotel is live!' in response.content or b'hotel is live' in response.content.lower()
        assert hotel.slug.encode() in response.content

    def test_global_nora_icon_accessible(self):
        """Test that global Nora icon partial exists and can be included"""
        from django.template.loader import get_template

        # Verify template exists
        template = get_template('ai_agent/partials/global_nora_icon.html')
        assert template is not None

        # Render it (should not raise errors)
        rendered = template.render({})
        assert 'nora-fab' in rendered
        assert 'toggleNoraChat' in rendered

    def test_api_message_endpoint(self):
        """Test sending a message to Nora API"""
        # Start onboarding first
        self.client.post('/nora/api/start-onboarding/')

        # Send a test message
        response = self.client.post(
            '/nora/api/message/',
            data={'message': 'Hello Nora'},
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        # Nora should respond with something
        assert len(data['message']) > 0
