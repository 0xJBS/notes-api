# Notes API - Secure JWT-Authenticated Backend

A production-ready Flask REST API for a note-taking application with JWT authentication. Users can securely register, login, and manage their own notes with full CRUD operations and pagination support.

## Features

✅ **JWT Authentication** - Secure token-based authentication with expiration  
✅ **User Registration & Login** - Secure password hashing with bcrypt  
✅ **CRUD Operations** - Create, read, update, and delete notes  
✅ **Pagination** - Efficient data retrieval with customizable page sizes  
✅ **Authorization** - Users can only access and modify their own notes  
✅ **Data Validation** - Input validation on all endpoints  
✅ **Error Handling** - Consistent, descriptive error responses  
✅ **Database Migrations** - Flask-Migrate for schema management  
✅ **CORS Support** - Ready for frontend integration  

## Tech Stack

- **Framework**: Flask 2.2.2
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: JWT (Flask-JWT-Extended)
- **Password Hashing**: bcrypt (Flask-Bcrypt)
- **Validation**: Marshmallow
- **Migrations**: Flask-Migrate
- **Testing**: Pytest

## Project Structure

```
notes_api/
├── app.py              # Main Flask application with all routes
├── models.py           # SQLAlchemy database models (User, Note)
├── config.py           # Configuration for different environments
├── seed.py             # Database seeding script with sample data
├── Pipfile             # Project dependencies
├── Pipfile.lock        # Locked dependency versions
├── README.md           # This file
├── migrations/         # Database migration files (created by Flask-Migrate)
└── app.db              # SQLite database (created at runtime)
```

## Installation

### Prerequisites

- Python 3.8.13 or higher
- pip or pipenv
- Git

### Setup Instructions

