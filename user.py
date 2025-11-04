# Database configuration
basedir = os.path.abspath(os.path.dirname(_file_))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'interioai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'interioai-secret-key-change-in-production'

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User Model - Stores user registration data"""
    _tablename_ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with designs
    designs = db.relationship('Design', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'designs_count': len(self.designs)
        }


class Design(db.Model):
    """Design Model - Stores user design projects"""
    _tablename_ = 'design'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    style = db.Column(db.String(50), nullable=False)
    palette = db.Column(db.String(100), nullable=False)
    furniture = db.Column(db.Text, nullable=True)
    width = db.Column(db.String(20), nullable=False)
    length = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert design object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_type': self.room_type,
            'style': self.style,
            'palette': self.palette,
            'furniture': self.furniture,
            'width': self.width,
            'length': self.length,
            'created_at': self.created_at.isoformat()
        }


# ==================== DATABASE INITIALIZATION ====================

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully!")


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not all(key in data for key in ['name', 'email', 'password']):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'Email already registered'}), 409
        
        # Create new user
        new_user = User(
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(data['password'])
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('email') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'user_id': user.id
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== USER ROUTES ====================

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details by ID"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user details"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            if User.query.filter_by(email=data['email']).filter(User.id != user_id).first():
                return jsonify({'success': False, 'error': 'Email already in use'}), 409
            user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== DESIGN ROUTES ====================

@app.route('/api/designs', methods=['POST'])
def save_design():
    """Save a design project"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Validate design data
        required_fields = ['room_type', 'style', 'palette', 'width', 'length']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Create new design
        new_design = Design(
            user_id=user_id,
            room_type=data['room_type'],
            style=data['style'],
            palette=data['palette'],
            furniture=data.get('furniture', ''),
            width=data['width'],
            length=data['length']
        )
        
        db.session.add(new_design)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Design saved successfully',
            'design': new_design.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/designs/<int:user_id>', methods=['GET'])
def get_user_designs(user_id):
    """Get all designs for a user"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        designs = Design.query.filter_by(user_id=user_id).order_by(Design.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'designs': [design.to_dict() for design in designs],
            'total': len(designs)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/designs/single/<int:design_id>', methods=['GET'])
def get_design(design_id):
    """Get a specific design"""
    try:
        design = Design.query.get(design_id)
        
        if not design:
            return jsonify({'success': False, 'error': 'Design not found'}), 404
        
        return jsonify({
            'success': True,
            'design': design.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/designs/<int:design_id>', methods=['DELETE'])
def delete_design(design_id):
    """Delete a design"""
    try:
        design = Design.query.get(design_id)
        
        if not design:
            return jsonify({'success': False, 'error': 'Design not found'}), 404
        
        db.session.delete(design)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Design deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'InterioAI Backend is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ==================== RUN APPLICATION ====================

if _name_ == '_main_':
    # Initialize database
    init_db()
    
    # Run Flask app
    print("🚀 Starting InterioAI Backend...")
    print("🌐 Server running at http://0.0.0.0:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
