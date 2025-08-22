"""
Transaction Processing Pipeline for Kitako MVP

This module handles parsing and processing of uploaded financial documents
to extract transaction data.
"""

import pandas as pd
import csv
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from django.core.files.uploadedfile import UploadedFile

from .models import FileUpload, Transaction

logger = logging.getLogger('kitako')


class TransactionProcessor:
    """
    Base class for processing different types of financial documents
    """
    
    def __init__(self, file_upload: FileUpload):
        self.file_upload = file_upload
        self.user = file_upload.user
    
    def process(self) -> Dict[str, Any]:
        """
        Process the uploaded file and extract transactions
        """
        try:
            # Update status
            self.file_upload.processing_status = 'processing'
            self.file_upload.save()
            
            # Determine file type and process accordingly
            file_extension = self.file_upload.original_filename.lower().split('.')[-1]
            
            if file_extension == 'csv':
                transactions_data = self._process_csv()
            elif file_extension in ['xlsx', 'xls']:
                transactions_data = self._process_excel()
            elif file_extension == 'pdf':
                transactions_data = self._process_pdf()
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Create transaction records
            created_transactions = self._create_transactions(transactions_data)
            
            # Update file upload status
            self.file_upload.processing_status = 'processed'
            self.file_upload.processed_at = timezone.now()
            self.file_upload.save()
            
            logger.info(f"Processed {len(created_transactions)} transactions from {self.file_upload.original_filename}")
            
            return {
                'success': True,
                'transactions_created': len(created_transactions),
                'transactions': created_transactions
            }
            
        except Exception as e:
            # Update file upload with error
            self.file_upload.processing_status = 'failed'
            self.file_upload.processing_error = str(e)
            self.file_upload.save()
            
            logger.error(f"Transaction processing failed for {self.file_upload.original_filename}: {str(e)}")
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_csv(self) -> List[Dict[str, Any]]:
        """
        Process CSV file to extract transaction data
        """
        transactions = []
        
        with open(self.file_upload.file.path, 'r', encoding='utf-8') as file:
            # Try to detect CSV format
            sample = file.read(1024)
            file.seek(0)
            
            # Detect delimiter
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            for row in reader:
                transaction_data = self._parse_transaction_row(row)
                if transaction_data:
                    transactions.append(transaction_data)
        
        return transactions
    
    def _process_excel(self) -> List[Dict[str, Any]]:
        """
        Process Excel file to extract transaction data
        """
        transactions = []
        
        # Read Excel file
        df = pd.read_excel(self.file_upload.file.path)
        
        for _, row in df.iterrows():
            transaction_data = self._parse_transaction_row(row.to_dict())
            if transaction_data:
                transactions.append(transaction_data)
        
        return transactions
    
    def _process_pdf(self) -> List[Dict[str, Any]]:
        """
        Process PDF file to extract transaction data
        Note: This is a placeholder - PDF processing would require OCR
        """
        # For MVP, we'll return empty list for PDFs
        # In production, this would use OCR libraries like pytesseract
        logger.warning(f"PDF processing not implemented for {self.file_upload.original_filename}")
        return []
    
    def _parse_transaction_row(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a single row of transaction data
        """
        try:
            # Common field mappings (case-insensitive)
            field_mappings = {
                'date': ['date', 'transaction_date', 'txn_date', 'datetime'],
                'amount': ['amount', 'value', 'sum', 'total'],
                'description': ['description', 'details', 'memo', 'reference', 'particulars'],
                'reference': ['reference', 'ref', 'transaction_id', 'txn_id'],
                'type': ['type', 'transaction_type', 'txn_type', 'debit_credit']
            }
            
            # Normalize row keys to lowercase
            normalized_row = {k.lower().strip(): v for k, v in row.items() if v is not None}
            
            # Extract fields
            transaction_data = {}
            
            # Date
            date_value = self._find_field_value(normalized_row, field_mappings['date'])
            if date_value:
                transaction_data['date'] = self._parse_date(date_value)
            else:
                # Skip rows without date
                return None
            
            # Amount
            amount_value = self._find_field_value(normalized_row, field_mappings['amount'])
            if amount_value:
                transaction_data['amount'] = self._parse_amount(amount_value)
            else:
                # Skip rows without amount
                return None
            
            # Description
            description_value = self._find_field_value(normalized_row, field_mappings['description'])
            transaction_data['description'] = str(description_value) if description_value else 'No description'
            
            # Reference
            reference_value = self._find_field_value(normalized_row, field_mappings['reference'])
            transaction_data['reference_number'] = str(reference_value) if reference_value else ''
            
            # Transaction type (basic inference)
            type_value = self._find_field_value(normalized_row, field_mappings['type'])
            transaction_data['transaction_type'] = self._infer_transaction_type(
                transaction_data['amount'], 
                type_value, 
                transaction_data['description']
            )
            
            return transaction_data
            
        except Exception as e:
            logger.warning(f"Failed to parse transaction row: {str(e)}")
            return None
    
    def _find_field_value(self, row: Dict[str, Any], possible_keys: List[str]) -> Any:
        """
        Find a field value using multiple possible key names
        """
        for key in possible_keys:
            if key in row and row[key] is not None:
                return row[key]
        return None
    
    def _parse_date(self, date_value: Any) -> datetime:
        """
        Parse date from various formats
        """
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            # Try common date formats
            date_formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y %H:%M:%S',
                '%d/%m/%Y %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_value.strip(), fmt)
                except ValueError:
                    continue
        
        # If all else fails, use current date
        logger.warning(f"Could not parse date: {date_value}, using current date")
        return timezone.now()
    
    def _parse_amount(self, amount_value: Any) -> Decimal:
        """
        Parse amount from various formats
        """
        if isinstance(amount_value, (int, float)):
            return Decimal(str(abs(amount_value)))
        
        if isinstance(amount_value, str):
            # Remove currency symbols and commas
            cleaned = amount_value.replace('₱', '').replace('PHP', '').replace(',', '').strip()
            
            # Handle negative amounts in parentheses
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            try:
                return Decimal(cleaned)
            except:
                logger.warning(f"Could not parse amount: {amount_value}")
                return Decimal('0')
        
        return Decimal('0')
    
    def _infer_transaction_type(self, amount: Decimal, type_hint: Any, description: str) -> str:
        """
        Infer transaction type from amount and other clues
        """
        # Check type hint first
        if type_hint:
            type_str = str(type_hint).lower()
            if 'debit' in type_str or 'expense' in type_str or 'out' in type_str:
                return 'expense'
            elif 'credit' in type_str or 'income' in type_str or 'in' in type_str:
                return 'income'
        
        # Check description for clues
        description_lower = description.lower()
        income_keywords = ['salary', 'payment', 'income', 'received', 'deposit', 'credit']
        expense_keywords = ['purchase', 'payment', 'bill', 'fee', 'charge', 'debit']
        
        for keyword in income_keywords:
            if keyword in description_lower:
                return 'income'
        
        for keyword in expense_keywords:
            if keyword in description_lower:
                return 'expense'
        
        # Default based on amount (positive = income, negative = expense)
        return 'income' if amount >= 0 else 'expense'
    
    def _create_transactions(self, transactions_data: List[Dict[str, Any]]) -> List[Transaction]:
        """
        Create Transaction objects from parsed data
        """
        created_transactions = []
        
        for txn_data in transactions_data:
            try:
                transaction = Transaction.objects.create(
                    user=self.user,
                    file_upload=self.file_upload,
                    date=txn_data['date'],
                    amount=txn_data['amount'],
                    description=txn_data['description'],
                    reference_number=txn_data.get('reference_number', ''),
                    transaction_type=txn_data['transaction_type'],
                    category='other',  # Will be categorized by AI later
                    source_platform=self.file_upload.source,
                    ai_categorized=False
                )
                created_transactions.append(transaction)
                
            except Exception as e:
                logger.error(f"Failed to create transaction: {str(e)}")
                continue
        
        return created_transactions


def process_file_upload(file_upload_id: str) -> Dict[str, Any]:
    """
    Process a file upload and extract transactions
    """
    try:
        file_upload = FileUpload.objects.get(id=file_upload_id)
        processor = TransactionProcessor(file_upload)
        return processor.process()
        
    except FileUpload.DoesNotExist:
        return {
            'success': False,
            'error': 'File upload not found'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
