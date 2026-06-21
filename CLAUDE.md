# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VEMS (Vehicle Entry Management System) is a Django REST Framework backend for AKGEC college. Students register vehicles, upload identity documents (RC, DL, College ID), pass OCR extraction, and await admin approval. Security guards then verify vehicles via a public unauthenticated search endpoint.

## Commands

All development runs through Docker Compose (PostgreSQL on port 5433, Redis on 6380, Django on 8005):

```bash
# Start all services
docker compose up -d --build

# Run migrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py makemigrations

# Django shell
docker compose exec web python manage.py shell

# Run tests
docker compose exec web python manage.py test

# Run a single app's tests
docker compose exec web python manage.py test accounts

# Promote a user to STAFF/ADMIN via shell
from accounts.models import User; u = User.objects.get(email="..."); u.role = "ADMIN"; u.save()
```

## Architecture

### URL namespace → app mapping
```
/api/auth/          → accounts       (register, OTP verify, set-password, login, refresh)
/api/users/         → users          (profile CRUD)
/api/documents/     → documents      (RC / DL / College ID uploads)
/api/ocr/           → ocr            (trigger OCR extraction on a document)
/api/vehicles/      → vehicles       (vehicle CRUD)
/api/registrations/ → registrations  (submit and view registration status)
/api/admin/         → staffs         (admin dashboard: list, approve, reject)
/api/search/        → search         (public, unauthenticated vehicle lookup)
```

### Auth model
- `AUTH_USER_MODEL = "accounts.User"` — custom user extending `AbstractUser` with `role` (USER/STAFF/ADMIN) and `is_verified`. Login uses `email` as `USERNAME_FIELD`.
- Custom `JWTAuthentication` in `accounts/authentication.py` decodes HS256 tokens using `SECRET_KEY`. Access + refresh tokens are generated in `accounts/utils.py`.
- Registration is a two-step flow: `POST /api/auth/register/` sends OTP → `POST /api/auth/verify-otp/` validates → `POST /api/auth/set-password/` creates the account.

### Permissions (`core/permissions.py`)
- `IsStaffUser` — role is STAFF or ADMIN; used for gate-search operations.
- `IsAdminUser` — role is ADMIN only; used for approve/reject and admin dashboard.

### Registration workflow
The critical path lives in `registrations/`:
1. `services.validate_registration(user)` — checks that a vehicle exists and all three required docs (RC, DL, COLLEGE_ID) have `ocr_status == "COMPLETED"`.
2. `services.cross_validate_documents(user, vehicle)` — cross-checks extracted OCR data (vehicle number on RC matches registered vehicle, owner name appears in RC text, student ID on College ID matches `user.profile.student_number`). Returns a list of warning strings stored in `VehicleRegistration.cross_validation_warnings`; does not block submission — admin makes the final call.

### OCR pipeline (`ocr/services.py`)
- Uses `pytesseract` + `Pillow` for images, `pdf2image` for PDFs.
- `process_document(document)` extracts `vehicle_number`, `dl_number`, `student_id`, and `raw_text` into `UserDocument.extracted_data` (JSONField).
- Regex patterns: vehicle number `[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}`, DL number `[A-Z]{2}[0-9]{13}`, student ID `\b\d{8}\b`.

### Key model relationships
```
User (accounts)
  ├── UserProfile (users)           — 1:1, student_number used in cross-validation
  ├── UserDocument (documents)      — FK, one per document type (latest is used)
  ├── Vehicle (vehicles)            — FK, owner_name cross-checked against RC
  └── VehicleRegistration           — FK to both User and Vehicle, unique_together
```

### Public search
`search/views.py` `PublicVehicleSearchView` explicitly sets `authentication_classes = []` and `permission_classes = []`. It returns owner name, vehicle type, and model only for APPROVED registrations — no PII beyond that.

### Email notifications
`send_mail` is called directly (no queue) in `accounts/views.py` (OTP) and `staffs/views.py` (approval/rejection emails to the vehicle owner). `fail_silently=True` on admin emails. Configured via `EMAIL_*` env vars.

## Environment variables (`.env`)
`SECRET_KEY`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`
