from models.base import BaseModel

class Vendor(BaseModel):
    """Model representing a vendor"""
    
    table_name = "vendors"
    
    def __init__(self, id=None, name=None, description=None, contact_info=None, status="active"):
        self.id = id
        self.name = name
        self.description = description
        self.contact_info = contact_info
        self.status = status
    
    @classmethod
    def create_table(cls):
        """Create the vendors table if it doesn't exist"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            contact_info TEXT,
            status TEXT DEFAULT 'active'
        )
        ''')
        conn.commit()
        conn.close()
    
    def save(self):
        """Save the vendor to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO vendors (name, description, contact_info, status)
        VALUES (?, ?, ?, ?)
        ''', (self.name, self.description, self.contact_info, self.status))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.id
    
    def update(self):
        """Update the vendor in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE vendors
        SET name = ?, description = ?, contact_info = ?, status = ?
        WHERE id = ?
        ''', (self.name, self.description, self.contact_info, self.status, self.id))
        conn.commit()
        conn.close()
    
    def delete(self):
        """Delete the vendor from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vendors WHERE id = ?', (self.id,))
        conn.commit()
        conn.close()
    
    @classmethod
    def find_by_name(cls, name):
        """Find vendors by name (partial match)"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors WHERE name LIKE ?", (f"%{name}%",))
        rows = cursor.fetchall()
        conn.close()
        return rows