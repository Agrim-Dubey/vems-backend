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

Add this header to every protected request:

```
Authorization: Bearer <access_token>
```

When the access token expires you will receive `401` with `"message": "Token expired"`. Call the refresh endpoint to silently get a new access token without making the user log in again.

---

## 2. Role-Based Routing

After login, call `GET /api/auth/me/` to get the user's role and navigate to the correct screen.

```
role == "USER"   →  Student registration flow
role == "STAFF"  →  Vehicle scanner screen
role == "ADMIN"  →  Admin dashboard
```

---

## 3. Complete User Flow (Step by Step)

This is the exact sequence a student goes through from first open to getting approved:

```
1.  Enter college email (@akgec.ac.in)
          ↓
2.  POST /api/auth/register/             → OTP sent to email
          ↓
3.  Enter OTP (valid for 10 minutes)
          ↓
4.  POST /api/auth/verify-otp/           → OTP marked verified
          ↓
5.  Set a password
          ↓
6.  POST /api/auth/set-password/         → account created
          ↓
7.  POST /api/auth/login/                → get access_token + refresh_token
          ↓
8.  GET  /api/auth/me/                   → check role, navigate to student screen
          ↓
9.  POST /api/users/profile/             → save name, student number, photo
          ↓
10. POST /api/vehicles/                  → add vehicle details, save the returned id
          ↓
11. POST /api/documents/upload/  × 3    → upload RC, DL, College ID (OCR runs automatically)
          ↓
12. POST /api/registrations/             → submit registration for admin review
          ↓
13. GET  /api/registrations/             → poll to check approval status
          ↓
14. User receives email when admin approves or rejects
```

**Step 11 must be done 3 times** — once for each document type: `RC`, `DL`, `COLLEGE_ID`.

**Step 12 will fail** unless all 3 documents are uploaded and OCR has completed on each one. If a document's `ocr_status` comes back as `"FAILED"`, the user must re-upload that document before submitting.

---

## 4. Complete Staff Flow (Step by Step)

Staff accounts are created by the admin — staff do not self-register.

```
1.  POST /api/auth/login/            → get tokens
          ↓
2.  GET  /api/auth/me/               → role == "STAFF" → open scanner screen
          ↓
3.  Scan vehicle number plate
          ↓
4.  GET  /api/search/vehicle/?vehicle_number=UP14AB1234   → check if approved
          ↓
5.  Show result: green (verified) or red (not verified)
```

The search endpoint requires **no login**. Staff login is only needed so the app knows to show the scanner UI. The search itself is public and works without any token.

---

## 5. Auth Endpoints

### Register (send OTP)

Starts the registration flow for a new student. Sends a 6-digit OTP to their college email. Does not create an account yet — that only happens after OTP verification and password setup.

Calling this again for the same email (before the account is created) resends a fresh OTP with a new 10-minute timer.

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

**Errors:**

| HTTP | `message` | Cause |
|---|---|---|
| `400` | `{"email": ["Invalid college email"]}` | Email is not `@akgec.ac.in` |
| `400` | `{"email": ["Email already exists"]}` | Account already created for this email |

---

### Verify OTP

Marks the OTP as verified. Must be called before `set-password`. OTPs expire after 10 minutes.

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

**Errors:**

| HTTP | `message` | Cause |
|---|---|---|
| `400` | `"Invalid OTP"` | OTP does not match |
| `400` | `"OTP expired"` | More than 10 minutes since OTP was sent |

---

### Set Password (creates the account)

Creates the user account. Requires OTP to have been verified first via `verify-otp`. Passwords must match.

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

**Errors:**

| HTTP | Field / `message` | Cause |
|---|---|---|
| `400` | `{"confirm_password": ["Passwords do not match"]}` | Passwords differ |
| `400` | `"OTP verification required"` | `verify-otp` was not called first |
| `400` | `"Account already exists"` | Account already created for this email |

---

### Login

Authenticates the user and returns both tokens. Use `access_token` for all protected requests. Store `refresh_token` securely to silently refresh the session later.

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

**Errors:**

| HTTP | `message` | Cause |
|---|---|---|
| `400` | `"Invalid credentials"` | Wrong email or password |

---

### Refresh Access Token

Gets a new access token using the refresh token. Call this silently when any request returns `401 "Token expired"` — no need to send the user back to the login screen.

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

