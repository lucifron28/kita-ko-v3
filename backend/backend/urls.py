"""
URL configuration for Kitako backend project.

Kitako MVP - AI-powered proof-of-income platform for informal earners in the Philippines.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render
import os

def react_app_view(request):
    """Serve the React app for all non-API routes"""
    try:
        with open(os.path.join(settings.BASE_DIR, '../frontend/dist/index.html'), 'r') as f:
            return HttpResponse(f.read(), content_type='text/html')
    except FileNotFoundError:
        # Serve a basic HTML response for production until React app is properly built
        return HttpResponse("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kita-Ko - Loading...</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
                .loading { color: #666; }
            </style>
        </head>
        <body>
            <h1>Kita-Ko</h1>
            <p class="loading">Application is starting up...</p>
            <p>API endpoints are available at /api/</p>
        </body>
        </html>
        """, content_type='text/html')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/ai/', include('ai_processing.urls')),
    path('api/reports/', include('reports.urls')),
    
    # React app - catch all non-API routes
    re_path(r'^(?!api/).*$', react_app_view, name='react_app'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
