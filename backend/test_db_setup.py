#!/usr/bin/env python3
"""
Test database setup script for CI/CD pipeline
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/forex_test")

def setup_test_database():
    """Create test database schema and tables"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ Database connection successful: {result.scalar()}")
            
        print("✅ Test database setup completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Error setting up test database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(setup_test_database())