**Errors:**

| HTTP | `message` | Cause |
|---|---|---|
| `400` | `"Refresh token required"` | Body was empty |
| `401` | `"Refresh token expired"` | 7 days have passed — user must log in again |
| `401` | `"Invalid refresh token"` | Token is malformed |
| `401` | `"Invalid token type"` | An access token was sent instead of a refresh token |
| `401` | `"User not found"` | Account was deleted |

---

### Get Current User

Returns the currently authenticated user's ID, email, and role. Call this immediately after login to decide which screen to show.

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

`role` will be `"USER"`, `"STAFF"`, or `"ADMIN"`.

**Errors:**

| HTTP | `message` | Cause |
|---|---|---|
| `401` | `"Authentication credentials were not provided."` | No Authorization header sent |
| `401` | `"Token expired"` | Access token has expired — refresh it |

---

## 6. Profile Endpoints

### Create / Update Profile

Saves the student's personal details. Must be completed before the student can submit a registration. Calling this endpoint again on the same account updates the existing profile — it will not create a duplicate.

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
| `student_number` | string | yes (unique) |
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

**Errors:**

| HTTP | Field | Cause |
|---|---|---|
| `400` | `{"first_name": ["This field is required."]}` | Missing field |
| `400` | `{"student_number": ["user profile with this student number already exists."]}` | Student number already in use |
| `401` | — | Token missing or expired |

---

### Get Profile

Returns the current user's saved profile. Use this to pre-fill the profile form or check whether the profile has been completed.

```
GET /api/users/profile/
🔒 Requires: Authorization header
```

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

**Errors:**

| HTTP | `message` | Cause |
|---|---|---|
| `404` | `"Profile not found"` | Profile has not been created yet |
| `401` | — | Token missing or expired |

---

## 7. Vehicle Endpoints

### Add Vehicle

Adds a vehicle to the student's account. A student must add a vehicle before they can submit a registration. Save the `id` from the response — you will need it when submitting the registration.

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

**Errors:**

| HTTP | Field / `message` | Cause |
|---|---|---|
| `400` | `{"vehicle_number": ["vehicle with this vehicle number already exists."]}` | Another user has already registered this number |
| `400` | `{"vehicle_type": ["\"TRUCK\" is not a valid choice."]}` | Invalid vehicle type |
| `400` | `{"owner_name": ["This field is required."]}` | Missing required field |
| `401` | — | Token missing or expired |

---

### List My Vehicles

Returns all vehicles added by the current user. Use this to let the student select which vehicle to submit a registration for.

```
GET /api/vehicles/
🔒 Requires: Authorization header
```

**Response `200`:** array of vehicle objects (same shape as above).

```json
[
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
]
```

Returns an empty array `[]` if no vehicles have been added yet.

---

## 8. Document Endpoints

### Upload a Document

Uploads a document file and runs OCR on it immediately. Must be done 3 times — once for each document type: `RC`, `DL`, `COLLEGE_ID`. Only the most recent upload per document type is checked at registration time, so re-uploading replaces the previous one.

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

**Always check `ocr_status` in the response before proceeding:**

| `ocr_status` | What to do |
|---|---|
| `"COMPLETED"` | Document is ready — proceed to the next upload or submit registration |
| `"FAILED"` | OCR could not read the document — ask the user to re-upload a clearer image |

**Errors:**

| HTTP | Field / `message` | Cause |
|---|---|---|
| `400` | `{"document_type": ["This field is required."]}` | Missing document type |
| `400` | `{"document_type": ["\"PASSPORT\" is not a valid choice."]}` | Invalid document type |
| `400` | `{"file": ["No file was submitted."]}` | Missing file |
| `401` | — | Token missing or expired |

---

### List My Documents

Returns all documents uploaded by the current user. Use this to show the student which documents they have already uploaded and their current OCR status.

```
GET /api/documents/upload/
🔒 Requires: Authorization header
```

**Response `200`:** array of document objects (same shape as above).

