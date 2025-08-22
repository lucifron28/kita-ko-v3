from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import uuid
import hashlib
import os

User = get_user_model()


def upload_to_reports(instance, filename):
    """Generate upload path for generated reports"""
    return f'reports/{instance.user.id}/{filename}'


class IncomeReport(models.Model):
    """
    Model for generated proof-of-income reports
    """
    REPORT_TYPE_CHOICES = [
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('annual', 'Annual Report'),
        ('custom', 'Custom Date Range'),
    ]

    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]

    PURPOSE_CHOICES = [
        ('loan_application', 'Loan Application'),
        ('government_subsidy', 'Government Subsidy'),
        ('insurance_application', 'Insurance Application'),
        ('rental_application', 'Rental Application'),
        ('business_registration', 'Business Registration'),
        ('visa_application', 'Visa Application'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='income_reports')

    # Report Configuration
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    date_from = models.DateField()
    date_to = models.DateField()
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    purpose_description = models.TextField(blank=True)

    # Report Content
    title = models.CharField(max_length=255)
    summary = models.TextField(help_text="AI-generated summary of financial activity")
    total_income = models.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2)
    net_income = models.DecimalField(max_digits=12, decimal_places=2)
    average_monthly_income = models.DecimalField(max_digits=12, decimal_places=2)

    # Income Breakdown
    income_breakdown = models.JSONField(
        default=dict,
        help_text="Breakdown of income by category"
    )
    expense_breakdown = models.JSONField(
        default=dict,
        help_text="Breakdown of expenses by category"
    )
    monthly_trends = models.JSONField(
        default=dict,
        help_text="Monthly income/expense trends"
    )

    # Data Sources
    data_sources = models.JSONField(
        default=list,
        help_text="List of data sources used (e.g., GCash, BPI, etc.)"
    )
    transaction_count = models.PositiveIntegerField(default=0)

    # AI Analysis
    ai_insights = models.TextField(blank=True, help_text="AI-generated insights and patterns")
    anomalies_detected = models.JSONField(
        default=list,
        help_text="List of anomalies detected in the data"
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Overall confidence score of the report (0-100)"
    )

    # File Information
    pdf_file = models.FileField(
        upload_to=upload_to_reports,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        null=True,
        blank=True
    )
    file_size = models.PositiveIntegerField(null=True, blank=True)

    # Verification
    document_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 hash for verification")
    verification_code = models.CharField(max_length=20, blank=True, unique=True)

    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    generation_error = models.TextField(blank=True)

    # Access Control
    is_public = models.BooleanField(default=False)
    access_token = models.CharField(max_length=64, blank=True, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'kitako_income_reports'
        verbose_name = 'Income Report'
        verbose_name_plural = 'Income Reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['verification_code']),
            models.Index(fields=['access_token']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    def save(self, *args, **kwargs):
        # Generate verification code if not exists
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()

        # Generate access token if not exists
        if not self.access_token:
            self.access_token = self.generate_access_token()

        # Calculate document hash if PDF exists
        if self.pdf_file and not self.document_hash:
            self.document_hash = self.calculate_file_hash()

        super().save(*args, **kwargs)

    def generate_verification_code(self):
        """Generate a unique verification code"""
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            if not IncomeReport.objects.filter(verification_code=code).exists():
                return code

    def generate_access_token(self):
        """Generate a unique access token"""
        import secrets
        while True:
            token = secrets.token_urlsafe(32)
            if not IncomeReport.objects.filter(access_token=token).exists():
                return token

    def calculate_file_hash(self):
        """Calculate SHA-256 hash of the PDF file"""
        if not self.pdf_file:
            return ""

        hash_sha256 = hashlib.sha256()
        for chunk in self.pdf_file.chunks():
            hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    @property
    def is_expired(self):
        """Check if the report has expired"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
