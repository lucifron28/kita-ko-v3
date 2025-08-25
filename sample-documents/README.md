# 📁 Sample Financial Documents

This collection provides **realistic Filipino financial documents** designed specifically for testing Kitako's AI-powered document processing capabilities. All documents contain authentic-looking data patterns commonly found in Philippine financial institutions.

## Quick Start Guide

### For New Users (Testing Kitako)
1. **Start Kitako** using `./run_app.sh` from the main directory
2. **Register/Login** at http://localhost:5173
3. **Upload any document** from this folder via the File Upload page
4. **Watch the AI magic** as transactions are automatically categorized
5. **Generate reports** to see professional PDF outputs

### For Developers (System Testing)
1. Use these documents to test file upload functionality
2. Validate AI categorization accuracy  
3. Test report generation with realistic data
4. Verify PDF output quality and formatting

##  Available Documents

### 🏦 **Professional Bank Statements** 
- **`mock_bpi_statement.pdf`** - Complete BPI bank statement with transaction table
  - *Features*: Professional formatting, account summaries, reference numbers
  - *Best for*: Testing comprehensive statement processing
  
- **`mock_gcash_statement.pdf`** - GCash transaction history statement  
  - *Features*: Digital wallet transactions, mobile money patterns
  - *Best for*: E-wallet integration testing
  
- **`mock_paymaya_statement.pdf`** - PayMaya digital payment statement
  - *Features*: Online payment records, merchant transactions
  - *Best for*: Digital payment processing validation

### **Mobile Banking Screenshots**
- **`mock_gcash_mobile.pdf`** - GCash mobile app transaction receipt
  - *Features*: Mobile UI elements, transaction confirmations
  - *Best for*: Mobile interface testing
  
- **`mock_bpi_mobile.pdf`** - BPI mobile banking account view
  - *Features*: Account balance display, recent transactions
  - *Best for*: Mobile banking integration

### **Simple Text Formats**
- **`mock_receipts.txt`** - Collection of ATM and store receipts
  - *Features*: Plain text format, various receipt types
  - *Best for*: Basic OCR and text extraction testing

### **Structured Data Files**
- **`mock_bank_export.csv`** - Bank transaction export in CSV format
  - *Features*: Machine-readable, structured columns
  - *Best for*: Direct data import testing
  
- **`mock_bank_data.json`** - Complete financial data in JSON format
  - *Features*: Hierarchical data structure, metadata included
  - *Best for*: API integration and data processing

### **Generator Scripts**
- **`mock_financial_document.py`** - PDF document generator
- **`mock_mobile_banking.py`** - Mobile interface generator

## �🇭 Authentic Filipino Financial Patterns

These documents are specifically designed to reflect **real Filipino financial behavior**:

### **Transaction Categories**
- **Income Sources**: Freelance payments, salaries, remittances, online sales
- **Essential Expenses**: Groceries (SM, Robinson's), transportation (jeepney, Grab), utilities (Meralco, PLDT)
- **Filipino Lifestyle**: Jollibee, McDonald's, 7-Eleven, Mercury Drug, shopping malls
- **Digital Payments**: GCash transfers, PayMaya top-ups, online shopping (Lazada, Shopee)
- **Traditional Banking**: BPI, BDO transactions, ATM withdrawals

### **Merchant Names & Descriptions**
- **Local Businesses**: Palengke, sari-sari stores, local restaurants
- **Major Retailers**: SM Supermalls, Robinson's, Ayala Malls
- **Transportation**: MRT/LRT, taxi services, gas stations (Petron, Shell)
- **Food & Dining**: Popular Filipino chains and local eateries
- **Healthcare**: Mercury Drug, clinics, hospitals

### **Realistic Amount Ranges**
- **Daily expenses**: ₱50 - ₱500 (meals, transportation)
- **Weekly shopping**: ₱1,000 - ₱3,000 (groceries, essentials)
- **Monthly bills**: ₱1,500 - ₱8,000 (utilities, rent, insurance)
- **Income patterns**: ₱15,000 - ₱25,000 (typical freelance/employee earnings)

### **Filipino Business Patterns**
- **Paydays**: 15th and 30th of the month
- **Holiday spending**: Increased transactions during Christmas, New Year
- **Remittance patterns**: OFW money transfers via Western Union, Palawan Express
- **Mobile money usage**: Heavy GCash and PayMaya adoption

##  How to Generate More Documents

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

## 🧪 Recommended Testing Workflows

### **🔄 Workflow 1: Complete Document Processing**
```bash
# 1. Upload bank statement
Upload: mock_bpi_statement.pdf
Expected: 15-20 transactions extracted, categorized automatically

# 2. Add mobile receipts  
Upload: mock_gcash_mobile.pdf
Expected: Mobile transaction parsed, amounts reconciled

# 3. Include structured data
Upload: mock_bank_export.csv  
Expected: Data merged, duplicates handled, balances verified

# 4. Generate comprehensive report
Result: Professional PDF with complete financial analysis
```

### **🤖 Workflow 2: AI Categorization Testing**
```bash
# Test AI accuracy with Filipino context
Upload: mock_gcash_statement.pdf
Verify: Jollibee → Food & Dining
Verify: Grab → Transportation  
Verify: SM Supermarket → Groceries
Verify: Freelance payment → Income
```

### **📱 Workflow 3: Mobile-First Experience**
```bash
# Test responsive design
Upload: mock_gcash_mobile.pdf (mobile format)
Upload: mock_bpi_mobile.pdf (mobile banking)
Expected: Optimized processing for mobile screenshots
```

### **📊 Workflow 4: Report Generation**
```bash
# Generate different report types
Purpose: Loan Application → Professional format with income focus
Purpose: Government Subsidy → Detailed expense breakdown  
Purpose: Visa Application → Comprehensive financial overview
```

## Expected Processing Results

When these documents are processed through your financial system, you should expect:

- **Total Income**: ~₱49,880.00
- **Total Expenses**: ~₱32,180.00
- **Net Income**: ~₱17,700.00
- **Transaction Count**: 20-25 transactions
- **Categories**: 12+ different expense/income categories
- **Date Range**: 30-day period
- **Multiple Platforms**: BPI, GCash, PayMaya representation

## Important Notes

- **Test Data Only**: These are fictional financial documents for testing purposes
- **No Real Accounts**: All account numbers and personal information are fake
- **Consistent Data**: Cross-document data should be logically consistent
- **Realistic Amounts**: Transaction amounts reflect typical Filipino financial patterns
- **Date Consistency**: All dates fall within the specified testing period

##  Customization

To modify the generated documents:

1. **Edit Transaction Data**: Modify the transaction generation functions
2. **Change Styling**: Update PDF styles and formatting
3. **Add New Platforms**: Include additional financial service providers
4. **Adjust Amounts**: Modify transaction amount ranges
5. **Update Dates**: Change the date generation logic

## Usage in Kita-Ko Application

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
