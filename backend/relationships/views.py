from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Follow
from .serializers import (
    FollowSerializer, FollowCreateSerializer, UserBasicSerializer, FollowStatsSerializer
)


class FollowUserAPI(APIView):
    """Follow a user"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = FollowCreateSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                follow = serializer.save()
                return Response({
                    'message': f'You are now following {follow.following.get_full_name()}',
                    'data': FollowSerializer(follow).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnfollowUserAPI(APIView):
    """Unfollow a user"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, user_id):
        try:
            following_user = get_object_or_404(User, id=user_id)
            
            try:
                follow = Follow.objects.get(follower=request.user, following=following_user)
                follow.delete()
                
                return Response({
                    'message': f'You have unfollowed {following_user.get_full_name()}'
                }, status=status.HTTP_200_OK)
                
            except Follow.DoesNotExist:
                return Response({
                    'error': 'You are not following this user'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FollowersListAPI(APIView):
    """List user's followers"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        try:
            if user_id:
                user = get_object_or_404(User, id=user_id)
            else:
                user = request.user
            
            followers = Follow.objects.filter(following=user).select_related('follower')
            follower_users = [follow.follower for follow in followers]
            
            serializer = UserBasicSerializer(follower_users, many=True)
            return Response({
                'message': f'Followers of {user.get_full_name()}',
                'count': len(follower_users),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FollowingListAPI(APIView):
    """List users that current user is following"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        try:
            if user_id:
                user = get_object_or_404(User, id=user_id)
            else:
                user = request.user
            
            following = Follow.objects.filter(follower=user).select_related('following')
            following_users = [follow.following for follow in following]
            
            serializer = UserBasicSerializer(following_users, many=True)
            return Response({
                'message': f'Users followed by {user.get_full_name()}',
                'count': len(following_users),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserFollowStatsAPI(APIView):
    """Get follow statistics for a user"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            
            followers_count = Follow.objects.filter(following=user).count()
            following_count = Follow.objects.filter(follower=user).count()
            is_following = Follow.objects.filter(
                follower=request.user, 
                following=user
            ).exists() if request.user != user else False
            
            stats = {
                'followers_count': followers_count,
                'following_count': following_count,
                'is_following': is_following
            }
            
            return Response({
                'message': f'Follow stats for {user.get_full_name()}',
                'data': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)