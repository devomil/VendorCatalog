"""
PostgreSQL-specific implementation of the VendorProduct model
"""

import sys
import os
import psycopg2
from psycopg2 import sql
import json
from datetime import datetime

class VendorProductPostgres:
    """PostgreSQL implementation of the VendorProduct model"""
    
    table_name = "vendor_products"
    
    def __init__(self, id=None, vendor_id=None, master_product_id=None, vendor_sku=None, 
                 vendor_price=None, list_price=None, map_price=None, mrp_price=None,
                 quantity=0, quantity_nj=0, quantity_fl=0, 
                 eta=None, eta_nj=None, eta_fl=None,
                 shipping_weight=None, shipping_dimensions=None, 
                 props=None, status="active"):
        self.id = id
        self.vendor_id = vendor_id
        self.master_product_id = master_product_id
        self.vendor_sku = vendor_sku
        self.vendor_price = vendor_price
        self.list_price = list_price
        self.map_price = map_price
        self.mrp_price = mrp_price
        self.quantity = quantity
        self.quantity_nj = quantity_nj
        self.quantity_fl = quantity_fl
        self.eta = eta
        self.eta_nj = eta_nj
        self.eta_fl = eta_fl
        self.shipping_weight = shipping_weight
        self.shipping_dimensions = shipping_dimensions
        self.props = props  # JSON string containing additional properties
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
        """Create the vendor_products table if it doesn't exist"""
        vendor_product = cls()  # Create instance to access connection method
        conn = vendor_product.get_connection()
        cursor = conn.cursor()
        
        # Check if master_products table exists
        master_products_exists = False
        try:
            cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'master_products'")
            master_products_exists = cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking for master_products table: {e}")
        
        # Check if vendor_products table already exists
        cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'vendor_products'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Attempt to drop any existing indexes first to avoid errors
            try:
                cursor.execute('DROP INDEX IF EXISTS idx_vendor_products_vendor_id')
                cursor.execute('DROP INDEX IF EXISTS idx_vendor_products_master_product_id')
            except Exception as e:
                print(f"Warning when dropping indexes: {e}")
            
            # Create the sequence for ID generation if it doesn't exist
            try:
                cursor.execute("CREATE SEQUENCE IF NOT EXISTS vendor_products_id_seq")
                conn.commit()
                print("Created ID sequence for vendor_products")
            except Exception as e:
                print(f"Error creating sequence: {e}")
                conn.rollback()
            
            # Create vendor_products table with or without the foreign key constraint
            if master_products_exists:
                # Create table with foreign key to master_products
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendor_products (
                    id INTEGER PRIMARY KEY DEFAULT nextval('vendor_products_id_seq'),
                    vendor_id INTEGER NOT NULL,
                    master_product_id INTEGER,
                    vendor_sku TEXT,
                    vendor_price NUMERIC,
                    list_price NUMERIC,
                    map_price NUMERIC,
                    mrp_price NUMERIC,
                    quantity INTEGER DEFAULT 0,
                    quantity_nj INTEGER DEFAULT 0,
                    quantity_fl INTEGER DEFAULT 0,
                    eta TEXT,
                    eta_nj TEXT,
                    eta_fl TEXT,
                    shipping_weight NUMERIC,
                    shipping_dimensions TEXT,
                    props TEXT,  -- JSON string containing additional properties
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (vendor_id) REFERENCES vendors (id),
                    FOREIGN KEY (master_product_id) REFERENCES master_products (id),
                    UNIQUE(vendor_id, vendor_sku)
                )
                ''')
                print("Created vendor_products table with master_products foreign key")
            else:
                # Create table without foreign key to master_products
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendor_products (
                    id INTEGER PRIMARY KEY DEFAULT nextval('vendor_products_id_seq'),
                    vendor_id INTEGER NOT NULL,
                    vendor_sku TEXT,
                    vendor_price NUMERIC,
                    list_price NUMERIC,
                    map_price NUMERIC,
                    mrp_price NUMERIC,
                    quantity INTEGER DEFAULT 0,
                    quantity_nj INTEGER DEFAULT 0,
                    quantity_fl INTEGER DEFAULT 0,
                    eta TEXT,
                    eta_nj TEXT,
                    eta_fl TEXT,
                    shipping_weight NUMERIC,
                    shipping_dimensions TEXT,
                    props TEXT,  -- JSON string containing additional properties
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (vendor_id) REFERENCES vendors (id),
                    UNIQUE(vendor_id, vendor_sku)
                )
                ''')
                print("Created vendor_products table without master_products foreign key")
            
            # Configure the sequence ownership
            try:
                cursor.execute("ALTER SEQUENCE vendor_products_id_seq OWNED BY vendor_products.id")
                conn.commit()
                print("Set sequence ownership for vendor_products.id")
            except Exception as e:
                print(f"Error setting sequence ownership: {e}")
                conn.rollback()
            
            conn.commit()
        else:
            print("Vendor_products table already exists")
            
            # Check if the ID column is correctly configured
            cursor.execute("""
            SELECT column_default FROM information_schema.columns 
            WHERE table_name = 'vendor_products' AND column_name = 'id'
            """)
            id_default = cursor.fetchone()
            
            # If ID column doesn't have a default or sequence, try to add one
            if not id_default or 'nextval' not in str(id_default[0]):
                try:
                    print("ID column doesn't have a proper sequence. Attempting to fix...")
                    
                    # Create sequence if it doesn't exist
                    cursor.execute("CREATE SEQUENCE IF NOT EXISTS vendor_products_id_seq")
                    
                    # Get current max ID
                    cursor.execute("SELECT MAX(id) FROM vendor_products")
                    max_id = cursor.fetchone()[0] or 0
                    
                    # Set sequence to start after the max ID
                    cursor.execute(f"ALTER SEQUENCE vendor_products_id_seq RESTART WITH {max_id + 1}")
                    
                    # Try to alter the column default
                    try:
                        cursor.execute("ALTER TABLE vendor_products ALTER COLUMN id SET DEFAULT nextval('vendor_products_id_seq')")
                    except Exception as e:
                        print(f"Could not set column default: {e}")
                    
                    # Set sequence ownership
                    cursor.execute("ALTER SEQUENCE vendor_products_id_seq OWNED BY vendor_products.id")
                    
                    conn.commit()
                    print("Fixed ID column sequence")
                except Exception as e:
                    print(f"Error fixing ID column: {e}")
                    conn.rollback()
            
            # List of required columns and their SQL definitions
            required_columns = {
                "master_product_id": "INTEGER",
                "vendor_sku": "TEXT",
                "vendor_price": "NUMERIC",
                "list_price": "NUMERIC",
                "map_price": "NUMERIC",
                "mrp_price": "NUMERIC",
                "quantity": "INTEGER DEFAULT 0",
                "quantity_nj": "INTEGER DEFAULT 0",
                "quantity_fl": "INTEGER DEFAULT 0",
                "eta": "TEXT",
                "eta_nj": "TEXT",
                "eta_fl": "TEXT",
                "shipping_weight": "NUMERIC",
                "shipping_dimensions": "TEXT",
                "props": "TEXT",
                "status": "TEXT DEFAULT 'active'"
            }
            
            # Check for each required column
            for column_name, column_type in required_columns.items():
                cursor.execute(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'vendor_products' AND column_name = %s",
                    (column_name,)
                )
                if not cursor.fetchone():
                    try:
                        print(f"Adding missing column: {column_name}")
                        cursor.execute(f'ALTER TABLE vendor_products ADD COLUMN {column_name} {column_type}')
                        conn.commit()
                        print(f"Added {column_name} column to vendor_products table")
                    except Exception as e:
                        print(f"Error adding {column_name} column: {e}")
                        conn.rollback()
            
            # Add foreign key constraint if master_products table exists and the column is there
            if master_products_exists:
                try:
                    # Check if the constraint already exists
                    cursor.execute("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'vendor_products' 
                    AND constraint_name = 'fk_master_product'
                    """)
                    if not cursor.fetchone():
                        cursor.execute('''
                        ALTER TABLE vendor_products 
                        ADD CONSTRAINT fk_master_product 
                        FOREIGN KEY (master_product_id) 
                        REFERENCES master_products (id)
                        ''')
                        conn.commit()
                        print("Added foreign key constraint for master_product_id")
                except Exception as e:
                    print(f"Error adding foreign key constraint: {e}")
                    conn.rollback()
        
        # Now create the indexes if they don't exist
        try:
            # Create indexes for faster lookups if they don't exist
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendor_products_vendor_id ON vendor_products (vendor_id)')
            
            # Verify if the master_product_id column exists again (it might have been added above)
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'vendor_products' AND column_name = 'master_product_id'")
            if cursor.fetchone():
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendor_products_master_product_id ON vendor_products (master_product_id)')
            
            conn.commit()
        except Exception as e:
            print(f"Warning when creating indexes: {e}")
        
        conn.close()
        print("Vendor product table setup complete")
    
    def save(self):
        """Save the vendor product to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert props to JSON string if it's a dict
        props_json = json.dumps(self.props) if isinstance(self.props, dict) else self.props
        
        try:
            # First, check if the id column is a SERIAL or IDENTITY
            cursor.execute("""
            SELECT column_default FROM information_schema.columns 
            WHERE table_name = 'vendor_products' AND column_name = 'id'
            """)
            id_default = cursor.fetchone()
            
            if id_default and ('nextval' in id_default[0] or 'identity' in id_default[0].lower()):
                # The id column is a SERIAL or IDENTITY, use RETURNING clause
                cursor.execute('''
                INSERT INTO vendor_products (
                    vendor_id, master_product_id, vendor_sku, vendor_price, list_price,
                    map_price, mrp_price, quantity, quantity_nj, quantity_fl,
                    eta, eta_nj, eta_fl, shipping_weight, shipping_dimensions, props, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                ''', (
                    self.vendor_id, self.master_product_id, self.vendor_sku, self.vendor_price,
                    self.list_price, self.map_price, self.mrp_price, 
                    self.quantity, self.quantity_nj, self.quantity_fl,
                    self.eta, self.eta_nj, self.eta_fl,
                    self.shipping_weight, self.shipping_dimensions,
                    props_json, self.status
                ))
                self.id = cursor.fetchone()[0]
            else:
                # The id column is not a SERIAL, we need to handle ID generation differently
                # First try to get the max id
                cursor.execute("SELECT MAX(id) FROM vendor_products")
                max_id = cursor.fetchone()[0]
                self.id = (max_id or 0) + 1
                
                # Insert with explicit id
                cursor.execute('''
                INSERT INTO vendor_products (
                    id, vendor_id, master_product_id, vendor_sku, vendor_price, list_price,
                    map_price, mrp_price, quantity, quantity_nj, quantity_fl,
                    eta, eta_nj, eta_fl, shipping_weight, shipping_dimensions, props, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    self.id, self.vendor_id, self.master_product_id, self.vendor_sku, self.vendor_price,
                    self.list_price, self.map_price, self.mrp_price, 
                    self.quantity, self.quantity_nj, self.quantity_fl,
                    self.eta, self.eta_nj, self.eta_fl,
                    self.shipping_weight, self.shipping_dimensions,
                    props_json, self.status
                ))
            
            conn.commit()
            print(f"Saved vendor product with ID: {self.id}")
            return self.id
        except Exception as e:
            conn.rollback()
            print(f"Error saving vendor product: {e}")
            raise
        finally:
            conn.close()
    
    def update(self):
        """Update the vendor product in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Convert props to JSON string if it's a dict
        props_json = json.dumps(self.props) if isinstance(self.props, dict) else self.props
        
        cursor.execute('''
        UPDATE vendor_products
        SET vendor_id = %s, master_product_id = %s, vendor_sku = %s, vendor_price = %s,
            list_price = %s, map_price = %s, mrp_price = %s,
            quantity = %s, quantity_nj = %s, quantity_fl = %s,
            eta = %s, eta_nj = %s, eta_fl = %s,
            shipping_weight = %s, shipping_dimensions = %s, props = %s, status = %s
        WHERE id = %s
        ''', (
            self.vendor_id, self.master_product_id, self.vendor_sku, self.vendor_price,
            self.list_price, self.map_price, self.mrp_price,
            self.quantity, self.quantity_nj, self.quantity_fl,
            self.eta, self.eta_nj, self.eta_fl,
            self.shipping_weight, self.shipping_dimensions,
            props_json, self.status, self.id
        ))
        conn.commit()
        conn.close()
    
    def delete(self):
        """Delete the vendor product from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vendor_products WHERE id = %s', (self.id,))
        conn.commit()
        conn.close()
    
    @classmethod
    def find_by_id(cls, id):
        """Find a vendor product by ID"""
        vendor_product = cls()  # Create instance to access connection method
        conn = vendor_product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendor_products WHERE id = %s", (id,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_by_vendor_and_sku(cls, vendor_id, vendor_sku):
        """Find a vendor product by vendor ID and SKU"""
        vendor_product = cls()  # Create instance to access connection method
        conn = vendor_product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendor_products WHERE vendor_id = %s AND vendor_sku = %s", 
                     (vendor_id, vendor_sku))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_by_vendor(cls, vendor_id):
        """Find all products for a vendor"""
        vendor_product = cls()  # Create instance to access connection method
        conn = vendor_product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendor_products WHERE vendor_id = %s", (vendor_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @classmethod
    def find_by_master_product(cls, master_product_id):
        """Find all vendor products for a master product"""
        vendor_product = cls()  # Create instance to access connection method
        conn = vendor_product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendor_products WHERE master_product_id = %s", (master_product_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @classmethod
    def find_all(cls):
        """Find all vendor products"""
        vendor_product = cls()  # Create instance to access connection method
        conn = vendor_product.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendor_products")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @classmethod
    def bulk_insert(cls, vendor_id, products_data, batch_size=1000):
        """
        Bulk insert vendor products
        
        products_data: List of dictionaries containing product data
        batch_size: Number of products to insert in a single batch
        """
        if not products_data:
            return 0
            
        vendor_product = cls()  # Create instance to access connection method
        conn = vendor_product.get_connection()
        cursor = conn.cursor()
        
        # Process products in batches
        total_inserted = 0
        for i in range(0, len(products_data), batch_size):
            batch = products_data[i:i+batch_size]
            
            # Prepare SQL placeholders and values
            placeholders = []
            values = []
            
            for product in batch:
                # Process product data to extract fields
                vendor_sku = product.get('sku', '')
                vendor_price = product.get('price')
                list_price = product.get('list')
                map_price = product.get('map')
                mrp_price = product.get('mrp')
                
                qty = product.get('qty', 0)
                qty_nj = product.get('qtynj', 0)
                qty_fl = product.get('qtyfl', 0)
                
                eta = product.get('eta')
                eta_nj = product.get('etanj')
                eta_fl = product.get('etafl')
                
                weight = product.get('wt')
                
                # Extract dimensions if available
                dimensions = None
                if 'bh' in product and 'bl' in product and 'bw' in product:
                    dimensions = f"{product.get('bl', '')}x{product.get('bw', '')}x{product.get('bh', '')}"
                
                # Extract all additional properties
                props = {k: v for k, v in product.items() if k not in [
                    'sku', 'price', 'list', 'map', 'mrp', 'qty', 'qtynj', 'qtyfl',
                    'eta', 'etanj', 'etafl', 'wt', 'bh', 'bl', 'bw'
                ]}
                
                # Add placeholders and values
                placeholders.append(
                    "(%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')"
                )
                values.extend([
                    vendor_id, vendor_sku, vendor_price, list_price, map_price, mrp_price,
                    qty, qty_nj, qty_fl, eta, eta_nj, eta_fl, weight, dimensions,
                    json.dumps(props) if props else None
                ])
            
            # Construct and execute the SQL query
            if placeholders:
                sql_query = f"""
                INSERT INTO vendor_products (
                    vendor_id, master_product_id, vendor_sku, vendor_price, list_price,
                    map_price, mrp_price, quantity, quantity_nj, quantity_fl,
                    eta, eta_nj, eta_fl, shipping_weight, shipping_dimensions, status
                )
                VALUES {", ".join(placeholders)}
                ON CONFLICT (vendor_id, vendor_sku) DO UPDATE
                SET 
                    vendor_price = EXCLUDED.vendor_price,
                    list_price = EXCLUDED.list_price,
                    map_price = EXCLUDED.map_price,
                    mrp_price = EXCLUDED.mrp_price,
                    quantity = EXCLUDED.quantity,
                    quantity_nj = EXCLUDED.quantity_nj,
                    quantity_fl = EXCLUDED.quantity_fl,
                    eta = EXCLUDED.eta,
                    eta_nj = EXCLUDED.eta_nj,
                    eta_fl = EXCLUDED.eta_fl,
                    shipping_weight = EXCLUDED.shipping_weight,
                    shipping_dimensions = EXCLUDED.shipping_dimensions
                """
                cursor.execute(sql_query, values)
                total_inserted += len(batch)
        
        conn.commit()
        conn.close()
        return total_inserted
    
    @staticmethod
    def test_postgres_integration():
        """Test PostgreSQL integration with vendor products"""
        try:
            import time
            import random
            
            print("Testing PostgreSQL integration with vendor products...")
            
            # Create table
            VendorProductPostgres.create_table()
            
            # First, we need to create a vendor to use
            from models.vendor_postgres import VendorPostgres
            VendorPostgres.create_table()
            
            # Generate unique identifiers
            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            vendor_name = f"Vendor Product Test Vendor {timestamp}_{random_suffix}"
            sku1 = f"VP{timestamp}_{random_suffix}"
            sku2 = f"VP{timestamp}_{random_suffix+1}"
            
            vendor = VendorPostgres(
                name=vendor_name,
                description="A vendor for testing vendor products",
                contact_info=f"test{timestamp}@vendorproduct.com"
            )
            vendor_id = vendor.save()
            print(f"Created test vendor with ID: {vendor_id}")
            
            # Create vendor products
            props1 = {
                "brand": "Test Brand",
                "category": "Test Category",
                "tags": ["test", "sample"]
            }
            
            vp1 = VendorProductPostgres(
                vendor_id=vendor_id,
                vendor_sku=sku1,
                vendor_price=19.99,
                list_price=24.99,
                map_price=22.99,
                quantity=100,
                quantity_nj=50,
                quantity_fl=50,
                props=props1
            )
            vp1_id = vp1.save()
            print(f"Created vendor product with ID: {vp1_id}")
            
            props2 = {
                "brand": "Another Brand",
                "category": "Another Category",
                "tags": ["sample", "test2"],
                "color": "Blue"
            }
            
            vp2 = VendorProductPostgres(
                vendor_id=vendor_id,
                vendor_sku=sku2,
                vendor_price=29.99,
                list_price=34.99,
                map_price=32.99,
                quantity=75,
                shipping_weight=1.5,
                shipping_dimensions="10x8x6",
                props=props2
            )
            vp2_id = vp2.save()
            print(f"Created vendor product with ID: {vp2_id}")
            
            # Retrieve vendor products
            all_vps = VendorProductPostgres.find_all()
            print(f"All vendor products: {len(all_vps)}")
            
            # Find by vendor
            vendor_vps = VendorProductPostgres.find_by_vendor(vendor_id)
            print(f"Products for vendor {vendor_id}: {len(vendor_vps)}")
            
            # Find by vendor and SKU
            vp_by_sku = VendorProductPostgres.find_by_vendor_and_sku(vendor_id, sku1)
            print(f"Vendor product with SKU {sku1}: {vp_by_sku[3] if vp_by_sku else None}")  # Print the SKU
            
            # Update vendor product
            updated_props = {
                "brand": "Updated Brand",
                "category": "Test Category",
                "tags": ["test", "sample", "updated"],
                "featured": True
            }
            
            vp1 = VendorProductPostgres(
                id=vp1_id,
                vendor_id=vendor_id,
                vendor_sku=sku1,
                vendor_price=21.99,
                list_price=26.99,
                map_price=23.99,
                quantity=120,
                quantity_nj=60,
                quantity_fl=60,
                props=updated_props
            )
            vp1.update()
            print(f"Updated vendor product: {VendorProductPostgres.find_by_id(vp1_id)}")
            
            # Generate unique SKUs for bulk insert
            bulk_sku1 = f"BULK{timestamp}_{random_suffix}"
            bulk_sku2 = f"BULK{timestamp}_{random_suffix+1}"
            bulk_sku3 = f"BULK{timestamp}_{random_suffix+2}"
            
            # Test bulk insert
            bulk_products = [
                {
                    "sku": bulk_sku1,
                    "price": 9.99,
                    "list": 12.99,
                    "map": 11.99,
                    "qty": 50,
                    "qtynj": 25,
                    "qtyfl": 25,
                    "brand": "Bulk Brand 1"
                },
                {
                    "sku": bulk_sku2,
                    "price": 14.99,
                    "list": 19.99,
                    "map": 17.99,
                    "qty": 30,
                    "wt": 1.2,
                    "bl": 8,
                    "bw": 6,
                    "bh": 4,
                    "brand": "Bulk Brand 2"
                },
                {
                    "sku": bulk_sku3,
                    "price": 24.99,
                    "list": 29.99,
                    "qty": 15,
                    "brand": "Bulk Brand 3",
                    "color": "Green"
                }
            ]
            
            bulk_count = VendorProductPostgres.bulk_insert(vendor_id, bulk_products)
            print(f"Bulk inserted {bulk_count} vendor products")
            
            # Verify bulk insert
            all_vps_after_bulk = VendorProductPostgres.find_by_vendor(vendor_id)
            print(f"Vendor products after bulk insert: {len(all_vps_after_bulk)}")
            
            # Delete vendor product
            vp2 = VendorProductPostgres(id=vp2_id)
            vp2.delete()
            print(f"Deleted vendor product ID: {vp2_id}")
            
            # Delete first vendor product
            vp1 = VendorProductPostgres(id=vp1_id)
            vp1.delete()
            print(f"Deleted vendor product ID: {vp1_id}")
            
            # Verify deletion
            remaining_vps = VendorProductPostgres.find_by_vendor(vendor_id)
            print(f"Remaining vendor products: {len(remaining_vps)}")
            
            # Clean up - delete test vendor
            # First delete all remaining vendor products for this vendor
            for vp in remaining_vps:
                vp_obj = VendorProductPostgres(id=vp[0])
                vp_obj.delete()
                print(f"Cleaned up vendor product ID: {vp[0]}")
            
            vendor = VendorPostgres(id=vendor_id)
            vendor.delete()
            print(f"Deleted test vendor ID: {vendor_id}")
            
            print("PostgreSQL integration test completed successfully!")
            return True
        except Exception as e:
            print(f"Error testing PostgreSQL integration: {e}")
            import traceback
            traceback.print_exc()
            return False

# Run the test if this file is executed directly
if __name__ == "__main__":
    VendorProductPostgres.test_postgres_integration() 