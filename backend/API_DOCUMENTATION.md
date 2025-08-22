# Kitako API Documentation

## Overview

The Kitako API provides endpoints for managing user accounts, uploading financial documents, processing transactions with AI, and generating proof-of-income reports.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## API Endpoints

### Authentication Endpoints

#### Register User
- **POST** `/auth/register/`
- **Description**: Register a new user account
- **Body**:
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "primary_occupation": "freelancer",
  "preferred_language": "en"
}
```

#### Login
- **POST** `/auth/login/`
- **Description**: Authenticate user and get tokens
- **Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Refresh Token
- **POST** `/auth/token/refresh/`
- **Description**: Refresh access token
- **Body**:
```json
{
  "refresh": "refresh_token_here"
}
```

#### User Profile
- **GET** `/auth/profile/`
- **Description**: Get current user profile
- **Authentication**: Required

#### Update Profile
- **PUT/PATCH** `/auth/profile/`
- **Description**: Update user profile
- **Authentication**: Required

#### User Dashboard
- **GET** `/auth/dashboard/`
- **Description**: Get user dashboard data with statistics
- **Authentication**: Required

### Transaction Endpoints

#### Upload File
- **POST** `/transactions/upload/`
- **Description**: Upload financial document
- **Authentication**: Required
- **Content-Type**: `multipart/form-data`
- **Body**:
```
file: [file]
file_type: "bank_statement" | "ewallet_statement" | "receipt" | "invoice" | "payslip" | "other"
source: "gcash" | "paymaya" | "bpi" | "bdo" | "other"
description: "Optional description"
```

#### List File Uploads
- **GET** `/transactions/uploads/`
- **Description**: Get list of uploaded files
- **Authentication**: Required

#### Process File Upload
- **POST** `/transactions/uploads/{upload_id}/process/`
- **Description**: Process uploaded file to extract transactions
- **Authentication**: Required

#### File Upload Status
- **GET** `/transactions/uploads/{upload_id}/status/`
- **Description**: Check processing status of uploaded file
- **Authentication**: Required

#### List Transactions
- **GET** `/transactions/`
- **Description**: Get list of transactions with filtering
- **Authentication**: Required
- **Query Parameters**:
  - `date_from`: Filter by start date (YYYY-MM-DD)
  - `date_to`: Filter by end date (YYYY-MM-DD)
  - `type`: Filter by transaction type
  - `category`: Filter by category
  - `source`: Filter by source platform
  - `search`: Search in description/counterparty

#### Transaction Detail
- **GET/PUT/PATCH** `/transactions/{transaction_id}/`
- **Description**: Get or update specific transaction
- **Authentication**: Required

#### Transaction Summary
- **GET** `/transactions/summary/`
- **Description**: Get transaction summary statistics
- **Authentication**: Required
- **Query Parameters**: Same as transaction list

#### Bulk Update Transactions
- **POST** `/transactions/bulk-update/`
- **Description**: Update multiple transactions at once
- **Authentication**: Required
- **Body**:
```json
{
  "transaction_ids": ["uuid1", "uuid2"],
  "updates": {
    "category": "new_category",
    "manually_verified": true
  }
}
```

### AI Processing Endpoints

#### Categorize Transactions
- **POST** `/ai/categorize/`
- **Description**: Use AI to categorize transactions
- **Authentication**: Required
- **Body**:
```json
{
  "transaction_ids": ["uuid1", "uuid2"],
  // OR
  "file_upload_id": "upload_uuid"
}
```

#### Generate Financial Summary
- **POST** `/ai/summarize/`
- **Description**: Generate AI-powered financial summary
- **Authentication**: Required
- **Body**:
```json
{
  "date_from": "2024-01-01",
  "date_to": "2024-12-31"
}
```

#### Detect Anomalies
- **POST** `/ai/detect-anomalies/`
- **Description**: Detect anomalies in transactions
- **Authentication**: Required
- **Body**:
```json
{
  "transaction_ids": ["uuid1", "uuid2"] // Optional
}
```

#### List AI Jobs
- **GET** `/ai/jobs/`
- **Description**: Get list of AI processing jobs
- **Authentication**: Required

#### AI Job Status
- **GET** `/ai/jobs/{job_id}/`
- **Description**: Check status of AI processing job
- **Authentication**: Required

### Reports Endpoints

#### Create Income Report
- **POST** `/reports/create/`
- **Description**: Create a new income report
- **Authentication**: Required
- **Body**:
```json
{
  "report_type": "monthly" | "quarterly" | "annual" | "custom",
  "date_from": "2024-01-01",
  "date_to": "2024-12-31",
  "purpose": "loan_application" | "government_subsidy" | "insurance_application" | "other",
  "purpose_description": "Optional description",
  "title": "Optional custom title"
}
```

#### List Income Reports
- **GET** `/reports/`
- **Description**: Get list of user's income reports
- **Authentication**: Required

#### Income Report Detail
- **GET/PUT/PATCH/DELETE** `/reports/{report_id}/`
- **Description**: Get, update, or delete specific income report
- **Authentication**: Required

#### Generate PDF Report
- **POST** `/reports/generate-pdf/`
- **Description**: Generate PDF for an income report
- **Authentication**: Required
- **Body**:
```json
{
  "report_id": "report_uuid",
  "include_ai_analysis": true,
  "include_charts": false
}
```

#### Download Report
- **GET** `/reports/{report_id}/download/`
- **Description**: Download PDF report
- **Authentication**: Optional (if public or with access token)
- **Query Parameters**:
  - `token`: Access token for private reports

#### Verify Report
- **POST** `/reports/verify/`
- **Description**: Verify report authenticity using verification code
- **Authentication**: Not required
- **Body**:
```json
{
  "verification_code": "ABC123DEF456"
}
```

#### Report Analytics
- **GET** `/reports/analytics/`
- **Description**: Get analytics data for user's reports
- **Authentication**: Required

## Response Format

### Success Response
```json
{
  "message": "Success message",
  "data": { ... }
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": "Detailed error information"
}
```

## Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## File Upload Limits

- Maximum file size: 50MB
- Supported formats: PDF, CSV, XLSX, XLS, JPG, JPEG, PNG, TXT
- Supported sources: GCash, PayMaya, BPI, BDO, and other banks/e-wallets

## Rate Limiting

API requests are rate-limited to prevent abuse. Current limits:
- 100 requests per minute per user
- 1000 requests per hour per user

## Error Handling

The API returns detailed error messages to help with debugging:

```json
{
  "error": "Validation failed",
  "details": {
    "field_name": ["Error message for this field"]
  }
}
```
