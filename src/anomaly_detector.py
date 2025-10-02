"""
Enhanced Anomaly Detection with Multiple Detection Methods
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import warnings
warnings.filterwarnings('ignore')

class AdvancedAnomalyDetector:
    def __init__(self, database):
        self.db = database
        self.amount_model = None
        self.vendor_profiles = {}
        
    def analyze_invoice(self, invoice_data, all_invoices=None):
        """Comprehensive anomaly analysis using multiple methods"""
        flags = []
        risk_score = 0
        anomaly_details = []
        
        # 1. Basic Business Rules
        basic_flags = self._check_business_rules(invoice_data, all_invoices)
        flags.extend(basic_flags)
        risk_score += len(basic_flags)
        
        # 2. Statistical Anomaly Detection
        statistical_flags = self._check_statistical_anomalies(invoice_data, all_invoices)
        flags.extend(statistical_flags)
        risk_score += len(statistical_flags) * 2  # Statistical anomalies are higher risk
        
        # 3. Vendor Behavior Analysis
        vendor_flags = self._check_vendor_behavior(invoice_data)
        flags.extend(vendor_flags)
        risk_score += len(vendor_flags)
        
        # 4. Temporal Anomalies
        temporal_flags = self._check_temporal_anomalies(invoice_data, all_invoices)
        flags.extend(temporal_flags)
        risk_score += len(temporal_flags)
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(risk_score, invoice_data['Total_Amount'])
        anomaly_type = self._categorize_anomaly(flags)
        
        # Prepare detailed anomaly information
        for flag in flags:
            anomaly_details.append({
                'type': flag,
                'severity': self._get_anomaly_severity(flag),
                'description': self._get_anomaly_description(flag, invoice_data),
                'amount_impact': self._calculate_amount_impact(flag, invoice_data)
            })
        
        return {
            'flags': flags,
            'risk_level': risk_level,
            'anomaly_type': anomaly_type,
            'risk_score': risk_score,
            'anomaly_details': anomaly_details
        }
    
    def _check_business_rules(self, invoice, all_invoices):
        """Check predefined business rules"""
        flags = []
        
        # Duplicate detection
        if self._is_duplicate_invoice(invoice, all_invoices):
            flags.append("POTENTIAL_DUPLICATE")
        
        # Extreme amount detection
        amount = invoice['Total_Amount']
        if amount > 50000:  # Very high threshold
            flags.append("EXTREME_AMOUNT_HIGH")
        elif amount < 10:   # Very low threshold
            flags.append("EXTREME_AMOUNT_LOW")
        
        # Round amount suspicion
        if amount % 1000 == 0 and amount > 5000:
            flags.append("ROUND_AMOUNT_SUSPICIOUS")
        
        # Tax calculation anomalies
        if 'Tax_Amount' in invoice and invoice['Tax_Amount'] > 0:
            expected_tax = round(invoice['Total_Amount'] * 0.1, 2)
            if abs(invoice['Tax_Amount'] - expected_tax) > 1.0:  # $1 tolerance
                flags.append("TAX_CALCULATION_ANOMALY")
        
        # Data quality issues
        if invoice.get('Vendor_Name') in ['UNKNOWN_VENDOR', 'NOT_FOUND']:
            flags.append("MISSING_VENDOR_INFO")
        
        if invoice.get('Invoice_ID') in ['NOT_FOUND', 'UNKNOWN']:
            flags.append("MISSING_INVOICE_ID")
        
        return flags
    
    def _check_statistical_anomalies(self, invoice, all_invoices):
        """Use ML algorithms for statistical anomaly detection"""
        flags = []
        
        if all_invoices is None or len(all_invoices) < 10:
            return flags
        
        try:
            # Prepare data for ML
            amounts = all_invoices['Total_Amount'].values.reshape(-1, 1)
            
            # Method 1: Isolation Forest
            if self.amount_model is None:
                self.amount_model = IsolationForest(
                    contamination=0.1, 
                    random_state=42,
                    n_estimators=100
                )
                self.amount_model.fit(amounts)
            
            # Predict current invoice
            prediction = self.amount_model.predict([[invoice['Total_Amount']]])
            if prediction[0] == -1:
                flags.append("STATISTICAL_OUTLIER")
            
            # Method 2: Z-score analysis
            mean_amount = amounts.mean()
            std_amount = amounts.std()
            z_score = abs((invoice['Total_Amount'] - mean_amount) / std_amount)
            
            if z_score > 3:  # 3 standard deviations
                flags.append("EXTREME_Z_SCORE")
            
            # Method 3: IQR (Interquartile Range) method
            Q1 = np.percentile(amounts, 25)
            Q3 = np.percentile(amounts, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            if invoice['Total_Amount'] < lower_bound or invoice['Total_Amount'] > upper_bound:
                flags.append("IQR_OUTLIER")
                
        except Exception as e:
            print(f"Statistical analysis error: {str(e)}")
        
        return flags
    
    def _check_vendor_behavior(self, invoice):
        """Analyze vendor-specific patterns"""
        flags = []
        vendor = invoice['Vendor_Name']
        amount = invoice['Total_Amount']
        
        # Skip if vendor is unknown
        if vendor in ['UNKNOWN_VENDOR', 'NOT_FOUND']:
            return flags
        
        # Get vendor historical data
        vendor_stats = self._get_vendor_statistics(vendor)
        
        if vendor_stats:
            avg_amount = vendor_stats['avg_amount']
            max_amount = vendor_stats['max_amount']
            std_amount = vendor_stats['std_amount']
            
            # Check for significant deviation from vendor average
            if avg_amount > 0:
                deviation_ratio = amount / avg_amount
                if deviation_ratio > 3:  # 300% of average
                    flags.append("VENDOR_AMOUNT_DEVIATION")
                
                # Check if amount is significantly higher than historical max
                if amount > max_amount * 1.5:  # 50% higher than historical max
                    flags.append("EXCEEDS_VENDOR_HISTORICAL_MAX")
        
        return flags
    
    def _check_temporal_anomalies(self, invoice, all_invoices):
        """Check for time-based anomalies"""
        flags = []
        
        # This would require date parsing and analysis
        # For now, implement basic checks
        
        # Check for weekend/holiday invoices (potential fraud pattern)
        try:
            from datetime import datetime
            invoice_date = datetime.strptime(invoice.get('Invoice_Date', ''), '%Y-%m-%d')
            if invoice_date.weekday() >= 5:  # Saturday or Sunday
                flags.append("WEEKEND_INVOICE")
        except:
            pass
        
        return flags
    
    def _is_duplicate_invoice(self, invoice, all_invoices):
        """Enhanced duplicate detection"""
        if all_invoices is None:
            return False
        
        vendor = invoice['Vendor_Name']
        invoice_id = invoice['Invoice_ID']
        amount = invoice['Total_Amount']
        
        if vendor == 'UNKNOWN_VENDOR' or invoice_id == 'NOT_FOUND':
            return False
        
        # Check exact duplicate
        exact_duplicates = all_invoices[
            (all_invoices['Vendor_Name'] == vendor) & 
            (all_invoices['Invoice_ID'] == invoice_id)
        ]
        if len(exact_duplicates) > 1:
            return True
        
        # Check fuzzy duplicates (same vendor, similar amount, close dates)
        try:
            from datetime import datetime, timedelta
            
            amount_tolerance = amount * 0.01  # 1% tolerance
            date_tolerance = timedelta(days=7)
            
            invoice_date = datetime.strptime(invoice.get('Invoice_Date', ''), '%Y-%m-%d')
            
            similar_invoices = all_invoices[
                (all_invoices['Vendor_Name'] == vendor) &
                (abs(all_invoices['Total_Amount'] - amount) <= amount_tolerance) &
                (all_invoices['Invoice_ID'] != invoice_id)  # Exclude self
            ]
            
            # Check dates for similar invoices
            for _, similar_inv in similar_invoices.iterrows():
                try:
                    similar_date = datetime.strptime(similar_inv.get('Invoice_Date', ''), '%Y-%m-%d')
                    if abs((similar_date - invoice_date).days) <= date_tolerance.days:
                        return True
                except:
                    continue
                    
        except Exception as e:
            print(f"Fuzzy duplicate check error: {str(e)}")
        
        return False
    
    def _get_vendor_statistics(self, vendor_name):
        """Get vendor historical statistics from database"""
        # In a real implementation, this would query the database
        # For now, return mock data or compute from available invoices
        return None
    
    def _calculate_risk_level(self, risk_score, amount):
        """Calculate risk level based on score and amount"""
        # Adjust score based on amount
        if amount > 10000:
            risk_score += 2
        elif amount > 5000:
            risk_score += 1
        
        if risk_score >= 5:
            return 'High'
        elif risk_score >= 3:
            return 'Medium'
        else:
            return 'Low'
    
    def _categorize_anomaly(self, flags):
        """Categorize the primary anomaly type"""
        if 'POTENTIAL_DUPLICATE' in flags:
            return 'Duplicate'
        elif any(flag.startswith('EXTREME_AMOUNT') for flag in flags):
            return 'Extreme Amount'
        elif any(flag in ['STATISTICAL_OUTLIER', 'EXTREME_Z_SCORE', 'IQR_OUTLIER'] for flag in flags):
            return 'Statistical Anomaly'
        elif any(flag.startswith('VENDOR_') for flag in flags):
            return 'Vendor Pattern Anomaly'
        elif any(flag in ['MISSING_VENDOR_INFO', 'MISSING_INVOICE_ID'] for flag in flags):
            return 'Data Quality Issue'
        else:
            return 'No Anomaly'
    
    def _get_anomaly_severity(self, anomaly_type):
        """Get severity level for an anomaly"""
        severity_map = {
            'POTENTIAL_DUPLICATE': 'High',
            'EXTREME_AMOUNT_HIGH': 'High',
            'STATISTICAL_OUTLIER': 'Medium',
            'EXTREME_Z_SCORE': 'High',
            'IQR_OUTLIER': 'Medium',
            'VENDOR_AMOUNT_DEVIATION': 'Medium',
            'EXCEEDS_VENDOR_HISTORICAL_MAX': 'High',
            'MISSING_VENDOR_INFO': 'Low',
            'MISSING_INVOICE_ID': 'Low',
            'TAX_CALCULATION_ANOMALY': 'Medium',
            'ROUND_AMOUNT_SUSPICIOUS': 'Low',
            'WEEKEND_INVOICE': 'Low'
        }
        return severity_map.get(anomaly_type, 'Low')
    
    def _get_anomaly_description(self, anomaly_type, invoice_data):
        """Get human-readable description for an anomaly"""
        descriptions = {
            'POTENTIAL_DUPLICATE': f"Possible duplicate of invoice {invoice_data['Invoice_ID']} from {invoice_data['Vendor_Name']}",
            'EXTREME_AMOUNT_HIGH': f"Extremely high amount: ${invoice_data['Total_Amount']:,.2f}",
            'EXTREME_AMOUNT_LOW': f"Extremely low amount: ${invoice_data['Total_Amount']:,.2f}",
            'STATISTICAL_OUTLIER': "Amount is statistical outlier based on historical data",
            'EXTREME_Z_SCORE': "Amount exceeds 3 standard deviations from mean",
            'VENDOR_AMOUNT_DEVIATION': "Amount significantly deviates from vendor's historical pattern",
            'TAX_CALCULATION_ANOMALY': "Tax amount doesn't match expected calculation"
        }
        return descriptions.get(anomaly_type, f"Anomaly detected: {anomaly_type}")
    
    def _calculate_amount_impact(self, anomaly_type, invoice_data):
        """Calculate potential financial impact of anomaly"""
        amount = invoice_data['Total_Amount']
        
        impact_map = {
            'POTENTIAL_DUPLICATE': amount,  # Full amount at risk for duplicates
            'EXTREME_AMOUNT_HIGH': amount * 0.1,  # 10% of amount for investigation
            'STATISTICAL_OUTLIER': amount * 0.05,  # 5% investigation cost
            'TAX_CALCULATION_ANOMALY': abs(invoice_data.get('Tax_Amount', 0) - (amount * 0.1))
        }
        
        return impact_map.get(anomaly_type, 0)