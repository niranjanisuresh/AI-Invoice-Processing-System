"""
Report Generator for Invoice Processing System
Generates downloadable PDF and CSV reports
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import os
from datetime import datetime
import numpy as np

class ReportGenerator:
    def __init__(self):
        self.report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def generate_all_reports(self, processed_data, results_data):
        """Generate all report types"""
        self.generate_pdf_report(processed_data, results_data)
        self.generate_csv_report(results_data)
        self.generate_executive_dashboard(processed_data, results_data)
    
    def generate_pdf_report(self, processed_data, results_data):
        """Generate comprehensive PDF report"""
        print("📄 Generating PDF report...")
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title Page
        pdf.add_page()
        self._add_title_page(pdf)
        
        # Executive Summary
        pdf.add_page()
        self._add_executive_summary(pdf, processed_data, results_data)
        
        # Anomaly Analysis
        pdf.add_page()
        self._add_anomaly_analysis(pdf, results_data)
        
        # Vendor Analysis
        pdf.add_page()
        self._add_vendor_analysis(pdf, processed_data, results_data)
        
        # Financial Insights
        pdf.add_page()
        self._add_financial_insights(pdf, processed_data, results_data)
        
        # High-Risk Invoices
        pdf.add_page()
        self._add_high_risk_invoices(pdf, results_data)
        
        # Save PDF
        pdf_output_path = "reports/pdf/invoice_analysis_report.pdf"
        pdf.output(pdf_output_path)
        print(f"✅ PDF report saved: {pdf_output_path}")
    
    def _add_title_page(self, pdf):
        """Add title page to PDF"""
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 50, 'Genpact Invoice Processing Report', 0, 1, 'C')
        pdf.set_font('Arial', 'I', 16)
        pdf.cell(0, 20, 'Intelligent Anomaly Detection System', 0, 1, 'C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 20, f'Generated on: {self.report_date}', 0, 1, 'C')
        pdf.ln(20)
        pdf.cell(0, 10, 'Confidential - For Internal Use Only', 0, 1, 'C')
    
    def _add_executive_summary(self, pdf, processed_data, results_data):
        """Add executive summary to PDF"""
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Executive Summary', 0, 1)
        pdf.ln(5)
        
        # Calculate KPIs
        total_invoices = len(processed_data)
        flagged_invoices = len(results_data[results_data['Requires_Review'] == True])
        automation_rate = ((total_invoices - flagged_invoices) / total_invoices) * 100
        total_amount = processed_data['Total_Amount'].sum()
        
        high_risk = len(results_data[results_data['Risk_Level'] == 'High'])
        medium_risk = len(results_data[results_data['Risk_Level'] == 'Medium'])
        
        # KPI Table
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Key Performance Indicators', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        kpis = [
            ['Total Invoices Processed', f'{total_invoices:,}'],
            ['Invoices Flagged for Review', f'{flagged_invoices:,}'],
            ['Automation Rate', f'{automation_rate:.1f}%'],
            ['Total Amount Processed', f'${total_amount:,.2f}'],
            ['High Risk Invoices', f'{high_risk}'],
            ['Medium Risk Invoices', f'{medium_risk}']
        ]
        
        for kpi in kpis:
            pdf.cell(100, 8, kpi[0], 1)
            pdf.cell(0, 8, kpi[1], 1, 1)
    
    def _add_anomaly_analysis(self, pdf, results_data):
        """Add anomaly analysis to PDF"""
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Anomaly Analysis', 0, 1)
        pdf.ln(5)
        
        # Anomaly distribution
        anomaly_counts = results_data['Anomaly_Type'].value_counts()
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Anomaly Distribution by Type', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        for anomaly_type, count in anomaly_counts.items():
            percentage = (count / len(results_data)) * 100
            pdf.cell(100, 8, anomaly_type, 1)
            pdf.cell(40, 8, f'{count}', 1)
            pdf.cell(0, 8, f'{percentage:.1f}%', 1, 1)
        
        pdf.ln(10)
        
        # Risk level distribution
        risk_counts = results_data['Risk_Level'].value_counts()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Risk Level Distribution', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        for risk_level, count in risk_counts.items():
            percentage = (count / len(results_data)) * 100
            pdf.cell(100, 8, risk_level, 1)
            pdf.cell(40, 8, f'{count}', 1)
            pdf.cell(0, 8, f'{percentage:.1f}%', 1, 1)
    
    def _add_vendor_analysis(self, pdf, processed_data, results_data):
        """Add vendor analysis to PDF"""
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Vendor Analysis', 0, 1)
        pdf.ln(5)
        
        # Top vendors by amount
        vendor_summary = processed_data.groupby('Vendor_Name').agg({
            'Total_Amount': ['sum', 'count', 'mean']
        }).round(2)
        
        # Vendor risk analysis
        vendor_risk = results_data.groupby('Vendor_Name').agg({
            'Risk_Level': lambda x: (x == 'High').sum(),
            'Total_Amount': 'sum'
        })
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Top Vendors by Invoice Volume and Risk', 0, 1)
        pdf.set_font('Arial', '', 8)
        
        # Table header
        pdf.cell(60, 8, 'Vendor', 1)
        pdf.cell(30, 8, 'Total Amount', 1)
        pdf.cell(20, 8, 'Invoices', 1)
        pdf.cell(25, 8, 'Avg Amount', 1)
        pdf.cell(0, 8, 'High Risk', 1, 1)
        
        # Table rows
        for vendor in vendor_summary.nlargest(10, ('Total_Amount', 'sum')).index:
            total = vendor_summary.loc[vendor, ('Total_Amount', 'sum')]
            count = vendor_summary.loc[vendor, ('Total_Amount', 'count')]
            avg = vendor_summary.loc[vendor, ('Total_Amount', 'mean')]
            high_risk_count = vendor_risk.loc[vendor, 'Risk_Level'] if vendor in vendor_risk.index else 0
            
            pdf.cell(60, 8, vendor[:25], 1)  # Truncate long names
            pdf.cell(30, 8, f'${total:,.0f}', 1)
            pdf.cell(20, 8, f'{count}', 1)
            pdf.cell(25, 8, f'${avg:,.0f}', 1)
            pdf.cell(0, 8, f'{high_risk_count}', 1, 1)
    
    def _add_financial_insights(self, pdf, processed_data, results_data):
        """Add financial insights to PDF"""
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Financial Insights', 0, 1)
        pdf.ln(5)
        
        # Amount statistics
        total_amount = processed_data['Total_Amount'].sum()
        avg_amount = processed_data['Total_Amount'].mean()
        max_amount = processed_data['Total_Amount'].max()
        min_amount = processed_data['Total_Amount'].min()
        
        # Anomalous amounts
        anomalous_amount = results_data[
            results_data['Requires_Review'] == True
        ]['Total_Amount'].sum()
        
        potential_savings = anomalous_amount * 0.1  # Assume 10% savings
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Financial Summary', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        financial_data = [
            ['Total Invoice Value', f'${total_amount:,.2f}'],
            ['Average Invoice Amount', f'${avg_amount:,.2f}'],
            ['Largest Invoice', f'${max_amount:,.2f}'],
            ['Smallest Invoice', f'${min_amount:,.2f}'],
            ['Value of Flagged Invoices', f'${anomalous_amount:,.2f}'],
            ['Estimated Potential Savings', f'${potential_savings:,.2f}']
        ]
        
        for item in financial_data:
            pdf.cell(100, 8, item[0], 1)
            pdf.cell(0, 8, item[1], 1, 1)
    
    def _add_high_risk_invoices(self, pdf, results_data):
        """Add high-risk invoices section to PDF"""
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'High-Risk Invoices Requiring Review', 0, 1)
        pdf.ln(5)
        
        high_risk = results_data[results_data['Risk_Level'] == 'High'].nlargest(20, 'Total_Amount')
        
        if len(high_risk) > 0:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(40, 8, 'Invoice ID', 1)
            pdf.cell(50, 8, 'Vendor', 1)
            pdf.cell(30, 8, 'Amount', 1)
            pdf.cell(0, 8, 'Anomaly Type', 1, 1)
            
            pdf.set_font('Arial', '', 8)
            for idx, invoice in high_risk.iterrows():
                pdf.cell(40, 8, invoice['Invoice_ID'][:15], 1)
                pdf.cell(50, 8, invoice['Vendor_Name'][:20], 1)
                pdf.cell(30, 8, f'${invoice["Total_Amount"]:,.0f}', 1)
                pdf.cell(0, 8, invoice['Anomaly_Type'][:25], 1, 1)
        else:
            pdf.set_font('Arial', 'I', 12)
            pdf.cell(0, 10, 'No high-risk invoices detected.', 0, 1)
    
    def generate_csv_report(self, results_data):
        """Generate detailed CSV report"""
        print("📊 Generating CSV report...")
        
        # Create enhanced CSV with all analysis details
        enhanced_report = results_data.copy()
        
        # Add additional calculated fields
        enhanced_report['Processing_Date'] = self.report_date
        enhanced_report['Amount_Category'] = enhanced_report['Total_Amount'].apply(
            lambda x: 'Very High (>$50K)' if x > 50000 
            else 'High ($10K-$50K)' if x > 10000 
            else 'Medium ($1K-$10K)' if x > 1000 
            else 'Low (<$1K)'
        )
        
        # Save CSV
        csv_output_path = "reports/csv/detailed_analysis.csv"
        enhanced_report.to_csv(csv_output_path, index=False)
        print(f"✅ CSV report saved: {csv_output_path}")
        
        # Also create a summary CSV
        summary_data = {
            'Report_Date': [self.report_date],
            'Total_Invoices': [len(results_data)],
            'Flagged_Invoices': [len(results_data[results_data['Requires_Review'] == True])],
            'High_Risk_Count': [len(results_data[results_data['Risk_Level'] == 'High'])],
            'Total_Amount_Processed': [results_data['Total_Amount'].sum()],
            'Total_Anomalous_Amount': [results_data[results_data['Requires_Review'] == True]['Total_Amount'].sum()]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv("reports/csv/executive_summary.csv", index=False)
    
    def generate_executive_dashboard(self, processed_data, results_data):
        """Generate executive dashboard visualizations"""
        # This creates additional charts for the report
        self._create_trend_analysis_chart(processed_data)
        self._create_vendor_risk_heatmap(processed_data, results_data)
    
    def _create_trend_analysis_chart(self, processed_data):
        """Create monthly trend analysis chart"""
        if 'Invoice_Date' in processed_data.columns:
            processed_data['Invoice_Date'] = pd.to_datetime(processed_data['Invoice_Date'])
            monthly_trends = processed_data.groupby(
                processed_data['Invoice_Date'].dt.to_period('M')
            ).agg({
                'Total_Amount': 'sum',
                'Invoice_ID': 'count'
            }).reset_index()
            
            monthly_trends['Invoice_Date'] = monthly_trends['Invoice_Date'].astype(str)
            
            plt.figure(figsize=(12, 6))
            plt.subplot(1, 2, 1)
            plt.plot(monthly_trends['Invoice_Date'], monthly_trends['Total_Amount'], marker='o')
            plt.title('Monthly Invoice Amount Trend')
            plt.xticks(rotation=45)
            plt.ylabel('Total Amount ($)')
            
            plt.subplot(1, 2, 2)
            plt.bar(monthly_trends['Invoice_Date'], monthly_trends['Invoice_ID'])
            plt.title('Monthly Invoice Volume')
            plt.xticks(rotation=45)
            plt.ylabel('Number of Invoices')
            
            plt.tight_layout()
            plt.savefig('reports/monthly_trends.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def _create_vendor_risk_heatmap(self, processed_data, results_data):
        """Create vendor risk heatmap"""
        vendor_analysis = results_data.groupby('Vendor_Name').agg({
            'Total_Amount': 'sum',
            'Risk_Level': lambda x: (x == 'High').sum(),
            'Invoice_ID': 'count'
        }).rename(columns={'Invoice_ID': 'Invoice_Count'})
        
        if len(vendor_analysis) > 1:
            vendor_analysis['Risk_Ratio'] = vendor_analysis['Risk_Level'] / vendor_analysis['Invoice_Count']
            
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                vendor_analysis[['Total_Amount', 'Risk_Ratio', 'Invoice_Count']].corr(),
                annot=True, cmap='coolwarm', center=0
            )
            plt.title('Vendor Metrics Correlation Heatmap')
            plt.tight_layout()
            plt.savefig('reports/vendor_risk_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()