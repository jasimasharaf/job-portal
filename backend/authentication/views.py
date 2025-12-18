from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializer import (
    RegisterSerializer, OTPVerificationSerializer, LoginSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, ChangePasswordSerializer,
    ProfileSerializer, ProfileUpdateSerializer, BasicProfileSerializer
)
from .models import OTP, UserProfile
from .utils import send_otp_email, create_otp_for_user

@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            otp = create_otp_for_user(user, 'email_verification')
            send_otp_email(user.email, otp.otp_code, 'email_verification')
            
            return Response({
                'message': 'Registration successful. Please verify your email with the OTP sent.'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return Response({'error': f'Registration failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@method_decorator(csrf_exempt, name='dispatch')
class VerifyEmailAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = OTPVerificationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            
            user = User.objects.get(email=email)
            otp = OTP.objects.filter(
                user=user, otp_code=otp_code, 
                otp_type='email_verification', is_verified=False
            ).first()
            
            if not otp:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp.is_expired():
                return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
            
            otp.is_verified = True
            otp.save()
            user.is_active = True
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_email_verified = True
            profile.save()
            
            return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Verification failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResendOTPAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.get(email=email)
            profile, created = UserProfile.objects.get_or_create(user=user)
            if profile.is_email_verified:
                return Response({'error': 'Email already verified'}, status=status.HTTP_400_BAD_REQUEST)
            
            otp = create_otp_for_user(user, 'email_verification')
            send_otp_email(user.email, otp.otp_code, 'email_verification')
            
            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Check if user exists
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check password
            if not user.check_password(password):
                return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({'error': 'Please verify your email first'}, status=status.HTTP_401_UNAUTHORIZED)

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': BasicProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Login failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForgotPasswordAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            otp = create_otp_for_user(user, 'password_reset')
            send_otp_email(user.email, otp.otp_code, 'password_reset')
            
            return Response({'message': 'Password reset OTP sent to your email'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyForgotPasswordAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = OTPVerificationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            
            user = User.objects.get(email=email)
            otp = OTP.objects.filter(
                user=user, otp_code=otp_code,
                otp_type='password_reset', is_verified=False
            ).first()
            
            if not otp:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp.is_expired():
                return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message': 'OTP verified. You can now reset your password'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Verification failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ResetPasswordAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = ResetPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            new_password = serializer.validated_data['new_password']
            
            user = User.objects.get(email=email)
            otp = OTP.objects.filter(
                user=user, otp_code=otp_code,
                otp_type='password_reset', is_verified=False
            ).first()
            
            if not otp:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp.is_expired():
                return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            otp.is_verified = True
            otp.save()
            
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Password reset failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            if not user.check_password(old_password):
                return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Password change failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            serializer = BasicProfileSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Failed to get profile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        try:
            serializer = ProfileUpdateSerializer(request.user, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Failed to update profile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        return self.put(request)