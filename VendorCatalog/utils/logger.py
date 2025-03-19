#!/usr/bin/env python3
"""
Logger utility for the VendorCatalog application.
"""
import logging
import os
from datetime import datetime

class Logger:
    """Simple logger utility for the application"""
    
    def __init__(self, name):
        """Initialize logger with a specific name
        
        Args:
            name: The name of the logger (usually the module name)
        """
        self.logger = logging.getLogger(name)
        
        # Configure logger if not already configured
        if not self.logger.handlers:
            self.logger.setLevel(logging.DEBUG)
            
            # Create logs directory if it doesn't exist
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # File handler for debug and above
            log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler for info and above
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Format for both handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers to logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message) 