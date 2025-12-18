from django.urls import path
from .views import ProfileUpdateAPI, ProfileDisplayAPI
from .post_views import (
    PostListCreateView, PostDetailView, toggle_post_like,
    PostCommentListCreateView, user_feed, my_posts
)

urlpatterns = [
    path('display/', ProfileDisplayAPI.as_view(), name='profile_display'),
    path('update/', ProfileUpdateAPI.as_view(), name='profile_update'),
    
    # Post endpoints
    path('posts/', PostListCreateView.as_view(), name='post_list_create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/update/', PostDetailView.as_view(), name='post_update'),
    path('posts/<int:post_id>/like/', toggle_post_like, name='toggle_post_like'),
    path('posts/<int:post_id>/comments/', PostCommentListCreateView.as_view(), name='post_comments'),
    path('feed/', user_feed, name='user_feed'),
    path('my-posts/', my_posts, name='my_posts'),
]