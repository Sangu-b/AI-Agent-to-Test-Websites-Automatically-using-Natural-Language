"""
Flask Application - Test Website Server
Serves a static login page for testing the AI agent
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')


@app.route('/')
def index():
    """Render the main login page"""
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Simple validation for testing purposes
    if username and password:
        if username == 'testuser' and password == 'testpass':
            return jsonify({
                'success': True,
                'message': 'Login successful!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
    else:
        return jsonify({
            'success': False,
            'message': 'Username and password are required'
        }), 400


@app.route('/dashboard')
def dashboard():
    """Simple dashboard page after successful login"""
    return render_template('dashboard.html')


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
