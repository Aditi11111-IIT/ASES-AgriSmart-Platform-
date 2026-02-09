import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
import requests
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ASES: Agri-Smart", layout="wide", page_icon="🌾")
API_KEY = "44ce6d6e018ff31baf4081ed56eb7fb7"

# --- 2. UNIVERSAL CONTRAST CSS ---
st.markdown("""
    <style>
    /* Ensures text remains visible across all themes */
    .stApp { color: #202124; }
    
    /* Elegant Telegram-style Cards */
    .main-card { 
        padding: 25px; border-radius: 12px; 
        background-color: rgba(255, 255, 255, 0.9); 
        border: 1px solid #2481CC; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        margin-bottom: 20px;
        color: #1c1c1c !important; /* Dark text for light background */
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] { background-color: #243139 !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: #ffffff !important; }

    /* Button Colors */
    .stButton>button {
        background-color: #2481CC; color: white !important;
        border-radius: 8px; font-weight: 600; width: 100%;
    }
    
    /* Responsive Highlighting */
    .highlight-text { color: #2481CC; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA & WEATHER ---
@st.cache_data
def load_agri_data():
    crops = {
        'Crop Name': ['Wheat', 'Rice', 'Cotton', 'Maize', 'Groundnut', 'Soybean', 'Mustard', 'Sugarcane'],
        'Soil Type': ['Alluvial', 'Alluvial', 'Black Soil', 'Red Soil', 'Sandy', 'Black Soil', 'Alluvial', 'Loamy'],
        'Water Requirement': [500, 1200, 800, 600, 400, 700, 450, 1500],
        'Sowing Month': [11, 6, 6, 6, 5, 6, 10, 2],
        'Cost per Acre': [15000, 25000, 20000, 12000, 18000, 16000, 14000, 30000]
    }
    pest_data = {
        'Crop': ['Wheat', 'Rice', 'Cotton', 'Sugarcane'],
        'Common Pest': ['Rust/Aphids', 'Stem Borer', 'Bollworm', 'Red Rot'],
        'Fertilizer': ['NPK 12:32:16', 'Urea + Zinc', 'DAP + Potash', 'Nitrogen Rich'],
        'Pesticide': ['Tilt (Propiconazole)', 'Chlorpyrifos', 'Spinosad', 'Carbendazim']
    }
    return pd.DataFrame(crops), pd.DataFrame(pest_data)

df, pest_df = load_agri_data()
le = LabelEncoder()
df['Soil_Idx'] = le.fit_transform(df['Soil Type'])

# --- 4. SESSION STATE & LOCATION ---
if 'temp' not in st.session_state: st.session_state.temp = 25
if 'hum' not in st.session_state: st.session_state.hum = 50

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/5/52/Indian_Institute_of_Technology_Patna_Logo.png", width=120)
    st.title("ASES NAVIGATION")
    tab = st.radio("SELECT SERVICE", ["🌾 Crop Engine", "🛡️ Pest & Fertilizer", "🚜 Rental Hub", "📜 Govt Schemes"])
    st.markdown("---")
    india_map = {"Bihar": ["Patna", "Gaya"], "Punjab": ["Ludhiana", "Amritsar"], "Maharashtra": ["Pune", "Mumbai"]}
    st_loc = st.selectbox("Your State", list(india_map.keys()))
    dt_loc = st.selectbox("Your District", india_map[st_loc])
    
    if st.button("Update Local Weather"):
        try:
            w_url = f"http://api.openweathermap.org/data/2.5/weather?q={dt_loc},IN&appid={API_KEY}&units=metric"
            res = requests.get(w_url).json()
            st.session_state.temp, st.session_state.hum = res['main']['temp'], res['main']['humidity']
            st.success("Weather Synced!")
        except: st.error("API Link Error")

# --- 5. TABS LOGIC ---

if tab == "🌾 Crop Engine":
    st.title("AgriAI Smart Recommendations")
    st.info(f"📍 Location: {dt_loc} | Temp: {st.session_state.temp}°C | Humidity: {st.session_state.hum}%")
    
    st.markdown('<div class="main-card"><b>Instruction:</b> Select your soil type to start.</div>', unsafe_allow_html=True)
    soil_opts = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
    if 'soil' not in st.session_state: st.session_state.soil = "Alluvial"
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
        recs = df.iloc[idx[0]]
        
        cols = st.columns(2)
        for i, row in enumerate(recs.iterrows()):
            with cols[i]:
                st.markdown(f"""<div class="main-card">
                <h3>{row[1]['Crop Name']}</h3>
                <p>Match Score: <span class="highlight-text">{99-i}%</span></p>
                <p>Est. Cost: ₹{row[1]['Cost per Acre']}</p>
                </div>""", unsafe_allow_html=True)

elif tab == "🛡️ Pest & Fertilizer":
    st.title("Protection & Nutrition Hub")
    
    st.markdown('<div class="main-card"><b>Instruction:</b> Select a crop to view specific protection and nutrient strategies.</div>', unsafe_allow_html=True)
    
    target_crop = st.selectbox("Select Crop", pest_df['Crop'].unique())
    data = pest_df[pest_df['Crop'] == target_crop].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="main-card">
        <h4>🛡️ Pest Control</h4>
        <p><b>Common Threat:</b> {data['Common Pest']}</p>
        <p><b>Recommended Pesticide:</b> {data['Pesticide']}</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="main-card">
        <h4>🧪 Nutrition Plan</h4>
        <p><b>Fertilizer Mix:</b> {data['Fertilizer']}</p>
        <p><b>Application:</b> Before Sowing & Top Dressing</p>
        </div>""", unsafe_allow_html=True)
    
    if st.session_state.hum > 70:
        st.warning(f"🚨 Humidity alert ({st.session_state.hum}%): Risk of Fungal Infection is high. Apply Carbendazim.")
        

