"""
PostgreSQL-specific implementation of the Product model
"""

import sys
import os
import psycopg2
from psycopg2 import sql
import json
import time
import random

class ProductPostgres:
    """PostgreSQL implementation of the Product model"""
    
    table_name = "products"
    
    def __init__(self, id=None, name=None, description=None, sku=None, price=None, status="active"):
        self.id = id
        self.name = name
        self.description = description
        self.sku = sku
        self.price = price
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
        """Create the products table if it doesn't exist"""
        product = cls()  # Create instance to access connection method
        conn = product.get_connection()
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            sku TEXT UNIQUE,
            price NUMERIC,
            status TEXT DEFAULT 'active'
        )
        ''')
        
        # Create the vendor_products join table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendor_products (
            vendor_id INTEGER,
            product_id INTEGER,
            vendor_sku TEXT,
            vendor_price NUMERIC,
            PRIMARY KEY (vendor_id, product_id),
            FOREIGN KEY (vendor_id) REFERENCES vendors (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        print("Product tables created or already exist")
    
    def save(self):
        """Save the product to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO products (name, description, sku, price, status)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
        ''', (self.name, self.description, self.sku, self.price, self.status))
        self.id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return self.id
    
    def update(self):
        """Update the product in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE products
        SET name = %s, description = %s, sku = %s, price = %s, status = %s
        WHERE id = %s
        ''', (self.name, self.description, self.sku, self.price, self.status, self.id))
        conn.commit()
        conn.close()
    
    def delete(self):
        """Delete the product from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = %s', (self.id,))
        conn.commit()
        conn.close()
    
    @classmethod
    def find_by_id(cls, id):
        """Find a product by ID"""
        product = cls()  # Create instance to access connection method
        conn = product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_by_sku(cls, sku):
        """Find a product by SKU"""
        product = cls()  # Create instance to access connection method
        conn = product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE sku = %s", (sku,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_by_name(cls, name):
        """Find products by name (partial match)"""
        product = cls()  # Create instance to access connection method
        conn = product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE name ILIKE %s", (f"%{name}%",))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @classmethod
    def find_all(cls):
        """Find all products"""
        product = cls()  # Create instance to access connection method
        conn = product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @staticmethod
    def test_postgres_integration():
        """Test PostgreSQL integration with products"""
        try:
            print("Testing PostgreSQL integration with products...")
            
            # Create table
            ProductPostgres.create_table()
            
            # Generate unique SKUs to avoid conflicts
            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            sku1 = f"TP{timestamp}_{random_suffix}"
            sku2 = f"TP{timestamp}_{random_suffix+1}"
            
            # Create products
            product1 = ProductPostgres(
                name="Test Product 1", 
                description="A test product", 
                sku=sku1,
                price=19.99
            )
            product1_id = product1.save()
            print(f"Created product with ID: {product1_id}")
            
            product2 = ProductPostgres(
                name="Test Product 2", 
                description="Another test product", 
                sku=sku2,
                price=29.99
            )
            product2_id = product2.save()
            print(f"Created product with ID: {product2_id}")
            
            # Retrieve products
            all_products = ProductPostgres.find_all()
            print(f"All products: {all_products}")
            
            # Update product
            product1 = ProductPostgres(
                id=product1_id,
                name="Updated Test Product", 
                description="An updated test product", 
                sku=sku1,
                price=24.99
            )
            product1.update()
            print(f"Updated product: {ProductPostgres.find_by_id(product1_id)}")
            
            # Search products
            test_products = ProductPostgres.find_by_name("Test")
            print(f"Test products: {test_products}")
            
            # Find by SKU
            sku_product = ProductPostgres.find_by_sku(sku2)
            print(f"Product with SKU {sku2}: {sku_product}")
            
            # Delete product
            product2 = ProductPostgres(id=product2_id)
            product2.delete()
            print(f"Deleted product ID: {product2_id}")
            
            # Verify deletion
            all_products_after_delete = ProductPostgres.find_all()
            print(f"All products after deletion: {all_products_after_delete}")
            
            # Clean up - delete test product
            product1 = ProductPostgres(id=product1_id)
            product1.delete()
            print(f"Deleted product ID: {product1_id}")
            
            print("PostgreSQL integration test completed successfully!")
            return True
        except Exception as e:
            print(f"Error testing PostgreSQL integration: {e}")
            import traceback
            traceback.print_exc()
            return False

# Run the test if this file is executed directly
if __name__ == "__main__":
    ProductPostgres.test_postgres_integration() 