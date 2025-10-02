"""
Genpact - Enhanced Invoice Processing System
With Database, Search, and Advanced Anomaly Detection
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
import warnings
warnings.filterwarnings('ignore')

# Add src directory to path
sys.path.append('src')

# Import enhanced modules
from invoice_processor import InvoiceProcessor
from database import InvoiceDB
from search_engine import InvoiceSearchEngine
from anomaly_detector import AdvancedAnomalyDetector
from dashboard import AnalyticsDashboard
from report_generator import ReportGenerator

class EnhancedInvoiceProcessingSystem:
    """Enhanced system with database, search, and advanced analytics"""
    
    def __init__(self):
        self.db = InvoiceDB()
        self.processor = InvoiceProcessor()
        self.search_engine = InvoiceSearchEngine(self.db)
        self.anomaly_detector = AdvancedAnomalyDetector(self.db)
        self.dashboard = AnalyticsDashboard()
        self.report_generator = ReportGenerator()
        self.processed_data = None
        self.analysis_results = None
        
    def setup_directories(self):
        """Create necessary directories"""
        directories = ['data', 'data/digital', 'data/scanned', 'data/output', 'reports', 'reports/pdf', 'reports/csv']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        print("✅ Directories and database setup completed")
    
    def generate_sample_data(self, num_digital=150, num_scanned=15):
        """Generate sample invoice data for demonstration"""
        print("\n📊 Generating sample data...")
        
        # Generate digital invoices
        digital_data = []
        vendors = ['Genpact_Vendor_A', 'Tech_Solutions_Inc', 'Global_Supplies_Ltd', 
                  'Office_Equipment_Co', 'IT_Services_Corp', 'Consulting_Partners_LLC']
        
        for i in range(num_digital):
            invoice_date = datetime.now() - timedelta(days=random.randint(1, 90))
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
                vendor = 'Tech_Solutions_Inc'
            elif i == 25:  # One extreme low
                amount = 5
                vendor = 'Office_Equipment_Co'
            elif i in [15, 16]:  # Duplicate
                amount = 12500
                vendor = 'Global_Supplies_Ltd'
                invoice_id = f'DUP-{5000}'
            else:
                amount = round(base_amount + random.uniform(-500, 500), 2)
                invoice_id = f'DIG-{5000 + i}'
            
            invoice = {
                'Invoice_ID': invoice_id if i not in [15, 16] else 'DUP-5000',
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
    
    def search_invoices_interactive(self):
        """Interactive search interface"""
        print("\n🔍 INVOICE SEARCH INTERFACE")
        print("=" * 50)
        
        while True:
            print("\nSearch Options:")
            print("1. Quick Search by Vendor")
            print("2. Advanced Search with Filters")
            print("3. View High-Risk Invoices")
            print("4. View Recent Invoices")
            print("5. Export Search Results")
            print("6. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self._quick_vendor_search()
            elif choice == '2':
                self._advanced_search()
            elif choice == '3':
                self._search_high_risk()
            elif choice == '4':
                self._search_recent()
            elif choice == '5':
                self._export_search_results()
            elif choice == '6':
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def _quick_vendor_search(self):
        """Quick search by vendor name"""
        vendor = input("Enter vendor name (or part of name): ").strip()
        if vendor:
            results = self.search_engine.search(search_term=vendor)
            self._display_search_results(results)
        else:
            print("❌ No vendor name provided.")
    
    def _advanced_search(self):
        """Advanced search with multiple filters"""
        print("\n🎯 Advanced Search Filters")
        filters = {}
        
        # Vendor filter
        vendor = input("Vendor name (leave empty to skip): ").strip()
        if vendor:
            filters['vendor'] = vendor
        
        # Amount range
        min_amount = input("Minimum amount (leave empty to skip): ").strip()
        if min_amount:
            try:
                filters['min_amount'] = float(min_amount)
            except ValueError:
                print("❌ Invalid amount format")
        
        max_amount = input("Maximum amount (leave empty to skip): ").strip()
        if max_amount:
            try:
                filters['max_amount'] = float(max_amount)
            except ValueError:
                print("❌ Invalid amount format")
        
        # Risk level
        print("\nRisk Levels: High, Medium, Low")
        risk_level = input("Risk level (leave empty to skip): ").strip()
        if risk_level and risk_level in ['High', 'Medium', 'Low']:
            filters['risk_level'] = risk_level
        
        # Date range
        start_date = input("Start date (YYYY-MM-DD, leave empty to skip): ").strip()
        if start_date:
            filters['start_date'] = start_date
        
        end_date = input("End date (YYYY-MM-DD, leave empty to skip): ").strip()
        if end_date:
            filters['end_date'] = end_date
        
        # Execute search
        results = self.search_engine.search(filters=filters)
        self._display_search_results(results)
    
    def _search_high_risk(self):
        """Search for high-risk invoices"""
        filters = {'risk_level': 'High'}
        results = self.search_engine.search(filters=filters)
        self._display_search_results(results, highlight_risk=True)
    
    def _search_recent(self):
        """Search for recent invoices"""
        filters = {
            'start_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        }
        results = self.search_engine.search(filters=filters)
        self._display_search_results(results)
    
    def _export_search_results(self):
        """Export search results to file"""
        print("\n📤 Export Search Results")
        filters = {}
        
        # Get basic filters
        vendor = input("Vendor name (leave empty for all): ").strip()
        if vendor:
            filters['vendor'] = vendor
        
        risk_level = input("Risk level (High/Medium/Low, leave empty for all): ").strip()
        if risk_level in ['High', 'Medium', 'Low']:
            filters['risk_level'] = risk_level
        
        format_choice = input("Export format (CSV/JSON, default CSV): ").strip().lower()
        format_type = format_choice if format_choice in ['csv', 'json'] else 'csv'
        
        # Execute search and export
        results = self.search_engine.search(filters=filters, per_page=1000)
        
        if not results['invoices'].empty:
            export_data = self.search_engine.export_search_results(filters, format_type)
            
            if format_type == 'csv':
                filename = f"reports/csv/invoice_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(filename, 'w') as f:
                    f.write(export_data)
                print(f"✅ Results exported to: {filename}")
            else:
                filename = f"reports/csv/invoice_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    f.write(export_data)
                print(f"✅ Results exported to: {filename}")
        else:
            print("❌ No invoices found matching your criteria.")
    
    def _display_search_results(self, results, highlight_risk=False):
        """Display search results in a formatted table"""
        if results['invoices'].empty:
            print("❌ No invoices found matching your criteria.")
            return
        
        invoices = results['invoices']
        total_count = results['total_count']
        page = results['page']
        total_pages = results['total_pages']
        
        print(f"\n📄 Search Results (Page {page}/{total_pages}, Total: {total_count} invoices)")
        print("=" * 100)
        print(f"{'Invoice ID':<12} {'Vendor':<20} {'Date':<12} {'Amount':<12} {'Risk':<8} {'Anomaly':<15} {'Status':<10}")
        print("-" * 100)
        
        for _, invoice in invoices.iterrows():
            risk_level = invoice.get('risk_level', 'Low')
            anomaly_type = invoice.get('anomaly_type', 'None')
            status = invoice.get('status', 'Pending')
            
            # Color coding for risk levels
            if highlight_risk and risk_level == 'High':
                risk_display = f"🚨{risk_level}"
            elif risk_level == 'Medium':
                risk_display = f"⚠️ {risk_level}"
            else:
                risk_display = f"✅ {risk_level}"
            
            print(f"{invoice['invoice_id']:<12} {invoice['vendor_name'][:18]:<20} "
                  f"{invoice['invoice_date']:<12} ${invoice['total_amount']:<11.2f} "
                  f"{risk_display:<8} {anomaly_type[:14]:<15} {status:<10}")
        
        print("-" * 100)
        
        # Show summary
        if not invoices.empty:
            total_amount = invoices['total_amount'].sum()
            high_risk_count = len(invoices[invoices['risk_level'] == 'High'])
            print(f"📊 Summary: ${total_amount:,.2f} total | {high_risk_count} high-risk invoices")
    
    def process_invoices(self):
        """Enhanced processing with database storage"""
        print("\n🔄 Processing invoices with enhanced anomaly detection...")
        
        # Process all invoices
        digital_path = 'data/digital/digital_invoices.csv'
        scanned_files = [f"data/scanned/{f}" for f in os.listdir('data/scanned') if f.endswith('.png')]
        
        self.processed_data = self.processor.process_all_invoices(digital_path, scanned_files)
        
        # Analyze and store each invoice
        self.analysis_results = []
        for idx, invoice in self.processed_data.iterrows():
            # Enhanced anomaly detection
            analysis_result = self.anomaly_detector.analyze_invoice(invoice, self.processed_data)
            
            # Prepare data for database
            db_invoice = {
                'invoice_id': invoice['Invoice_ID'],
                'vendor_name': invoice['Vendor_Name'],
                'invoice_date': invoice.get('Invoice_Date', '2024-01-01'),
                'due_date': invoice.get('Due_Date'),
                'total_amount': invoice['Total_Amount'],
                'tax_amount': invoice.get('Tax_Amount', 0),
                'item_description': invoice.get('Item_Description', ''),
                'payment_terms': invoice.get('Payment_Terms', ''),
                'department': invoice.get('Department', 'Unknown'),
                'source_type': invoice.get('Source_Type', 'Digital'),
                'risk_level': analysis_result['risk_level'],
                'anomaly_type': analysis_result['anomaly_type']
            }
            
            # Save to database
            self.db.save_invoice(db_invoice)
            
            # Save individual anomalies
            for anomaly in analysis_result['anomaly_details']:
                self.db.save_anomaly(
                    invoice['Invoice_ID'],
                    anomaly['type'],
                    anomaly['description'],
                    anomaly['severity'],
                    anomaly['amount_impact']
                )
            
            # Store for reporting
            result = {
                'Invoice_ID': invoice['Invoice_ID'],
                'Vendor_Name': invoice['Vendor_Name'],
                'Total_Amount': invoice['Total_Amount'],
                'Invoice_Date': invoice.get('Invoice_Date', 'N/A'),
                'Source_Type': invoice.get('Source_Type', 'Unknown'),
                'Department': invoice.get('Department', 'Unknown'),
                'Flags': analysis_result['flags'],
                'Flag_Count': len(analysis_result['flags']),
                'Requires_Review': len(analysis_result['flags']) > 0,
                'Risk_Level': analysis_result['risk_level'],
                'Anomaly_Type': analysis_result['anomaly_type'],
                'Risk_Score': analysis_result['risk_score']
            }
            self.analysis_results.append(result)
        
        self.analysis_results_df = pd.DataFrame(self.analysis_results)
        
        print(f"✅ Processing completed: {len(self.processed_data)} invoices analyzed and stored in database")
        return self.analysis_results_df
    
    def show_database_stats(self):
        """Display database statistics"""
        print("\n📊 DATABASE STATISTICS")
        print("=" * 50)
        
        stats = self.db.get_invoice_stats()
        
        if stats:
            # Basic counts
            total_invoices = stats['total_invoices'].iloc[0]['count']
            total_amount = stats['total_amount'].iloc[0]['total'] or 0
            avg_amount = stats['avg_amount'].iloc[0]['avg'] or 0
            high_risk_count = stats['high_risk_count'].iloc[0]['count']
            
            print(f"Total Invoices: {total_invoices:,}")
            print(f"Total Amount: ${total_amount:,.2f}")
            print(f"Average Invoice: ${avg_amount:,.2f}")
            print(f"High Risk Invoices: {high_risk_count}")
            
            # Risk level distribution
            if not stats['by_risk_level'].empty:
                print("\nRisk Level Distribution:")
                for _, row in stats['by_risk_level'].iterrows():
                    print(f"  {row['risk_level']}: {row['count']} invoices")
            
            # Top vendors
            if not stats['by_vendor'].empty:
                print("\nTop 5 Vendors by Amount:")
                for _, row in stats['by_vendor'].head(5).iterrows():
                    print(f"  {row['vendor_name']}: ${row['total_amount']:,.2f} ({row['invoice_count']} invoices)")
        
        else:
            print("❌ No statistics available.")
    
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
        
        print("✅ Reports generated successfully")
        print(f"   - Analysis results: data/output/anomaly_analysis_results.csv")
        print(f"   - Processed data: data/output/processed_invoices.csv")
        print(f"   - Downloadable PDF: reports/pdf/invoice_analysis_report.pdf")
        print(f"   - Downloadable CSV: reports/csv/detailed_analysis.csv")
        print(f"   - Visualizations: reports/")
    
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
    
    def run_enhanced_pipeline(self):
        """Run the complete enhanced pipeline"""
        print("🚀 GENPACT ENHANCED INVOICE PROCESSING SYSTEM")
        print("=" * 60)
        
        try:
            # Step 1: Setup
            self.setup_directories()
            
            # Step 2: Generate sample data
            self.generate_sample_data()
            
            # Step 3: Process invoices with enhanced detection
            self.process_invoices()
            
            # Step 4: Generate reports
            self.generate_reports()
            
            # Step 5: Show database statistics
            self.show_database_stats()
            
            # Step 6: Show high-risk invoices
            self.show_high_risk_invoices()
            
            print("\n🎯 ENHANCED PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
            print("\n📊 New Features Available:")
            print("   - Database storage with SQLite")
            print("   - Advanced search and filtering")
            print("   - Enhanced anomaly detection")
            print("   - Interactive search interface")
            print("   - Export capabilities")
            
        except Exception as e:
            print(f"❌ Error in pipeline execution: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Enhanced main function with new features"""
    system = EnhancedInvoiceProcessingSystem()
    
    while True:
        print("\n" + "="*60)
        print("🏢 GENPACT - Enhanced Invoice Processing System")
        print("="*60)
        print("1. Run Complete Enhanced Pipeline")
        print("2. Search Invoices")
        print("3. Database Statistics")
        print("4. Process Invoices Only")
        print("5. Generate Reports")
        print("6. Show High-Risk Invoices")
        print("7. Download PDF Report")
        print("8. Download CSV Report")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            system.run_enhanced_pipeline()
        elif choice == '2':
            system.search_invoices_interactive()
        elif choice == '3':
            system.show_database_stats()
        elif choice == '4':
            system.process_invoices()
        elif choice == '5':
            system.generate_reports()
        elif choice == '6':
            system.show_high_risk_invoices()
        elif choice == '7':
            if system.analysis_results_df is not None:
                system.report_generator.generate_pdf_report(system.processed_data, system.analysis_results_df)
            else:
                print("❌ Please process invoices first")
        elif choice == '8':
            if system.analysis_results_df is not None:
                system.report_generator.generate_csv_report(system.analysis_results_df)
            else:
                print("❌ Please process invoices first")
        elif choice == '9':
            print("👋 Thank you for using the Enhanced Invoice Processing System!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()