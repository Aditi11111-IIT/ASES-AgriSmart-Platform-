import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
import requests
from fpdf import FPDF

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ASES: Agri-Smart", layout="wide", page_icon="🌾")
API_KEY = "44ce6d6e018ff31baf4081ed56eb7fb7"

# --- 2. TELEGRAM ELEGANCE & HIGH-CONTRAST CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-card { 
        padding: 25px; border-radius: 12px; 
        background-color: #ffffff; 
        border: 1px solid #e0e0e0; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
        margin-bottom: 20px;
        color: #1c1c1c !important; /* Forces dark text visibility */
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

# --- 3. DATA & LOGIC ENGINE ---
@st.cache_data
def load_agri_data():
    crops = {
        'Crop Name': ['Wheat', 'Rice', 'Cotton', 'Maize', 'Groundnut', 'Soybean', 'Mustard', 'Sugarcane'],
        'Soil Type': ['Alluvial', 'Alluvial', 'Black Soil', 'Red Soil', 'Sandy', 'Black Soil', 'Alluvial', 'Loamy'],
        'Sowing Month': [11, 6, 6, 6, 5, 6, 10, 2],
        'Cost per Acre': [15000, 25000, 20000, 12000, 18000, 16000, 14000, 30000]
    }
    pest_info = {
        'Crop': ['Wheat', 'Rice', 'Cotton', 'Sugarcane'],
        'Pest': ['Rust/Aphids', 'Stem Borer', 'Bollworm', 'Red Rot'],
        'Fertilizer': ['NPK 12:32:16', 'Urea', 'DAP', 'Nitrogen Rich']
    }
    return pd.DataFrame(crops), pd.DataFrame(pest_info)

df, pest_df = load_agri_data()
le = LabelEncoder()
df['Soil_Idx'] = le.fit_transform(df['Soil Type'])

# --- 4. SESSION STATE (Preserves data across tabs) ---
if 'temp' not in st.session_state: st.session_state.temp = 25
if 'hum' not in st.session_state: st.session_state.hum = 50
if 'soil' not in st.session_state: st.session_state.soil = "Alluvial"
if 'recs' not in st.session_state: st.session_state.recs = []

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/5/52/Indian_Institute_of_Technology_Patna_Logo.png", width=120)
    st.title("ASES NAVIGATION")
    tab = st.radio("GO TO SECTION", ["🌾 Crop Engine", "🛡️ Pest & Fertilizer", "🚜 Rental Hub", "📜 Govt Schemes", "📊 Farmer Report"])
    st.markdown("---")
    india_map = {"Bihar": ["Patna", "Gaya"], "Punjab": ["Ludhiana", "Amritsar"], "Maharashtra": ["Pune", "Mumbai"]}
    st.session_state.u_state = st.selectbox("State", list(india_map.keys()))
    st.session_state.u_dist = st.selectbox("District", india_map[st.session_state.u_state])
    
    if st.button("Sync Local Weather"):
        try:
            w_url = f"http://api.openweathermap.org/data/2.5/weather?q={st.session_state.u_dist},IN&appid={API_KEY}&units=metric"
            res = requests.get(w_url).json()
            st.session_state.temp, st.session_state.hum = res['main']['temp'], res['main']['humidity']
        except: st.error("Weather Sync Failed")

# --- 6. PAGE CONTENT ---

if tab == "🌾 Crop Engine":
    st.title("Crop Recommendation Engine")
    st.info(f"📍 {st.session_state.u_dist} | {st.session_state.temp}°C | {st.session_state.hum}% Humidity")
    
    st.markdown('<div class="main-card"><b>Instruction:</b> Select soil type and set your budget.</div>', unsafe_allow_html=True)
    soil_opts = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
    s_cols = st.columns(4)
    for i, s in enumerate(soil_opts):
        with s_cols[i]:
            if st.button(s): st.session_state.soil = s
    
    bud = st.slider("Investment Budget (₹/Acre)", 5000, 50000, 15000)
    
    if st.button("🚀 ANALYZE DATA"):
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=2).fit(X)
        u_idx = le.transform([st.session_state.soil])[0]
        dist, idx = knn.kneighbors([[u_idx, 6, bud]])
        st.session_state.recs = df.iloc[idx[0]]['Crop Name'].tolist()
        st.success("Analysis Complete. View results in the Farmer Report tab.")

elif tab == "🛡️ Pest & Fertilizer":
    st.title("Pest & Nutrition Hub")
    
    st.markdown('<div class="main-card"><b>Instruction:</b> High humidity (>70%) increases fungal risk.</div>', unsafe_allow_html=True)
    if st.session_state.hum > 70:
        st.warning(f"🚨 Humidity is {st.session_state.hum}%. High Risk of Blight.")
        

elif tab == "🚜 Rental Hub":
    st.title(f"Machinery Marketplace: {st.session_state.u_dist}")
    machines = [
        {"Name": "Tractor", "Owner": "Rajesh Kumar", "Phone": "9876543210", "Price": "₹700/hr"},
        {"Name": "Harvester", "Owner": "Gurpreet Singh", "Phone": "9988776655", "Price": "₹2200/hr"}
    ]
    for m in machines:
        with st.expander(f"{m['Name']} - {m['Price']}"):
            st.write(f"Owner: {m['Owner']}")
            st.markdown(f'<a href="tel:{m['Phone']}"><button style="width:100%; background:#2481CC; color:white; border:none; border-radius:5px; padding:10px;">📞 Call Owner</button></a>', unsafe_allow_html=True)

elif tab == "📊 Farmer Report":
    st.title("Personalized Farmer Report")
    st.markdown('<div class="main-card"><b>Instruction:</b> Review and download your generated farming summary.</div>', unsafe_allow_html=True)
    
    # Visual Layout
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="main-card">
        <h3>📍 Farm Details</h3>
        <p><b>Location:</b> {st.session_state.u_dist}, {st.session_state.u_state}</p>
        <p><b>Soil:</b> {st.session_state.soil}</p>
        <p><b>Humidity:</b> {st.session_state.hum}%</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="main-card"><h3>🌱 AI Recommendations</h3>', unsafe_allow_html=True)
        if st.session_state.recs:
            for crop in st.session_state.recs:
                st.write(f"✅ Recommended: **{crop}**")
        else:
            st.write("No data found. Use 'Crop Engine' first.")
        st.markdown('</div>', unsafe_allow_html=True)

    # PDF Logic
    if st.button("📥 GENERATE PDF REPORT"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(36, 129, 204) # Telegram Blue
        pdf.cell(200, 20, txt="ASES AGRI-REPORT", ln=True, align='C')
        
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Location: {st.session_state.u_dist}, {st.session_state.u_state}", ln=True)
        pdf.cell(200, 10, txt=f"Soil Selection: {st.session_state.soil}", ln=True)
        pdf.cell(200, 10, txt=f"Climate: {st.session_state.temp}C with {st.session_state.hum}% Humidity", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="AI Recommended Crops:", ln=True)
        pdf.set_font("Arial", '', 12)
        for crop in st.session_state.recs:
            pdf.cell(200, 10, txt=f"- {crop}", ln=True)
        
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="💾 Save Report to Device", data=pdf_bytes, file_name="ASES_Farmer_Report.pdf", mime="application/pdf")

elif tab == "📜 Govt Schemes":
    st.title("Official Government Schemes")
    st.table(pd.DataFrame({"Scheme": ["PM-KISAN", "PMFBY"], "Benefit": ["Cash Support", "Insurance"]}))
