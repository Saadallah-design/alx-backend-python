"""
Authentication views and utilities for the messaging_app API.

This module provides authentication endpoints for user login, logout,
token refresh, and user registration.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from .models import user as User
from .serializers import UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view that returns user info along with tokens.
    
    POST /api/token/
    {
        "email": "user@example.com",
        "password": "password123"
    }
    
    Response:
    {
        "refresh": "...",
        "access": "...",
        "user": {
            "user_id": "...",
            "email": "...",
            "first_name": "...",
            ...
        }
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Authenticate user
        try:
            user_obj = User.objects.get(email=email)
            if user_obj.check_password(password):
                # Generate tokens
                refresh = RefreshToken.for_user(user_obj)
                
                # Serialize user data
                user_serializer = UserSerializer(user_obj)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': user_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    
    POST /api/register/
    {
        "email": "user@example.com",
        "password": "password123",
        "password_confirm": "password123",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1234567890",
        "role": "guest"
    }
    
    Response:
    {
        "user": {
            "user_id": "...",
            "email": "...",
            "first_name": "...",
            ...
        },
        "refresh": "...",
        "access": "..."
    }
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        # Validate password confirmation
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')
        
        if password != password_confirm:
            return Response(
                {'error': 'Passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user (serializer.create() handles password hashing)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user_obj)
        
        # Return user data with tokens
        return Response({
            'user': UserSerializer(user_obj).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint that blacklists the refresh token.
    
    POST /api/logout/
    {
        "refresh": "refresh_token_here"
    }
    
    Response:
    {
        "message": "Logout successful"
    }
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Blacklist the token
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response(
            {'message': 'Logout successful'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current authenticated user's information.
    
    GET /api/user/me/
    Headers: Authorization: Bearer <access_token>
    
    Response:
    {
        "user_id": "...",
        "email": "...",
        "first_name": "...",
        ...
    }
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user_view(request):
    """
    Update current authenticated user's information.
    
    PUT/PATCH /api/user/me/
    Headers: Authorization: Bearer <access_token>
    {
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "+9876543210"
    }
    
    Response:
    {
        "user_id": "...",
        "email": "...",
        "first_name": "Jane",
        ...
    }
    """
    partial = request.method == 'PATCH'
    serializer = UserSerializer(
        request.user,
        data=request.data,
        partial=partial
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Change password for the current authenticated user.
    
    POST /api/user/change-password/
    Headers: Authorization: Bearer <access_token>
    {
        "old_password": "oldpass123",
        "new_password": "newpass123",
        "new_password_confirm": "newpass123"
    }
    
    Response:
    {
        "message": "Password changed successfully"
    }
    """
    user_obj = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    new_password_confirm = request.data.get('new_password_confirm')
    
    # Validate required fields
    if not all([old_password, new_password, new_password_confirm]):
        return Response(
            {'error': 'All password fields are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check old password
    if not user_obj.check_password(old_password):
        return Response(
            {'error': 'Old password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check password confirmation
    if new_password != new_password_confirm:
        return Response(
            {'error': 'New passwords do not match'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user_obj.set_password(new_password)
    user_obj.save()
    
    return Response(
        {'message': 'Password changed successfully'},
        status=status.HTTP_200_OK
    )
