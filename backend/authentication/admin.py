from django.contrib import admin
from .models import UserProfile, OTP

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_email_verified')
    list_filter = ('is_email_verified', 'role')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'otp_type', 'created_at', 'is_verified')
    list_filter = ('otp_type', 'is_verified', 'created_at')
    search_fields = ('user__email', 'otp_code')
