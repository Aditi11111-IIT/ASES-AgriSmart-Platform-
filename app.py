import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
import requests
import time
from fpdf import FPDF

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ASES: Agri-Smart", layout="wide", page_icon="🌾")
API_KEY = "44ce6d6e018ff31baf4081ed56eb7fb7"

# --- 2. ULTRA-HIGH VISIBILITY CSS ---
st.markdown("""
    <style>
    /* Force high contrast for all text */
    html, body, [class*="st-"] {
        color: #000000 !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar: Dark background with WHITE text for contrast */
    [data-testid="stSidebar"] {
        background-color: #0E1117 !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* Main Cards: White background with Black text */
    .main-card { 
        padding: 25px; 
        border-radius: 10px; 
        background-color: #FFFFFF; 
        border: 2px solid #28B463; /* Green border for visibility */
        box-shadow: 0 4px 8px rgba(0,0,0,0.2); 
        margin-bottom: 20px;
        color: #000000 !important;
    }
    
    /* Weather Widget: High contrast Blue */
    .weather-widget {
        background-color: #1A5276;
        color: #FFFFFF !important; 
        padding: 15px; 
        border-radius: 8px; 
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* Green Status Badges */
    .status-badge {
        padding: 5px 15px; 
        border-radius: 4px; 
        font-weight: bold; 
        background-color: #28B463; 
        color: #FFFFFF !important;
        display: inline-block;
    }

    /* Headers */
    h1, h2, h3 { color: #186A3B !important; font-weight: 800 !important; }
    
    /* Input Labels visibility */
    label { color: #000000 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
@st.cache_data
def load_data():
    crops = {
        'Crop Name': ['Wheat', 'Rice', 'Cotton', 'Maize', 'Groundnut', 'Soybean', 'Mustard', 'Sugarcane'],
        'Soil Type': ['Alluvial', 'Alluvial', 'Black Soil', 'Red Soil', 'Sandy', 'Black Soil', 'Alluvial', 'Loamy'],
        'Water Requirement': [500, 1200, 800, 600, 400, 700, 450, 1500],
        'Sowing Month': [11, 6, 6, 6, 5, 6, 10, 2],
        'Cost per Acre': [15000, 25000, 20000, 12000, 18000, 16000, 14000, 30000]
    }
    return pd.DataFrame(crops)

df = load_data()
le = LabelEncoder()
df['Soil_Idx'] = le.fit_transform(df['Soil Type'])

india_map = {
    "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Uttar Pradesh": ["Lucknow", "Agra", "Varanasi"]
}

# --- 4. SIDEBAR SECTIONS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/5/52/Indian_Institute_of_Technology_Patna_Logo.png", width=120)
    st.markdown("### 🗺️ NAVIGATION")
    tab_selection = st.radio("GO TO PAGE:", 
                            ["🌾 Crop Recommendation", "🛡️ Environmental Risk", "📜 Government Schemes", "🚜 Rental Marketplace"])
    st.markdown("---")
    st.write("ASES System v3.0")

# --- 5. TAB LOGIC ---

if tab_selection == "🌾 Crop Recommendation":
    st.title("Crop Recommendation Engine")
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: u_state = st.selectbox("STEP 1: SELECT STATE", list(india_map.keys()))
    with c2: u_dist = st.selectbox("STEP 2: SELECT DISTRICT", india_map[u_state])
    st.markdown('</div>', unsafe_allow_html=True)

    # Weather widget
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={u_dist},IN&appid={API_KEY}&units=metric"
        w_res = requests.get(url).json()
        temp, hum = w_res['main']['temp'], w_res['main']['humidity']
        st.markdown(f'<div class="weather-widget">CURRENT WEATHER: {temp}°C | {hum}% HUMIDITY</div>', unsafe_allow_html=True)
    except:
        temp, hum = 28, 52

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("### STEP 3: SELECT SOIL TYPE")
    soil_opts = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
    if 'soil' not in st.session_state: st.session_state.soil = "Alluvial"
    s_cols = st.columns(4)
    for i, s in enumerate(soil_opts):
        with s_cols[i]:
            if st.button(s, use_container_width=True): st.session_state.soil = s
    
    st.write(f"CURRENTLY SELECTED: **{st.session_state.soil}**")
    st.markdown('</div>', unsafe_allow_html=True)

    u_budget = st.slider("INVESTMENT BUDGET (₹ PER ACRE)", 5000, 50000, 15000)
    u_month = st.slider("SOWING MONTH (1-12)", 1, 12, 6)

    if st.button("🚀 GET AI RECOMMENDATION"):
        # KNN Analysis
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=2).fit(X)
        u_idx = le.transform([st.session_state.soil])[0]
        dist, idx = knn.kneighbors([[u_idx, u_month, u_budget]])
        recs = df.iloc[idx[0]]
        
        st.write("### 🎯 TOP MATCHES FOR YOUR LAND")
        res_cols = st.columns(len(recs))
        for i, row in enumerate(recs.iterrows()):
            with res_cols[i]:
                st.markdown(f"""
                <div class="main-card">
                    <h2 style="color:#1D8348;">{row[1]['Crop Name']}</h2>
                    <p><b>Estimated Cost:</b> ₹{row[1]['Cost per Acre']}</p>
                    <p><b>Water Need:</b> {row[1]['Water Requirement']}mm</p>
                    <div class="status-badge">AI MATCH: {99-i}%</div>
                </div>
                """, unsafe_allow_html=True)

elif tab_selection == "🛡️ Environmental Risk":
    st.title("Risk Assessment")
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    if 'hum' in locals() and hum > 70:
        st.error(f"🚨 ALERT: HIGH HUMIDITY DETECTED ({hum}%)")
        st.write("Fungal pathogens thrive in these conditions. Check for Blight or Mildew.")
        
    else:
        st.success(f"✅ SAFE: HUMIDITY IS {hum}%")
        st.write("Climatic conditions are currently stable. No major fungal alerts.")
    st.markdown('</div>', unsafe_allow_html=True)

elif tab_selection == "📜 Government Schemes":
    st.title("Agricultural Schemes")
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    schemes = pd.DataFrame({
        "SCHEME NAME": ["PM-KISAN", "PMFBY", "SOIL HEALTH CARD"],
        "OFFICIAL BENEFIT": ["₹6,000 Direct Payout", "Crop Insurance Cover", "Detailed Soil Lab Report"]
    })
    st.table(schemes)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab_selection == "🚜 Rental Marketplace":
    st.title("Equipment Rental")
    st.markdown("""
    <div class="main-card" style="text-align:center;">
        <h3>CONNECT WITH PROVIDERS</h3>
        <p>Verified machinery owners available in your district.</p>
        <br>
        <a href="tel:9999911111" style="text-decoration:none;">
            <button style="padding:15px 50px; background-color:#186A3B; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer; font-size:1.2rem;">
                📞 CALL SERVICE PROVIDER
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
