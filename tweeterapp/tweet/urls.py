
from django.urls import path
from . import views

urlpatterns = [
    path('', views.tweet_list, name='tweet_list'),
    path('home/', views.home, name='home'),
    path('my-tweets/', views.my_tweets, name='my_tweets'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('create/', views.tweet_create, name='tweet_create'),
    path('<int:pk>/', views.tweet_detail, name='tweet_detail'),
    path('<int:pk>/edit/', views.tweet_edit, name='tweet_edit'),
    path('<int:pk>/delete/', views.tweet_delete, name='tweet_delete'),
    path('<int:pk>/like/', views.tweet_like, name='tweet_like'),
    path('<int:pk>/comment/', views.tweet_comment, name='tweet_comment'),
    path('register/', views.register, name='register'),
] 
