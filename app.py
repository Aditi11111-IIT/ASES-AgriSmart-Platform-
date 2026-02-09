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

# --- 2. UNIVERSAL CONTRAST CSS (Fixed Visibility) ---
st.markdown("""
    <style>
    /* Global contrast for light/dark modes */
    .stApp { background-color: #f4f7f9; }
    .main-card { 
        padding: 25px; border-radius: 12px; 
        background-color: #ffffff; 
        border: 1px solid #e0e0e0; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
        margin-bottom: 20px;
        color: #1c1c1c !important;
    }
    [data-testid="stSidebar"] { background-color: #243139 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stButton>button {
        background-color: #2481CC; color: white !important;
        border-radius: 8px; font-weight: 600; width: 100%; border: none;
    }
    h1, h2, h3 { color: #2481CC !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & ANALYTICS ENGINE ---
@st.cache_data
def load_agri_data():
    crops = {
        'Crop Name': ['Wheat', 'Rice', 'Cotton', 'Maize', 'Groundnut', 'Soybean', 'Mustard', 'Sugarcane'],
        'Soil Type': ['Alluvial', 'Alluvial', 'Black Soil', 'Red Soil', 'Sandy', 'Black Soil', 'Alluvial', 'Loamy'],
        'Water Requirement': [500, 1200, 800, 600, 400, 700, 450, 1500],
        'Sowing Month': [11, 6, 6, 6, 5, 6, 10, 2],
        'Cost per Acre': [15000, 25000, 20000, 12000, 18000, 16000, 14000, 30000]
    }
    return pd.DataFrame(crops)

df = load_agri_data()
le = LabelEncoder()
df['Soil_Idx'] = le.fit_transform(df['Soil Type'])

# Initialize Session States
if 'temp' not in st.session_state: st.session_state.temp = 25
if 'hum' not in st.session_state: st.session_state.hum = 50
if 'soil' not in st.session_state: st.session_state.soil = "Alluvial"
if 'recs' not in st.session_state: st.session_state.recs = None

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/5/52/Indian_Institute_of_Technology_Patna_Logo.png", width=120)
    st.title("ASES NAVIGATION")
    tab = st.radio("SELECT SERVICE", ["🌾 Crop Engine", "🛡️ Pest & Fertilizer", "🚜 Rental Hub", "📜 Govt Schemes", "📊 Farmer Report"])
    st.markdown("---")
    india_map = {"Bihar": ["Patna", "Gaya"], "Punjab": ["Ludhiana", "Amritsar"], "Maharashtra": ["Pune", "Mumbai"]}
    st.session_state.u_state = st.selectbox("Your State", list(india_map.keys()))
    st.session_state.u_dist = st.selectbox("Your District", india_map[st.session_state.u_state])
    
    if st.button("Sync Weather"):
        try:
            w_url = f"http://api.openweathermap.org/data/2.5/weather?q={st.session_state.u_dist},IN&appid={API_KEY}&units=metric"
            res = requests.get(w_url).json()
            st.session_state.temp, st.session_state.hum = res['main']['temp'], res['main']['humidity']
        except: st.error("Weather Sync Error")

# --- 5. TABS LOGIC ---

if tab == "🌾 Crop Engine":
    st.title("AgriAI Smart Recommendations")
    st.info(f"📍 Location: {st.session_state.u_dist} | {st.session_state.temp}°C | {st.session_state.hum}% Humidity")
    
    st.markdown('<div class="main-card"><b>Instruction:</b> Select your soil type to begin.</div>', unsafe_allow_html=True)
    soil_opts = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
    s_cols = st.columns(4)
    for i, s in enumerate(soil_opts):
        with s_cols[i]:
            if st.button(s): st.session_state.soil = s
    
    bud = st.slider("Investment Budget (₹/Acre)", 5000, 50000, 15000)
    
    if st.button("🚀 FIND BEST CROPS"):
        
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=2).fit(X)
        u_idx = le.transform([st.session_state.soil])[0]
        dist, idx = knn.kneighbors([[u_idx, 6, bud]])
        st.session_state.recs = df.iloc[idx[0]]
        st.success("Recommendations Updated! Go to Farmer Report tab to see your full summary.")

elif tab == "🛡️ Pest & Fertilizer":
    st.title("Protection & Nutrition")
    
    st.markdown('<div class="main-card"><b>Instruction:</b> High humidity triggers risk alerts. Monitor local levels.</div>', unsafe_allow_html=True)
    if st.session_state.hum > 70:
        st.warning(f"🚨 High Risk: Humidity is {st.session_state.hum}%. Fungal infections are likely.")
        

elif tab == "🚜 Rental Hub":
    st.title(f"Machinery Marketplace: {st.session_state.u_dist}")
    rentals = [
        {"Machine": "Mahindra Tractor", "Rate": "₹800/hr", "Contact": "9876543210"},
        {"Machine": "Combine Harvester", "Rate": "₹2500/hr", "Contact": "9988776655"}
    ]
    for r in rentals:
        with st.expander(f"🚜 {r['Machine']} ({r['Rate']})"):
            st.markdown(f'<a href="tel:{r['Contact']}"><button style="width:100%; padding:10px; background:#2481CC; color:white; border:none; border-radius:5px;">📞 Call Owner</button></a>', unsafe_allow_html=True)

elif tab == "📊 Farmer Report":
    st.title("Final Assessment Report")
    st.markdown('<div class="main-card"><b>Instruction:</b> Review your personalized farming strategy below.</div>', unsafe_allow_html=True)
    
    # Report Layout
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="main-card">
        <h4>📋 Farm Profile</h4>
        <p><b>Location:</b> {st.session_state.u_dist}, {st.session_state.u_state}</p>
        <p><b>Soil Type:</b> {st.session_state.soil}</p>
        <p><b>Climate:</b> {st.session_state.temp}°C | {st.session_state.hum}% Hum</p>
        </div>""", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="main-card"><h4>🌱 Top Recommended Crop</h4>', unsafe_allow_html=True)
        if st.session_state.recs is not None:
            top_crop = st.session_state.recs.iloc[0]['Crop Name']
            st.write(f"Based on AI Analysis: **{top_crop}**")
        else:
            st.write("No data yet. Please use the Crop Engine first.")
        st.markdown('</div>', unsafe_allow_html=True)

    # PDF Generation Logic
    if st.button("📥 Download PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="ASES: Farmer Assessment Report", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Location: {st.session_state.u_dist}, {st.session_state.u_state}", ln=True)
        pdf.cell(200, 10, txt=f"Soil Type: {st.session_state.soil}", ln=True)
        if st.session_state.recs is not None:
            pdf.cell(200, 10, txt=f"Recommended Crop: {st.session_state.recs.iloc[0]['Crop Name']}", ln=True)
        
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="Click to Save PDF", data=pdf_output, file_name="Farmer_Report.pdf", mime="application/pdf")

elif tab == "📜 Govt Schemes":
    st.title("Government Library")
    st.table(pd.DataFrame({"Scheme": ["PM-KISAN", "PMFBY"], "Benefit": ["₹6000 Payout", "Insurance"]}))
