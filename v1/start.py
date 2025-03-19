#!/usr/bin/env python3
"""
VendorCatalog Startup Script

This script handles startup tasks such as database initialization before
launching the main application.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import traceback

def check_dependencies():
    """Check for required Python dependencies"""
    required_packages = ['psycopg2', 'tkinter']
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install the missing packages with pip:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_database_connection():
    """Check database connection"""
    try:
        # Import settings
        from config.settings import initialize_settings, get_setting
        
        # Initialize settings
        initialize_settings()
        
        # Check database type
        db_type = get_setting('database.type')
        if db_type == 'postgresql':
            # Import psycopg2
            import psycopg2
            
            # Get connection parameters
            db_host = get_setting('database.host')
            db_port = get_setting('database.port')
            db_name = get_setting('database.name')
            db_user = get_setting('database.user')
            db_password = get_setting('database.password')
            
            # Try to connect
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name
            )
            
            # Test the connection
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            print(f"Connected to PostgreSQL: {version}")
        else:
            # SQLite - no connection test needed
            print(f"Using SQLite database")
        
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        traceback.print_exc()
        return False

def initialize_database():
    """Initialize the database tables"""
    try:
        # Import controllers
        from controllers.vendor_controller import VendorController
        from controllers.product_controller import ProductController
        from controllers.connection_controller import ConnectionController
        from controllers.master_product_controller import MasterProductController
        
        # Initialize database tables
        print("Initializing database tables...")
        VendorController.initialize_database()
        ProductController.initialize_database()
        ConnectionController.initialize_database()
        MasterProductController.initialize_database()
        
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Database initialization failed: {e}")
        traceback.print_exc()
        return False

def launch_application():
    """Launch the main application"""
    try:
        # Import main components
        from views.main_window import MainWindow
        
        # Create and start the application GUI
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()
        
        return True
    except Exception as e:
        print(f"Application launch failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("VendorCatalog Startup")
    print("====================\n")
    
    # Check dependencies
    if not check_dependencies():
        print("\nMissing dependencies. Please install required packages.")
        return
    
    # Check database connection
    if not check_database_connection():
        print("\nDatabase connection failed. Please check your database settings.")
        
        if tk._default_root is None:
            root = tk.Tk()
            root.withdraw()
        
        messagebox.showerror(
            "Database Error",
            "Could not connect to the database. Please run the PostgreSQL setup script first."
        )
        
        return
    
    # Initialize database
    if not initialize_database():
        print("\nDatabase initialization failed. Application cannot start.")
        
        if tk._default_root is None:
            root = tk.Tk()
            root.withdraw()
        
        messagebox.showerror(
            "Database Error",
            "Could not initialize the database. Please check error logs."
        )
        
        return
    
    # Launch application
    print("\nStarting VendorCatalog application...\n")
    launch_application()

if __name__ == "__main__":
    main() 