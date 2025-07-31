#!/usr/bin/env python3
"""
Database clearing script - drops ALL tables.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from config import Config
from models import db
from sqlalchemy import text

def create_app():
    """Create Flask app instance for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def clear_database():
    """Drop ALL tables in the database."""
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
            print("✅ All tables cleared!")
        else:
            print("📋 No existing tables found - database already empty")

def main():
    """Main clearing process."""
    try:
        print("🚨 WARNING: This will DELETE ALL TABLES and DATA in your database!")
        
        response = input("Are you sure you want to continue? (y/n): ")
        if response.lower() != 'y':
            print("❌ Operation cancelled")
            return
        
        clear_database()
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 