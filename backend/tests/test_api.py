"""
API tests for Kitako backend
"""

import json
import tempfile
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from decimal import Decimal
from datetime import date

from accounts.models import UserProfile
from transactions.models import FileUpload, Transaction
from reports.models import IncomeReport

User = get_user_model()


class AuthenticationAPITest(APITestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPassword123!',
            'password_confirm': 'TestPassword123!',
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'primary_occupation': 'freelancer',
            'preferred_language': 'en'
        }
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post('/api/auth/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        
        # Check user was created
        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.first_name, 'Juan')
        self.assertTrue(hasattr(user, 'profile'))
    
    def test_user_login(self):
        """Test user login"""
        # Create user first
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!'
        )
        
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        }
        
        response = self.client.post('/api/auth/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        # Refresh token is set as httpOnly cookie, not in response data
        self.assertIn('refresh_token', response.cookies)
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/auth/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_profile_access(self):
        """Test accessing user profile"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!'
        )
        UserProfile.objects.create(user=user)
        
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/auth/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')


class TransactionAPITest(APITestCase):
    """Test transaction endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!'
        )
        self.client = APIClient()
        
        # Generate JWT token for authentication
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_file_upload(self):
        """Test file upload"""
        # Create a test CSV file
        csv_content = "Date,Description,Amount,Type\n2024-01-15,Test Transaction,1000.00,Income"
        uploaded_file = SimpleUploadedFile(
            "test.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        data = {
            'file': uploaded_file,
            'file_type': 'bank_statement',
            'source': 'gcash',
            'description': 'Test upload'
        }
        
        response = self.client.post('/api/transactions/upload/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file_upload', response.data)
        
        # Check file upload was created
        file_upload = FileUpload.objects.get(user=self.user)
        self.assertEqual(file_upload.file_type, 'bank_statement')
        self.assertEqual(file_upload.source, 'gcash')
    
    def test_file_upload_unauthorized(self):
        """Test file upload without authentication"""
        self.client.force_authenticate(user=None)
        
        csv_content = "Date,Description,Amount,Type\n2024-01-15,Test Transaction,1000.00,Income"
        uploaded_file = SimpleUploadedFile(
            "test.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        data = {
            'file': uploaded_file,
            'file_type': 'bank_statement',
            'source': 'gcash'
        }
        
        response = self.client.post('/api/transactions/upload/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_transaction_list(self):
        """Test transaction list endpoint"""
        # Create test transactions
        Transaction.objects.create(
            user=self.user,
            date='2024-01-15',
            amount=Decimal('1000.00'),
            description='Test income',
            transaction_type='income',
            category='salary'
        )
        
        Transaction.objects.create(
            user=self.user,
            date='2024-01-16',
            amount=Decimal('500.00'),
            description='Test expense',
            transaction_type='expense',
            category='food'
        )
        
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_transaction_filtering(self):
        """Test transaction filtering"""
        # Create test transactions
        Transaction.objects.create(
            user=self.user,
            date='2024-01-15',
            amount=Decimal('1000.00'),
            description='Test income',
            transaction_type='income',
            category='salary'
        )
        
        Transaction.objects.create(
            user=self.user,
            date='2024-01-16',
            amount=Decimal('500.00'),
            description='Test expense',
            transaction_type='expense',
            category='food'
        )
        
        # Filter by type
        response = self.client.get('/api/transactions/?type=income')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['transaction_type'], 'income')
    
    def test_transaction_summary(self):
        """Test transaction summary endpoint"""
        # Create test transactions
        Transaction.objects.create(
            user=self.user,
            date='2024-01-15',
            amount=Decimal('1000.00'),
            description='Test income',
            transaction_type='income',
            category='salary'
        )
        
        Transaction.objects.create(
            user=self.user,
            date='2024-01-16',
            amount=Decimal('500.00'),
            description='Test expense',
            transaction_type='expense',
            category='food'
        )
        
        response = self.client.get('/api/transactions/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'], 1000.0)
        self.assertEqual(response.data['total_expenses'], 500.0)
        self.assertEqual(response.data['net_income'], 500.0)


class ReportsAPITest(APITestCase):
    """Test reports endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPassword123!'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test transactions
        Transaction.objects.create(
            user=self.user,
            date='2024-01-15',
            amount=Decimal('5000.00'),
            description='Freelance payment',
            transaction_type='income',
            category='freelance'
        )
        
        Transaction.objects.create(
            user=self.user,
            date='2024-01-16',
            amount=Decimal('1200.00'),
            description='Grocery shopping',
            transaction_type='expense',
            category='food'
        )
    
    def test_create_income_report(self):
        """Test income report creation"""
        report_data = {
            'report_type': 'custom',
            'date_from': '2024-01-01',
            'date_to': '2024-01-31',
            'purpose': 'loan_application',
            'title': 'Test Income Report'
        }
        
        response = self.client.post('/api/reports/create/', report_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('report', response.data)
        
        # Check report was created
        report = IncomeReport.objects.get(user=self.user)
        self.assertEqual(report.title, 'Test Income Report')
        self.assertEqual(report.total_income, Decimal('5000.00'))
        self.assertEqual(report.total_expenses, Decimal('1200.00'))
    
    def test_list_income_reports(self):
        """Test listing income reports"""
        # Clear any existing reports for this user first
        IncomeReport.objects.filter(user=self.user).delete()
        
        # Create test report
        IncomeReport.objects.create(
            user=self.user,
            report_type='monthly',
            date_from=date(2024, 1, 1),
            date_to=date(2024, 1, 31),
            purpose='loan_application',
            title='Test Report',
            total_income=Decimal('5000.00'),
            total_expenses=Decimal('1200.00'),
            net_income=Decimal('3800.00'),
            average_monthly_income=Decimal('5000.00'),
            confidence_score=Decimal('100.0')
        )
        
        response = self.client.get('/api/reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the count in pagination or the results array length
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['count'], 1)
        else:
            self.assertEqual(len(response.data), 1)
    
    def test_report_verification(self):
        """Test report verification"""
        # Create test report
        report = IncomeReport.objects.create(
            user=self.user,
            report_type='monthly',
            date_from=date(2024, 1, 1),
            date_to=date(2024, 1, 31),
            purpose='loan_application',
            title='Test Report',
            total_income=Decimal('5000.00'),
            total_expenses=Decimal('1200.00'),
            net_income=Decimal('3800.00'),
            average_monthly_income=Decimal('5000.00'),
            confidence_score=Decimal('100.0'),
            verification_code='TEST123456'
        )
        
        # Test verification (no auth required)
        self.client.force_authenticate(user=None)
        verification_data = {'verification_code': 'TEST123456'}
        
        response = self.client.post('/api/reports/verify/', verification_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['verified'])
        self.assertEqual(str(response.data['report_id']), str(report.id))
