from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import uuid
import os

User = get_user_model()


def upload_to_user_files(instance, filename):
    """Generate upload path for user files"""
    return f'user_files/{instance.user.id}/{filename}'


class FileUpload(models.Model):
    """
    Model for storing uploaded financial documents
    """
    FILE_TYPE_CHOICES = [
        ('bank_statement', 'Bank Statement'),
        ('ewallet_statement', 'E-wallet Statement'),
        ('receipt', 'Receipt'),
        ('invoice', 'Invoice'),
        ('payslip', 'Payslip'),
        ('other', 'Other'),
    ]

    SOURCE_CHOICES = [
        ('gcash', 'GCash'),
        ('paymaya', 'PayMaya'),
        ('grabpay', 'GrabPay'),
        ('coins_ph', 'Coins.ph'),
        ('bpi', 'BPI'),
        ('bdo', 'BDO'),
        ('metrobank', 'Metrobank'),
        ('unionbank', 'UnionBank'),
        ('security_bank', 'Security Bank'),
        ('pnb', 'PNB'),
        ('landbank', 'Landbank'),
        ('other_bank', 'Other Bank'),
        ('other_ewallet', 'Other E-wallet'),
        ('manual_entry', 'Manual Entry'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_uploads')

    # File Information
    file = models.FileField(
        upload_to=upload_to_user_files,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'csv', 'xlsx', 'xls', 'jpg', 'jpeg', 'png', 'txt']
        )]
    )
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)

    # Processing Status
    PROCESSING_STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    ]
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='uploaded'
    )
    processing_error = models.TextField(blank=True, null=True)

    # Metadata
    date_range_start = models.DateField(null=True, blank=True)
    date_range_end = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'kitako_file_uploads'
        verbose_name = 'File Upload'
        verbose_name_plural = 'File Uploads'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_filename} - {self.user.email}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.original_filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """
    Model for individual financial transactions extracted from uploaded files
    """
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('fee', 'Fee'),
        ('refund', 'Refund'),
        ('other', 'Other'),
    ]

    CATEGORY_CHOICES = [
        # Income categories
        ('salary', 'Salary'),
        ('freelance', 'Freelance Work'),
        ('business_income', 'Business Income'),
        ('commission', 'Commission'),
        ('tips', 'Tips'),
        ('rental_income', 'Rental Income'),
        ('investment_income', 'Investment Income'),
        ('government_benefit', 'Government Benefit'),
        ('loan_received', 'Loan Received'),
        ('gift_received', 'Gift Received'),

        # Expense categories
        ('food', 'Food & Dining'),
        ('transportation', 'Transportation'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('shopping', 'Shopping'),
        ('loan_payment', 'Loan Payment'),
        ('insurance', 'Insurance'),
        ('business_expense', 'Business Expense'),
        ('family_support', 'Family Support'),

        # Transfer categories
        ('bank_transfer', 'Bank Transfer'),
        ('ewallet_transfer', 'E-wallet Transfer'),
        ('cash_in', 'Cash In'),
        ('cash_out', 'Cash Out'),

        # Fee categories
        ('transaction_fee', 'Transaction Fee'),
        ('service_fee', 'Service Fee'),
        ('atm_fee', 'ATM Fee'),

        ('other', 'Other'),
    ]

    CONFIDENCE_LEVEL_CHOICES = [
        ('high', 'High (90-100%)'),
        ('medium', 'Medium (70-89%)'),
        ('low', 'Low (50-69%)'),
        ('very_low', 'Very Low (<50%)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    file_upload = models.ForeignKey(
        FileUpload,
        on_delete=models.CASCADE,
        related_name='transactions',
        null=True,
        blank=True
    )

    # Transaction Details
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='PHP')
    description = models.TextField()
    reference_number = models.CharField(max_length=100, blank=True)

    # Categorization
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=100, blank=True)

    # AI Processing Information
    ai_categorized = models.BooleanField(default=False)
    ai_confidence = models.CharField(
        max_length=10,
        choices=CONFIDENCE_LEVEL_CHOICES,
        null=True,
        blank=True
    )
    ai_reasoning = models.TextField(blank=True, help_text="AI explanation for categorization")

    # Manual Override
    manually_verified = models.BooleanField(default=False)
    manual_notes = models.TextField(blank=True)

    # Source Information
    source_platform = models.CharField(max_length=50, blank=True)  # e.g., "GCash", "BPI"
    counterparty = models.CharField(max_length=255, blank=True)  # Who the transaction was with

    # Flags
    is_anomaly = models.BooleanField(default=False)
    anomaly_reason = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kitako_transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['transaction_type', 'category']),
            models.Index(fields=['amount']),
        ]

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} - {self.description[:50]} - ₱{self.amount}"

    @property
    def is_income(self):
        return self.transaction_type == 'income'

    @property
    def is_expense(self):
        return self.transaction_type == 'expense'
