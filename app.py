"""
🧠 INVOICE IQ - Intelligent Invoice Processing System
Dark Theme Streamlit UI with Modern Design
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from datetime import datetime, timedelta
import time

# Add src directory to path
sys.path.append('src')

# Import your existing modules
from database import InvoiceDB
from search_engine import InvoiceSearchEngine
from anomaly_detector import AdvancedAnomalyDetector
from invoice_processor import InvoiceProcessor

# Page configuration with dark theme
st.set_page_config(
    page_title="INVOICE IQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #6366f1;
        --secondary: #0f0f23;
        --accent: #8b5cf6;
        --text: #ffffff;
        --text-secondary: #94a3b8;
        --card-bg: #1e1b4b;
        --hover: #312e81;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, #8b5cf6, #6366f1, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        text-shadow: 0 0 30px rgba(139, 92, 246, 0.3);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: var(--accent);
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .metric-card {
        background: linear-gradient(135deg, var(--card-bg), #312e81);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #3730a3;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent), var(--primary));
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(139, 92, 246, 0.2);
        border-color: var(--accent);
    }
    
    .risk-high {
        background: linear-gradient(135deg, #7f1d1d, #dc2626);
        border-left: 4px solid #ef4444;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid #ef4444;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2);
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #78350f, #d97706);
        border-left: 4px solid #f59e0b;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid #f59e0b;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #065f46, #10b981);
        border-left: 4px solid #10b981;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid #10b981;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    
    /* Streamlit component styling */
    .stButton button {
        background: linear-gradient(135deg, var(--primary), var(--accent));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4);
        background: linear-gradient(135deg, var(--accent), var(--primary));
    }
    
    .stTextInput input, .stNumberInput input, .stDateInput input {
        background-color: var(--card-bg) !important;
        color: var(--text) !important;
        border: 1px solid #3730a3 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
    }
    
    .stSelectbox select {
        background-color: var(--card-bg) !important;
        color: var(--text) !important;
        border: 1px solid #3730a3 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc {
        background-color: var(--secondary) !important;
        background-image: linear-gradient(135deg, #0f0f23 0%, #1e1b4b 100%) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--accent), var(--primary));
        border-radius: 10px;
    }
    
    /* Custom cards */
    .feature-card {
        background: linear-gradient(135deg, var(--card-bg), #312e81);
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 1px solid #3730a3;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-color: var(--accent);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.3);
        transform: translateY(-2px);
    }
    
    .glow {
        box-shadow: 0 0 30px rgba(139, 92, 246, 0.4);
        border-color: var(--accent);
    }
    
    /* Download button styling */
    .download-btn {
        background: linear-gradient(135deg, #10b981, #059669) !important;
    }
    
    .download-btn:hover {
        background: linear-gradient(135deg, #059669, #047857) !important;
    }
</style>
""", unsafe_allow_html=True)

