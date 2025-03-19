import tkinter as tk
from tkinter import ttk, messagebox

class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Vendor and Product Catalog")
        self.root.geometry("1024x768")
        
        # Set up the main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Set up the status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize tabs
        self.create_vendors_tab()
        self.create_products_tab()
        self.create_master_catalog_tab()
        self.create_import_tab()
        
    def create_vendors_tab(self):
        """Create the vendors tab"""
        from views.vendor_view import VendorFrame
        vendors_frame = VendorFrame(self.notebook)
        self.notebook.add(vendors_frame, text="Vendors")
        
    def create_products_tab(self):
        """Create the products tab"""
        products_frame = ttk.Frame(self.notebook)
        self.notebook.add(products_frame, text="Products")
        
        # Placeholder - we'll implement this tab later
        ttk.Label(products_frame, text="Products tab content will go here").pack(expand=True)
        
    def create_master_catalog_tab(self):
        """Create the master catalog tab"""
        master_frame = ttk.Frame(self.notebook)
        self.notebook.add(master_frame, text="Master Catalog")
        
        # Placeholder - we'll implement this tab later
        ttk.Label(master_frame, text="Master catalog content will go here").pack(expand=True)
        
    def create_import_tab(self):
        """Create the import tab"""
        from views.import_view import ImportFrame
        import_frame = ImportFrame(self.notebook)
        self.notebook.add(import_frame, text="Import", padding=5)
        # Force update to show content
        self.root.update_idletasks()
        
    def set_status(self, message):
        """Set the status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()