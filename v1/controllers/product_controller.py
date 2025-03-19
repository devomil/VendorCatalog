from models.product import Product

class ProductController:
    """Controller for product-related operations"""
    
    @staticmethod
    def initialize_database():
        """Initialize the database tables"""
        Product.create_table()
    
    @staticmethod
    def create_product(name, description=None, sku=None, price=None):
        """Create a new product"""
        product = Product(name=name, description=description, sku=sku, price=price)
        product_id = product.save()
        return product_id
    
    @staticmethod
    def update_product(product_id, name=None, description=None, sku=None, price=None, status=None):
        """Update an existing product"""
        # Get current product data
        product_data = Product.find_by_id(product_id)
        if not product_data:
            return False
            
        # Create product object with current data
        product = Product(
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
        product = Product(id=product_id)
        product.delete()
        return True
    
    @staticmethod
    def get_product(product_id):
        """Get a product by ID"""
        return Product.find_by_id(product_id)
    
    @staticmethod
    def search_products(search_term):
        """Search products by name"""
        return Product.find_by_name(search_term)
    
    @staticmethod
    def get_all_products():
        """Get all products"""
        return Product.find_all()