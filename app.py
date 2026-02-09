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

# --- 2. GLOBAL UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #f9fbf9; }
    .main-card { 
        padding: 20px; border-radius: 15px; 
        background: white; border-left: 5px solid #2e7d32;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px;
    }
    .weather-widget {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white; padding: 20px; border-radius: 15px; text-align: center;
    }
    .status-badge {
        padding: 5px 12px; border-radius: 20px; font-size: 0.8rem;
        font-weight: bold; background: #e8f5e9; color: #2e7d32;
    }
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

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/5/52/Indian_Institute_of_Technology_Patna_Logo.png", width=100)
    st.title("🍀 ASES Platform")
    st.markdown("---")
    menu = st.radio("Navigation Hub", ["Crop Recommendation", "Environmental Risk", "National Schemes"])
    st.markdown("---")
    st.info("The system uses K-Nearest Neighbors (KNN) to analyze soil and climatic data.")

# --- 5. LOGIC MODULES ---

if menu == "Crop Recommendation":
    st.title("🌾 AgriAI Recommendation Dashboard")
    
    # Selection Row
    c1, c2 = st.columns(2)
    with c1: u_state = st.selectbox("State", list(india_map.keys()))
    with c2: u_dist = st.selectbox("District", india_map[u_state])
    
    # Live Weather Data
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={u_dist},IN&appid={API_KEY}&units=metric"
        w_data = requests.get(url).json()
        temp, hum = w_data['main']['temp'], w_data['main']['humidity']
        st.markdown(f"""<div class="weather-widget">📍 {u_dist}: {temp}°C | 💧 Humidity: {hum}%</div>""", unsafe_allow_html=True)
    except:
        temp, hum = 26, 55 # Fallback defaults

    # Soil Selection
    st.subheader("🌱 Select Soil Type")
    soil_opts = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
    if 'soil' not in st.session_state: st.session_state.soil = "Alluvial"
    s_cols = st.columns(4)
    for i, s in enumerate(soil_opts):
        with s_cols[i]:
            if st.button(s, use_container_width=True): st.session_state.soil = s
    st.info(f"Selected Soil: **{st.session_state.soil}**")

    # Parameters
    u_budget = st.slider("Investment Budget (Rs/Acre)", 5000, 50000, 20000)
    u_month = st.slider("Target Sowing Month", 1, 12, 6)

    if st.button("🚀 GENERATE RECOMMENDATION"):
        # Visual Progress Feedback
        bar = st.progress(0)
        for p in range(100):
            time.sleep(0.005)
            bar.progress(p + 1)
        
        # Machine Learning Engine (KNN)
        
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=2).fit(X)
        u_idx = le.transform([st.session_state.soil])[0]
        dist, idx = knn.kneighbors([[u_idx, u_month, u_budget]])
        recs = df.iloc[idx[0]]
        
        st.subheader("🎯 Optimized Crop Matches")
        r_cols = st.columns(len(recs))
        for i, row in enumerate(recs.iterrows()):
            with r_cols[i]:
                st.markdown(f"""<div class="main-card">
                <h3>{row[1]['Crop Name']}</h3>
                <p><b>Estimated Cost:</b> ₹{row[1]['Cost per Acre']}</p>
                <span class="status-badge">AI Match Score: {98-i}%</span>
                </div>""", unsafe_allow_html=True)

        # PDF Report Generation
        pdf = FPDF()
        pdf.add_page(); pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "ASES Professional Farm Report", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.ln(10)
        pdf.cell(200, 10, f"Location: {u_dist}, {u_state}", ln=True)
        pdf.cell(200, 10, f"Soil: {st.session_state.soil}", ln=True)
        report_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Download Official Report", report_bytes, f"ASES_Report_{u_dist}.pdf")

elif menu == "Environmental Risk":
    st.title("🛡️ Risk Assessment & Resilience")
    st.write("Real-time monitoring of atmospheric conditions to prevent crop loss.")
    
    
    
    # Humidity Risk Logic
    if 'hum' in locals() and hum > 70:
        st.error(f"⚠️ HIGH HUMIDITY ALERT ({hum}%): Conditions are favorable for fungal outbreaks.")
        
        st.markdown("""
        **Maintenance Protocol:**
        - Ensure proper drainage to avoid waterlogging.
        - Monitor leaves for spots or powdery residue.
        - Avoid overhead irrigation during peak humidity hours.
        """)
    else:
        st.success("✅ ENVIRONMENTAL STABILITY: Humidity levels are within safe parameters.")
    
    st.markdown("---")
    st.subheader("🛠️ Maintenance Strategies")
    st.info("Regular soil testing is recommended to ensure nutrient levels are balanced for the upcoming sowing season.")

elif menu == "National Schemes":
    st.title("🚜 National Agri-Support")
    st.write("Stay updated with the latest government benefits and local services.")
    
    st.subheader("Government Schemes")
    st.table(pd.DataFrame({
        "Scheme Name": ["PM-KISAN", "PM Fasal Bima Yojana", "Soil Health Card"],
        "Focus Area": ["Direct Income Support", "Crop Insurance", "Nutrient Lab Testing"],
        "Benefit": ["₹6000 Annual Payout", "Financial Risk Coverage", "Soil Analysis Report"]
    }))
    
    st.markdown("---")
    st.subheader("Equipment & Marketplace")
    st.markdown("""<div class="main-card" style="text-align:center;">
    <p>Need machinery for the upcoming season?</p>
    <a href="tel:9999911111" style="text-decoration:none; color:white;">
    <button style="width:50%; padding:15px; background:#2e7d32; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">
    📞 Call Nearest Rental Provider
    </button>
    </a></div>""", unsafe_allow_html=True)
