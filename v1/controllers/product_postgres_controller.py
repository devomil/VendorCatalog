"""
PostgreSQL-specific implementation of the Product Controller
"""

import sys
import os

# Add the parent directory to sys.path to allow importing from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.product_postgres import ProductPostgres

class ProductPostgresController:
    """Controller for product-related operations using PostgreSQL"""
    
    @staticmethod
    def initialize_database():
        """Initialize the database tables"""
        ProductPostgres.create_table()
    
    @staticmethod
    def create_product(name, description=None, sku=None, price=None):
        """Create a new product"""
        product = ProductPostgres(name=name, description=description, sku=sku, price=price)
        product_id = product.save()
        return product_id
    
    @staticmethod
    def update_product(product_id, name=None, description=None, sku=None, price=None, status=None):
        """Update an existing product"""
        # Get current product data
        product_data = ProductPostgres.find_by_id(product_id)
        if not product_data:
            return False
            
        # Create product object with current data
        product = ProductPostgres(
            id=product_id,
            name=product_data[1] if name is None else name,
            description=product_data[2] if description is None else description,
            sku=product_data[3] if sku is None else sku,
            price=product_data[4] if price is None else price,
            status=product_data[5] if status is None else status
        )
        
        product.update()
        return True
    
    @staticmethod
    def delete_product(product_id):
        """Delete a product"""
        product = ProductPostgres(id=product_id)
        product.delete()
        return True
    
    @staticmethod
    def get_product(product_id):
        """Get a product by ID"""
        return ProductPostgres.find_by_id(product_id)
    
    @staticmethod
    def get_product_by_sku(sku):
        """Get a product by SKU"""
        return ProductPostgres.find_by_sku(sku)
    
    @staticmethod
    def search_products(search_term):
        """Search products by name"""
        return ProductPostgres.find_by_name(search_term)
    
    @staticmethod
    def get_all_products():
        """Get all products"""
        return ProductPostgres.find_all()
    
    @staticmethod
    def test_controller():
        """Test the controller functionality"""
        try:
            print("Testing ProductPostgresController...")
            
            # Initialize database
            ProductPostgresController.initialize_database()
            print("Database initialized.")
            
            # Create product
            product_id = ProductPostgresController.create_product(
                name="Controller Test Product",
                description="A product for testing PostgreSQL controller",
                sku="CTP001",
                price=39.99
            )
            print(f"Created product with ID: {product_id}")
            
            # Get product
            product = ProductPostgresController.get_product(product_id)
            print(f"Retrieved product: {product}")
            
            # Update product
            ProductPostgresController.update_product(
                product_id,
                name="Updated Controller Test Product",
                description="An updated product for testing",
                price=44.99
            )
            print("Product updated.")
            
            # Get updated product
            updated_product = ProductPostgresController.get_product(product_id)
            print(f"Updated product: {updated_product}")
            
            # Search products
            search_results = ProductPostgresController.search_products("Controller")
            print(f"Search results: {search_results}")
            
            # Get by SKU
            sku_product = ProductPostgresController.get_product_by_sku("CTP001")
            print(f"Product with SKU CTP001: {sku_product}")
            
            # Get all products
            all_products = ProductPostgresController.get_all_products()
            print(f"All products count: {len(all_products)}")
            
            # Delete product
            ProductPostgresController.delete_product(product_id)
            print(f"Deleted product ID: {product_id}")
            
            # Verify deletion
            all_products_after_delete = ProductPostgresController.get_all_products()
            print(f"All products after deletion: {len(all_products_after_delete)}")
            
            print("ProductPostgresController test completed successfully!")
            return True
        except Exception as e:
            print(f"Error testing ProductPostgresController: {e}")
            import traceback
            traceback.print_exc()
            return False

# Run the test if this file is executed directly
if __name__ == "__main__":
    ProductPostgresController.test_controller() 