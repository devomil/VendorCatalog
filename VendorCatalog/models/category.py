from models.base import BaseModel

class Category(BaseModel):
    """Model representing a product category"""
    
    table_name = "categories"
    
    def __init__(self, id=None, name=None, parent_id=None, description=None, status="active"):
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.description = description
        self.status = status
    
    @classmethod
    def create_table(cls):
        """Create the categories table if it doesn't exist"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER,
            description TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (parent_id) REFERENCES categories (id)
        )
        ''')
        conn.commit()
        conn.close()
    
    def save(self):
        """Save the category to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO categories (name, parent_id, description, status)
        VALUES (?, ?, ?, ?)
        ''', (self.name, self.parent_id, self.description, self.status))
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.id