"""
Unit tests for Kitako models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, datetime
from django.utils import timezone

from accounts.models import User, UserProfile
from transactions.models import FileUpload, Transaction
from reports.models import IncomeReport
from ai_processing.models import AIProcessingJob, AIPromptTemplate, AIModelUsage

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'password': 'testpass123',
            'phone_number': '+639123456789'
        }
    
    def test_create_user(self):
        """Test user creation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.full_name, 'Juan Dela Cruz')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_full_name_with_middle_name(self):
        """Test full name with middle name"""
        self.user_data['middle_name'] = 'Santos'
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.full_name, 'Juan Santos Dela Cruz')
    
    def test_user_full_address(self):
        """Test full address property"""
        user = User.objects.create_user(**self.user_data)
        user.address_line_1 = '123 Main St'
        user.city = 'Manila'
        user.province = 'Metro Manila'
        user.postal_code = '1000'
        user.save()
        
        expected_address = '123 Main St, Manila, Metro Manila, 1000'
        self.assertEqual(user.full_address, expected_address)
    
    def test_phone_number_validation(self):
        """Test phone number validation"""
        # Valid phone numbers
        valid_phones = ['+639123456789', '09123456789']
        for i, phone in enumerate(valid_phones):
            user_data = self.user_data.copy()
            user_data['username'] = f"testuser_valid_{i}"
            user_data['email'] = f"valid{i}@example.com"
            user_data['phone_number'] = phone
            user = User.objects.create_user(**user_data)
            user.full_clean()  # Should not raise ValidationError

        # Invalid phone numbers should raise ValidationError
        invalid_phones = ['123', 'invalid', '+1234567890']
        for i, phone in enumerate(invalid_phones):
            user_data = self.user_data.copy()
            user_data['username'] = f"testuser_invalid_{i}"
            user_data['email'] = f"invalid{i}@example.com"
            user_data['phone_number'] = phone
            user = User.objects.create_user(**user_data)
            with self.assertRaises(ValidationError):
                user.full_clean()


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_create_user_profile(self):
        """Test user profile creation"""
        profile = UserProfile.objects.create(
            user=self.user,
            estimated_monthly_income=Decimal('50000.00'),
            has_gcash=True,
            has_bank_account=True
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.estimated_monthly_income, Decimal('50000.00'))
        self.assertTrue(profile.has_gcash)
        self.assertTrue(profile.has_bank_account)


class FileUploadModelTest(TestCase):
    """Test cases for FileUpload model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_create_file_upload(self):
        """Test file upload creation"""
        file_upload = FileUpload.objects.create(
            user=self.user,
            original_filename='test.csv',
            file_size=1024,
            file_type='bank_statement',
            source='gcash'
        )
        
        self.assertEqual(file_upload.user, self.user)
        self.assertEqual(file_upload.original_filename, 'test.csv')
        self.assertEqual(file_upload.processing_status, 'uploaded')


class TransactionModelTest(TestCase):
    """Test cases for Transaction model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.file_upload = FileUpload.objects.create(
            user=self.user,
            original_filename='test.csv',
            file_size=1024,
            file_type='bank_statement',
            source='gcash'
        )
    
    def test_create_transaction(self):
        """Test transaction creation"""
        transaction = Transaction.objects.create(
            user=self.user,
            file_upload=self.file_upload,
            date=timezone.now(),
            amount=Decimal('1000.00'),
            description='Test transaction',
            transaction_type='income',
            category='salary'
        )
        
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, Decimal('1000.00'))
        self.assertTrue(transaction.is_income)
        self.assertFalse(transaction.is_expense)
    
    def test_transaction_properties(self):
        """Test transaction properties"""
        income_txn = Transaction.objects.create(
            user=self.user,
            date=timezone.now(),
            amount=Decimal('1000.00'),
            description='Income transaction',
            transaction_type='income',
            category='salary'
        )
        
        expense_txn = Transaction.objects.create(
            user=self.user,
            date=timezone.now(),
            amount=Decimal('500.00'),
            description='Expense transaction',
            transaction_type='expense',
            category='food'
        )
        
        self.assertTrue(income_txn.is_income)
        self.assertFalse(income_txn.is_expense)
        self.assertFalse(expense_txn.is_income)
        self.assertTrue(expense_txn.is_expense)


