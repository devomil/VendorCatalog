import os
import sqlite3
import psycopg2
from config.settings import get_setting, DATABASE_PATH

class BaseModel:
    """Base model providing common functionality for all models"""
    
    table_name = None
    
    @classmethod
    def get_connection(cls):
        """Get a database connection based on configuration"""
        db_type = get_setting('database.type', 'sqlite')
        
        if db_type == 'postgresql':
            # PostgreSQL connection
            return psycopg2.connect(
                host=get_setting('database.host', 'localhost'),
                port=get_setting('database.port', 5432),
                database=get_setting('database.name', 'vendor_catalog'),
                user=get_setting('database.user', 'postgres'),
                password=get_setting('database.password', '')
            )
        else:
            # SQLite connection (default)
            os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
            return sqlite3.connect(DATABASE_PATH)
    
    @classmethod
    def create_table(cls):
        """Create the table if it doesn't exist"""
        raise NotImplementedError("Subclasses must implement create_table()")
    
    @classmethod
    def find_by_id(cls, id):
        """Find a record by ID"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        db_type = get_setting('database.type', 'sqlite')
        placeholder = '%s' if db_type == 'postgresql' else '?'
        
        cursor.execute(f"SELECT * FROM {cls.table_name} WHERE id = {placeholder}", (id,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def find_all(cls):
        """Find all records"""
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {cls.table_name}")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def save(self):
        """Save the record to the database"""
        raise NotImplementedError("Subclasses must implement save()")
    
    def update(self):
        """Update the record in the database"""
        raise NotImplementedError("Subclasses must implement update()")
    
    def delete(self):
        """Delete the record from the database"""
        raise NotImplementedError("Subclasses must implement delete()")