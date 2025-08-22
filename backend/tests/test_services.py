"""
Service tests for Kitako backend
"""

import tempfile
import os
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
from django.utils import timezone
from decimal import Decimal
from datetime import date

from transactions.models import FileUpload, Transaction
from reports.models import IncomeReport
from reports.services import IncomeReportGenerator
from ai_processing.services import TransactionCategorizationService, FinancialSummaryService
from backend.encryption import DataEncryption, HashUtility

User = get_user_model()


class TransactionProcessorTest(TestCase):
    """Test transaction processing services"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!'
        )
    
    def test_csv_file_upload(self):
        """Test CSV file upload"""
        csv_content = """Date,Description,Amount,Type
2024-01-15,Freelance Payment,5000.00,Income
2024-01-16,Grocery Shopping,-1500.00,Expense
2024-01-17,Transportation,150.00,Expense"""
        
        # Create a Django File object from CSV content
        csv_file = ContentFile(csv_content.encode('utf-8'), name='test.csv')
        
        # Create file upload with the file already attached
        file_upload = FileUpload(
            user=self.user,
            file=csv_file,
            original_filename='test.csv',
            file_type='bank_statement',
            source='gcash'
        )
        file_upload.save()
        
        # Test file upload exists
        self.assertTrue(file_upload.file)
        self.assertEqual(file_upload.file_size, len(csv_content.encode('utf-8')))
    
    def test_invalid_file_upload(self):
        """Test processing of invalid file"""
        # Create file upload with minimal required fields
        csv_file = ContentFile(b"invalid,data", name='test.txt')
        
        file_upload = FileUpload(
            user=self.user,
            file=csv_file,
            original_filename='test.txt',
            file_type='other',
            source='other'
        )
        file_upload.save()
        
        # Test file upload creation
        self.assertTrue(file_upload.file)
        self.assertGreater(file_upload.file_size, 0)


class IncomeReportGeneratorTest(TestCase):
    """Test income report generation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!'
        )
        
        # Create test report
        self.report = IncomeReport.objects.create(
            user=self.user,
            report_type='monthly',
            date_from=date(2024, 1, 1),
            date_to=date(2024, 1, 31),
            purpose='loan_application',
            title='Test Income Report',
            total_income=Decimal('50000.00'),
            total_expenses=Decimal('30000.00'),
            net_income=Decimal('20000.00'),
            average_monthly_income=Decimal('50000.00'),
            income_breakdown={'salary': 30000.0, 'freelance': 20000.0},
            confidence_score=Decimal('95.5')
        )
    
    def test_generator_initialization(self):
        """Test report generator initialization"""
        generator = IncomeReportGenerator()
        self.assertIsNotNone(generator.styles)
    
    def test_ai_insights_generation(self):
        """Test AI insights generation method"""
        generator = IncomeReportGenerator()
        insights = generator.generate_ai_insights(self.report)
        
        self.assertIsInstance(insights, str)
        self.assertGreater(len(insights), 0)


class TransactionCategorizationTest(TestCase):
    """Test AI transaction categorization"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!'
        )
        self.service = TransactionCategorizationService()
        
    def test_service_initialization(self):
        """Test service initialization"""
        self.assertIsNotNone(self.service.client)
        
    @patch('ai_processing.services.OpenRouterClient.create_completion')
    def test_categorize_transactions(self, mock_completion):
        """Test transaction categorization"""
        mock_completion.return_value = {
            'success': True,
            'content': '{"categories": [{"description": "McDonald\'s purchase", "category": "Food", "confidence": 0.95}]}',
            'usage': {'total_tokens': 100}
        }
        
        transactions = [
            {'description': "McDonald's purchase", 'amount': 250.00}
        ]
        
        result = self.service.categorize_transactions(transactions)
        
        self.assertTrue(result['success'])
        mock_completion.assert_called_once()


class FinancialSummaryTest(TestCase):
    """Test financial summary generation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!'
        )
        self.service = FinancialSummaryService()
        
        # Create test transactions
        Transaction.objects.create(
            user=self.user,
            transaction_type='income',
            amount=Decimal('5000.00'),
            description='Salary',
            date=timezone.now().date()
        )
        Transaction.objects.create(
            user=self.user,
            transaction_type='expense', 
            amount=Decimal('1500.00'),
            description='Rent',
            date=timezone.now().date()
        )
        
    @patch('ai_processing.services.OpenRouterClient.create_completion')
    def test_generate_summary(self, mock_completion):
        """Test financial summary generation"""
        mock_completion.return_value = {
            'success': True,
            'content': 'Financial analysis shows stable income patterns.',
            'usage': {'total_tokens': 150}
        }
        
        transactions_data = [
            {'description': 'Salary', 'amount': 5000.00, 'type': 'income'},
            {'description': 'Rent', 'amount': 1500.00, 'type': 'expense'}
        ]
        date_range = {'start': '2024-01-01', 'end': '2024-01-31'}
        
        result = self.service.generate_summary(transactions_data, date_range)
        
        self.assertTrue(result['success'])
        self.assertIn('summary', result)
        mock_completion.assert_called_once()


class EncryptionTest(TestCase):
    """Test encryption services"""
    
    def setUp(self):
        self.encryption = DataEncryption()
        self.hash_util = HashUtility()
        
    def test_data_encryption(self):
        """Test data encryption and decryption"""
        original_data = "Sensitive financial information"
        
        encrypted_data = self.encryption.encrypt(original_data)
        self.assertNotEqual(original_data, encrypted_data)
        
        decrypted_data = self.encryption.decrypt(encrypted_data)
        self.assertEqual(original_data, decrypted_data)
        
    def test_hashing(self):
        """Test data hashing"""
        data = "test@example.com"
        hash_value = self.hash_util.hash_data(data)
        
        self.assertIsInstance(hash_value, str)
        self.assertNotEqual(data, hash_value)
        
        # Same data should produce same hash
        hash_value2 = self.hash_util.hash_data(data)
        self.assertEqual(hash_value, hash_value2)
