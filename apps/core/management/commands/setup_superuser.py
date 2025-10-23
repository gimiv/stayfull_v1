"""
Django management command to create superuser for production.
Usage: python manage.py setup_superuser
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = 'Create superuser with default or environment-based credentials'

    def handle(self, *args, **options):
        User = get_user_model()

        # Check if superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            superuser = User.objects.filter(is_superuser=True).first()
            self.stdout.write(self.style.SUCCESS('✅ Superuser already exists!'))
            self.stdout.write(f'   Username: {superuser.username}')
            self.stdout.write(f'   Email: {superuser.email}')
            return

        # Get credentials from environment or use defaults
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@stayfull.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Stayfull2025!')

        # Create superuser
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(self.style.SUCCESS('🎉 Superuser created successfully!'))
        self.stdout.write(f'   Username: {username}')
        self.stdout.write(f'   Email: {email}')
        self.stdout.write(f'   Password: {password}')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('⚠️  IMPORTANT: Change this password immediately after first login!'))
        self.stdout.write('')
        self.stdout.write('🔗 Login at: https://web-production-2765.up.railway.app/admin/')
