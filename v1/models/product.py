from models.base import BaseModel

class Product(BaseModel):
    """Model representing a product"""
    
    table_name = "products"
    
    def __init__(self, id=None, name=None, description=None, sku=None, price=None, status="active"):
        self.id = id
        self.name = name
        self.description = description
        self.sku = sku
        self.price = price
        self.status = status
    
    @classmethod
    def create_table(cls):
        """Create the products table if it doesn't exist"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            sku TEXT UNIQUE,
            price REAL,
            status TEXT DEFAULT 'active'
        )
        ''')
        
        # Create the vendor_products join table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendor_products (
            vendor_id INTEGER,
            product_id INTEGER,
            vendor_sku TEXT,
            vendor_price REAL,
            PRIMARY KEY (vendor_id, product_id),
            FOREIGN KEY (vendor_id) REFERENCES vendors (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save(self):
        """Save the product to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO products (name, description, sku, price, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (self.name, self.description, self.sku, self.price, self.status))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.id
    
    def update(self):
        """Update the product in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE products
        SET name = ?, description = ?, sku = ?, price = ?, status = ?
        WHERE id = ?
        ''', (self.name, self.description, self.sku, self.price, self.status, self.id))
        conn.commit()
        conn.close()
    
    def delete(self):
        """Delete the product from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()
    
    @classmethod
    def find_by_sku(cls, sku):
        """Find a product by SKU"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE sku = ?", (sku,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_by_name(cls, name):
        """Find products by name (partial match)"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{name}%",))
        rows = cursor.fetchall()
        conn.close()
        return rows