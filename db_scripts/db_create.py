#!/usr/bin/env python3
"""
Database setup script - creates tables from models.
Run this after clearing the database to create fresh tables.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from config import Config
from models import db

def create_app():
    """Create Flask app instance for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def create_database():
    """Create all tables from models."""
    app = create_app()
    
    with app.app_context():
        print("🏗️  Creating tables from models...")
        db.create_all()
        print("✅ Tables created successfully!")

if __name__ == '__main__':
    try:
        create_database()
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        sys.exit(1) 