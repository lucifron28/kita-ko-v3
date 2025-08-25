# Mock Financial Documents for Testing

This collection provides various realistic financial documents that can be used to test document scanning, OCR (Optical Character Recognition), and financial data processing functionality.

## 📋 Available Mock Documents

### 1. **PDF Bank Statements** (Professional Format)
- **`mock_bpi_statement.pdf`** - Full BPI bank statement with transactions table
- **`mock_gcash_statement.pdf`** - GCash transaction history statement
- **`mock_paymaya_statement.pdf`** - PayMaya-style digital wallet statement

**Features:**
- Professional formatting with headers, logos, and styling
- Transaction tables with dates, descriptions, amounts, and balances
- Account summaries with opening/closing balances
- Reference numbers and transaction categories

### 2. **Mobile Banking Screenshots** (Mobile App Format)
- **`mock_gcash_mobile.pdf`** - GCash mobile app transaction receipt
- **`mock_bpi_mobile.pdf`** - BPI mobile banking account view

**Features:**
- Mobile phone dimensions (4" x 7")
- App-like interface design
- Transaction receipts with success confirmations
- Account balance displays
- Recent transaction lists

### 3. **Text-Based Receipts** (Simple Format)
- **`mock_receipts.txt`** - Collection of ATM, transaction, and store receipts

**Features:**
- Simple ASCII text format
- Various receipt types: ATM withdrawals, money transfers, cash-in, deposits
- Easy to scan with basic OCR
- Multiple payment platforms represented

### 4. **Structured Data Formats**
- **`mock_bank_export.csv`** - Bank transaction export in CSV format
- **`mock_bank_data.json`** - Complete bank data in JSON format

**Features:**
- Machine-readable formats
- Structured transaction data
- Category classifications
- Account summaries and metadata

## 🎯 Use Cases

### **Document Scanning & OCR Testing**
- Test OCR accuracy with different document formats
- Validate text extraction from PDF statements
- Test mobile screenshot recognition
- Verify receipt data parsing

### **Financial Data Processing**
- Test transaction categorization algorithms
- Validate balance calculations
- Test date range filtering
- Verify income vs expense classification

### **AI Training Data**
- Machine learning model training for financial document recognition
- Pattern recognition for transaction types
- Category classification training
- Account balance extraction

### **API Integration Testing**
- Test file upload functionality
- Validate document processing pipelines
- Test data transformation and normalization
- Verify error handling for different formats

## 🚀 How to Generate More Documents

### Generate PDF Documents
```bash
python mock_financial_document.py
```

### Generate Mobile Banking Documents
```bash
python mock_mobile_banking.py
```

## 📊 Sample Data Overview

### Transaction Types Included:
- **Income**: Salary, freelance payments, bonuses, dividends, interest
- **Expenses**: Groceries, gas, restaurants, bills, shopping, healthcare
- **Transfers**: Bank-to-bank, e-wallet top-ups, fund movements
- **Withdrawals**: ATM cash withdrawals
- **Payments**: Bill payments, subscriptions, insurance

### Financial Platforms Represented:
- **BPI Bank** - Traditional banking
- **GCash** - Digital wallet
- **PayMaya** - Digital payments
- **7-Eleven** - Cash-in services
- **Various merchants** - POS transactions

### Time Periods:
- **Date Range**: July 22, 2024 - August 22, 2024
- **Transaction Frequency**: Daily to weekly
- **Realistic timing**: Business hours, weekend patterns

## 🔍 Technical Specifications

### PDF Documents:
- **Page Size**: A4 (210mm x 297mm)
- **Font**: Helvetica family
- **Colors**: Professional color schemes
- **Tables**: Structured transaction data

### Mobile Documents:
- **Page Size**: Mobile phone (4" x 7")
- **Interface**: App-like design elements
- **Navigation**: Mobile UI components
- **Responsive**: Optimized for mobile screens

### Data Formats:
- **CSV**: Standard comma-separated values
- **JSON**: Structured hierarchical data
- **TXT**: Plain text receipts
- **PDF**: Formatted documents with styling

## 🧪 Testing Scenarios

### **Scenario 1: Complete Bank Statement Processing**
1. Upload `mock_bpi_statement.pdf`
2. Extract all transactions
3. Categorize by type (income/expense)
4. Calculate monthly summaries
5. Generate insights and reports

### **Scenario 2: Mobile Receipt Scanning**
1. Upload `mock_gcash_mobile.pdf`
2. Extract transaction details
3. Parse recipient information
4. Verify amount and fees
5. Update account balance

### **Scenario 3: Multi-Format Data Integration**
1. Process `mock_bank_export.csv`
2. Scan `mock_receipts.txt`
3. Parse `mock_bank_data.json`
4. Merge all data sources
5. Reconcile balances and transactions

### **Scenario 4: OCR Accuracy Testing**
1. Compare extracted text vs expected data
2. Measure accuracy percentages
3. Identify problematic formats
4. Optimize OCR parameters
5. Validate data transformation

## 📈 Expected Processing Results

When these documents are processed through your financial system, you should expect:

- **Total Income**: ~₱49,880.00
- **Total Expenses**: ~₱32,180.00
- **Net Income**: ~₱17,700.00
- **Transaction Count**: 20-25 transactions
- **Categories**: 12+ different expense/income categories
- **Date Range**: 30-day period
- **Multiple Platforms**: BPI, GCash, PayMaya representation

## ⚠️ Important Notes

- **Test Data Only**: These are fictional financial documents for testing purposes
- **No Real Accounts**: All account numbers and personal information are fake
- **Consistent Data**: Cross-document data should be logically consistent
- **Realistic Amounts**: Transaction amounts reflect typical Filipino financial patterns
- **Date Consistency**: All dates fall within the specified testing period

## 🛠️ Customization

To modify the generated documents:

1. **Edit Transaction Data**: Modify the transaction generation functions
2. **Change Styling**: Update PDF styles and formatting
3. **Add New Platforms**: Include additional financial service providers
4. **Adjust Amounts**: Modify transaction amount ranges
5. **Update Dates**: Change the date generation logic

## 📞 Usage in Kita-Ko Application

These mock documents are specifically designed to work with the Kita-Ko financial management application:

1. **Upload via Web Interface**: Use the file upload feature
2. **AI Processing**: Test the AI-powered transaction analysis
3. **Report Generation**: Generate income reports using this data
4. **PDF Output**: Verify the generated PDF reports include this data
5. **Data Visualization**: Test charts and graphs with this sample data

---

**Generated**: August 22, 2025  
**Version**: 1.0  
**Compatible with**: Kita-Ko v3 Financial Management System
