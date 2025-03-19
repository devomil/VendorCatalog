#!/usr/bin/env python3
"""
PostgreSQL Vendor Test

A simple script to test vendor creation, storage, and retrieval in PostgreSQL.
"""

import sys
import psycopg2
from psycopg2 import sql

# Hardcoded credentials
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "vendor_catalog"
DB_USER = "postgres"  # Admin user for initial setup
DB_PASSWORD = "as4001"
VENDOR_USER = "vendor_user"
VENDOR_PASSWORD = "vendor_pass"

def setup_database():
    """Set up the database and user"""
    try:
        print("Setting up PostgreSQL database...")
        
        # Connect to default database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database if not exists
        try:
            cursor.execute("CREATE DATABASE vendor_catalog")
            print("Database created.")
        except psycopg2.errors.DuplicateDatabase:
            print("Database already exists.")
        
        # Create user if not exists
        try:
            cursor.execute(f"CREATE USER {VENDOR_USER} WITH PASSWORD '{VENDOR_PASSWORD}'")
            print("User created.")
        except psycopg2.errors.DuplicateObject:
            print("User already exists.")
            cursor.execute(f"ALTER USER {VENDOR_USER} WITH PASSWORD '{VENDOR_PASSWORD}'")
        
        # Grant privileges
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {VENDOR_USER}")
        
        cursor.close()
        conn.close()
        
        # Connect to vendor_catalog database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Grant schema privileges
        cursor.execute(f"GRANT ALL ON SCHEMA public TO {VENDOR_USER}")
        cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {VENDOR_USER}")
        
        cursor.close()
        conn.close()
        
        print("Database setup completed.")
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

class VendorTest:
    """Test class for vendor operations"""
    
    def __init__(self):
        """Initialize the test class"""
        self.conn = None
        self.cursor = None
    
    def connect_to_database(self):
        """Connect to the database"""
        try:
            print(f"Connecting to PostgreSQL database at {DB_HOST}:{DB_PORT}...")
            
            # Connect to PostgreSQL
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=VENDOR_USER,
                password=VENDOR_PASSWORD,
                database=DB_NAME
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            
            print("Connected successfully!")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def create_vendor_table(self):
        """Create the vendors table if it doesn't exist"""
        try:
            print("Creating vendors table...")
            
            # Create table with PostgreSQL syntax
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendors (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                contact_info TEXT,
                status TEXT DEFAULT 'active'
            )
            ''')
            
            print("Vendors table created successfully!")
            return True
        except Exception as e:
            print(f"Error creating vendors table: {e}")
            return False
    
    def test_vendor_operations(self):
        """Test vendor CRUD operations"""
        try:
            print("\n--- Testing Vendor Operations ---")
            
            # Test creating a vendor
            print("\nCreating test vendors...")
            
            # Insert first vendor
            self.cursor.execute('''
            INSERT INTO vendors (name, description, contact_info, status)
            VALUES (%s, %s, %s, %s) RETURNING id
            ''', ("Acme Corporation", "A global manufacturer of everything", "contact@acme.com", "active"))
            vendor1_id = self.cursor.fetchone()[0]
            print(f"Created vendor with ID: {vendor1_id}")
            
            # Insert second vendor
            self.cursor.execute('''
            INSERT INTO vendors (name, description, contact_info, status)
            VALUES (%s, %s, %s, %s) RETURNING id
            ''', ("Tech Solutions Inc", "Technology products and services", "info@techsolutions.com", "active"))
            vendor2_id = self.cursor.fetchone()[0]
            print(f"Created vendor with ID: {vendor2_id}")
            
            # Test retrieving vendors
            print("\nRetrieving vendors...")
            self.cursor.execute("SELECT * FROM vendors WHERE id = %s", (vendor1_id,))
            vendor1 = self.cursor.fetchone()
            
            self.cursor.execute("SELECT * FROM vendors WHERE id = %s", (vendor2_id,))
            vendor2 = self.cursor.fetchone()
            
            print(f"Vendor 1: {vendor1}")
            print(f"Vendor 2: {vendor2}")
            
            # Test updating a vendor
            print("\nUpdating vendor...")
            self.cursor.execute('''
            UPDATE vendors
            SET name = %s, description = %s, contact_info = %s
            WHERE id = %s
            ''', ("Acme Corp", "A global manufacturer of innovative products", "sales@acme.com", vendor1_id))
            
            # Verify the update
            self.cursor.execute("SELECT * FROM vendors WHERE id = %s", (vendor1_id,))
            updated_vendor = self.cursor.fetchone()
            print(f"Updated vendor: {updated_vendor}")
            
            # Test searching vendors
            print("\nSearching for vendors with 'Tech'...")
            self.cursor.execute("SELECT * FROM vendors WHERE name LIKE %s", ("%Tech%",))
            search_results = self.cursor.fetchall()
            print(f"Search results: {search_results}")
            
            # Test getting all vendors
            print("\nGetting all vendors...")
            self.cursor.execute("SELECT * FROM vendors")
            all_vendors = self.cursor.fetchall()
            print(f"All vendors count: {len(all_vendors)}")
            for vendor in all_vendors:
                print(f"- {vendor}")
            
            # Test deleting a vendor
            print("\nDeleting vendor...")
            self.cursor.execute("DELETE FROM vendors WHERE id = %s", (vendor2_id,))
            
            # Verify deletion
            self.cursor.execute("SELECT * FROM vendors")
            all_vendors_after_delete = self.cursor.fetchall()
            print(f"Vendors after deletion: {len(all_vendors_after_delete)}")
            for vendor in all_vendors_after_delete:
                print(f"- {vendor}")
            
            print("\nVendor operations test completed successfully!")
            return True
        except Exception as e:
            print(f"Error testing vendor operations: {e}")
            return False
    
    def cleanup(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

def main():
    """Main function"""
    print("PostgreSQL Vendor Test")
    print("=====================\n")
    
    # First, setup the database
    if not setup_database():
        print("Database setup failed. Exiting.")
        return
    
    test = VendorTest()
    
    try:
        # Connect to database
        if not test.connect_to_database():
            print("Failed to connect to database. Exiting.")
            return
        
        # Create vendor table
        if not test.create_vendor_table():
            print("Failed to create vendor table. Exiting.")
            return
        
        # Test vendor operations
        test.test_vendor_operations()
    finally:
        # Clean up
        test.cleanup()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 