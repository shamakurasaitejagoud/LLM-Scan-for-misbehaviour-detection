import streamlit as st
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set page config for a clean widescreen layout
st.set_page_config(
    page_title="LLM Scan Graph Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide Streamlit header/footer and force dark background matching Next.js
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    body {
        background-color: #131314;
        color: #e2e8f0;
    }
    .stApp {
        background-color: #131314;
    }
    .metric-card {
        background-color: #1e1f22;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 20px;
        font-weight: bold;
        color: #fff;
    }
    .metric-label {
        font-size: 12px;
        color: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

# Parse prompt and token from query parameters
query_params = st.query_params
prompt = query_params.get("prompt", "")
token = query_params.get("token", "")

if not prompt:
    st.info("No prompt provided in query parameters. Displaying interactive scanner input.")
    prompt = st.text_input("Enter prompt to scan:", "What is 2+2?")

# Endpoint to fetch cached scan results or run a new scan
import os
backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/") + "/scan-results"

headers = {}
if token:
    headers["Authorization"] = f"Bearer {token}"

try:
    with st.spinner("Fetching scan analysis from backend..."):
        response = requests.get(backend_url, params={"prompt": prompt}, headers=headers, timeout=120)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("status") == "processing":
            st.warning("⏳ **Analysis is currently in progress...**")
            st.info("The model is scanning activation states. This page will refresh automatically.")
            import time
            time.sleep(3)
            st.rerun()
            st.stop()
            
        # Extract variables
        layer_aie = data.get("layer_aie", [])
        num_layers = data.get("num_layers", 32)
        threat_assessment = data.get("threat_assessment", {})
        stats = data.get("stats", {})
        is_safe = data.get("is_safe", True)
        safety_summary = data.get("safety_summary", "")
        generated_text = data.get("generated_text", "")
        tokens = data.get("tokens", [])
        prompt_aie = data.get("prompt_aie", [])
        
        # Display header
        st.markdown(f"### Prompt Scan Analysis")
        st.markdown(f"**Prompt:** *{prompt}*")
        
        # Safety alert
        if is_safe:
            st.success(f"🟢 **{safety_summary}**")
        else:
            st.error(f"🔴 **{safety_summary}**")
            
        # Top metrics columns
        st.markdown("#### Threat Assessment & Statistics")
        col_threat, col_stats = st.columns([1, 1])
        
        with col_threat:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("##### Threat Probabilities")
            for key, val in threat_assessment.items():
                # Progress bar display
                color = "red" if val > 0.8 else ("orange" if val > 0.4 else "green")
                val_percentage = val * 100
                st.markdown(f"**{key.capitalize()}**: {val:.2%} ({'High' if val > 0.8 else ('Moderate' if val > 0.4 else 'Low')})")
                st.progress(min(1.0, float(val)))
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_stats:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("##### Causal Statistical Features")
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("Mean Effect", f"{stats.get('mean', 0.0):.4f}")
                st.metric("Std Dev", f"{stats.get('std', 0.0):.4f}")
            with col_s2:
                st.metric("Range", f"{stats.get('range', 0.0):.4f}")
                st.metric("Kurtosis", f"{stats.get('kurtosis', 0.0):.4f}")
            with col_s3:
                st.metric("Skewness", f"{stats.get('skewness', 0.0):.4f}")
            st.markdown("</div>", unsafe_allow_html=True)

        # Draw graphs
        st.markdown("#### Causal Importance Visualization")
        
        # Set up matplotlib dark style
        plt.style.use('dark_background')
        
        # 1. Token-level Causal Effects (Prompt Intervention)
        st.markdown("##### Prompt Interventions: Token-level Causal Effect")
        
        fig1, ax1 = plt.subplots(figsize=(12, 3.5), facecolor='#131314')
        ax1.set_facecolor('#131314')
        
        # Plot bars
        bars = ax1.bar(range(len(tokens)), prompt_aie, color="#38bdf8", width=0.5)
        
        ax1.set_xticks(range(len(tokens)))
        ax1.set_xticklabels(tokens, fontsize=8, color="#94a3b8", rotation=30, ha='right')
        
        # Set yticks dynamically depending on max prompt_aie
        max_val = max(prompt_aie) if prompt_aie else 1.0
        ax1.set_ylim(-0.02, max_val * 1.25)
        
        # Grid and spines
        ax1.grid(True, which='both', color='#1e1f22', linestyle='-', linewidth=0.5, axis='y')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#1e1f22')
        ax1.spines['bottom'].set_color('#1e1f22')
        ax1.tick_params(axis='y', colors='#94a3b8', labelsize=8)
        ax1.set_ylabel("Causal Weight (Δ Prob)", fontsize=8, color="#94a3b8")
        
        # Add labels on top of the bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2.0, height + (max_val * 0.02), f"{height:.4f}", ha='center', va='bottom', fontsize=8, color='#e2e8f0')
            
        st.pyplot(fig1)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Layer-level Causal Effects (Layer Intervention)
        st.markdown("##### Layer Interventions: Causal Importance per Layer")
        
        x_layers = list(range(len(layer_aie)))
        fig2, ax2 = plt.subplots(figsize=(12, 3.5), facecolor='#131314')
        ax2.set_facecolor('#131314')
        
        # Plot bars for layers
        bars2 = ax2.bar(x_layers, layer_aie, color="#fda4af", width=0.6)
        
        ax2.set_xticks(x_layers)
        ax2.set_xticklabels([str(i) for i in x_layers], fontsize=8, color="#94a3b8")
        
        # Set yticks dynamically depending on max layer_aie
        max_layer_val = max(layer_aie) if layer_aie else 1.0
        ax2.set_ylim(-0.02, max_layer_val * 1.25)
        
        # Grid and spines
        ax2.grid(True, which='both', color='#1e1f22', linestyle='-', linewidth=0.5, axis='y')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#1e1f22')
        ax2.spines['bottom'].set_color('#1e1f22')
        ax2.tick_params(axis='y', colors='#94a3b8', labelsize=8)
        ax2.set_ylabel("Causal Weight (Δ Prob)", fontsize=8, color="#94a3b8")
        
        # Add labels on top of the bars
        for bar in bars2:
            height = bar.get_height()
            if height > 0.001:  # Only add labels if height is visible to avoid cluttering
                ax2.text(bar.get_x() + bar.get_width()/2.0, height + (max_layer_val * 0.02), f"{height:.4f}", ha='center', va='bottom', fontsize=8, color='#e2e8f0')
            
        st.pyplot(fig2)

    else:
        st.error(f"Failed to fetch data from backend. Status code: {response.status_code}")
        st.write(response.text)

except requests.exceptions.Timeout as e:
    st.markdown("""
        <div style="background-color: #42400e; border: 1px solid #5a5611; border-radius: 8px; padding: 16px; margin-bottom: 16px; margin-top: 16px;">
            <span style="color: #f6e05e; font-weight: bold;">⚠️ Request Timed Out:</span> <span style="color: #fef08a;">The backend server is busy processing other activation scans in queue. Please wait a moment and click below to retry.</span>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Retry Scan", key="retry_btn", help="Click to retry the scan"):
        st.rerun()
    st.markdown("""
        <style>
        .stButton>button {
            background-color: transparent !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            font-weight: normal !important;
        }
        .stButton>button:hover {
            border-color: rgba(255, 255, 255, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Could not connect to FastAPI backend on port 8000.")
    st.exception(e)
    st.info("Make sure you run the backend using: `python backend/main.py` first.")
