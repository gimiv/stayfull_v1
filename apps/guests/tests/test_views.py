"""
Tests for Guests API ViewSets.
"""

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User

from ..models import Guest
from .factories import GuestFactory


class GuestViewSetTest(APITestCase):
    """Tests for GuestViewSet API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.guest = GuestFactory()

    def test_list_guests(self):
        """GET /api/v1/guests/ returns guest list"""
        GuestFactory.create_batch(3)
        response = self.client.get('/api/v1/guests/')

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1

    def test_create_guest(self):
        """POST /api/v1/guests/ creates a guest"""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone': '+1234567890',
            'date_of_birth': '1990-05-15',
            'nationality': 'US',
        }
        response = self.client.post('/api/v1/guests/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['first_name'] == 'Jane'
        assert response.data['email'] == 'jane.smith@example.com'

    def test_search_guests(self):
        """GET /api/v1/guests/?search=email searches guests"""
        guest1 = GuestFactory(first_name='John', email='john@example.com')
        guest2 = GuestFactory(first_name='Jane', email='jane@example.com')

        response = self.client.get('/api/v1/guests/?search=john')

        assert response.status_code == status.HTTP_200_OK
        # Should find john by name or email
        emails = [g['email'] for g in response.data['results']]
        assert 'john@example.com' in emails

    def test_update_guest(self):
        """PATCH /api/v1/guests/{id}/ updates guest"""
        data = {'phone': '+9876543210'}
        response = self.client.patch(f'/api/v1/guests/{self.guest.id}/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone'] == '+9876543210'

    def test_unauthenticated_access_denied(self):
        """Unauthenticated requests are rejected"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/guests/')

        # Can be 401 or 403 depending on authentication configuration
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_retrieve_nonexistent_guest(self):
        """GET /api/v1/guests/{invalid_id}/ returns 404"""
        response = self.client.get('/api/v1/guests/00000000-0000-0000-0000-000000000000/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_guests_pagination(self):
        """GET /api/v1/guests/?page=1 returns paginated results"""
        GuestFactory.create_batch(20)
        response = self.client.get('/api/v1/guests/?page=1')

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert response.data['count'] >= 20

    def test_create_guest_with_duplicate_email(self):
        """POST /api/v1/guests/ with duplicate email returns validation error"""
        existing_guest = GuestFactory(email='duplicate@example.com')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'duplicate@example.com',  # Duplicate
            'phone': '+1234567890',
            'date_of_birth': '1990-01-01',
            'nationality': 'US',
        }
        response = self.client.post('/api/v1/guests/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