```json
[
  {
    "id": 7,
    "user": 5,
    "document_type": "RC",
    "file": "/media/documents/rc_upload.jpg",
    "ocr_status": "COMPLETED",
    "extracted_data": { "vehicle_number": "UP14AB1234", "dl_number": null, "student_id": null, "raw_text": "..." },
    "verification_status": "PENDING",
    "uploaded_at": "2026-06-19T10:35:00Z"
  },
  {
    "id": 8,
    "user": 5,
    "document_type": "DL",
    "file": "/media/documents/dl_upload.jpg",
    "ocr_status": "COMPLETED",
    "extracted_data": { "vehicle_number": null, "dl_number": "UP1420230012345", "student_id": null, "raw_text": "..." },
    "verification_status": "PENDING",
    "uploaded_at": "2026-06-19T10:36:00Z"
  }
]
```

Returns an empty array `[]` if no documents have been uploaded yet.

---

### Retry OCR on a Document

Re-runs OCR on a previously uploaded document. Use this if the original upload returned `"ocr_status": "FAILED"` and the user does not want to re-upload the file. If re-uploading is possible, prefer that instead — uploading a clearer image gives better results.

```
POST /api/ocr/process/<document_id>/
🔒 Requires: Authorization header
```

**No body required.** `document_id` is the `id` from the document upload response.

**Response `200` (OCR succeeded):**

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

**Errors:**

| HTTP | `message` | Cause |
|---|---|---|
| `404` | `"Document not found"` | ID does not exist or belongs to another user |
| `500` | `"OCR processing failed — please re-upload a clearer image"` | OCR failed again — ask user to re-upload |
| `401` | — | Token missing or expired |

---

## 9. Registration Endpoints

A **registration** is the student's formal application to bring their vehicle on campus. It links a student's account to one of their vehicles and goes through an admin review process before being approved or rejected.

**To submit a registration the student must have:**
1. A completed profile (`POST /api/users/profile/`)
2. A vehicle added to their account (`POST /api/vehicles/`)
3. All 3 documents uploaded with `ocr_status == "COMPLETED"` (RC, DL, College ID)

There is one registration per student per vehicle. A student cannot submit a second registration for the same vehicle.

---

### Submit Registration

Submits the student's vehicle registration for admin review. The backend validates that all prerequisites are met and runs cross-document consistency checks before creating the registration record.

After a successful submit the registration status is `"PENDING"`. The student will receive an email when the admin approves or rejects it.

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

`vehicle` is the `id` returned when the vehicle was added.

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

**About `cross_validation_warnings`:**

This is a list of strings. An empty list means the backend found no inconsistencies across the uploaded documents. A non-empty list means the backend flagged something — for example, the vehicle number on the RC does not match the registered vehicle number. This is **information for the admin**, not an error for the student. The registration is still created and goes to the admin for review regardless.

Example with warnings:

```json
{
  "cross_validation_warnings": [
    "Vehicle number on RC (UP14AB9999) does not match registered vehicle number (UP14AB1234)",
    "Student ID on College ID (2100456) does not match profile student number (2100123)"
  ]
}
```

**Errors:**

| HTTP | Field / `message` | Cause |
|---|---|---|
| `400` | `{"vehicle": ["This field is required."]}` | No vehicle ID in request body |
| `400` | `"Registration already submitted for this vehicle"` | This vehicle was already registered |
| `400` | `"No vehicle registered"` | Vehicle ID does not exist on the account |
| `400` | `"RC document missing"` | RC has not been uploaded yet |
| `400` | `"DL document missing"` | DL has not been uploaded yet |
| `400` | `"COLLEGE_ID document missing"` | College ID has not been uploaded yet |
| `400` | `"RC OCR not completed — please re-upload a clearer image"` | RC OCR failed — user must re-upload |
| `400` | `"DL OCR not completed — please re-upload a clearer image"` | DL OCR failed — user must re-upload |
| `400` | `"COLLEGE_ID OCR not completed — please re-upload a clearer image"` | College ID OCR failed — user must re-upload |
| `404` | `"Vehicle not found"` | Vehicle ID does not belong to this user |
| `401` | — | Token missing or expired |

---

### Check My Registration Status

Returns all registrations submitted by the current user. Poll this to check whether the admin has approved or rejected the registration.

```
GET /api/registrations/
🔒 Requires: Authorization header
```

**Response `200`:** array of registration objects.

```json
[
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
]
```

Returns an empty array `[]` if no registration has been submitted yet.

**What to show for each `status` value:**

| `status` | What to show the user |
|---|---|
| `"PENDING"` | "Your application is under review" |
| `"APPROVED"` | "Your vehicle has been approved" |
| `"REJECTED"` | Show the `rejection_reason` string to the user |

