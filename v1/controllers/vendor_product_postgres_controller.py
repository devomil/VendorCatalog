"""
PostgreSQL-specific implementation of the Vendor Product Controller
"""

import sys
import os

# Add the parent directory to sys.path to allow importing from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.vendor_product_postgres import VendorProductPostgres

class VendorProductPostgresController:
    """Controller for vendor product-related operations using PostgreSQL"""
    
    @staticmethod
    def initialize_database():
        """Initialize the database tables"""
        VendorProductPostgres.create_table()
    
    @staticmethod
    def create_vendor_product(vendor_id, master_product_id=None, vendor_sku=None, 
                              vendor_price=None, list_price=None, map_price=None, mrp_price=None,
                              quantity=0, quantity_nj=0, quantity_fl=0, 
                              eta=None, eta_nj=None, eta_fl=None,
                              shipping_weight=None, shipping_dimensions=None, 
                              props=None):
        """Create a new vendor product"""
        vendor_product = VendorProductPostgres(
            vendor_id=vendor_id,
            master_product_id=master_product_id,
            vendor_sku=vendor_sku,
            vendor_price=vendor_price,
            list_price=list_price,
            map_price=map_price,
            mrp_price=mrp_price,
            quantity=quantity,
            quantity_nj=quantity_nj,
            quantity_fl=quantity_fl,
            eta=eta,
            eta_nj=eta_nj,
            eta_fl=eta_fl,
            shipping_weight=shipping_weight,
            shipping_dimensions=shipping_dimensions,
            props=props
        )
        vendor_product_id = vendor_product.save()
        return vendor_product_id
    
    @staticmethod
    def update_vendor_product(vendor_product_id, vendor_id=None, master_product_id=None, 
                              vendor_sku=None, vendor_price=None, list_price=None, 
                              map_price=None, mrp_price=None, quantity=None, 
                              quantity_nj=None, quantity_fl=None, eta=None, 
                              eta_nj=None, eta_fl=None, shipping_weight=None, 
                              shipping_dimensions=None, props=None, status=None):
        """Update an existing vendor product"""
        # Get current vendor product data
        vendor_product_data = VendorProductPostgres.find_by_id(vendor_product_id)
        if not vendor_product_data:
            return False
            
        # Create vendor product object with current data
        vendor_product = VendorProductPostgres(
            id=vendor_product_id,
            vendor_id=vendor_product_data[1] if vendor_id is None else vendor_id,
            master_product_id=vendor_product_data[2] if master_product_id is None else master_product_id,
            vendor_sku=vendor_product_data[3] if vendor_sku is None else vendor_sku,
            vendor_price=vendor_product_data[4] if vendor_price is None else vendor_price,
            list_price=vendor_product_data[5] if list_price is None else list_price,
            map_price=vendor_product_data[6] if map_price is None else map_price,
            mrp_price=vendor_product_data[7] if mrp_price is None else mrp_price,
            quantity=vendor_product_data[8] if quantity is None else quantity,
            quantity_nj=vendor_product_data[9] if quantity_nj is None else quantity_nj,
            quantity_fl=vendor_product_data[10] if quantity_fl is None else quantity_fl,
            eta=vendor_product_data[11] if eta is None else eta,
            eta_nj=vendor_product_data[12] if eta_nj is None else eta_nj,
            eta_fl=vendor_product_data[13] if eta_fl is None else eta_fl,
            shipping_weight=vendor_product_data[14] if shipping_weight is None else shipping_weight,
            shipping_dimensions=vendor_product_data[15] if shipping_dimensions is None else shipping_dimensions,
            props=vendor_product_data[16] if props is None else props,
            status=vendor_product_data[17] if status is None else status
        )
        
        vendor_product.update()
        return True
    
    @staticmethod
    def delete_vendor_product(vendor_product_id):
        """Delete a vendor product"""
        vendor_product = VendorProductPostgres(id=vendor_product_id)
        vendor_product.delete()
        return True
    
    @staticmethod
    def get_vendor_product(vendor_product_id):
        """Get a vendor product by ID"""
        return VendorProductPostgres.find_by_id(vendor_product_id)
    
    @staticmethod
    def get_vendor_product_by_sku(vendor_id, vendor_sku):
        """Get a vendor product by vendor ID and SKU"""
        return VendorProductPostgres.find_by_vendor_and_sku(vendor_id, vendor_sku)
    
    @staticmethod
    def get_vendor_products(vendor_id):
        """Get all products for a vendor"""
        return VendorProductPostgres.find_by_vendor(vendor_id)
    
    @staticmethod
    def get_master_product_vendors(master_product_id):
        """Get all vendor products for a master product"""
        return VendorProductPostgres.find_by_master_product(master_product_id)
    
    @staticmethod
    def get_all_vendor_products():
        """Get all vendor products"""
        return VendorProductPostgres.find_all()
    
    @staticmethod
    def bulk_import_vendor_products(vendor_id, products_data, batch_size=1000):
        """Bulk import vendor products"""
        return VendorProductPostgres.bulk_insert(vendor_id, products_data, batch_size)
    
    @staticmethod
    def test_controller():
        """Test the controller functionality"""
        try:
            print("Testing VendorProductPostgresController...")
            
            # Initialize database
            VendorProductPostgresController.initialize_database()
            print("Database initialized.")
            
            # First, we need to create a vendor to use
            from models.vendor_postgres import VendorPostgres
            VendorPostgres.create_table()
            
            vendor = VendorPostgres(
                name="Controller Test Vendor",
                description="A vendor for testing the vendor product controller",
                contact_info="test@vpcontroller.com"
            )
            vendor_id = vendor.save()
            print(f"Created test vendor with ID: {vendor_id}")
            
            # Create properties object
            props = {
                "brand": "Controller Brand",
                "category": "Controller Category",
                "tags": ["controller", "test"]
            }
            
            # Create vendor product
            vendor_product_id = VendorProductPostgresController.create_vendor_product(
                vendor_id=vendor_id,
                vendor_sku="CTOR001",
                vendor_price=39.99,
                list_price=49.99,
                map_price=44.99,
                quantity=200,
                props=props
            )
            print(f"Created vendor product with ID: {vendor_product_id}")
            
            # Get vendor product
            vendor_product = VendorProductPostgresController.get_vendor_product(vendor_product_id)
            print(f"Retrieved vendor product: {vendor_product}")
            
            # Update vendor product
            updated_props = {
                "brand": "Updated Brand",
                "category": "Controller Category",
                "tags": ["controller", "test", "updated"],
                "featured": True
            }
            
            VendorProductPostgresController.update_vendor_product(
                vendor_product_id,
                vendor_price=41.99,
                list_price=51.99,
                quantity=220,
                props=updated_props
            )
            print("Vendor product updated.")
            
            # Get updated vendor product
            updated_vendor_product = VendorProductPostgresController.get_vendor_product(vendor_product_id)
            print(f"Updated vendor product: {updated_vendor_product}")
            
            # Get by vendor and SKU
            sku_vendor_product = VendorProductPostgresController.get_vendor_product_by_sku(vendor_id, "CTOR001")
            print(f"Vendor product with SKU CTOR001: {sku_vendor_product[3] if sku_vendor_product else None}")
            
            # Get all products for vendor
            vendor_products = VendorProductPostgresController.get_vendor_products(vendor_id)
            print(f"Products for vendor {vendor_id}: {len(vendor_products)}")
            
            # Test bulk import
            bulk_products = [
                {
                    "sku": "CTORBULK001",
                    "price": 9.99,
                    "list": 12.99,
                    "map": 11.99,
                    "qty": 50,
                    "brand": "Bulk Controller Brand 1"
                },
                {
                    "sku": "CTORBULK002",
                    "price": 14.99,
                    "list": 19.99,
                    "qty": 30,
                    "brand": "Bulk Controller Brand 2"
                }
            ]
            
            bulk_count = VendorProductPostgresController.bulk_import_vendor_products(vendor_id, bulk_products)
            print(f"Bulk imported {bulk_count} vendor products")
            
            # Verify bulk import
            vendor_products_after_bulk = VendorProductPostgresController.get_vendor_products(vendor_id)
            print(f"Vendor products after bulk import: {len(vendor_products_after_bulk)}")
            
            # Get all vendor products
            all_vendor_products = VendorProductPostgresController.get_all_vendor_products()
            print(f"All vendor products count: {len(all_vendor_products)}")
            
            # Delete vendor product
            VendorProductPostgresController.delete_vendor_product(vendor_product_id)
            print(f"Deleted vendor product ID: {vendor_product_id}")
            
            # Verify deletion
            vendor_products_after_delete = VendorProductPostgresController.get_vendor_products(vendor_id)
            print(f"Vendor products after deletion: {len(vendor_products_after_delete)}")
            
            # Clean up - delete vendor
            vendor = VendorPostgres(id=vendor_id)
            vendor.delete()
            print(f"Deleted test vendor ID: {vendor_id}")
            
            print("VendorProductPostgresController test completed successfully!")
            return True
        except Exception as e:
            print(f"Error testing VendorProductPostgresController: {e}")
            import traceback
            traceback.print_exc()
            return False

# Run the test if this file is executed directly
if __name__ == "__main__":
    VendorProductPostgresController.test_controller() 