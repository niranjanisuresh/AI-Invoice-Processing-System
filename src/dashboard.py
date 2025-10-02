import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime

class AnalyticsDashboard:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.figsize = (16, 12)
        self.colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
    
    def create_enhanced_dashboard(self, processed_data, results_data):
        """Create an enhanced analytics dashboard with advanced visualizations"""
        fig = plt.figure(figsize=self.figsize)
        fig.suptitle('InvoiceIQ Analytics Dashboard', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        # Create grid layout
        gs = fig.add_gridspec(3, 3)
        
        # 1. Anomaly Distribution (Pie Chart)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_anomaly_pie_chart(results_data, ax1)
        
        # 2. Risk Level Distribution (Pie Chart)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_risk_pie_chart(results_data, ax2)
        
        # 3. Amount Distribution with Anomalies
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_amount_distribution_with_anomalies(processed_data, results_data, ax3)
        
        # 4. Top Vendors by Amount
        ax4 = fig.add_subplot(gs[1, 0])
        self._plot_top_vendors(processed_data, ax4)
        
        # 5. Vendor Risk Analysis
        ax5 = fig.add_subplot(gs[1, 1])
        self._plot_vendor_risk_analysis(results_data, ax5)
        
        # 6. Monthly Trends
        ax6 = fig.add_subplot(gs[1, 2])
        self._plot_monthly_trends(processed_data, ax6)
        
        # 7. Anomaly Types Breakdown
        ax7 = fig.add_subplot(gs[2, 0])
        self._plot_anomaly_types(results_data, ax7)
        
        # 8. Amount vs Risk Scatter Plot
        ax8 = fig.add_subplot(gs[2, 1])
        self._plot_amount_risk_scatter(results_data, ax8)
        
        # 9. Summary Statistics
        ax9 = fig.add_subplot(gs[2, 2])
        self._plot_enhanced_summary_stats(processed_data, results_data, ax9)
        
        plt.tight_layout()
        plt.savefig('reports/enhanced_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _plot_anomaly_pie_chart(self, results_data, ax):
        """Plot pie chart of anomaly distribution"""
        anomaly_counts = results_data['Anomaly_Type'].value_counts()
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(anomaly_counts)))
        wedges, texts, autotexts = ax.pie(
            anomaly_counts.values, 
            labels=anomaly_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Anomaly Types Distribution', fontweight='bold')
    
    def _plot_risk_pie_chart(self, results_data, ax):
        """Plot pie chart of risk level distribution"""
        risk_counts = results_data['Risk_Level'].value_counts()
        colors = {'High': '#FF6B6B', 'Medium': '#FFD166', 'Low': '#06D6A0'}
        
        risk_colors = [colors.get(risk, 'gray') for risk in risk_counts.index]
        
        wedges, texts, autotexts = ax.pie(
            risk_counts.values, 
            labels=risk_counts.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=risk_colors
        )
        
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        ax.set_title('Risk Level Distribution', fontweight='bold')
    
    def _plot_amount_distribution_with_anomalies(self, processed_data, results_data, ax):
        """Plot amount distribution with anomalies highlighted"""
        normal_invoices = results_data[results_data['Risk_Level'] == 'Low']
        risky_invoices = results_data[results_data['Risk_Level'].isin(['Medium', 'High'])]
        
        ax.hist(normal_invoices['Total_Amount'], bins=20, alpha=0.7, 
               label='Normal', color='green', edgecolor='black')
        ax.hist(risky_invoices['Total_Amount'], bins=20, alpha=0.7,
               label='Risky', color='red', edgecolor='black')
        
        ax.set_xlabel('Invoice Amount ($)')
        ax.set_ylabel('Frequency')
        ax.set_title('Amount Distribution with Anomalies', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_top_vendors(self, processed_data, ax):
        """Plot top vendors by total amount"""
        vendor_totals = processed_data.groupby('Vendor_Name')['Total_Amount'].sum().nlargest(8)
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(vendor_totals)))
        bars = ax.bar(range(len(vendor_totals)), vendor_totals.values, color=colors)
        
        ax.set_xlabel('Vendors')
        ax.set_ylabel('Total Amount ($)')
        ax.set_title('Top Vendors by Total Amount', fontweight='bold')
        ax.set_xticks(range(len(vendor_totals)))
        ax.set_xticklabels([v[:15] + '...' if len(v) > 15 else v for v in vendor_totals.index], 
                          rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height/1000:.0f}K', ha='center', va='bottom', fontweight='bold')
    
    def _plot_vendor_risk_analysis(self, results_data, ax):
        """Plot vendor risk analysis"""
        vendor_risk = results_data.groupby('Vendor_Name').agg({
            'Risk_Level': lambda x: (x == 'High').sum(),
            'Invoice_ID': 'count'
        }).rename(columns={'Invoice_ID': 'Total_Invoices'})
        
        if len(vendor_risk) > 0:
            vendor_risk = vendor_risk.nlargest(6, 'Risk_Level')
            
            x = range(len(vendor_risk))
            width = 0.35
            
            ax.bar(x, vendor_risk['Total_Invoices'], width, label='Total Invoices', alpha=0.6)
            ax.bar([i + width for i in x], vendor_risk['Risk_Level'], width, 
                  label='High Risk', color='red', alpha=0.8)
            
            ax.set_xlabel('Vendors')
            ax.set_ylabel('Number of Invoices')
            ax.set_title('Vendor Risk Analysis', fontweight='bold')
            ax.set_xticks([i + width/2 for i in x])
            ax.set_xticklabels([v[:12] + '...' if len(v) > 12 else v for v in vendor_risk.index], 
                              rotation=45)
            ax.legend()
    
    def _plot_monthly_trends(self, processed_data, ax):
        """Plot monthly invoice trends"""
        if 'Invoice_Date' in processed_data.columns:
            try:
                processed_data['Invoice_Date'] = pd.to_datetime(processed_data['Invoice_Date'])
                monthly_data = processed_data.groupby(
                    processed_data['Invoice_Date'].dt.to_period('M')
                ).agg({
                    'Total_Amount': 'sum',
                    'Invoice_ID': 'count'
                }).reset_index()
                
                monthly_data['Invoice_Date'] = monthly_data['Invoice_Date'].astype(str)
                
                # Plot amount trend
                color = 'tab:blue'
                ax.set_xlabel('Month')
                ax.set_ylabel('Total Amount ($)', color=color)
                line = ax.plot(monthly_data['Invoice_Date'], monthly_data['Total_Amount'], 
                              color=color, marker='o', linewidth=2, label='Total Amount')
                ax.tick_params(axis='y', labelcolor=color)
                ax.set_xticklabels(monthly_data['Invoice_Date'], rotation=45)
                
                # Plot volume trend on secondary axis
                ax2 = ax.twinx()
                color = 'tab:red'
                ax2.set_ylabel('Number of Invoices', color=color)
                bars = ax2.bar(monthly_data['Invoice_Date'], monthly_data['Invoice_ID'],
                              alpha=0.3, color=color, label='Invoice Count')
                ax2.tick_params(axis='y', labelcolor=color)
                
                ax.set_title('Monthly Invoice Trends', fontweight='bold')
                
            except Exception as e:
                ax.text(0.5, 0.5, 'Date data not available', ha='center', va='center',
                       transform=ax.transAxes, fontsize=12)
                ax.set_title('Monthly Trends (Data Unavailable)', fontweight='bold')
    
    def _plot_anomaly_types(self, results_data, ax):
        """Plot detailed anomaly types breakdown"""
        all_flags = []
        for flags in results_data['Flags']:
            all_flags.extend(flags)
        
        if all_flags:
            flag_counts = pd.Series(all_flags).value_counts()
            
            colors = plt.cm.Reds(np.linspace(0.4, 0.8, len(flag_counts)))
            bars = ax.barh(range(len(flag_counts)), flag_counts.values, color=colors)
            
            ax.set_yticks(range(len(flag_counts)))
            ax.set_yticklabels(flag_counts.index)
            ax.set_xlabel('Frequency')
            ax.set_title('Detailed Anomaly Types', fontweight='bold')
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                       str(int(width)), ha='left', va='center', fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No anomalies detected', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('Anomaly Types', fontweight='bold')
    
    def _plot_amount_risk_scatter(self, results_data, ax):
        """Plot scatter plot of amount vs risk"""
        risk_colors = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}
        colors = [risk_colors.get(risk, 'gray') for risk in results_data['Risk_Level']]
        
        scatter = ax.scatter(range(len(results_data)), results_data['Total_Amount'],
                           c=colors, alpha=0.6, s=50)
        
        ax.set_xlabel('Invoice Index')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Amount vs Risk Level', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Create custom legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='High Risk'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=8, label='Medium Risk'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Low Risk')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
    
    def _plot_enhanced_summary_stats(self, processed_data, results_data, ax):
        """Plot enhanced summary statistics"""
        ax.axis('off')
        
        # Calculate comprehensive statistics
        total_invoices = len(processed_data)
        flagged_invoices = len(results_data[results_data['Requires_Review'] == True])
        automation_rate = ((total_invoices - flagged_invoices) / total_invoices) * 100
        total_amount = processed_data['Total_Amount'].sum()
        
        high_risk = len(results_data[results_data['Risk_Level'] == 'High'])
        medium_risk = len(results_data[results_data['Risk_Level'] == 'Medium'])
        
        # Financial metrics
        avg_amount = processed_data['Total_Amount'].mean()
        max_amount = processed_data['Total_Amount'].max()
        min_amount = processed_data['Total_Amount'].min()
        
        # Anomaly financial impact
        anomalous_amount = results_data[
            results_data['Requires_Review'] == True
        ]['Total_Amount'].sum()
        
        potential_savings = anomalous_amount * 0.1
        
        stats_text = f"""
Key Performance Indicators
──────────────────────────
• Total Invoices: {total_invoices:,}
• Flagged for Review: {flagged_invoices:,}
• Automation Rate: {automation_rate:.1f}%

Risk Assessment
───────────────
• High Risk: {high_risk} invoices
• Medium Risk: {medium_risk} invoices
• Low Risk: {total_invoices - high_risk - medium_risk:,} invoices

Financial Summary
────────────────
• Total Amount: ${total_amount:,.2f}
• Average Invoice: ${avg_amount:,.2f}
• Largest Invoice: ${max_amount:,.2f}

Anomaly Impact
──────────────
• Anomalous Amount: ${anomalous_amount:,.2f}
• Potential Savings: ${potential_savings:,.2f}
"""
        
        ax.text(0.05, 0.95, stats_text, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3),
               fontfamily='monospace')