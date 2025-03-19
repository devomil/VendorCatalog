#!/usr/bin/env python3
"""
Check and fix the vendor_products table structure
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
            
            # Check for primary key
            cursor.execute("""
            SELECT c.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
            JOIN information_schema.columns AS c 
                ON c.table_schema = tc.constraint_schema
                AND c.table_name = tc.table_name
                AND c.column_name = ccu.column_name
            WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_name = 'vendor_products'
            """)
            
            pk = cursor.fetchone()
            if pk:
                print(f"\nPrimary key column: {pk[0]}")
            else:
                print("\nNo primary key found!")
            
            # Check for foreign keys
            cursor.execute("""
            SELECT tc.constraint_name, kcu.column_name, ccu.table_name AS foreign_table_name,
                   ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'vendor_products'
            """)
            
            fks = cursor.fetchall()
            if fks:
                print("\nForeign keys:")
                for fk in fks:
                    print(f"{fk[0]}: {fk[1]} references {fk[2]}.{fk[3]}")
            else:
                print("\nNo foreign keys found!")
            
            # Try to query the table
            try:
                cursor.execute("SELECT * FROM vendor_products LIMIT 5")
                rows = cursor.fetchall()
                print(f"\nSample data (first {len(rows)} rows):")
                for row in rows:
                    print(row)
            except Exception as e:
                print(f"\nError querying table: {e}")
        
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
        cursor.execute("CREATE SEQUENCE IF NOT EXISTS vendor_products_id_seq")
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
    print("Checking vendor_products table structure...\n")
    check_table_structure()
    
    answer = input("\nDo you want to recreate the table? (y/n): ")
    if answer.lower() == 'y':
        recreate_table()
        print("\nChecking new table structure...\n")
        check_table_structure()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 