from django.urls import path
from . import views

app_name = 'ai_processing'

urlpatterns = [
    # AI Processing endpoints
    path('categorize/', views.categorize_transactions, name='categorize-transactions'),
    path('summarize/', views.generate_financial_summary, name='generate-summary'),
    path('detect-anomalies/', views.detect_anomalies, name='detect-anomalies'),
    
    # Job management endpoints
    path('jobs/', views.ai_jobs_list, name='ai-jobs-list'),
    path('jobs/<uuid:job_id>/', views.ai_job_status, name='ai-job-status'),
]
