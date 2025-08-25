from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from .models import IncomeReport
from .serializers import (
    IncomeReportCreateSerializer,
    IncomeReportSerializer,
    IncomeReportListSerializer,
    ReportGenerationRequestSerializer,
    ReportVerificationSerializer,
    ReportSharingSerializer
)
from .services import IncomeReportGenerator
from transactions.models import Transaction

logger = logging.getLogger('kitako')


class IncomeReportCreateView(generics.CreateAPIView):
    """
    API endpoint to create a new income report
    """
    serializer_class = IncomeReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create income report and calculate financial data"""
        try:
            from decimal import Decimal
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Create the report with default values for required fields
            report_data = serializer.validated_data
            report_data.update({
                'user': request.user,  # Associate with authenticated user
                'total_income': Decimal('0.00'),
                'total_expenses': Decimal('0.00'),
                'net_income': Decimal('0.00'),
                'average_monthly_income': Decimal('0.00'),
                'confidence_score': Decimal('0.00'),
                'summary': 'Generating report...'
            })
            
            report = IncomeReport.objects.create(**report_data)

            # Calculate financial data
            self._calculate_report_data(report)

            logger.info(f"Created income report {report.id} for user {request.user.email}")

            return Response(
                {
                    'message': 'Income report created successfully',
                    'report': IncomeReportSerializer(report, context={'request': request}).data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Income report creation failed: {str(e)}")
            return Response(
                {'error': 'Report creation failed', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _calculate_report_data(self, report: IncomeReport):
        """Calculate financial data for the report with enhanced accuracy"""
        from django.db.models import Q, F, Sum
        from datetime import datetime, timedelta
        from collections import defaultdict
        from decimal import Decimal
        
        # Get transactions for the date range
        transactions = Transaction.objects.filter(
            user=report.user,
            date__date__gte=report.date_from,
            date__date__lte=report.date_to
        ).select_related('user')

        # Validate data integrity
        if not transactions.exists():
            logger.warning(f"No transactions found for report {report.id} user {report.user.email}")
            report.confidence_score = 0.0
            report.generation_error = "No transaction data available for the selected period"
            report.save()
            return

        # Calculate totals with better precision and Decimal handling
        income_transactions = transactions.filter(transaction_type='income')
        expense_transactions = transactions.filter(transaction_type='expense')

        total_income = income_transactions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_expenses = expense_transactions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        # Enhanced period calculation with Decimal arithmetic
        period_days = (report.date_to - report.date_from).days + 1  # Include both dates
        period_months = max(Decimal(str(period_days)) / Decimal('30.44'), Decimal('0.1'))  # Minimum 0.1 to avoid division issues
        average_monthly_income = total_income / period_months

        # Enhanced income breakdown by category with validation
        income_breakdown = {}
        for category_data in income_transactions.values('category').annotate(total=Sum('amount')):
            category = category_data['category'] or 'Uncategorized'
            income_breakdown[category] = float(category_data['total'])

        # Enhanced expense breakdown by category with validation
        expense_breakdown = {}
        for category_data in expense_transactions.values('category').annotate(total=Sum('amount')):
            category = category_data['category'] or 'Uncategorized'
            expense_breakdown[category] = float(category_data['total'])

        # Monthly trends calculation
        monthly_trends = self._calculate_monthly_trends(transactions, report.date_from, report.date_to)

        # Enhanced data sources with platform info
        data_sources = list(transactions.values_list('source_platform', flat=True).distinct())
        data_sources = [source for source in data_sources if source]
        # Ensure unique data sources using set to prevent duplicates
        data_sources = list(set(data_sources))

        # Calculate confidence score based on data quality
        confidence_score = self._calculate_confidence_score(
            transactions, income_transactions, expense_transactions, data_sources
        )

        # Detect anomalies
        anomalies = self._detect_financial_anomalies(income_transactions, expense_transactions)

        # Update report with all calculated data
        report.total_income = total_income
        report.total_expenses = total_expenses
        report.net_income = total_income - total_expenses
        report.average_monthly_income = average_monthly_income
        report.income_breakdown = income_breakdown
        report.expense_breakdown = expense_breakdown
        report.monthly_trends = monthly_trends
        report.data_sources = data_sources
        report.transaction_count = transactions.count()
        report.confidence_score = confidence_score
        report.anomalies_detected = anomalies
        report.save()

        logger.info(f"Calculated financial data for report {report.id}: Income=₱{total_income:,.2f}, Confidence={confidence_score}%")

    def _calculate_monthly_trends(self, transactions, date_from, date_to):
        """Calculate monthly income and expense trends"""
        from django.db.models.functions import TruncMonth
        
        monthly_data = transactions.annotate(
            month=TruncMonth('date')
        ).values('month', 'transaction_type').annotate(
            total=Sum('amount')
        ).order_by('month', 'transaction_type')

        trends = {}
        for item in monthly_data:
            month_key = item['month'].strftime('%Y-%m')
            if month_key not in trends:
                trends[month_key] = {'income': 0, 'expenses': 0}
            
            trends[month_key][item['transaction_type']] = float(item['total'])

        return trends

    def _calculate_confidence_score(self, transactions, income_transactions, expense_transactions, data_sources):
        """Calculate confidence score based on data quality indicators"""
        score = 100.0
        
        # Reduce score for limited data
        if transactions.count() < 10:
            score -= 30
        elif transactions.count() < 50:
            score -= 15
            
        # Reduce score for limited time period
        if len(data_sources) < 2:
            score -= 15
            
        # Reduce score for high percentage of uncategorized transactions
        uncategorized_count = transactions.filter(Q(category__isnull=True) | Q(category='')).count()
        uncategorized_percentage = (uncategorized_count / transactions.count()) * 100 if transactions.count() > 0 else 0
        if uncategorized_percentage > 50:
            score -= 20
        elif uncategorized_percentage > 20:
            score -= 10
            
        # Reduce score for irregular patterns
        if income_transactions.count() == 0:
            score -= 40
            
        return max(score, 0.0)

    def _detect_financial_anomalies(self, income_transactions, expense_transactions):
        """Detect potential anomalies in financial data"""
        anomalies = []
        
        if income_transactions.exists():
            # Check for unusually large income transactions
            avg_income = income_transactions.aggregate(Avg('amount'))['amount__avg'] or 0
            large_income = income_transactions.filter(amount__gt=avg_income * 3)
            if large_income.exists():
                anomalies.append(f"{large_income.count()} unusually large income transactions detected")
                
        if expense_transactions.exists():
            # Check for unusually large expense transactions
            avg_expense = expense_transactions.aggregate(Avg('amount'))['amount__avg'] or 0
            large_expense = expense_transactions.filter(amount__gt=avg_expense * 3)
            if large_expense.exists():
                anomalies.append(f"{large_expense.count()} unusually large expense transactions detected")
        
        return anomalies


class IncomeReportListView(generics.ListAPIView):
    """
    API endpoint to list user's income reports
    """
    serializer_class = IncomeReportListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return reports for the current user"""
        return IncomeReport.objects.filter(user=self.request.user).order_by('-created_at')


class IncomeReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete an income report
    """
    serializer_class = IncomeReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return reports for the current user"""
        return IncomeReport.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.request.method in ['PUT', 'PATCH']:
            return ReportSharingSerializer
        return IncomeReportSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_pdf_report(request):
    """
    Start PDF generation for an income report (async processing)
    """
    logger.info(f"PDF generation request from user: {request.user.email}")
    logger.info(f"Request data: {request.data}")
    
    try:
        serializer = ReportGenerationRequestSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        report_id = serializer.validated_data['report_id']
        report = get_object_or_404(IncomeReport, id=report_id, user=request.user)

        if report.status == 'generating':
            return Response(
                {
                    'message': 'Report is already being generated',
                    'report': IncomeReportSerializer(report, context={'request': request}).data
                },
                status=status.HTTP_200_OK
            )

        if report.status == 'completed' and report.pdf_file:
            return Response(
                {
                    'message': 'Report already generated',
                    'report': IncomeReportSerializer(report, context={'request': request}).data
                },
                status=status.HTTP_200_OK
            )

        # Update status to generating
        report.status = 'generating'
        report.generation_error = ''  # Clear any previous errors
        report.save(update_fields=['status', 'generation_error'])

        # Start background PDF generation
        from threading import Thread
        
        def generate_pdf_background():
            try:
                generator = IncomeReportGenerator()
                generator.generate_report(report)
                logger.info(f"Background PDF generation completed for report {report.id}")
            except Exception as e:
                logger.error(f"Background PDF generation failed: {str(e)}")
                # The generator already handles error status updates
        
        # Start generation in background thread
        thread = Thread(target=generate_pdf_background)
        thread.daemon = True
        thread.start()
        
        # Return immediately with status
        return Response(
            {
                'message': 'PDF generation started',
                'report': IncomeReportSerializer(report, context={'request': request}).data
            }
        )

    except Exception as e:
        logger.error(f"PDF generation start failed: {str(e)}")
        # Update report status if we have the report
        if 'report' in locals():
            report.status = 'failed'
            report.generation_error = str(e)
            report.save(update_fields=['status', 'generation_error'])
        
        return Response(
            {'error': 'PDF generation start failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def report_status(request, report_id):
    """
    Get real-time status of a report generation
    """
    try:
        report = get_object_or_404(IncomeReport, id=report_id, user=request.user)
        
        status_data = {
            'id': report.id,
            'status': report.status,
            'progress': 100 if report.status == 'completed' else 50 if report.status == 'generating' else 0,
            'message': {
                'generating': 'Generating PDF report...',
                'completed': 'PDF report generated successfully',
                'failed': f'Generation failed: {report.generation_error}',
            }.get(report.status, 'Unknown status'),
            'pdf_available': bool(report.pdf_file),
            'created_at': report.created_at,
            'completed_at': report.completed_at,
        }
        
        return Response(status_data)
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return Response(
            {'error': 'Status check failed'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def download_report(request, report_id):
    """
    Download PDF report (public access with verification)
    """
    try:
        report = get_object_or_404(IncomeReport, id=report_id)

        # Check if report is public or user has access
        if not report.is_public and report.user != request.user:
            # Check for access token
            access_token = request.query_params.get('token')
            if not access_token or access_token != report.access_token:
                raise Http404("Report not found or access denied")

        # Check if report is expired
        if report.is_expired:
            return Response(
                {'error': 'Report has expired'},
                status=status.HTTP_410_GONE
            )

        # Check if PDF exists
        if not report.pdf_file:
            return Response(
                {'error': 'PDF not available'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Increment download count
        report.download_count += 1
        report.save(update_fields=['download_count'])

        # Return PDF file
        response = HttpResponse(
            report.pdf_file.read(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{report.pdf_file.name}"'

        logger.info(f"Downloaded report {report.id}")
        return response

    except Exception as e:
        logger.error(f"Report download failed: {str(e)}")
        return Response(
            {'error': 'Download failed'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_report(request):
    """
    Verify a report using verification code
    """
    try:
        serializer = ReportVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        verification_code = serializer.validated_data['verification_code']

        try:
            report = IncomeReport.objects.get(verification_code=verification_code)
        except IncomeReport.DoesNotExist:
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Return basic report information for verification
        verification_data = {
            'verified': True,
            'report_id': report.id,
            'title': report.title,
            'date_from': report.date_from,
            'date_to': report.date_to,
            'total_income': f"₱{report.total_income:,.2f}",
            'net_income': f"₱{report.net_income:,.2f}",
            'generated_on': report.created_at,
            'user_name': report.user.full_name,
            'confidence_score': report.confidence_score,
            'is_expired': report.is_expired
        }

        logger.info(f"Verified report {report.id} with code {verification_code}")
        return Response(verification_data)

    except Exception as e:
        logger.error(f"Report verification failed: {str(e)}")
        return Response(
            {'error': 'Verification failed'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def report_analytics(request):
    """
    Get analytics data for user's reports
    """
    try:
        user_reports = IncomeReport.objects.filter(user=request.user)

        # Basic statistics
        total_reports = user_reports.count()
        completed_reports = user_reports.filter(status='completed').count()
        total_downloads = user_reports.aggregate(Sum('download_count'))['download_count__sum'] or 0

        # Recent reports
        recent_reports = user_reports.order_by('-created_at')[:5]

        # Monthly report creation trend (last 12 months)
        from django.db.models.functions import TruncMonth
        monthly_trend = user_reports.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        analytics_data = {
            'total_reports': total_reports,
            'completed_reports': completed_reports,
            'total_downloads': total_downloads,
            'success_rate': (completed_reports / total_reports * 100) if total_reports > 0 else 0,
            'recent_reports': IncomeReportListSerializer(
                recent_reports,
                many=True,
                context={'request': request}
            ).data,
            'monthly_trend': list(monthly_trend)
        }

        return Response(analytics_data)

    except Exception as e:
        logger.error(f"Report analytics failed: {str(e)}")
        return Response(
            {'error': 'Analytics failed'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_report(request, report_id):
    """
    Delete an income report
    """
    try:
        report = get_object_or_404(IncomeReport, id=report_id, user=request.user)

        # Delete the PDF file if it exists
        if report.pdf_file:
            report.pdf_file.delete()

        # Delete the report
        report.delete()

        logger.info(f"Deleted report {report_id} for user {request.user.email}")

        return Response({'message': 'Report deleted successfully'})

    except Exception as e:
        logger.error(f"Report deletion failed: {str(e)}")
        return Response(
            {'error': 'Deletion failed'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_signature_verification(request, report_id):
    """
    Submit a report for signature verification by admin
    """
    try:
        report = get_object_or_404(IncomeReport, id=report_id, user=request.user)
        
        # Check if report has PDF file
        if not report.pdf_file or report.status != 'completed':
            return Response(
                {'error': 'Report must be completed with PDF before verification'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already submitted
        if report.is_signature_submitted:
            return Response(
                {
                    'message': 'Report already submitted for verification',
                    'status': report.signature_verification_status
                }
            )
        
        # Submit for verification
        report.submit_for_signature_verification()
        
        logger.info(f"Report {report_id} submitted for signature verification by {request.user.email}")
        
        return Response({
            'message': 'Report submitted for signature verification',
            'verification_status': report.signature_verification_status,
            'qr_code_url': report.qr_code_url,
            'verification_code': report.verification_code
        })

    except Exception as e:
        logger.error(f"Signature verification submission failed: {str(e)}")
        return Response(
            {'error': 'Submission failed'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Public access
def public_verification(request, verification_code):
    """
    Public verification page - no authentication required
    Returns document verification status for QR code scanning
    """
    try:
        report = get_object_or_404(IncomeReport, verification_code=verification_code)
        
        verification_data = {
            'verification_code': verification_code,
            'document_title': report.title,
            'created_date': report.created_at.strftime('%B %d, %Y'),
            'is_verified': report.is_verified,
            'verification_status': report.get_signature_verification_status_display(),
            'user_email': report.user.email[:3] + '***@' + report.user.email.split('@')[1],  # Partially masked email
        }
        
        # Add verification details based on status
        if report.signature_verification_status == 'approved':
            verification_data.update({
                'verified': True,
                'verified_date': report.signature_approved_at.strftime('%B %d, %Y at %I:%M %p') if report.signature_approved_at else None,
                'message': 'This document has been verified and approved by KitaKo administrators.',
                'status_class': 'verified'
            })
        elif report.signature_verification_status == 'rejected':
            verification_data.update({
                'verified': False,
                'rejected_date': report.signature_approved_at.strftime('%B %d, %Y at %I:%M %p') if report.signature_approved_at else None,
                'message': 'This document signature was not approved.',
                'admin_notes': report.admin_notes if report.admin_notes else None,
                'status_class': 'rejected'
            })
        elif report.signature_verification_status == 'pending':
            verification_data.update({
                'verified': False,
                'message': 'This document is currently under review by KitaKo administrators.',
                'status_class': 'pending'
            })
        else:
            verification_data.update({
                'verified': False,
                'message': 'This document has not been submitted for signature verification.',
                'status_class': 'not_submitted'
            })
        
        # Add document hash for technical verification
        verification_data['document_hash'] = report.document_hash[:16] + '...' if report.document_hash else None
        
        logger.info(f"Public verification accessed for code {verification_code}")
        
        return Response(verification_data)

    except IncomeReport.DoesNotExist:
        logger.warning(f"Invalid verification code accessed: {verification_code}")
        return Response(
            {
                'error': 'Invalid verification code',
                'message': 'The verification code you provided is not valid.',
                'verified': False,
                'status_class': 'invalid'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        logger.error(f"Public verification failed: {str(e)}")
        return Response(
            {
                'error': 'Verification failed',
                'message': 'Unable to verify document at this time.',
                'verified': False,
                'status_class': 'error'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
