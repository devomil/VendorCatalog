#!/usr/bin/env python3
"""
Import Controller Module

Handles importing vendor product catalogs from various sources:
- CSV/Excel files
- RESTful APIs
- EDI (Electronic Data Interchange)
- SFTP servers
"""

import os
import json
import csv
import pandas as pd
import ftplib
import requests
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Dict, List, Any, Callable, Optional, Union, Tuple
from pathlib import Path

from models.vendor import Vendor
from models.product import Product
from controllers.product_controller import ProductController
from controllers.vendor_controller import VendorController


class ImportController:
    """Controller for importing vendor product catalogs from various sources"""
    
    @classmethod
    def import_from_file(cls, file_path: str, vendor_id: int, mapping: Dict = None) -> Tuple[int, List[str]]:
        """
        Import products from a file (CSV, Excel, JSON, XML)
        
        Args:
            file_path: Path to the file
            vendor_id: ID of the vendor
            mapping: Optional dictionary mapping file columns to product fields
            
        Returns:
            Tuple containing (count of imported products, list of errors)
        """
        _, file_ext = os.path.splitext(file_path)
        file_ext = file_ext.lower()
        
        # Select appropriate import method based on file extension
        if file_ext == '.csv':
            return cls._import_from_csv(file_path, vendor_id, mapping)
        elif file_ext in ['.xlsx', '.xls']:
            return cls._import_from_excel(file_path, vendor_id, mapping)
        elif file_ext == '.json':
            return cls._import_from_json(file_path, vendor_id, mapping)
        elif file_ext == '.xml':
            return cls._import_from_xml(file_path, vendor_id, mapping)
        else:
            return 0, [f"Unsupported file format: {file_ext}"]
    
    @classmethod
    def import_from_api(cls, api_config: Dict, vendor_id: int, mapping: Dict = None) -> Tuple[int, List[str]]:
        """
        Import products from a RESTful API
        
        Args:
            api_config: Dictionary containing API configuration (url, auth, headers, etc.)
            vendor_id: ID of the vendor
            mapping: Optional dictionary mapping API response fields to product fields
            
        Returns:
            Tuple containing (count of imported products, list of errors)
        """
        url = api_config.get('url')
        auth_type = api_config.get('auth_type', 'none')
        auth_params = api_config.get('auth_params', {})
        headers = api_config.get('headers', {})
        params = api_config.get('params', {})
        
        # Authentication methods
        auth = None
        if auth_type == 'basic':
            auth = (auth_params.get('username', ''), auth_params.get('password', ''))
        elif auth_type == 'bearer':
            headers['Authorization'] = f"Bearer {auth_params.get('token', '')}"
        
        try:
            response = requests.get(url, auth=auth, headers=headers, params=params)
            response.raise_for_status()
            
            # Assume JSON response
            data = response.json()
            
            # Handle pagination if needed
            if api_config.get('paginated', False):
                all_data = []
                all_data.extend(cls._extract_items(data, api_config.get('items_path', '')))
                
                while cls._has_next_page(data, api_config.get('next_page_path', '')):
                    next_url = cls._get_next_page_url(data, api_config.get('next_page_path', ''))
                    response = requests.get(next_url, auth=auth, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    all_data.extend(cls._extract_items(data, api_config.get('items_path', '')))
                
                return cls._process_api_data(all_data, vendor_id, mapping)
            else:
                items = cls._extract_items(data, api_config.get('items_path', ''))
                return cls._process_api_data(items, vendor_id, mapping)
                
        except requests.RequestException as e:
            return 0, [f"API request failed: {str(e)}"]
        except json.JSONDecodeError:
            return 0, ["API response is not valid JSON"]
        except Exception as e:
            return 0, [f"Unexpected error during API import: {str(e)}"]
    
    @classmethod
    def import_from_sftp(cls, sftp_config: Dict, vendor_id: int, mapping: Dict = None) -> Tuple[int, List[str]]:
        """
        Import products from an SFTP server
        
        Args:
            sftp_config: Dictionary containing SFTP configuration
            vendor_id: ID of the vendor
            mapping: Optional dictionary mapping file columns to product fields
            
        Returns:
            Tuple containing (count of imported products, list of errors)
        """
        host = sftp_config.get('host', '')
        port = sftp_config.get('port', 22)
        username = sftp_config.get('username', '')
        password = sftp_config.get('password', '')
        directory = sftp_config.get('directory', '/')
        file_pattern = sftp_config.get('file_pattern', '*')
        
        try:
            # Connect to SFTP server
            with ftplib.FTP() as ftp:
                ftp.connect(host, port)
                ftp.login(username, password)
                
                # Navigate to the directory
                ftp.cwd(directory)
                
                # List files matching the pattern
                files = [f for f in ftp.nlst() if cls._matches_pattern(f, file_pattern)]
                
                if not files:
                    return 0, ["No matching files found on SFTP server"]
                
                # Process each file
                total_imported = 0
                all_errors = []
                
                for file in files:
                    # Create a temporary file to store the downloaded content
                    temp_file = f"temp_{file}"
                    with open(temp_file, 'wb') as f:
                        ftp.retrbinary(f"RETR {file}", f.write)
                    
                    # Import from the downloaded file
                    imported, errors = cls.import_from_file(temp_file, vendor_id, mapping)
                    total_imported += imported
                    all_errors.extend(errors)
                    
                    # Clean up the temporary file
                    os.remove(temp_file)
                
                return total_imported, all_errors
                
        except ftplib.all_errors as e:
            return 0, [f"SFTP error: {str(e)}"]
        except Exception as e:
            return 0, [f"Unexpected error during SFTP import: {str(e)}"]
    
    @classmethod
    def import_from_edi(cls, edi_data: str, vendor_id: int, mapping: Dict = None) -> Tuple[int, List[str]]:
        """
        Import products from EDI data
        
        Args:
            edi_data: String containing EDI data
            vendor_id: ID of the vendor
            mapping: Optional dictionary mapping EDI segments to product fields
            
        Returns:
            Tuple containing (count of imported products, list of errors)
        """
        # Basic EDI parsing - this would need to be enhanced for production use
        try:
            # Split EDI into segments
            segments = edi_data.split('~')
            
            # Extract product data from relevant segments
            # This is a simplified example - real EDI parsing would be more complex
            products_data = []
            current_product = {}
            
            for segment in segments:
                if not segment.strip():
                    continue
                    
                elements = segment.split('*')
                segment_id = elements[0]
                
                if segment_id == 'LIN':  # Line item (product) identifier
                    if current_product:
                        products_data.append(current_product)
                    current_product = {}
                    # Extract product ID if present (position may vary)
                    if len(elements) > 3:
                        current_product['sku'] = elements[3]
                        
                elif segment_id == 'PID':  # Product description
                    if len(elements) > 5:
                        current_product['name'] = elements[5]
                        
                elif segment_id == 'CTP':  # Pricing information
                    if len(elements) > 3:
                        try:
                            current_product['price'] = float(elements[3])
                        except ValueError:
                            pass
            
            # Add the last product if exists
            if current_product:
                products_data.append(current_product)
                
            # Process the extracted product data
            return cls._process_mapped_data(products_data, vendor_id, mapping)
            
        except Exception as e:
            return 0, [f"Error parsing EDI data: {str(e)}"]
    
    # Helper methods
    @classmethod
    def _import_from_csv(cls, file_path: str, vendor_id: int, mapping: Dict = None) -> Tuple[int, List[str]]:
        """Import products from a CSV file"""
        try:
            # Read CSV file into a list of dictionaries
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            # Process the data
            return cls._process_mapped_data(data, vendor_id, mapping)
            
        except FileNotFoundError:
            return 0, [f"File not found: {file_path}"]
        except Exception as e:
            return 0, [f"Error importing from CSV: {str(e)}"]
    
    @classmethod
    def _import_from_excel(cls, file_path: str, vendor_id: int, mapping: Dict = None) -> Tuple[int, List[str]]:
        """Import products from an Excel file"""
        try:
            # Read Excel file into a DataFrame
            df = pd.read_excel(file_path)
            
            # Convert DataFrame to list of dictionaries
            data = df.to_dict('records')
            
            # Process the data
            return cls._process_mapped_data(data, vendor_id, mapping)
            
        except FileNotFoundError:
            return 0, [f"File not found: {file_path}"]
        except Exception as e:
            return 0, [f"Error importing from Excel: {str(e)}"]
    
    @classmethod
    def _import_from_json(cls, file_path: str, vendor_id: int, mapping: Dict = None) -> Tuple[int, List[str]]:
        """Import products from a JSON file"""
        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle potential array or object with items array
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'items' in data:
                items = data['items']
            elif isinstance(data, dict) and 'products' in data:
                items = data['products']
            else:
                items = [data]  # Single item
            
            # Process the data
            return cls._process_mapped_data(items, vendor_id, mapping)
            
        except FileNotFoundError:
            return 0, [f"File not found: {file_path}"]
        except json.JSONDecodeError:
            return 0, [f"Invalid JSON format in file: {file_path}"]
        except Exception as e:
            return 0, [f"Error importing from JSON: {str(e)}"]
    
    @classmethod
    def _import_from_xml(cls, file_path: str, vendor_id: int, mapping: Dict = None) -> Tuple[int, List[str]]:
        """Import products from an XML file"""
        try:
            # Parse XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract product elements (assuming a structure like <products><product>...</product></products>)
            product_elements = []
            
            # Look for product elements at different possible paths
            for path in ['./product', './products/product', './items/item', '.']:
                elements = root.findall(path)
                if elements:
                    product_elements = elements
                    break
            
            # Convert XML elements to dictionaries
            items = []
            for elem in product_elements:
                item = {}
                for child in elem:
                    item[child.tag] = child.text
                items.append(item)
            
            # Process the data
            return cls._process_mapped_data(items, vendor_id, mapping)
            
        except FileNotFoundError:
            return 0, [f"File not found: {file_path}"]
        except ET.ParseError:
            return 0, [f"Invalid XML format in file: {file_path}"]
        except Exception as e:
            return 0, [f"Error importing from XML: {str(e)}"]
    
    @classmethod
    def _process_mapped_data(cls, data: List[Dict], vendor_id: int, mapping: Dict = None) -> Tuple[int, List[str]]:
        """
        Process imported data with field mapping and save to database
        
        Args:
            data: List of dictionaries containing product data
            vendor_id: ID of the vendor
            mapping: Optional dictionary mapping source fields to product fields
            
        Returns:
            Tuple containing (count of imported products, list of errors)
        """
        errors = []
        imported_count = 0
        
        # Default mapping if none provided
        if not mapping:
            mapping = {
                'sku': ['sku', 'product_id', 'item_number', 'part_number', 'id'],
                'name': ['name', 'product_name', 'title', 'description'],
                'description': ['description', 'long_description', 'details'],
                'price': ['price', 'cost', 'wholesale_price', 'msrp'],
                'category': ['category', 'product_type', 'type'],
                'brand': ['brand', 'manufacturer'],
                'upc': ['upc', 'gtin', 'ean', 'barcode'],
                'weight': ['weight'],
                'dimensions': ['dimensions', 'size'],
                'status': ['status', 'availability', 'is_active']
            }
        
        # Get the vendor
        vendor = VendorController.get_by_id(vendor_id)
        if not vendor:
            return 0, [f"Vendor with ID {vendor_id} not found"]
        
        # Process each product
        for item in data:
            try:
                # Apply mapping
                product_data = {}
                for target_field, source_fields in mapping.items():
                    for source_field in source_fields:
                        if source_field in item and item[source_field]:
                            product_data[target_field] = item[source_field]
                            break
                
                # Make sure we have required fields
                if 'sku' not in product_data or not product_data['sku']:
                    errors.append(f"Missing required field 'sku' for item: {item}")
                    continue
                    
                if 'name' not in product_data or not product_data['name']:
                    errors.append(f"Missing required field 'name' for item: {item}")
                    continue
                
                # Set vendor ID
                product_data['vendor_id'] = vendor_id
                
                # Check if product already exists
                existing_product = ProductController.get_by_vendor_sku(vendor_id, product_data['sku'])
                
                if existing_product:
                    # Update existing product
                    ProductController.update(existing_product.id, product_data)
                else:
                    # Create new product
                    ProductController.create(product_data)
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Error processing item {item}: {str(e)}")
        
        return imported_count, errors
    
    @classmethod
    def _process_api_data(cls, items: List[Dict], vendor_id: int, mapping: Dict = None) -> Tuple[int, List[str]]:
        """Process data retrieved from API"""
        return cls._process_mapped_data(items, vendor_id, mapping)
    
    @classmethod
    def _extract_items(cls, data: Dict, items_path: str) -> List[Dict]:
        """Extract items from API response using a dot-notation path"""
        if not items_path:
            return data if isinstance(data, list) else [data]
        
        current = data
        for key in items_path.split('.'):
            if key in current:
                current = current[key]
            else:
                return []
        
        return current if isinstance(current, list) else [current]
    
    @classmethod
    def _has_next_page(cls, data: Dict, next_page_path: str) -> bool:
        """Check if API response has a next page"""
        if not next_page_path:
            return False
            
        parts = next_page_path.split('.')
        current = data
        
        for part in parts[:-1]:
            if part in current:
                current = current[part]
            else:
                return False
                
        return parts[-1] in current and current[parts[-1]] is not None
    
    @classmethod
    def _get_next_page_url(cls, data: Dict, next_page_path: str) -> str:
        """Get the URL for the next page"""
        if not next_page_path:
            return ""
            
        parts = next_page_path.split('.')
        current = data
        
        for part in parts:
            if part in current:
                current = current[part]
            else:
                return ""
                
        return current
    
    @classmethod
    def _matches_pattern(cls, filename: str, pattern: str) -> bool:
        """Check if a filename matches a pattern (simple wildcard support)"""
        if pattern == '*':
            return True
            
        if pattern.startswith('*') and pattern.endswith('*'):
            return pattern[1:-1] in filename
            
        if pattern.startswith('*'):
            return filename.endswith(pattern[1:])
            
        if pattern.endswith('*'):
            return filename.startswith(pattern[:-1])
            
        return filename == pattern
    
    @classmethod
    def import_from_sftp_multi(cls, sftp_configs, vendor_id, mapping=None):
        """
        Import products from multiple directories on an SFTP server
        
        Args:
            sftp_configs: List of dictionaries containing SFTP configurations
            vendor_id: ID of the vendor
            mapping: Optional dictionary mapping file columns to product fields
            
        Returns:
            Tuple containing (count of imported products, list of errors)
        """
        total_imported = 0
        all_errors = []
        
        for config in sftp_configs:
            try:
                imported, errors = cls.import_from_sftp(config, vendor_id, mapping)
                total_imported += imported
                all_errors.extend(errors)
            except Exception as e:
                all_errors.append(f"Error processing directory {config.get('directory', 'unknown')}: {str(e)}")
        
        return total_imported, all_errors