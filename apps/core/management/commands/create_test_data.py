"""
Django management command to create test data for F-001 demo.
Usage: python manage.py create_test_data
"""
from django.core.management.base import BaseCommand
from apps.hotels.models import Hotel, RoomType, Room
from apps.guests.models import Guest
from apps.staff.models import Staff
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date


class Command(BaseCommand):
    help = 'Create test data for F-001 Stayfull PMS demo'

    def handle(self, *args, **options):
        self.stdout.write('🏨 Creating test hotel data...\n')

        # 1. Create Test Hotel
        hotel, created = Hotel.objects.get_or_create(
            name='Test Grand Hotel',
            defaults={
                'type': 'independent',
                'total_rooms': 50,
                'check_in_time': '15:00:00',
                'check_out_time': '11:00:00',
                'timezone': 'America/New_York',
                'currency': 'USD',
                'languages': ['en'],
                'address': {
                    'street': '123 Test Street',
                    'city': 'New York',
                    'state': 'NY',
                    'country': 'US',
                    'postal_code': '10001'
                },
                'contact': {
                    'phone': '+1-555-0100',
                    'email': 'info@testgrandhotel.com'
                }
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created hotel: {hotel.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Hotel already exists: {hotel.name}'))

        # 2. Create Room Types
        room_types_data = [
            {
                'name': 'Standard Room',
                'code': 'STD',
                'description': 'Comfortable standard room with queen bed',
                'base_price': Decimal('99.00'),
                'max_occupancy': 2,
                'max_adults': 2,
                'max_children': 0,
                'size_sqm': Decimal('25.0'),
                'bed_configuration': {'beds': [{'type': 'Queen', 'count': 1}]},
                'amenities': ['WiFi', 'TV', 'Air Conditioning']
            },
            {
                'name': 'Deluxe Suite',
                'code': 'DLX',
                'description': 'Spacious suite with king bed and sofa bed',
                'base_price': Decimal('199.00'),
                'max_occupancy': 4,
                'max_adults': 2,
                'max_children': 2,
                'size_sqm': Decimal('45.0'),
                'bed_configuration': {'beds': [{'type': 'King', 'count': 1}, {'type': 'Sofa Bed', 'count': 1}]},
                'amenities': ['WiFi', 'TV', 'Air Conditioning', 'Mini Bar', 'City View']
            }
        ]

        room_types = []
        for rt_data in room_types_data:
            rt, created = RoomType.objects.get_or_create(
                hotel=hotel,
                name=rt_data['name'],
                defaults=rt_data
            )
            room_types.append(rt)

            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created room type: {rt.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  Room type already exists: {rt.name}'))

        # 3. Create Rooms
        rooms_created = 0
        for i, room_type in enumerate(room_types):
            floor = 1 if i == 0 else 2
            for room_num in range(1, 6):  # 5 rooms of each type
                room_number = f'{floor}0{room_num}'

                room, created = Room.objects.get_or_create(
                    hotel=hotel,
                    room_number=room_number,
                    defaults={
                        'room_type': room_type,
                        'floor': floor,
                        'status': 'available',
                        'cleaning_status': 'clean'
                    }
                )

                if created:
                    rooms_created += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Created {rooms_created} rooms'))

        # 4. Create Test Guest (commented out - create manually in Django Admin)
#         # guest, created = Guest.objects.get_or_create(
#             email='john.doe@example.com',
#             defaults={
#                 'first_name': 'John',
#                 'last_name': 'Doe',
#                 'phone': '+1-555-0200',
#                 'date_of_birth': date(1985, 5, 15),
#                 'nationality': 'US',
#                 'id_document_type': 'passport',
#                 'id_document_number': 'AB1234567',  # This will be encrypted
#                 'account_status': 'active',
#                 'loyalty_tier': 'silver',
#                 'loyalty_points': 500,
#                 'preferences': {
#                     'room_type': 'non-smoking',
#                     'floor': 'high',
#                     'special_requests': 'Extra pillows'
#                 }
#             }
#         )
# 
#         if created:
#             self.stdout.write(self.style.SUCCESS(f'✅ Created guest: {guest.full_name}'))
#         else:
#             self.stdout.write(self.style.WARNING(f'⚠️  Guest already exists: {guest.full_name}'))
# 
#         # 5. Create Test Staff
#         staff_user, user_created = User.objects.get_or_create(
#             username='jane.manager',
#             defaults={
#                 'email': 'jane.manager@testgrandhotel.com',
#                 'first_name': 'Jane',
#                 'last_name': 'Manager'
#             }
#         )
# 
#         if user_created:
#             staff_user.set_password('password123')
#             staff_user.save()
# 
#         staff, created = Staff.objects.get_or_create(
#             user=staff_user,
#             hotel=hotel,
#             defaults={
#                 'role': 'manager',
#                 'employee_id': 'MGR001',
#                 'phone': '+1-555-0300',
#                 'is_active': True,
#                 'permissions': ['manage_reservations', 'manage_rooms', 'view_reports']
#             }
#         )
# 
#         if created:
#             self.stdout.write(self.style.SUCCESS(f'✅ Created staff: {staff_user.get_full_name()} ({staff.role})'))
#         else:
#             self.stdout.write(self.style.WARNING(f'⚠️  Staff already exists: {staff_user.get_full_name()}'))
# 
#         # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎉 Test Data Creation Complete!\n'))
        self.stdout.write(f'Hotel: {hotel.name}')
        self.stdout.write(f'Room Types: {RoomType.objects.filter(hotel=hotel).count()}')
        self.stdout.write(f'Rooms: {Room.objects.filter(hotel=hotel).count()}')
        self.stdout.write(f'Guests: {Guest.objects.count()}')
        self.stdout.write(f'Staff: {Staff.objects.filter(hotel=hotel).count()}')
        self.stdout.write('\n✅ You can now test reservations in Django Admin or via API!')
        self.stdout.write('='*60)
