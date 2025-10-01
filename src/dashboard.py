import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class AnalyticsDashboard:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.figsize = (15, 10)
    
    def create_comprehensive_dashboard(self, processed_data, results_data):
        """Create a comprehensive analytics dashboard"""
        fig, axes = plt.subplots(2, 3, figsize=self.figsize)
        fig.suptitle('Genpact - Invoice Processing Analytics Dashboard', 
                    fontsize=16, fontweight='bold')
        
        # 1. Anomaly Distribution
        self._plot_anomaly_distribution(results_data, axes[0, 0])
        
        # 2. Amount Distribution
        self._plot_amount_distribution(processed_data, axes[0, 1])
        
        # 3. Vendor Analysis
        self._plot_vendor_analysis(processed_data, results_data, axes[0, 2])
        
        # 4. Risk Level Distribution
        self._plot_risk_distribution(results_data, axes[1, 0])
        
        # 5. Source Type Analysis
        if 'Source_Type' in processed_data.columns:
            self._plot_source_analysis(processed_data, axes[1, 1])
        
        # 6. Summary Statistics
        self._plot_summary_stats(processed_data, results_data, axes[1, 2])
        
        plt.tight_layout()
        plt.savefig('reports/dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _plot_anomaly_distribution(self, results_data, ax):
        flag_counts = results_data['Flag_Count'].value_counts().sort_index()
        colors = ['green' if x == 0 else 'orange' if x == 1 else 'red' for x in flag_counts.index]
        ax.bar(flag_counts.index, flag_counts.values, color=colors, alpha=0.7)
        ax.set_title('Invoice Anomaly Distribution')
        ax.set_xlabel('Number of Flags')
        ax.set_ylabel('Number of Invoices')
        
        for i, v in enumerate(flag_counts.values):
            ax.text(flag_counts.index[i], v + 0.5, str(v), ha='center')
    
    def _plot_amount_distribution(self, processed_data, ax):
        ax.hist(processed_data['Total_Amount'], bins=20, color='skyblue', 
               edgecolor='black', alpha=0.7)
        ax.set_title('Invoice Amount Distribution')
        ax.set_xlabel('Amount ($)')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
    
    def _plot_vendor_analysis(self, processed_data, results_data, ax):
        vendor_analysis = processed_data.groupby('Vendor_Name').agg({
            'Total_Amount': 'sum',
            'Invoice_ID': 'count'
        }).rename(columns={'Invoice_ID': 'Invoice_Count'})
        
        if len(vendor_analysis) > 0:
            vendor_analysis = vendor_analysis.nlargest(8, 'Total_Amount')
            ax.bar(vendor_analysis.index, vendor_analysis['Total_Amount'], 
                  color='lightcoral', alpha=0.7)
            ax.set_title('Top Vendors by Total Amount')
            ax.set_xlabel('Vendor')
            ax.set_ylabel('Total Amount ($)')
            ax.tick_params(axis='x', rotation=45)
    
    def _plot_risk_distribution(self, results_data, ax):
        risk_counts = results_data['Risk_Level'].value_counts()
        colors = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
        risk_colors = [colors.get(risk, 'gray') for risk in risk_counts.index]
        
        ax.pie(risk_counts.values, labels=risk_counts.index, colors=risk_colors,
               autopct='%1.1f%%', startangle=90)
        ax.set_title('Risk Level Distribution')
    
    def _plot_source_analysis(self, processed_data, ax):
        source_counts = processed_data['Source_Type'].value_counts()
        ax.pie(source_counts.values, labels=source_counts.index, 
               autopct='%1.1f%%', startangle=90, colors=['lightblue', 'lightgreen'])
        ax.set_title('Invoices by Source Type')
    
    def _plot_summary_stats(self, processed_data, results_data, ax):
        ax.axis('off')
        
        total_invoices = len(processed_data)
        flagged_invoices = len(results_data[results_data['Requires_Review'] == True])
        automation_rate = ((total_invoices - flagged_invoices) / total_invoices) * 100
        total_amount = processed_data['Total_Amount'].sum()
        
        high_risk = len(results_data[results_data['Risk_Level'] == 'High'])
        
        stats_text = f"""
Key Performance Indicators:

Total Invoices: {total_invoices:,}
Flagged for Review: {flagged_invoices:,}
Automation Rate: {automation_rate:.1f}%

Financial Summary:
Total Amount: ${total_amount:,.2f}
Avg Invoice: ${processed_data['Total_Amount'].mean():.2f}

Risk Assessment:
High Risk: {high_risk} invoices
"""
        
        ax.text(0.1, 0.9, stats_text, fontsize=12, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))