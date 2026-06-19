# VEMS Backend — API Documentation

> **For:** Flutter Developer (Shreeyansh)
> **Base URL:** `http://vems.akgec.ac.in`
> **Content-Type:** `application/json` for all requests **except** file uploads (use `multipart/form-data`)

---

## Table of Contents

1. [How Authentication Works](#1-how-authentication-works)
2. [Role-Based Routing](#2-role-based-routing)
3. [Complete User Flow](#3-complete-user-flow-step-by-step)
4. [Complete Staff Flow](#4-complete-staff-flow-step-by-step)
5. [Auth Endpoints](#5-auth-endpoints)
6. [Profile Endpoints](#6-profile-endpoints)
7. [Vehicle Endpoints](#7-vehicle-endpoints)
8. [Document Endpoints](#8-document-endpoints)
9. [Registration Endpoints](#9-registration-endpoints)
10. [Search Endpoint](#10-search-endpoint-no-auth-required)
11. [Admin Endpoints](#11-admin-endpoints)
12. [Error Reference](#12-error-reference)

---

## 1. How Authentication Works

The backend uses **JWT (JSON Web Tokens)**. After login you get two tokens:

| Token | Lifetime | Purpose |
|---|---|---|
| `access_token` | 15 minutes | Send with every protected request |
| `refresh_token` | 7 days | Use to get a new access token when it expires |

**How to attach the token to a request:**

Add this header to every protected request:

```
Authorization: Bearer <access_token>
```

**When the access token expires** (you'll get `401 Token expired`), call the refresh endpoint to get a new one without making the user log in again.

---

## 2. Role-Based Routing

After login, call `GET /api/auth/me/` to get the user's role and route them to the right screen.

```
role == "USER"   →  Student registration flow
role == "STAFF"  →  Vehicle scanner screen
role == "ADMIN"  →  Admin dashboard
```

---

## 3. Complete User Flow (Step by Step)

This is the exact sequence a student goes through:

```
1.  Enter college email (@akgec.ac.in)
          ↓
2.  POST /api/auth/register/         → OTP sent to email
          ↓
3.  Enter OTP (valid for 10 minutes)
          ↓
4.  POST /api/auth/verify-otp/       → OTP marked verified
          ↓
5.  Set a password
          ↓
6.  POST /api/auth/set-password/     → account created
          ↓
7.  POST /api/auth/login/            → get access_token + refresh_token
          ↓
8.  POST /api/users/profile/         → save first name, last name, student number, photo
          ↓
9.  POST /api/vehicles/              → add vehicle details
          ↓
10. POST /api/documents/upload/  x3  → upload RC, DL, College ID (OCR runs automatically)
          ↓
11. POST /api/registrations/         → submit registration for admin review
          ↓
12. GET  /api/registrations/         → poll to check approval status
          ↓
13. User receives email when admin approves or rejects
```

> **Important:** Step 10 must be done 3 times — once for each document type: `RC`, `DL`, `COLLEGE_ID`.
> The registration submit (Step 11) will **fail** unless all 3 documents are uploaded and OCR has completed.
> If a document's OCR fails, the user must re-upload that document before submitting.

---

## 4. Complete Staff Flow (Step by Step)

```
1.  POST /api/auth/login/            → get tokens (staff account created by admin)
          ↓
2.  GET  /api/auth/me/               → role == "STAFF" → open scanner screen
          ↓
3.  Scan vehicle number plate
          ↓
4.  GET  /api/search/vehicle/?vehicle_number=XX   → check if approved
          ↓
5.  Show result: verified or not verified
```

> **Note:** The search endpoint requires **no login**. Staff login is only needed so the app knows to show the scanner UI. The search itself is public.

---

## 5. Auth Endpoints

### Register (send OTP)

```
POST /api/auth/register/
```

**Body:**

```json
{
  "email": "2100123@akgec.ac.in"
}
```

**Response `200`:**

```json
{
  "message": "OTP sent successfully"
}
```

**Errors:** `400` if email is not `@akgec.ac.in` or is already registered.

> Calling register again for the same email resends a fresh OTP with a new 10-minute timer.

---

### Verify OTP

```
POST /api/auth/verify-otp/
```

**Body:**

```json
{
  "email": "2100123@akgec.ac.in",
  "otp": "482910"
}
```

**Response `200`:**

```json
{
  "message": "OTP verified successfully"
}
```

**Errors:** `400` if OTP is wrong or expired (OTPs expire after 10 minutes).

---

### Set Password (creates the account)

```
POST /api/auth/set-password/
```

**Body:**

```json
{
  "email": "2100123@akgec.ac.in",
  "password": "MyPassword123",
  "confirm_password": "MyPassword123"
}
```

**Response `200`:**

```json
{
  "message": "Account created successfully"
}
```

**Errors:** `400` if OTP was not verified first, passwords don't match, or account already exists.

---

### Login

```
POST /api/auth/login/
```

**Body:**

```json
{
  "email": "2100123@akgec.ac.in",
  "password": "MyPassword123"
}
```

**Response `200`:**

```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:** `400` invalid credentials.

---

### Refresh Access Token

```
POST /api/auth/refresh/
```

**Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `200`:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:** `401` if refresh token is expired — user must log in again.

---

### Get Current User

```
GET /api/auth/me/
🔒 Requires: Authorization header
```

**Response `200`:**

```json
{
  "id": 5,
  "email": "2100123@akgec.ac.in",
  "role": "USER"
}
```

> `role` will be `"USER"`, `"STAFF"`, or `"ADMIN"`. Use this to decide which screen to show after login.

---

## 6. Profile Endpoints

### Create / Update Profile

```
POST /api/users/profile/
🔒 Requires: Authorization header
Content-Type: multipart/form-data
```

**Fields:**

| Field | Type | Required |
|---|---|---|
| `first_name` | string | yes |
| `last_name` | string | yes |
| `student_number` | string | yes (must be unique) |
| `photo` | image file | no |

**Response `200`:**

```json
{
  "id": 1,
  "first_name": "Rahul",
  "last_name": "Verma",
  "student_number": "2100123",
  "photo": "/media/profile_photos/rahul.jpg"
}
```

> Calling this endpoint again on the same account will **update** the existing profile, not create a duplicate.

---

### Get Profile

```
GET /api/users/profile/
🔒 Requires: Authorization header
```

**Response `200`:** same shape as above.
**Response `404`:** if profile has not been created yet.

---

## 7. Vehicle Endpoints

### Add Vehicle

```
POST /api/vehicles/
🔒 Requires: Authorization header
```

**Body:**

```json
{
  "owner_name": "Rahul Verma",
  "vehicle_number": "UP14AB1234",
  "vehicle_type": "BIKE",
  "vehicle_model": "Honda Shine",
  "vehicle_color": "Black",
  "rc_number": "RC1234567890"
}
```

| Field | Allowed Values |
|---|---|
| `vehicle_type` | `"CAR"`, `"BIKE"`, `"SCOOTY"` |
| `vehicle_number` | must be unique across all users |

**Response `200`:**

```json
{
  "id": 3,
  "user": 5,
  "owner_name": "Rahul Verma",
  "vehicle_number": "UP14AB1234",
  "vehicle_type": "BIKE",
  "vehicle_model": "Honda Shine",
  "vehicle_color": "Black",
  "rc_number": "RC1234567890",
  "is_active": true,
  "created_at": "2026-06-19T10:30:00Z"
}
```

> Save the `id` from this response — you will need it when submitting the registration.

---

### List My Vehicles

```
GET /api/vehicles/
🔒 Requires: Authorization header
```

**Response `200`:** array of vehicle objects (same shape as above).

---

## 8. Document Endpoints

### Upload a Document

```
POST /api/documents/upload/
🔒 Requires: Authorization header
Content-Type: multipart/form-data
```

**Fields:**

| Field | Type | Allowed Values |
|---|---|---|
| `document_type` | string | `"RC"`, `"DL"`, `"COLLEGE_ID"` |
| `file` | file | image (jpg/png) or PDF |

**Do this 3 times — once for each document type.**

**Response `200`:**

```json
{
  "id": 7,
  "user": 5,
  "document_type": "RC",
  "file": "/media/documents/rc_upload.jpg",
  "ocr_status": "COMPLETED",
  "extracted_data": {
    "vehicle_number": "UP14AB1234",
    "dl_number": null,
    "student_id": null,
    "raw_text": "..."
  },
  "verification_status": "PENDING",
  "uploaded_at": "2026-06-19T10:35:00Z"
}
```

**`ocr_status` values:**

| Value | Meaning | What to do |
|---|---|---|
| `COMPLETED` | OCR ran successfully | proceed |
| `FAILED` | OCR could not read the document | ask user to re-upload a clearer image |
| `PROCESSING` | Still running | unlikely — OCR is synchronous |

> **Registration submit will fail if the latest upload of any document type has `ocr_status != "COMPLETED"`.**
> If a document fails, the user just uploads it again — only the most recent upload per type is checked.

---

### List My Documents

```
GET /api/documents/upload/
🔒 Requires: Authorization header
```

**Response `200`:** array of document objects (same shape as above).

---

## 9. Registration Endpoints

### Submit Registration

```
POST /api/registrations/
🔒 Requires: Authorization header
```

**Body:**

```json
{
  "vehicle": 3
}
```

> `vehicle` is the `id` you got when adding the vehicle.

**Response `201`:**

```json
{
  "id": 12,
  "user": 5,
  "vehicle": 3,
  "status": "PENDING",
  "rejection_reason": null,
  "cross_validation_warnings": [],
  "submitted_at": "2026-06-19T11:00:00Z",
  "reviewed_at": null
}
```

> `cross_validation_warnings` is a list of strings. Empty list means all document data was consistent.
> Non-empty means the backend flagged some inconsistency — the admin will review it manually.
> **This does not block approval** — it is information for the admin, not an error for the user.

**Example with warnings:**

```json
{
  "cross_validation_warnings": [
    "Vehicle number on RC (UP14AB9999) does not match registered vehicle number (UP14AB1234)",
    "Student ID on College ID (2100456) does not match profile student number (2100123)"
  ]
}
```

**`400` errors that block submission:**

| Message | What to do |
|---|---|
| `"RC document missing"` | User has not uploaded RC yet |
| `"DL document missing"` | User has not uploaded DL yet |
| `"COLLEGE_ID document missing"` | User has not uploaded College ID yet |
| `"RC OCR not completed — please re-upload a clearer image"` | RC upload failed OCR — re-upload |
| `"DL OCR not completed — please re-upload a clearer image"` | DL upload failed OCR — re-upload |
| `"COLLEGE_ID OCR not completed — please re-upload a clearer image"` | College ID upload failed OCR — re-upload |
| `"No vehicle registered"` | Vehicle was not added yet |
| `"Registration already submitted for this vehicle"` | Already submitted — check status instead |

**`404`:** Vehicle ID does not belong to this user.

---

### Check My Registration Status

```
GET /api/registrations/
🔒 Requires: Authorization header
```

**Response `200`:** array of registration objects (same shape as submit response above).

The key field is `status`:

| Status | What to show the user |
|---|---|
| `"PENDING"` | Your application is under review |
| `"APPROVED"` | Your vehicle has been approved |
| `"REJECTED"` | Show `rejection_reason` to the user |

> The user also receives an **email** automatically when the admin approves or rejects.

---

## 10. Search Endpoint (No Auth Required)

This is the endpoint used at the gate after scanning a vehicle number plate.

```
GET /api/search/vehicle/?vehicle_number=UP14AB1234
No auth needed
```

**Response — vehicle is approved:**

```json
{
  "verified": true,
  "owner_name": "Rahul Verma",
  "vehicle_number": "UP14AB1234",
  "vehicle_type": "BIKE",
  "vehicle_model": "Honda Shine"
}
```

**Response — not found or not approved:**

```json
{
  "verified": false
}
```

**Response — missing param:**

```json
{
  "verified": false,
  "message": "vehicle_number param required"
}
```

> Show a clear green screen for `verified: true` and red screen for `verified: false`.

---

## 11. Admin Endpoints

> All admin endpoints require `role == "ADMIN"`. Calling them with a USER or STAFF token returns `403`.

### Dashboard Stats

```
GET /api/admin/dashboard/stats/
🔒 Requires: Admin token
```

**Response `200`:**

```json
{
  "pending": 14,
  "approved": 52,
  "rejected": 3
}
```

---

### List All Registrations

```
GET /api/admin/registrations/
GET /api/admin/registrations/?status=PENDING
🔒 Requires: Admin token
```

Optional `?status=` filter: `PENDING`, `APPROVED`, `REJECTED`

**Response `200`:**

```json
[
  {
    "id": 12,
    "status": "PENDING",
    "submitted_at": "2026-06-19T11:00:00Z",
    "reviewed_at": null,
    "rejection_reason": null,
    "cross_validation_warnings": [
      "Vehicle number on RC (UP14AB9999) does not match registered vehicle number (UP14AB1234)"
    ],
    "user": {
      "id": 5,
      "email": "2100123@akgec.ac.in"
    },
    "vehicle": {
      "id": 3,
      "owner_name": "Rahul Verma",
      "vehicle_number": "UP14AB1234",
      "vehicle_type": "BIKE",
      "vehicle_model": "Honda Shine",
      "vehicle_color": "Black",
      "rc_number": "RC1234567890",
      "is_active": true,
      "created_at": "2026-06-19T10:30:00Z"
    }
  }
]
```

---

### Registration Detail (with Documents + OCR Data)

```
GET /api/admin/registrations/<id>/
🔒 Requires: Admin token
```

**Response `200`:**

```json
{
  "id": 12,
  "status": "PENDING",
  "submitted_at": "2026-06-19T11:00:00Z",
  "reviewed_at": null,
  "rejection_reason": null,
  "cross_validation_warnings": [],
  "user": {
    "id": 5,
    "email": "2100123@akgec.ac.in"
  },
  "vehicle": {
    "id": 3,
    "owner_name": "Rahul Verma",
    "vehicle_number": "UP14AB1234",
    "vehicle_type": "BIKE",
    "vehicle_model": "Honda Shine",
    "vehicle_color": "Black",
    "rc_number": "RC1234567890",
    "is_active": true,
    "created_at": "2026-06-19T10:30:00Z"
  },
  "documents": [
    {
      "id": 7,
      "document_type": "RC",
      "file": "/media/documents/rc.jpg",
      "ocr_status": "COMPLETED",
      "extracted_data": {
        "vehicle_number": "UP14AB1234",
        "dl_number": null,
        "student_id": null,
        "raw_text": "..."
      },
      "verification_status": "PENDING",
      "uploaded_at": "2026-06-19T10:35:00Z"
    },
    {
      "id": 8,
      "document_type": "DL",
      "file": "/media/documents/dl.jpg",
      "ocr_status": "COMPLETED",
      "extracted_data": {
        "vehicle_number": null,
        "dl_number": "UP1420230012345",
        "student_id": null,
        "raw_text": "..."
      },
      "verification_status": "PENDING",
      "uploaded_at": "2026-06-19T10:36:00Z"
    },
    {
      "id": 9,
      "document_type": "COLLEGE_ID",
      "file": "/media/documents/college_id.jpg",
      "ocr_status": "COMPLETED",
      "extracted_data": {
        "vehicle_number": null,
        "dl_number": null,
        "student_id": "2100123",
        "raw_text": "..."
      },
      "verification_status": "PENDING",
      "uploaded_at": "2026-06-19T10:37:00Z"
    }
  ]
}
```

---

### Approve a Registration

```
POST /api/admin/registrations/<id>/approve/
🔒 Requires: Admin token
```

**Body:** (empty)

**Response `200`:**

```json
{
  "message": "Registration approved"
}
```

> The user receives an approval email automatically.

---

### Reject a Registration

```
POST /api/admin/registrations/<id>/reject/
🔒 Requires: Admin token
```

**Body:**

```json
{
  "reason": "RC document is not legible. Please re-submit."
}
```

**Response `200`:**

```json
{
  "message": "Registration rejected"
}
```

> The user receives a rejection email with the reason automatically.

---

## 12. Error Reference

| HTTP Code | Meaning |
|---|---|
| `400` | Bad request — check `message` field for what's wrong |
| `401` | Token missing, expired, or invalid — redirect to login |
| `403` | Wrong role — user does not have permission for this endpoint |
| `404` | Resource not found |

**All error responses follow this shape:**

```json
{
  "message": "Human readable description of the problem"
}
```

**Validation errors** (missing or invalid fields) follow this shape:

```json
{
  "field_name": ["This field is required."]
}
```
