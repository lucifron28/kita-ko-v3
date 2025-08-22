from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import FileUpload, Transaction
from .serializers import (
    FileUploadSerializer,
    TransactionSerializer,
    TransactionBulkUpdateSerializer,
    FileUploadStatusSerializer
)

logger = logging.getLogger('kitako')


class FileUploadView(generics.CreateAPIView):
    """
    API endpoint for uploading financial documents
    """
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        """Handle file upload with enhanced logging and error handling"""
        try:
            logger.info(f"File upload initiated by user {request.user.email}")

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Save the file upload
            file_upload = serializer.save()

            logger.info(f"File uploaded successfully: {file_upload.original_filename} by {request.user.email}")

            # TODO: Trigger background processing task
            # from .tasks import process_uploaded_file
            # process_uploaded_file.delay(file_upload.id)

            return Response(
                {
                    'message': 'File uploaded successfully',
                    'file_upload': serializer.data,
                    'processing_status': 'uploaded'
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"File upload failed for user {request.user.email}: {str(e)}")
            return Response(
                {'error': 'File upload failed', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FileUploadListView(generics.ListAPIView):
    """
    API endpoint to list user's file uploads
    """
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return file uploads for the current user"""
        return FileUpload.objects.filter(user=self.request.user)


class FileUploadDetailView(generics.RetrieveDestroyAPIView):
    """
    API endpoint to retrieve or delete a specific file upload
    """
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return file uploads for the current user"""
        return FileUpload.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def file_upload_status(request, upload_id):
    """
    Check the processing status of a file upload
    """
    try:
        file_upload = get_object_or_404(
            FileUpload,
            id=upload_id,
            user=request.user
        )

        serializer = FileUploadStatusSerializer(file_upload)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error checking file upload status: {str(e)}")
        return Response(
            {'error': 'Failed to check status'},
            status=status.HTTP_400_BAD_REQUEST
        )


class TransactionListView(generics.ListAPIView):
    """
    API endpoint to list user's transactions with filtering
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return transactions for the current user with optional filtering"""
        queryset = Transaction.objects.filter(user=self.request.user)

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__date__gte=date_from)
            except ValueError:
                pass

        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__date__lte=date_to)
            except ValueError:
                pass

        # Filter by transaction type
        transaction_type = self.request.query_params.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Filter by source
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source_platform=source)

        # Search in description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(counterparty__icontains=search) |
                Q(reference_number__icontains=search)
            )

        return queryset.order_by('-date')


