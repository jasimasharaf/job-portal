from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from .models import EmployeeProfile, EmployerProfile, CompanyProfile, Post, PostLike, PostComment


class PostSerializer(serializers.ModelSerializer):
    """Serializer for creating and displaying posts"""
    author_name = serializers.SerializerMethodField()
    author_type = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'post_type', 'content', 'image', 'likes_count', 'comments_count', 
                 'created_at', 'updated_at', 'author_name', 'author_type', 'is_liked']
        read_only_fields = ['id', 'likes_count', 'comments_count', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        if hasattr(obj.profile, 'user'):
            return obj.profile.user.get_full_name() or obj.profile.user.username
        return "Unknown"
    
    def get_author_type(self, obj):
        if isinstance(obj.profile, EmployeeProfile):
            return 'employee'
        elif isinstance(obj.profile, EmployerProfile):
            return 'employer'
        elif isinstance(obj.profile, CompanyProfile):
            return 'company'
        return 'unknown'
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        
        # Get user's profile based on their role
        profile = None
        content_type = None
        
        if hasattr(user, 'userprofile'):
            role = user.userprofile.role
            if role == 'employee' and hasattr(user, 'employee_profile'):
                profile = user.employee_profile
                content_type = ContentType.objects.get_for_model(EmployeeProfile)
            elif role == 'employer' and hasattr(user, 'employer_profile'):
                profile = user.employer_profile
                content_type = ContentType.objects.get_for_model(EmployerProfile)
            elif role == 'company' and hasattr(user, 'company_profile'):
                profile = user.company_profile
                content_type = ContentType.objects.get_for_model(CompanyProfile)
        
        if not profile:
            raise serializers.ValidationError("User profile not found")
        
        validated_data['content_type'] = content_type
        validated_data['object_id'] = profile.id
        
        return super().create(validated_data)


class PostCommentSerializer(serializers.ModelSerializer):
    """Serializer for post comments"""
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PostComment
        fields = ['id', 'content', 'created_at', 'author_name']
        read_only_fields = ['id', 'created_at']
    
    def get_author_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PostLikeSerializer(serializers.ModelSerializer):
    """Serializer for post likes"""
    
    class Meta:
        model = PostLike
        fields = ['id', 'created_at']
        read_only_fields = ['id', 'created_at']