"""
PostgreSQL-specific implementation of the Master Product Controller
"""

import sys
import os

# Add the parent directory to sys.path to allow importing from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.master_product_postgres import MasterProductPostgres

class MasterProductPostgresController:
    """Controller for master product-related operations using PostgreSQL"""
    
    @staticmethod
    def initialize_database():
        """Initialize the database tables"""
        MasterProductPostgres.create_table()
    
    @staticmethod
    def create_product(name, description=None, sku=None, upc=None, manufacturer=None, 
                       manufacturer_part_number=None, category_id=None, specs=None):
        """Create a new master product"""
        product = MasterProductPostgres(
            name=name, 
            description=description, 
            sku=sku,
            upc=upc,
            manufacturer=manufacturer,
            manufacturer_part_number=manufacturer_part_number,
            category_id=category_id,
            specs=specs
        )
        product_id = product.save()
        return product_id
    
    @staticmethod
    def update_product(product_id, name=None, description=None, sku=None, upc=None, 
                      manufacturer=None, manufacturer_part_number=None, 
                      category_id=None, specs=None, status=None):
        """Update an existing master product"""
        # Get current product data
        product_data = MasterProductPostgres.find_by_id(product_id)
        if not product_data:
            return False
            
        # Create product object with current data
        product = MasterProductPostgres(
            id=product_id,
            name=product_data[1] if name is None else name,
            description=product_data[2] if description is None else description,
            sku=product_data[3] if sku is None else sku,
            upc=product_data[4] if upc is None else upc,
            manufacturer=product_data[5] if manufacturer is None else manufacturer,
            manufacturer_part_number=product_data[6] if manufacturer_part_number is None else manufacturer_part_number,
            category_id=product_data[7] if category_id is None else category_id,
            specs=product_data[8] if specs is None else specs,
            status=product_data[9] if status is None else status
        )
        
        product.update()
        return True
    
    @staticmethod
    def delete_product(product_id):
        """Delete a master product"""
        product = MasterProductPostgres(id=product_id)
        product.delete()
        return True
    
    @staticmethod
    def get_product(product_id):
        """Get a master product by ID"""
        return MasterProductPostgres.find_by_id(product_id)
    
    @staticmethod
    def get_product_by_sku(sku):
        """Get a master product by SKU"""
        return MasterProductPostgres.find_by_sku(sku)
    
    @staticmethod
    def get_product_by_upc(upc):
        """Get a master product by UPC"""
        return MasterProductPostgres.find_by_upc(upc)
    
    @staticmethod
    def get_product_by_mpn(manufacturer, mpn):
        """Get a master product by manufacturer and part number"""
        return MasterProductPostgres.find_by_mpn(manufacturer, mpn)
    
    @staticmethod
    def search_products(search_term):
        """Search master products by name"""
        return MasterProductPostgres.find_by_name(search_term)
    
    @staticmethod
    def get_all_products():
        """Get all master products"""
        return MasterProductPostgres.find_all()
    
    @staticmethod
    def test_controller():
        """Test the controller functionality"""
        try:
            print("Testing MasterProductPostgresController...")
            
            # Initialize database
            MasterProductPostgresController.initialize_database()
            print("Database initialized.")
            
            # Create specs object
            specs = {
                "color": "Blue",
                "dimensions": "15x8x3",
                "weight": 1.2,
                "material": "Metal"
            }
            
            # Create master product
            product_id = MasterProductPostgresController.create_product(
                name="Controller Test Master Product",
                description="A master product for testing PostgreSQL controller",
                sku="CTMP001",
                upc="323456789012",
                manufacturer="Test Controller Manufacturer",
                manufacturer_part_number="TCM-001",
                specs=specs
            )
            print(f"Created master product with ID: {product_id}")
            
            # Get master product
            product = MasterProductPostgresController.get_product(product_id)
            print(f"Retrieved master product: {product}")
            
            # Update master product
            updated_specs = {
                "color": "Green",
                "dimensions": "15x8x3",
                "weight": 1.25,
                "material": "Metal",
                "packaging": "Retail Box"
            }
            
            MasterProductPostgresController.update_product(
                product_id,
                name="Updated Controller Test Master Product",
                description="An updated master product for testing",
                specs=updated_specs
            )
            print("Master product updated.")
            
            # Get updated master product
            updated_product = MasterProductPostgresController.get_product(product_id)
            print(f"Updated master product: {updated_product}")
            
            # Search master products
            search_results = MasterProductPostgresController.search_products("Controller")
            print(f"Search results: {len(search_results)}")
            
            # Get by SKU
            sku_product = MasterProductPostgresController.get_product_by_sku("CTMP001")
            print(f"Master product with SKU CTMP001: {sku_product[1] if sku_product else None}")
            
            # Get by UPC
            upc_product = MasterProductPostgresController.get_product_by_upc("323456789012")
            print(f"Master product with UPC 323456789012: {upc_product[1] if upc_product else None}")
            
            # Get by manufacturer and part number
            mpn_product = MasterProductPostgresController.get_product_by_mpn("Test Controller Manufacturer", "TCM-001")
            print(f"Master product with MPN TCM-001: {mpn_product[1] if mpn_product else None}")
            
            # Get all master products
            all_products = MasterProductPostgresController.get_all_products()
            print(f"All master products count: {len(all_products)}")
            
            # Delete master product
            MasterProductPostgresController.delete_product(product_id)
            print(f"Deleted master product ID: {product_id}")
            
            # Verify deletion
            all_products_after_delete = MasterProductPostgresController.get_all_products()
            print(f"All master products after deletion: {len(all_products_after_delete)}")
            
            print("MasterProductPostgresController test completed successfully!")
            return True
        except Exception as e:
            print(f"Error testing MasterProductPostgresController: {e}")
            import traceback
            traceback.print_exc()
            return False

# Run the test if this file is executed directly
if __name__ == "__main__":
    MasterProductPostgresController.test_controller() 