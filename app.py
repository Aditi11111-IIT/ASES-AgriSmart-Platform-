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

# --- 2. TELEGRAM ELEGANCE CSS ---
st.markdown("""
    <style>
    /* Telegram Palette */
    html, body, [class*="st-"] { color: #222222 !important; font-family: 'Inter', -apple-system, sans-serif; }
    
    /* Sidebar: Telegram Dark Blue */
    [data-testid="stSidebar"] {
        background-color: #243139 !important;
    }
    [data-testid="stSidebar"] * { color: #EFEFEF !important; }

    /* Elegant Card Layout */
    .main-card { 
        padding: 30px; border-radius: 12px; background-color: #FFFFFF; 
        border: 1px solid #E0E0E0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
        margin-bottom: 25px; color: #222222 !important;
    }
    
    /* Header & Action Buttons: Telegram Blue */
    .weather-widget {
        background-color: #2481CC; color: #FFFFFF !important; 
        padding: 20px; border-radius: 12px; text-align: center;
        font-size: 1.2rem; font-weight: 500; margin-bottom: 25px;
    }
    .stButton>button {
        background-color: #2481CC; color: white !important; border-radius: 8px;
        height: 3.5em; width: 100%; font-weight: 600; border: none;
    }
    
    .status-badge {
        padding: 6px 16px; border-radius: 20px; font-weight: bold; 
        background-color: #E1F5FE; color: #0288D1; display: inline-block;
    }

    h1, h2, h3 { color: #2481CC !important; font-weight: 700 !important; }
    label { color: #666666 !important; font-size: 0.9rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & WEATHER ENGINE ---
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

# Initialize Global Session State
if 'temp' not in st.session_state: st.session_state.temp = 25
if 'hum' not in st.session_state: st.session_state.hum = 50
if 'u_dist' not in st.session_state: st.session_state.u_dist = "Patna"

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/5/52/Indian_Institute_of_Technology_Patna_Logo.png", width=120)
    st.markdown("### ASES SERVICES")
    tab = st.radio("GO TO SECTION", ["🌾 Recommendations", "🛡️ Risk Center", "📜 Govt Library", "🚜 Resource Hub"])
    
    st.markdown("---")
    st.markdown("#### 📍 SET LOCATION")
    india_map = {"Bihar": ["Patna", "Gaya"], "Punjab": ["Ludhiana", "Amritsar"], 
                 "Maharashtra": ["Mumbai", "Pune"], "UP": ["Lucknow", "Agra"]}
    st_select = st.selectbox("State", list(india_map.keys()))
    dt_select = st.selectbox("District", india_map[st_select])
    st.session_state.u_dist = dt_select
    
    # Global Weather Update
    try:
        w_url = f"http://api.openweathermap.org/data/2.5/weather?q={dt_select},IN&appid={API_KEY}&units=metric"
        w_res = requests.get(w_url).json()
        st.session_state.temp = w_res['main']['temp']
        st.session_state.hum = w_res['main']['humidity']
    except: pass

# --- 5. TAB-SPECIFIC LAYOUTS ---

if tab == "🌾 Recommendations":
    st.title("AgriAI Crop Recommendation")
    st.markdown(f'<div class="weather-widget">📍 {st.session_state.u_dist}: {st.session_state.temp}°C | {st.session_state.hum}% Humidity</div>', unsafe_allow_html=True)

    # Instruction Card 1
    with st.container():
        st.markdown('<div class="main-card"><b>Instruction:</b> Select your land\'s soil type from the options below.</div>', unsafe_allow_html=True)
        soil_types = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
        if 'soil' not in st.session_state: st.session_state.soil = "Alluvial"
        s_cols = st.columns(4)
        for i, s in enumerate(soil_types):
            with s_cols[i]:
                if st.button(s): st.session_state.soil = s
        st.write(f"Current Choice: **{st.session_state.soil}**")

    # Instruction Card 2
    with st.container():
        st.markdown('<div class="main-card"><b>Instruction:</b> Adjust the budget and timing to find the best match.</div>', unsafe_allow_html=True)
        bud = st.slider("Budget (₹/Acre)", 5000, 50000, 15000)
        mon = st.slider("Month (1=Jan, 12=Dec)", 1, 12, 6)

    if st.button("🚀 RUN AI ANALYZER"):
        
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=2).fit(X)
        u_idx = le.transform([st.session_state.soil])[0]
        dist, idx = knn.kneighbors([[u_idx, mon, bud]])
        recs = df.iloc[idx[0]]
        
        st.subheader("Top Matches")
        r_cols = st.columns(len(recs))
        for i, row in enumerate(recs.iterrows()):
            with r_cols[i]:
                st.markdown(f"""<div class="main-card">
                <h3>{row[1]['Crop Name']}</h3>
                <p>₹{row[1]['Cost per Acre']} Cost</p>
                <div class="status-badge">{99-i}% Match</div>
                </div>""", unsafe_allow_html=True)

elif tab == "🛡️ Risk Center":
    st.title("Environmental Resilience")
    
    st.markdown('<div class="main-card"><b>Instruction:</b> Review regional humidity alerts to prepare maintenance cycles.</div>', unsafe_allow_html=True)
    
    if st.session_state.hum > 70:
        st.error(f"High Risk Alert: Humidity is at {st.session_state.hum}%")
        
    else:
        st.success(f"Safe: Humidity is at {st.session_state.hum}%. No fungal outbreaks expected.")

elif tab == "📜 Govt Library":
    st.title("National Scheme Database")
    st.markdown('<div class="main-card"><b>Instruction:</b> Check eligibility for the following active schemes.</div>', unsafe_allow_html=True)
    st.table(pd.DataFrame({
        "Scheme": ["PM-KISAN", "PMFBY", "Soil Card"],
        "Provision": ["Direct Cash Support", "Crop Insurance", "Soil Testing"]
    }))

elif tab == "🚜 Resource Hub":
    st.title("Machinery & Logistics")
    st.markdown(f'<div class="main-card"><b>Instruction:</b> Direct connect to verified equipment owners in {st.session_state.u_dist}.</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="main-card" style="text-align:center;">
        <a href="tel:9999911111" style="text-decoration:none;">
            <button style="background:#2481CC; color:white; padding:15px; border-radius:8px; border:none; width:60%; font-size:1.1rem; cursor:pointer;">
                📞 CONTACT NEAREST PROVIDER
            </button>
        </a>
    </div>""", unsafe_allow_html=True)
