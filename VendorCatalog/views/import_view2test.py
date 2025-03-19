#!/usr/bin/env python3
"""
Import View Module

Provides the UI for importing vendor product catalogs from various sources.
"""
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
import json
import threading
import logging
from typing import Dict, List, Any, Optional, Callable

from controllers.import_controller import ImportController
from controllers.vendor_controller import VendorController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Constants for reuse
UI_PADDING = 10
DEFAULT_FONT = ("TkDefaultFont", 14, "bold")

class ImportFrame(ttk.Frame):
    """View for importing vendor product catalogs"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.import_in_progress = False
        self.logger = logging.getLogger("ImportView")  # Initialize logger
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components"""
        # Main frame
        self.pack(fill=tk.BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)
        
        # Title
        title_label = ttk.Label(self, text="Import Vendor Products", font=DEFAULT_FONT)
        title_label.pack(pady=(0, UI_PADDING))
        
        # Vendor selection frame
        vendor_frame = ttk.LabelFrame(self, text="Select Vendor")
        vendor_frame.pack(fill=tk.X, pady=UI_PADDING)
        
        # Create vendor dropdown - we'll populate it in refresh_vendors()
        self.vendors = []
        self.vendor_names = []
        self.vendor_var = tk.StringVar()
        
        self.vendor_dropdown = ttk.Combobox(vendor_frame, textvariable=self.vendor_var, state="readonly")
        self.vendor_dropdown.pack(fill=tk.X, padx=UI_PADDING, pady=UI_PADDING)
        
        # Refresh button for vendors
        refresh_btn = ttk.Button(vendor_frame, text="Refresh Vendors", command=self.refresh_vendors)
        refresh_btn.pack(side=tk.RIGHT, padx=UI_PADDING, pady=(0, UI_PADDING))
        
        # Initial population of vendors
        self.refresh_vendors()
        
        # Notebook for different import methods
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=UI_PADDING)
        
        # File import tab
        self.file_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.file_frame, text="File Import")
        self.setup_file_import_ui()
        
        # API import tab
        self.api_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.api_frame, text="API Import")
        self.setup_api_import_ui()
        
        # SFTP import tab
        self.sftp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sftp_frame, text="SFTP Import")
        self.setup_sftp_import_ui()
        
        # EDI import tab
        self.edi_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.edi_frame, text="EDI Import")
        self.setup_edi_import_ui()
        
        # Field mapping tab
        self.mapping_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mapping_frame, text="Field Mapping")
        self.setup_mapping_ui()
        
        # Import status frame
        status_frame = ttk.LabelFrame(self, text="Import Status")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=UI_PADDING)
        
        # Status text widget
        self.status_text = tk.Text(status_frame, height=10, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.status_text.config(state=tk.DISABLED)
        
        # Scrollbar for status text
        status_scrollbar = ttk.Scrollbar(self.status_text, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=(0, 5))
    
    def setup_file_import_ui(self):
        """Set up the UI for file imports"""
        
        # File selection
        file_select_frame = ttk.Frame(self.file_frame)
        file_select_frame.pack(fill=tk.X, padx=UI_PADDING, pady=UI_PADDING)
        
        ttk.Label(file_select_frame, text="File:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=50)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(file_select_frame, text="Browse...", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT)
        
        # Import button
        import_btn = ttk.Button(self.file_frame, text="Import File", command=self.import_file)
        import_btn.pack(pady=UI_PADDING)
    
    def setup_api_import_ui(self):
        """Set up the UI for API imports"""
        
        # API configuration frame
        api_config_frame = ttk.Frame(self.api_frame)
        api_config_frame.pack(fill=tk.BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)
        
        # URL
        url_frame = ttk.Frame(api_config_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="URL:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.api_url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.api_url_var, width=50)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Authentication frame
        auth_frame = ttk.LabelFrame(api_config_frame, text="Authentication")
        auth_frame.pack(fill=tk.X, pady=5)
        
        # Authentication type
        auth_type_frame = ttk.Frame(auth_frame)
        auth_type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(auth_type_frame, text="Type:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.auth_type_var = tk.StringVar(value="None")
        auth_types = ["None", "Basic Auth", "Bearer Token", "API Key"]
        auth_type_combo = ttk.Combobox(auth_type_frame, textvariable=self.auth_type_var, 
                                       values=auth_types, state="readonly")
        auth_type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        auth_type_combo.bind("<<ComboboxSelected>>", self.on_auth_type_change)
        
        # Auth details container (will be populated based on auth type)
        self.auth_details_frame = ttk.Frame(auth_frame)
        self.auth_details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Headers frame
        headers_frame = ttk.LabelFrame(api_config_frame, text="Headers")
        headers_frame.pack(fill=tk.X, pady=5)
        
        # Headers text (JSON format)
        self.headers_text = tk.Text(headers_frame, height=5, wrap=tk.WORD)
        self.headers_text.pack(fill=tk.X, padx=5, pady=5)
        self.headers_text.insert(tk.END, "{\n  \"Content-Type\": \"application/json\"\n}")
        
        # Pagination frame
        pagination_frame = ttk.LabelFrame(api_config_frame, text="Pagination (Optional)")
        pagination_frame.pack(fill=tk.X, pady=5)
        
        # Paginated checkbox
        self.is_paginated_var = tk.BooleanVar(value=False)
        paginated_check = ttk.Checkbutton(pagination_frame, text="API uses pagination", 
                                          variable=self.is_paginated_var)
        paginated_check.pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        # Items path
        items_path_frame = ttk.Frame(pagination_frame)
        items_path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(items_path_frame, text="Items Path:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.items_path_var = tk.StringVar(value="data.items")
        items_path_entry = ttk.Entry(items_path_frame, textvariable=self.items_path_var)
        items_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Next page path
        next_page_frame = ttk.Frame(pagination_frame)
        next_page_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(next_page_frame, text="Next Page Path:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.next_page_var = tk.StringVar(value="meta.next_page_url")
        next_page_entry = ttk.Entry(next_page_frame, textvariable=self.next_page_var)
        next_page_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Import button
        import_btn = ttk.Button(self.api_frame, text="Import from API", command=self.import_from_api)
        import_btn.pack(pady=UI_PADDING)
    
    def setup_sftp_import_ui(self):
        """Set up the UI for SFTP imports"""
        
        # SFTP configuration frame
        sftp_config_frame = ttk.Frame(self.sftp_frame)
        sftp_config_frame.pack(fill=tk.BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)
        
        # Host
        host_frame = ttk.Frame(sftp_config_frame)
        host_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(host_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.sftp_host_var = tk.StringVar()
        host_entry = ttk.Entry(host_frame, textvariable=self.sftp_host_var)
        host_entry.grid(row=0, column=1, sticky=tk.EW)
        
        # Port
        ttk.Label(host_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        
        self.sftp_port_var = tk.StringVar(value="22")
        port_entry = ttk.Entry(host_frame, textvariable=self.sftp_port_var, width=6)
        port_entry.grid(row=0, column=3, sticky=tk.W)
        
        host_frame.columnconfigure(1, weight=1)
        
        # Username and Password
        credentials_frame = ttk.Frame(sftp_config_frame)
        credentials_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(credentials_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.sftp_username_var = tk.StringVar()
        username_entry = ttk.Entry(credentials_frame, textvariable=self.sftp_username_var)
        username_entry.grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(credentials_frame, text="Password:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        
        self.sftp_password_var = tk.StringVar()
        password_entry = ttk.Entry(credentials_frame, textvariable=self.sftp_password_var, show="*")
        password_entry.grid(row=0, column=3, sticky=tk.EW)
        
        credentials_frame.columnconfigure(1, weight=1)
        credentials_frame.columnconfigure(3, weight=1)
        
        # Multiple Directories
        directories_label_frame = ttk.LabelFrame(sftp_config_frame, text="Directories")
        directories_label_frame.pack(fill=tk.X, pady=5)
        
        # Directory 1
        dir1_frame = ttk.Frame(directories_label_frame)
        dir1_frame.pack(fill=tk.X, pady=(5,2))
        
        ttk.Label(dir1_frame, text="Directory 1:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.sftp_directory1_var = tk.StringVar(value="/")
        directory1_entry = ttk.Entry(dir1_frame, textvariable=self.sftp_directory1_var)
        directory1_entry.grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(dir1_frame, text="Pattern:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        
        self.sftp_pattern1_var = tk.StringVar(value="*.csv")
        pattern1_entry = ttk.Entry(dir1_frame, textvariable=self.sftp_pattern1_var)
        pattern1_entry.grid(row=0, column=3, sticky=tk.EW)
        
        dir1_frame.columnconfigure(1, weight=1)
        dir1_frame.columnconfigure(3, weight=1)
        
        # Directory 2
        dir2_frame = ttk.Frame(directories_label_frame)
        dir2_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(dir2_frame, text="Directory 2:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.sftp_directory2_var = tk.StringVar(value="")
        directory2_entry = ttk.Entry(dir2_frame, textvariable=self.sftp_directory2_var)
        directory2_entry.grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(dir2_frame, text="Pattern:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        
        self.sftp_pattern2_var = tk.StringVar(value="")
        pattern2_entry = ttk.Entry(dir2_frame, textvariable=self.sftp_pattern2_var)
        pattern2_entry.grid(row=0, column=3, sticky=tk.EW)
        
        dir2_frame.columnconfigure(1, weight=1)
        dir2_frame.columnconfigure(3, weight=1)
        
        # Directory 3
        dir3_frame = ttk.Frame(directories_label_frame)
        dir3_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(dir3_frame, text="Directory 3:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.sftp_directory3_var = tk.StringVar(value="")
        directory3_entry = ttk.Entry(dir3_frame, textvariable=self.sftp_directory3_var)
        directory3_entry.grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(dir3_frame, text="Pattern:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        
        self.sftp_pattern3_var = tk.StringVar(value="")
        pattern3_entry = ttk.Entry(dir3_frame, textvariable=self.sftp_pattern3_var)
        pattern3_entry.grid(row=0, column=3, sticky=tk.EW)
        
        dir3_frame.columnconfigure(1, weight=1)
        dir3_frame.columnconfigure(3, weight=1)
        
        # Directory 4
        dir4_frame = ttk.Frame(directories_label_frame)
        dir4_frame.pack(fill=tk.X, pady=(2,5))
        
        ttk.Label(dir4_frame, text="Directory 4:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.sftp_directory4_var = tk.StringVar(value="")
        directory4_entry = ttk.Entry(dir4_frame, textvariable=self.sftp_directory4_var)
        directory4_entry.grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(dir4_frame, text="Pattern:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        
        self.sftp_pattern4_var = tk.StringVar(value="")
        pattern4_entry = ttk.Entry(dir4_frame, textvariable=self.sftp_pattern4_var)
        pattern4_entry.grid(row=0, column=3, sticky=tk.EW)
        
        dir4_frame.columnconfigure(1, weight=1)
        dir4_frame.columnconfigure(3, weight=1)
        
        # Button frame
        button_frame = ttk.Frame(self.sftp_frame)
        button_frame.pack(fill=tk.X, pady=UI_PADDING)
        
        # Test import button
        test_btn = ttk.Button(button_frame, text="Test Import (100 Products)", command=self.test_sftp_import)
        test_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Import button
        import_btn = ttk.Button(button_frame, text="Import from SFTP", command=self.import_from_sftp)
        import_btn.pack(side=tk.LEFT)
    
    def setup_edi_import_ui(self):
        """Set up the UI for EDI imports"""
        
        # EDI input frame
        edi_input_frame = ttk.Frame(self.edi_frame)
        edi_input_frame.pack(fill=tk.BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)
        
        # EDI text area
        ttk.Label(edi_input_frame, text="EDI Data (X12 format):").pack(anchor=tk.W)
        
        edi_text_frame = ttk.Frame(edi_input_frame)
        edi_text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.edi_text = tk.Text(edi_text_frame, height=15, wrap=tk.WORD)
        self.edi_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        edi_scrollbar = ttk.Scrollbar(edi_text_frame, orient=tk.VERTICAL, command=self.edi_text.yview)
        self.edi_text.configure(yscrollcommand=edi_scrollbar.set)
        edi_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load EDI file option
        load_frame = ttk.Frame(edi_input_frame)
        load_frame.pack(fill=tk.X, pady=5)
        
        load_btn = ttk.Button(load_frame, text="Load EDI File", command=self.load_edi_file)
        load_btn.pack(side=tk.LEFT)
        
        # Import button
        import_btn = ttk.Button(self.edi_frame, text="Import EDI Data", command=self.import_from_edi)
        import_btn.pack(pady=UI_PADDING)
    
    def setup_mapping_ui(self):
        """Set up the UI for field mapping"""
        
        # Mapping frame
        mapping_container = ttk.Frame(self.mapping_frame)
        mapping_container.pack(fill=tk.BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)
        
        # Instructions
        ttk.Label(mapping_container, text="Define how source fields map to product fields:").pack(anchor=tk.W, pady=(0, 10))
        
        # Mapping fields
        self.mapping_entries = {}
        product_fields = [
            "sku", "name", "description", "price", "category", 
            "brand", "upc", "weight", "dimensions", "status"
        ]
        
        for i, field in enumerate(product_fields):
            field_frame = ttk.Frame(mapping_container)
            field_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(field_frame, text=f"{field.capitalize()}:", width=12).pack(side=tk.LEFT)
            
            entry_var = tk.StringVar()
            # Set default mapping suggestions
            if field == "sku":
                entry_var.set("sku,product_id,item_number,part_number,id")
            elif field == "name":
                entry_var.set("name,product_name,title,description")
            elif field == "description":
                entry_var.set("description,long_description,details")
            elif field == "price":
                entry_var.set("price,cost,wholesale_price,msrp")
            
            entry = ttk.Entry(field_frame, textvariable=entry_var)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.mapping_entries[field] = entry_var
        
        # Help text
        help_text = ("Enter comma-separated field names from the source file that should map to each product field.\n"
                    "The first matching field will be used.")
        ttk.Label(mapping_container, text=help_text, wraplength=400).pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(mapping_container)
        button_frame.pack(fill=tk.X, pady=10)
        
        save_btn = ttk.Button(button_frame, text="Save Mapping", command=self.save_mapping)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        load_btn = ttk.Button(button_frame, text="Load Mapping", command=self.load_mapping)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_mapping)
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    def update_status(self, message):
        """Update the status text widget"""
        def _update():
            self.status_text.config(state=tk.NORMAL)
            self.status_text.insert(tk.END, message + "\n")
            self.status_text.see(tk.END)
            self.status_text.config(state=tk.DISABLED)
        
        # Use after() method from the parent if we don't have it
        if hasattr(self, 'after'):
            self.after(0, _update)
        else:
            self.parent.after(0, _update)
    
    def refresh_vendors(self):
        """Refresh the vendor dropdown with current data"""
        try:
            # Get all vendors from the database
            vendor_rows = VendorController.get_all_vendors()
            
            # Clear existing vendors
            self.vendors = []
            
            # Process vendor data
            if vendor_rows:
                for row in vendor_rows:
                    self.vendors.append({'id': row[0], 'name': row[1]})
                
                # Update dropdown values
                self.vendor_names = [f"{v['name']} (ID: {v['id']})" for v in self.vendors]
                self.vendor_dropdown['values'] = self.vendor_names
                
                # Set default selection if available
                if self.vendor_names and not self.vendor_var.get():
                    self.vendor_var.set(self.vendor_names[0])
            else:
                # No vendors available
                self.vendor_dropdown['values'] = ["No vendors available"]
                self.vendor_var.set("No vendors available")
            
            self.update_status("Vendor list refreshed")
        except Exception as e:
            self.logger.error(f"Error refreshing vendors: {str(e)}")
            self.update_status(f"Error refreshing vendors: {str(e)}")
    
    def get_selected_vendor_id(self):
        """Get the ID of the selected vendor"""
        vendor_str = self.vendor_var.get()
        
        if not vendor_str or "No vendors available" in vendor_str:
            messagebox.showerror("Error", "No vendor selected. Please add vendors first.")
            raise ValueError("No vendor selected")
            
        try:
            vendor_id = int(vendor_str.split("ID: ")[1].rstrip(")"))
            return vendor_id
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Invalid vendor selection format. Please refresh the vendor list.")
            raise ValueError("Invalid vendor selection format")
    
    def browse_file(self):
        """Open file browser and update file path"""
        filetypes = [
            ("All Supported Files", "*.csv *.xlsx *.xls *.json *.xml"),
            ("CSV Files", "*.csv"),
            ("Excel Files", "*.xlsx *.xls"),
            ("JSON Files", "*.json"),
            ("XML Files", "*.xml"),
            ("All Files", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_path_var.set(filename)
            self.update_status(f"Selected file: {filename}")
    
    def load_edi_file(self):
        """Load EDI file into text area"""
        filetypes = [
            ("EDI Files", "*.edi *.txt"),
            ("All Files", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    edi_content = f.read()
                self.edi_text.delete(1.0, tk.END)
                self.edi_text.insert(tk.END, edi_content)
                self.update_status(f"Loaded EDI file: {filename}")
            except Exception as e:
                self.logger.error(f"Error loading EDI file: {str(e)}")
                messagebox.showerror("Error", f"Error loading EDI file: {str(e)}")
    
    def on_auth_type_change(self, event=None):
        """Update auth details frame based on selected auth type"""
        
        # Clear existing widgets
        for widget in self.auth_details_frame.winfo_children():
            widget.destroy()
        
        auth_type = self.auth_type_var.get()
        
        if auth_type == "Basic Auth":
            # Username and password fields
            ttk.Label(self.auth_details_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            
            self.basic_username_var = tk.StringVar()
            username_entry = ttk.Entry(self.auth_details_frame, textvariable=self.basic_username_var)
            username_entry.grid(row=0, column=1, sticky=tk.EW)
            
            ttk.Label(self.auth_details_frame, text="Password:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
            
            self.basic_password_var = tk.StringVar()
            password_entry = ttk.Entry(self.auth_details_frame, textvariable=self.basic_password_var, show="*")
            password_entry.grid(row=0, column=3, sticky=tk.EW)
            
            self.auth_details_frame.columnconfigure(1, weight=1)
            self.auth_details_frame.columnconfigure(3, weight=1)
            
        elif auth_type == "Bearer Token":
            # Token field
            ttk.Label(self.auth_details_frame, text="Token:").pack(side=tk.LEFT, padx=(0, 5))
            
            self.bearer_token_var = tk.StringVar()
            token_entry = ttk.Entry(self.auth_details_frame, textvariable=self.bearer_token_var)
            token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
        elif auth_type == "API Key":
            # Key name and value fields
            ttk.Label(self.auth_details_frame, text="Key Name:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            
            self.api_key_name_var = tk.StringVar(value="api_key")
            key_name_entry = ttk.Entry(self.auth_details_frame, textvariable=self.api_key_name_var)
            key_name_entry.grid(row=0, column=1, sticky=tk.EW)
            
            ttk.Label(self.auth_details_frame, text="Key Value:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
            
            self.api_key_value_var = tk.StringVar()
            key_value_entry = ttk.Entry(self.auth_details_frame, textvariable=self.api_key_value_var)
            key_value_entry.grid(row=0, column=3, sticky=tk.EW)
            
            self.auth_details_frame.columnconfigure(1, weight=1)
            self.auth_details_frame.columnconfigure(3, weight=1)

    def _build_sftp_configs(self):
        """Build SFTP configurations for all directories"""
        configs = []
        
        try:
            port = int(self.sftp_port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Port must be a number.")
            return []
            
        # Base configuration
        base_config = {
            'host': self.sftp_host_var.get(),
            'port': port,
            'username': self.sftp_username_var.get(),
            'password': self.sftp_password_var.get()
        }
        
        # Add configs for each directory
        if self.sftp_directory1_var.get() and self.sftp_pattern1_var.get():
            config = base_config.copy()
            config['directory'] = self.sftp_directory1_var.get()
            config['file_pattern'] = self.sftp_pattern1_var.get()
            configs.append(config)
        
        if self.sftp_directory2_var.get() and self.sftp_pattern2_var.get():
            config = base_config.copy()
            config['directory'] = self.sftp_directory2_var.get()
            config['file_pattern'] = self.sftp_pattern2_var.get()
            configs.append(config)
        
        if self.sftp_directory3_var.get() and self.sftp_pattern3_var.get():
            config = base_config.copy()
            config['directory'] = self.sftp_directory3_var.get()
            config['file_pattern'] = self.sftp_pattern3_var.get()
            configs.append(config)
            
        if self.sftp_directory4_var.get() and self.sftp_pattern4_var.get():
            config = base_config.copy()
            config['directory'] = self.sftp_directory4_var.get()
            config['file_pattern'] = self.sftp_pattern4_var.get()
            configs.append(config)
        
        return configs

    def import_file(self):
        """Import products from file"""
        if self.import_in_progress:
            self.update_status("Import already in progress")
            return
            
        try:
            vendor_id = self.get_selected_vendor_id()
            file_path = self.file_path_var.get()
            
            if not file_path:
                messagebox.showerror("Error", "Please select a file to import")
                return
                
            # Get field mappings
            mappings = self._get_current_mappings()
            
            self.import_in_progress = True
            self.update_status(f"Starting file import from {file_path}")
            
            # Set progress bar for indeterminate progress
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start(15)
            
            # Run import in a separate thread to keep UI responsive
            threading.Thread(
                target=self._run_import_process,
                args=(
                    lambda: ImportController.import_from_file(vendor_id, file_path, mappings),
                    "File import completed successfully",
                    "Error during file import"
                ),
                daemon=True
            ).start()
        except Exception as e:
            self.logger.error(f"Error in import_file: {str(e)}")
            messagebox.showerror("Error", f"Error starting import: {str(e)}")
            self.import_in_progress = False
            
    def import_from_api(self):
        """Import products from API"""
        if self.import_in_progress:
            self.update_status("Import already in progress")
            return
            
        try:
            vendor_id = self.get_selected_vendor_id()
            api_url = self.api_url_var.get()
            
            if not api_url:
                messagebox.showerror("Error", "Please enter an API URL")
                return
                
            # Get auth configuration
            auth_config = self._get_api_auth_config()
            
            # Get pagination configuration
            pagination_config = None
            if self.is_paginated_var.get():
                pagination_config = {
                    'items_path': self.items_path_var.get(),
                    'next_page_path': self.next_page_var.get()
                }
                
            # Get headers
            try:
                headers = json.loads(self.headers_text.get(1.0, tk.END))
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Headers must be valid JSON")
                return
                
            # Get field mappings
            mappings = self._get_current_mappings()
            
            self.import_in_progress = True
            self.update_status(f"Starting API import from {api_url}")
            
            # Set progress bar for indeterminate progress
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start(15)
            
            # Run import in a separate thread to keep UI responsive
            threading.Thread(
                target=self._run_import_process,
                args=(
                    lambda: ImportController.import_from_api(
                        vendor_id, api_url, auth_config, headers, 
                        pagination_config, mappings
                    ),
                    "API import completed successfully",
                    "Error during API import"
                ),
                daemon=True
            ).start()
        except Exception as e:
            self.logger.error(f"Error in import_from_api: {str(e)}")
            messagebox.showerror("Error", f"Error starting import: {str(e)}")
            self.import_in_progress = False
    
    def import_from_sftp(self):
        """Import products from SFTP"""
        # Implementation similar to other import methods
        pass
        
    def import_from_edi(self):
        """Import products from EDI data"""
        # Implementation similar to other import methods
        pass
    
    def test_sftp_import(self):
        """Test SFTP connection and import a limited number of products"""
        # Implementation for testing SFTP
        pass
    
    def _run_import_process(self, import_func: Callable, success_msg: str, error_msg: str):
        """Run the import process and handle UI updates
        
        Args:
            import_func: The import function to call
            success_msg: Message to display on success
            error_msg: Message prefix for errors
        """
        try:
            result = import_func()
            
            # Update UI on the main thread
            self.parent.after(0, lambda: self._handle_import_result(result, success_msg))
        except Exception as e:
            self.logger.error(f"Import error: {str(e)}")
            # Update UI on the main thread
            self.parent.after(0, lambda: self._handle_import_error(f"{error_msg}: {str(e)}"))
    
    def _handle_import_result(self, result: Dict[str, Any], success_msg: str):
        """Handle successful import results
        
        Args:
            result: Import result dictionary
            success_msg: Success message to display
        """
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')
        self.progress_var.set(100)
        
        # Display result information
        products_imported = result.get('products_imported', 0)
        
        self.update_status(f"{success_msg}")
        self.update_status(f"Products imported: {products_imported}")
        
        if 'warnings' in result and result['warnings']:
            for warning in result['warnings']:
                self.update_status(f"Warning: {warning}")
        
        self.import_in_progress = False
    
    def _handle_import_error(self, error_msg: str):
        """Handle import error
        
        Args:
            error_msg: Error message to display
        """
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')
        self.progress_var.set(0)
        
        self.update_status(error_msg)
        messagebox.showerror("Import Error", error_msg)
        
        self.import_in_progress = False
    
    def _get_current_mappings(self) -> Dict[str, List[str]]:
        """Get current field mappings
        
        Returns:
            Dictionary mapping product fields to source fields
        """
        mappings = {}
        for field, var in self.mapping_entries.items():
            source_fields = [f.strip() for f in var.get().split(',') if f.strip()]
            if source_fields:
                mappings[field] = source_fields
        return mappings
    
    def _get_api_auth_config(self) -> Optional[Dict[str, Any]]:
        """Get API authentication configuration
        
        Returns:
            Authentication configuration dictionary or None if no auth
        """
        auth_type = self.auth_type_var.get()
        
        if auth_type == "None":
            return None
            
        if auth_type == "Basic Auth":
            return {
                'type': 'basic',
                'username': self.basic_username_var.get(),
                'password': self.basic_password_var.get()
            }
            
        if auth_type == "Bearer Token":
            return {
                'type': 'bearer',
                'token': self.bearer_token_var.get()
            }
            
        if auth_type == "API Key":
            return {
                'type': 'apikey',
                'key_name': self.api_key_name_var.get(),
                'key_value': self.api_key_value_var.get(),
                'location': self.api_key_location_var.get()
            }
            
        return None

    def update_progress(self, percentage, message=None):
        """Update the progress bar and optionally display a message
        
        Args:
            percentage: Progress percentage (0-100)
            message: Optional status message to display
        """
        if percentage is not None:
            # Make sure progress is between 0 and 100
            percentage = max(0, min(100, percentage))
            
            # Update progress on the main thread
            if hasattr(self, 'after'):
                self.after(0, lambda: self.progress_var.set(percentage))
            else:
                self.parent.after(0, lambda: self.progress_var.set(percentage))
        
        if message:
            self.update_status(message)

    # ... other existing methods ...