import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile

def clear_company_name():
    try:
        user = User.objects.get(email='jazz62785@gmail.com')
        profile = UserProfile.objects.get(user=user)
        
        # Keep role as company but clear company_name
        profile.company_name = None
        profile.save()
        
        print(f"Role: {profile.role}")
        print(f"Company name: {profile.company_name}")
        print("Company name cleared. You can now add it via profile update.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_company_name()