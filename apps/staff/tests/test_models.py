"""
Test suite for Staff model
Following TDD: Write tests first, then implement model
"""

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from datetime import date

from apps.staff.models import Staff
from apps.hotels.tests.factories import HotelFactory


@pytest.mark.django_db
class TestStaffModel:
    """Test suite for Staff model"""

    @pytest.fixture
    def test_user(self):
        """Create a test user"""
        return User.objects.create_user(
            username='teststaff',
            email='staff@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )

    @pytest.fixture
    def test_hotel(self):
        """Create a test hotel"""
        return HotelFactory()

    def test_staff_creation_with_valid_data(self, test_user, test_hotel):
        """Test creating a Staff with all valid required fields"""
        staff = Staff.objects.create(
            user=test_user,
            hotel=test_hotel,
            role='receptionist',
            department='Front Desk',
            shift='morning',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        assert staff.pk is not None
        assert staff.user == test_user
        assert staff.hotel == test_hotel
        assert staff.role == 'receptionist'
        assert staff.department == 'Front Desk'
        assert staff.shift == 'morning'
        assert staff.is_active is True
        assert staff.hired_at == date(2024, 1, 1)

    def test_staff_can_work_at_multiple_hotels(self, test_user):
        """Test that a user can have multiple Staff entries for different hotels"""
        hotel1 = HotelFactory()
        hotel2 = HotelFactory()

        staff1 = Staff.objects.create(
            user=test_user,
            hotel=hotel1,
            role='receptionist',
            department='Front Desk',
            shift='morning',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        staff2 = Staff.objects.create(
            user=test_user,
            hotel=hotel2,
            role='manager',
            department='Management',
            shift='day',
            is_active=True,
            hired_at=date(2024, 2, 1)
        )

        assert Staff.objects.filter(user=test_user).count() == 2
        assert staff1.hotel != staff2.hotel
        assert staff1.role != staff2.role

    def test_staff_unique_together_user_and_hotel(self, test_user, test_hotel):
        """Test that user + hotel combination must be unique"""
        Staff.objects.create(
            user=test_user,
            hotel=test_hotel,
            role='receptionist',
            department='Front Desk',
            shift='morning',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        # Attempt to create another Staff with same user and hotel should fail
        with pytest.raises(IntegrityError):
            Staff.objects.create(
                user=test_user,
                hotel=test_hotel,
                role='manager',  # Different role
                department='Management',
                shift='day',
                is_active=True,
                hired_at=date(2024, 2, 1)
            )

    def test_manager_role_gets_correct_default_permissions(self, test_user, test_hotel):
        """Test that manager role receives correct default permissions"""
        staff = Staff.objects.create(
            user=test_user,
            hotel=test_hotel,
            role='manager',
            department='Management',
            shift='day',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        # Default permissions should be set automatically
        assert staff.permissions is not None
        assert 'reservations' in staff.permissions
        assert staff.permissions['reservations']['can_create'] is True
        assert staff.permissions['reservations']['can_delete'] is True
        assert staff.permissions['settings']['can_edit_hotel'] is True
        assert staff.permissions['settings']['can_manage_staff'] is True
        assert staff.permissions['reports']['can_view_financial'] is True

    def test_receptionist_role_gets_correct_default_permissions(self, test_user, test_hotel):
        """Test that receptionist role receives correct default permissions"""
        staff = Staff.objects.create(
            user=test_user,
            hotel=test_hotel,
            role='receptionist',
            department='Front Desk',
            shift='morning',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        # Receptionist should have limited permissions
        assert staff.permissions is not None
        assert staff.permissions['reservations']['can_create'] is True
        assert staff.permissions['reservations']['can_delete'] is False
        assert staff.permissions['settings']['can_edit_hotel'] is False
        assert staff.permissions['settings']['can_manage_staff'] is False
        assert staff.permissions['reports']['can_view_financial'] is False

    def test_housekeeping_role_gets_correct_default_permissions(self, test_user, test_hotel):
        """Test that housekeeping role receives correct default permissions"""
        staff = Staff.objects.create(
            user=test_user,
            hotel=test_hotel,
            role='housekeeping',
            department='Housekeeping',
            shift='morning',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        # Housekeeping should have very limited permissions
        assert staff.permissions is not None
        assert staff.permissions['reservations']['can_create'] is False
        assert staff.permissions['reservations']['can_edit'] is False
        assert staff.permissions['rooms']['can_edit_status'] is True  # Can update room status
        assert staff.permissions['guests']['can_edit'] is False

    def test_maintenance_role_gets_correct_default_permissions(self, test_user, test_hotel):
        """Test that maintenance role receives correct default permissions"""
        staff = Staff.objects.create(
            user=test_user,
            hotel=test_hotel,
            role='maintenance',
            department='Maintenance',
            shift='afternoon',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        # Maintenance should have room access but no guest info
        assert staff.permissions is not None
        assert staff.permissions['rooms']['can_edit_status'] is True
        assert staff.permissions['guests']['can_view'] is False
        assert staff.permissions['reservations']['can_create'] is False

    def test_is_manager_property(self, test_user, test_hotel):
        """Test is_manager property returns correct value"""
        manager = Staff.objects.create(
            user=test_user,
            hotel=test_hotel,
            role='manager',
            department='Management',
            shift='day',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        assert manager.is_manager is True

        # Create a non-manager
        user2 = User.objects.create_user(username='staff2', email='staff2@example.com', password='pass')
        receptionist = Staff.objects.create(
            user=user2,
            hotel=test_hotel,
            role='receptionist',
            department='Front Desk',
            shift='morning',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        assert receptionist.is_manager is False

    def test_staff_permissions_can_be_customized(self, test_user, test_hotel):
        """Test that default permissions can be overridden with custom permissions"""
        staff = Staff.objects.create(
            user=test_user,
            hotel=test_hotel,
            role='receptionist',
            department='Front Desk',
            shift='morning',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        # Override default permissions
        custom_permissions = staff.permissions.copy()
        custom_permissions['reservations']['can_delete'] = True  # Grant delete permission
        staff.permissions = custom_permissions
        staff.save()

        # Reload from DB
        staff_from_db = Staff.objects.get(pk=staff.pk)
        assert staff_from_db.permissions['reservations']['can_delete'] is True

    def test_staff_string_representation(self, test_user, test_hotel):
        """Test __str__ method returns correct format"""
        staff = Staff.objects.create(
            user=test_user,
            hotel=test_hotel,
            role='manager',
            department='Management',
            shift='day',
            is_active=True,
            hired_at=date(2024, 1, 1)
        )

        expected_str = f"{test_user.get_full_name()} - {test_hotel.name} (manager)"
        assert str(staff) == expected_str
