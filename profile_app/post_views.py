from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Post, PostLike, PostComment
from .post_serializers import PostSerializer, PostCommentSerializer, PostLikeSerializer


class PostListCreateView(generics.ListCreateAPIView):
    """List all posts or create a new post"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.all().select_related('content_type').prefetch_related('likes', 'comments').order_by('-created_at')
    
    def perform_create(self, serializer):
        # Auto-assign the post to current user's profile
        user = self.request.user
        from authentication.models import UserProfile
        try:
            profile = UserProfile.objects.get(user=user)
            serializer.save()
        except UserProfile.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("User profile not found")


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a post"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.all()
    
    def perform_update(self, serializer):
        # Check if user owns this post
        post = self.get_object()
        user = self.request.user
        
        # Simple ownership check - if the post was created by this user
        if hasattr(post.profile, 'user') and post.profile.user == user:
            serializer.save()
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only modify your own posts")
    
    def perform_destroy(self, instance):
        # Check if user owns this post
        user = self.request.user
        if hasattr(instance.profile, 'user') and instance.profile.user == user:
            instance.delete()
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own posts")


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def toggle_post_like(request, post_id):
    """Like or unlike a post"""
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
    if request.method == 'POST':
        like, created = PostLike.objects.get_or_create(post=post, user=user)
        if created:
            post.likes_count += 1
            post.save()
            return Response({'message': 'Post liked', 'liked': True}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already liked', 'liked': True}, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        try:
            like = PostLike.objects.get(post=post, user=user)
            like.delete()
            post.likes_count = max(0, post.likes_count - 1)
            post.save()
            return Response({'message': 'Post unliked', 'liked': False}, status=status.HTTP_200_OK)
        except PostLike.DoesNotExist:
            return Response({'message': 'Not liked', 'liked': False}, status=status.HTTP_200_OK)


class PostCommentListCreateView(generics.ListCreateAPIView):
    """List comments for a post or create a new comment"""
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return PostComment.objects.filter(post_id=post_id)
    
    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)
        serializer.save(post=post)
        # Update comment count
        post.comments_count += 1
        post.save()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_feed(request):
    """Get personalized feed for the user"""
    # For now, return all posts ordered by creation date
    # In future, this can be enhanced with following logic
    posts = Post.objects.all().select_related('content_type').prefetch_related('likes', 'comments')
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_posts(request):
    """Get current user's posts"""
    user = request.user
    posts = []
    
    if hasattr(user, 'userprofile'):
        role = user.userprofile.role
        if role == 'employee' and hasattr(user, 'employee_profile'):
            posts = Post.objects.filter(
                content_type__model='employeeprofile',
                object_id=user.employee_profile.id
            )
        elif role == 'employer' and hasattr(user, 'employer_profile'):
            posts = Post.objects.filter(
                content_type__model='employerprofile',
                object_id=user.employer_profile.id
            )
        elif role == 'company' and hasattr(user, 'company_profile'):
            posts = Post.objects.filter(
                content_type__model='companyprofile',
                object_id=user.company_profile.id
            )
    
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)