elif tab == "🚜 Rental Hub":
    st.title(f"Machinery Marketplace: {dt_loc}")
    st.markdown('<div class="main-card"><b>Instruction:</b> Contact local owners for machinery rentals. Rates are per hour.</div>', unsafe_allow_html=True)
    
    # Static data simulation of local providers
    rentals = [
        {"Machine": "Mahindra Tractor", "Owner": "Suresh Kumar", "Rate": "₹800/hr", "Contact": "9876543210"},
        {"Machine": "Combine Harvester", "Owner": "Amrit Singh", "Rate": "₹2500/hr", "Contact": "9988776655"},
        {"Machine": "Rotavator", "Owner": "Vikram Patil", "Rate": "₹600/hr", "Contact": "9122334455"},
        {"Machine": "Power Tiller", "Owner": "Mohammad Arif", "Rate": "₹400/hr", "Contact": "8877990011"}
    ]
    
    for r in rentals:
        with st.expander(f"🚜 {r['Machine']} - {r['Rate']}"):
            st.write(f"**Owner:** {r['Owner']}")
            st.write(f"**Availability:** Immediate")
            st.markdown(f"""<a href="tel:{r['Contact']}" style="text-decoration:none;">
            <button style="background:#2481CC; color:white; border:none; padding:10px; border-radius:5px; width:100%;">
            📞 Call {r['Contact']}
            </button></a>""", unsafe_allow_html=True)

elif tab == "📜 Govt Schemes":
    st.title("Agricultural Schemes")
    st.markdown('<div class="main-card"><b>Instruction:</b> Detailed data on active Indian farming incentives.</div>', unsafe_allow_html=True)
    st.table(pd.DataFrame({
        "Scheme Name": ["PM-KISAN", "PMFBY", "KCC", "Soil Health Card"],
        "Financial Benefit": ["₹6000/yr Cash Support", "Crop Insurance Cover", "Low Interest Loan", "Lab Analysis Report"]
    }))
