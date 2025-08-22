from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # File Upload endpoints
    path('upload/', views.FileUploadView.as_view(), name='file-upload'),
    path('uploads/', views.FileUploadListView.as_view(), name='file-upload-list'),
    path('uploads/<uuid:pk>/', views.FileUploadDetailView.as_view(), name='file-upload-detail'),
    path('uploads/<uuid:upload_id>/status/', views.file_upload_status, name='file-upload-status'),
    path('uploads/<uuid:upload_id>/process/', views.process_file_upload, name='process-file-upload'),
    path('uploads/<uuid:upload_id>/transactions/', views.get_file_upload_transactions, name='file-upload-transactions'),
    path('uploads/<uuid:upload_id>/approve/', views.approve_file_upload_transactions, name='approve-file-upload-transactions'),
    path('uploads/<uuid:upload_id>/delete/', views.delete_file_upload, name='delete-file-upload'),
    
    # Transaction endpoints
    path('', views.TransactionListView.as_view(), name='transaction-list'),
    path('<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('bulk-update/', views.bulk_update_transactions, name='bulk-update-transactions'),
    path('summary/', views.transaction_summary, name='transaction-summary'),
]
