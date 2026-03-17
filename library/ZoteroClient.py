#!/usr/bin/env python3
"""
Zotero Client Module

This module provides functionality to interact with the Zotero API to fetch files
and check file types based on item IDs.
"""

import requests
import os
import mimetypes
from typing import Optional, Dict, Any, Tuple

# Import default credentials from ConfigManager
try:
    from library.ConfigManager import get_zotero_api_key, get_zotero_user_id
    DEFAULT_API_KEY = get_zotero_api_key()
    DEFAULT_USER_ID = get_zotero_user_id()
except ImportError:
    DEFAULT_API_KEY = None
    DEFAULT_USER_ID = None


class ZoteroClient:
    """Client for interacting with Zotero API."""
    
    BASE_URL = "https://api.zotero.org"
    
    def __init__(self, api_key: str = None, user_id: str = None):
        """Initialize Zotero client with API key and user ID.
        
        Args:
            api_key: Zotero API key (uses default from ConfigManager if None)
            user_id: Zotero user ID (uses default from ConfigManager if None)
        """
        self.api_key = api_key if api_key is not None else DEFAULT_API_KEY
        self.user_id = user_id if user_id is not None else DEFAULT_USER_ID
        
        if not self.api_key or not self.user_id:
            raise ValueError("Zotero API key and user ID must be provided either as parameters or in ConfigManager")
        
        self.headers = {
            'Zotero-API-Key': self.api_key,
            'Accept': 'application/json'
        }
    
    def get_item_metadata(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific Zotero item.
        
        Args:
            item_id: Zotero item ID
            
        Returns:
            Dictionary containing item metadata or None if request fails
        """
        url = f"{self.BASE_URL}/users/{self.user_id}/items/{item_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching item metadata: {e}")
            return None
    
    def get_file_type(self, item_id: str) -> Optional[str]:
        """Get the file type of a Zotero item.
        
        Args:
            item_id: Zotero item ID
            
        Returns:
            File type (e.g., 'application/pdf') or None if cannot be determined
        """
        metadata = self.get_item_metadata(item_id)
        if not metadata:
            return None
        
        # Check if item has attachment information in data section
        if 'data' in metadata and 'contentType' in metadata['data']:
            return metadata['data']['contentType']
        
        # Check if item has link mode (imported file)
        if 'data' in metadata and metadata['data'].get('linkMode') == 'imported_file':
            # Try to determine file type from filename
            filename = metadata['data'].get('filename', '')
            if filename:
                # Guess mime type from filename extension
                mime_type, _ = mimetypes.guess_type(filename)
                return mime_type
        
        return None
    
    def download_file(self, item_id: str, save_path: str) -> bool:
        """Download a file from Zotero.
        
        Args:
            item_id: Zotero item ID
            save_path: Local path to save the downloaded file
            
        Returns:
            True if download successful, False otherwise
        """
        url = f"{self.BASE_URL}/users/{self.user_id}/items/{item_id}/file"
        
        try:
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()
            
            # Ensure directory exists
            dir_name = os.path.dirname(save_path)
            if dir_name:  # Only try to create directory if it's not empty
                os.makedirs(dir_name, exist_ok=True)
            
            # Save file
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
            return False
        except IOError as e:
            print(f"Error saving file: {e}")
            return False
    
    def get_pdf_file(self, item_id: str, save_path: str) -> Tuple[bool, Optional[str]]:
        """Get a PDF file from Zotero, checking file type first.
        
        Args:
            item_id: Zotero item ID
            save_path: Local path to save the PDF file
            
        Returns:
            Tuple of (success: bool, file_type: Optional[str])
            success: True if PDF was downloaded successfully
            file_type: The detected file type (e.g., 'application/pdf')
        """
        # Check file type first
        file_type = self.get_file_type(item_id)
        if not file_type:
            print(f"Could not determine file type for item {item_id}")
            return False, None
        
        # Check if it's a PDF
        if not file_type.startswith('application/pdf'):
            print(f"Item {item_id} is not a PDF file. Detected type: {file_type}")
            return False, file_type
        
        # Download the file
        success = self.download_file(item_id, save_path)
        if success:
            return True, file_type
        else:
            return False, file_type

    def get_pdf_url(self, item_id: str) -> Optional[str]:
        """Get the direct URL to a PDF file in Zotero.
        
        Args:
            item_id: Zotero item ID
            
        Returns:
            Direct URL to the PDF file, or None if not available
        """
        metadata = self.get_item_metadata(item_id)
        if not metadata:
            return None
        
        # Check if it's a PDF attachment
        file_type = self.get_file_type(item_id)
        if not file_type or not file_type.startswith('application/pdf'):
            return None
        
        # Try to get direct download URL
        if 'links' in metadata and 'enclosure' in metadata['links']:
            return metadata['links']['enclosure']['href']
        
        return None


def create_zotero_client(api_key: str = None, user_id: str = None) -> ZoteroClient:
    """Factory function to create a ZoteroClient instance.
    
    Args:
        api_key: Zotero API key (uses default from ConfigManager if None)
        user_id: Zotero user ID (uses default from ConfigManager if None)
        
    Returns:
        ZoteroClient instance
    """
    return ZoteroClient(api_key, user_id)