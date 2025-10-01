# app.py (fully automatic, crash-proof)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.title("🏢 AI-Invoice Processing System")
    st.write("Automated Invoice Processing with Anomaly Detection")

    uploaded_file = st.file_uploader("Upload Invoice Data", type=['csv', 'xlsx'])

    if uploaded_file:
        try:
            # --- Read CSV or Excel safely ---
            if uploaded_file.name.endswith('.csv'):
                try:
                    data = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        data = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                    except UnicodeDecodeError:
                        data = pd.read_csv(uploaded_file, encoding='latin1')
            else:
                data = pd.read_excel(uploaded_file)

            st.success("Data loaded successfully!")
            st.write("Columns in your file:", data.columns.tolist())
            st.write("Preview of your data:", data.head())

            # --- Automatically detect numeric column for Total Amount ---
            numeric_cols = data.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                amount_col = numeric_cols[0]  # pick the first numeric column
            else:
                # Let user pick a column and convert to numeric
                amount_col = st.selectbox("Select a numeric column for Total Amount", data.columns)
                data[amount_col] = pd.to_numeric(data[amount_col], errors='coerce')

            # --- Automatically detect categorical column for Vendor ---
            categorical_cols = data.select_dtypes(include='object').columns.tolist()
            if categorical_cols:
                vendor_col = categorical_cols[0]  # pick first string column
            else:
                vendor_col = st.selectbox("Select a column for Vendor Name", data.columns)

            # --- Show Metrics ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Invoices", len(data))
            with col2:
                total_amount = data[amount_col].sum()
                st.metric("Total Amount", f"${total_amount:,.2f}")
            with col3:
                avg_amount = data[amount_col].mean()
                st.metric("Avg. Amount", f"${avg_amount:,.2f}")

            # --- Bar chart for Vendor ---
            fig, ax = plt.subplots()
            data[vendor_col].value_counts().plot(kind='bar', ax=ax)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Error loading file: {e}")

if __name__ == "__main__":
    main()