class IncomeReportModelTest(TestCase):
    """Test cases for IncomeReport model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_create_income_report(self):
        """Test income report creation"""
        report = IncomeReport.objects.create(
            user=self.user,
            report_type='monthly',
            date_from=date(2024, 1, 1),
            date_to=date(2024, 1, 31),
            purpose='loan_application',
            title='Test Report',
            total_income=Decimal('50000.00'),
            total_expenses=Decimal('30000.00'),
            net_income=Decimal('20000.00'),
            average_monthly_income=Decimal('50000.00'),
            confidence_score=Decimal('85.50')
        )
        
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.total_income, Decimal('50000.00'))
        self.assertIsNotNone(report.verification_code)
        self.assertIsNotNone(report.access_token)
    
    def test_report_expiration(self):
        """Test report expiration"""
        report = IncomeReport.objects.create(
            user=self.user,
            report_type='monthly',
            date_from=date(2024, 1, 1),
            date_to=date(2024, 1, 31),
            purpose='loan_application',
            title='Test Report',
            total_income=Decimal('50000.00'),
            total_expenses=Decimal('30000.00'),
            net_income=Decimal('20000.00'),
            average_monthly_income=Decimal('50000.00'),
            confidence_score=Decimal('100.0'),
            expires_at=timezone.now() - timezone.timedelta(days=1)  # Expired
        )
        
        self.assertTrue(report.is_expired)


class AIProcessingJobModelTest(TestCase):
    """Test cases for AIProcessingJob model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_create_ai_job(self):
        """Test AI processing job creation"""
        job = AIProcessingJob.objects.create(
            user=self.user,
            job_type='categorize_transactions',
            input_data={'transaction_count': 10},
            status='pending'
        )
        
        self.assertEqual(job.user, self.user)
        self.assertEqual(job.job_type, 'categorize_transactions')
        self.assertEqual(job.status, 'pending')
        self.assertEqual(job.progress_percentage, 0)


class AIPromptTemplateModelTest(TestCase):
    """Test cases for AIPromptTemplate model"""
    
    def test_create_prompt_template(self):
        """Test AI prompt template creation"""
        template = AIPromptTemplate.objects.create(
            name='Transaction Categorization',
            description='Template for categorizing transactions',
            task_type='transaction_categorization',
            system_prompt='You are an AI assistant...',
            user_prompt_template='Categorize these transactions: {transaction_data}',
            model_name='claude-3-sonnet',
            temperature=Decimal('0.10'),
            max_tokens=4000
        )
        
        self.assertEqual(template.name, 'Transaction Categorization')
        self.assertEqual(template.task_type, 'transaction_categorization')
        self.assertEqual(template.temperature, Decimal('0.10'))
        self.assertTrue(template.is_active)


class AIModelUsageModelTest(TestCase):
    """Test cases for AIModelUsage model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.job = AIProcessingJob.objects.create(
            user=self.user,
            job_type='categorize_transactions',
            input_data={'transaction_count': 10}
        )
    
    def test_create_ai_usage(self):
        """Test AI model usage creation"""
        usage = AIModelUsage.objects.create(
            user=self.user,
            processing_job=self.job,
            model_name='claude-3-sonnet',
            provider='openrouter',
            input_tokens=1000,
            output_tokens=500,
            input_cost_per_token=Decimal('0.000003'),
            output_cost_per_token=Decimal('0.000015')
        )
        
        self.assertEqual(usage.total_tokens, 1500)
        expected_cost = (1000 * Decimal('0.000003')) + (500 * Decimal('0.000015'))
        self.assertEqual(usage.total_cost_usd, expected_cost)
