# Kitako Frontend

Modern React frontend for the Kitako AI-powered proof-of-income platform.

## Overview

The Kitako frontend is a React application built with Vite, featuring:

- **Modern UI**: Clean, responsive design with Dracula color theme
- **Authentication**: JWT-based auth with automatic token refresh
- **File Upload**: Drag-and-drop file upload with progress tracking
- **AI Integration**: Real-time AI processing status and results
- **Report Generation**: Professional PDF report creation and management
- **Responsive Design**: Mobile-first approach with Tailwind CSS

## Technology Stack

- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS with custom Dracula theme
- **State Management**: React Context API
- **HTTP Client**: Axios with interceptors
- **Forms**: React Hook Form with Yup validation
- **Icons**: Lucide React
- **Notifications**: React Hot Toast
- **File Upload**: React Dropzone

## Features

### Core Functionality
- ✅ User authentication (login/register)
- ✅ Dashboard with statistics and recent activity
- ✅ File upload with drag-and-drop support
- ✅ Transaction management and filtering
- ✅ AI-powered transaction categorization
- ✅ Income report generation and management
- ✅ User profile management

### UI/UX Features
- ✅ Dracula color theme
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Loading states and error handling
- ✅ Form validation with user-friendly messages
- ✅ Toast notifications for user feedback
- ✅ Smooth animations and transitions

### Security Features
- ✅ JWT token management with auto-refresh
- ✅ Protected routes
- ✅ Secure API communication
- ✅ Input validation and sanitization

## Installation

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start development server**
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Environment Variables

Create a `.env` file with the following variables:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api

# App Configuration
VITE_APP_NAME=Kitako
VITE_APP_VERSION=1.0.0

# Development
VITE_DEBUG=true
```

## Custom Utility Classes

The application uses custom Tailwind utility classes for consistency:

### Buttons
- `btn-primary` - Primary action button
- `btn-secondary` - Secondary button
- `btn-success` - Success button
- `btn-danger` - Danger button
- `btn-outline` - Outlined button

### Forms
- `input-field` - Standard input field
- `form-group` - Form group container
- `form-label` - Form label
- `form-error` - Error message

### Cards
- `card` - Card container
- `card-header` - Card header
- `card-body` - Card body
- `card-footer` - Card footer

## Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## API Integration

The frontend communicates with the Django backend through:

- JWT token storage in localStorage
- Automatic token refresh using httpOnly cookies
- Axios interceptors for token management
- Real-time status updates for AI processing

## License

This project is licensed under the MIT License.
