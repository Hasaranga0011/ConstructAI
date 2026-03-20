"""Database initialization script"""
from app.config.database import engine, Base
from app.models.user import User
from app.models.project import Project
from app.models.activity import Activity

def init_database():
    """Initialize database tables"""
    print("=" * 50)
    print("Database Tables Initialization")
    print("=" * 50)
    
    try:
        # Drop existing tables (optional - comment if you want to keep data)
        print("1. Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("   ✓ Existing tables dropped successfully")
        
        # Create all tables
        print("2. Creating new tables...")
        Base.metadata.create_all(bind=engine)
        print("   ✓ New tables created successfully")
        
        # Verify tables
        print("3. Verifying tables...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("\n✅ Database initialization completed!")
        print(f"\nCreated tables: {', '.join(tables)}")
        
        # Show table details
        print("\n📊 Table Details:")
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"\n   {table}:")
            for col in columns:
                print(f"      - {col['name']} ({col['type']})")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL is running")
        print("2. DATABASE_URL in .env is correct")
        print("3. Database credentials are valid")

if __name__ == "__main__":
    init_database()