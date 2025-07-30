#!/usr/bin/env python3
"""
Complete database cleanup script for LMS application.
This script will:
1. Connect to the database
2. Drop ALL existing tables (not just our models)
3. Create fresh tables from our models
4. Seed with test user
"""

import os
import sys
from flask import Flask
from config import Config
from models import db, User
import psycopg2
from sqlalchemy import text

def create_app():
    """Create Flask app instance for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def drop_all_tables():
    """Drop ALL tables in the database, including ones not managed by SQLAlchemy."""
    app = create_app()
    
    with app.app_context():
        print("🗄️  Connecting to database...")
        
        # Get all table names first
        result = db.session.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """))
        
        table_names = [row[0] for row in result.fetchall()]
        
        if table_names:
            print(f"📋 Found {len(table_names)} existing tables:")
            for table in table_names:
                print(f"   - {table}")
            
            print("🧹 Dropping all existing tables...")
            
            # Drop all tables with CASCADE to handle dependencies
            for table in table_names:
                try:
                    db.session.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                    print(f"   ✅ Dropped {table}")
                except Exception as e:
                    print(f"   ⚠️  Warning dropping {table}: {e}")
            
            db.session.commit()
        else:
            print("📋 No existing tables found")

def setup_fresh_database():
    """Create fresh tables and seed data."""
    app = create_app()
    
    with app.app_context():
        print("🏗️  Creating new tables from models...")
        db.create_all()
        
        # Seed test user
        print("🌱 Seeding test user...")
        test_user = User(
            email='test@test.com',
            name='Test User'
        )
        test_user.set_password('Sample12')
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Database setup complete!")
        print(f"   📧 Test user: test@test.com")
        print(f"   🔑 Password: Sample12")
        print(f"   🆔 User ID: {test_user.id}")

def main():
    """Main cleanup and setup process."""
    try:
        print("🚨 WARNING: This will DELETE ALL DATA in your database!")
        print("   This includes any existing tables not created by this app.")
        
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled")
            return
        
        drop_all_tables()
        setup_fresh_database()
        
        print("\n🎉 Database completely cleaned and reinitialized!")
        
    except Exception as e:
        print(f"❌ Error during database cleanup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 