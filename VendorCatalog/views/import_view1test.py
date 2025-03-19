import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from controllers.import_controller import ImportController
from controllers.vendor_controller import VendorController

class ImportFrame(ttk.Frame):
    """Frame for bulk importing products"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Initialize variables
        self.vendor_id = None
        self.file_path = None
        self.is_test_mode = tk.BooleanVar(value=True)
        self.file_type = tk.StringVar(value="csv")
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create the UI widgets"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Import File")
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Vendor:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.vendor_combo = ttk.Combobox(file_frame, width=30)
        self.vendor_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.vendor_combo.bind("<<ComboboxSelected>>", self.on_vendor_selected)
        
        ttk.Label(file_frame, text="File Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        type_frame = ttk.Frame(file_frame)
        type_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Radiobutton(type_frame, text="CSV", variable=self.file_type, value="csv").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Excel", variable=self.file_type, value="excel").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="JSON", variable=self.file_type, value="json").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(file_frame, text="File:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.browse_button = ttk.Button(file_select_frame, text="Browse...", command=self.browse_file)
        self.browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Import Options")
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(options_frame, text="Test Mode (import up to 100 products)", variable=self.is_test_mode).pack(anchor=tk.W, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Test Import", command=self.test_import).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Import", command=self.start_import).pack(side=tk.RIGHT, padx=5)
        
        # Load vendors
        self.load_vendors()
    
    def load_vendors(self):
        """Load vendors into the combo box"""
        vendors = VendorController.get_all_vendors()
        self.vendor_combo['values'] = [f"{v[0]}: {v[1]}" for v in vendors]
    
    def on_vendor_selected(self, event):
        """Handle vendor selection"""
        selection = self.vendor_combo.get().split(':')[0].strip()
        try:
            self.vendor_id = int(selection)
        except ValueError:
            self.vendor_id = None

    def browse_file(self):
        """Open file dialog to select import file"""
        file_type = self.file_type.get()
        
        if file_type == "csv":
            filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
        elif file_type == "excel":
            filetypes = [("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        elif file_type == "json":
            filetypes = [("JSON files", "*.json"), ("All files", "*.*")]
        else:
            filetypes = [("All files", "*.*")]
        
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            self.file_path = file_path
            self.file_path_var.set(file_path)

    def test_import(self):
        """Test import with a small batch of products"""
        if not self.vendor_id:
            messagebox.showerror("Error", "Please select a vendor first")
            return
            
        if not self.file_path:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        # For now, just show a message
        messagebox.showinfo("Test Import", "Test import functionality will be implemented soon.")

    def start_import(self):
        """Start the actual import process"""
        if not self.vendor_id:
            messagebox.showerror("Error", "Please select a vendor first")
            return
            
        if not self.file_path:
            messagebox.showerror("Error", "Please select a file first")
            return
            
        # Confirm import
        if not messagebox.askyesno("Confirm Import", "Are you sure you want to import these products?"):
            return
            
        # For now, just show a message
        messagebox.showinfo("Import", "Import functionality will be implemented soon.")