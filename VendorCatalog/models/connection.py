from models.base import BaseModel

class Connection(BaseModel):
    """Model representing a connection to a vendor"""
    
    table_name = "connections"
    
    CONNECTION_TYPES = ["sftp", "ftp", "api", "edi", "rest", "soap", "other"]
    
    def __init__(self, id=None, vendor_id=None, name=None, conn_type=None, config=None, status="active"):
        self.id = id
        self.vendor_id = vendor_id
        self.name = name
        self.conn_type = conn_type
        self.config = config  # JSON string containing connection details
        self.status = status
    
    @classmethod
    def create_table(cls):
        """Create the connections table if it doesn't exist"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            conn_type TEXT NOT NULL,
            config TEXT,  -- JSON string
            status TEXT DEFAULT 'active',
            FOREIGN KEY (vendor_id) REFERENCES vendors (id)
        )
        ''')
        conn.commit()
        conn.close()
    
    def save(self):
        """Save the connection to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO connections (vendor_id, name, conn_type, config, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (self.vendor_id, self.name, self.conn_type, self.config, self.status))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.id
    
    def update(self):
        """Update the connection in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE connections
        SET vendor_id = ?, name = ?, conn_type = ?, config = ?, status = ?
        WHERE id = ?
        ''', (self.vendor_id, self.name, self.conn_type, self.config, self.status, self.id))
        conn.commit()
        conn.close()
    
    def delete(self):
        """Delete the connection from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM connections WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()