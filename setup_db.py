"""Database setup script"""
import os
from app.config.database import engine, Base
from app.models.user import User
from app.models.project import Project
from app.models.activity import Activity

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def drop_database():
    """Drop all database tables"""
    print("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped successfully!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        confirm = input("This will delete all data. Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            drop_database()
    else:
        init_database()