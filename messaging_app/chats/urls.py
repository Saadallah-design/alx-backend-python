from django.urls import path, include
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter
from .views import ConversationViewSet, MessageViewSet
from . import auth

# Create a router and register our viewsets
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Create nested router for messages under conversations
conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# The API URLs are determined automatically by the router
urlpatterns = [
    # Authentication endpoints
    path('auth/register/', auth.RegisterView.as_view(), name='register'),
    path('auth/login/', auth.CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', auth.logout_view, name='logout'),
    path('auth/user/', auth.current_user_view, name='current-user'),
    path('auth/user/update/', auth.update_user_view, name='update-user'),
    path('auth/user/change-password/', auth.change_password_view, name='change-password'),
    
    # Router URLs
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]
