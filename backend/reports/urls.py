from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Income report CRUD endpoints
    path('', views.IncomeReportListView.as_view(), name='income-report-list'),
    path('create/', views.IncomeReportCreateView.as_view(), name='income-report-create'),
    path('<uuid:pk>/', views.IncomeReportDetailView.as_view(), name='income-report-detail'),
    path('<uuid:report_id>/delete/', views.delete_report, name='delete-report'),
    
    # PDF generation and download
    path('generate-pdf/', views.generate_pdf_report, name='generate-pdf'),
    path('<uuid:report_id>/download/', views.download_report, name='download-report'),
    path('<uuid:report_id>/status/', views.report_status, name='report-status'),
    
    # Verification and analytics
    path('verify/', views.verify_report, name='verify-report'),
    path('analytics/', views.report_analytics, name='report-analytics'),
]
