from models.master_product import MasterProduct

class MasterProductController:
    """Controller for master product-related operations"""
    
    @staticmethod
    def initialize_database():
        """Initialize the database tables"""
        MasterProduct.create_table()
    
    @staticmethod
    def create_product(name, description=None, sku=None, upc=None, manufacturer=None, 
                       manufacturer_part_number=None, category_id=None, specs=None):
        """Create a new master product"""
        product = MasterProduct(
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