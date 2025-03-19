#!/usr/bin/env python3
"""
Vendor Management Application

A simplified version of the VendorCatalog application that focuses only on
vendor management, using PostgreSQL as the backend.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add the current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from config.settings import initialize_settings
from utils.db_factory import DatabaseFactory

class VendorApp(tk.Tk):
    """Main Vendor Management Application"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Vendor Management")
        self.geometry("800x600")
        
        # Initialize variables
        self.vendor_controller = DatabaseFactory.get_vendor_controller()
        
        # Create main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create title label
        title_label = ttk.Label(self.main_frame, text="Vendor Management", font=("Arial", 16, "bold"))
        title_label.pack(side=tk.TOP, pady=10)
        
        # Create split pane
        self.paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Create vendor list frame (left side)
        self.vendor_list_frame = self.create_vendor_list_frame(self.paned)
        self.paned.add(self.vendor_list_frame, weight=1)
        
        # Create vendor detail frame (right side)
        self.vendor_detail_frame = self.create_vendor_detail_frame(self.paned)
        self.paned.add(self.vendor_detail_frame, weight=2)
        
        # Set status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Populate vendor list
        self.refresh_vendors()
    
    def create_vendor_list_frame(self, parent):
        """Create the vendor list frame"""
        frame = ttk.Frame(parent)
        
        # Create toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Add button
        add_button = ttk.Button(toolbar, text="Add Vendor", command=self.on_add_vendor)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_button = ttk.Button(toolbar, text="Refresh", command=self.refresh_vendors)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Create treeview for vendors
        columns = ("id", "name", "status")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Set column headings
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("status", text="Status")
        
        # Set column widths
        self.tree.column("id", width=50)
        self.tree.column("name", width=200)
        self.tree.column("status", width=100)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Place treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_vendor_selected)
        
        return frame
    
    def create_vendor_detail_frame(self, parent):
        """Create the vendor detail frame"""
        frame = ttk.Frame(parent)
        
        # Create title label
        self.detail_title_var = tk.StringVar(value="Select a Vendor")
        title_label = ttk.Label(frame, textvariable=self.detail_title_var, font=("Arial", 14, "bold"))
        title_label.pack(side=tk.TOP, padx=10, pady=10, anchor=tk.W)
        
        # Create toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Edit button
        self.edit_button = ttk.Button(toolbar, text="Edit", command=self.on_edit_vendor, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        self.delete_button = ttk.Button(toolbar, text="Delete", command=self.on_delete_vendor, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Create detail fields
        detail_frame = ttk.Frame(frame)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info labels
        ttk.Label(detail_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.id_var = tk.StringVar()
        ttk.Label(detail_frame, textvariable=self.id_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(detail_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Label(detail_frame, textvariable=self.name_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(detail_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.description_var = tk.StringVar()
        ttk.Label(detail_frame, textvariable=self.description_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(detail_frame, text="Contact Info:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.contact_var = tk.StringVar()
        ttk.Label(detail_frame, textvariable=self.contact_var).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(detail_frame, text="Status:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.status_var = tk.StringVar()
        ttk.Label(detail_frame, textvariable=self.status_var).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        return frame
    
    def refresh_vendors(self):
        """Refresh the vendor list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all vendors
        vendors = self.vendor_controller.get_all_vendors()
        
        # Add vendors to treeview
        for vendor in vendors:
            self.tree.insert("", tk.END, values=(vendor[0], vendor[1], vendor[4]))
        
        # Update status
        self.status_var.set(f"Showing {len(vendors)} vendors")
    
    def on_vendor_selected(self, event):
        """Handle vendor selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get selected vendor ID
        item = selection[0]
        vendor_id = self.tree.item(item, "values")[0]
        
        # Get vendor data
        vendor_data = self.vendor_controller.get_vendor(vendor_id)
        if not vendor_data:
            return
        
        # Update detail view
        self.load_vendor_details(vendor_data)
    
    def load_vendor_details(self, vendor_data):
        """Load vendor data into the detail view"""
        if not vendor_data:
            return
        
        # Set title
        self.detail_title_var.set(f"Vendor: {vendor_data[1]}")
        
        # Set details
        self.id_var.set(vendor_data[0])
        self.name_var.set(vendor_data[1])
        self.description_var.set(vendor_data[2] or "")
        self.contact_var.set(vendor_data[3] or "")
        self.status_var.set(vendor_data[4])
        
        # Enable buttons
        self.edit_button["state"] = tk.NORMAL
        self.delete_button["state"] = tk.NORMAL
    
    def on_add_vendor(self):
        """Handle add vendor button click"""
        VendorDialog(self, callback=self.refresh_vendors)
    
    def on_edit_vendor(self):
        """Handle edit vendor button click"""
        vendor_id = self.id_var.get()
        if not vendor_id:
            return
        
        vendor_data = self.vendor_controller.get_vendor(int(vendor_id))
        if not vendor_data:
            return
        
        VendorDialog(self, title="Edit Vendor", vendor_id=int(vendor_id), vendor_data=vendor_data, callback=self.refresh_vendors)
    
    def on_delete_vendor(self):
        """Handle delete vendor button click"""
        vendor_id = self.id_var.get()
        if not vendor_id:
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this vendor?"):
            return
        
        # Delete vendor
        success = self.vendor_controller.delete_vendor(int(vendor_id))
        
        if success:
            messagebox.showinfo("Success", "Vendor deleted successfully.")
            
            # Clear detail view
            self.detail_title_var.set("Select a Vendor")
            self.id_var.set("")
            self.name_var.set("")
            self.description_var.set("")
            self.contact_var.set("")
            self.status_var.set("")
            
            # Disable buttons
            self.edit_button["state"] = tk.DISABLED
            self.delete_button["state"] = tk.DISABLED
            
            # Refresh vendor list
            self.refresh_vendors()
        else:
            messagebox.showerror("Error", "Failed to delete vendor.")

class VendorDialog(tk.Toplevel):
    """Dialog for adding or editing a vendor"""
    
    def __init__(self, parent, title="Add Vendor", vendor_id=None, vendor_data=None, callback=None):
        super().__init__(parent)
        
        self.vendor_id = vendor_id
        self.callback = callback
        self.vendor_controller = DatabaseFactory.get_vendor_controller()
        
        self.title(title)
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create form
        self.create_form(vendor_data)
        
        # Position the dialog relative to the parent
        if parent is not None:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            
            dialog_width = 400
            dialog_height = 300
            
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
            
            self.geometry(f"+{x}+{y}")
        
        # Focus the dialog
        self.focus_set()
        
        # Wait for the dialog to be closed
        self.wait_window()
    
    def create_form(self, vendor_data):
        """Create the form elements"""
        # Create form frame
        form_frame = ttk.Frame(self, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar(value=vendor_data[1] if vendor_data else "")
        ttk.Entry(form_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.description_var = tk.StringVar(value=vendor_data[2] if vendor_data else "")
        ttk.Entry(form_frame, textvariable=self.description_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Contact Info
        ttk.Label(form_frame, text="Contact Info:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.contact_var = tk.StringVar(value=vendor_data[3] if vendor_data else "")
        ttk.Entry(form_frame, textvariable=self.contact_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Status
        ttk.Label(form_frame, text="Status:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.status_var = tk.StringVar(value=vendor_data[4] if vendor_data else "active")
        status_combobox = ttk.Combobox(form_frame, textvariable=self.status_var, width=15)
        status_combobox["values"] = ["active", "inactive"]
        status_combobox.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def on_save(self):
        """Handle save button click"""
        # Validate form
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        
        description = self.description_var.get().strip()
        contact_info = self.contact_var.get().strip()
        status = self.status_var.get()
        
        if self.vendor_id:
            # Update vendor
            success = self.vendor_controller.update_vendor(
                self.vendor_id,
                name=name,
                description=description,
                contact_info=contact_info,
                status=status
            )
            message = "Vendor updated successfully."
        else:
            # Create vendor
            vendor_id = self.vendor_controller.create_vendor(
                name=name,
                description=description,
                contact_info=contact_info
            )
            success = bool(vendor_id)
            message = "Vendor created successfully."
        
        if success:
            messagebox.showinfo("Success", message)
            
            # Call the callback function
            if self.callback:
                self.callback()
                
            # Close the dialog
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save vendor")

def main():
    """Main application entry point"""
    # Initialize settings
    initialize_settings()
    
    # Initialize database tables
    DatabaseFactory.initialize_database()
    
    # Create and start the application
    app = VendorApp()
    app.mainloop()

if __name__ == "__main__":
    main() 