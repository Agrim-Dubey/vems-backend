# VEMS Backend — Handover Document

**Project**: Vehicle Entry Management System  
**Client**: AKGEC Software Development Centre  
**Backend**: Agrim Dubey  
**Stack**: Django 6 + DRF + PostgreSQL + Redis + Docker  
**Live**: https://vems.akgec.ac.in  
**Swagger**: https://vems.akgec.ac.in/api/docs/  
**Repo**: https://github.com/Agrim-Dubey/vems-backend

---

## Infrastructure

| Service | Image | Internal Port | Exposed Port |
|---------|-------|---------------|--------------|
| Django (web) | Custom Dockerfile | 8000 | 127.0.0.1:8005 |
| PostgreSQL | postgres:16-alpine | 5432 | 127.0.0.1:5433 |
| Redis | redis:7-alpine | 6379 | 127.0.0.1:6380 |

- **Server**: AWS EC2 (Ubuntu), nginx reverse-proxies `vems.akgec.ac.in` → port 8005
- **Media files**: stored on server disk at `/app/media/` — backed up manually
- **Docker Compose version**: 1.29.2 — use `sudo docker-compose`, NOT `docker compose`

### Deploy command
```bash
sudo docker-compose down && sudo docker-compose up -d --build
```

### View logs
```bash
sudo docker-compose logs -f web
```

### Django shell
```bash
sudo docker-compose exec web python manage.py shell
```

### Promote user to STAFF or ADMIN
```python
from accounts.models import User
u = User.objects.get(email="guard@akgec.ac.in")
u.role = "STAFF"  # or "ADMIN"
u.save()
```

---

## Environment Variables (`.env`)

```
SECRET_KEY=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=
DEBUG=False
ALLOWED_HOSTS=vems.akgec.ac.in,localhost
```

---

## Auth Flow

### Registration (new user)
```
POST /api/auth/register/        → sends OTP to @akgec.ac.in email
POST /api/auth/verify-otp/      → validates OTP
POST /api/auth/set-password/    → creates account, password min 8 chars
POST /api/auth/login/           → returns access_token (15min) + refresh_token (7 days)
```

### Forgot Password
```
POST /api/auth/forgot-password/         → sends OTP to registered email
POST /api/auth/verify-otp/              → same endpoint as above
POST /api/auth/forgot-password/reset/   → updates password
```

### Token Usage
All protected endpoints require: `Authorization: Bearer <access_token>`

When access token expires → `POST /api/auth/refresh/` with `{refresh_token}` → new access token.

---

## All Endpoints

### Auth — `/api/auth/`

| Method | Endpoint | Auth | Rate Limit | Notes |
|--------|----------|------|------------|-------|
| POST | `/register/` | None | 5/hr | Email must be @akgec.ac.in |
| POST | `/verify-otp/` | None | — | Shared by registration + forgot password |
| POST | `/set-password/` | None | — | Creates account |
| POST | `/login/` | None | 20/hr | Returns both tokens |
| POST | `/refresh/` | None | — | Returns new access_token |
| GET | `/me/` | JWT | — | Returns id, email, role. ADMIN → 403 |
| POST | `/forgot-password/` | None | 5/hr | User must exist |
| POST | `/forgot-password/reset/` | None | — | — |

### Profile — `/api/users/`

| Method | Endpoint | Auth | Notes |
|--------|----------|------|-------|
| GET | `/profile/` | JWT | — |
| POST | `/profile/` | JWT | Creates or fully replaces. Multipart or JSON |
| PATCH | `/profile/` | JWT | Partial update |

### Vehicles — `/api/vehicles/`

| Method | Endpoint | Auth | Notes |
|--------|----------|------|-------|
| POST | `/` | JWT | `vehicle_type`: CAR / BIKE / SCOOTY |
| GET | `/` | JWT | Only returns vehicles that have a submitted registration |

### Documents — `/api/documents/`

