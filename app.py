from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from flask_cors import CORS
import os
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from models import db, bcrypt, User, Note

# Initialize Flask app
app = Flask(__name__)

# Load configuration based on environment
env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    app.config.from_object(ProductionConfig)
elif env == 'testing':
    app.config.from_object(TestingConfig)
else:
    app.config.from_object(DevelopmentConfig)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
CORS(app)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.route('/signup', methods=['POST'])
def signup():
    """Register a new user with username and password"""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'errors': ['Username and password are required']}), 400
    
    username = data.get('username').strip()
    password = data.get('password')
    password_confirmation = data.get('password_confirmation')
    email = data.get('email', '').strip() or None
    
    # Validate password confirmation
    if password != password_confirmation:
        return jsonify({'errors': ['Passwords do not match']}), 400
    
    # Validate password length
    if len(password) < 6:
        return jsonify({'errors': ['Password must be at least 6 characters']}), 400
    
    # Check if user exists
    if User.query.filter_by(username=username).first():
        return jsonify({'errors': ['Username already taken']}), 400
    
    if email and User.query.filter_by(email=email).first():
        return jsonify({'errors': ['Email already registered']}), 400
    
    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    # Generate JWT token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'access_token': access_token
    }), 201


@app.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'errors': ['Username and password are required']}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # Find user
    user = User.query.filter_by(username=username).first()
    
    # Verify credentials
    if not user or not user.check_password(password):
        return jsonify({'errors': ['Invalid username or password']}), 401
    
    # Generate JWT token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'access_token': access_token
    }), 200


@app.route('/check_session', methods=['GET'])
def check_session():
    """Check if user is authenticated (for compatibility with session-based frontend)"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return jsonify({}), 401
    
    try:
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        user_id = int(decoded['sub'])
        user = db.session.get(User, user_id)
        
        if user:
            return jsonify(user.to_dict()), 200
    except Exception:
        pass
    
    return jsonify({}), 401


@app.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    """Logout user (JWT is stateless, just return success)"""
    return jsonify({'message': 'Logged out successfully'}), 200


# ============================================================================
# NOTE ENDPOINTS - CRUD OPERATIONS
# ============================================================================

@app.route('/notes', methods=['GET'])
@jwt_required()
def get_notes():
    """
    Get all notes for the authenticated user with pagination.
    Query params: page (default=1), per_page (default=10)
    """
    user_id = int(get_jwt_identity())
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate pagination params
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
    
    # Query notes for this user
    pagination = Note.query.filter_by(user_id=user_id).order_by(Note.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    notes = [note.to_dict() for note in pagination.items]
    
    return jsonify({
        'notes': notes,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@app.route('/notes', methods=['POST'])
@jwt_required()
def create_note():
    """Create a new note for the authenticated user"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'errors': ['Title and content are required']}), 400
    
    title = data.get('title').strip()
    content = data.get('content').strip()
    
    # Validate non-empty
    if not title or not content:
        return jsonify({'errors': ['Title and content cannot be empty']}), 400
    
    # Create note
    note = Note(title=title, content=content, user_id=user_id)
    db.session.add(note)
    db.session.commit()
    
    return jsonify(note.to_dict()), 201


@app.route('/notes/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    """Get a specific note (must be owned by authenticated user)"""
    user_id = int(get_jwt_identity())
    
    note = db.session.get(Note, note_id)
    
    # Check if note exists
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    # Check authorization
    if note.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(note.to_dict()), 200


@app.route('/notes/<int:note_id>', methods=['PATCH', 'PUT'])
@jwt_required()
def update_note(note_id):
    """Update a note (must be owned by authenticated user)"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    note = db.session.get(Note, note_id)
    
    # Check if note exists
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    # Check authorization
    if note.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update fields if provided
    if 'title' in data:
        title = data.get('title').strip() if data.get('title') else note.title
        if not title:
            return jsonify({'errors': ['Title cannot be empty']}), 400
        note.title = title
    
    if 'content' in data:
        content = data.get('content').strip() if data.get('content') else note.content
        if not content:
            return jsonify({'errors': ['Content cannot be empty']}), 400
        note.content = content
    
    db.session.commit()
    
    return jsonify(note.to_dict()), 200


@app.route('/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    """Delete a note (must be owned by authenticated user)"""
    user_id = int(get_jwt_identity())
    
    note = db.session.get(Note, note_id)
    
    # Check if note exists
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    # Check authorization
    if note.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({'message': 'Note deleted successfully'}), 200


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
