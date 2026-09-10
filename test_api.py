"""
Test suite for the Notes API using pytest.

Run with: pytest test_api.py -v
"""

import pytest
import json
from sqlalchemy.pool import StaticPool
from app import app, db
from models import User, Note
from config import TestingConfig


@pytest.fixture
def client():
    """Create a test client with a fresh, isolated database for each test."""
    app.config.from_object(TestingConfig)
    # Use a single shared connection so the in-memory DB persists across the
    # whole test (a new connection to sqlite :memory: would be a new empty DB).
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'poolclass': StaticPool,
        'connect_args': {'check_same_thread': False},
    }

    with app.app_context():
        db.drop_all()      # clear any tables left over from a previous test
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def auth_token(client):
    """Register and login a test user, return the JWT token"""
    # Sign up
    signup_response = client.post('/signup', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'password_confirmation': 'testpass123'
    })
    return signup_response.json['access_token']


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_signup_success(self, client):
        """Test successful user registration"""
        response = client.post('/signup', json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        assert response.status_code == 201
        assert response.json['username'] == 'alice'
        assert 'access_token' in response.json
    
    def test_signup_missing_fields(self, client):
        """Test signup with missing fields"""
        response = client.post('/signup', json={
            'username': 'alice'
        })
        assert response.status_code == 400
        assert 'errors' in response.json
    
    def test_signup_password_mismatch(self, client):
        """Test signup with mismatched passwords"""
        response = client.post('/signup', json={
            'username': 'alice',
            'password': 'password123',
            'password_confirmation': 'different'
        })
        assert response.status_code == 400
        assert 'Passwords do not match' in str(response.json['errors'])
    
    def test_signup_duplicate_username(self, client):
        """Test signup with duplicate username"""
        # First signup
        client.post('/signup', json={
            'username': 'alice',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Try duplicate
        response = client.post('/signup', json={
            'username': 'alice',
            'password': 'different123',
            'password_confirmation': 'different123'
        })
        assert response.status_code == 400
        assert 'Username already taken' in str(response.json['errors'])
    
    def test_login_success(self, client):
        """Test successful login"""
        # Signup first
        client.post('/signup', json={
            'username': 'alice',
            'password': 'password123',
            'password_confirmation': 'password123'
        })
        
        # Login
        response = client.post('/login', json={
            'username': 'alice',
            'password': 'password123'
        })
        assert response.status_code == 200
        assert response.json['username'] == 'alice'
        assert 'access_token' in response.json
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/login', json={
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        assert 'errors' in response.json
    
    def test_logout(self, client, auth_token):
        """Test logout"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.delete('/logout', headers=headers)
        assert response.status_code == 200


class TestNotes:
    """Test note CRUD endpoints"""
    
    def test_create_note(self, client, auth_token):
        """Test creating a note"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.post('/notes', 
            json={
                'title': 'Test Note',
                'content': 'This is test content'
            },
            headers=headers
        )
        assert response.status_code == 201
        assert response.json['title'] == 'Test Note'
        assert response.json['content'] == 'This is test content'
    
    def test_create_note_missing_fields(self, client, auth_token):
        """Test creating a note with missing fields"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.post('/notes',
            json={'title': 'Test'},
            headers=headers
        )
        assert response.status_code == 400
    
    def test_get_notes_empty(self, client, auth_token):
        """Test getting notes when none exist"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/notes', headers=headers)
        assert response.status_code == 200
        assert response.json['notes'] == []
        assert response.json['pagination']['total'] == 0
    
    def test_get_notes_paginated(self, client, auth_token):
        """Test getting notes with pagination"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # Create 3 notes
        for i in range(3):
            client.post('/notes',
                json={
                    'title': f'Note {i}',
                    'content': f'Content {i}'
                },
                headers=headers
            )
        
        # Get first page
        response = client.get('/notes?page=1&per_page=2', headers=headers)
        assert response.status_code == 200
        assert len(response.json['notes']) == 2
        assert response.json['pagination']['total'] == 3
        assert response.json['pagination']['pages'] == 2
    
    def test_get_single_note(self, client, auth_token):
        """Test getting a single note"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # Create note
        create_response = client.post('/notes',
            json={
                'title': 'Test Note',
                'content': 'Test content'
            },
            headers=headers
        )
        note_id = create_response.json['id']
        
        # Get note
        response = client.get(f'/notes/{note_id}', headers=headers)
        assert response.status_code == 200
        assert response.json['id'] == note_id
        assert response.json['title'] == 'Test Note'
    
    def test_get_nonexistent_note(self, client, auth_token):
        """Test getting a note that doesn't exist"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/notes/999', headers=headers)
        assert response.status_code == 404
    
    def test_update_note(self, client, auth_token):
        """Test updating a note"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # Create note
        create_response = client.post('/notes',
            json={
                'title': 'Original Title',
                'content': 'Original content'
            },
            headers=headers
        )
        note_id = create_response.json['id']
        
        # Update note
        response = client.patch(f'/notes/{note_id}',
            json={
                'title': 'Updated Title',
                'content': 'Updated content'
            },
            headers=headers
        )
        assert response.status_code == 200
        assert response.json['title'] == 'Updated Title'
        assert response.json['content'] == 'Updated content'
    
    def test_delete_note(self, client, auth_token):
        """Test deleting a note"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        # Create note
        create_response = client.post('/notes',
            json={
                'title': 'To Delete',
                'content': 'This will be deleted'
            },
            headers=headers
        )
        note_id = create_response.json['id']
        
        # Delete note
        response = client.delete(f'/notes/{note_id}', headers=headers)
        assert response.status_code == 200
        
        # Verify it's deleted
        verify_response = client.get(f'/notes/{note_id}', headers=headers)
        assert verify_response.status_code == 404


class TestAuthorization:
    """Test authorization and access control"""
    
    def test_access_without_token(self, client):
        """Test that unauthenticated users can't access notes"""
        response = client.get('/notes')
        assert response.status_code == 401
    
    def test_user_cant_access_others_notes(self, client):
        """Test that users can't access other users' notes"""
        # Create two users
        user1_response = client.post('/signup', json={
            'username': 'user1',
            'password': 'password1',
            'password_confirmation': 'password1'
        })
        token1 = user1_response.json['access_token']
        
        user2_response = client.post('/signup', json={
            'username': 'user2',
            'password': 'password2',
            'password_confirmation': 'password2'
        })
        token2 = user2_response.json['access_token']
        
        # User1 creates a note
        headers1 = {'Authorization': f'Bearer {token1}'}
        create_response = client.post('/notes',
            json={'title': 'User1 Note', 'content': 'Private'},
            headers=headers1
        )
        note_id = create_response.json['id']
        
        # User2 tries to access it
        headers2 = {'Authorization': f'Bearer {token2}'}
        response = client.get(f'/notes/{note_id}', headers=headers2)
        assert response.status_code == 403
    
    def test_user_cant_delete_others_notes(self, client):
        """Test that users can't delete other users' notes"""
        # Create two users
        user1_response = client.post('/signup', json={
            'username': 'user1',
            'password': 'password1',
            'password_confirmation': 'password1'
        })
        token1 = user1_response.json['access_token']
        
        user2_response = client.post('/signup', json={
            'username': 'user2',
            'password': 'password2',
            'password_confirmation': 'password2'
        })
        token2 = user2_response.json['access_token']
        
        # User1 creates a note
        headers1 = {'Authorization': f'Bearer {token1}'}
        create_response = client.post('/notes',
            json={'title': 'User1 Note', 'content': 'Private'},
            headers=headers1
        )
        note_id = create_response.json['id']
        
        # User2 tries to delete it
        headers2 = {'Authorization': f'Bearer {token2}'}
        response = client.delete(f'/notes/{note_id}', headers=headers2)
        assert response.status_code == 403


class TestHealthCheck:
    """Test utility endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])