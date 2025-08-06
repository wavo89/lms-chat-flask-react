from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
from flask_login import LoginManager
import os
from config import Config
from models import db, bcrypt, User
from api import register_blueprints

app = Flask(__name__, static_folder='frontend/build')
app.config.from_object(Config)

# Initialize extensions
CORS(app, supports_credentials=True)
db.init_app(app)
bcrypt.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register API blueprints
register_blueprints(app)

# Serve React Frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve the React frontend application."""
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors by serving React app (for client-side routing)."""
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 