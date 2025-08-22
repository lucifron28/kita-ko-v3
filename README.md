# Kitako - AI-Powered Proof-of-Income Platform

A comprehensive platform that helps informal earners in the Philippines generate professional, AI-powered proof-of-income reports for loan applications, government subsidies, and other financial needs.

## 🚀 Overview

Kitako bridges the gap between informal income and formal financial requirements by:

- **AI-Powered Analysis**: Using Claude 3 to categorize transactions and generate insights
- **Professional Reports**: Creating bank-ready PDF reports with verification codes
- **Multi-Source Support**: Processing data from GCash, PayMaya, banks, and manual uploads
- **Security First**: GDPR-compliant with data encryption and privacy protection
- **User-Friendly**: Clean, responsive interface with Dracula theme

## 🏗️ Architecture

### Backend (Django)
- **Framework**: Django 5.0+ with Django REST Framework
- **Database**: PostgreSQL (SQLite for development)
- **AI Integration**: Claude 3 Sonnet/Opus via OpenRouter API
- **Authentication**: JWT with automatic refresh
- **File Processing**: Pandas, OpenPyXL for CSV/Excel parsing
- **PDF Generation**: ReportLab for professional reports
- **Security**: Field-level encryption, rate limiting, audit logging

### Frontend (React)
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS with custom Dracula theme
- **State Management**: React Context API
- **HTTP Client**: Axios with interceptors
- **Forms**: React Hook Form with Yup validation
- **File Upload**: React Dropzone with progress tracking
- **Notifications**: React Hot Toast

## ✨ Key Features

### 🔐 Authentication & Security
- JWT-based authentication with httpOnly refresh tokens
- Field-level data encryption for sensitive information
- Rate limiting and audit logging
- GDPR compliance with data export and anonymization
- Secure file upload validation

### 📁 File Processing
- Support for CSV, Excel, PDF, and image files
- Automatic transaction extraction and parsing
- Multi-source platform support (GCash, PayMaya, banks)
- Real-time processing status updates
- Error handling and retry mechanisms

### 🤖 AI-Powered Analysis
- Transaction categorization using Claude 3
- Financial summary generation with insights
- Anomaly detection in transaction patterns
- Confidence scoring and reasoning
- Customizable AI prompts and models

### 📊 Report Generation
- Professional PDF reports suitable for official use
- Income breakdown and expense analysis
- Verification codes for authenticity
- Document hashing for integrity
- Public/private sharing options

### 📱 User Experience
- Responsive design for mobile, tablet, and desktop
- Dracula color theme for reduced eye strain
- Real-time notifications and feedback
- Comprehensive dashboard with statistics
- Intuitive file upload with drag-and-drop

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL (for production)
- Redis (for caching)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
# Edit .env with your configuration

# Database setup
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Environment configuration
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm run dev
```

## 🔧 Configuration

### Backend Environment Variables

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

# Security
FIELD_ENCRYPTION_KEY=your-encryption-key-here
```

### Frontend Environment Variables

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api

# App Configuration
VITE_APP_NAME=Kitako
VITE_APP_VERSION=1.0.0
```

## 📚 API Documentation

The backend provides comprehensive REST API endpoints:

- **Authentication**: `/api/auth/` - Login, register, profile management
- **Transactions**: `/api/transactions/` - File upload, transaction management
- **AI Processing**: `/api/ai/` - Categorization, summaries, anomaly detection
- **Reports**: `/api/reports/` - Report creation, PDF generation, verification

Full API documentation is available at `/api/docs/` when running the backend.

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🚀 Deployment

### Production Considerations

1. **Backend**:
   - Set `DEBUG=False`
   - Configure PostgreSQL database
   - Set up Redis for caching
   - Configure proper `ALLOWED_HOSTS`
   - Enable HTTPS
   - Set up static file serving

2. **Frontend**:
   - Build for production: `npm run build`
   - Configure API base URL
   - Set up CDN for static assets
   - Enable gzip compression

### Docker Support

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Claude 3** by Anthropic for AI capabilities
- **OpenRouter** for AI API access
- **Django** and **React** communities
- **Tailwind CSS** for styling framework
- **Dracula Theme** for color palette

## 📞 Support

For technical support or questions:
- Email: support@kitako.ph
- Documentation: See individual README files in `/backend` and `/frontend`
- Issues: GitHub Issues

---

**Kitako** - Empowering informal earners with AI-powered financial documentation.
