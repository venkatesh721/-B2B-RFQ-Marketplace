# B2B RFQ Marketplace

Small assignment project scaffold for a business-to-business Request for Quotation (RFQ) marketplace. It includes the core database schema and configuration, but intentionally has no API views, serializers, or RFQ user-interface flows yet.

## Stack

- Frontend: React, Vite, React Router, Axios
- Backend: Django and Django REST Framework
- Database: MySQL
- Authentication foundation: JWT with `djangorestframework-simplejwt`

## Project layout

```
backend/                 Django API
  config/                Project-wide settings and URL configuration
  users/                 Email-based User model and account code
  rfqs/                  RFQ and Quotation models
frontend/                React single-page application
  src/api/               Shared Axios client
  src/pages/             Route-level page components
```

## Important files

| File | Purpose |
| --- | --- |
| `backend/config/settings.py` | Loads environment variables, connects Django to MySQL, enables DRF, JWT authentication, and CORS for the React app. |
| `backend/config/urls.py` | Keeps project URLs in one place, including the authentication endpoints. |
| `backend/users/serializers.py` | Validates registration and login data and defines safe user API responses. |
| `backend/users/views.py` | Implements register, login, and the protected current-user endpoint. |
| `backend/users/permissions.py` | Reusable BUYER/SUPPLIER and ownership authorization rules for future RFQ and quotation views. |
| `backend/.env.example` | Safe template for backend environment settings. Copy it to `.env`; do not commit the copy. |
| `backend/requirements.txt` | Python packages required by the backend. |
| `backend/users/models.py` | Defines the custom email-based User model and its BUYER/SUPPLIER roles. |
| `backend/rfqs/models.py` | Defines RFQ and Quotation tables, their relationships, validation, indexes, and constraints. |
| `backend/rfqs/serializers.py` | Validates buyer RFQ input and provides a buyer-private-free representation for suppliers. |
| `backend/rfqs/views.py` | Role-aware RFQ REST endpoints, using reusable permissions, filtering, search, and pagination. |
| `backend/*/migrations/` | Versioned instructions Django uses to create the tables, indexes, and constraints in MySQL. |
| `frontend/vite.config.js` | Minimal Vite configuration with React support. |
| `frontend/src/main.jsx` | React entry point; wraps the app with `BrowserRouter`. |
| `frontend/src/App.jsx` | Central route definition, currently only a setup home page and a 404 page. |
| `frontend/src/api/client.js` | One reusable Axios instance, using `VITE_API_BASE_URL`. |
| `frontend/.env.example` | Safe template for the frontend API base URL. |
| `.gitignore` | Prevents secrets, dependencies, builds, and local files from being committed. |

## Database relationships

- A `User` is either a `BUYER` or `SUPPLIER` and signs in with a unique email address.
- One buyer can create many RFQs. Each RFQ belongs to exactly one buyer.
- One RFQ can receive many quotations. Each quotation belongs to exactly one RFQ and exactly one supplier.
- A supplier can quote a particular RFQ only once. The database enforces this with a unique `(rfq, supplier)` constraint.
- RFQs have an `OPEN`/`CLOSED` status, so model validation rejects quotations on a closed RFQ.

The schema enforces positive quantities and prices at database level. Model validation also rejects RFQs created by non-buyers, quotations created by non-suppliers, and a buyer quoting on their own RFQ.

## Local setup

### 1. Create the MySQL database

Create an empty database named `rfq_marketplace` (or use a different name and set it in the backend environment file).

### 2. Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

Update the MySQL password and any other values in `backend/.env` before running migrations.

For production, set `DJANGO_DEBUG=False` and provide a long random `DJANGO_SECRET_KEY`. HTTPS redirect, secure cookies, HSTS, and content-type sniffing protection are enabled by default in this mode. If TLS is terminated by a trusted reverse proxy, configure the documented `DJANGO_SECURE_*` environment overrides to match that deployment.

## Authentication API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/auth/register/` | Register a buyer or supplier. |
| `POST` | `/api/auth/login/` | Log in with email and password and receive JWT tokens. |
| `POST` | `/api/auth/refresh/` | Exchange a refresh token for a new access token. |
| `GET` | `/api/auth/me/` | Return the current user. Send `Authorization: Bearer <access-token>`. |

Registration accepts `email`, `password`, `name`, and a role of exactly `BUYER` or `SUPPLIER`. It validates the email, enforces Django's configured password-strength rules, and stores the password using Django's secure one-way password hash. The response has only safe user fields—never a password.

Login verifies the submitted email and password with Django's authentication system. On success it returns a short-lived access token, a refresh token, and the same safe user fields. The JWTs are signed credentials; by default SimpleJWT includes a token type, issue/expiry times, a unique token ID where applicable, and the user ID. They do not contain the password.

