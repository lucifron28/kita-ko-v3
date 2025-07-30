from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class AIProcessingJob(models.Model):
    """
    Model to track AI processing jobs for transaction categorization and analysis
    """
    JOB_TYPE_CHOICES = [
        ('categorize_transactions', 'Categorize Transactions'),
        ('generate_summary', 'Generate Summary'),
        ('detect_anomalies', 'Detect Anomalies'),
        ('extract_insights', 'Extract Insights'),
        ('validate_data', 'Validate Data'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_jobs')

    # Job Configuration
    job_type = models.CharField(max_length=30, choices=JOB_TYPE_CHOICES)
    input_data = models.JSONField(help_text="Input data for the AI processing job")
    parameters = models.JSONField(default=dict, help_text="Additional parameters for the job")

    # Processing Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress_percentage = models.PositiveIntegerField(default=0)

    # Results
    output_data = models.JSONField(null=True, blank=True, help_text="Output from the AI processing")
    error_message = models.TextField(blank=True)

    # AI Model Information
    model_used = models.CharField(max_length=100, blank=True, help_text="AI model used for processing")
    model_version = models.CharField(max_length=50, blank=True)

    # Performance Metrics
    processing_time_seconds = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True
    )
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kitako_ai_processing_jobs'
        verbose_name = 'AI Processing Job'
        verbose_name_plural = 'AI Processing Jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['job_type', 'status']),
        ]

    def __str__(self):
        return f"{self.job_type} - {self.user.email} - {self.status}"


class AIPromptTemplate(models.Model):
    """
    Model to store and manage AI prompt templates for different tasks
    """
    TASK_TYPE_CHOICES = [
        ('transaction_categorization', 'Transaction Categorization'),
        ('income_summary', 'Income Summary'),
        ('expense_analysis', 'Expense Analysis'),
        ('anomaly_detection', 'Anomaly Detection'),
        ('insight_generation', 'Insight Generation'),
        ('data_validation', 'Data Validation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Template Information
    name = models.CharField(max_length=255)
    description = models.TextField()
    task_type = models.CharField(max_length=30, choices=TASK_TYPE_CHOICES)

    # Prompt Content
    system_prompt = models.TextField(help_text="System prompt for the AI model")
    user_prompt_template = models.TextField(
        help_text="User prompt template with placeholders like {transaction_data}"
    )

    # Configuration
    model_name = models.CharField(max_length=100, default='claude-3-sonnet')
    temperature = models.DecimalField(max_digits=3, decimal_places=2, default=0.1)
    max_tokens = models.PositiveIntegerField(default=4000)

    # Validation
    expected_output_format = models.TextField(
        blank=True,
        help_text="Description of expected output format"
    )
    validation_schema = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON schema for validating AI output"
    )

    # Usage Tracking
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        help_text="Success rate percentage"
    )

    # Version Control
    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kitako_ai_prompt_templates'
        verbose_name = 'AI Prompt Template'
        verbose_name_plural = 'AI Prompt Templates'
        ordering = ['-created_at']
        unique_together = ['task_type', 'version', 'is_active']

    def __str__(self):
        return f"{self.name} (v{self.version})"


class AIModelUsage(models.Model):
    """
    Model to track AI model usage and costs
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage')
    processing_job = models.ForeignKey(
        AIProcessingJob,
        on_delete=models.CASCADE,
        related_name='usage_records',
        null=True,
        blank=True
    )

    # Model Information
    model_name = models.CharField(max_length=100)
    provider = models.CharField(max_length=50, default='openrouter')

    # Usage Metrics
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)

    # Cost Information
    input_cost_per_token = models.DecimalField(max_digits=12, decimal_places=8, default=0)
    output_cost_per_token = models.DecimalField(max_digits=12, decimal_places=8, default=0)
    total_cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    # Performance
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kitako_ai_model_usage'
        verbose_name = 'AI Model Usage'
        verbose_name_plural = 'AI Model Usage Records'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['model_name']),
        ]

    def __str__(self):
        return f"{self.model_name} - {self.total_tokens} tokens - ${self.total_cost_usd}"

    def save(self, *args, **kwargs):
        # Calculate total tokens and cost
        self.total_tokens = self.input_tokens + self.output_tokens
        self.total_cost_usd = (
            (self.input_tokens * self.input_cost_per_token) +
            (self.output_tokens * self.output_cost_per_token)
        )
        super().save(*args, **kwargs)
