from django.urls import path
from .views import (
    FollowUserAPI, UnfollowUserAPI, FollowersListAPI, 
    FollowingListAPI, UserFollowStatsAPI
)

urlpatterns = [
    # Follow Actions
    path('follow/', FollowUserAPI.as_view(), name='follow-user'),
    path('unfollow/<int:user_id>/', UnfollowUserAPI.as_view(), name='unfollow-user'),
    
    # Follow Lists
    path('followers/', FollowersListAPI.as_view(), name='my-followers'),
    path('followers/<int:user_id>/', FollowersListAPI.as_view(), name='user-followers'),
    path('following/', FollowingListAPI.as_view(), name='my-following'),
    path('following/<int:user_id>/', FollowingListAPI.as_view(), name='user-following'),
    
    # Follow Stats
    path('stats/<int:user_id>/', UserFollowStatsAPI.as_view(), name='user-follow-stats'),
]