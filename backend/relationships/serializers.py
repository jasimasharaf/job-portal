from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Follow
from authentication.models import UserProfile


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for follow lists"""
    role = serializers.CharField(source='userprofile.role', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role']


class FollowSerializer(serializers.ModelSerializer):
    """Follow relationship serializer"""
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']


class FollowCreateSerializer(serializers.Serializer):
    """Create follow relationship"""
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
    
    def validate(self, data):
        follower = self.context['request'].user
        following = data['user_id']
        
        # Prevent self-following
        if follower == following:
            raise serializers.ValidationError("You cannot follow yourself")
        
        # Check if already following
        if Follow.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError("You are already following this user")
        
        # Role-based validation
        try:
            follower_profile = UserProfile.objects.get(user=follower)
            following_profile = UserProfile.objects.get(user=following)
            
            # Companies can only follow other companies
            if follower_profile.role == 'company' and following_profile.role != 'company':
                raise serializers.ValidationError("Companies can only follow other companies")
                
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("User profile not found")
        
        return data
    
    def create(self, validated_data):
        follower = self.context['request'].user
        following = validated_data['user_id']
        
        return Follow.objects.create(follower=follower, following=following)


class FollowStatsSerializer(serializers.Serializer):
    """User follow statistics"""
    followers_count = serializers.IntegerField()
    following_count = serializers.IntegerField()
    is_following = serializers.BooleanField()