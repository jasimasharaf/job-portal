from django.core.mail import send_mail
from django.conf import settings
from .models import OTP
import random

def generate_otp():
    return f"{random.randint(100000, 999999):06d}"

def send_otp_email(email, otp_code, otp_type='email_verification'):
    if otp_type == 'email_verification':
        subject = 'Email Verification - Job Portal'
        message = f'Your email verification OTP: {otp_code}\n\nThis code expires in 5 minutes.'
    else:
        subject = 'Password Reset - Job Portal'
        message = f'Your password reset OTP: {otp_code}\n\nThis code expires in 5 minutes.'
    
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        return True
    except:
        return False

def create_otp_for_user(user, otp_type='email_verification'):
    OTP.objects.filter(user=user, otp_type=otp_type, is_verified=False).delete()
    return OTP.objects.create(user=user, otp_type=otp_type)