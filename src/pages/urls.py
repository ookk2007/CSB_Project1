from django.urls import path

from .views import homePageView, create_post, signup, post_detail, post_update, post_delete, post_search, signup_reset, password_reset

urlpatterns = [
    path('', homePageView, name='home'),
    path('create-post/', create_post, name='create_post'),
    path('signup/', signup, name='signup'),
    path('post-detail/<int:post_id>', post_detail, name='post_detail'),
    path('post-update/<int:post_id>', post_update, name='post_update'),
    path('post-delete/<int:post_id>', post_delete, name='post_delete'),
    path('search/', post_search, name='search'),
    path('signup-reset/', signup_reset, name='signup_reset'),
    path('password-reset/', password_reset, name='password_reset'),
]
