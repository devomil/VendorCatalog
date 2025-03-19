#!/usr/bin/env python3
"""
PostgreSQL Database Setup

This script creates the PostgreSQL database required for the Vendor Catalog application.
"""

import sys
import psycopg2
from psycopg2 import sql
from getpass import getpass

def create_database():
    """Create the PostgreSQL database"""
    db_name = "vendor_catalog"
    username = "postgres"
    password = getpass("Enter PostgreSQL password for user 'postgres': ")
    host = "localhost"
    port = "5432"
    
    # Connect to PostgreSQL server
    try:
        print(f"Connecting to PostgreSQL server on {host}:{port}...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            # Connect to 'postgres' database to create our new database
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{db_name}'...")
            # Create the database
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
        
        print("\nDatabase setup complete!")
        return True
    
    except Exception as e:
        print(f"Error setting up PostgreSQL database: {e}")
        return False

def main():
    """Main function"""
    print("PostgreSQL Database Setup")
    print("========================\n")
    
    if create_database():
        print("\nNext steps:")
        print("1. Run test_postgres.py to test the PostgreSQL integration")
        print("2. Launch the app with PostgreSQL using 'python app.py'")
    else:
        print("\nDatabase setup failed. Please check your PostgreSQL installation and credentials.")

if __name__ == "__main__":
    main() 