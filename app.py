# app.py (for Streamlit)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.title("🏢 Intelligent Invoice Processing")
    st.write("Automated Invoice Processing with Anomaly Detection")
    
    # Upload section
    uploaded_file = st.file_uploader("Upload Invoice Data", type=['csv', 'xlsx'])
    
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.success("Data loaded successfully!")
        
        # Show analytics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Invoices", len(data))
        with col2:
            st.metric("Total Amount", f"${data['Total_Amount'].sum():,.2f}")
        with col3:
            st.metric("Avg. Amount", f"${data['Total_Amount'].mean():.2f}")
        
        # Show charts
        fig, ax = plt.subplots()
        data['Vendor_Name'].value_counts().plot(kind='bar', ax=ax)
        st.pyplot(fig)

if __name__ == "__main__":
    main()