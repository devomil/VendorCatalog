"""
PostgreSQL-specific implementation of the Vendor model
"""

import sys
import os
import psycopg2
from psycopg2 import sql

class VendorPostgres:
    """PostgreSQL implementation of the Vendor model"""
    
    table_name = "vendors"
    
    def __init__(self, id=None, name=None, description=None, contact_info=None, status="active"):
        self.id = id
        self.name = name
        self.description = description
        self.contact_info = contact_info
        self.status = status
        
        # PostgreSQL connection parameters
        self.db_host = "localhost"
        self.db_port = 5432
        self.db_name = "vendor_catalog"
        self.db_user = "vendor_user"  # The designated app user
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
        """Create the vendors table if it doesn't exist"""
        vendor = cls()  # Create instance to access connection method
        conn = vendor.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            contact_info TEXT,
            status TEXT DEFAULT 'active'
        )
        ''')
        conn.commit()
        conn.close()
        print("Vendor table created or already exists")
    
    def save(self):
        """Save the vendor to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO vendors (name, description, contact_info, status)
        VALUES (%s, %s, %s, %s) RETURNING id
        ''', (self.name, self.description, self.contact_info, self.status))
        self.id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return self.id
    
    def update(self):
        """Update the vendor in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE vendors
        SET name = %s, description = %s, contact_info = %s, status = %s
        WHERE id = %s
        ''', (self.name, self.description, self.contact_info, self.status, self.id))
        conn.commit()
        conn.close()
    
    def delete(self):
        """Delete the vendor from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vendors WHERE id = %s', (self.id,))
        conn.commit()
        conn.close()
    
    @classmethod
    def find_by_id(cls, id):
        """Find a vendor by ID"""
        vendor = cls()  # Create instance to access connection method
        conn = vendor.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors WHERE id = %s", (id,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_by_name(cls, name):
        """Find vendors by name (partial match)"""
        vendor = cls()  # Create instance to access connection method
        conn = vendor.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors WHERE name LIKE %s", (f"%{name}%",))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @classmethod
    def find_all(cls):
        """Find all vendors"""
        vendor = cls()  # Create instance to access connection method
        conn = vendor.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @staticmethod
    def test_postgres_integration():
        """Test PostgreSQL integration with vendors"""
        try:
            print("Testing PostgreSQL integration with vendors...")
            
            # Create table
            VendorPostgres.create_table()
            
            # Create vendors
            vendor1 = VendorPostgres(
                name="Acme Corporation", 
                description="A global manufacturer of everything", 
                contact_info="contact@acme.com"
            )
            vendor1_id = vendor1.save()
            print(f"Created vendor with ID: {vendor1_id}")
            
            vendor2 = VendorPostgres(
                name="Tech Solutions Inc", 
                description="Technology products and services", 
                contact_info="info@techsolutions.com"
            )
            vendor2_id = vendor2.save()
            print(f"Created vendor with ID: {vendor2_id}")
            
            # Retrieve vendors
            all_vendors = VendorPostgres.find_all()
            print(f"All vendors: {all_vendors}")
            
            # Update vendor
            vendor1 = VendorPostgres(
                id=vendor1_id,
                name="Acme Corp", 
                description="A global manufacturer of innovative products", 
                contact_info="sales@acme.com"
            )
            vendor1.update()
            print(f"Updated vendor: {VendorPostgres.find_by_id(vendor1_id)}")
            
            # Search vendors
            tech_vendors = VendorPostgres.find_by_name("Tech")
            print(f"Tech vendors: {tech_vendors}")
            
            # Delete vendor
            vendor2 = VendorPostgres(id=vendor2_id)
            vendor2.delete()
            print(f"Deleted vendor ID: {vendor2_id}")
            
            # Verify deletion
            all_vendors_after_delete = VendorPostgres.find_all()
            print(f"All vendors after deletion: {all_vendors_after_delete}")
            
            print("PostgreSQL integration test completed successfully!")
            return True
        except Exception as e:
            print(f"Error testing PostgreSQL integration: {e}")
            import traceback
            traceback.print_exc()
            return False

# Run the test if this file is executed directly
if __name__ == "__main__":
    VendorPostgres.test_postgres_integration() 