For protected endpoints, DRF's `JWTAuthentication` reads and verifies the Bearer access token, loads its user ID, and makes that user available as `request.user`. The `/api/auth/me/` view requires this authentication. Passwords are never stored directly because a database leak would expose every user's secret; Django stores a salted one-way hash and checks a login attempt by safely comparing hashes.

## Role-based authorization

Authentication answers **who is making the request**. In this project, a valid JWT identifies the logged-in user; without it, DRF returns HTTP `401 Unauthorized` for protected endpoints.

Authorization answers **whether that user may perform this action**. The reusable permission classes in `users/permissions.py` return HTTP `403 Forbidden` for an authenticated user without permission:

- `IsBuyer`: use when creating RFQs.
- `IsRFQBuyer`: use when editing or deleting an RFQ; it checks that the buyer owns that RFQ.
- `CanViewRFQ`: lets a buyer view only their RFQs and lets a supplier view only available, unexpired RFQs. `visible_rfqs_for(user)` provides the matching queryset for future list/browse views.
- `CanSubmitQuotation`: lets only suppliers quote open, unexpired RFQs.
- `IsQuotationSupplier`: lets only the supplier who submitted a quotation modify it.
- `IsSelf`: use for private user-detail endpoints, preventing one user from reading another user's private data.

Future RFQ and quotation API views should apply these classes with `permission_classes`. Quotation model validation separately rejects a quotation for a closed or expired RFQ, providing a second line of defense.

## Buyer RFQ API

All endpoints require a Buyer JWT in `Authorization: Bearer <access-token>`.

| Method | Endpoint | Result |
| --- | --- | --- |
| `POST` | `/api/rfqs/` | Creates an RFQ for the authenticated buyer (`201 Created`). |
| `GET` | `/api/rfqs/` | Lists only the authenticated buyer's RFQs. |
| `GET` | `/api/rfqs/{id}/` | Returns one RFQ owned by that buyer. |
| `PUT` / `PATCH` | `/api/rfqs/{id}/` | Updates an RFQ owned by that buyer. |
| `DELETE` | `/api/rfqs/{id}/` | Deletes an RFQ owned by that buyer (`204 No Content`). |

`RFQSerializer` accepts only `product_or_service_name`, `requirement_description`, `quantity`, `delivery_location`, and `deadline` as writable business fields. It makes ownership server-controlled, requires all creation fields through the model schema, rejects quantities of zero or below, and rejects past deadlines. The viewset combines `IsBuyer` for creation/listing with `IsRFQBuyer` for detail, update, and delete, returning `401` without authentication and `403` when a buyer tries to access another buyer's RFQ.

## Supplier RFQ browsing API

The same read endpoints are role-aware. A supplier receives only `OPEN`, unexpired RFQs and cannot see the buyer ID or other buyer profile information.

| Method | Endpoint | Supplier behaviour |
| --- | --- | --- |
| `GET` | `/api/rfqs/` | Browse available RFQs with pagination (10 per page). |
| `GET` | `/api/rfqs/{id}/` | View an available RFQ; expired/non-available RFQs return `404`. |

Use `?search=steel` to search product/service name and delivery location. Use `?product_or_service_name=steel` and `?delivery_location=mumbai` for simple case-insensitive filters. `?page=2` and optional `?page_size=20` control pagination (maximum page size: 50). Available results are always restricted to open, non-expired RFQs; no request parameter can expose expired ones.

Run the API tests without MySQL using:

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py test rfqs --settings=config.settings_test
```

## Quotation API

All quotation endpoints require a JWT. Quotation ownership is server-controlled; clients cannot submit a supplier ID.

| Method | Endpoint | Access and result |
| --- | --- | --- |
| `POST` | `/api/quotations/` | Supplier submits one quotation for an open, unexpired RFQ (`201 Created`). Required fields: `rfq`, `quoted_price`, and `estimated_delivery_time`; `message` is optional. |
| `GET` | `/api/quotations/my/` | Supplier receives only their own submitted quotations. |
| `GET` | `/api/rfqs/{id}/quotations/` | The RFQ's owning buyer receives its quotations. |

The API returns `400 Bad Request` for a non-positive price, a closed/expired RFQ, or a duplicate quote. The database additionally enforces both a positive price and one quotation per `(rfq, supplier)`, including under concurrent requests. Buyers cannot submit quotations, suppliers cannot see another supplier's quotation, and a buyer cannot read quotations for another buyer's RFQ.

### 3. Start the frontend

In another terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open the local URL printed by Vite, normally `http://localhost:5173`.

## Next implementation stage

Add frontend quotation flows when the user-interface requirements are agreed.
