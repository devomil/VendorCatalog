#!/usr/bin/env python3
"""
PostgreSQL Server Setup

This script helps set up a dedicated PostgreSQL server for the VendorCatalog project.
It creates a new database, user, and necessary privileges.
"""

import os
import sys
import subprocess
import platform
import psycopg2
from psycopg2 import sql
from getpass import getpass

# Configuration
DB_NAME = "vendor_catalog"
DB_USER = "vendor_user"
DB_PASSWORD = "vendor_pass"  # You should change this in production
DB_HOST = "localhost"
DB_PORT = "5432"
ADMIN_USER = "postgres"  # PostgreSQL admin user

def check_postgres_installation():
    """Check if PostgreSQL is installed and accessible"""
    try:
        # Try to connect to the default PostgreSQL database
        print("Checking PostgreSQL installation...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=ADMIN_USER,
            password=getpass(f"Enter password for PostgreSQL admin user '{ADMIN_USER}': "),
            database="postgres"
        )
        conn.autocommit = True
        
        # Get PostgreSQL version
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"Connected to PostgreSQL: {version}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return False

def setup_database(admin_password):
    """Set up the database, user, and privileges"""
    try:
        # Connect to PostgreSQL with admin user
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=ADMIN_USER,
            password=admin_password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if the database already exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        db_exists = cursor.fetchone()
        
        # Create database if it doesn't exist
        if not db_exists:
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Database '{DB_NAME}' created successfully")
        else:
            print(f"Database '{DB_NAME}' already exists")
        
        # Check if the user exists
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (DB_USER,))
        user_exists = cursor.fetchone()
        
        # Create user if it doesn't exist
        if not user_exists:
            print(f"Creating user '{DB_USER}'...")
            cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD {}").format(
                sql.Identifier(DB_USER), sql.Literal(DB_PASSWORD)))
            print(f"User '{DB_USER}' created successfully")
        else:
            print(f"User '{DB_USER}' already exists")
            # Update password
            cursor.execute(sql.SQL("ALTER USER {} WITH PASSWORD {}").format(
                sql.Identifier(DB_USER), sql.Literal(DB_PASSWORD)))
            print(f"Updated password for user '{DB_USER}'")
        
        # Grant privileges
        print(f"Granting privileges on database '{DB_NAME}' to user '{DB_USER}'...")
        cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
            sql.Identifier(DB_NAME), sql.Identifier(DB_USER)))
        
        # Connect to the specific database to grant table privileges
        cursor.close()
        conn.close()
        
        # Connect to the newly created database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=ADMIN_USER,
            password=admin_password,
            database=DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Grant schema privileges (will apply to future tables)
        cursor.execute(sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(sql.Identifier(DB_USER)))
        cursor.execute(sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {}").format(
            sql.Identifier(DB_USER)))
        
        cursor.close()
        conn.close()
        
        print("Database setup completed successfully!")
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

def update_config_settings():
    """Update the application's configuration settings"""
    try:
        from config.settings import set_setting, initialize_settings
        
        # Initialize settings
        initialize_settings()
        
        # Update database settings
        set_setting('database.type', 'postgresql')
        set_setting('database.host', DB_HOST)
        set_setting('database.port', int(DB_PORT))
        set_setting('database.name', DB_NAME)
        set_setting('database.user', DB_USER)
        set_setting('database.password', DB_PASSWORD)
        
        print("Application configuration updated successfully!")
        return True
    except ImportError:
        print("Could not import settings module. Make sure you're running this script from the correct directory.")
        return False
    except Exception as e:
        print(f"Error updating configuration: {e}")
        return False

def main():
    """Main function"""
    print("VendorCatalog PostgreSQL Server Setup")
    print("=====================================\n")
    
    # Check PostgreSQL installation
    if not check_postgres_installation():
        print("\nFailed to connect to PostgreSQL. Please check your installation and try again.")
        return
    
    # Get admin password
    admin_password = getpass(f"Re-enter password for PostgreSQL admin user '{ADMIN_USER}': ")
    
    # Setup database
    if not setup_database(admin_password):
        print("\nDatabase setup failed. Please check the error messages and try again.")
        return
    
    # Update application config
    if not update_config_settings():
        print("\nFailed to update application configuration.")
        return
    
    print("\nSetup completed successfully!")
    print(f"\nDatabase connection details:")
    print(f"  Host: {DB_HOST}")
    print(f"  Port: {DB_PORT}")
    print(f"  Database: {DB_NAME}")
    print(f"  User: {DB_USER}")
    print(f"  Password: {DB_PASSWORD}")
    
    print("\nNext steps:")
    print("1. You can now run the application to test the connection")
    print("2. Remember to change the password in production environments")

if __name__ == "__main__":
    main() 