"""
Advanced Search and Filter Engine for Invoice System
"""

import pandas as pd
from datetime import datetime, timedelta

class InvoiceSearchEngine:
    def __init__(self, database):
        self.db = database
    
    def search(self, search_term=None, filters=None, sort_by='invoice_date', sort_order='DESC', page=1, per_page=20):
        """Comprehensive search with multiple filter options"""
        
        # Build filters from search term
        if search_term and not filters:
            filters = self._parse_search_term(search_term)
        
        # Execute search
        result = self.db.search_invoices(filters, page, per_page)
        
        # Apply additional sorting if needed
        if sort_by and not result['invoices'].empty:
            result['invoices'] = result['invoices'].sort_values(
                by=sort_by, 
                ascending=(sort_order.upper() == 'ASC')
            )
        
        return result
    
    def _parse_search_term(self, search_term):
        """Parse free-text search into structured filters"""
        filters = {}
        
        # Check if search term is a vendor name
        if any(word in search_term.lower() for word in ['vendor', 'supplier', 'company']):
            filters['vendor'] = search_term
        
        # Check if it's an invoice ID pattern
        elif any(prefix in search_term.upper() for prefix in ['INV-', 'DIG-', 'SCAN-', 'DUP-']):
            # For exact invoice ID match, we'll handle separately
            pass
        
        # Check for amount patterns
        elif '$' in search_term or any(word in search_term.lower() for word in ['usd', 'amount', 'total']):
            try:
                # Extract numeric value
                amount = float(''.join(c for c in search_term if c.isdigit() or c == '.'))
                filters['min_amount'] = amount * 0.9  # 10% range
                filters['max_amount'] = amount * 1.1
            except:
                pass
        
        # Check for date patterns
        elif any(word in search_term.lower() for word in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                                                         'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
            # Simple date parsing - in real implementation, use dateutil
            pass
        
        else:
            # Default to vendor search
            filters['vendor'] = search_term
        
        return filters
    
    def get_quick_filters(self):
        """Get predefined quick filter options"""
        return {
            'high_risk': {'risk_level': 'High'},
            'needs_review': {'status': 'Pending', 'risk_level': 'High'},
            'recent_week': {
                'start_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            },
            'large_invoices': {'min_amount': 10000},
            'duplicates': {'anomaly_type': 'Duplicate'},
            'extreme_amounts': {'anomaly_type': 'Extreme Amount'}
        }
    
    def export_search_results(self, filters=None, format='csv'):
        """Export search results to various formats"""
        result = self.search(filters=filters, per_page=1000)  # Large page size for export
        
        if format.lower() == 'csv':
            return result['invoices'].to_csv(index=False)
        elif format.lower() == 'excel':
            return result['invoices'].to_excel('exported_invoices.xlsx', index=False)
        else:
            return result['invoices'].to_json(orient='records')
    
    def get_search_suggestions(self, partial_term):
        """Get search suggestions based on partial input"""
        stats = self.db.get_invoice_stats()
        suggestions = []
        
        # Vendor suggestions
        vendors = stats.get('by_vendor', pd.DataFrame())
        if not vendors.empty:
            vendor_matches = vendors[vendors['vendor_name'].str.contains(partial_term, case=False, na=False)]
            suggestions.extend([f"vendor:{row['vendor_name']}" for _, row in vendor_matches.head(3).iterrows()])
        
        # Amount suggestions
        try:
            amount = float(partial_term.replace('$', '').replace(',', ''))
            suggestions.extend([
                f"amount:>{amount}",
                f"amount:<{amount}",
                f"amount:{amount-100}-{amount+100}"
            ])
        except:
            pass
        
        return suggestions[:5]  # Limit to 5 suggestions