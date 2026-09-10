# Quick Start Guide

Get the Notes API running in 5 minutes.

## Option 1: Using Pipenv (Recommended)

```bash
# 1. Install dependencies
pipenv install

# 2. Activate virtual environment
pipenv shell

# 3. Initialize database
flask db upgrade

# 4. Seed sample data (optional)
python seed.py

# 5. Run the server
flask run
```

**Server will be running at**: `http://localhost:5000`

---

## Option 2: Using pip + venv

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
flask db upgrade

# 5. Seed sample data (optional)
python seed.py

# 6. Run the server
flask run
```

---

## Test the API with Curl

### 1. Sign Up
```bash
curl -X POST http://localhost:5000/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "password123",
    "password_confirmation": "password123"
  }'
```

### 2. Login and Get Token
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "password123"
  }'
```

Copy the `access_token` from the response.

### 3. Create a Note
```bash
curl -X POST http://localhost:5000/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "My First Note",
    "content": "This is my first note!"
  }'
```

### 4. Get All Notes
```bash
curl -X GET http://localhost:5000/notes \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Test with Postman

1. **Download Postman**: https://www.postman.com/downloads/
2. **Import the following endpoints**:
   - `POST /signup`
   - `POST /login`
   - `GET /notes`
   - `POST /notes`
   - `PATCH /notes/<id>`
   - `DELETE /notes/<id>`
3. **Set Authorization** on requests to use the JWT token from login

---

## Sample Test Credentials (if seeded)

```
Username: alice
Password: password123

Username: bob
Password: password456

Username: charlie
Password: password789
```

---

## Troubleshooting

### Port Already in Use
```bash
flask run --port 5001
```

### Database Not Found
```bash
flask db upgrade
```

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Still Having Issues?
Check the full README.md for detailed documentation and troubleshooting.

---

## Next Steps

1. ✅ Server is running
2. ✅ Test endpoints with curl or Postman
3. 📖 Read the full README.md for complete API documentation
4. 🚀 Deploy to production (Heroku, AWS, etc.)

Enjoy building! 🎉
