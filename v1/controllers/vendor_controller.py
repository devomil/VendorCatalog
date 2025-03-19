from models.vendor import Vendor
from models.connection import Connection

class VendorController:
    """Controller for vendor-related operations"""
    
    @staticmethod
    def initialize_database():
        """Initialize the database tables"""
        Vendor.create_table()
    
    @staticmethod
    def create_vendor(name, description=None, contact_info=None):
        """Create a new vendor"""
        vendor = Vendor(name=name, description=description, contact_info=contact_info)
        vendor_id = vendor.save()
        return vendor_id
    
    @staticmethod
    def update_vendor(vendor_id, name=None, description=None, contact_info=None, status=None):
        """Update an existing vendor"""
        # Get current vendor data
        vendor_data = Vendor.find_by_id(vendor_id)
        if not vendor_data:
            return False
            
        # Create vendor object with current data
        vendor = Vendor(
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
        vendor = Vendor(id=vendor_id)
        vendor.delete()
        return True
    
    @staticmethod
    def get_vendor(vendor_id):
        """Get a vendor by ID"""
        return Vendor.find_by_id(vendor_id)
    
    @staticmethod
    def search_vendors(search_term):
        """Search vendors by name"""
        return Vendor.find_by_name(search_term)
    
    @staticmethod
    def get_all_vendors():
        """Get all vendors"""
        return Vendor.find_all()