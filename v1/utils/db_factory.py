"""
Database Factory Module

This module provides a factory for database-specific models and controllers.
It allows the application to switch between SQLite and PostgreSQL backends.
"""

import sys
import os

# Add the parent directory to sys.path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config.settings import get_setting, initialize_settings

# Import SQLite models and controllers
from models.vendor import Vendor
from controllers.vendor_controller import VendorController
from models.product import Product
from controllers.product_controller import ProductController
from models.master_product import MasterProduct
from controllers.master_product_controller import MasterProductController

# Import PostgreSQL-specific classes
try:
    from models.vendor_postgres import VendorPostgres
    from controllers.vendor_postgres_controller import VendorPostgresController
    from models.product_postgres import ProductPostgres
    from controllers.product_postgres_controller import ProductPostgresController
    from models.master_product_postgres import MasterProductPostgres
    from controllers.master_product_postgres_controller import MasterProductPostgresController
    from models.vendor_product_postgres import VendorProductPostgres
    from controllers.vendor_product_postgres_controller import VendorProductPostgresController
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

class DatabaseFactory:
    """Factory for database-specific classes"""
    
    @staticmethod
    def get_db_type():
        """Get the configured database type"""
        # Initialize settings if needed
        initialize_settings()
        
        # Get database type from settings
        db_type = get_setting('database.type', 'sqlite')
        return db_type
    
    @staticmethod
    def get_vendor_model():
        """Get the appropriate vendor model based on configuration"""
        db_type = DatabaseFactory.get_db_type()
        
        if db_type == 'postgresql' and POSTGRES_AVAILABLE:
            print("Using PostgreSQL backend for Vendor model")
            return VendorPostgres
        else:
            print("Using SQLite backend for Vendor model")
            return Vendor
    
    @staticmethod
    def get_vendor_controller():
        """Get the appropriate vendor controller based on configuration"""
        db_type = DatabaseFactory.get_db_type()
        
        if db_type == 'postgresql' and POSTGRES_AVAILABLE:
            print("Using PostgreSQL backend for Vendor controller")
            return VendorPostgresController
        else:
            print("Using SQLite backend for Vendor controller")
            return VendorController
    
    @staticmethod
    def get_product_model():
        """Get the appropriate product model based on configuration"""
        db_type = DatabaseFactory.get_db_type()
        
        if db_type == 'postgresql' and POSTGRES_AVAILABLE:
            print("Using PostgreSQL backend for Product model")
            return ProductPostgres
        else:
            print("Using SQLite backend for Product model")
            return Product
    
    @staticmethod
    def get_product_controller():
        """Get the appropriate product controller based on configuration"""
        db_type = DatabaseFactory.get_db_type()
        
        if db_type == 'postgresql' and POSTGRES_AVAILABLE:
            print("Using PostgreSQL backend for Product controller")
            return ProductPostgresController
        else:
            print("Using SQLite backend for Product controller")
            return ProductController
    
    @staticmethod
    def get_master_product_model():
        """Get the appropriate master product model based on configuration"""
        db_type = DatabaseFactory.get_db_type()
        
        if db_type == 'postgresql' and POSTGRES_AVAILABLE:
            print("Using PostgreSQL backend for MasterProduct model")
            return MasterProductPostgres
        else:
            print("Using SQLite backend for MasterProduct model")
            return MasterProduct
    
    @staticmethod
    def get_master_product_controller():
        """Get the appropriate master product controller based on configuration"""
        db_type = DatabaseFactory.get_db_type()
        
        if db_type == 'postgresql' and POSTGRES_AVAILABLE:
            print("Using PostgreSQL backend for MasterProduct controller")
            return MasterProductPostgresController
        else:
            print("Using SQLite backend for MasterProduct controller")
            return MasterProductController
    
    @staticmethod
    def get_vendor_product_model():
        """Get the appropriate vendor product model based on configuration"""
        db_type = DatabaseFactory.get_db_type()
        
        if db_type == 'postgresql' and POSTGRES_AVAILABLE:
            print("Using PostgreSQL backend for VendorProduct model")
            return VendorProductPostgres
        else:
            print("Using SQLite backend for the base Product model with join tables")
            return Product  # SQLite uses the base Product model with join tables
    
    @staticmethod
    def get_vendor_product_controller():
        """Get the appropriate vendor product controller based on configuration"""
        db_type = DatabaseFactory.get_db_type()
        
        if db_type == 'postgresql' and POSTGRES_AVAILABLE:
            print("Using PostgreSQL backend for VendorProduct controller")
            return VendorProductPostgresController
        else:
            print("Using SQLite backend for Product controller with vendor-product methods")
            return ProductController  # SQLite uses the base Product controller with vendor-product methods
    
    @staticmethod
    def initialize_database():
        """Initialize all database tables using the appropriate controllers"""
        db_type = DatabaseFactory.get_db_type()
        
        print(f"Initializing database tables with {db_type} backend...")
        
        # Get appropriate controllers
        vendor_controller = DatabaseFactory.get_vendor_controller()
        product_controller = DatabaseFactory.get_product_controller()
        master_product_controller = DatabaseFactory.get_master_product_controller()
        
        # For PostgreSQL we also initialize the vendor_product controller
        if db_type == 'postgresql' and POSTGRES_AVAILABLE:
            vendor_product_controller = DatabaseFactory.get_vendor_product_controller()
            vendor_product_controller.initialize_database()
        
        # Initialize tables
        vendor_controller.initialize_database()
        product_controller.initialize_database()
        master_product_controller.initialize_database()
        
        print("Database initialization complete")
    
    @staticmethod
    def test_factory():
        """Test the database factory"""
        try:
            import time
            import random
            
            print("Testing DatabaseFactory...")
            
            # Generate unique identifiers
            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            
            # Print the detected database type
            db_type = DatabaseFactory.get_db_type()
            print(f"Configured database type: {db_type}")
            
            # Get and test models
            vendor_model = DatabaseFactory.get_vendor_model()
            print(f"Selected vendor model: {vendor_model.__name__}")
            
            product_model = DatabaseFactory.get_product_model()
            print(f"Selected product model: {product_model.__name__}")
            
            master_product_model = DatabaseFactory.get_master_product_model()
            print(f"Selected master product model: {master_product_model.__name__}")
            
            vendor_product_model = DatabaseFactory.get_vendor_product_model()
            print(f"Selected vendor product model: {vendor_product_model.__name__}")
            
            # Get and test controllers
            vendor_controller = DatabaseFactory.get_vendor_controller()
            print(f"Selected vendor controller: {vendor_controller.__name__}")
            
            product_controller = DatabaseFactory.get_product_controller()
            print(f"Selected product controller: {product_controller.__name__}")
            
            master_product_controller = DatabaseFactory.get_master_product_controller()
            print(f"Selected master product controller: {master_product_controller.__name__}")
            
            vendor_product_controller = DatabaseFactory.get_vendor_product_controller()
            print(f"Selected vendor product controller: {vendor_product_controller.__name__}")
            
            # Initialize the database
            DatabaseFactory.initialize_database()
            
            # Test creating a vendor
            vendor_controller = DatabaseFactory.get_vendor_controller()
            vendor_name = f"Factory Test Vendor {timestamp}_{random_suffix}"
            vendor_id = vendor_controller.create_vendor(
                name=vendor_name,
                description="A vendor for testing the database factory",
                contact_info=f"factory{timestamp}@test.com"
            )
            print(f"Created vendor with ID: {vendor_id}")
            
            # Test creating a product
            product_controller = DatabaseFactory.get_product_controller()
            product_sku = f"FTP{timestamp}_{random_suffix}"
            product_id = product_controller.create_product(
                name="Factory Test Product",
                description="A product for testing the database factory",
                sku=product_sku,
                price=29.99
            )
            print(f"Created product with ID: {product_id}")
            
            # Test creating a master product
            master_product_controller = DatabaseFactory.get_master_product_controller()
            master_product_sku = f"FTMP{timestamp}_{random_suffix}"
            master_product_upc = f"123456{timestamp}{random_suffix}"
            master_product_id = master_product_controller.create_product(
                name="Factory Test Master Product",
                description="A master product for testing the database factory",
                sku=master_product_sku,
                upc=master_product_upc,
                manufacturer="Test Factory",
                manufacturer_part_number=f"TF-{timestamp}"
            )
            print(f"Created master product with ID: {master_product_id}")
            
            # Test creating a vendor product if we're using PostgreSQL
            if db_type == 'postgresql' and POSTGRES_AVAILABLE:
                vendor_product_controller = DatabaseFactory.get_vendor_product_controller()
                vendor_product_sku = f"FTVP{timestamp}_{random_suffix}"
                vendor_product_id = vendor_product_controller.create_vendor_product(
                    vendor_id=vendor_id,
                    vendor_sku=vendor_product_sku,
                    vendor_price=25.99,
                    list_price=29.99,
                    quantity=100
                )
                print(f"Created vendor product with ID: {vendor_product_id}")
                
                # Clean up vendor product
                vendor_product_controller.delete_vendor_product(vendor_product_id)
                print(f"Deleted vendor product with ID: {vendor_product_id}")
            
            # Clean up test data
            vendor_controller.delete_vendor(vendor_id)
            print(f"Deleted vendor with ID: {vendor_id}")
            
            product_controller.delete_product(product_id)
            print(f"Deleted product with ID: {product_id}")
            
            master_product_controller.delete_product(master_product_id)
            print(f"Deleted master product with ID: {master_product_id}")
            
            print("DatabaseFactory test completed successfully!")
            return True
        except Exception as e:
            print(f"Error testing DatabaseFactory: {e}")
            import traceback
            traceback.print_exc()
            return False

# Run the test if this file is executed directly
if __name__ == "__main__":
    DatabaseFactory.test_factory() 