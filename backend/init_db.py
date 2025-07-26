"""
Database initialization script for AI Companion app
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import Database

async def init_database():
    """Initialize the database with tables and default data"""
    print("Initializing AI Companion database...")
    
    try:
        await Database.initialize()
        print("✅ Database initialized successfully!")
        print("✅ Default AI agents created")
        print("\nDefault agents available:")
        print("- Aria (caring personality)")
        print("- Maya (playful personality)")  
        print("- Priya (romantic personality)")
        print("- Shreya (supportive personality)")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(init_database())
    if success:
        print("\n🚀 Database ready! You can now start the backend server.")
        print("Run: uvicorn main:app --reload")
    else:
        print("\n❌ Database initialization failed.")
        sys.exit(1)
