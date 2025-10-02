"""
Database module for Invoice Processing System
Uses SQLite for portability, easily switchable to MySQL
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

class InvoiceDB:
    def __init__(self, db_path='data/invoice_system.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables"""
        os.makedirs('data', exist_ok=True)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT UNIQUE NOT NULL,
                vendor_name TEXT NOT NULL,
                invoice_date DATE NOT NULL,
                due_date DATE,
                total_amount DECIMAL(15,2) NOT NULL,
                tax_amount DECIMAL(15,2),
                item_description TEXT,
                payment_terms TEXT,
                department TEXT,
                source_type TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                risk_level TEXT,
                anomaly_type TEXT
            )
        ''')
        
        # Create anomalies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,
                description TEXT,
                severity TEXT,
                amount_impact DECIMAL(15,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id)
            )
        ''')
        
        # Create processing_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                performed_by TEXT DEFAULT 'system',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoice_id ON invoices(invoice_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vendor_name ON invoices(vendor_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoices(invoice_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_risk_level ON invoices(risk_level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomaly_type ON invoices(anomaly_type)')
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def save_invoice(self, invoice_data):
        """Save invoice to database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO invoices (
                    invoice_id, vendor_name, invoice_date, due_date, total_amount,
                    tax_amount, item_description, payment_terms, department,
                    source_type, status, risk_level, anomaly_type, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_data['invoice_id'],
                invoice_data['vendor_name'],
                invoice_data['invoice_date'],
                invoice_data.get('due_date'),
                invoice_data['total_amount'],
                invoice_data.get('tax_amount', 0),
                invoice_data.get('item_description', ''),
                invoice_data.get('payment_terms', ''),
                invoice_data.get('department', 'Unknown'),
                invoice_data.get('source_type', 'Digital'),
                invoice_data.get('status', 'Pending'),
                invoice_data.get('risk_level', 'Low'),
                invoice_data.get('anomaly_type', 'No Anomaly'),
                datetime.now()
            ))
            
            # Log the action
            cursor.execute('''
                INSERT INTO processing_log (invoice_id, action, details)
                VALUES (?, ?, ?)
            ''', (
                invoice_data['invoice_id'],
                'SAVE',
                f"Invoice saved/updated with risk level: {invoice_data.get('risk_level', 'Low')}"
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving invoice: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def save_anomaly(self, invoice_id, anomaly_type, description, severity, amount_impact=0):
        """Save anomaly detection result"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO anomalies (invoice_id, anomaly_type, description, severity, amount_impact)
                VALUES (?, ?, ?, ?, ?)
            ''', (invoice_id, anomaly_type, description, severity, amount_impact))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving anomaly: {str(e)}")
            return False
        finally:
            conn.close()
    
    def search_invoices(self, filters=None, page=1, per_page=20):
        """Search invoices with filters and pagination"""
        conn = self._get_connection()
        
        try:
            query = "SELECT * FROM invoices WHERE 1=1"
            params = []
            
            if filters:
                # Vendor filter
                if filters.get('vendor'):
                    query += " AND vendor_name LIKE ?"
                    params.append(f"%{filters['vendor']}%")
                
                # Date range filter
                if filters.get('start_date'):
                    query += " AND invoice_date >= ?"
                    params.append(filters['start_date'])
                
                if filters.get('end_date'):
                    query += " AND invoice_date <= ?"
                    params.append(filters['end_date'])
                
                # Amount range filter
                if filters.get('min_amount'):
                    query += " AND total_amount >= ?"
                    params.append(float(filters['min_amount']))
                
                if filters.get('max_amount'):
                    query += " AND total_amount <= ?"
                    params.append(float(filters['max_amount']))
                
                # Risk level filter
                if filters.get('risk_level'):
                    query += " AND risk_level = ?"
                    params.append(filters['risk_level'])
                
                # Anomaly type filter
                if filters.get('anomaly_type'):
                    query += " AND anomaly_type = ?"
                    params.append(filters['anomaly_type'])
                
                # Status filter
                if filters.get('status'):
                    query += " AND status = ?"
                    params.append(filters['status'])
            
            # Add ordering and pagination
            query += " ORDER BY invoice_date DESC, total_amount DESC"
            
            # Get total count for pagination
            count_query = "SELECT COUNT(*) FROM (" + query + ")"
            total_count = pd.read_sql(count_query, conn, params=params).iloc[0,0]
            
            # Add pagination
            offset = (page - 1) * per_page
            query += " LIMIT ? OFFSET ?"
            params.extend([per_page, offset])
            
            # Execute query
            invoices_df = pd.read_sql(query, conn, params=params)
            
            return {
                'invoices': invoices_df,
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }
            
        except Exception as e:
            print(f"Error searching invoices: {str(e)}")
            return {'invoices': pd.DataFrame(), 'total_count': 0, 'page': page, 'per_page': per_page, 'total_pages': 0}
        finally:
            conn.close()
    
    def get_invoice_stats(self):
        """Get comprehensive invoice statistics"""
        conn = self._get_connection()
        
        try:
            stats_queries = {
                'total_invoices': "SELECT COUNT(*) as count FROM invoices",
                'total_amount': "SELECT SUM(total_amount) as total FROM invoices",
                'avg_amount': "SELECT AVG(total_amount) as avg FROM invoices",
                'high_risk_count': "SELECT COUNT(*) as count FROM invoices WHERE risk_level = 'High'",
                'by_vendor': '''
                    SELECT vendor_name, COUNT(*) as invoice_count, 
                           SUM(total_amount) as total_amount 
                    FROM invoices 
                    GROUP BY vendor_name 
                    ORDER BY total_amount DESC
                ''',
                'by_risk_level': '''
                    SELECT risk_level, COUNT(*) as count 
                    FROM invoices 
                    GROUP BY risk_level
                ''',
                'by_anomaly_type': '''
                    SELECT anomaly_type, COUNT(*) as count 
                    FROM invoices 
                    GROUP BY anomaly_type
                ''',
                'monthly_trends': '''
                    SELECT strftime('%Y-%m', invoice_date) as month,
                           COUNT(*) as invoice_count,
                           SUM(total_amount) as total_amount
                    FROM invoices
                    GROUP BY strftime('%Y-%m', invoice_date)
                    ORDER BY month
                '''
            }
            
            stats = {}
            for key, query in stats_queries.items():
                stats[key] = pd.read_sql(query, conn)
            
            return stats
            
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {}
        finally:
            conn.close()
    
    def update_invoice_status(self, invoice_id, status, notes=None):
        """Update invoice status (e.g., after review)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE invoices 
                SET status = ?, processed_at = ?
                WHERE invoice_id = ?
            ''', (status, datetime.now(), invoice_id))
            
            # Log the status change
            cursor.execute('''
                INSERT INTO processing_log (invoice_id, action, details)
                VALUES (?, ?, ?)
            ''', (invoice_id, 'STATUS_UPDATE', f"Status changed to {status}. Notes: {notes or 'No notes'}"))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error updating invoice status: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()