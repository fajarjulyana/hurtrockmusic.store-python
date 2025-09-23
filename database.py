from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def configure_database(app):
    """Configure database for PostgreSQL"""
    import os
    
    # Use PostgreSQL database from environment variable or create one
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("⚠️  DATABASE_URL tidak ditemukan, akan membuat database PostgreSQL...")
        return False
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database PostgreSQL berhasil dikonfigurasi dan tabel dibuat")
            return True
        except Exception as e:
            print(f"❌ Error konfigurasi database: {e}")
            return False