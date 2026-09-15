# Notes API - Secure JWT-Authenticated Backend

A Flask REST API for a note-taking application with JWT authentication. Users can securely register, log in, and manage their own notes with full CRUD operations and pagination support. Each note belongs to a single user, and access controls ensure users can only read or modify their own data.

**Author**: [0xJBS](https://github.com/0xJBS)
**Repository**: https://github.com/0xJBS/notes-api

## Features

- **JWT Authentication** - Secure token-based authentication with expiration
- **User Registration & Login** - Secure password hashing with bcrypt
- **CRUD Operations** - Create, read, update, and delete notes
- **Pagination** - Efficient data retrieval with customizable page sizes
- **Authorization** - Users can only access and modify their own notes
- **Data Validation** - Input validation on all endpoints
- **Error Handling** - Consistent, descriptive error responses
- **Database Migrations** - Flask-Migrate for schema management
- **CORS Support** - Ready for frontend integration

## Tech Stack

- **Framework**: Flask 3.0.3
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: JWT (Flask-JWT-Extended 4.6.0)
- **Password Hashing**: bcrypt (Flask-Bcrypt)
- **Migrations**: Flask-Migrate
- **Testing**: Pytest

## Project Structure

```
notes-api/
├── app.py              # Main Flask application with all routes
├── models.py           # SQLAlchemy database models (User, Note)
├── config.py           # Configuration for different environments
├── seed.py             # Database seeding script with sample data
├── test_api.py         # Pytest test suite
├── requirements.txt    # pip dependencies
├── Pipfile             # pipenv dependencies
├── README.md           # This file
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── migrations/         # Database migration files (Flask-Migrate)
```

## Installation

### Prerequisites

- Python 3.10 or higher (tested on Python 3.12 and 3.14)
- pip or pipenv
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/0xJBS/notes-api.git
   cd notes-api
   ```

2. **Install dependencies**

   Using pip:
   ```bash
   pip install -r requirements.txt
   ```

   Or using pipenv:
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Apply database migrations**
   ```bash
   flask db upgrade
   ```

   If you are starting from a clean checkout without a `migrations/` folder, initialize it first:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

4. **Seed the database with sample data** (optional)
   ```bash
   python seed.py
   ```

   This creates:
   - 3 test users (alice, bob, charlie)
   - 5-8 sample notes per user
   - Test passwords printed to the console

## Running the Application

Start the development server:

```bash
flask run
```

Or:

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

### Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

```
FLASK_ENV=development
FLASK_APP=app.py
JWT_SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///app.db
```

## Test Credentials (after seeding)

| Username | Password    |
|----------|-------------|
| alice    | password123 |
| bob      | password234 |
| charlie  | password345 |

## API Endpoints

### Authentication Endpoints

#### Register (Sign Up)
Create a new user account.

**Endpoint**: `POST /signup`

**Request Body**:
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "password123",
  "password_confirmation": "password123"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Errors**:
- 400: Username/email already taken, passwords don't match, missing fields, or password shorter than 6 characters

---

#### Login
Authenticate and receive a JWT token.

**Endpoint**: `POST /login`

**Request Body**:
```json
{
  "username": "alice",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Errors**:
- 400: Missing username or password
- 401: Invalid credentials

---

#### Check Session
Verify current user authentication (useful for frontend integration).

**Endpoint**: `GET /check_session`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2024-01-15T10:30:00"
}
```

**Errors**:
- 401: Invalid or missing token

---

#### Logout
Log out the current user. Because JWTs are stateless, this endpoint is mainly for client-side cleanup.

**Endpoint**: `DELETE /logout`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

### Note Endpoints (CRUD)

All note endpoints require JWT authentication via the `Authorization` header:
```
Authorization: Bearer <access_token>
```

#### Get All Notes (Paginated)
Retrieve a paginated list of the authenticated user's notes.

**Endpoint**: `GET /notes`

**Query Parameters**:
- `page` (optional, default=1): Page number
- `per_page` (optional, default=10, max=100): Notes per page

**Example**: `GET /notes?page=1&per_page=5`

**Response** (200 OK):
```json
{
  "notes": [
    {
      "id": 1,
      "title": "Daily standup notes",
      "content": "Discussed project timeline and blockers...",
      "user_id": 1,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 5,
    "total": 8,
    "pages": 2
  }
}
```

**Errors**:
- 401: Missing or invalid token

---

#### Create a Note
Create a new note for the authenticated user.

**Endpoint**: `POST /notes`

**Request Body**:
```json
{
  "title": "My First Note",
  "content": "This is the content of my note."
}
```

**Response** (201 Created):
```json
{
  "id": 9,
  "title": "My First Note",
  "content": "This is the content of my note.",
  "user_id": 1,
  "created_at": "2024-01-16T09:00:00",
  "updated_at": "2024-01-16T09:00:00"
}
```

**Errors**:
- 400: Missing or empty title/content
- 401: Missing or invalid token

---

#### Get a Single Note
Retrieve a specific note (must be owned by the authenticated user).

**Endpoint**: `GET /notes/<note_id>`

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Daily standup notes",
  "content": "Discussed project timeline and blockers...",
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Errors**:
- 401: Missing or invalid token
- 403: Note belongs to another user
- 404: Note not found

---

#### Update a Note
Modify an existing note (must be owned by the authenticated user).

**Endpoint**: `PATCH /notes/<note_id>` (also accepts `PUT`)

**Request Body** (partial update supported):
```json
{
  "title": "Updated Title",
  "content": "Updated content goes here"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Updated Title",
  "content": "Updated content goes here",
  "user_id": 1,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-16T14:22:30"
}
```

**Errors**:
- 400: Empty title or content
- 401: Missing or invalid token
- 403: Note belongs to another user
- 404: Note not found

---

#### Delete a Note
Delete a note (must be owned by the authenticated user).

**Endpoint**: `DELETE /notes/<note_id>`

**Response** (200 OK):
```json
{
  "message": "Note deleted successfully"
}
```

**Errors**:
- 401: Missing or invalid token
- 403: Note belongs to another user
- 404: Note not found

---

### Utility Endpoints

#### Health Check
Check API status.

**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy"
}
```

## Running the Tests

The project includes a pytest suite covering authentication, CRUD, pagination, and access control:

```bash
pytest test_api.py -v
```

All 19 tests should pass.

## Testing with Postman

1. `POST /signup` or `POST /login` to obtain an `access_token`.
2. For protected requests, set the **Authorization** tab to **Bearer Token** and paste the token.
3. Exercise the note endpoints: create, list (with `?page=` and `?per_page=`), fetch, update, and delete.

## Security Notes

- Passwords are hashed with bcrypt (never stored in plain text).
- JWT tokens expire after 30 days (configurable in `config.py`).
- Every note endpoint verifies ownership before returning or modifying data, so users cannot access each other's notes.
- Input is validated on all endpoints.

### For Production

- Set a strong random `JWT_SECRET_KEY`.
- Use PostgreSQL instead of SQLite.
- Enable HTTPS and set `SESSION_COOKIE_SECURE = True`.
- Set `DEBUG = False`.
- Serve with a production WSGI server such as Gunicorn.

## License

This project is provided as-is for educational purposes.

---

**Created for the Secure API Backend Lab** — JWT Authentication | Flask | SQLAlchemy | SQLite