| Method | Endpoint | Auth | Rate Limit | Notes |
|--------|----------|------|------------|-------|
| POST | `/upload/` | JWT | 30/hr | Multipart. Types: RC / DL / COLLEGE_ID. Max 5MB. JPG/PNG/WEBP/PDF only |
| GET | `/upload/` | JWT | — | All docs for logged-in user |

### OCR — `/api/ocr/`

| Method | Endpoint | Auth | Notes |
|--------|----------|------|-------|
| POST | `/process/{document_id}/` | JWT | Re-runs OCR on an existing document |

### Registrations — `/api/registrations/`

| Method | Endpoint | Auth | Notes |
|--------|----------|------|-------|
| POST | `/` | JWT | Requires vehicle + all 3 docs with OCR COMPLETED |
| GET | `/` | JWT | All registrations for logged-in user |

### Search — `/api/search/`

| Method | Endpoint | Auth | Rate Limit | Notes |
|--------|----------|------|------------|-------|
| GET | `/vehicle/?vehicle_number=X` | **None** | 60/min | Public gate lookup. Returns minimal info |
| GET | `/vehicle/staff/?vehicle_number=X` | JWT STAFF/ADMIN | 120/min | Returns full student + vehicle + photo |

### Admin — `/api/admin/`

| Method | Endpoint | Auth | Notes |
|--------|----------|------|-------|
| GET | `/dashboard/stats/` | JWT ADMIN | Returns pending/approved/rejected counts |
| GET | `/registrations/` | JWT ADMIN | Filter: `?status=PENDING\|APPROVED\|REJECTED` |
| GET | `/registrations/{id}/` | JWT ADMIN | Full detail with all documents |
| POST | `/registrations/{id}/approve/` | JWT ADMIN | 400 if already reviewed |
| POST | `/registrations/{id}/reject/` | JWT ADMIN | Body: `{reason}`. 400 if already reviewed |

---

## Data Models

### User
| Field | Type | Notes |
|-------|------|-------|
| email | EmailField (unique) | Login field |
| role | CharField | USER / STAFF / ADMIN |
| is_verified | BooleanField | Set true on account creation |

### UserProfile
| Field | Type | Notes |
|-------|------|-------|
| user | OneToOne → User | — |
| first_name | CharField | — |
| last_name | CharField | — |
| student_number | CharField (unique) | Cross-validated against College ID OCR |
| photo | ImageField (nullable) | Stored at `/media/profile_photos/` |

### Vehicle
| Field | Type | Notes |
|-------|------|-------|
| vehicle_number | CharField (unique globally) | Normalized to uppercase |
| vehicle_type | CharField | CAR / BIKE / SCOOTY |
| vehicle_model | CharField | e.g. Honda City |
| vehicle_color | CharField | — |
| rc_number | CharField | — |
| owner_name | CharField | Cross-validated against RC OCR |

### UserDocument
| Field | Type | Notes |
|-------|------|-------|
| document_type | CharField | RC / DL / COLLEGE_ID |
| file | FileField | `/media/documents/` |
| ocr_status | CharField | PENDING / PROCESSING / COMPLETED / FAILED |
| verification_status | CharField | PENDING / VERIFIED / REJECTED (unused — admin approves at registration level) |
| extracted_data | JSONField | `{vehicle_number, dl_number, student_id, raw_text}` |

### VehicleRegistration
| Field | Type | Notes |
|-------|------|-------|
| status | CharField | PENDING / APPROVED / REJECTED |
| cross_validation_warnings | JSONField | List of strings — flags, not blockers |
| rejection_reason | TextField (nullable) | Set on reject |
| reviewed_at | DateTimeField (nullable) | Set on approve or reject |
| unique_together | (user, vehicle) | One registration per vehicle per user |

---

## OCR Pipeline

1. File uploaded → saved to disk
2. If PDF: `pdf2image` converts page 1 → image → `pytesseract`
3. If image: `pytesseract` directly
4. Regex extraction:
   - Vehicle number: `[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}`
   - DL number: `[A-Z]{2}[0-9]{13}`
   - Student ID: `\b\d{8}\b`
