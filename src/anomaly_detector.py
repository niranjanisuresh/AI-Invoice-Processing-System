import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

class InvoiceAnomalyDetector:
    def __init__(self, historical_data):
        self.historical_data = historical_data
        self.amount_model = IsolationForest(contamination=0.15, random_state=42)
        self._train_model()
    
    def _train_model(self):
        """Train anomaly detection model on historical amounts"""
        if len(self.historical_data) > 0:
            amounts = self.historical_data[['Total_Amount']].fillna(0).values
            self.amount_model.fit(amounts)
    
    def check_duplicate(self, current_invoice, all_invoices):
        """Check for duplicate invoices"""
        vendor = current_invoice['Vendor_Name']
        invoice_id = current_invoice['Invoice_ID']
        
        if vendor == 'UNKNOWN_VENDOR' or invoice_id == 'NOT_FOUND':
            return False
            
        duplicates = all_invoices[
            (all_invoices['Vendor_Name'] == vendor) & 
            (all_invoices['Invoice_ID'] == invoice_id)
        ]
        return len(duplicates) > 1
    
    def check_amount_anomaly(self, current_amount):
        """Check if amount is anomalous using ML"""
        if len(self.historical_data) > 0 and current_amount > 0:
            prediction = self.amount_model.predict([[current_amount]])
            return prediction[0] == -1
        return False
    
    def check_extreme_amount(self, amount):
        """Check for extremely high or low amounts"""
        if amount > 50000:  # Very high amount threshold
            return True
        elif amount < 10:   # Very low amount threshold
            return True
        return False
    
    def analyze_invoice(self, invoice, all_invoices):
        """Run all checks on a single invoice"""
        flags = []
        
        if self.check_duplicate(invoice, all_invoices):
            flags.append("POTENTIAL_DUPLICATE")
        
        if self.check_amount_anomaly(invoice['Total_Amount']):
            flags.append("AMOUNT_ANOMALY")
        
        if self.check_extreme_amount(invoice['Total_Amount']):
            flags.append("EXTREME_AMOUNT")
        
        # Check for missing critical data
        if invoice.get('Vendor_Name') in ['UNKNOWN_VENDOR', 'NOT_FOUND']:
            flags.append("MISSING_VENDOR_INFO")
        
        if invoice.get('Invoice_ID') in ['NOT_FOUND', 'UNKNOWN']:
            flags.append("MISSING_INVOICE_ID")
        
        return flags