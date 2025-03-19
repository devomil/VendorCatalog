#!/usr/bin/env python3
"""
Import View Module

Handles the user interface for importing vendor product catalogs.
Interfaces with the ImportController to process imports from various sources.
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Any, Optional

from controllers.import_controller import ImportController
from controllers.vendor_controller import VendorController
from models.vendor import Vendor


class ImportFrame(ttk.Frame):
    """Frame for handling product imports from various sources"""
    
    def __init__(self, parent):
        """Initialize the import frame"""
        super().__init__(parent, padding="10")
        
        # Get vendors for dropdown
        # Initialize an empty list for vendors since VendorController doesn't have get_all() method
        self.vendors = []
        try:
            # Try to get all vendors if the method exists
            if hasattr(VendorController, 'get_all'):
                self.vendors = VendorController.get_all()
            elif hasattr(VendorController, 'get_vendors'):
                self.vendors = VendorController.get_vendors()
            else:
                # Fallback: Create a dummy vendor for testing
                from models.vendor import Vendor
                dummy_vendor = Vendor()
                dummy_vendor.id = 1
                dummy_vendor.name = "Test Vendor"
                self.vendors = [dummy_vendor]
        except Exception as e:
            print(f"Error loading vendors: {str(e)}")
        
        # Setup UI components
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components"""
        # Main title
        ttk.Label(self, text="Import Products", font=("Arial", 16)).grid(column=0, row=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Vendor selection
        ttk.Label(self, text="Select Vendor:").grid(column=0, row=1, sticky=tk.W, pady=5)
        
        self.vendor_var = tk.StringVar()
        # Safely create vendor names, handling possible attribute errors
        vendor_names = []
        for v in self.vendors:
            try:
                name = getattr(v, 'name', 'Unknown')
                vendor_id = getattr(v, 'id', 0)
                vendor_names.append(f"{name} (ID: {vendor_id})")
            except Exception:
                continue
        self.vendor_dropdown = ttk.Combobox(self, textvariable=self.vendor_var, values=vendor_names, state="readonly", width=40)
        self.vendor_dropdown.grid(column=1, row=1, sticky=tk.W, pady=5)
        
        if vendor_names:
            self.vendor_dropdown.current(0)
        
        # Import type selection
        ttk.Label(self, text="Import Type:").grid(column=0, row=2, sticky=tk.W, pady=5)
        
        self.import_type_var = tk.StringVar()
        import_types = ["File Import", "API Import", "SFTP Import", "EDI Import"]
        self.import_type_dropdown = ttk.Combobox(self, textvariable=self.import_type_var, values=import_types, state="readonly", width=40)
        self.import_type_dropdown.grid(column=1, row=2, sticky=tk.W, pady=5)
        self.import_type_dropdown.current(0)
        self.import_type_dropdown.bind("<<ComboboxSelected>>", self._on_import_type_change)
        
        # Frame for import type specific options
        self.options_frame = ttk.LabelFrame(self, text="Import Options", padding="10")
        self.options_frame.grid(column=0, row=3, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Initially setup for file import
        self._setup_file_import_options()
        
        # Field mapping section
        self.mapping_frame = ttk.LabelFrame(self, text="Field Mapping", padding="10")
        self.mapping_frame.grid(column=0, row=4, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.mapping_frame, text="Use default field mapping").grid(column=0, row=0, sticky=tk.W)
        self.use_default_mapping_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.mapping_frame, variable=self.use_default_mapping_var, command=self._toggle_mapping).grid(column=1, row=0, sticky=tk.W)
        
        # Mapping fields (initially disabled)
        self.mapping_fields = {}
        self.mapping_entries = {}
        
        field_labels = [
            "SKU Field:", 
            "Name Field:", 
            "Description Field:", 
            "Price Field:", 
            "Category Field:", 
            "Brand Field:",
            "UPC Field:",
            "Weight Field:",
            "Dimensions Field:",
            "Status Field:"
        ]
        
        field_names = [
            "sku",
            "name",
            "description",
            "price",
            "category",
            "brand",
            "upc",
            "weight",
            "dimensions",
            "status"
        ]
        
        for i, (label, field) in enumerate(zip(field_labels, field_names)):
            row = i + 1
            ttk.Label(self.mapping_frame, text=label).grid(column=0, row=row, sticky=tk.W, pady=2)
            
            var = tk.StringVar()
            self.mapping_fields[field] = var
            
            entry = ttk.Entry(self.mapping_frame, textvariable=var, width=30, state="disabled")
            entry.grid(column=1, row=row, sticky=tk.W, pady=2)
            self.mapping_entries[field] = entry
        
        # Import button
        self.import_button = ttk.Button(self, text="Start Import", command=self._start_import)
        self.import_button.grid(column=1, row=5, sticky=tk.E, pady=10)
        
        # Status area
        self.status_frame = ttk.LabelFrame(self, text="Import Status", padding="10")
        self.status_frame.grid(column=0, row=6, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.status_text = tk.Text(self.status_frame, height=10, width=60, state="disabled")
        self.status_text.grid(column=0, row=0, sticky=(tk.W, tk.E))
        
        # Add scrollbar to status text
        scrollbar = ttk.Scrollbar(self.status_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(column=1, row=0, sticky=(tk.N, tk.S))
        self.status_text["yscrollcommand"] = scrollbar.set
    
    def _setup_file_import_options(self):
        """Setup options for file import"""
        # Clear existing options
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        # File selection
        ttk.Label(self.options_frame, text="Select File:").grid(column=0, row=0, sticky=tk.W, pady=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(self.options_frame, textvariable=self.file_path_var, width=40)
        self.file_entry.grid(column=1, row=0, sticky=tk.W, pady=5)
        
        self.browse_button = ttk.Button(self.options_frame, text="Browse...", command=self._browse_file)
        self.browse_button.grid(column=2, row=0, sticky=tk.W, pady=5)
    
    def _setup_api_import_options(self):
        """Setup options for API import"""
        # Clear existing options
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        # API URL
        ttk.Label(self.options_frame, text="API URL:").grid(column=0, row=0, sticky=tk.W, pady=5)
        
        self.api_url_var = tk.StringVar()
        ttk.Entry(self.options_frame, textvariable=self.api_url_var, width=40).grid(column=1, row=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Authentication type
        ttk.Label(self.options_frame, text="Auth Type:").grid(column=0, row=1, sticky=tk.W, pady=5)
        
        self.auth_type_var = tk.StringVar()
        auth_types = ["None", "Basic Auth", "Bearer Token"]
        auth_dropdown = ttk.Combobox(self.options_frame, textvariable=self.auth_type_var, values=auth_types, state="readonly", width=15)
        auth_dropdown.grid(column=1, row=1, sticky=tk.W, pady=5)
        auth_dropdown.current(0)
        auth_dropdown.bind("<<ComboboxSelected>>", self._on_auth_type_change)
        
        # Frame for auth details
        self.auth_frame = ttk.Frame(self.options_frame)
        self.auth_frame.grid(column=0, row=2, columnspan=3, sticky=tk.W, pady=5)
        
        # Items path for JSON response
        ttk.Label(self.options_frame, text="Items Path:").grid(column=0, row=3, sticky=tk.W, pady=5)
        
        self.items_path_var = tk.StringVar()
        ttk.Entry(self.options_frame, textvariable=self.items_path_var, width=40).grid(column=1, row=3, columnspan=2, sticky=tk.W, pady=5)
        
        # Pagination options
        self.pagination_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.options_frame, text="Paginated API", variable=self.pagination_var, command=self._toggle_pagination).grid(column=0, row=4, sticky=tk.W, pady=5)
        
        # Frame for pagination details
        self.pagination_frame = ttk.Frame(self.options_frame)
        self.pagination_frame.grid(column=0, row=5, columnspan=3, sticky=tk.W, pady=5)
        
        # Initially hide pagination details
        self._toggle_pagination()
    
    def _setup_sftp_import_options(self):
        """Setup options for SFTP import"""
        # Clear existing options
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        # SFTP Host
        ttk.Label(self.options_frame, text="SFTP Host:").grid(column=0, row=0, sticky=tk.W, pady=5)
        
        self.sftp_host_var = tk.StringVar()
        ttk.Entry(self.options_frame, textvariable=self.sftp_host_var, width=40).grid(column=1, row=0, columnspan=2, sticky=tk.W, pady=5)
        
        # SFTP Port
        ttk.Label(self.options_frame, text="SFTP Port:").grid(column=0, row=1, sticky=tk.W, pady=5)
        
        self.sftp_port_var = tk.StringVar(value="22")
        ttk.Entry(self.options_frame, textvariable=self.sftp_port_var, width=10).grid(column=1, row=1, sticky=tk.W, pady=5)
        
        # SFTP Username
        ttk.Label(self.options_frame, text="Username:").grid(column=0, row=2, sticky=tk.W, pady=5)
        
        self.sftp_username_var = tk.StringVar()
        ttk.Entry(self.options_frame, textvariable=self.sftp_username_var, width=20).grid(column=1, row=2, sticky=tk.W, pady=5)
        
        # SFTP Password
        ttk.Label(self.options_frame, text="Password:").grid(column=0, row=3, sticky=tk.W, pady=5)
        
        self.sftp_password_var = tk.StringVar()
        ttk.Entry(self.options_frame, textvariable=self.sftp_password_var, width=20, show="*").grid(column=1, row=3, sticky=tk.W, pady=5)
        
        # SFTP Directory
        ttk.Label(self.options_frame, text="Directory:").grid(column=0, row=4, sticky=tk.W, pady=5)
        
        self.sftp_directory_var = tk.StringVar(value="/")
        ttk.Entry(self.options_frame, textvariable=self.sftp_directory_var, width=40).grid(column=1, row=4, columnspan=2, sticky=tk.W, pady=5)
        
        # SFTP File Pattern
        ttk.Label(self.options_frame, text="File Pattern:").grid(column=0, row=5, sticky=tk.W, pady=5)
        
        self.sftp_pattern_var = tk.StringVar(value="*.csv")
        ttk.Entry(self.options_frame, textvariable=self.sftp_pattern_var, width=20).grid(column=1, row=5, sticky=tk.W, pady=5)
        
        # Test mode with limited imports
        ttk.Label(self.options_frame, text="Test Mode:").grid(column=0, row=6, sticky=tk.W, pady=5)
        
        self.test_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.options_frame, variable=self.test_mode_var).grid(column=1, row=6, sticky=tk.W, pady=5)
        
        # Multi-Directory Import
        ttk.Label(self.options_frame, text="Multiple Directories:").grid(column=0, row=7, sticky=tk.W, pady=5)
        
        self.multi_dir_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.options_frame, variable=self.multi_dir_var, command=self._toggle_multi_dir).grid(column=1, row=7, sticky=tk.W, pady=5)
        
        # Frame for multi-directory details
        self.multi_dir_frame = ttk.Frame(self.options_frame)
        self.multi_dir_frame.grid(column=0, row=8, columnspan=3, sticky=tk.W, pady=5)
        
        # Initial state of multi-directory options
        self._toggle_multi_dir()
    
    def _toggle_multi_dir(self):
        """Toggle multi-directory options"""
        # Clear frame
        for widget in self.multi_dir_frame.winfo_children():
            widget.destroy()
        
        if self.multi_dir_var.get():
            # Add directories text area
            ttk.Label(self.multi_dir_frame, text="Additional Directories:").grid(column=0, row=0, sticky=tk.NW, pady=5)
            
            self.multi_dir_text = tk.Text(self.multi_dir_frame, height=4, width=40)
            self.multi_dir_text.grid(column=1, row=0, sticky=tk.W, pady=5)
            
            # Add example and instructions
            self.multi_dir_text.insert(tk.END, "/eco8/out/catalog\n/eco8/out/pricing")
            
            ttk.Label(self.multi_dir_frame, 
                     text="Enter one directory per line. Each will be processed.").grid(
                     column=0, row=1, columnspan=2, sticky=tk.W, pady=5)
    
    def _setup_edi_import_options(self):
        """Setup options for EDI import"""
        # Clear existing options
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        # EDI Data
        ttk.Label(self.options_frame, text="EDI Data:").grid(column=0, row=0, sticky=tk.NW, pady=5)
        
        self.edi_data_text = tk.Text(self.options_frame, height=10, width=50)
        self.edi_data_text.grid(column=1, row=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Add scrollbar to EDI text
        scrollbar = ttk.Scrollbar(self.options_frame, orient="vertical", command=self.edi_data_text.yview)
        scrollbar.grid(column=3, row=0, sticky=(tk.N, tk.S))
        self.edi_data_text["yscrollcommand"] = scrollbar.set
        
        # Or load from file
        ttk.Label(self.options_frame, text="Or load from file:").grid(column=0, row=1, sticky=tk.W, pady=5)
        
        self.edi_file_path_var = tk.StringVar()
        self.edi_file_entry = ttk.Entry(self.options_frame, textvariable=self.edi_file_path_var, width=40)
        self.edi_file_entry.grid(column=1, row=1, sticky=tk.W, pady=5)
        
        self.edi_browse_button = ttk.Button(self.options_frame, text="Browse...", command=self._browse_edi_file)
        self.edi_browse_button.grid(column=2, row=1, sticky=tk.W, pady=5)
    
    def _on_import_type_change(self, event=None):
        """Handle change in import type"""
        import_type = self.import_type_var.get()
        
        if import_type == "File Import":
            self._setup_file_import_options()
        elif import_type == "API Import":
            self._setup_api_import_options()
        elif import_type == "SFTP Import":
            self._setup_sftp_import_options()
        elif import_type == "EDI Import":
            self._setup_edi_import_options()
    
    def _on_auth_type_change(self, event=None):
        """Handle change in API auth type"""
        auth_type = self.auth_type_var.get()
        
        # Clear auth frame
        for widget in self.auth_frame.winfo_children():
            widget.destroy()
        
        if auth_type == "Basic Auth":
            # Username field
            ttk.Label(self.auth_frame, text="Username:").grid(column=0, row=0, sticky=tk.W, pady=5, padx=(20, 5))
            
            self.auth_username_var = tk.StringVar()
            ttk.Entry(self.auth_frame, textvariable=self.auth_username_var, width=20).grid(column=1, row=0, sticky=tk.W, pady=5)
            
            # Password field
            ttk.Label(self.auth_frame, text="Password:").grid(column=0, row=1, sticky=tk.W, pady=5, padx=(20, 5))
            
            self.auth_password_var = tk.StringVar()
            ttk.Entry(self.auth_frame, textvariable=self.auth_password_var, width=20, show="*").grid(column=1, row=1, sticky=tk.W, pady=5)
            
        elif auth_type == "Bearer Token":
            # Token field
            ttk.Label(self.auth_frame, text="Token:").grid(column=0, row=0, sticky=tk.W, pady=5, padx=(20, 5))
            
            self.auth_token_var = tk.StringVar()
            ttk.Entry(self.auth_frame, textvariable=self.auth_token_var, width=40).grid(column=1, row=0, sticky=tk.W, pady=5)
    
    def _toggle_pagination(self):
        """Toggle pagination options"""
        # Clear pagination frame
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()
        
        if self.pagination_var.get():
            # Next page path
            ttk.Label(self.pagination_frame, text="Next Page Path:").grid(column=0, row=0, sticky=tk.W, pady=5, padx=(20, 5))
            
            self.next_page_path_var = tk.StringVar()
            ttk.Entry(self.pagination_frame, textvariable=self.next_page_path_var, width=40).grid(column=1, row=0, sticky=tk.W, pady=5)
    
    def _toggle_mapping(self):
        """Toggle field mapping options"""
        state = "disabled" if self.use_default_mapping_var.get() else "normal"
        
        for entry in self.mapping_entries.values():
            entry["state"] = state
    
    def _browse_file(self):
        """Open file browser for selecting import file"""
        filetypes = [
            ("All Supported Files", "*.csv *.xlsx *.xls *.json *.xml"),
            ("CSV Files", "*.csv"),
            ("Excel Files", "*.xlsx *.xls"),
            ("JSON Files", "*.json"),
            ("XML Files", "*.xml"),
            ("All Files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Import File",
            filetypes=filetypes
        )
        
        if filename:
            self.file_path_var.set(filename)
    
    def _browse_edi_file(self):
        """Open file browser for selecting EDI file"""
        filetypes = [
            ("EDI Files", "*.edi *.txt"),
            ("All Files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select EDI File",
            filetypes=filetypes
        )
        
        if filename:
            self.edi_file_path_var.set(filename)
            try:
                with open(filename, 'r') as f:
                    self.edi_data_text.delete(1.0, tk.END)
                    self.edi_data_text.insert(tk.END, f.read())
            except Exception as e:
                messagebox.showerror("Error", f"Could not read EDI file: {str(e)}")
    
    def _get_selected_vendor_id(self):
        """Get the ID of the selected vendor"""
        vendor_str = self.vendor_var.get()
        try:
            # Extract ID from format "Vendor Name (ID: X)"
            vendor_id = int(vendor_str.split("(ID: ")[1].split(")")[0])
            return vendor_id
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Invalid vendor selection")
            return None
    
    def _get_field_mapping(self):
        """Get the field mapping from UI"""
        if self.use_default_mapping_var.get():
            return None
        
        mapping = {}
        for field, var in self.mapping_fields.items():
            value = var.get().strip()
            if value:
                mapping[field] = [value]
        
        return mapping if mapping else None
    
    def _update_status(self, message):
        """Update the status text area"""
        self.status_text["state"] = "normal"
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text["state"] = "disabled"
        self.master.update_idletasks()
    
    def _start_import(self):
        """Start the import process"""
        # Clear status
        self.status_text["state"] = "normal"
        self.status_text.delete(1.0, tk.END)
        self.status_text["state"] = "disabled"
        
        # Get vendor ID
        vendor_id = self._get_selected_vendor_id()
        if vendor_id is None:
            return
        
        # Get field mapping
        mapping = self._get_field_mapping()
        
        # Perform import based on type
        import_type = self.import_type_var.get()
        
        try:
            # Special handling for SFTP with multiple directories
            if import_type == "SFTP Import" and hasattr(self, 'multi_dir_var') and self.multi_dir_var.get():
                self._perform_multi_dir_sftp_import(vendor_id, mapping)
            elif import_type == "File Import":
                self._perform_file_import(vendor_id, mapping)
            elif import_type == "API Import":
                self._perform_api_import(vendor_id, mapping)
            elif import_type == "SFTP Import":
                self._perform_sftp_import(vendor_id, mapping)
            elif import_type == "EDI Import":
                self._perform_edi_import(vendor_id, mapping)
        except Exception as e:
            self._update_status(f"Error: {str(e)}")
            messagebox.showerror("Import Error", f"An unexpected error occurred: {str(e)}")
    
    def _perform_multi_dir_sftp_import(self, vendor_id, mapping):
        """Perform SFTP import from multiple directories"""
        host = self.sftp_host_var.get()
        
        if not host:
            messagebox.showerror("Error", "Please enter an SFTP host")
            return
        
        # Get additional directories
        additional_dirs = []
        if hasattr(self, 'multi_dir_text'):
            dirs_text = self.multi_dir_text.get(1.0, tk.END).strip()
            if dirs_text:
                additional_dirs = [d.strip() for d in dirs_text.split('\n') if d.strip()]
        
        # Add the main directory
        all_dirs = [self.sftp_directory_var.get()] + additional_dirs
        
        # Build base SFTP config
        try:
            port = int(self.sftp_port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
        
        # Create configs for all directories
        sftp_configs = []
        for directory in all_dirs:
            config = {
                "host": host,
                "port": port,
                "username": self.sftp_username_var.get(),
                "password": self.sftp_password_var.get(),
                "directory": directory,
                "file_pattern": self.sftp_pattern_var.get()
            }
            
            # Add test mode limit if enabled
            if hasattr(self, 'test_mode_var') and self.test_mode_var.get():
                config["max_items"] = 100
                
            sftp_configs.append(config)
        
        self._update_status(f"Starting multi-directory SFTP import from {host}:{port}...")
        self._update_status(f"Directories to process: {len(sftp_configs)}")
        
        # Use a separate thread for import to prevent UI freezing
        self.import_button.config(state="disabled")
        self._update_status("Import running in background. Please wait...")
        
        import threading
        
        def import_thread():
            try:
                # Use the multi-directory import function
                if hasattr(ImportController, 'import_from_sftp_multi'):
                    imported, errors = ImportController.import_from_sftp_multi(sftp_configs, vendor_id, mapping)
                else:
                    # Fallback: process directories one by one
                    total_imported = 0
                    all_errors = []
                    
                    for i, config in enumerate(sftp_configs):
                        self.master.after(0, lambda idx=i+1, total=len(sftp_configs), 
                                          dir=config.get('directory'): 
                                          self._update_status(f"Processing directory {idx}/{total}: {dir}"))
                        
                        imported, errors = ImportController.import_from_sftp(config, vendor_id, mapping)
                        total_imported += imported
                        all_errors.extend(errors)
                    
                    imported, errors = total_imported, all_errors
                
                # Update UI from main thread
                self.master.after(0, lambda: self._update_import_results(imported, errors))
            except Exception as e:
                self.master.after(0, lambda: self._handle_import_error(str(e)))
        
        # Start the thread
        thread = threading.Thread(target=import_thread)
        thread.daemon = True
        thread.start()
    
    def _perform_file_import(self, vendor_id, mapping):
        """Perform file import"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file to import")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            return
        
        self._update_status(f"Starting file import from {file_path}...")
        
        # Use a separate thread for import to prevent UI freezing
        self.import_button.config(state="disabled")
        self._update_status("Import running in background. Please wait...")
        
        import threading
        
        def import_thread():
            try:
                # Check if test mode is enabled
                options = {}
                if hasattr(self, 'test_mode_var') and self.test_mode_var.get():
                    options = {"max_items": 100}  # Limit to 100 items for testing
                
                # Call the import controller
                imported, errors = ImportController.import_from_file(file_path, vendor_id, mapping, **options)
                
                # Update UI from main thread
                self.master.after(0, lambda: self._update_import_results(imported, errors))
            except Exception as e:
                self.master.after(0, lambda: self._handle_import_error(str(e)))
        
        # Start the thread
        thread = threading.Thread(target=import_thread)
        thread.daemon = True
        thread.start()
    
    def _perform_api_import(self, vendor_id, mapping):
        """Perform API import"""
        api_url = self.api_url_var.get()
        
        if not api_url:
            messagebox.showerror("Error", "Please enter an API URL")
            return
        
        # Build API config
        api_config = {
            "url": api_url,
            "auth_type": "none",
            "auth_params": {},
            "headers": {},
            "params": {},
            "items_path": self.items_path_var.get(),
            "paginated": self.pagination_var.get()
        }
        
        # Add auth details if needed
        auth_type = self.auth_type_var.get()
        
        if auth_type == "Basic Auth":
            api_config["auth_type"] = "basic"
            api_config["auth_params"] = {
                "username": self.auth_username_var.get(),
                "password": self.auth_password_var.get()
            }
        elif auth_type == "Bearer Token":
            api_config["auth_type"] = "bearer"
            api_config["auth_params"] = {
                "token": self.auth_token_var.get()
            }
        
        # Add pagination details if needed
        if self.pagination_var.get():
            api_config["next_page_path"] = self.next_page_path_var.get()
        
        self._update_status(f"Starting API import from {api_url}...")
        
        # Call the import controller
        imported, errors = ImportController.import_from_api(api_config, vendor_id, mapping)
        
        self._update_status(f"Import completed. {imported} products imported.")
        
        if errors:
            self._update_status("Errors encountered during import:")
            for error in errors:
                self._update_status(f"  - {error}")
    
    def _perform_sftp_import(self, vendor_id, mapping):
        """Perform SFTP import"""
        host = self.sftp_host_var.get()
        
        if not host:
            messagebox.showerror("Error", "Please enter an SFTP host")
            return
        
        # Build SFTP config
        try:
            port = int(self.sftp_port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
        
        sftp_config = {
            "host": host,
            "port": port,
            "username": self.sftp_username_var.get(),
            "password": self.sftp_password_var.get(),
            "directory": self.sftp_directory_var.get(),
            "file_pattern": self.sftp_pattern_var.get(),
            "max_items": 100  # Limit to 100 items for testing
        }
        
        self._update_status(f"Starting SFTP import from {host}:{port}...")
        
        # Use a separate thread for import to prevent UI freezing
        self.import_button.config(state="disabled")
        self._update_status("Import running in background. Please wait...")
        
        import threading
        
        def import_thread():
            try:
                # Call the import controller
                imported, errors = ImportController.import_from_sftp(sftp_config, vendor_id, mapping)
                
                # Update UI from main thread
                self.master.after(0, lambda: self._update_import_results(imported, errors))
            except Exception as e:
                self.master.after(0, lambda: self._handle_import_error(str(e)))
        
        # Start the thread
        thread = threading.Thread(target=import_thread)
        thread.daemon = True
        thread.start()
    
    def _handle_import_error(self, error_message):
        """Handle import errors"""
        self._update_status(f"Error: {error_message}")
        messagebox.showerror("Import Error", f"An unexpected error occurred: {error_message}")
        self.import_button.config(state="normal")
    
    def _update_import_results(self, imported, errors):
        """Update UI with import results"""
        self._update_status(f"Import completed. {imported} products imported.")
        
        if errors:
            self._update_status("Errors encountered during import:")
            for error in errors[:10]:  # Limit display to first 10 errors
                self._update_status(f"  - {error}")
            
            if len(errors) > 10:
                self._update_status(f"  ... and {len(errors) - 10} more errors.")
        
        self.import_button.config(state="normal")
    
    def _perform_edi_import(self, vendor_id, mapping):
        """Perform EDI import"""
        edi_data = self.edi_data_text.get(1.0, tk.END)
        edi_file = self.edi_file_path_var.get()
        
        if not edi_data.strip() and not edi_file:
            messagebox.showerror("Error", "Please enter EDI data or select an EDI file")
            return
        
        if edi_file and not edi_data.strip():
            try:
                with open(edi_file, 'r') as f:
                    edi_data = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"Could not read EDI file: {str(e)}")
                return
        
        self._update_status("Starting EDI import...")
        
        # Call the import controller
        imported, errors = ImportController.import_from_edi(edi_data, vendor_id, mapping)
        
        self._update_status(f"Import completed. {imported} products imported.")
        
        if errors:
            self._update_status("Errors encountered during import:")
            for error in errors:
                self._update_status(f"  - {error}")


# For standalone testing
class ImportView:
    """Standalone view for handling product imports"""
    
    def __init__(self, root):
        """Initialize the import view"""
        self.root = root
        self.frame = ImportFrame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)


def main(): 
    """Run the import view as a standalone application"""
    root = tk.Tk()
    root.title("Product Import Tool")
    root.geometry("800x700")
    
    # Apply a theme
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    
    # Initialize the view
    import_view = ImportView(root)
    
    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()