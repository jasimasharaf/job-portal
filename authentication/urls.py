from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import(
    RegisterAPI, VerifyEmailAPI, ResendOTPAPI, LoginAPI,
    ForgotPasswordAPI, VerifyForgotPasswordAPI, ResetPasswordAPI,
    ChangePasswordAPI, UserProfileAPI
)

urlpatterns = [
    # Registration Flow
    path('register/', RegisterAPI.as_view(), name='register'),
    path('verify-email/', VerifyEmailAPI.as_view(), name='verify_email'),
    path('resend-otp/', ResendOTPAPI.as_view(), name='resend_otp'),
    
    # Login Flow
    path('login/', LoginAPI.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password Management
    path('forgot-password/', ForgotPasswordAPI.as_view(), name='forgot_password'),
    path('verify-forgot-password/', VerifyForgotPasswordAPI.as_view(), name='verify_forgot_password'),
    path('reset-password/', ResetPasswordAPI.as_view(), name='reset_password'),
    path('change-password/', ChangePasswordAPI.as_view(), name='change_password'),
    
    # User Profile
    path('profile/', UserProfileAPI.as_view(), name='profile'),
    path('profile/update/', UserProfileAPI.as_view(), name='profile_update'),
]