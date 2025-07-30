"""
Privacy Management for Kitako MVP

This module handles GDPR compliance, data anonymization,
and user privacy rights.
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from backend.encryption import PrivacyUtility

logger = logging.getLogger('kitako')
User = get_user_model()


class PrivacyManager:
    """
    Manager for handling user privacy and GDPR compliance
    """
    
    def __init__(self, user):
        self.user = user
    
    def export_user_data(self) -> dict:
        """
        Export all user data for GDPR compliance
        """
        try:
            # Basic user information
            user_data = {
                'personal_info': {
                    'email': self.user.email,
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                    'middle_name': self.user.middle_name,
                    'phone_number': self.user.phone_number,
                    'address': {
                        'line_1': self.user.address_line_1,
                        'line_2': self.user.address_line_2,
                        'city': self.user.city,
                        'province': self.user.province,
                        'postal_code': self.user.postal_code,
                    },
                    'occupation': self.user.primary_occupation,
                    'occupation_description': self.user.occupation_description,
                    'preferred_language': self.user.preferred_language,
                    'date_joined': self.user.date_joined.isoformat(),
                    'last_login': self.user.last_login.isoformat() if self.user.last_login else None,
                }
            }
            
            # Profile information
            if hasattr(self.user, 'profile'):
                profile = self.user.profile
                user_data['profile'] = {
                    'estimated_monthly_income': float(profile.estimated_monthly_income) if profile.estimated_monthly_income else None,
                    'financial_services': {
                        'has_gcash': profile.has_gcash,
                        'has_paymaya': profile.has_paymaya,
                        'has_grabpay': profile.has_grabpay,
                        'has_coins_ph': profile.has_coins_ph,
                        'has_other_ewallet': profile.has_other_ewallet,
                        'has_bank_account': profile.has_bank_account,
                    },
                    'business_info': {
                        'business_name': profile.business_name,
                        'business_type': profile.business_type,
                        'business_registration_number': profile.business_registration_number,
                    }
                }
            
            # File uploads
            file_uploads = []
            for upload in self.user.file_uploads.all():
                file_uploads.append({
                    'id': str(upload.id),
                    'filename': upload.original_filename,
                    'file_type': upload.file_type,
                    'source': upload.source,
                    'upload_date': upload.created_at.isoformat(),
                    'processing_status': upload.processing_status,
                })
            user_data['file_uploads'] = file_uploads
            
            # Transactions (anonymized amounts for privacy)
            transactions = []
            for txn in self.user.transactions.all():
                transactions.append({
                    'id': str(txn.id),
                    'date': txn.date.isoformat(),
                    'amount': float(txn.amount),
                    'description': txn.description,
                    'category': txn.category,
                    'transaction_type': txn.transaction_type,
                    'source_platform': txn.source_platform,
                    'created_at': txn.created_at.isoformat(),
                })
            user_data['transactions'] = transactions
            
            # Income reports
            reports = []
            for report in self.user.income_reports.all():
                reports.append({
                    'id': str(report.id),
                    'title': report.title,
                    'report_type': report.report_type,
                    'date_from': report.date_from.isoformat(),
                    'date_to': report.date_to.isoformat(),
                    'purpose': report.purpose,
                    'total_income': float(report.total_income),
                    'total_expenses': float(report.total_expenses),
                    'net_income': float(report.net_income),
                    'created_at': report.created_at.isoformat(),
                    'verification_code': report.verification_code,
                })
            user_data['income_reports'] = reports
            
            # AI processing jobs
            ai_jobs = []
            for job in self.user.ai_jobs.all():
                ai_jobs.append({
                    'id': str(job.id),
                    'job_type': job.job_type,
                    'status': job.status,
                    'created_at': job.created_at.isoformat(),
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                })
            user_data['ai_processing_jobs'] = ai_jobs
            
            logger.info(f"Exported data for user {self.user.email}")
            return user_data
            
        except Exception as e:
            logger.error(f"Data export failed for user {self.user.email}: {str(e)}")
            raise
    
    def anonymize_user_data(self):
        """
        Anonymize user data while preserving functionality
        """
        try:
            # Anonymize personal information
            self.user.email = f"anonymized_{self.user.id}@kitako.local"
            self.user.first_name = PrivacyUtility.anonymize_name(self.user.first_name)
            self.user.last_name = PrivacyUtility.anonymize_name(self.user.last_name)
            self.user.middle_name = PrivacyUtility.anonymize_name(self.user.middle_name) if self.user.middle_name else None
            self.user.phone_number = PrivacyUtility.anonymize_phone(self.user.phone_number) if self.user.phone_number else None
            
            # Clear address information
            self.user.address_line_1 = "ANONYMIZED"
            self.user.address_line_2 = ""
            self.user.city = "ANONYMIZED"
            self.user.province = "ANONYMIZED"
            self.user.postal_code = "0000"
            
            # Clear occupation details
            self.user.occupation_description = "ANONYMIZED"
            
            self.user.save()
            
            # Anonymize profile data
            if hasattr(self.user, 'profile'):
                profile = self.user.profile
                profile.other_ewallet_details = "ANONYMIZED"
                profile.bank_names = "ANONYMIZED"
                profile.business_name = "ANONYMIZED" if profile.business_name else None
                profile.business_registration_number = "ANONYMIZED" if profile.business_registration_number else None
                profile.save()
            
            # Anonymize transaction descriptions
            for txn in self.user.transactions.all():
                txn.description = "ANONYMIZED TRANSACTION"
                txn.counterparty = "ANONYMIZED"
                txn.reference_number = "ANON" + str(txn.id)[:8]
                txn.save()
            
            # Anonymize report titles and descriptions
            for report in self.user.income_reports.all():
                report.title = f"ANONYMIZED REPORT {report.id}"
                report.purpose_description = "ANONYMIZED"
                report.summary = "This report has been anonymized."
                report.ai_insights = "ANONYMIZED"
                report.save()
            
            logger.info(f"Anonymized data for user {self.user.email}")
            
        except Exception as e:
            logger.error(f"Data anonymization failed for user {self.user.email}: {str(e)}")
            raise
    
    def delete_user_data(self, keep_anonymized=True):
        """
        Delete user data with option to keep anonymized records
        """
        try:
            if keep_anonymized:
                # Anonymize data first
                self.anonymize_user_data()
                logger.info(f"User data anonymized for {self.user.email}")
            else:
                # Delete all related data
                self.user.file_uploads.all().delete()
                self.user.transactions.all().delete()
                self.user.income_reports.all().delete()
                self.user.ai_jobs.all().delete()
                
                # Delete user account
                self.user.delete()
                logger.info(f"User data completely deleted for {self.user.email}")
                
        except Exception as e:
            logger.error(f"Data deletion failed for user {self.user.email}: {str(e)}")
            raise
    
    def cleanup_old_data(self):
        """
        Clean up old data based on retention policies
        """
        try:
            # Delete old file uploads (older than retention period)
            retention_date = timezone.now() - timedelta(days=settings.DATA_RETENTION_DAYS)
            old_uploads = self.user.file_uploads.filter(created_at__lt=retention_date)
            old_uploads_count = old_uploads.count()
            old_uploads.delete()
            
            # Delete old reports
            report_retention_date = timezone.now() - timedelta(days=settings.REPORT_RETENTION_DAYS)
            old_reports = self.user.income_reports.filter(created_at__lt=report_retention_date)
            old_reports_count = old_reports.count()
            old_reports.delete()
            
            # Delete old AI jobs
            old_ai_jobs = self.user.ai_jobs.filter(created_at__lt=retention_date)
            old_ai_jobs_count = old_ai_jobs.count()
            old_ai_jobs.delete()
            
            logger.info(f"Cleaned up old data for user {self.user.email}: {old_uploads_count} uploads, {old_reports_count} reports, {old_ai_jobs_count} AI jobs")
            
        except Exception as e:
            logger.error(f"Data cleanup failed for user {self.user.email}: {str(e)}")
            raise


def export_user_data(user_id: int) -> dict:
    """
    Export user data for GDPR compliance
    """
    try:
        user = User.objects.get(id=user_id)
        privacy_manager = PrivacyManager(user)
        return privacy_manager.export_user_data()
    except User.DoesNotExist:
        raise ValueError(f"User with ID {user_id} not found")


def anonymize_user(user_id: int):
    """
    Anonymize user data
    """
    try:
        user = User.objects.get(id=user_id)
        privacy_manager = PrivacyManager(user)
        privacy_manager.anonymize_user_data()
    except User.DoesNotExist:
        raise ValueError(f"User with ID {user_id} not found")


def delete_user_data(user_id: int, keep_anonymized: bool = True):
    """
    Delete user data with privacy compliance
    """
    try:
        user = User.objects.get(id=user_id)
        privacy_manager = PrivacyManager(user)
        privacy_manager.delete_user_data(keep_anonymized)
    except User.DoesNotExist:
        raise ValueError(f"User with ID {user_id} not found")
