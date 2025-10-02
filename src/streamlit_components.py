"""
Reusable Streamlit Components for Better UI
"""

import streamlit as st
import plotly.express as px
import pandas as pd

def metric_card(title, value, delta=None, delta_color="normal"):
    """Create a beautiful metric card"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(title, value, delta=delta, delta_color=delta_color)
    return col1

def risk_badge(risk_level):
    """Create a risk level badge"""
    colors = {
        "High": "🔴",
        "Medium": "🟡", 
        "Low": "🟢"
    }
    return colors.get(risk_level, "⚪")

def loading_animation(message="Processing..."):
    """Show a nice loading animation"""
    with st.spinner(message):
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
            time.sleep(0.01)

def success_message(title, message):
    """Show a success message with emoji"""
    st.success(f"✅ **{title}**\n\n{message}")

def error_message(title, message):
    """Show an error message with emoji"""
    st.error(f"❌ **{title}**\n\n{message}")

def warning_message(title, message):
    """Show a warning message with emoji"""
    st.warning(f"⚠️ **{title}**\n\n{message}")