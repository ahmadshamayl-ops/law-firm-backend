"""Database initialization script - creates tables in PostgreSQL"""

import os
from dotenv import load_dotenv
from app.database import engine, Base, DATABASE_URL
from app.models.database_models import User

load_dotenv()

def init_db():
    """Create all tables in the database"""
    print("=" * 50)
    print("Database Initialization")
    print("=" * 50)
    
    # Display connection info (hide password)
    db_name = os.getenv("DB_NAME", "law_firm")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "postgres")
    
    print(f"Connecting to: {db_user}@{db_host}:{db_port}/{db_name}")
    print(f"Connection string: {DATABASE_URL.split('@')[0]}@***")
    print()
    
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print(f"   - Table 'users' created in database '{db_name}'")
        print()
        print("You can now start the application with:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print()
        print("Please check:")
        print("  1. PostgreSQL is running")
        print("  2. Database exists in PostgreSQL")
        print("  3. Environment variables in .env file are correct")
        print("  4. User has permission to create tables")
        raise

if __name__ == "__main__":
    init_db()

