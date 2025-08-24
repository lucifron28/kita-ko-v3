"""
Security and Privacy Middleware for Kitako MVP
"""

import logging
import time
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model

logger = logging.getLogger('kitako')
User = get_user_model()


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    """
    
    def process_response(self, request, response):
        """Add security headers"""
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (basic)
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'"
        
        # HTTPS enforcement (in production)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware to prevent abuse
    """
    
    def process_request(self, request):
        if settings.DEBUG:
            return None
            
        skip_paths = [
            '/admin/', 
            '/api/docs/', 
            '/api/redoc/',
            '/api/auth/dashboard/',
            '/api/auth/profile/',
        ]
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        ip = self.get_client_ip(request)
        
        # Different limits for authenticated vs anonymous users
        # Check if user attribute exists and is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Authenticated users: 200 requests per minute (increased for development)
            limit_key = f"rate_limit_user_{request.user.id}"
            limit = 200
            window = 60  # 1 minute
            if settings.DEBUG:
                logger.debug(f"Rate limiting authenticated user {request.user.id} with key {limit_key}")
        else:
            limit_key = f"rate_limit_ip_{ip}"
            limit = 100
            window = 60  # 1 minute
            if settings.DEBUG:
                user_status = "no user attr" if not hasattr(request, 'user') else "not authenticated"
                logger.debug(f"Rate limiting anonymous user ({user_status}) with key {limit_key}")
            window = 60  # 1 minute
        
        # Check current count
        current_count = cache.get(limit_key, 0)
        
        if current_count >= limit:
            user_info = 'anonymous'
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = f"user_{request.user.id}"
            logger.warning(f"Rate limit exceeded for {ip} ({user_info})")
            return JsonResponse(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=429
            )
        
        # Increment count
        cache.set(limit_key, current_count + 1, window)
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AuditLogMiddleware(MiddlewareMixin):
    """
    Audit logging middleware for sensitive operations
    """
    
    SENSITIVE_PATHS = [
        '/api/auth/login/',
        '/api/auth/register/',
        '/api/transactions/upload/',
        '/api/reports/create/',
        '/api/reports/generate-pdf/',
    ]
    
    def process_request(self, request):
        """Log sensitive operations"""
        if request.path in self.SENSITIVE_PATHS:
            user_id = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = request.user.id
            ip = self.get_client_ip(request)
            
            logger.info(f"Sensitive operation: {request.method} {request.path} - User: {user_id} - IP: {ip}")
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DataPrivacyMiddleware(MiddlewareMixin):
    """
    Data privacy middleware to handle sensitive data
    """
    
    def process_response(self, request, response):
        """Remove sensitive data from responses in production"""
        if not settings.DEBUG and hasattr(response, 'content'):
            # Remove debug information from error responses
            if response.status_code >= 400:
                try:
                    import json
                    data = json.loads(response.content)
                    
                    # Remove detailed error information in production
                    if 'details' in data and isinstance(data['details'], str):
                        # Keep only generic error messages
                        if 'Traceback' in data['details'] or 'Exception' in data['details']:
                            data['details'] = 'Internal server error'
                            response.content = json.dumps(data).encode('utf-8')
                            
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
        
        return response


class FileUploadSecurityMiddleware(MiddlewareMixin):
    """
    Security middleware specifically for file uploads
    """
    
    def process_request(self, request):
        """Validate file uploads"""
        if request.path.startswith('/api/transactions/upload/') and request.method == 'POST':
            # Try to authenticate JWT token for this specific endpoint
            authenticated = False
            
            # Check session authentication first
            if hasattr(request, 'user') and request.user.is_authenticated:
                authenticated = True
            
            # If not authenticated via session, try JWT
            if not authenticated:
                from rest_framework_simplejwt.authentication import JWTAuthentication
                from rest_framework.exceptions import AuthenticationFailed
                
                jwt_auth = JWTAuthentication()
                try:
                    auth_result = jwt_auth.authenticate(request)
                    if auth_result:
                        request.user, _ = auth_result
                        authenticated = True
                except AuthenticationFailed:
                    pass
            
            if not authenticated:
                return JsonResponse(
                    {'error': 'Authentication required for file uploads'},
                    status=401
                )
            
            # Check file size before processing
            if hasattr(request, 'FILES'):
                for file_field, uploaded_file in request.FILES.items():
                    if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
                        return JsonResponse(
                            {'error': f'File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB'},
                            status=413
                        )
        
        return None
