from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, PostLike, PostComment, PostImage
from authentication.models import UserProfile


class PostAuthorSerializer(serializers.ModelSerializer):
    """Author info for posts"""
    role = serializers.CharField(source='userprofile.role', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'role']


class PostCommentSerializer(serializers.ModelSerializer):
    """Post comments"""
    author = PostAuthorSerializer(read_only=True)
    
    class Meta:
        model = PostComment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at']


class PostImageSerializer(serializers.ModelSerializer):
    """Post images with post details, counts and comments"""
    title = serializers.CharField(source='post.title', read_only=True)
    content = serializers.CharField(source='post.content', read_only=True)
    likes_count = serializers.IntegerField(source='post.likes_count', read_only=True)
    comments_count = serializers.IntegerField(source='post.comments_count', read_only=True)
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = PostImage
        fields = [
            'id', 'image', 'created_at', 'title', 'content',
            'likes_count', 'comments_count', 'comments'
        ]
    
    def get_comments(self, obj):
        comments = obj.post.comments.all().select_related('author')
        return [{
            'id': comment.id,
            'content': comment.content,
            'author': {
                'id': comment.author.id if comment.author else None,
                'first_name': comment.author.first_name if comment.author else 'Anonymous',
                'last_name': comment.author.last_name if comment.author else 'User'
            } if comment.author else {
                'id': None,
                'first_name': 'Anonymous',
                'last_name': 'User'
            },
            'created_at': comment.created_at
        } for comment in comments]


class PostListSerializer(serializers.ModelSerializer):
    """Post list view"""
    author = PostAuthorSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'images', 'author']


class PostDetailSerializer(serializers.ModelSerializer):
    """Detailed post view"""
    author = PostAuthorSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'images', 'author']


class PostCreateSerializer(serializers.ModelSerializer):
    """Create new post"""
    author = PostAuthorSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'post_type', 'author']
        read_only_fields = ['id', 'author']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostCommentCreateSerializer(serializers.ModelSerializer):
    """Create comment"""
    
    class Meta:
        model = PostComment
        fields = ['content']
    
    def create(self, validated_data):
        # Allow anonymous comments
        user = self.context['request'].user
        validated_data['author'] = user if user.is_authenticated else None
        validated_data['post'] = self.context['post']
        return super().create(validated_data)