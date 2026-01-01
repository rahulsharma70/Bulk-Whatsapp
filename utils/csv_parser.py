"""
CSV/Excel/TXT file parser for contact lists
Extracted from app.py for better separation of concerns
"""

import os
import re
import pandas as pd
from utils.logger import logger

def normalize_phone_number(phone):
    """
    Normalize phone number - remove spaces, dashes, and handle country codes
    
    Args:
        phone: Raw phone number string
    
    Returns:
        Normalized phone number with + prefix
    """
    # Remove all non-digit characters except +
    phone = re.sub(r'[^\d+]', '', str(phone))
    
    # Remove leading zeros
    phone = phone.lstrip('0')
    
    # If it doesn't start with +, add it (assuming it's a valid number)
    if not phone.startswith('+'):
        # If it starts with country code without +, add +
        if len(phone) >= 10:
            phone = '+' + phone
    
    return phone

def remove_duplicates(contacts):
    """
    Remove duplicate phone numbers while preserving order
    
    Args:
        contacts: List of phone numbers
    
    Returns:
        List of unique phone numbers
    """
    seen = set()
    unique_contacts = []
    for contact in contacts:
        if contact not in seen:
            seen.add(contact)
            unique_contacts.append(contact)
    return unique_contacts

def read_contacts_from_file(filepath):
    """
    Read contacts from CSV, Excel, or TXT file
    
    Args:
        filepath: Path to the contact file
    
    Returns:
        List of normalized phone numbers
    
    Raises:
        Exception: If file cannot be read or is invalid
    """
    contacts = []
    
    # Convert to absolute path
    filepath = os.path.abspath(filepath)
    
    # Check if file exists
    if not os.path.exists(filepath):
        # Try to find the file with different name variations
        upload_dir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        
        # List all files in upload directory for debugging
        if os.path.exists(upload_dir):
            available_files = os.listdir(upload_dir)
            raise Exception(
                f"File not found: {filepath}\n"
                f"Looking for: {filename}\n"
                f"Available files in uploads: {', '.join(available_files) if available_files else 'None'}\n"
                f"Please re-upload the file."
            )
        else:
            raise Exception(f"Upload directory not found: {upload_dir}")
    
    # Get file extension
    if '.' not in filepath:
        raise Exception("File has no extension. Please use .csv, .xlsx, .xls, or .txt files.")
    
    file_ext = filepath.rsplit('.', 1)[1].lower()
    
    try:
        if file_ext == 'txt':
            logger.info(f"Reading TXT file: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        contacts.append(normalize_phone_number(line))
        elif file_ext in ['csv', 'xlsx', 'xls']:
            logger.info(f"Reading {file_ext.upper()} file: {filepath}")
            if file_ext == 'csv':
                # Try different encodings for CSV
                try:
                    df = pd.read_csv(filepath, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(filepath, encoding='latin-1')
                    except:
                        df = pd.read_csv(filepath, encoding='iso-8859-1')
            else:
                df = pd.read_excel(filepath)
            
            # Try to find phone number column
            phone_col = None
            for col in df.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['phone', 'mobile', 'number', 'contact', 'whatsapp', 'mob']):
                    phone_col = col
                    break
            
            # If no phone column found, use first column
            if phone_col is None:
                phone_col = df.columns[0]
            
            logger.info(f"Using column '{phone_col}' for phone numbers")
            
            for phone in df[phone_col].dropna():
                normalized = normalize_phone_number(phone)
                if normalized:
                    contacts.append(normalized)
    except FileNotFoundError:
        raise Exception(f"File not found: {filepath}")
    except pd.errors.EmptyDataError:
        raise Exception("The file is empty. Please check your file and try again.")
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {str(e)}")
        raise Exception(f"Error reading file: {str(e)}")
    
    logger.info(f"Parsed {len(contacts)} contacts from {filepath}")
    return contacts
