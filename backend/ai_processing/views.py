from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging

from .models import AIProcessingJob
from .services import TransactionCategorizationService, FinancialSummaryService
from transactions.models import Transaction, FileUpload

logger = logging.getLogger('kitako')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def categorize_transactions(request):
    """
    API endpoint to categorize transactions using AI
    """
    try:
        # Get transaction IDs from request
        transaction_ids = request.data.get('transaction_ids', [])
        file_upload_id = request.data.get('file_upload_id')

        # Get transactions to categorize
        if transaction_ids:
            transactions = Transaction.objects.filter(
                id__in=transaction_ids,
                user=request.user
            )
        elif file_upload_id:
            file_upload = get_object_or_404(
                FileUpload,
                id=file_upload_id,
                user=request.user
            )
            transactions = file_upload.transactions.all()
        else:
            return Response(
                {'error': 'Must provide either transaction_ids or file_upload_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not transactions.exists():
            return Response(
                {'error': 'No transactions found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create AI processing job
        job = AIProcessingJob.objects.create(
            user=request.user,
            job_type='categorize_transactions',
            input_data={
                'transaction_count': transactions.count(),
                'transaction_ids': [str(t.id) for t in transactions]
            },
            status='processing',
            started_at=timezone.now()
        )

        # Prepare transaction data for AI
        transactions_data = []
        for txn in transactions:
            transactions_data.append({
                'id': str(txn.id),
                'date': txn.date.isoformat(),
                'amount': float(txn.amount),
                'description': txn.description,
                'reference_number': txn.reference_number,
                'counterparty': txn.counterparty or ''
            })

        # Use AI service to categorize
        categorization_service = TransactionCategorizationService()
        result = categorization_service.categorize_transactions(transactions_data)

        if result['success']:
            # Update transactions with AI categorization
            categorized_count = 0
            for categorized_txn in result['categorized_transactions']:
                try:
                    txn_id = categorized_txn.get('id')
                    if isinstance(txn_id, int):
                        # If ID is index, get the actual transaction
                        txn = transactions[txn_id]
                    else:
                        # If ID is UUID string
                        txn = transactions.get(id=txn_id)

                    # Update transaction with AI categorization
                    txn.transaction_type = categorized_txn.get('transaction_type', txn.transaction_type)
                    txn.category = categorized_txn.get('category', txn.category)
                    txn.ai_confidence = categorized_txn.get('confidence', 'medium')
                    txn.ai_reasoning = categorized_txn.get('reasoning', '')
                    txn.ai_categorized = True
                    txn.save()

                    categorized_count += 1

                except Exception as e:
                    logger.error(f"Error updating transaction: {str(e)}")
                    continue

            # Update job status
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.output_data = {
                'categorized_count': categorized_count,
                'total_count': len(transactions_data)
            }
            job.save()

            logger.info(f"Categorized {categorized_count} transactions for user {request.user.email}")

            return Response({
                'message': f'Successfully categorized {categorized_count} transactions',
                'job_id': job.id,
                'categorized_count': categorized_count,
                'total_count': len(transactions_data)
            })

        else:
            # Update job with error
            job.status = 'failed'
            job.error_message = result.get('error', 'Unknown error')
            job.completed_at = timezone.now()
            job.save()

            return Response(
                {'error': 'AI categorization failed', 'details': result.get('error')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Transaction categorization failed for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Categorization failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_financial_summary(request):
    """
    API endpoint to generate financial summary using AI
    """
    try:
        # Get parameters from request
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')

        if not date_from or not date_to:
            return Response(
                {'error': 'date_from and date_to are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get transactions for the date range
        transactions = Transaction.objects.filter(
            user=request.user,
            date__date__gte=date_from,
            date__date__lte=date_to
        )

        if not transactions.exists():
            return Response(
                {'error': 'No transactions found for the specified date range'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create AI processing job
        job = AIProcessingJob.objects.create(
            user=request.user,
            job_type='generate_summary',
            input_data={
                'date_from': date_from,
                'date_to': date_to,
                'transaction_count': transactions.count()
            },
            status='processing',
            started_at=timezone.now()
        )

        # Prepare transaction data for AI
        transactions_data = []
        for txn in transactions:
            transactions_data.append({
                'date': txn.date.isoformat(),
                'amount': float(txn.amount),
                'description': txn.description,
                'transaction_type': txn.transaction_type,
                'category': txn.category,
                'counterparty': txn.counterparty or ''
            })

        # Use AI service to generate summary
        summary_service = FinancialSummaryService()
        result = summary_service.generate_summary(
            transactions_data,
            {'from': date_from, 'to': date_to}
        )

        if result['success']:
            # Update job status
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.output_data = {
                'summary': result['summary'],
                'statistics': result['statistics']
            }
            job.save()

            logger.info(f"Generated financial summary for user {request.user.email}")

            return Response({
                'message': 'Financial summary generated successfully',
                'job_id': job.id,
                'summary': result['summary'],
                'statistics': result['statistics']
            })

        else:
            # Update job with error
            job.status = 'failed'
            job.error_message = result.get('error', 'Unknown error')
            job.completed_at = timezone.now()
            job.save()

            return Response(
                {'error': 'Summary generation failed', 'details': result.get('error')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Summary generation failed for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Summary generation failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_job_status(request, job_id):
    """
    Check the status of an AI processing job
    """
    try:
        job = get_object_or_404(
            AIProcessingJob,
            id=job_id,
            user=request.user
        )

        job_data = {
            'id': job.id,
            'job_type': job.job_type,
            'status': job.status,
            'progress_percentage': job.progress_percentage,
            'created_at': job.created_at,
            'started_at': job.started_at,
            'completed_at': job.completed_at,
            'error_message': job.error_message,
            'output_data': job.output_data
        }

        return Response(job_data)

    except Exception as e:
        logger.error(f"AI job status check failed: {str(e)}")
        return Response(
            {'error': 'Failed to check job status'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ai_jobs_list(request):
    """
    List AI processing jobs for the user
    """
    try:
        jobs = AIProcessingJob.objects.filter(user=request.user).order_by('-created_at')

        # Optional filtering
        job_type = request.query_params.get('job_type')
        if job_type:
            jobs = jobs.filter(job_type=job_type)

        status_filter = request.query_params.get('status')
        if status_filter:
            jobs = jobs.filter(status=status_filter)

        # Pagination
        from django.core.paginator import Paginator
        paginator = Paginator(jobs, 20)
        page_number = request.query_params.get('page', 1)
        page_obj = paginator.get_page(page_number)

        jobs_data = []
        for job in page_obj:
            jobs_data.append({
                'id': job.id,
                'job_type': job.job_type,
                'status': job.status,
                'progress_percentage': job.progress_percentage,
                'created_at': job.created_at,
                'completed_at': job.completed_at,
                'processing_time_seconds': job.processing_time_seconds,
                'error_message': job.error_message
            })

        return Response({
            'jobs': jobs_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })

    except Exception as e:
        logger.error(f"AI jobs list failed: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve jobs'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def detect_anomalies(request):
    """
    API endpoint to detect anomalies in transactions using AI
    """
    try:
        # Get parameters from request
        transaction_ids = request.data.get('transaction_ids', [])

        if not transaction_ids:
            # Use all user transactions if none specified
            transactions = Transaction.objects.filter(user=request.user)
        else:
            transactions = Transaction.objects.filter(
                id__in=transaction_ids,
                user=request.user
            )

        if not transactions.exists():
            return Response(
                {'error': 'No transactions found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Simple anomaly detection logic (can be enhanced with AI)
        anomalies = []

        # Calculate average transaction amounts by category
        from django.db.models import Avg
        avg_amounts = transactions.values('category').annotate(avg_amount=Avg('amount'))
        avg_dict = {item['category']: item['avg_amount'] for item in avg_amounts}

        # Check for anomalies
        for txn in transactions:
            avg_amount = avg_dict.get(txn.category, 0)
            if avg_amount > 0:
                deviation = abs(float(txn.amount) - float(avg_amount)) / float(avg_amount)

                # Flag as anomaly if deviation is > 200%
                if deviation > 2.0:
                    anomalies.append({
                        'transaction_id': str(txn.id),
                        'amount': float(txn.amount),
                        'average_amount': float(avg_amount),
                        'deviation_percentage': deviation * 100,
                        'reason': f'Amount significantly higher than average for {txn.category} category'
                    })

                    # Update transaction
                    txn.is_anomaly = True
                    txn.anomaly_reason = f'Amount deviation: {deviation*100:.1f}% from category average'
                    txn.save()

        logger.info(f"Detected {len(anomalies)} anomalies for user {request.user.email}")

        return Response({
            'message': f'Anomaly detection completed. Found {len(anomalies)} anomalies.',
            'anomalies': anomalies,
            'total_transactions_checked': transactions.count()
        })

    except Exception as e:
        logger.error(f"Anomaly detection failed for user {request.user.email}: {str(e)}")
        return Response(
            {'error': 'Anomaly detection failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
