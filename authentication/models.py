from django.db import models
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('employer', 'Employer'),
        ('company', 'Company'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    is_email_verified = models.BooleanField(default=False)
    
    # Employee/Employer fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Company fields
    company_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    company_image = models.ImageField(upload_to='companies/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.role}"

class OTP(models.Model):
    OTP_TYPES = (
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES, default='email_verification')
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = f"{random.randint(100000, 999999):06d}"
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)
    
    def __str__(self):
        return f"{self.user.email} - {self.otp_code} - {self.otp_type}"