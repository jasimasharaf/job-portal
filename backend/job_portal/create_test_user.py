#!/usr/bin/env python
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

# Create verified test user
email = "test@example.com"
password = "SecurePass123!"

# Delete existing user
User.objects.filter(email=email).delete()

# Create new user
user = User.objects.create_user(
    username=email,
    email=email,
    first_name="Test",
    last_name="User",
    password=password,
    is_active=True  # Already verified
)

# Create profile
UserProfile.objects.create(
    user=user,
    job_role="Developer",
    is_email_verified=True
)

print(f"Test user created:")
print(f"Email: {email}")
print(f"Password: {password}")
print(f"Status: Active and Verified")