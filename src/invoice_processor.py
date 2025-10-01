import pandas as pd
import pytesseract
from PIL import Image
import re

class InvoiceProcessor:
    def __init__(self):
        self.extracted_data = []
    
    def extract_from_scanned(self, image_path):
        """Extract data from scanned invoice images"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            
            # Enhanced pattern matching for invoice data
            patterns = {
                'invoice_id': r'Invoice Number:\s*([A-Z0-9-]+)',
                'amount': r'Total Amount:\s*\$?([0-9,]+\.?[0-9]*)',
                'vendor': r'Vendor:\s*([A-Za-z_]+)',
                'date': r'Date:\s*(\d{4}-\d{2}-\d{2})'
            }
            
            extracted = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, text)
                extracted[key] = match.group(1) if match else None
            
            # Clean amount
            if extracted['amount']:
                extracted['amount'] = float(extracted['amount'].replace(',', ''))
            
            return {
                'Invoice_ID': extracted['invoice_id'] or 'NOT_FOUND',
                'Vendor_Name': extracted['vendor'] or 'UNKNOWN_VENDOR',
                'Total_Amount': extracted['amount'] or 0.0,
                'Invoice_Date': extracted['date'] or '2024-01-01',
                'Source_Type': 'Scanned'
            }
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return None
    
    def extract_from_digital(self, csv_path):
        """Extract data from digital invoices (CSV)"""
        df = pd.read_csv(csv_path)
        df['Source_Type'] = 'Digital'
        return df
    
    def process_all_invoices(self, digital_path, scanned_paths):
        """Process both digital and scanned invoices"""
        self.extracted_data = []
        
        # Process digital invoices
        digital_data = self.extract_from_digital(digital_path)
        self.extracted_data.extend(digital_data.to_dict('records'))
        
        # Process scanned invoices
        for scanned_path in scanned_paths:
            scanned_data = self.extract_from_scanned(scanned_path)
            if scanned_data:
                self.extracted_data.append(scanned_data)
        
        return pd.DataFrame(self.extracted_data)