The user also receives an **email** automatically when the admin approves or rejects.

---

## 10. Search Endpoint (No Auth Required)

Used at the campus gate after scanning or manually entering a vehicle number plate. Returns whether the vehicle has an approved registration. No login or token required — security guards can use this directly.

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

**Response — vehicle not found or not yet approved:**

```json
{
  "verified": false
}
```

**Response — missing query param:**

```json
{
  "verified": false,
  "message": "vehicle_number param required"
}
```

HTTP `400` when the param is missing. HTTP `200` for all other cases regardless of `verified` value.

Show a clear **green screen** for `"verified": true` and **red screen** for `"verified": false`.

---

## 11. Admin Endpoints

All admin endpoints require `role == "ADMIN"`. Calling them with a USER or STAFF token returns `403 "Admin access required"`.

---

### Dashboard Stats

Returns a count of registrations in each state. Use this to build the admin overview screen.

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

Returns all registrations across all users, ordered by most recently submitted. Can be filtered by status. Use this to show the admin the registration queue.

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
  }
]
```

If `cross_validation_warnings` is non-empty, highlight the registration so the admin knows to check the documents carefully before approving.

---

### Registration Detail (with Documents and OCR Data)

Returns full information about one registration including the student's uploaded documents and extracted OCR data. Use this for the admin's review screen — the admin needs to see the document images and extracted fields before deciding.

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
    "user": 5,
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
      "user": 5,
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
      "user": 5,
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
      "user": 5,
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

**Errors:**

| HTTP | `message` | Cause |
|---|---|---|
| `404` | `"Registration not found"` | ID does not exist |

---

### Approve a Registration

Approves the registration and sends an approval email to the student automatically. The registration `status` changes to `"APPROVED"`.

```
POST /api/admin/registrations/<id>/approve/
🔒 Requires: Admin token
```

**Body:** empty

**Response `200`:**

```json
{
  "message": "Registration approved"
}
```

**Errors:**

| HTTP | `message` | Cause |
|---|---|---|
| `404` | `"Registration not found"` | ID does not exist |
| `403` | `"Admin access required"` | Token is not an admin token |

---

### Reject a Registration

Rejects the registration with a reason and sends a rejection email to the student automatically. The `reason` is stored and shown to the student when they check their status. The `reason` field is required.

```
POST /api/admin/registrations/<id>/reject/
🔒 Requires: Admin token
```

**Body:**

```json
{
  "reason": "RC document is not legible. Please re-submit with a clearer scan."
}
```

**Response `200`:**

```json
{
  "message": "Registration rejected"
}
```

**Errors:**

| HTTP | Field / `message` | Cause |
|---|---|---|
| `400` | `{"reason": ["This field is required."]}` | Reason not provided |
| `404` | `"Registration not found"` | ID does not exist |
| `403` | `"Admin access required"` | Token is not an admin token |

---

## 12. Error Reference

### HTTP Status Codes

| Code | Meaning |
|---|---|
| `200` | Success |
| `201` | Created (registration submitted) |
| `400` | Bad request — check the response body for what is wrong |
| `401` | Token missing, expired, or invalid — refresh the token or redirect to login |
| `403` | Wrong role — the user does not have permission for this endpoint |
| `404` | Resource not found |
| `500` | Server-side failure (e.g. OCR crashed) — display a generic error, let the user retry |

### Error Response Shapes

All non-validation errors follow this shape:

```json
{
  "message": "Human readable description of the problem"
}
```

Validation errors (missing fields, invalid values) follow this shape:

```json
{
  "field_name": ["Description of what is wrong with this field."]
}
```

Multiple field errors can appear together:

```json
{
  "first_name": ["This field is required."],
  "student_number": ["This field is required."]
}
```

### Common 401 Messages

| `message` | What to do |
|---|---|
| `"Authentication credentials were not provided."` | No Authorization header was sent |
| `"Token expired"` | Call `/api/auth/refresh/` to get a new access token |
| `"Invalid token"` | Token is malformed — redirect to login |
| `"Invalid authorization header format"` | Header is not in `Bearer <token>` format |

### Common 403 Message

| `message` | What to do |
|---|---|
| `"Admin access required"` | User is not an admin — do not show admin screens |
| `"Staff or admin access required"` | User does not have staff-level access |
