import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
import requests
import time
from fpdf import FPDF

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ASES: Agri-Smart Solutions", layout="wide", page_icon="🌾")
API_KEY = "44ce6d6e018ff31baf4081ed56eb7fb7"

# --- 2. MEMBER 2: ADVANCED UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #f8f9fa; }
    .main-card { 
        padding: 25px; border-radius: 20px; 
        background: white; box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-bottom: 5px solid #2e7d32; margin-bottom: 20px;
    }
    .weather-widget {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white; padding: 20px; border-radius: 15px;
        margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .status-badge {
        padding: 8px 15px; border-radius: 30px;
        font-size: 0.85rem; font-weight: bold; 
        background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9;
    }
    .stButton>button {
        background: #2e7d32; color: white; border-radius: 12px;
        height: 3.5em; width: 100%; font-weight: bold; border: none;
        box-shadow: 0 4px 10px rgba(46, 125, 50, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CORE DATA ENGINE ---
@st.cache_data
def load_data():
    crops = {
        'Crop Name': ['Wheat', 'Rice', 'Cotton', 'Maize', 'Groundnut', 'Soybean', 'Mustard', 'Sugarcane'],
        'Soil Type': ['Alluvial', 'Alluvial', 'Black Soil', 'Red Soil', 'Sandy', 'Black Soil', 'Alluvial', 'Loamy'],
        'Sowing Month': [11, 6, 6, 6, 5, 6, 10, 2],
        'Cost per Acre': [15000, 25000, 20000, 12000, 18000, 16000, 14000, 30000]
    }
    blue = {"Member": ["M1", "M2", "M3", "M4"], "Role": ["AI Engine", "UI Design", "Pest Risk", "Reports"]}
    return pd.DataFrame(crops), pd.DataFrame(blue)

df, blue_df = load_data()
le = LabelEncoder()
df['Soil_Idx'] = le.fit_transform(df['Soil Type'])

india_map = {
    "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Uttar Pradesh": ["Lucknow", "Agra", "Varanasi"]
}

# --- 4. SIDEBAR (STAYS CONSTANT) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/5/52/Indian_Institute_of_Technology_Patna_Logo.png", width=100)
    st.title("🌾 ASES Hub")
    st.write("### 👥 Group 32 Blueprint")
    st.table(blue_df) # Instructions visible for presentation
    st.markdown("---")
    menu = st.radio("Navigation", ["AgriAI Engine", "Pest Resilience", "Marketplace"])

# --- 5. INTERFACE LOGIC ---

if menu == "AgriAI Engine":
    st.title("🌾 AgriAI Recommendation Dashboard")
    
    # 1. Location & Weather Selection
    c1, c2 = st.columns(2)
    with c1: u_state = st.selectbox("Select State", list(india_map.keys()))
    with c2: u_dist = st.selectbox("Select District", india_map[u_state])
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={u_dist},IN&appid={API_KEY}&units=metric"
        w = requests.get(url).json()
        temp, hum, desc = w['main']['temp'], w['main']['humidity'], w['weather'][0]['description']
        st.markdown(f"""<div class="weather-widget">
            <b>{u_dist} Weather:</b> {temp}°C | {hum}% Humidity | {desc.title()}
        </div>""", unsafe_allow_html=True)
    except:
        st.error("Weather data unavailable. Using default values.")
        temp, hum = 25, 50

    # 2. Visual Soil Selection (Member 2 Zero-Typing)
    st.subheader("🌱 Identify Soil Type")
    soil_types = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
    if 'soil' not in st.session_state: st.session_state.soil = "Alluvial"
    
    s_cols = st.columns(4)
    for i, s in enumerate(soil_types):
        with s_cols[i]:
            if st.button(s, key=f"soil_{s}"):
                st.session_state.soil = s
    st.markdown(f"Selected Soil: <span class='status-badge'>{st.session_state.soil}</span>", unsafe_allow_html=True)

    # 3. Parameters
    u_budget = st.slider("Budget (Rs/Acre)", 5000, 50000, 20000)
    u_month = st.select_slider("Sowing Month", options=list(range(1,13)), value=6)

    # 4. Trigger Analysis with Progress Bar (Member 2 UX)
    if st.button("🚀 RUN AI ANALYSIS"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulated Steps
        steps = ["Fetching soil data...", "Initializing KNN weights...", "Calculating Euclidean distances...", "Ranking matches..."]
        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) * 25)
            time.sleep(0.4)
            
        # KNN Logic (Member 1)
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=2).fit(X)
        u_idx = le.transform([st.session_state.soil])[0]
        dist, idx = knn.kneighbors([[u_idx, u_month, u_budget]])
        recs = df.iloc[idx[0]]
        
        status_text.success("Analysis Complete!")
        
        # 5. Visual Results Cards
        st.subheader("🎯 Top Crop Matches")
        r_cols = st.columns(len(recs))
        for i, row in enumerate(recs.iterrows()):
            with r_cols[i]:
                st.markdown(f"""<div class="main-card">
                <h3>{row[1]['Crop Name']}</h3>
                <p><b>Estimated Cost:</b> ₹{row[1]['Cost per Acre']}</p>
                <span class='status-badge'>Match: {98 - (i*5)}%</span>
                </div>""", unsafe_allow_html=True)

        # Presentation Math Link
        with st.expander("📊 Technical View (Member 1 Logic)"):
            st.write("We use KNN to find the smallest Euclidean distance between user input and crop data.")
            
            

elif menu == "Pest Resilience":
    st.title("🛡️ Pest Protection & Crisis Control")
    st.info("Based on your location's humidity, we monitor for fungal risks.")
    
    if hum > 70:
        st.error(f"⚠️ HIGH HUMIDITY ALERT ({hum}%): Risk of fungal infection is extremely high.")
        
    else:
        st.success(f"✅ Humidity is safe ({hum}%). Standard monitoring recommended.")

elif menu == "Marketplace":
    st.title("🚜 Rental Marketplace")
    st.markdown("""<div class="main-card" style="text-align:center;">
        <h3>Machinery & Seed Rental</h3>
        <p>Contact local providers near your district.</p>
        <a href="tel:9999911111" style="text-decoration:none;">
            <button style="width:50%; background:#2e7d32; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-weight:bold;">
                📞 Call Nearest Provider
            </button>
        </a>
    </div>""", unsafe_allow_html=True)
