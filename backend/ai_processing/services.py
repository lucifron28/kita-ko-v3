"""
AI Processing Services for Kitako MVP

This module handles integration with Claude 3 via OpenRouter API for:
- Transaction categorization
- Financial summary generation
- Anomaly detection
- Insight extraction
"""

import openai
import json
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

from .models import AIProcessingJob, AIPromptTemplate, AIModelUsage

logger = logging.getLogger('kitako')


class OpenRouterClient:
    """
    Client for interacting with OpenRouter API (Claude 3)
    """
    
    def __init__(self):
        self.client = openai.OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.default_model = "anthropic/claude-3-sonnet"
    
    def create_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = None,
        temperature: float = 0.1,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Create a completion using OpenRouter API
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'usage': {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'model': response.model
            }
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content': None,
                'usage': None
            }


class TransactionCategorizationService:
    """
    Service for categorizing transactions using AI
    """
    
    def __init__(self):
        self.client = OpenRouterClient()
    
    def categorize_transactions(self, transactions_data: List[Dict]) -> Dict[str, Any]:
        """
        Categorize a list of transactions using AI
        """
        try:
            # Prepare the prompt
            system_prompt = self._get_categorization_system_prompt()
            user_prompt = self._format_transactions_for_categorization(transactions_data)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Get AI response
            response = self.client.create_completion(messages)
            
            if response['success']:
                # Parse the AI response
                categorized_data = self._parse_categorization_response(response['content'])
                return {
                    'success': True,
                    'categorized_transactions': categorized_data,
                    'usage': response['usage']
                }
            else:
                return {
                    'success': False,
                    'error': response['error']
                }
                
        except Exception as e:
            logger.error(f"Transaction categorization error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_categorization_system_prompt(self) -> str:
        """
        Get the system prompt for transaction categorization
        """
        return """You are an AI assistant specialized in categorizing financial transactions for informal earners in the Philippines. Your task is to analyze transaction data and categorize each transaction accurately.

TRANSACTION TYPES:
- income: Money received (salary, freelance, business income, etc.)
- expense: Money spent (food, transportation, utilities, etc.)
- transfer_in: Money transferred into account
- transfer_out: Money transferred out of account
- fee: Service fees, transaction fees
- refund: Money refunded

INCOME CATEGORIES:
- salary: Regular employment income
- freelance: Freelance work payments
- business_income: Income from business operations
- commission: Sales commissions
- tips: Tips and gratuities
- rental_income: Income from rentals
- government_benefit: Government subsidies/benefits
- loan_received: Money borrowed
- gift_received: Gifts or financial assistance

EXPENSE CATEGORIES:
- food: Food and dining expenses
- transportation: Transportation costs
- utilities: Electricity, water, internet bills
- rent: Rent payments
- healthcare: Medical expenses
- education: Educational expenses
- entertainment: Entertainment and leisure
- shopping: General shopping
- loan_payment: Loan repayments
- insurance: Insurance payments
- business_expense: Business-related expenses
- family_support: Money sent to family

For each transaction, provide:
1. transaction_type (from the list above)
2. category (from the appropriate list above)
3. confidence (high/medium/low/very_low)
4. reasoning (brief explanation)

Respond in JSON format with an array of objects, one for each transaction."""
    
    def _format_transactions_for_categorization(self, transactions: List[Dict]) -> str:
        """
        Format transaction data for AI processing
        """
        formatted_transactions = []
        
        for i, txn in enumerate(transactions):
            formatted_txn = {
                'id': i,
                'date': txn.get('date', ''),
                'amount': float(txn.get('amount', 0)),
                'description': txn.get('description', ''),
                'reference': txn.get('reference_number', ''),
                'counterparty': txn.get('counterparty', '')
            }
            formatted_transactions.append(formatted_txn)
        
        return f"Please categorize these transactions:\n\n{json.dumps(formatted_transactions, indent=2)}"
    
    def _parse_categorization_response(self, response_content: str) -> List[Dict]:
        """
        Parse AI response for transaction categorization
        """
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Fallback: try to parse the entire response as JSON
                return json.loads(response_content)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI categorization response: {str(e)}")
            return []


class FinancialSummaryService:
    """
    Service for generating financial summaries using AI
    """
    
    def __init__(self):
        self.client = OpenRouterClient()
    
    def generate_summary(self, transactions_data: List[Dict], date_range: Dict) -> Dict[str, Any]:
        """
        Generate a financial summary from transaction data
        """
        try:
            # Calculate basic statistics
            stats = self._calculate_basic_stats(transactions_data)
            
            # Prepare the prompt
            system_prompt = self._get_summary_system_prompt()
            user_prompt = self._format_data_for_summary(transactions_data, stats, date_range)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Get AI response
            response = self.client.create_completion(messages, max_tokens=2000)
            
            if response['success']:
                return {
                    'success': True,
                    'summary': response['content'],
                    'statistics': stats,
                    'usage': response['usage']
                }
            else:
                return {
                    'success': False,
                    'error': response['error']
                }
                
        except Exception as e:
            logger.error(f"Financial summary generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_basic_stats(self, transactions: List[Dict]) -> Dict[str, Any]:
        """
        Calculate basic financial statistics
        """
        total_income = sum(float(t['amount']) for t in transactions if t.get('transaction_type') == 'income')
        total_expenses = sum(float(t['amount']) for t in transactions if t.get('transaction_type') == 'expense')
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_income': total_income - total_expenses,
            'transaction_count': len(transactions),
            'income_count': len([t for t in transactions if t.get('transaction_type') == 'income']),
            'expense_count': len([t for t in transactions if t.get('transaction_type') == 'expense'])
        }
    
    def _get_summary_system_prompt(self) -> str:
        """
        Get the system prompt for financial summary generation
        """
        return """You are an AI assistant specialized in creating financial summaries for informal earners in the Philippines. Your task is to analyze transaction data and create a clear, professional summary suitable for loan applications, government subsidies, or other financial services.

Create a summary that includes:
1. Overview of financial activity during the period
2. Income sources and patterns
3. Major expense categories
4. Financial stability indicators
5. Notable trends or patterns

Write in a professional tone suitable for financial institutions. Focus on demonstrating the person's financial capability and reliability. Use Philippine Peso (₱) currency format.

Keep the summary concise but comprehensive, highlighting positive financial behaviors and income consistency."""
    
    def _format_data_for_summary(self, transactions: List[Dict], stats: Dict, date_range: Dict) -> str:
        """
        Format data for summary generation
        """
        return f"""Please generate a financial summary for the following data:

PERIOD: {date_range.get('from', 'N/A')} to {date_range.get('to', 'N/A')}

STATISTICS:
- Total Income: ₱{stats['total_income']:,.2f}
- Total Expenses: ₱{stats['total_expenses']:,.2f}
- Net Income: ₱{stats['net_income']:,.2f}
- Total Transactions: {stats['transaction_count']}

TRANSACTION DATA:
{json.dumps(transactions[:50], indent=2)}  # Limit to first 50 transactions

Please provide a professional financial summary suitable for formal applications."""
