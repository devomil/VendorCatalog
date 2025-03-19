from models.base import BaseModel
import json
from datetime import datetime

class VendorProduct(BaseModel):
    """Model representing a vendor's product"""
    
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

@classmethod
def create_table(cls):
    """Create the vendor_products table if it doesn't exist"""
    conn = cls.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendor_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL,
        master_product_id INTEGER,
        vendor_sku TEXT,
        vendor_price REAL,
        list_price REAL,
        map_price REAL,
        mrp_price REAL,
        quantity INTEGER DEFAULT 0,
        quantity_nj INTEGER DEFAULT 0,
        quantity_fl INTEGER DEFAULT 0,
        eta TEXT,
        eta_nj TEXT,
        eta_fl TEXT,
        shipping_weight REAL,
        shipping_dimensions TEXT,
        props TEXT,  -- JSON string containing additional properties
        status TEXT DEFAULT 'active',
        FOREIGN KEY (vendor_id) REFERENCES vendors (id),
        FOREIGN KEY (master_product_id) REFERENCES master_products (id),
        UNIQUE(vendor_id, vendor_sku)
    )
    ''')
    
    # Create indexes for faster lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendor_products_vendor_id ON vendor_products (vendor_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendor_products_master_product_id ON vendor_products (master_product_id)')
    
    conn.commit()
    conn.close()

def save(self):
    """Save the vendor product to the database"""
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO vendor_products (
        vendor_id, master_product_id, vendor_sku, vendor_price, list_price,
        map_price, mrp_price, quantity, quantity_nj, quantity_fl,
        eta, eta_nj, eta_fl, shipping_weight, shipping_dimensions, props, status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        self.vendor_id, self.master_product_id, self.vendor_sku, self.vendor_price,
        self.list_price, self.map_price, self.mrp_price, 
        self.quantity, self.quantity_nj, self.quantity_fl,
        self.eta, self.eta_nj, self.eta_fl,
        self.shipping_weight, self.shipping_dimensions,
        json.dumps(self.props) if self.props else None, 
        self.status
    ))
    self.id = cursor.lastrowid
    conn.commit()
    conn.close()
    return self.id

def update(self):
    """Update the vendor product in the database"""
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE vendor_products
    SET vendor_id = ?, master_product_id = ?, vendor_sku = ?, vendor_price = ?,
        list_price = ?, map_price = ?, mrp_price = ?,
        quantity = ?, quantity_nj = ?, quantity_fl = ?,
        eta = ?, eta_nj = ?, eta_fl = ?,
        shipping_weight = ?, shipping_dimensions = ?, props = ?, status = ?
    WHERE id = ?
    ''', (
        self.vendor_id, self.master_product_id, self.vendor_sku, self.vendor_price,
        self.list_price, self.map_price, self.mrp_price,
        self.quantity, self.quantity_nj, self.quantity_fl,
        self.eta, self.eta_nj, self.eta_fl,
        self.shipping_weight, self.shipping_dimensions,
        json.dumps(self.props) if self.props else None,
        self.status, self.id
    ))
    conn.commit()
    conn.close()

def delete(self):
    """Delete the vendor product from the database"""
    conn = self.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vendor_products WHERE id = ?', (self.id,))
    conn.commit()
    conn.close()

@classmethod
def bulk_insert(cls, vendor_id, products_data, batch_size=1000):
    """
    Bulk insert vendor products
    
    products_data: List of dictionaries containing product data
    batch_size: Number of products to insert in a single batch
    """
    if not products_data:
        return 0
        
    conn = cls.get_connection()
    cursor = conn.cursor()
    
    # Process products in batches
    total_inserted = 0
    for i in range(0, len(products_data), batch_size):
        batch = products_data[i:i+batch_size]
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
            
            values.append((
                vendor_id, None, vendor_sku, vendor_price, list_price, map_price, mrp_price,
                qty, qty_nj, qty_fl, eta, eta_nj, eta_fl, weight, dimensions,
                json.dumps(props) if props else None, 'active'
            ))
        
        # Perform bulk insert
        cursor.executemany('''
        INSERT OR REPLACE INTO vendor_products (
            vendor_id, master_product_id, vendor_sku, vendor_price, list_price,
            map_price, mrp_price, quantity, quantity_nj, quantity_fl,
            eta, eta_nj, eta_fl, shipping_weight, shipping_dimensions, props, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', values)
        
        total_inserted += len(batch)
        
    conn.commit()
    conn.close()
    
    return total_inserted