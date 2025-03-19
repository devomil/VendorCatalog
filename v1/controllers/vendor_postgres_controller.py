"""
PostgreSQL-specific implementation of the Vendor Controller
"""

import sys
import os

# Add the parent directory to sys.path to allow importing from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.vendor_postgres import VendorPostgres

class VendorPostgresController:
    """Controller for vendor-related operations using PostgreSQL"""
    
    @staticmethod
    def initialize_database():
        """Initialize the database tables"""
        VendorPostgres.create_table()
    
    @staticmethod
    def create_vendor(name, description=None, contact_info=None):
        """Create a new vendor"""
        vendor = VendorPostgres(name=name, description=description, contact_info=contact_info)
        vendor_id = vendor.save()
        return vendor_id
    
    @staticmethod
    def update_vendor(vendor_id, name=None, description=None, contact_info=None, status=None):
        """Update an existing vendor"""
        # Get current vendor data
        vendor_data = VendorPostgres.find_by_id(vendor_id)
        if not vendor_data:
            return False
            
        # Create vendor object with current data
        vendor = VendorPostgres(
            id=vendor_id,
            name=vendor_data[1] if name is None else name,
            description=vendor_data[2] if description is None else description,
            contact_info=vendor_data[3] if contact_info is None else contact_info,
            status=vendor_data[4] if status is None else status
        )
        
        vendor.update()
        return True
    
    @staticmethod
    def delete_vendor(vendor_id):
        """Delete a vendor"""
        vendor = VendorPostgres(id=vendor_id)
        vendor.delete()
        return True
    
    @staticmethod
    def get_vendor(vendor_id):
        """Get a vendor by ID"""
        return VendorPostgres.find_by_id(vendor_id)
    
    @staticmethod
    def search_vendors(search_term):
        """Search vendors by name"""
        return VendorPostgres.find_by_name(search_term)
    
    @staticmethod
    def get_all_vendors():
        """Get all vendors"""
        return VendorPostgres.find_all()
    
    @staticmethod
    def test_controller():
        """Test the controller functionality"""
        try:
            print("Testing VendorPostgresController...")
            
            # Initialize database
            VendorPostgresController.initialize_database()
            print("Database initialized.")
            
            # Create vendor
            vendor_id = VendorPostgresController.create_vendor(
                name="PostgreSQL Test Vendor",
                description="A vendor for testing PostgreSQL",
                contact_info="test@postgres.com"
            )
            print(f"Created vendor with ID: {vendor_id}")
            
            # Get vendor
            vendor = VendorPostgresController.get_vendor(vendor_id)
            print(f"Retrieved vendor: {vendor}")
            
            # Update vendor
            VendorPostgresController.update_vendor(
                vendor_id,
                name="Updated PostgreSQL Vendor",
                description="An updated vendor for testing",
                contact_info="updated@postgres.com"
            )
            print("Vendor updated.")
            
            # Get updated vendor
            updated_vendor = VendorPostgresController.get_vendor(vendor_id)
            print(f"Updated vendor: {updated_vendor}")
            
            # Search vendors
            search_results = VendorPostgresController.search_vendors("PostgreSQL")
            print(f"Search results: {search_results}")
            
            # Get all vendors
            all_vendors = VendorPostgresController.get_all_vendors()
            print(f"All vendors count: {len(all_vendors)}")
            
            # Delete vendor
            VendorPostgresController.delete_vendor(vendor_id)
            print(f"Deleted vendor ID: {vendor_id}")
            
            # Verify deletion
            all_vendors_after_delete = VendorPostgresController.get_all_vendors()
            print(f"All vendors after deletion: {len(all_vendors_after_delete)}")
            
            print("VendorPostgresController test completed successfully!")
            return True
        except Exception as e:
            print(f"Error testing VendorPostgresController: {e}")
            import traceback
            traceback.print_exc()
            return False

# Run the test if this file is executed directly
if __name__ == "__main__":
    VendorPostgresController.test_controller() 