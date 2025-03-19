#!/usr/bin/env python3
"""
PostgreSQL Integration Test

This script tests the connection to PostgreSQL and verifies the vendor functionality
by creating, updating, and retrieving vendor records.
"""

import os
import sys
from config.settings import initialize_settings, set_setting, get_setting
from controllers.vendor_controller import VendorController
from models.vendor import Vendor

def setup_database():
    """Setup the PostgreSQL database configuration"""
    # Ensure we're using PostgreSQL
    set_setting('database.type', 'postgresql')
    
    # Set your PostgreSQL credentials here
    set_setting('database.host', 'localhost')
    set_setting('database.port', 5432)
    set_setting('database.name', 'vendor_catalog')
    set_setting('database.user', 'postgres')
    
    # For security, we'll prompt for the password if needed
    password = get_setting('database.password')
    if not password:
        from getpass import getpass
        password = getpass("Enter PostgreSQL password: ")
        set_setting('database.password', password)
    
    print(f"Database configuration:")
    print(f"Type: {get_setting('database.type')}")
    print(f"Host: {get_setting('database.host')}")
    print(f"Port: {get_setting('database.port')}")
    print(f"Name: {get_setting('database.name')}")
    print(f"User: {get_setting('database.user')}")

def test_database_connection():
    """Test the database connection"""
    try:
        # Get a connection from our base model
        conn = Vendor.get_connection()
        print("Successfully connected to PostgreSQL database!")
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return False

def test_vendor_operations():
    """Test vendor CRUD operations"""
    print("\n--- Testing Vendor Operations ---")
    
    # Initialize database tables
    print("Initializing database tables...")
    VendorController.initialize_database()
    
    # Test creating a vendor
    print("\nCreating test vendors...")
    vendor1_id = VendorController.create_vendor(
        name="Acme Corporation",
        description="A global manufacturer of everything",
        contact_info="contact@acme.com"
    )
    print(f"Created vendor with ID: {vendor1_id}")
    
    vendor2_id = VendorController.create_vendor(
        name="Tech Solutions Inc",
        description="Technology products and services",
        contact_info="info@techsolutions.com"
    )
    print(f"Created vendor with ID: {vendor2_id}")
    
    # Test retrieving vendors
    print("\nRetrieving vendors...")
    vendor1 = VendorController.get_vendor(vendor1_id)
    vendor2 = VendorController.get_vendor(vendor2_id)
    
    print(f"Vendor 1: {vendor1}")
    print(f"Vendor 2: {vendor2}")
    
    # Test updating a vendor
    print("\nUpdating vendor...")
    success = VendorController.update_vendor(
        vendor_id=vendor1_id,
        name="Acme Corp",
        description="A global manufacturer of innovative products",
        contact_info="sales@acme.com"
    )
    print(f"Update successful: {success}")
    
    # Verify the update
    updated_vendor = VendorController.get_vendor(vendor1_id)
    print(f"Updated vendor: {updated_vendor}")
    
    # Test searching vendors
    print("\nSearching for vendors with 'Tech'...")
    search_results = VendorController.search_vendors("Tech")
    print(f"Search results: {search_results}")
    
    # Test getting all vendors
    print("\nGetting all vendors...")
    all_vendors = VendorController.get_all_vendors()
    print(f"All vendors count: {len(all_vendors)}")
    for vendor in all_vendors:
        print(f"- {vendor}")
    
    # Test deleting a vendor
    print("\nDeleting vendor...")
    deleted = VendorController.delete_vendor(vendor2_id)
    print(f"Deletion successful: {deleted}")
    
    # Verify deletion
    all_vendors_after_delete = VendorController.get_all_vendors()
    print(f"Vendors after deletion: {len(all_vendors_after_delete)}")
    for vendor in all_vendors_after_delete:
        print(f"- {vendor}")

def main():
    """Main function to run the integration test"""
    print("Starting PostgreSQL integration test...\n")
    
    # Initialize settings
    initialize_settings()
    
    # Setup database configuration
    setup_database()
    
    # Test connection
    if not test_database_connection():
        print("Failed to connect to database. Exiting.")
        return
    
    # Test vendor operations
    test_vendor_operations()
    
    print("\nPostgreSQL integration test completed!")

if __name__ == "__main__":
    main() 