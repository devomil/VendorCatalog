#!/usr/bin/env python3
"""
Fix the vendor_products table structure
"""

import psycopg2
import sys
import os
import traceback

def get_connection():
    """Get a PostgreSQL database connection"""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        user="vendor_user",
        password="vendor_pass",
        database="vendor_catalog"
    )

def check_table_structure():
    """Check the structure of the vendor_products table"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'vendor_products'")
        table_exists = cursor.fetchone() is not None
        
        print(f"Table vendor_products exists: {table_exists}")
        
        if table_exists:
            # Get column information
            cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'vendor_products'
            ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("\nColumns in vendor_products table:")
            for col in columns:
                print(f"{col[0]}: {col[1]}, Default: {col[2]}")
        
    except Exception as e:
        print(f"Error checking table structure: {e}")
        traceback.print_exc()
    finally:
        conn.close()

def recreate_table():
    """Drop and recreate the vendor_products table"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Drop existing table
        cursor.execute("DROP TABLE IF EXISTS vendor_products CASCADE")
        conn.commit()
        print("Dropped vendor_products table")
        
        # Create sequence
        cursor.execute("DROP SEQUENCE IF EXISTS vendor_products_id_seq")
        conn.commit()
        cursor.execute("CREATE SEQUENCE vendor_products_id_seq")
        conn.commit()
        print("Created vendor_products_id_seq")
        
        # Create table
        cursor.execute('''
        CREATE TABLE vendor_products (
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
            props TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (vendor_id) REFERENCES vendors (id)
        )
        ''')
        conn.commit()
        print("Created vendor_products table")
        
        # Add indexes
        cursor.execute('CREATE INDEX idx_vendor_products_vendor_id ON vendor_products (vendor_id)')
        cursor.execute('CREATE INDEX idx_vendor_products_master_product_id ON vendor_products (master_product_id)')
        conn.commit()
        print("Created indexes")
        
        # Add unique constraint
        cursor.execute('ALTER TABLE vendor_products ADD CONSTRAINT vendor_products_vendor_id_vendor_sku_key UNIQUE (vendor_id, vendor_sku)')
        conn.commit()
        print("Added unique constraint")
        
        print("Table recreation completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Error recreating table: {e}")
        traceback.print_exc()
    finally:
        conn.close()

def main():
    """Main function"""
    print("Checking vendor_products table structure before fix...\n")
    check_table_structure()
    
    # Automatically recreate the table
    print("\nRecreating vendor_products table...")
    recreate_table()
    
    print("\nChecking new table structure...\n")
    check_table_structure()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 