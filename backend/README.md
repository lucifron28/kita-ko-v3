# Kitako Backend

AI-powered proof-of-income platform for informal earners in the Philippines.

## Overview

The Kitako backend is a Django REST API that provides:

- **User Authentication & Management**: JWT-based authentication with user profiles
- **File Upload & Processing**: Secure upload and processing of financial documents
- **AI-Powered Analysis**: Transaction categorization and financial insights using Claude 3
- **Report Generation**: Professional PDF reports for loan applications and government subsidies
- **Security & Privacy**: GDPR compliance, data encryption, and privacy protection

## Features

### Core Functionality
- ✅ User registration and authentication
- ✅ File upload (CSV, Excel, PDF support)
- ✅ Transaction extraction and categorization
- ✅ AI-powered financial analysis
- ✅ PDF report generation
- ✅ Report verification system

### Security Features
- ✅ JWT authentication
- ✅ Rate limiting
- ✅ Data encryption
- ✅ Audit logging
- ✅ GDPR compliance
- ✅ Privacy protection

### AI Integration
- ✅ Claude 3 integration via OpenRouter
- ✅ Transaction categorization
- ✅ Financial summary generation
- ✅ Anomaly detection
- ✅ Insight extraction

## Technology Stack

- **Framework**: Django 5.0+ with Django REST Framework
- **Database**: PostgreSQL (SQLite for development)
- **AI**: Claude 3 Sonnet/Opus via OpenRouter API
- **PDF Generation**: ReportLab
- **Authentication**: JWT with SimpleJWT
- **File Processing**: Pandas, OpenPyXL
- **Security**: Cryptography, Django security middleware

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL (for production)
- Redis (for caching and background tasks)

### Setup

1. **Clone and navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/kitako_db

# OpenRouter API (for Claude 3)
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0

# Security
FIELD_ENCRYPTION_KEY=your-encryption-key-here
```

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `GET /api/auth/dashboard/` - User dashboard data

### Transaction Endpoints
- `POST /api/transactions/upload/` - Upload financial document
- `GET /api/transactions/uploads/` - List file uploads
- `POST /api/transactions/uploads/{id}/process/` - Process uploaded file
- `GET /api/transactions/` - List transactions (with filtering)
- `GET /api/transactions/{id}/` - Get transaction details
- `GET /api/transactions/summary/` - Transaction summary statistics

### AI Processing Endpoints
- `POST /api/ai/categorize/` - Categorize transactions with AI
- `POST /api/ai/summarize/` - Generate financial summary
- `POST /api/ai/detect-anomalies/` - Detect transaction anomalies
- `GET /api/ai/jobs/` - List AI processing jobs
- `GET /api/ai/jobs/{id}/` - Get AI job status

### Reports Endpoints
- `POST /api/reports/create/` - Create income report
- `GET /api/reports/` - List income reports
- `GET /api/reports/{id}/` - Get report details
- `POST /api/reports/generate-pdf/` - Generate PDF report
- `GET /api/reports/{id}/download/` - Download PDF report
- `POST /api/reports/verify/` - Verify report authenticity

## Testing

### Run all tests
```bash
python manage.py test
```

### Run specific test modules
```bash
python manage.py test tests.test_models
python manage.py test tests.test_api
python manage.py test tests.test_services
```

### Run API tests
```bash
python manage.py test_api
```

### Coverage report
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## File Upload Support

### Supported File Types
- **CSV**: Comma-separated values
- **Excel**: .xlsx, .xls files
- **PDF**: Bank statements (OCR planned)
- **Images**: .jpg, .jpeg, .png (OCR planned)

### File Size Limits
- Maximum file size: 50MB
- Recommended: Under 10MB for faster processing

### Data Sources
- GCash statements
- PayMaya statements
- Bank statements (BPI, BDO, Metrobank, etc.)
- Manual CSV uploads
- Receipt images (planned)

## Security Features

### Data Protection
- Field-level encryption for sensitive data
- Secure file upload validation
- Rate limiting to prevent abuse
- Audit logging for sensitive operations

### Privacy Compliance
- GDPR-compliant data export
- User data anonymization
- Data retention policies
- Right to be forgotten implementation

### Authentication Security
- JWT token-based authentication
- Password strength validation
- Session management
- CORS protection

## Deployment

### Production Settings
1. Set `DEBUG=False`
2. Configure PostgreSQL database
3. Set up Redis for caching
4. Configure proper `ALLOWED_HOSTS`
5. Set secure `SECRET_KEY`
6. Enable HTTPS
7. Configure static file serving

### Docker Deployment
```bash
# Build image
docker build -t kitako-backend .

# Run container
docker run -p 8000:8000 kitako-backend
```

## Monitoring and Logging

### Log Files
- Application logs: `logs/kitako.log`
- Error logs: Django's default logging
- Audit logs: Security-related operations

### Monitoring Endpoints
- Health check: `/admin/` (requires authentication)
- API status: All endpoints return proper HTTP status codes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For technical support or questions:
- Email: support@kitako.ph
- Documentation: See API_DOCUMENTATION.md
- Issues: GitHub Issues
