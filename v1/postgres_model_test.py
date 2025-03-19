#!/usr/bin/env python3
"""
PostgreSQL Model Integration Test

This script tests the PostgreSQL integration with all models:
- Vendor
- Product
- MasterProduct
- VendorProduct
"""

import sys
import os
import traceback

# Add the parent directory to sys.path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from config.settings import initialize_settings, set_setting
from models.vendor_postgres import VendorPostgres
from models.product_postgres import ProductPostgres
from models.master_product_postgres import MasterProductPostgres
from models.vendor_product_postgres import VendorProductPostgres
from controllers.vendor_postgres_controller import VendorPostgresController
from controllers.product_postgres_controller import ProductPostgresController
from controllers.master_product_postgres_controller import MasterProductPostgresController
from controllers.vendor_product_postgres_controller import VendorProductPostgresController
from utils.db_factory import DatabaseFactory

def setup_configuration():
    """Set up the configuration to use PostgreSQL"""
    initialize_settings()
    set_setting('database.type', 'postgresql')
    set_setting('database.host', 'localhost')
    set_setting('database.port', 5432)
    set_setting('database.name', 'vendor_catalog')
    set_setting('database.user', 'vendor_user')
    set_setting('database.password', 'vendor_pass')
    print("Configuration set up to use PostgreSQL")

def test_vendor_integration():
    """Test the Vendor PostgreSQL integration"""
    try:
        print("\n--- Testing Vendor PostgreSQL Integration ---")
        
        # Test the model directly
        success = VendorPostgres.test_postgres_integration()
        if not success:
            print("Vendor model test failed")
            return False
        
        # Test the controller
        success = VendorPostgresController.test_controller()
        if not success:
            print("Vendor controller test failed")
            return False
        
        print("Vendor PostgreSQL integration tests completed successfully")
        return True
    except Exception as e:
        print(f"Error testing vendor integration: {e}")
        traceback.print_exc()
        return False

def test_product_integration():
    """Test the Product PostgreSQL integration"""
    try:
        print("\n--- Testing Product PostgreSQL Integration ---")
        
        # Test the model directly
        success = ProductPostgres.test_postgres_integration()
        if not success:
            print("Product model test failed")
            return False
        
        # Test the controller
        success = ProductPostgresController.test_controller()
        if not success:
            print("Product controller test failed")
            return False
        
        print("Product PostgreSQL integration tests completed successfully")
        return True
    except Exception as e:
        print(f"Error testing product integration: {e}")
        traceback.print_exc()
        return False

def test_master_product_integration():
    """Test the MasterProduct PostgreSQL integration"""
    try:
        print("\n--- Testing MasterProduct PostgreSQL Integration ---")
        
        # Test the model directly
        success = MasterProductPostgres.test_postgres_integration()
        if not success:
            print("MasterProduct model test failed")
            return False
        
        # Test the controller
        success = MasterProductPostgresController.test_controller()
        if not success:
            print("MasterProduct controller test failed")
            return False
        
        print("MasterProduct PostgreSQL integration tests completed successfully")
        return True
    except Exception as e:
        print(f"Error testing master product integration: {e}")
        traceback.print_exc()
        return False

def test_vendor_product_integration():
    """Test the VendorProduct PostgreSQL integration"""
    try:
        print("\n--- Testing VendorProduct PostgreSQL Integration ---")
        
        # Test the model directly
        success = VendorProductPostgres.test_postgres_integration()
        if not success:
            print("VendorProduct model test failed")
            return False
        
        # Test the controller
        success = VendorProductPostgresController.test_controller()
        if not success:
            print("VendorProduct controller test failed")
            return False
        
        print("VendorProduct PostgreSQL integration tests completed successfully")
        return True
    except Exception as e:
        print(f"Error testing vendor product integration: {e}")
        traceback.print_exc()
        return False

def test_db_factory():
    """Test the database factory with PostgreSQL"""
    try:
        print("\n--- Testing Database Factory with PostgreSQL ---")
        
        # Ensure PostgreSQL is selected
        db_type = DatabaseFactory.get_db_type()
        if db_type != 'postgresql':
            print(f"Expected database type to be 'postgresql', got '{db_type}'")
            return False
        
        # Test the factory
        success = DatabaseFactory.test_factory()
        if not success:
            print("Database factory test failed")
            return False
        
        print("Database factory tests with PostgreSQL completed successfully")
        return True
    except Exception as e:
        print(f"Error testing database factory: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("PostgreSQL Model Integration Test")
    print("===============================\n")
    
    # Set up configuration
    setup_configuration()
    
    # Test all components
    vendor_success = test_vendor_integration()
    product_success = test_product_integration()
    master_product_success = test_master_product_integration()
    vendor_product_success = test_vendor_product_integration()
    factory_success = test_db_factory()
    
    # Print summary
    print("\n--- Test Summary ---")
    print(f"Vendor Integration: {'SUCCESS' if vendor_success else 'FAILED'}")
    print(f"Product Integration: {'SUCCESS' if product_success else 'FAILED'}")
    print(f"MasterProduct Integration: {'SUCCESS' if master_product_success else 'FAILED'}")
    print(f"VendorProduct Integration: {'SUCCESS' if vendor_product_success else 'FAILED'}")
    print(f"Database Factory: {'SUCCESS' if factory_success else 'FAILED'}")
    
    # Overall result
    overall_success = (
        vendor_success and 
        product_success and 
        master_product_success and 
        vendor_product_success and 
        factory_success
    )
    
    print(f"\nOverall Result: {'SUCCESS' if overall_success else 'FAILED'}")
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main()) 