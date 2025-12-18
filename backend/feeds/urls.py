from django.urls import path
from .views import (
    PostCreateAPI, PostListAPI, PostDetailAPI, UserPostsAPI,
    PostLikeAPI, PostCommentAPI, PostImageDeleteAPI, PostImagesListAPI, PostDeleteAPI, AllPostsAPI,
    PostUpdateByImageAPI, PostLikeByImageAPI, PostCommentByImageAPI
)

urlpatterns = [
    # Post Management
    path('create/', PostCreateAPI.as_view(), name='post-create'),
    path('feed/', PostListAPI.as_view(), name='post-feed'),
    path('all-posts/', AllPostsAPI.as_view(), name='all-posts'),
    path('post/<int:post_id>/', PostDetailAPI.as_view(), name='post-detail'),
    
    # User Posts
    path('my-posts/', UserPostsAPI.as_view(), name='my-posts'),
    path('user-posts/<int:user_id>/', UserPostsAPI.as_view(), name='user-posts'),
    
    # Post Interactions
    path('post/<int:post_id>/like/', PostLikeAPI.as_view(), name='post-like'),
    path('post/<int:post_id>/comment/', PostCommentAPI.as_view(), name='post-comment'),
    
    # Image-based Interactions
    path('image/<int:image_id>/update/', PostUpdateByImageAPI.as_view(), name='post-update-by-image'),
    path('image/<int:image_id>/like/', PostLikeByImageAPI.as_view(), name='post-like-by-image'),
    path('image/<int:image_id>/comment/', PostCommentByImageAPI.as_view(), name='post-comment-by-image'),
    
    # Image Management
    path('images/', PostImagesListAPI.as_view(), name='post-images-list'),
    path('image/<int:image_id>/delete/', PostImageDeleteAPI.as_view(), name='post-image-delete'),
    path('post/<int:post_id>/delete/', PostDeleteAPI.as_view(), name='post-delete'),
]