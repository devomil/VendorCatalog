from models.base import BaseModel
from config.settings import get_setting

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
        
        db_type = get_setting('database.type', 'sqlite')
        
        if db_type == 'postgresql':
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendors (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                contact_info TEXT,
                status TEXT DEFAULT 'active'
            )
            ''')
        else:
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
        db_type = get_setting('database.type', 'sqlite')
        
        if db_type == 'postgresql':
            cursor.execute('''
            INSERT INTO vendors (name, description, contact_info, status)
            VALUES (%s, %s, %s, %s) RETURNING id
            ''', (self.name, self.description, self.contact_info, self.status))
            self.id = cursor.fetchone()[0]
        else:
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
        db_type = get_setting('database.type', 'sqlite')
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        cursor.execute(f'''
        UPDATE vendors
        SET name = {placeholder}, description = {placeholder}, contact_info = {placeholder}, status = {placeholder}
        WHERE id = {placeholder}
        ''', (self.name, self.description, self.contact_info, self.status, self.id))
        conn.commit()
        conn.close()
    
    def delete(self):
        """Delete the vendor from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        db_type = get_setting('database.type', 'sqlite')
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        cursor.execute(f'DELETE FROM vendors WHERE id = {placeholder}', (self.id,))
        conn.commit()
        conn.close()
    
    @classmethod
    def find_by_name(cls, name):
        """Find vendors by name (partial match)"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        db_type = get_setting('database.type', 'sqlite')
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        cursor.execute(f"SELECT * FROM vendors WHERE name LIKE {placeholder}", (f"%{name}%",))
        rows = cursor.fetchall()
        conn.close()
        return rows