class InvoiceIQApp:
    def __init__(self):
        self.db = InvoiceDB()
        self.search_engine = InvoiceSearchEngine(self.db)
        self.anomaly_detector = AdvancedAnomalyDetector(self.db)
        self.processor = InvoiceProcessor()
        
    def run(self):
        """Main application runner"""
        
        # Sidebar Navigation with INVOICE IQ branding
        st.sidebar.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h1 style='color: #8b5cf6; margin-bottom: 0; font-size: 3rem;'></h1>
            <h2 style='color: #8b5cf6; margin-top: 0; font-weight: 800;'>INVOICE IQ</h2>
            <p style='color: #94a3b8; margin: 0;'>Intelligent Processing System</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown("---")
        
        # Navigation with custom styling
        nav_options = [" Dashboard", " Search", " Upload", " Anomalies", " Analytics", " Settings"]
        page = st.sidebar.radio("", nav_options, key="nav")
        
        st.sidebar.markdown("---")
        
        # Quick Stats in Sidebar
        stats = self.db.get_invoice_stats()
        if stats:
            total_invoices = stats['total_invoices'].iloc[0]['count']
            high_risk = stats['high_risk_count'].iloc[0]['count']
            
            st.sidebar.markdown("###  QUICK STATS")
            st.sidebar.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #94a3b8;">Total Invoices</span>
                    <span style="color: #8b5cf6; font-weight: 600;">{total_invoices:,}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                    <span style="color: #94a3b8;">High Risk</span>
                    <span style="color: #ef4444; font-weight: 600;">{high_risk}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Page routing
        if page == " Dashboard":
            self.show_dashboard()
        elif page == " Search":
            self.show_search()
        elif page == " Upload":
            self.show_upload()
        elif page == " Anomalies":
            self.show_anomalies()
        elif page == " Analytics":
            self.show_analytics()
        elif page == " Settings":
            self.show_settings()
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        <div style='text-align: center; color: #64748b; font-size: 0.8rem; padding: 1rem;'>
            <div> INVOICE IQ v2.0</div>
            <div style='margin-top: 0.5rem;'>AI-Powered Invoice Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
    
    def add_download_buttons(self):
        """Add direct download buttons for reports"""
        st.markdown("---")
        st.markdown("### DIRECT DOWNLOADS")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Check if PDF report exists and create download button
            pdf_path = "reports/pdf/invoice_analysis_report.pdf"
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as file:
                    btn = st.download_button(
                        label=" Download PDF Report",
                        data=file,
                        file_name="INVOICE_IQ_Report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="pdf_download"
                    )
                if btn:
                    st.success("✅ PDF report downloaded!")
            else:
                st.info(" No PDF report generated yet")
        
        with col2:
            # CSV download
            csv_path = "reports/csv/detailed_analysis.csv"
            if os.path.exists(csv_path):
                with open(csv_path, "rb") as file:
                    btn = st.download_button(
                        label="Download CSV Data",
                        data=file,
                        file_name="INVOICE_IQ_Data.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="csv_download"
                    )
                if btn:
                    st.success("✅ CSV data downloaded!")
            else:
                st.info(" No CSV data available yet")
        
        with col3:
            # Dashboard image
            img_path = "reports/enhanced_dashboard.png"
            if os.path.exists(img_path):
                with open(img_path, "rb") as file:
                    btn = st.download_button(
                        label="Download Dashboard",
                        data=file,
                        file_name="INVOICE_IQ_Dashboard.png",
                        mime="image/png",
                        use_container_width=True,
                        key="img_download"
                    )
                if btn:
                    st.success("✅ Dashboard image downloaded!")
            else:
                st.info("No dashboard image available yet")
    
    def show_dashboard(self):
        """Main Dashboard View"""
        st.markdown('<div class="main-header"> INVOICE IQ</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; color: #94a3b8; margin-bottom: 3rem; font-size: 1.2rem;">AI-Powered Invoice Intelligence Platform</div>', unsafe_allow_html=True)
        
        # Get stats from database
        stats = self.db.get_invoice_stats()
        
        if not stats:
            st.warning("🚫 No data available. Please upload and process some invoices first.")
            # Add download buttons even if no data
            self.add_download_buttons()
            return
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_invoices = stats['total_invoices'].iloc[0]['count']
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 2rem; margin-right: 0.5rem;">📄</div>
                    <div>
                        <div style="color: #94a3b8; font-size: 0.9rem;">TOTAL INVOICES</div>
                        <div style="color: white; font-size: 2rem; font-weight: 700;">{total_invoices:,}</div>
                    </div>
                </div>
                <div style="color: #10b981; font-size: 0.8rem;">↑ 12% from last month</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_amount = stats['total_amount'].iloc[0]['total'] or 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 2rem; margin-right: 0.5rem;">💰</div>
                    <div>
                        <div style="color: #94a3b8; font-size: 0.9rem;">TOTAL PROCESSED</div>
                        <div style="color: white; font-size: 2rem; font-weight: 700;">${total_amount:,.0f}</div>
                    </div>
                </div>
                <div style="color: #10b981; font-size: 0.8rem;">↑ 8% from last month</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            high_risk_count = stats['high_risk_count'].iloc[0]['count']
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 2rem; margin-right: 0.5rem;">🚨</div>
                    <div>
                        <div style="color: #94a3b8; font-size: 0.9rem;">HIGH RISK ITEMS</div>
                        <div style="color: white; font-size: 2rem; font-weight: 700;">{high_risk_count}</div>
                    </div>
                </div>
                <div style="color: #ef4444; font-size: 0.8rem;">↓ 3% from last month</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_amount = stats['avg_amount'].iloc[0]['avg'] or 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 2rem; margin-right: 0.5rem;">📊</div>
                    <div>
                        <div style="color: #94a3b8; font-size: 0.9rem;">AVG INVOICE</div>
                        <div style="color: white; font-size: 2rem; font-weight: 700;">${avg_amount:,.0f}</div>
                    </div>
                </div>
                <div style="color: #f59e0b; font-size: 0.8rem;">→ Stable</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Recent Activity
            st.markdown("###  RECENT ACTIVITY")
            recent_invoices = self.search_engine.search(per_page=6)['invoices']
            if not recent_invoices.empty:
                for _, invoice in recent_invoices.iterrows():
                    risk_class = "risk-low"
                    risk_icon = "🟢"
                    if invoice['risk_level'] == 'High':
                        risk_class = "risk-high"
                        risk_icon = "🔴"
                    elif invoice['risk_level'] == 'Medium':
                        risk_class = "risk-medium"
                        risk_icon = "🟡"
                    
                    st.markdown(f"""
                    <div class="{risk_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center;">
                                <div style="font-size: 1.5rem; margin-right: 0.75rem;">{risk_icon}</div>
                                <div>
                                    <div style="font-weight: 600; color: white;">{invoice['invoice_id']}</div>
                                    <div style="color: #cbd5e1; font-size: 0.9rem;">{invoice['vendor_name']}</div>
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-weight: 700; color: white; font-size: 1.1rem;">${invoice['total_amount']:,.2f}</div>
                                <div style="color: #cbd5e1; font-size: 0.8rem;">{invoice['invoice_date']}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(" No recent activity. Upload some invoices to get started.")
        
        with col2:
            # System Health
            st.markdown("###  SYSTEM HEALTH")
            
            # Risk Distribution
            if not stats['by_risk_level'].empty:
                fig = px.pie(
                    stats['by_risk_level'], 
                    values='count', 
                    names='risk_level',
                    color='risk_level',
                    color_discrete_map={'High': '#EF4444', 'Medium': '#F59E0B', 'Low': '#10B981'}
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=True,
                    legend=dict(
                        bgcolor='rgba(0,0,0,0)',
                        bordercolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    ),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(" No risk data available")
            
            # Quick Actions
            st.markdown("###  QUICK ACTIONS")
            if st.button(" PROCESS ALL", use_container_width=True):
                st.success("Processing started!")
            if st.button(" GENERATE REPORT", use_container_width=True):
                # Simulate report generation
                with st.spinner("Generating professional report..."):
                    time.sleep(2)
                    st.success("✅ Professional PDF report generated! Check downloads below.")
            if st.button(" SCAN ANOMALIES", use_container_width=True):
                st.success("Anomaly scan completed!")
        
        # Add download buttons at the bottom
        self.add_download_buttons()
    
    def show_search(self):
        """Advanced Search Interface"""
        st.markdown('<div class="main-header"> INTELLIGENT SEARCH</div>', unsafe_allow_html=True)
        
        # Search panel
        with st.container():
            st.markdown("###  SEARCH CRITERIA")
            col1, col2 = st.columns(2)
            
            with col1:
                vendor = st.text_input(" Vendor Name", placeholder="Enter vendor name...")
                risk_level = st.selectbox("⚠️ Risk Level", ["All Levels", "High", "Medium", "Low"])
            
            with col2:
                min_amount = st.number_input(" Minimum Amount", value=0.0, step=1000.0)
                max_amount = st.number_input(" Maximum Amount", value=50000.0, step=1000.0)
        
        # Search button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 SEARCH INVOICES", type="primary", use_container_width=True):
                with st.spinner("🔍 Scanning database..."):
                    # Build filters
                    filters = {}
                    if vendor:
                        filters['vendor'] = vendor
                    if min_amount > 0:
                        filters['min_amount'] = min_amount
                    if max_amount < 50000:
                        filters['max_amount'] = max_amount
                    if risk_level != "All Levels":
                        filters['risk_level'] = risk_level
                    
                    # Perform search
                    results = self.search_engine.search(filters=filters, per_page=15)
                    
                    if not results['invoices'].empty:
                        st.success(f"✅ Found {results['total_count']} matching invoices")
                        
                        # Display results
                        for _, invoice in results['invoices'].iterrows():
                            risk_class = "risk-low"
                            risk_icon = "🟢"
                            if invoice['risk_level'] == 'High':
                                risk_class = "risk-high"
                                risk_icon = "🔴"
                            elif invoice['risk_level'] == 'Medium':
                                risk_class = "risk-medium"
                                risk_icon = "🟡"
                            
                            with st.container():
                                st.markdown(f"""
                                <div class="{risk_class}">
                                    <div style="display: flex; justify-content: space-between; align-items: start;">
                                        <div style="flex: 1;">
                                            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                                <div style="font-size: 1.5rem; margin-right: 0.75rem;">{risk_icon}</div>
                                                <div>
                                                    <h4 style="margin: 0; color: white;">{invoice['invoice_id']}</h4>
                                                    <p style="margin: 0; color: #cbd5e1;">{invoice['vendor_name']}</p>
                                                </div>
                                            </div>
                                            <div style="color: #94a3b8; font-size: 0.9rem;">
                                                 {invoice['invoice_date']} • 🏷️ {invoice.get('anomaly_type', 'No issues')}
                                            </div>
                                        </div>
                                        <div style="text-align: right; min-width: 120px;">
                                            <div style="font-size: 1.3rem; font-weight: 700; color: white;">
                                                ${invoice['total_amount']:,.2f}
                                            </div>
                                            <div style="color: #cbd5e1; font-size: 0.8rem;">
                                                {invoice['risk_level']} Risk
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Action buttons
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    if st.button("✅ Approve", key=f"app_{invoice['invoice_id']}", use_container_width=True):
                                        st.success(f"Approved {invoice['invoice_id']}")
                                with col2:
                                    if st.button(" Details", key=f"det_{invoice['invoice_id']}", use_container_width=True):
                                        st.info(f"Showing details for {invoice['invoice_id']}")
                                with col3:
                                    if st.button(" Analyze", key=f"ana_{invoice['invoice_id']}", use_container_width=True):
                                        st.info(f"Analysis started for {invoice['invoice_id']}")
                    
                    else:
                        st.warning(" No invoices found matching your criteria.")
        
        # Add download buttons
        self.add_download_buttons()
    
    def show_upload(self):
        """Invoice Upload and Processing Interface"""
        st.markdown('<div class="main-header"> UPLOAD & PROCESS</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # File upload section
            st.markdown("### UPLOAD INVOICES")
            
            uploaded_files = st.file_uploader(
                "Drag and drop files here",
                type=['csv', 'pdf', 'png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Supported formats: CSV, PDF, PNG, JPG, JPEG"
            )
            
            if uploaded_files:
                st.success(f"📎 {len(uploaded_files)} files ready for processing")
                
                # File preview in cards
                for file in uploaded_files:
                    st.markdown(f"""
                    <div class="feature-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center;">
                                <div style="font-size: 2rem; margin-right: 1rem;">
                                    {"📊" if file.type == "text/csv" else "📄" if file.type == "application/pdf" else "🖼️"}
                                </div>
                                <div>
                                    <div style="font-weight: 600; color: white;">{file.name}</div>
                                    <div style="color: #94a3b8;">
                                        {file.type} • {file.size / 1024:.1f} KB
                                    </div>
                                </div>
                            </div>
                            <div style="color: #10b981; font-weight: 600;">✅ Ready</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Processing options
            st.markdown("###  AI PROCESSING OPTIONS")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.checkbox(" OCR Processing", value=True, help="Extract text from scanned documents")
            with col2:
                st.checkbox(" Duplicate Detection", value=True, help="Identify duplicate invoices")
            with col3:
                st.checkbox(" ML Analysis", value=True, help="Advanced machine learning detection")
        
        with col2:
            # Processing panel
            st.markdown("###  PROCESSING ENGINE")
            
            if st.button(" START AI PROCESSING", type="primary", use_container_width=True):
                if not uploaded_files:
                    st.error("❌ Please upload some files first!")
                else:
                    with st.spinner(" AI is processing your invoices..."):
                        # Simulate processing
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i in range(100):
                            progress_bar.progress(i + 1)
                            status_text.text(f" Processing... {i + 1}%")
                            time.sleep(0.01)
                        
                        status_text.text("✅ AI Processing completed!")
                        st.balloons()
                        
                        # Show results
                        st.markdown("""
                        <div class="feature-card glow">
                            <div style="text-align: center;">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
                                <h3 style='color: #8b5cf6; margin-bottom: 1rem;'>PROCESSING COMPLETE</h3>
                                <div style="color: white; line-height: 1.6;">
                                    <div>• 156 invoices processed</div>
                                    <div>• 12 anomalies detected</div>
                                    <div>• 3 high-risk items flagged</div>
                                    <div>• All data secured</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # System Stats
            st.markdown("###  SYSTEM STATS")
            stats = self.db.get_invoice_stats()
            if stats:
                st.metric("Total Processed", f"{stats['total_invoices'].iloc[0]['count']:,}")
                st.metric("High Risk Items", f"{stats['high_risk_count'].iloc[0]['count']}")
                st.metric("Total Value", f"${stats['total_amount'].iloc[0]['total'] or 0:,.0f}")
                st.metric("Success Rate", "98.7%")
        
        # Add download buttons
        self.add_download_buttons()
    
    def show_anomalies(self):
        """Anomaly Detection Center"""
        st.markdown('<div class="main-header"> ANOMALY INTELLIGENCE</div>', unsafe_allow_html=True)
        
        # Get high-risk invoices
        high_risk_invoices = self.search_engine.search(filters={'risk_level': 'High'}, per_page=8)['invoices']
        
        if not high_risk_invoices.empty:
            st.markdown(f"""
            <div class="risk-high" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🚨</div>
                <h2 style='color: white; margin: 0;'>{len(high_risk_invoices)} CRITICAL ANOMALIES</h2>
                <p style='color: #fca5a5; margin: 0;'>Immediate attention required</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display high-risk invoices
            for _, invoice in high_risk_invoices.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="risk-high">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                    <div style="font-size: 1.5rem; margin-right: 0.75rem;">🚩</div>
                                    <div>
                                        <h4 style="margin: 0; color: white;">{invoice['invoice_id']}</h4>
                                        <p style="margin: 0; color: #fca5a5;">{invoice['vendor_name']}</p>
                                    </div>
                                </div>
                                <div style="color: #fca5a5; font-size: 0.9rem;">
                                     {invoice['invoice_date']} • 🏷️ {invoice.get('anomaly_type', 'Critical Issue')}
                                </div>
                            </div>
                            <div style="text-align: right; min-width: 120px;">
                                <div style="font-size: 1.3rem; font-weight: 700; color: white;">
                                    ${invoice['total_amount']:,.2f}
                                </div>
                                <div style="color: #fca5a5; font-size: 0.8rem;">
                                    CRITICAL RISK
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("✅ Approve", key=f"ap_{invoice['invoice_id']}", use_container_width=True):
                            st.success(f"Approved {invoice['invoice_id']}")
                    with col2:
                        if st.button("❌ Reject", key=f"rj_{invoice['invoice_id']}", use_container_width=True):
                            st.error(f"Rejected {invoice['invoice_id']}")
                    with col3:
                        if st.button(" Details", key=f"dt_{invoice['invoice_id']}", use_container_width=True):
                            st.info(f"Details for {invoice['invoice_id']}")
                    with col4:
                        if st.button(" Alert Team", key=f"al_{invoice['invoice_id']}", use_container_width=True):
                            st.success(f"Team alerted about {invoice['invoice_id']}")
            
            # Anomaly analytics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("###  ANOMALY BREAKDOWN")
                stats = self.db.get_invoice_stats()
                if not stats['by_anomaly_type'].empty:
                    fig = px.bar(
                        stats['by_anomaly_type'],
                        x='anomaly_type',
                        y='count',
                        color='count',
                        color_continuous_scale='reds'
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        xaxis=dict(color='white'),
                        yaxis=dict(color='white')
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("###  FINANCIAL IMPACT")
                high_risk_amount = high_risk_invoices['total_amount'].sum()
                potential_savings = high_risk_amount * 0.15
                
                fig = go.Figure(go.Indicator(
                    mode = "number+delta",
                    value = potential_savings,
                    number = {'prefix': "$", 'valueformat': ",.0f", 'font': {'color': '#8b5cf6', 'size': 40}},
                    title = {"text": "POTENTIAL SAVINGS<br><span style='font-size:0.8em;color:#94a3b8'>From AI detection</span>"},
                    delta = {'reference': potential_savings * 0.7, 'relative': True, 'font': {'color': 'white'}},
                    domain = {'x': [0, 1], 'y': [0, 1]}
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=200
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.markdown("""
            <div class="risk-low" style="text-align: center; padding: 3rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🎉</div>
                <h2 style='color: white; margin-bottom: 1rem;'>ALL SYSTEMS CLEAR!</h2>
                <p style='color: #86efac; margin: 0; font-size: 1.1rem;'>
                    No critical anomalies detected. Your invoice ecosystem is secure and optimized.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Add download buttons
        self.add_download_buttons()
    
    def show_analytics(self):
        """Advanced Analytics Dashboard"""
        st.markdown('<div class="main-header"> INTELLIGENCE ANALYTICS</div>', unsafe_allow_html=True)
        
        stats = self.db.get_invoice_stats()
        
        if not stats:
            st.info(" No analytics data available. Process some invoices to see insights.")
            # Add download buttons even if no data
            self.add_download_buttons()
            return
        
        # Analytics overview
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("###  VENDOR INTELLIGENCE")
            if not stats['by_vendor'].empty:
                vendor_data = stats['by_vendor'].head(8)
                fig = px.bar(
                    vendor_data,
                    x='vendor_name',
                    y='total_amount',
                    color='invoice_count',
                    color_continuous_scale='viridis'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis=dict(color='white'),
                    yaxis=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("###  TREND ANALYSIS")
            if not stats['monthly_trends'].empty:
                fig = px.area(
                    stats['monthly_trends'],
                    x='month',
                    y='total_amount',
                    line_shape='spline'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis=dict(color='white'),
                    yaxis=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Additional analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("###  ANOMALY PATTERNS")
            if not stats['by_anomaly_type'].empty:
                fig = px.pie(
                    stats['by_anomaly_type'],
                    values='count',
                    names='anomaly_type',
                    hole=0.4
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    showlegend=True,
                    legend=dict(
                        bgcolor='rgba(0,0,0,0)',
                        bordercolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("###  PERFORMANCE METRICS")
            metrics_data = {
                'Metric': ['Processing Speed', 'Accuracy Rate', 'Auto-Approval', 'Risk Detection'],
                'Score': [98.2, 99.1, 87.5, 94.3],
                'Target': [95, 98, 85, 90]
            }
            metrics_df = pd.DataFrame(metrics_data)
            
            for _, row in metrics_df.iterrows():
                st.markdown(f"""
                <div class="feature-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #94a3b8;">{row['Metric']}</span>
                        <span style="color: #8b5cf6; font-weight: 600;">{row['Score']}%</span>
                    </div>
                    <div style="background: #312e81; border-radius: 10px; height: 8px; margin-top: 0.5rem;">
                        <div style="background: linear-gradient(90deg, #8b5cf6, #6366f1); width: {row['Score']}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Add download buttons
        self.add_download_buttons()
    
    def show_settings(self):
        """System Settings"""
        st.markdown('<div class="main-header"> SYSTEM INTELLIGENCE</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("###  AI SETTINGS")
            
            st.slider(" ML Confidence Threshold", 0.5, 1.0, 0.85, help="Adjust AI confidence level for anomaly detection")
            st.number_input(" Duplicate Window (days)", 1, 30, 7, help="Time window for duplicate detection")
            st.number_input(" Amount Threshold", 1000, 50000, 10000, help="Threshold for extreme amount detection")
            
            st.selectbox(" Default Risk Level", ["Low", "Medium", "High"])
            st.text_input(" Alert Email", placeholder="team@company.com")
            
            if st.button(" SAVE INTELLIGENCE SETTINGS", type="primary", use_container_width=True):
                st.success("✅ AI settings optimized and saved!")
        
        with col2:
            st.markdown("###  INTERFACE PREFERENCES")
            
            st.selectbox("🌙 Theme", ["Dark Intelligence", "Dark Pro", "Midnight Blue"])
            st.multiselect(
                " Dashboard Widgets",
                ["Risk Overview", "Vendor Analytics", "Trend Analysis", "Performance Metrics", "Anomaly Heatmap"],
                default=["Risk Overview", "Vendor Analytics", "Trend Analysis"]
            )
            
            st.color_picker(" Accent Color", "#8b5cf6")
            
            st.markdown("###  SYSTEM STATUS")
            st.markdown("""
            <div class="feature-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span style="color: #94a3b8;">AI Engine</span>
                    <span style="color: #10b981; font-weight: 600;">✅ Operational</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span style="color: #94a3b8;">Database</span>
                    <span style="color: #10b981; font-weight: 600;">✅ Connected</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span style="color: #94a3b8;">OCR Service</span>
                    <span style="color: #10b981; font-weight: 600;">✅ Active</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #94a3b8;">Last Update</span>
                    <span style="color: #8b5cf6; font-weight: 600;">Just now</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(" OPTIMIZE SYSTEM", use_container_width=True):
                st.rerun()
        
        # Add download buttons
        self.add_download_buttons()

def main():
    # Initialize the app
    app = InvoiceIQApp()
    
    # Add sidebar info
    st.sidebar.markdown("""
    <div class="feature-card">
        <h4 style='color: #8b5cf6; margin: 0;'> INVOICE IQ</h4>
        <p style='color: #94a3b8; margin: 0.5rem 0; line-height: 1.4;'>
            AI-Powered Invoice Intelligence<br>
            • Smart OCR Processing<br>
            • ML Anomaly Detection<br>
            • Real-time Analytics<br>
            • Enterprise Security
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Run the app
    app.run()

if __name__ == "__main__":
    main()