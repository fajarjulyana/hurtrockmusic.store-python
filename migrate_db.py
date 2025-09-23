
#!/usr/bin/env python3
"""
Database migration script to ensure all tables and columns exist
"""
import os
from flask import Flask
from database import db
import models

# Create minimal Flask app for database operations
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

def migrate_database():
    """Create or update database tables"""
    with app.app_context():
        try:
            # Drop all tables and recreate them to ensure schema matches models
            print("Dropping existing tables...")
            db.drop_all()
            
            print("Creating all tables...")
            db.create_all()
            
            print("Database migration completed successfully!")
            return True
        except Exception as e:
            print(f"Migration failed: {e}")
            return False

if __name__ == "__main__":
    migrate_database()