class TransactionDetailView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve or update a specific transaction
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return transactions for the current user"""
        return Transaction.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_transactions(request):
    """
    Bulk update multiple transactions
    """
    try:
        serializer = TransactionBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transaction_ids = serializer.validated_data['transaction_ids']
        updates = serializer.validated_data['updates']

        # Get transactions belonging to the user
        transactions = Transaction.objects.filter(
            id__in=transaction_ids,
            user=request.user
        )

        if len(transactions) != len(transaction_ids):
            return Response(
                {'error': 'Some transactions not found or not accessible'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Apply updates
        updated_count = transactions.update(**updates, updated_at=timezone.now())

        logger.info(f"Bulk updated {updated_count} transactions for user {request.user.email}")

        return Response({
            'message': f'Successfully updated {updated_count} transactions',
            'updated_count': updated_count
        })

    except Exception as e:
        logger.error(f"Bulk update failed for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Bulk update failed', 'details': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def transaction_summary(request):
    """
    Get transaction summary statistics for the user
    """
    try:
        # Get date range from query params
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        queryset = Transaction.objects.filter(user=request.user)

        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(date__date__gte=date_from)
            except ValueError:
                pass

        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__date__lte=date_to)
            except ValueError:
                pass

        # Calculate summary statistics
        from django.db.models import Sum, Count, Avg

        income_transactions = queryset.filter(transaction_type='income')
        expense_transactions = queryset.filter(transaction_type='expense')

        total_income = income_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = expense_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        net_income = total_income - total_expenses

        # Category breakdown
        income_by_category = income_transactions.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        expense_by_category = expense_transactions.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        # Monthly trends (last 12 months)
        from django.db.models.functions import TruncMonth
        monthly_data = queryset.annotate(
            month=TruncMonth('date')
        ).values('month', 'transaction_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')

        summary = {
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'net_income': float(net_income),
            'transaction_count': queryset.count(),
            'income_count': income_transactions.count(),
            'expense_count': expense_transactions.count(),
            'income_by_category': list(income_by_category),
            'expense_by_category': list(expense_by_category),
            'monthly_trends': list(monthly_data),
            'date_range': {
                'from': date_from.isoformat() if date_from else None,
                'to': date_to.isoformat() if date_to else None
            }
        }

        return Response(summary)

    except Exception as e:
        logger.error(f"Transaction summary failed for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to generate summary'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_file_upload(request, upload_id):
    """
    Delete a file upload and all associated transactions
    """
    try:
        file_upload = get_object_or_404(
            FileUpload,
            id=upload_id,
            user=request.user
        )

        # Count associated transactions
        transaction_count = file_upload.transactions.count()

        # Delete the file upload (this will cascade delete transactions)
        file_upload.delete()

        logger.info(f"Deleted file upload {upload_id} and {transaction_count} transactions for user {request.user.email}")

        return Response({
            'message': 'File upload and associated transactions deleted successfully',
            'deleted_transactions': transaction_count
        })

    except Exception as e:
        logger.error(f"Delete file upload failed for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Failed to delete file upload'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_file_upload_transactions(request, upload_id):
    """
    Get transactions extracted from a specific file upload for review
    """
    try:
        file_upload = get_object_or_404(
            FileUpload,
            id=upload_id,
            user=request.user
        )

        transactions = file_upload.transactions.all().order_by('-date')
        serializer = TransactionSerializer(transactions, many=True)
        
        return Response({
            'file_upload': {
                'id': str(file_upload.id),
                'filename': file_upload.original_filename,
                'processing_status': file_upload.processing_status,
                'uploaded_at': file_upload.uploaded_at
            },
            'transactions': serializer.data,
            'count': transactions.count()
        })

    except Exception as e:
        logger.error(f"Failed to get transactions for upload {upload_id}: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve transactions'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_file_upload_transactions(request, upload_id):
    """
    Approve/finalize transactions from a file upload after review
    """
    try:
        file_upload = get_object_or_404(
            FileUpload,
            id=upload_id,
            user=request.user
        )

        transaction_updates = request.data.get('transactions', [])
        approved_transactions = []
        rejected_transaction_ids = request.data.get('rejected_transaction_ids', [])

        # Delete rejected transactions
        if rejected_transaction_ids:
            file_upload.transactions.filter(id__in=rejected_transaction_ids).delete()

        # Update approved transactions
        for transaction_data in transaction_updates:
            try:
                transaction = file_upload.transactions.get(id=transaction_data['id'])
                # Update transaction fields if provided
                for field in ['amount', 'description', 'transaction_type', 'category', 'counterparty']:
                    if field in transaction_data:
                        setattr(transaction, field, transaction_data[field])
                
                transaction.save()
                approved_transactions.append(transaction)
            except Transaction.DoesNotExist:
                continue

        # Mark file upload as processed after approval
        file_upload.processing_status = 'processed'
        file_upload.save()

        logger.info(f"Approved {len(approved_transactions)} transactions, rejected {len(rejected_transaction_ids)} for upload {upload_id}")
        
        return Response({
            'message': 'Transactions approved successfully',
            'approved_count': len(approved_transactions),
            'rejected_count': len(rejected_transaction_ids)
        })

    except Exception as e:
        logger.error(f"Failed to approve transactions for upload {upload_id}: {str(e)}")
        return Response(
            {'error': 'Failed to approve transactions'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_file_upload(request, upload_id):
    """
    Process a file upload to extract transactions
    """
    try:
        file_upload = get_object_or_404(
            FileUpload,
            id=upload_id,
            user=request.user
        )

        if file_upload.processing_status == 'processed':
            return Response(
                {'message': 'File already processed'},
                status=status.HTTP_200_OK
            )

        if file_upload.processing_status == 'processing':
            return Response(
                {'message': 'File is currently being processed'},
                status=status.HTTP_200_OK
            )

        # Process the file
        from .processors import process_file_upload
        result = process_file_upload(str(file_upload.id))

        if result['success']:
            logger.info(f"File processing completed for {file_upload.original_filename}")
            return Response({
                'message': 'File processed successfully',
                'transactions_created': result['transactions_created'],
                'upload_id': str(file_upload.id)
            })
        else:
            return Response(
                {'error': 'File processing failed', 'details': result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"File processing failed for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'File processing failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
