"""
PostgreSQL-specific implementation of the MasterProduct model
"""

import sys
import os
import psycopg2
from psycopg2 import sql
import json
import time
import random

class MasterProductPostgres:
    """PostgreSQL implementation of the MasterProduct model"""
    
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
        
        # PostgreSQL connection parameters
        self.db_host = "localhost"
        self.db_port = 5432
        self.db_name = "vendor_catalog"
        self.db_user = "vendor_user"
        self.db_password = "vendor_pass"
    
    def get_connection(self):
        """Get a PostgreSQL database connection"""
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name
        )
    
    @classmethod
    def create_table(cls):
        """Create the master_products table if it doesn't exist"""
        master_product = cls()  # Create instance to access connection method
        conn = master_product.get_connection()
        cursor = conn.cursor()
        
        # Create master_products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS master_products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            sku TEXT UNIQUE,
            upc TEXT,
            manufacturer TEXT,
            manufacturer_part_number TEXT,
            category_id INTEGER,
            specs TEXT,  -- JSON string containing specifications
            status TEXT DEFAULT 'active'
        )
        ''')
        
        # Create indexes for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_master_products_upc ON master_products (upc)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_master_products_manufacturer_part_number ON master_products (manufacturer_part_number)')
        
        conn.commit()
        conn.close()
        print("Master product table created or already exists")
    
    def save(self):
        """Save the master product to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert specs to JSON string if it's a dict
        specs_json = json.dumps(self.specs) if isinstance(self.specs, dict) else self.specs
        
        cursor.execute('''
        INSERT INTO master_products (
            name, description, sku, upc, manufacturer,
            manufacturer_part_number, category_id, specs, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        ''', (
            self.name, self.description, self.sku, self.upc, self.manufacturer,
            self.manufacturer_part_number, self.category_id, specs_json, self.status
        ))
        self.id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return self.id
    
    def update(self):
        """Update the master product in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert specs to JSON string if it's a dict
        specs_json = json.dumps(self.specs) if isinstance(self.specs, dict) else self.specs
        
        cursor.execute('''
        UPDATE master_products
        SET name = %s, description = %s, sku = %s, upc = %s, manufacturer = %s,
            manufacturer_part_number = %s, category_id = %s, specs = %s, status = %s
        WHERE id = %s
        ''', (
            self.name, self.description, self.sku, self.upc, self.manufacturer,
            self.manufacturer_part_number, self.category_id, specs_json, self.status, self.id
        ))
        conn.commit()
        conn.close()
    
    def delete(self):
        """Delete the master product from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM master_products WHERE id = %s', (self.id,))
        conn.commit()
        conn.close()
    
    @classmethod
    def find_by_id(cls, id):
        """Find a master product by ID"""
        master_product = cls()  # Create instance to access connection method
        conn = master_product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM master_products WHERE id = %s", (id,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_by_sku(cls, sku):
        """Find a master product by SKU"""
        master_product = cls()  # Create instance to access connection method
        conn = master_product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM master_products WHERE sku = %s", (sku,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_by_upc(cls, upc):
        """Find a master product by UPC"""
        master_product = cls()  # Create instance to access connection method
        conn = master_product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM master_products WHERE upc = %s", (upc,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_by_mpn(cls, manufacturer, mpn):
        """Find a master product by manufacturer and part number"""
        master_product = cls()  # Create instance to access connection method
        conn = master_product.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM master_products WHERE manufacturer ILIKE %s AND manufacturer_part_number = %s", 
            (manufacturer, mpn)
        )
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_by_name(cls, name):
        """Find master products by name (partial match)"""
        master_product = cls()  # Create instance to access connection method
        conn = master_product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM master_products WHERE name ILIKE %s", (f"%{name}%",))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @classmethod
    def find_all(cls):
        """Find all master products"""
        master_product = cls()  # Create instance to access connection method
        conn = master_product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM master_products")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @staticmethod
    def test_postgres_integration():
        """Test PostgreSQL integration with master products"""
        try:
            print("Testing PostgreSQL integration with master products...")
            
            # Create table
            MasterProductPostgres.create_table()
            
            # Generate unique SKUs to avoid conflicts
            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            sku1 = f"TMP{timestamp}_{random_suffix}"
            sku2 = f"TMP{timestamp}_{random_suffix+1}"
            upc1 = f"1234{timestamp}{random_suffix}"
            upc2 = f"2234{timestamp}{random_suffix}"
            
            # Create master products
            specs1 = {
                "color": "Black",
                "dimensions": "10x5x2",
                "weight": 0.5
            }
            
            product1 = MasterProductPostgres(
                name="Test Master Product 1", 
                description="A test master product", 
                sku=sku1,
                upc=upc1,
                manufacturer="Test Manufacturer",
                manufacturer_part_number="TM-001",
                specs=specs1
            )
            product1_id = product1.save()
            print(f"Created master product with ID: {product1_id}")
            
            specs2 = {
                "color": "White",
                "dimensions": "12x6x3",
                "weight": 0.75
            }
            
            product2 = MasterProductPostgres(
                name="Test Master Product 2", 
                description="Another test master product", 
                sku=sku2,
                upc=upc2,
                manufacturer="Test Manufacturer",
                manufacturer_part_number="TM-002",
                specs=specs2
            )
            product2_id = product2.save()
            print(f"Created master product with ID: {product2_id}")
            
            # Retrieve products
            all_products = MasterProductPostgres.find_all()
            print(f"All master products: {len(all_products)}")
            
            # Update product
            updated_specs = {
                "color": "Red",
                "dimensions": "10x5x2",
                "weight": 0.55,
                "material": "Plastic"
            }
            
            product1 = MasterProductPostgres(
                id=product1_id,
                name="Updated Test Master Product", 
                description="An updated test master product", 
                sku=sku1,
                upc=upc1,
                manufacturer="Test Manufacturer",
                manufacturer_part_number="TM-001",
                specs=updated_specs
            )
            product1.update()
            print(f"Updated master product: {MasterProductPostgres.find_by_id(product1_id)}")
            
            # Search products
            test_products = MasterProductPostgres.find_by_name("Master")
            print(f"Master products matching 'Master': {len(test_products)}")
            
            # Find by SKU
            sku_product = MasterProductPostgres.find_by_sku(sku2)
            print(f"Master product with SKU {sku2}: {sku_product[1] if sku_product else None}")
            
            # Find by UPC
            upc_product = MasterProductPostgres.find_by_upc(upc1)
            print(f"Master product with UPC {upc1}: {upc_product[1] if upc_product else None}")
            
            # Find by manufacturer and part number
            mpn_product = MasterProductPostgres.find_by_mpn("Test Manufacturer", "TM-002")
            print(f"Master product with MPN TM-002: {mpn_product[1] if mpn_product else None}")
            
            # Delete products (cleanup)
            product2 = MasterProductPostgres(id=product2_id)
            product2.delete()
            print(f"Deleted master product ID: {product2_id}")
            
            product1 = MasterProductPostgres(id=product1_id)
            product1.delete()
            print(f"Deleted master product ID: {product1_id}")
            
            # Verify deletion
            all_products_after_delete = MasterProductPostgres.find_all()
            print(f"All master products after deletion: {len(all_products_after_delete)}")
            
            print("PostgreSQL integration test completed successfully!")
            return True
        except Exception as e:
            print(f"Error testing PostgreSQL integration: {e}")
            import traceback
            traceback.print_exc()
            return False

# Run the test if this file is executed directly
if __name__ == "__main__":
    MasterProductPostgres.test_postgres_integration() 