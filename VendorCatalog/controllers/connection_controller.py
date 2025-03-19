import json
from models.connection import Connection

class ConnectionController:
    """Controller for connection-related operations"""
    
    @staticmethod
    def initialize_database():
        """Initialize the database tables"""
        Connection.create_table()
    
    @staticmethod
    def create_connection(vendor_id, name, conn_type, config_dict=None):
        """
        Create a new connection
        config_dict: Dictionary with connection configuration
        """
        # Convert config dict to JSON string
        config = json.dumps(config_dict) if config_dict else None
        
        connection = Connection(
            vendor_id=vendor_id,
            name=name,
            conn_type=conn_type,
            config=config
        )
        connection_id = connection.save()
        return connection_id
    
    @staticmethod
    def update_connection(connection_id, vendor_id=None, name=None, conn_type=None, config_dict=None, status=None):
        """Update an existing connection"""
        # Get current connection data
        connection_data = Connection.find_by_id(connection_id)
        if not connection_data:
            return False
            
        # Parse existing config if it exists
        existing_config = None
        if connection_data[4]:
            try:
                existing_config = json.loads(connection_data[4])
            except json.JSONDecodeError:
                existing_config = {}
        
        # Merge with new config if provided
        if config_dict and existing_config:
            merged_config = {**existing_config, **config_dict}
            config_json = json.dumps(merged_config)
        elif config_dict:
            config_json = json.dumps(config_dict)
        else:
            config_json = connection_data[4]
        
        # Create connection object with current data
        connection = Connection(
            id=connection_id,
            vendor_id=connection_data[1] if vendor_id is None else vendor_id,
            name=connection_data[2] if name is None else name,
            conn_type=connection_data[3] if conn_type is None else conn_type,
            config=config_json,
            status=connection_data[5] if status is None else status
        )
        
        connection.update()
        return True
    
    @staticmethod
    def delete_connection(connection_id):
        """Delete a connection"""
        connection = Connection(id=connection_id)
        connection.delete()
        return True
    
    @staticmethod
    def get_connection(connection_id):
        """Get a connection by ID"""
        return Connection.find_by_id(connection_id)
    
    @staticmethod
    def get_connection_types():
        """Get list of available connection types"""
        return Connection.CONNECTION_TYPES