"""
FIN AI LEDGER
Enhanced Version with Advanced Reporting & Visualizations
Author: Niranjani 
Date: [June 2024]
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from datetime import datetime, timedelta
import random
import re
from PIL import Image, ImageDraw
import pytesseract
from sklearn.ensemble import IsolationForest
from fpdf import FPDF
import warnings
warnings.filterwarnings('ignore')

# Add src directory to path
sys.path.append('src')

# Import custom modules
from invoice_processor import InvoiceProcessor
from anomaly_detector import InvoiceAnomalyDetector
from dashboard import AnalyticsDashboard
from report_generator import ReportGenerator

class InvoiceProcessingSystem:
    """Main class for the Intelligent Invoice Processing System"""
    
    def __init__(self):
        self.processor = InvoiceProcessor()
        self.detector = None
        self.dashboard = AnalyticsDashboard()
        self.report_generator = ReportGenerator()
        self.processed_data = None
        self.analysis_results = None
        
    def setup_directories(self):
        """Create necessary directories for the project"""
        directories = ['data', 'data/digital', 'data/scanned', 'data/output', 'reports', 'reports/pdf', 'reports/csv']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        print("✅ Directories setup completed")
    
    def generate_sample_data(self, num_digital=150, num_scanned=20):
        """Generate sample invoice data for demonstration with realistic trends"""
        print("\n📊 Generating sample data...")
        
        # Generate digital invoices with realistic patterns
        digital_data = []
        vendors = ['Genpact_Vendor_A', 'Tech_Solutions_Inc', 'Global_Supplies_Ltd', 
                  'Office_Equipment_Co', 'IT_Services_Corp', 'Consulting_Partners_LLC']
        
        # Create some intentional anomalies
        anomaly_invoices = [
            {'vendor': 'Tech_Solutions_Inc', 'amount': 75000, 'type': 'EXTREME_HIGH'},
            {'vendor': 'Office_Equipment_Co', 'amount': 5, 'type': 'EXTREME_LOW'},
            {'vendor': 'Global_Supplies_Ltd', 'amount': 25000, 'type': 'DUPLICATE_CANDIDATE'},
        ]
        
        for i in range(num_digital):
            # Create realistic date distribution
            base_date = datetime.now() - timedelta(days=120)
            invoice_date = base_date + timedelta(days=random.randint(0, 90))
            due_date = invoice_date + timedelta(days=random.randint(10, 45))
            
            # Vendor-specific amount patterns
            vendor = random.choice(vendors)
            if vendor == 'Tech_Solutions_Inc':
                base_amount = random.uniform(1000, 15000)
            elif vendor == 'Office_Equipment_Co':
                base_amount = random.uniform(200, 5000)
            else:
                base_amount = random.uniform(500, 10000)
            
            # Add some intentional anomalies
            if i == 10:  # One extreme high
                amount = 75000
            elif i == 25:  # One extreme low
                amount = 5
            elif i in [15, 16]:  # Duplicate
                amount = 12500
                vendor = 'Global_Supplies_Ltd'
                invoice_id = f'DUP-{5000}'
            else:
                amount = round(base_amount + random.uniform(-500, 500), 2)
            
            invoice = {
                'Invoice_ID': f'DIG-{5000 + i}' if i not in [15, 16] else 'DUP-5000',
                'Vendor_Name': vendor,
                'Invoice_Date': invoice_date.strftime('%Y-%m-%d'),
                'Due_Date': due_date.strftime('%Y-%m-%d'),
                'Total_Amount': amount,
                'Tax_Amount': round(amount * 0.1, 2),
                'Item_Description': f'Professional Services {random.randint(1, 100)}',
                'Payment_Terms': f'Net {random.randint(15, 45)}',
                'Department': random.choice(['IT', 'Finance', 'Operations', 'HR', 'Marketing'])
            }
            digital_data.append(invoice)
        
        # Save digital invoices
        digital_df = pd.DataFrame(digital_data)
        digital_df.to_csv('data/digital/digital_invoices.csv', index=False)
        
        # Generate scanned invoices
        scanned_files = []
        for i in range(num_scanned):
            filename = self._create_scanned_invoice_image(
                f"SCAN-{6000 + i}", 
                random.choice(vendors),
                round(random.uniform(800, 15000), 2),
                (datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d')
            )
            scanned_files.append(filename)
        
        print(f"✅ Generated {num_digital} digital invoices and {num_scanned} scanned invoices")
        return digital_df, scanned_files
    
    def _create_scanned_invoice_image(self, invoice_id, vendor, amount, date):
        """Create a simulated scanned invoice image"""
        img = Image.new('RGB', (600, 300), color='white')
        d = ImageDraw.Draw(img)
        
        # Add invoice content
        d.rectangle([10, 10, 590, 290], outline='black', width=2)
        
        # Title
        d.text((50, 30), "COMMERCIAL INVOICE", fill='black')
        d.line([50, 50, 550, 50], fill='black', width=1)
        
        # Invoice details
        d.text((50, 70), f"Invoice Number: {invoice_id}", fill='black')
        d.text((50, 100), f"Vendor: {vendor}", fill='black')
        d.text((50, 130), f"Date: {date}", fill='black')
        d.text((50, 160), f"Total Amount: ${amount:,.2f}", fill='black')
        d.text((50, 190), "Terms: Net 30 Days", fill='black')
        d.text((50, 220), "Status: Pending Payment", fill='black')
        
        # Add some "noise" to simulate scanning
        for _ in range(200):
            x = random.randint(0, 599)
            y = random.randint(0, 299)
            d.point((x, y), fill=(200, 200, 200))
        
        filename = f"data/scanned/scanned_invoice_{invoice_id}.png"
        img.save(filename)
        return filename
    
    def process_invoices(self):
        """Main processing pipeline"""
        print("\n🔄 Processing invoices...")
        
        # Process all invoices
        digital_path = 'data/digital/digital_invoices.csv'
        scanned_files = [f"data/scanned/{f}" for f in os.listdir('data/scanned') if f.endswith('.png')]
        
        self.processed_data = self.processor.process_all_invoices(digital_path, scanned_files)
        
        # Initialize anomaly detector with processed data
        self.detector = InvoiceAnomalyDetector(self.processed_data)
        
        # Analyze for anomalies
        self.analysis_results = []
        for idx, invoice in self.processed_data.iterrows():
            flags = self.detector.analyze_invoice(invoice, self.processed_data)
            
            result = {
                'Invoice_ID': invoice['Invoice_ID'],
                'Vendor_Name': invoice['Vendor_Name'],
                'Total_Amount': invoice['Total_Amount'],
                'Invoice_Date': invoice.get('Invoice_Date', 'N/A'),
                'Source_Type': invoice.get('Source_Type', 'Unknown'),
                'Department': invoice.get('Department', 'Unknown'),
                'Flags': flags,
                'Flag_Count': len(flags),
                'Requires_Review': len(flags) > 0,
                'Risk_Level': self._calculate_risk_level(flags, invoice['Total_Amount']),
                'Anomaly_Type': self._categorize_anomaly(flags, invoice['Total_Amount'])
            }
            self.analysis_results.append(result)
        
        self.analysis_results_df = pd.DataFrame(self.analysis_results)
        
        print(f"✅ Processing completed: {len(self.processed_data)} invoices analyzed")
        return self.analysis_results_df
    
    def _calculate_risk_level(self, flags, amount):
        """Calculate risk level based on flags and amount"""
        risk_score = len(flags)
        if amount > 10000:
            risk_score += 1
        if 'POTENTIAL_DUPLICATE' in flags:
            risk_score += 2
        if 'EXTREME_AMOUNT' in flags:
            risk_score += 2
        
        if risk_score >= 3:
            return 'High'
        elif risk_score >= 2:
            return 'Medium'
        else:
            return 'Low'
    
    def _categorize_anomaly(self, flags, amount):
        """Categorize the type of anomaly"""
        if 'POTENTIAL_DUPLICATE' in flags:
            return 'Duplicate'
        elif 'EXTREME_AMOUNT' in flags:
            return 'Extreme Amount'
        elif 'AMOUNT_ANOMALY' in flags:
            return 'Statistical Anomaly'
        elif 'MISSING_VENDOR_INFO' in flags or 'MISSING_INVOICE_ID' in flags:
            return 'Data Quality Issue'
        else:
            return 'No Anomaly'
    
    def generate_reports(self):
        """Generate comprehensive reports and analytics"""
        print("\n📈 Generating reports and analytics...")
        
        if self.analysis_results_df is None or self.processed_data is None:
            print("❌ No data available for reporting. Please process invoices first.")
            return
        
        # Generate enhanced dashboard with advanced charts
        self.dashboard.create_enhanced_dashboard(self.processed_data, self.analysis_results_df)
        
        # Generate downloadable reports
        self.report_generator.generate_all_reports(self.processed_data, self.analysis_results_df)
        
        # Save analysis results
        self.analysis_results_df.to_csv('data/output/anomaly_analysis_results.csv', index=False)
        self.processed_data.to_csv('data/output/processed_invoices.csv', index=False)
        
        # Generate summary report
        self._generate_summary_report()
        
        print("✅ Reports generated successfully")
        print(f"   - Analysis results: data/output/anomaly_analysis_results.csv")
        print(f"   - Processed data: data/output/processed_invoices.csv")
        print(f"   - Downloadable PDF: reports/pdf/invoice_analysis_report.pdf")
        print(f"   - Downloadable CSV: reports/csv/detailed_analysis.csv")
        print(f"   - Visualizations: reports/")
    
    def _generate_summary_report(self):
        """Generate a text summary report"""
        total_invoices = len(self.processed_data)
        flagged_invoices = len(self.analysis_results_df[self.analysis_results_df['Requires_Review'] == True])
        automation_rate = ((total_invoices - flagged_invoices) / total_invoices) * 100
        total_amount = self.processed_data['Total_Amount'].sum()
        
        high_risk = len(self.analysis_results_df[self.analysis_results_df['Risk_Level'] == 'High'])
        medium_risk = len(self.analysis_results_df[self.analysis_results_df['Risk_Level'] == 'Medium'])
        
        # Calculate potential savings from catching anomalies
        anomalous_amount = self.analysis_results_df[
            self.analysis_results_df['Requires_Review'] == True
        ]['Total_Amount'].sum()
        potential_savings = anomalous_amount * 0.1  # Assume 10% of anomalous amounts are actual losses
        
        report_content = f"""
