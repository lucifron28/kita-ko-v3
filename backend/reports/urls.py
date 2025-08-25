from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Report Management
    path('', views.IncomeReportListView.as_view(), name='report-list'),
    path('create/', views.IncomeReportCreateView.as_view(), name='create-report'),
    path('<uuid:pk>/', views.IncomeReportDetailView.as_view(), name='get-report'),
    
    # PDF Generation
    path('generate-pdf/', views.generate_pdf_report, name='generate-pdf'),
    path('<uuid:report_id>/status/', views.report_status, name='report-status'),
    
    # Download and Access
    path('<uuid:report_id>/download/', views.download_report, name='download-report'),
    
    # Verification
    path('verify/', views.verify_report, name='verify-report'),
    path('<uuid:report_id>/submit-verification/', views.submit_signature_verification, name='submit-verification'),
    path('verify-public/<str:verification_code>/', views.public_verification, name='public-verification'),
    
    # Analytics
    path('analytics/', views.report_analytics, name='report-analytics'),
    
    # Delete
    path('<uuid:report_id>/delete/', views.delete_report, name='delete-report'),
]
