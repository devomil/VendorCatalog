#!/usr/bin/env python3
"""
Simple PostgreSQL Connection Test
"""

import sys
import psycopg2

# Use the credentials directly
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"  # Connect to default database first
DB_USER = "postgres"
DB_PASSWORD = "as4001"  # Your provided password

def test_admin_connection():
    """Test connection with admin user"""
    try:
        print(f"Testing connection to PostgreSQL as admin user '{DB_USER}'...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
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

def create_database():
    """Create vendor_catalog database and user"""
    if not test_admin_connection():
        return False
    
    try:
        # Connect to PostgreSQL with admin user
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database vendor_catalog
        print("Creating vendor_catalog database...")
        try:
            cursor.execute("CREATE DATABASE vendor_catalog")
            print("Database created successfully!")
        except psycopg2.errors.DuplicateDatabase:
            print("Database vendor_catalog already exists.")
        
        # Create user vendor_user
        print("Creating vendor_user...")
        try:
            cursor.execute("CREATE USER vendor_user WITH PASSWORD 'vendor_pass'")
            print("User created successfully!")
        except psycopg2.errors.DuplicateObject:
            print("User vendor_user already exists.")
            # Update password
            cursor.execute("ALTER USER vendor_user WITH PASSWORD 'vendor_pass'")
            print("Updated password for vendor_user.")
        
        # Grant privileges
        print("Granting privileges...")
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE vendor_catalog TO vendor_user")
        
        cursor.close()
        conn.close()
        
        # Connect to vendor_catalog database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="vendor_catalog"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Grant schema privileges
        cursor.execute("GRANT ALL ON SCHEMA public TO vendor_user")
        cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vendor_user")
        
        cursor.close()
        conn.close()
        
        print("Database setup completed successfully!")
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

def test_vendor_user_connection():
    """Test connection with vendor_user"""
    try:
        print(f"Testing connection to PostgreSQL as vendor_user...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user="vendor_user",
            password="vendor_pass",
            database="vendor_catalog"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"Connected successfully as vendor_user! PostgreSQL version: {version}")
        
        # Create a test table
        print("Creating test table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        )
        ''')
        print("Test table created.")
        
        # Insert test data
        cursor.execute("INSERT INTO test_table (name) VALUES ('Test Name') RETURNING id")
        row_id = cursor.fetchone()[0]
        print(f"Inserted test row with ID: {row_id}")
        
        # Query the data
        cursor.execute("SELECT * FROM test_table")
        rows = cursor.fetchall()
        print(f"Query results: {rows}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error testing vendor_user connection: {e}")
        return False

def main():
    """Main function"""
    print("Simple PostgreSQL Connection Test")
    print("================================\n")
    
    # Test admin connection
    if not test_admin_connection():
        print("Failed to connect as admin. Please check PostgreSQL installation and credentials.")
        return
    
    # Create database and user
    if not create_database():
        print("Failed to set up database. Please check error messages.")
        return
    
    # Test vendor_user connection
    if not test_vendor_user_connection():
        print("Failed to connect as vendor_user. Please check error messages.")
        return
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main() 