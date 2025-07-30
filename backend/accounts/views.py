from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import login
from django.conf import settings
import logging

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    LoginSerializer
)

logger = logging.getLogger('kitako')


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """Handle user registration"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            logger.info(f"New user registered: {user.email}")

            response = Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

            # Set refresh token as httpOnly cookie
            response.set_cookie(
                'refresh_token',
                str(refresh),
                max_age=60 * 60 * 24 * 7,  # 7 days
                httponly=True,
                secure=not settings.DEBUG,  # Use secure in production
                samesite='Lax'
            )

            return response

        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            return Response(
                {'error': 'Registration failed', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    API endpoint for user login
    """
    try:
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        logger.info(f"User logged in: {user.email}")

        response = Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
            }
        })

        # Set refresh token as httpOnly cookie
        response.set_cookie(
            'refresh_token',
            str(refresh),
            max_age=60 * 60 * 24 * 7,  # 7 days
            httponly=True,
            secure=not settings.DEBUG,  # Use secure in production
            samesite='Lax'
        )

        return response

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return Response(
            {'error': 'Login failed', 'details': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update user profile
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the current user"""
        return self.request.user

    def get_serializer_class(self):
        """Use different serializers for GET and PUT/PATCH"""
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    API endpoint for changing user password
    """
    try:
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # Change password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        logger.info(f"Password changed for user: {user.email}")

        return Response({'message': 'Password changed successfully'})

    except Exception as e:
        logger.error(f"Password change failed for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Password change failed', 'details': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout (blacklist refresh token)
    """
    try:
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        logger.info(f"User logged out: {request.user.email}")

        response = Response({'message': 'Logout successful'})
        
        # Clear the refresh token cookie
        response.delete_cookie('refresh_token')
        
        return response

    except Exception as e:
        logger.error(f"Logout failed for user {request.user.email}: {str(e)}")
        response = Response(
            {'error': 'Logout failed'},
            status=status.HTTP_400_BAD_REQUEST
        )
        # Still clear the cookie even if blacklisting fails
        response.delete_cookie('refresh_token')
        return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """
    API endpoint for user dashboard data
    """
    try:
        user = request.user

        # Get basic statistics
        from transactions.models import FileUpload, Transaction
        from reports.models import IncomeReport

        file_uploads_count = FileUpload.objects.filter(user=user).count()
        transactions_count = Transaction.objects.filter(user=user).count()
        reports_count = IncomeReport.objects.filter(user=user).count()

        # Get recent activity
        recent_uploads = FileUpload.objects.filter(user=user).order_by('-created_at')[:5]
        recent_transactions = Transaction.objects.filter(user=user).order_by('-date')[:10]

        from transactions.serializers import FileUploadSerializer, TransactionSerializer

        dashboard_data = {
            'user': UserSerializer(user).data,
            'statistics': {
                'file_uploads': file_uploads_count,
                'transactions': transactions_count,
                'reports': reports_count,
            },
            'recent_uploads': FileUploadSerializer(recent_uploads, many=True, context={'request': request}).data,
            'recent_transactions': TransactionSerializer(recent_transactions, many=True).data,
        }

        return Response(dashboard_data)

    except Exception as e:
        logger.error(f"Dashboard data failed for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to load dashboard data'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CookieTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that reads refresh token from httpOnly cookie
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({
                'access': access_token
            })

            # If token rotation is enabled, set new refresh token
            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS'):
                new_refresh = refresh.rotate()
                response.set_cookie(
                    'refresh_token',
                    str(new_refresh),
                    max_age=60 * 60 * 24 * 7,  # 7 days
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax'
                )

            return response

        except (InvalidToken, TokenError) as e:
            response = Response(
                {'error': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            response.delete_cookie('refresh_token')
            return response