5. `extracted_data` stored in `UserDocument.extracted_data`

OCR works best on clear, well-lit photos. Blurry images return `null` for structured fields but always return `raw_text`.

---

## Cross-Validation (auto-run on registration submit)

Three checks run and produce warnings (not blockers — admin decides):

1. Vehicle number on RC matches the registered vehicle number
2. Owner name appears in RC raw text
3. Student ID on College ID matches `profile.student_number`

---

## Rate Limiting

Uses DRF throttling backed by Redis:

| Throttle | Rate | Applied To |
|----------|------|------------|
| OTP | 5/hour per IP | Register, Forgot Password |
| Login | 20/hour per IP | Login |
| Upload | 30/hour per user | Document Upload |
| Public Search | 60/minute per IP | Public vehicle search |
| Staff Search | 120/minute per user | Staff vehicle search |

---

## Permissions

| Class | Allows |
|-------|--------|
| `IsAuthenticated` | Any valid JWT |
| `IsStaffUser` | role = STAFF or ADMIN |
| `IsAdminUser` | role = ADMIN only |

---

## Known Limitations

1. **Media files on server disk** — not backed up automatically. If EC2 instance is terminated, all uploaded documents are lost. Production fix: migrate to S3 using `django-storages`.
2. **Access token is 15 min** — frontend must implement silent refresh using the refresh token.
3. **OCR only reads page 1 of PDFs** — sufficient for ID documents.
4. **DL not cross-validated** — DL is uploaded and OCR'd but extracted `dl_number` is stored and never verified against anything. Future: verify format or cross-check against a registry.
5. **No email verification on forgot-password** — the forgot-password OTP flow reuses the same `EmailOTP` table. If a registration OTP is pending for an email, forgot-password will delete it.
6. **`verification_status` on documents is unused** — stays PENDING forever. Admin approval happens at the registration level, not per-document.

---

## PDF-Promised Features — Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| College email sign-up | ✅ Done | Only @akgec.ac.in allowed |
| Document upload (RC, DL, College ID) | ✅ Done | |
| OCR extraction | ✅ Done | pytesseract |
| Cross-validation | ✅ Done | Warnings, not blockers |
| Public vehicle search | ✅ Done | No auth required |
| Admin approve/reject | ✅ Done | With email notifications |
| Staff gate verification | ✅ Done | Staff-authenticated endpoint with full student details |
| Barcode-based ID verification | ✅ Frontend handled | Flutter/Web scans the barcode on the college ID → sends extracted student number as plain string → backend stores and cross-validates normally. No backend change needed. |
| AI-based document forgery detection | ❌ Not done | PDF mentioned "AI-powered OCR and image analysis". Currently using basic Tesseract OCR. Would require a vision model or dedicated forgery detection service. |

---

## Future Enhancements (from PDF + audit)

1. **S3 storage** — replace local disk with `django-storages` + AWS S3. One config change.
2. **AI document validation** — integrate a vision model to detect if uploaded documents are genuine (not screenshots of PDFs or edited images).
3. **DL cross-validation** — DL is uploaded and OCR extracts `dl_number`, but it is not yet cross-validated against owner name or any registry. Add owner name check against DL raw text (same pattern as RC).
4. **Sticker issuance tracking** — add a `sticker_issued` boolean on `VehicleRegistration` so guards can mark when a physical sticker is handed out.
5. **Push notifications (FCM)** — integrate Firebase Cloud Messaging to notify students when registration is approved/rejected in addition to email. Backend needs to store FCM device tokens per user and call FCM API on approve/reject.
6. **Password complexity** — currently min 8 chars only. Add uppercase, number, and special character requirements.

---

## Project Team

| Person | Role |
|--------|------|
| Agrim Dubey | Backend |
| Ayush Singh | Backend |
| Vishwajeet | Web frontend |
| Shreeyansh | Mobile app (Flutter) |

---

## Admin Panel

Django admin at `https://vems.akgec.ac.in/admin/`  
Use to: promote users to STAFF/ADMIN, inspect raw DB records, manage registrations manually.