1. **Clone the repository** (if you haven't already)
   ```bash
   git clone <repository-url>
   cd notes_api
   ```

2. **Install dependencies with Pipenv**
   ```bash
   pipenv install
   ```
   
   This installs all packages specified in `Pipfile`, including:
   - Flask and extensions
   - SQLAlchemy for database
   - JWT for authentication
   - bcrypt for password hashing
   - And more...

3. **Activate the virtual environment**
   ```bash
   pipenv shell
   ```
   
   Or prepend commands with `pipenv run` if not entering the shell.

4. **Initialize the database with migrations**
   ```bash
   flask db upgrade
   ```
   
   If this is the first time, you may need to initialize migrations:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Seed the database with sample data** (optional)
   ```bash
   python seed.py
   ```
   
   This creates:
   - 3 test users (alice, bob, charlie)
   - 5-8 sample notes per user
   - Test passwords listed in the console output

## Running the Application

### Development Server

Start the Flask development server:

```bash
flask run
```

Or:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Production Server

For production, use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Environment Variables

Create a `.env` file for sensitive configuration:

```
FLASK_ENV=development
FLASK_APP=app.py
JWT_SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///app.db
```

## API Endpoints

### Authentication Endpoints

#### 1. Register (Sign Up)
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
- 400: Username/email already taken, passwords don't match, missing fields
- 400: Password less than 6 characters

---

#### 2. Login
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

#### 3. Check Session
Verify current user authentication (useful for frontend).

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

#### 4. Logout
Logout the current user (JWT is stateless, so this is mainly for client-side cleanup).

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

#### 5. Get All Notes (Paginated)
Retrieve paginated list of the authenticated user's notes.

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
    },
    {
      "id": 2,
      "title": "Project ideas",
      "content": "Consider implementing...",
      "user_id": 1,
      "created_at": "2024-01-14T15:45:00",
      "updated_at": "2024-01-14T15:45:00"
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

#### 6. Create a Note
Create a new note for the authenticated user.

**Endpoint**: `POST /notes`

**Request Body**:
```json
{
  "title": "My First Note",
  "content": "This is the content of my note. It can be quite long!"
}
```

**Response** (201 Created):
```json
{
  "id": 9,
  "title": "My First Note",
  "content": "This is the content of my note. It can be quite long!",
  "user_id": 1,
  "created_at": "2024-01-16T09:00:00",
  "updated_at": "2024-01-16T09:00:00"
}
```

**Errors**:
- 400: Missing title or content
- 400: Empty title or content
- 401: Missing or invalid token

---

#### 7. Get a Single Note
Retrieve a specific note (must be owned by authenticated user).

**Endpoint**: `GET /notes/<note_id>`

**Example**: `GET /notes/1`

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

#### 8. Update a Note
Modify an existing note (must be owned by authenticated user).

**Endpoint**: `PATCH /notes/<note_id>` or `PUT /notes/<note_id>`

**Example**: `PATCH /notes/1`

**Request Body** (partial update):
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

#### 9. Delete a Note
Delete a note (must be owned by authenticated user).

**Endpoint**: `DELETE /notes/<note_id>`

**Example**: `DELETE /notes/1`

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

---

## Testing with Postman

### Setup Postman Environment

1. **Create a new Postman collection**
2. **Add an environment variable** for the base URL:
   - `base_url`: `http://localhost:5000`
3. **Add a variable** for the JWT token (set after login):
   - `access_token`: (empty initially)

### Sample Testing Flow

1. **Sign Up**: POST to `/signup` with test credentials
2. **Login**: POST to `/login` → Save the `access_token` from response
3. **Create Note**: POST to `/notes` with `Authorization: Bearer {{access_token}}`
4. **Get Notes**: GET `/notes` with the auth header
5. **Update Note**: PATCH `/notes/1` with updated data
6. **Delete Note**: DELETE `/notes/1`

### Postman Authorization Setup

For authenticated requests:
1. Select the request
2. Go to **Authorization** tab
3. Choose **Bearer Token** type
4. Paste your JWT token in the token field
5. Or use the environment variable: `{{access_token}}`

---

## Security Considerations

✅ **Password Hashing**: All passwords are hashed using bcrypt with salt  
✅ **JWT Tokens**: Tokens expire after 30 days (configurable)  
✅ **Authorization Checks**: Users cannot access other users' notes  
✅ **Input Validation**: All inputs are validated and sanitized  
✅ **CORS**: Configured to prevent cross-site requests  
✅ **HTTPS**: Use in production (set `SESSION_COOKIE_SECURE = True`)  

### Production Recommendations

1. Change `JWT_SECRET_KEY` to a strong random value
2. Use PostgreSQL instead of SQLite for production
3. Enable HTTPS (set `SESSION_COOKIE_SECURE = True`)
4. Set `DEBUG = False` in production
5. Use environment variables for sensitive data
6. Use a production WSGI server (Gunicorn, uWSGI)
7. Add rate limiting to prevent abuse
8. Implement request logging and monitoring

---

## Troubleshooting

### Database Issues

**Problem**: `No such table: user`  
**Solution**: Run migrations: `flask db upgrade`

**Problem**: `(sqlite3.OperationalError) database is locked`  
**Solution**: Close other connections; use PostgreSQL for concurrent access

### Authentication Issues

**Problem**: Token not recognized  
**Solution**: Ensure token is passed in `Authorization: Bearer <token>` header

**Problem**: Expired token  
**Solution**: Login again to get a fresh token

### Port Already in Use

**Problem**: `Address already in use`  
**Solution**: Change the port: `flask run --port 5001`

---

## Development Workflow

### Making Database Changes

1. Modify models in `models.py`
2. Create a migration: `flask db migrate -m "Description"`
3. Review the migration file
4. Apply it: `flask db upgrade`

### Testing Locally

1. Seed the database: `python seed.py`
2. Start the server: `flask run`
3. Use Postman or curl to test endpoints
4. Check responses and status codes

### Git Workflow

```bash
# Make your changes
git add .
git commit -m "Add new feature"
git push origin main
```

---

## API Response Format

### Success Response (2xx)
```json
{
  "id": 1,
  "username": "alice",
  ...
}
```

### Error Response (4xx, 5xx)
```json
{
  "error": "Description of what went wrong"
}
```

or

```json
{
  "errors": [
    "Validation error 1",
    "Validation error 2"
  ]
}
```

---

## License

This project is provided as-is for educational purposes.

---

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the endpoint documentation
3. Test with Postman
4. Check server logs for detailed error messages

---

**Created for the Secure API Backend Lab**  
JWT Authentication | Flask | SQLAlchemy | SQLite
