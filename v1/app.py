#!/usr/bin/env python3
"""
Vendor and Product Catalog Application

A comprehensive application for managing vendors, products, and their connections.
"""

import sys
import os
from config.settings import initialize_settings
from utils.db_factory import DatabaseFactory
from views.main_window import MainWindow
import tkinter as tk

def main():
    """Main application entry point"""
    
    # Initialize settings
    initialize_settings()
    
    # Initialize database tables using the factory
    # This automatically uses the configured database type (SQLite or PostgreSQL)
    DatabaseFactory.initialize_database()
    
    # Create and start the application GUI
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()