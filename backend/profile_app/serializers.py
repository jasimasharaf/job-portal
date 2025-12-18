from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    company_name = serializers.CharField(source='user.userprofile.company_name', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['user', 'phone_number', 'address', 'skills', 'education', 'experience', 'profile_image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = args[0] if args else None
        if instance and hasattr(instance, 'user'):
            try:
                from authentication.models import UserProfile
                profile = UserProfile.objects.get(user=instance.user)
                if profile.job_role == 'company':
                    # For companies: only show company_name, address, profile_image
                    allowed_fields = ['user', 'company_name', 'address', 'profile_image']
                    for field_name in list(self.fields.keys()):
                        if field_name not in allowed_fields:
                            self.fields.pop(field_name)
            except:
                pass


class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    company_name = serializers.CharField(required=False)
    
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'skills', 'education', 'experience', 'profile_image', 'first_name', 'last_name', 'email', 'company_name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                from authentication.models import UserProfile
                profile = UserProfile.objects.get(user=request.user)
                if profile.job_role == 'company':
                    # For companies: only company_name, address, profile_image
                    allowed_fields = ['company_name', 'address', 'profile_image', 'first_name', 'last_name', 'email']
                    for field_name in list(self.fields.keys()):
                        if field_name not in allowed_fields:
                            self.fields.pop(field_name)
            except:
                pass
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Handle company_name update for UserProfile
        company_name = validated_data.pop('company_name', None)
        if company_name:
            from authentication.models import UserProfile
            user_profile, created = UserProfile.objects.get_or_create(user=instance.user)
            user_profile.company_name = company_name
            user_profile.save()
        
        # Update user fields
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance