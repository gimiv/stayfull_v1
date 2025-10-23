#!/usr/bin/env python
"""
One-time script to create a superuser for production deployment.
Run this via: railway run python create_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if superuser already exists
if User.objects.filter(is_superuser=True).exists():
    print("✅ Superuser already exists!")
    superuser = User.objects.filter(is_superuser=True).first()
    print(f"   Username: {superuser.username}")
    print(f"   Email: {superuser.email}")
else:
    # Create superuser with default credentials
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@stayfull.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Stayfull2025!')

    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )

    print("🎉 Superuser created successfully!")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print("\n⚠️  IMPORTANT: Change this password immediately after first login!")
    print(f"\n🔗 Login at: https://web-production-2765.up.railway.app/admin/")
