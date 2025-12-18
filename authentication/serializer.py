from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP, UserProfile
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, default='employee')
    company_name = serializers.CharField(max_length=200, required=False)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        role = validated_data.pop('role')
        company_name = validated_data.pop('company_name', None)
        
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            is_active=False
        )
        UserProfile.objects.create(
            user=user, 
            role=role,
            company_name=company_name if company_name else None
        )
        return user
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'confirm_password', 'role', 'company_name')

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='userprofile.role', read_only=True)
    
    # Employee/Employer fields
    phone_number = serializers.CharField(source='userprofile.phone_number', read_only=True)
    skills = serializers.CharField(source='userprofile.skills', read_only=True)
    education = serializers.CharField(source='userprofile.education', read_only=True)
    experience = serializers.CharField(source='userprofile.experience', read_only=True)
    profile_image = serializers.ImageField(source='userprofile.profile_image', read_only=True)
    
    # Company fields
    company_name = serializers.CharField(source='userprofile.company_name', read_only=True)
    address = serializers.CharField(source='userprofile.address', read_only=True)
    company_image = serializers.ImageField(source='userprofile.company_image', read_only=True)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user_role = instance.userprofile.role
        
        if user_role == 'company':
            # Only return company fields
            return {
                'id': data['id'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'role': data['role'],
                'company_name': data['company_name'],
                'address': data['address'],
                'company_image': data['company_image']
            }
        else:
            # Return employee/employer fields
            return {
                'id': data['id'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
                'role': data['role'],
                'phone_number': data['phone_number'],
                'skills': data['skills'],
                'education': data['education'],
                'experience': data['experience'],
                'profile_image': data['profile_image']
            }
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'role', 'phone_number', 'skills', 
                 'education', 'experience', 'profile_image', 'company_name', 'address', 
                 'company_image')

class ProfileUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False)
    skills = serializers.CharField(required=False)
    education = serializers.CharField(required=False)
    experience = serializers.CharField(required=False)
    profile_image = serializers.ImageField(required=False)
    company_name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    company_image = serializers.ImageField(required=False)
    
    def update(self, instance, validated_data):
        # Update User fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        
        # Update UserProfile fields
        profile = instance.userprofile
        for field in ['phone_number', 'skills', 'education', 'experience', 'profile_image', 'company_name', 'address', 'company_image']:
            if field in validated_data:
                setattr(profile, field, validated_data[field])
        profile.save()
        
        return instance
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'skills', 'education', 'experience', 'profile_image', 'company_name', 'address', 'company_image')

class BasicProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='userprofile.role', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'role')

# Keep old serializer for backward compatibility
UserProfileSerializer = BasicProfileSerializer