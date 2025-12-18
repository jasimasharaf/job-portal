from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import Post, PostLike, PostComment, PostImage
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateSerializer,
    PostCommentSerializer, PostCommentCreateSerializer
)
from relationships.models import Follow


class PostCreateAPI(APIView):
    """Create new post with multiple images"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = PostCreateSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                post = serializer.save()
                
                # Handle multiple images
                images = request.FILES.getlist('images')
                for image in images:
                    PostImage.objects.create(post=post, image=image)
                
                return Response({
                    'message': 'Post created successfully',
                    'data': PostDetailSerializer(post, context={'request': request}).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostListAPI(APIView):
    """List posts (feed)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get posts from followed users + own posts
            following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
            feed_users = list(following_users) + [request.user.id]
            
            posts = Post.objects.filter(
                author__in=feed_users,
                is_active=True
            ).select_related('author')
            
            # Filter by post type if provided
            post_type = request.query_params.get('type')
            if post_type:
                posts = posts.filter(post_type=post_type)
            
            serializer = PostListSerializer(posts, many=True, context={'request': request})
            return Response({
                'message': 'Feed retrieved successfully',
                'count': posts.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostDetailAPI(APIView):
    """Get, update or delete post details"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            serializer = PostDetailSerializer(post, context={'request': request})
            
            return Response({
                'message': 'Post retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, post_id):
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            
            # Check if user owns this post
            if post.author != request.user:
                return Response({
                    'error': 'You can only update your own posts'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = PostCreateSerializer(post, data=request.data, partial=True, context={'request': request})
            
            if serializer.is_valid():
                updated_post = serializer.save()
                
                return Response({
                    'message': 'Post updated successfully',
                    'data': PostDetailSerializer(updated_post, context={'request': request}).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, post_id):
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            
            # Check if user owns this post
            if post.author != request.user:
                return Response({
                    'error': 'You can only delete your own posts'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Delete all images
            for image in post.images.all():
                image.image.delete()
                image.delete()
            
            # Delete the post
            post.delete()
            
            return Response({
                'message': 'Post deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserPostsAPI(APIView):
    """Get user's posts"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        try:
            if user_id:
                from django.contrib.auth.models import User
                user = get_object_or_404(User, id=user_id)
            else:
                user = request.user
            
            posts = Post.objects.filter(author=user, is_active=True)
            
            # Filter by post type if provided
            post_type = request.query_params.get('type')
            if post_type:
                posts = posts.filter(post_type=post_type)
            
            serializer = PostListSerializer(posts, many=True, context={'request': request})
            return Response({
                'message': f'Posts by {user.get_full_name()}',
                'count': posts.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostLikeAPI(APIView):
    """Like/Unlike post"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            
            like, created = PostLike.objects.get_or_create(post=post, user=request.user)
            
            if created:
                # Increment likes count
                post.likes_count += 1
                post.save(update_fields=['likes_count'])
                message = 'Post liked successfully'
            else:
                # Unlike - remove like
                like.delete()
                post.likes_count = max(0, post.likes_count - 1)
                post.save(update_fields=['likes_count'])
                message = 'Post unliked successfully'
            
            return Response({
                'message': message,
                'likes_count': post.likes_count,
                'is_liked': created
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostCommentAPI(APIView):
    """Add comment to post"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        try:
            post = get_object_or_404(Post, id=post_id, is_active=True)
            
            serializer = PostCommentCreateSerializer(
                data=request.data,
                context={'request': request, 'post': post}
            )
            
            if serializer.is_valid():
                comment = serializer.save()
                
                # Increment comments count
                post.comments_count += 1
                post.save(update_fields=['comments_count'])
                
                return Response({
                    'message': 'Comment added successfully',
                    'data': PostCommentSerializer(comment).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostImageDeleteAPI(APIView):
    """Delete individual post image"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, image_id):
        try:
            image = get_object_or_404(PostImage, id=image_id)
            
            # Check if user owns this post
            if image.post.author != request.user:
                return Response({
                    'error': 'You can only delete images from your own posts'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Delete the image file
            image.image.delete()
            image.delete()
            
            return Response({
                'message': 'Image deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except PostImage.DoesNotExist:
            return Response({
                'error': f'Image with ID {image_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostImagesListAPI(APIView):
    """List user's posted images"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            images = PostImage.objects.filter(post__author=request.user).select_related('post')
            
            from .serializers import PostImageSerializer
            serializer = PostImageSerializer(images, many=True)
            
            return Response({
                'message': 'Your images retrieved successfully',
                'count': images.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostDeleteAPI(APIView):
    """Delete post"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, post_id):
        try:
            post = get_object_or_404(Post, id=post_id)
            
            # Check if user owns this post
            if post.author != request.user:
                return Response({
                    'error': 'You can only delete your own posts'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Delete all images
            for image in post.images.all():
                image.image.delete()
                image.delete()
            
            # Delete the post
            post.delete()
            
            return Response({
                'message': 'Post deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Post.DoesNotExist:
            return Response({
                'error': f'Post with ID {post_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllPostsAPI(APIView):
    """List all posts from all users"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            posts = Post.objects.filter(is_active=True).select_related('author')
            
            serializer = PostListSerializer(posts, many=True, context={'request': request})
            return Response({
                'message': 'All posts retrieved successfully',
                'count': posts.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostUpdateByImageAPI(APIView):
    """Update post using image ID"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def put(self, request, image_id):
        try:
            image = get_object_or_404(PostImage, id=image_id)
            post = image.post
            
            # Check if post is active
            if not post.is_active:
                return Response({
                    'error': 'Post is not active'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user owns this post
            if post.author != request.user:
                return Response({
                    'error': 'You can only update your own posts'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = PostCreateSerializer(post, data=request.data, partial=True, context={'request': request})
            
            if serializer.is_valid():
                updated_post = serializer.save()
                
                return Response({
                    'message': 'Post updated successfully via image',
                    'data': PostDetailSerializer(updated_post, context={'request': request}).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostLikeByImageAPI(APIView):
    """Like/Unlike post using image ID - Available for all users"""
    
    def post(self, request, image_id):
        try:
            image = get_object_or_404(PostImage, id=image_id)
            post = image.post
            
            # Check if post is active
            if not post.is_active:
                return Response({
                    'error': 'Post is not active'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Handle both authenticated and anonymous users
            if request.user.is_authenticated:
                like, created = PostLike.objects.get_or_create(post=post, user=request.user)
                if created:
                    post.likes_count += 1
                    post.save(update_fields=['likes_count'])
                    message = 'Post liked successfully via image'
                else:
                    like.delete()
                    post.likes_count = max(0, post.likes_count - 1)
                    post.save(update_fields=['likes_count'])
                    message = 'Post unliked successfully via image'
            else:
                # Anonymous user - just increment count
                post.likes_count += 1
                post.save(update_fields=['likes_count'])
                created = True
                message = 'Post liked successfully (anonymous)'
            
            return Response({
                'message': message,
                'likes_count': post.likes_count,
                'is_liked': created
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostCommentByImageAPI(APIView):
    """Add comment to post using image ID - Available for all users"""
    
    def post(self, request, image_id):
        try:
            image = get_object_or_404(PostImage, id=image_id)
            post = image.post
            
            # Check if post is active
            if not post.is_active:
                return Response({
                    'error': 'Post is not active'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = PostCommentCreateSerializer(
                data=request.data,
                context={'request': request, 'post': post}
            )
            
            if serializer.is_valid():
                comment = serializer.save()
                
                # Increment comments count
                post.comments_count += 1
                post.save(update_fields=['comments_count'])
                
                return Response({
                    'message': 'Comment added successfully via image',
                    'data': PostCommentSerializer(comment).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)