FinAI Ledger
============================================
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY:
-----------------
Total Invoices Processed: {total_invoices:,}
Invoices Flagged for Review: {flagged_invoices:,}
Automation Rate: {automation_rate:.1f}%
Total Amount Processed: ${total_amount:,.2f}
Potential Savings: ${potential_savings:,.2f}

RISK ASSESSMENT:
---------------
High Risk Invoices: {high_risk:,}
Medium Risk Invoices: {medium_risk:,}
Low Risk Invoices: {total_invoices - high_risk - medium_risk:,}

ANOMALY BREAKDOWN:
-----------------
"""
        # Count different flag types
        flag_counts = {}
        anomaly_types = {}
        
        for flags in self.analysis_results_df['Flags']:
            for flag in flags:
                flag_counts[flag] = flag_counts.get(flag, 0) + 1
        
        for anomaly_type in self.analysis_results_df['Anomaly_Type']:
            anomaly_types[anomaly_type] = anomaly_types.get(anomaly_type, 0) + 1
        
        for flag_type, count in flag_counts.items():
            report_content += f"{flag_type}: {count} occurrences\n"
        
        report_content += f"\nANOMALY CATEGORIES:\n"
        report_content += f"--------------------\n"
        for anomaly_type, count in anomaly_types.items():
            report_content += f"{anomaly_type}: {count} invoices\n"
        
        # Top vendors by amount and anomalies
        vendor_summary = self.processed_data.groupby('Vendor_Name').agg({
            'Total_Amount': ['sum', 'mean', 'count']
        }).round(2)
        
        # Vendor risk analysis
        vendor_risk = self.analysis_results_df.groupby('Vendor_Name').agg({
            'Risk_Level': lambda x: (x == 'High').sum(),
            'Total_Amount': 'sum'
        })
        
        report_content += f"\nTOP VENDORS ANALYSIS:\n"
        report_content += f"---------------------\n"
        for vendor in vendor_summary.nlargest(5, ('Total_Amount', 'sum')).index:
            total = vendor_summary.loc[vendor, ('Total_Amount', 'sum')]
            count = vendor_summary.loc[vendor, ('Total_Amount', 'count')]
            high_risk_count = vendor_risk.loc[vendor, 'Risk_Level'] if vendor in vendor_risk.index else 0
            report_content += f"{vendor}: ${total:,.2f} ({count} invoices, {high_risk_count} high-risk)\n"
        
        # Save report
        with open('reports/executive_summary.txt', 'w') as f:
            f.write(report_content)
        
        print(report_content)
    
    def show_high_risk_invoices(self):
        """Display high-risk invoices requiring immediate attention"""
        if self.analysis_results_df is None:
            print("❌ No analysis results available.")
            return
        
        high_risk = self.analysis_results_df[
            self.analysis_results_df['Risk_Level'] == 'High'
        ].sort_values('Total_Amount', ascending=False)
        
        if len(high_risk) > 0:
            print("\n🚨 HIGH RISK INVOICES REQUIRING IMMEDIATE REVIEW:")
            print("=" * 80)
            for idx, invoice in high_risk.iterrows():
                print(f"Invoice ID: {invoice['Invoice_ID']}")
                print(f"Vendor: {invoice['Vendor_Name']}")
                print(f"Amount: ${invoice['Total_Amount']:,.2f}")
                print(f"Anomaly Type: {invoice['Anomaly_Type']}")
                print(f"Flags: {', '.join(invoice['Flags'])}")
                print(f"Source: {invoice['Source_Type']}")
                print("-" * 80)
        else:
            print("✅ No high-risk invoices detected.")
    
    def run_complete_pipeline(self):
        """Run the complete invoice processing pipeline"""
        print("🚀 FIN AI LEDGER")
        print("=" * 55)
        
        try:
            # Step 1: Setup
            self.setup_directories()
            
            # Step 2: Generate sample data (comment out if using real data)
            self.generate_sample_data()
            
            # Step 3: Process invoices
            self.process_invoices()
            
            # Step 4: Generate reports
            self.generate_reports()
            
            # Step 5: Show critical findings
            self.show_high_risk_invoices()
            
            print("\n🎯 PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
            print("\n📊 Next Steps:")
            print("   - Review high-risk invoices in the console above")
            print("   - Check 'reports/' folder for detailed analytics")
            print("   - Download PDF report: reports/pdf/invoice_analysis_report.pdf")
            print("   - Download CSV data: reports/csv/detailed_analysis.csv")
            
        except Exception as e:
            print(f"❌ Error in pipeline execution: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    system = InvoiceProcessingSystem()
    
    while True:
        print("\n" + "="*60)
        print("🏢 FIN AI LEDGER")
        print("="*60)
        print("1. Run Complete Pipeline (Recommended)")
        print("2. Generate Sample Data Only")
        print("3. Process Existing Invoices")
        print("4. Generate Reports Only")
        print("5. Show High-Risk Invoices")
        print("6. Download PDF Report")
        print("7. Download CSV Report")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            system.run_complete_pipeline()
        elif choice == '2':
            system.setup_directories()
            system.generate_sample_data()
        elif choice == '3':
            system.process_invoices()
        elif choice == '4':
            system.generate_reports()
        elif choice == '5':
            system.show_high_risk_invoices()
        elif choice == '6':
            if system.analysis_results_df is not None:
                system.report_generator.generate_pdf_report(system.processed_data, system.analysis_results_df)
            else:
                print("❌ Please process invoices first")
        elif choice == '7':
            if system.analysis_results_df is not None:
                system.report_generator.generate_csv_report(system.analysis_results_df)
            else:
                print("❌ Please process invoices first")
        elif choice == '8':
            print("👋 Thank you for using the Invoice Processing System!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()