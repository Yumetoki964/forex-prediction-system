#!/usr/bin/env python3
"""Renderデプロイのデバッグ用スクリプト"""

import sys
import os

print("Python version:", sys.version)
print("Python path:", sys.executable)
print("Current directory:", os.getcwd())
print("PYTHONPATH:", os.environ.get('PYTHONPATH'))

try:
    print("\n=== Testing imports ===")
    
    print("1. Importing os...")
    import os
    
    print("2. Setting environment variables...")
    os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['JWT_SECRET_KEY'] = 'test-jwt-key'
    
    print("3. Importing FastAPI...")
    from fastapi import FastAPI
    
    print("4. Importing app.database...")
    from app.database import Base, engine
    
    print("5. Importing app.main...")
    from app.main import app
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Error during import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)