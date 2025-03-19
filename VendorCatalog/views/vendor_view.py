import tkinter as tk
from tkinter import ttk, messagebox
from controllers.vendor_controller import VendorController

class VendorFrame(ttk.Frame):
    """Frame for managing vendors"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Create a split pane
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Create the vendor list frame (left side)
        self.vendor_list_frame = VendorListFrame(self.paned, self.on_vendor_selected)
        self.paned.add(self.vendor_list_frame, weight=1)
        
        # Create the vendor detail frame (right side)
        self.vendor_detail_frame = VendorDetailFrame(self.paned)
        self.paned.add(self.vendor_detail_frame, weight=2)
    
    def on_vendor_selected(self, vendor_id, vendor_data):
        """Handle vendor selection"""
        self.vendor_detail_frame.load_vendor(vendor_id, vendor_data)
    
    def refresh(self):
        """Refresh the vendor list"""
        self.vendor_list_frame.refresh_vendors()

class VendorDetailFrame(ttk.Frame):
    """Frame for displaying vendor details"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Initialize variables
        self.vendor_id = None
        
        # Create title label
        self.title_var = tk.StringVar(value="Select a Vendor")
        self.title_label = ttk.Label(self, textvariable=self.title_var, font=("TkDefaultFont", 14, "bold"))
        self.title_label.pack(side=tk.TOP, padx=10, pady=10, anchor=tk.W)
        
        # Create toolbar
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Edit button
        self.edit_button = ttk.Button(self.toolbar, text="Edit", command=self.on_edit_vendor)
        self.edit_button.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        self.delete_button = ttk.Button(self.toolbar, text="Delete", command=self.on_delete_vendor)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Create notebook for details
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create details tab
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text="Details")
        
        # Create details grid
        self.details_grid = ttk.Frame(self.details_frame)
        self.details_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info labels
        row = 0
        ttk.Label(self.details_grid, text="ID:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.id_var = tk.StringVar()
        ttk.Label(self.details_grid, textvariable=self.id_var).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        
        row += 1
        ttk.Label(self.details_grid, text="Name:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Label(self.details_grid, textvariable=self.name_var).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        
        row += 1
        ttk.Label(self.details_grid, text="Description:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.description_var = tk.StringVar()
        ttk.Label(self.details_grid, textvariable=self.description_var).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        
        row += 1
        ttk.Label(self.details_grid, text="Contact Info:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.contact_var = tk.StringVar()
        ttk.Label(self.details_grid, textvariable=self.contact_var).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        
        row += 1
        ttk.Label(self.details_grid, text="Status:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.status_var = tk.StringVar()
        ttk.Label(self.details_grid, textvariable=self.status_var).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Disable detail buttons initially
        self.edit_button["state"] = "disabled"
        self.delete_button["state"] = "disabled"
    
    def load_vendor(self, vendor_id, vendor_data):
        """Load vendor data into the detail view"""
        if not vendor_data:
            return
            
        self.vendor_id = vendor_id
        
        # Set title
        self.title_var.set(f"Vendor: {vendor_data[1]}")
        
        # Set details
        self.id_var.set(vendor_data[0])
        self.name_var.set(vendor_data[1])
        self.description_var.set(vendor_data[2] or "")
        self.contact_var.set(vendor_data[3] or "")
        self.status_var.set(vendor_data[4])
        
        # Enable buttons
        self.edit_button["state"] = "normal"
        self.delete_button["state"] = "normal"
    
    def on_edit_vendor(self):
        """Handle edit vendor button click"""
        if not self.vendor_id:
            return
            
        vendor_data = VendorController.get_vendor(self.vendor_id)
        if not vendor_data:
            return
            
        VendorDialog(self, title="Edit Vendor", vendor_id=self.vendor_id, vendor_data=vendor_data, callback=self.refresh_vendor)
    
    def refresh_vendor(self):
        """Refresh vendor data"""
        if not self.vendor_id:
            return
            
        vendor_data = VendorController.get_vendor(self.vendor_id)
        self.load_vendor(self.vendor_id, vendor_data)
    
    def on_delete_vendor(self):
        """Handle delete vendor button click"""
        if not self.vendor_id:
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this vendor?"):
            return
            
        # Delete vendor
        success = VendorController.delete_vendor(self.vendor_id)
        
        if success:
            # Clear detail view
            self.vendor_id = None
            self.title_var.set("Select a Vendor")
            self.id_var.set("")
            self.name_var.set("")
            self.description_var.set("")
            self.contact_var.set("")
            self.status_var.set("")
            
            # Disable buttons
            self.edit_button["state"] = "disabled"
            self.delete_button["state"] = "disabled"
            
            # Refresh vendor list in parent
            # Assuming our parent has a method to refresh vendors
            if hasattr(self.master.master, "refresh"):
                self.master.master.refresh()


class VendorDialog(tk.Toplevel):
    """Dialog for adding or editing a vendor"""
    
    def __init__(self, parent, title="Vendor", vendor_id=None, vendor_data=None, callback=None):
        super().__init__(parent)
        
        self.vendor_id = vendor_id
        self.callback = callback
        
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
            success = VendorController.update_vendor(
                self.vendor_id,
                name=name,
                description=description,
                contact_info=contact_info,
                status=status
            )
        else:
            # Create vendor
            vendor_id = VendorController.create_vendor(
                name=name,
                description=description,
                contact_info=contact_info
            )
            success = bool(vendor_id)
        
        if success:
            # Call the callback function
            if self.callback:
                self.callback()
                
            # Close the dialog
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save vendor")

class VendorListFrame(ttk.Frame):
    """Frame for displaying the list of vendors"""
    
    def __init__(self, parent, selection_callback):
        super().__init__(parent)
        self.selection_callback = selection_callback
        
        # Create toolbar
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Search box
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        ttk.Label(self.toolbar, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(self.toolbar, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Add button
        self.add_button = ttk.Button(self.toolbar, text="Add Vendor", command=self.on_add_vendor)
        self.add_button.pack(side=tk.RIGHT, padx=5)
        
        # Create treeview for vendors
        self.tree = ttk.Treeview(self, columns=("id", "name", "status"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Vendor Name")
        self.tree.heading("status", text="Status")
        
        self.tree.column("id", width=50)
        self.tree.column("name", width=200)
        self.tree.column("status", width=100)
        
        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack the tree and scrollbar
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_vendor_selected)
        
        # Load initial data
        self.refresh_vendors()
    
    def refresh_vendors(self):
        """Refresh the vendor list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get vendors from controller
        vendors = VendorController.get_all_vendors()
        
        # Add vendors to treeview
        for vendor in vendors:
            self.tree.insert("", tk.END, values=(vendor[0], vendor[1], vendor[4]))
    
    def on_search(self, *args):
        """Handle search input"""
        search_term = self.search_var.get()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if search_term:
            # Search vendors
            vendors = VendorController.search_vendors(search_term)
        else:
            # Get all vendors
            vendors = VendorController.get_all_vendors()
        
        # Add vendors to treeview
        for vendor in vendors:
            self.tree.insert("", tk.END, values=(vendor[0], vendor[1], vendor[4]))
    
    def on_add_vendor(self):
        """Handle add vendor button click"""
        VendorDialog(self, title="Add Vendor", callback=self.refresh_vendors)
    
    def on_vendor_selected(self, event):
        """Handle vendor selection"""
        selection = self.tree.selection()
        if not selection:
            return
            
        # Get selected vendor ID
        vendor_id = self.tree.item(selection[0], "values")[0]
        
        # Get vendor data
        vendor_data = VendorController.get_vendor(vendor_id)
        
        # Call the selection callback
        self.selection_callback(vendor_id, vendor_data)