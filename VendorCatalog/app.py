#!/usr/bin/env python3
"""
Vendor and Product Catalog Application

A comprehensive application for managing vendors, products, and their connections.
"""

import sys
import os
from config.settings import initialize_settings
from controllers.vendor_controller import VendorController
from controllers.product_controller import ProductController
from controllers.connection_controller import ConnectionController
from controllers.master_product_controller import MasterProductController
from controllers.import_controller import ImportController
from views.main_window import MainWindow
import tkinter as tk

def main():
    """Main application entry point"""
    
    # Initialize settings
    initialize_settings()
    
    # Initialize database tables
    VendorController.initialize_database()
    ProductController.initialize_database()
    ConnectionController.initialize_database()
    MasterProductController.initialize_database()
    
    # Create and start the application GUI
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()