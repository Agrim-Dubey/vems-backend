# VEMS — Vehicle Entry Management System

## Overview

VEMS (Vehicle Entry Management System) is a centralized digital vehicle verification and entry authorization system designed for educational institutions.

The system replaces manual gate verification processes using:
- College email authentication
- OCR-based document verification
- Vehicle registration workflows
- Public vehicle verification
- Physical sticker issuance

---

# Core Workflow

```txt
Register
→ Verify OTP
→ Set Password
→ Login
→ Complete Profile
→ Upload Documents
→ OCR Extraction
→ Add Vehicle
→ Submit Registration
→ Staff/Admin Approval
→ Public Vehicle Search
→ Physical Sticker Assignment
```

---

# Tech Stack

## Backend
- Django
- Django REST Framework

## Database
- PostgreSQL

## Cache / Queue
- Redis

## Authentication
- Custom JWT Authentication

## Infrastructure
- Docker
- Docker Compose

---

# Project Structure

```txt
vems/
│
├── accounts/
├── users/
├── documents/
├── ocr/
├── vehicles/
├── registrations/
├── staffs/
├── stickers/
├── search/
├── core/
│
├── config/
├── media/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

---

# Modules

# accounts/

Handles:
- Registration
- OTP verification
- Login
- JWT token generation
- RBAC roles

## Features
- College email validation
- Email OTP verification
- Access + refresh tokens
- JWT middleware

## Roles

```txt
USER
STAFF
ADMIN
```

---

# users/

Handles:
- User profile
- Student details

## Stored Data
- Full name
- Student ID
- Phone number
- Department
- Year
- Gender
- Hostel

---

# documents/

Handles:
- RC uploads
- DL uploads
- College ID uploads

## Features
- Media storage
- OCR status tracking
- Extracted JSON storage

## OCR Status

```txt
PENDING
PROCESSING
COMPLETED
FAILED
```

---

# ocr/

Handles:
- OCR extraction pipeline
- Vehicle number extraction
- DL extraction
- Student ID extraction

## Current Status
Simulated OCR extraction.

## Planned
- PaddleOCR
- Tesseract OCR
- Barcode scanning

---

# vehicles/

Handles:
- Vehicle information
- Vehicle ownership records

## Stored Data
- Vehicle number
- Vehicle model
- Vehicle type
- Vehicle color
- RC number

---

# registrations/

Main business workflow.

Handles:
- Registration submissions
- Approval states
- Validation engine
- Rejection reasons

## Statuses

```txt
PENDING
APPROVED
REJECTED
```

## Validation Rules
- Profile must exist
- All required docs uploaded
- OCR completed
- Vehicle exists

---

# staffs/

Handles:
- Staff/admin dashboard APIs
- Pending registrations
- Approval/rejection workflows

## Features
- Dashboard stats
- Approve registration
- Reject registration

---

# stickers/

Handles:
- Physical sticker assignment

## Features
- Sticker number generation
- Issued-by tracking
- Active/inactive stickers

---

# search/

Public searchable vehicle verification system.

## Important
This endpoint requires NO authentication.

Security guards can verify vehicles directly.

## Endpoint

```txt
/api/search/vehicle/
```

## Query Example

```txt
?vehicle_number=UP14AB1234
```

---

# Authentication Flow

# Register

```http
POST /api/auth/register/
```

Body:

```json
{
  "email": "agrim24154080@akgec.in"
}
```

---

# Verify OTP

```http
POST /api/auth/verify-otp/
```

```json
{
  "email": "agrim24154080@akgec.in",
  "otp": "123456"
}
```

---

# Set Password

```http
POST /api/auth/set-password/
```

```json
{
  "email": "agrim24154080@akgec.in",
  "password": "test123",
  "confirm_password": "test123"
}
```

---

# Login

```http
POST /api/auth/login/
```

```json
{
  "email": "agrim24154080@akgec.in",
  "password": "test123"
}
```

Response:

```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

---

# Protected Routes

Use:

```txt
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

# Docker Setup

# Services

```txt
web
postgres
redis
```

# Ports

```txt
Django    → 8005
Postgres  → 5433
Redis     → 6780
```

---

# Run Project

```bash
docker compose up -d --build
```

---

# Run Migrations

```bash
docker compose exec web python manage.py makemigrations
```

```bash
docker compose exec web python manage.py migrate
```

---

# Make User Staff

```bash
docker compose exec web python manage.py shell
```

```python
from accounts.models import User

u = User.objects.get(email="agrim24154080@akgec.in")

u.role = "STAFF"

u.save()
```

---

# Public Vehicle Verification Example

```bash
curl "http://localhost:8005/api/search/vehicle/?vehicle_number=UP14AB1234"
```

Response:

```json
{
  "verified": true,
  "owner_name": "Agrim Dubey",
  "vehicle_number": "UP14AB1234",
  "vehicle_type": "BIKE",
  "vehicle_model": "Royal Enfield"
}
```

---

# OCR Pipeline

```txt
Upload Document
→ OCR Processing
→ Extracted JSON
→ Validation Engine
→ Registration Eligibility
```

---

# Future Improvements

## OCR
- PaddleOCR integration
- Barcode scanning
- AI-based forgery detection

## Security
- Blacklist system
- Audit logs

## Realtime
- WebSockets
- Live approvals

## Infrastructure
- Celery workers
- Async OCR queues
- Nginx
- Gunicorn
- S3 media storage

## Analytics
- Admin charts
- Daily stats
- Fraud detection

---

# Current MVP Status

```txt
✅ JWT Authentication
✅ OTP Verification
✅ Profile System
✅ Document Uploads
✅ OCR Simulation
✅ Vehicle Registration
✅ Registration Workflow
✅ RBAC
✅ Admin Approval APIs
✅ Public Vehicle Search
✅ Sticker Assignment
✅ Dockerized Infrastructure
```

---

# Stakeholders

## Students/Staff
- Register vehicles
- Upload documents
- Submit registrations

## Security Guards
- Search vehicle numbers
- Verify approval status
- Assign physical stickers

## Admins
- Approve/reject registrations
- Monitor system

---

# Vision

VEMS aims to replace insecure manual vehicle verification systems with a centralized, secure, searchable, and scalable digital infrastructure for educational institutions.