#!/usr/bin/env python3
"""
Database Connection Test Script
This script helps diagnose database connection issues
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def test_database_connection():
    """Test the database connection with current environment variables"""
    
    print("=== Database Connection Test ===")
    
    # Check environment variables
    database_url = os.environ.get('DATABASE_URL')
    flask_env = os.environ.get('FLASK_ENV', 'ProductionConfig')
    
    print(f"FLASK_ENV: {flask_env}")
    print(f"DATABASE_URL present: {'Yes' if database_url else 'No'}")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("Please set your DATABASE_URL in your Render environment variables.")
        return False
    
    # Don't print the full URL for security, just show the host
    if database_url:
        try:
            # Extract host from URL for display (without credentials)
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            print(f"Database Host: {parsed.hostname}")
            print(f"Database Port: {parsed.port}")
            print(f"Database Name: {parsed.path[1:] if parsed.path else 'Not specified'}")
        except Exception as e:
            print(f"Could not parse DATABASE_URL: {e}")
    
    # Fix postgres:// to postgresql:// if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print("✅ Fixed postgres:// to postgresql://")
    
    # Test connection
    try:
        print("\n🔄 Testing database connection...")
        
        # Create engine with SSL and connection options
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                'sslmode': 'require',
                'connect_timeout': 30
            }
        )
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version}")
            return True
            
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        
        # Provide specific troubleshooting advice
        error_str = str(e)
        if "SSL connection has been closed unexpectedly" in error_str:
            print("\n🔧 SSL Connection Issue Detected:")
            print("- This usually means the database server is overloaded or restarting")
            print("- Try again in a few minutes")
            print("- Check your Render dashboard for database status")
            
        elif "connection to server" in error_str and "failed" in error_str:
            print("\n🔧 Connection Issue Detected:")
            print("- Check if your database is running in Render dashboard")
            print("- Verify your DATABASE_URL is correct")
            print("- Ensure your database isn't paused/sleeping")
            
        elif "authentication failed" in error_str:
            print("\n🔧 Authentication Issue Detected:")
            print("- Check your database username and password")
            print("- Verify your DATABASE_URL has correct credentials")
            
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    success = test_database_connection()
    
    if success:
        print("\n✅ Database connection test passed!")
        print("Your database should work with the Flask app.")
    else:
        print("\n❌ Database connection test failed!")
        print("Please fix the issues above before deploying.")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
