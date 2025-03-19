from models.base import BaseModel
import json

class MasterProduct(BaseModel):
    """Model representing a master product in the catalog"""
    
    table_name = "master_products"
    
    def __init__(self, id=None, name=None, description=None, sku=None, upc=None, 
                 manufacturer=None, manufacturer_part_number=None, 
                 category_id=None, specs=None, status="active"):
        self.id = id
        self.name = name
        self.description = description
        self.sku = sku
        self.upc = upc
        self.manufacturer = manufacturer
        self.manufacturer_part_number = manufacturer_part_number
        self.category_id = category_id
        self.specs = specs  # JSON string containing product specifications
        self.status = status
    
    @classmethod
    def create_table(cls):
        """Create the master_products table if it doesn't exist"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS master_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            sku TEXT UNIQUE,
            upc TEXT,
            manufacturer TEXT,
            manufacturer_part_number TEXT,
            category_id INTEGER,
            specs TEXT,  -- JSON string containing specifications
            status TEXT DEFAULT 'active',
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')
        
        # Create the index for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_master_products_upc ON master_products (upc)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_master_products_manufacturer_part_number ON master_products (manufacturer_part_number)')
        
        conn.commit()
        conn.close()