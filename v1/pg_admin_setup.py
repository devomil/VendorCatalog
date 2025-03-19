#!/usr/bin/env python3
"""
PostgreSQL Admin Setup

This script sets up the vendor_catalog database and vendor_user account
using the PostgreSQL admin credentials.
"""

import psycopg2
from psycopg2 import sql

# Admin credentials
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "postgres"  # Connect to default database first
DB_USER = "postgres"
DB_PASSWORD = "as4001"  # Your provided password

# Application credentials
APP_DB_NAME = "vendor_catalog"
APP_DB_USER = "vendor_user"
APP_DB_PASSWORD = "vendor_pass"

def connect_to_postgres():
    """Connect to PostgreSQL admin database"""
    try:
        print(f"Connecting to PostgreSQL as admin user '{DB_USER}'...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.autocommit = True
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"Connected successfully! PostgreSQL version: {version}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return False

def setup_database():
    """Create application database and user"""
    try:
        # Connect to PostgreSQL admin database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create application database
        try:
            print(f"Creating database '{APP_DB_NAME}'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(APP_DB_NAME)))
            print(f"Database '{APP_DB_NAME}' created successfully")
        except psycopg2.errors.DuplicateDatabase:
            print(f"Database '{APP_DB_NAME}' already exists")
        
        # Create application user
        try:
            print(f"Creating user '{APP_DB_USER}'...")
            cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD {}").format(
                sql.Identifier(APP_DB_USER), sql.Literal(APP_DB_PASSWORD)))
            print(f"User '{APP_DB_USER}' created successfully")
        except psycopg2.errors.DuplicateObject:
            print(f"User '{APP_DB_USER}' already exists")
            # Update password
            cursor.execute(sql.SQL("ALTER USER {} WITH PASSWORD {}").format(
                sql.Identifier(APP_DB_USER), sql.Literal(APP_DB_PASSWORD)))
            print(f"Updated password for user '{APP_DB_USER}'")
        
        # Grant privileges
        print(f"Granting privileges on database '{APP_DB_NAME}' to user '{APP_DB_USER}'...")
        cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
            sql.Identifier(APP_DB_NAME), sql.Identifier(APP_DB_USER)))
        
        cursor.close()
        conn.close()
        
        # Connect to application database as admin to set schema privileges
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=APP_DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Grant schema privileges
        print("Granting schema privileges...")
        cursor.execute(sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(sql.Identifier(APP_DB_USER)))
        cursor.execute(sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {}").format(
            sql.Identifier(APP_DB_USER)))
        
        cursor.close()
        conn.close()
        
        print("\nDatabase setup completed successfully!")
        
        # Show connection string for application
        print("\nConnection information for VendorCatalog application:")
        print(f"Host: {DB_HOST}")
        print(f"Port: {DB_PORT}")
        print(f"Database: {APP_DB_NAME}")
        print(f"User: {APP_DB_USER}")
        print(f"Password: {APP_DB_PASSWORD}")
        
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("PostgreSQL Admin Setup")
    print("=====================\n")
    
    # Connect to PostgreSQL
    if not connect_to_postgres():
        print("Failed to connect to PostgreSQL. Please check your credentials.")
        return
    
    # Setup database and user
    if not setup_database():
        print("Failed to set up database and user. Please check the error messages.")
        return
    
    print("\nSetup completed successfully! You can now run the VendorCatalog application.")
    print("To test PostgreSQL integration with vendors, run:")
    print("python VendorCatalog/models/vendor_postgres.py")

if __name__ == "__main__":
    main() 