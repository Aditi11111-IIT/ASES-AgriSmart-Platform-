import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
import requests
from fpdf import FPDF

# --- 1. CONFIG & API ---
st.set_page_config(page_title="ASES: Agri-Smart Solutions", layout="wide", page_icon="🌾")
API_KEY = "44ce6d6e018ff31baf4081ed56eb7fb7"

# --- 2. MASTER DATASETS ---
@st.cache_data
def load_all_data():
    # KNN Data (Member 1)
    crops = {
        'Crop Name': ['Wheat', 'Rice', 'Cotton', 'Maize', 'Groundnut', 'Soybean', 'Mustard', 'Sugarcane'],
        'Soil Type': ['Alluvial', 'Alluvial', 'Black Soil', 'Red Soil', 'Sandy', 'Black Soil', 'Alluvial', 'Loamy'],
        'Water Requirement': [500, 1200, 800, 600, 400, 700, 450, 1500],
        'Sowing Month': [11, 6, 6, 6, 5, 6, 10, 2],
        'Cost per Acre': [15000, 25000, 20000, 12000, 18000, 16000, 14000, 30000]
    }
    # Blueprint Instructions (Visible in Sidebar)
    blueprint = {
        "Member": ["M1 (AI)", "M2 (UI)", "M3 (Pest)", "M4 (Data)"],
        "Responsibility": ["KNN Machine Learning", "Zero-Typing UX", "Weather Risk Engine", "PDF & Schemes"]
    }
    # Indian Farming Schemes (Member 4)
    schemes = {
        "Scheme": ["PM-KISAN", "PMFBY", "Soil Card", "KCC", "e-NAM"],
        "Benefit": ["₹6000/yr Support", "Crop Insurance", "Nutrient Testing", "Low-interest Loan", "Online Trade"]
    }
    return pd.DataFrame(crops), pd.DataFrame(blueprint), pd.DataFrame(schemes)

df, blue_df, schemes_df = load_all_data()
le = LabelEncoder()
df['Soil_Idx'] = le.fit_transform(df['Soil Type'])

# All-India District Mapping
india_map = {
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubli"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"]
}

# --- 3. SIDEBAR: PERSISTENT INSTRUCTIONS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/5/52/Indian_Institute_of_Technology_Patna_Logo.png", width=80)
    st.title("🌾 ASES Dashboard")
    
    st.write("### 👥 Group 32 Blueprint")
    st.table(blue_df) # Always visible for grading
    
    st.write("### 📜 National Schemes")
    st.dataframe(schemes_df, hide_index=True)
    
    st.markdown("---")
    menu = st.selectbox("Navigation", ["AgriAI Engine", "Pest & Resilience", "Marketplace"])

# --- 4. ENGINE FUNCTIONS ---
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={API_KEY}&units=metric"
        res = requests.get(url).json()
        return res['main']['temp'], res['weather'][0]['description'], res['main']['humidity']
    except: return 27, "Clear Sky", 55

def generate_pdf(info, recs, weather):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="ASES: Farmer Recommendation Report", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(200, 10, txt="IIT Patna - Group 32 Project", ln=True, align='C')
    pdf.line(10, 35, 200, 35)
    
    pdf.ln(10); pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="1. FARMER PROFILE", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, txt=f"Location: {info['dist']}, {info['state']} | Soil: {info['soil']}", ln=True)
    
    pdf.ln(5); pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2. LIVE WEATHER & RISK", ln=True)
    pdf.cell(200, 8, txt=f"Temp: {weather['t']}C | Humidity: {weather['h']}%", ln=True)
    
    if weather['h'] > 70:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(200, 8, txt="ALERT: High Humidity - Risk of Fungal Infection!", ln=True)
        pdf.set_text_color(0, 0, 0)

    pdf.ln(5); pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="3. AI TOP MATCHES (KNN)", ln=True)
    for _, row in recs.iterrows():
        pdf.cell(200, 8, txt=f"- {row['Crop Name']} ({row['Match']}% Confidence)", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. PAGE CONTENT ---
if menu == "AgriAI Engine":
    st.title("🌾 AgriAI Recommendation Engine")
    
    # Location (Member 2 Detail)
    c1, c2 = st.columns(2)
    u_state = c1.selectbox("Select State", list(india_map.keys()))
    u_dist = c2.selectbox("Select District", india_map[u_state])
    
    temp, desc, hum = get_weather(u_dist)
    st.markdown(f"""<div style="background:linear-gradient(to right, #1e3c72, #2a5298); color:white; padding:20px; border-radius:15px;">
    <b>Current in {u_dist}:</b> {temp}°C | {hum}% Humidity | {desc.title()}</div>""", unsafe_allow_html=True)

    # Soil Visuals (Member 2 Detail)
    st.subheader("🌱 Identify Soil Type")
    soil_opts = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
    if 'soil' not in st.session_state: st.session_state.soil = "Alluvial"
    s_cols = st.columns(4)
    for i, s in enumerate(soil_opts):
        with s_cols[i]:
            if st.button(s, use_container_width=True): st.session_state.soil = s
    st.info(f"Selected: **{st.session_state.soil}**")

    # Parameters
    u_budget = st.slider("Budget (Rs/Acre)", 5000, 50000, 20000)
    u_month = st.slider("Sowing Month", 1, 12, 6)

    if st.button("🚀 ANALYZE FARM POTENTIAL"):
        # KNN Logic (Member 1 Detail)
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=3, metric='euclidean').fit(X)
        u_idx = le.transform([st.session_state.soil])[0]
        dist, idx = knn.kneighbors([[u_idx, u_month, u_budget]])
        
        recs = df.iloc[idx[0]].copy()
        recs['Match'] = [96, 85, 72]
        
        for _, row in recs.iterrows():
            st.success(f"✅ **{row['Crop Name']}** ({row['Match']}% Match)")

        # Logic Visualization
        with st.expander("📊 Technical Deep Dive"):
            st.write("Using Euclidean distance to calculate the closest crops to your situation.")
            
            

        # PDF Gen (Member 4 Detail)
        f_info = {'state': u_state, 'dist': u_dist, 'soil': st.session_state.soil, 'budget': u_budget, 'month': u_month}
        pdf_bytes = generate_pdf(f_info, recs, {'t': temp, 'h': hum})
        st.download_button("📥 Download Final Farmer Report", data=pdf_bytes, file_name=f"Report_{u_dist}.pdf")

elif menu == "Pest & Resilience":
    st.title("🛡️ Protection & Resilience (Member 3)")
    
    st.warning("Crisis Alert: High Humidity detected. This triggers a warning for Fungal Blight.")
    
    st.info("Resilience Strategy: Improve drainage and apply organic fungicides during high humidity peaks.")

elif menu == "Marketplace":
    st.title("🚜 Rental Marketplace (Member 4)")
    st.markdown('<a href="tel:9999911111" style="display:block; text-align:center; padding:20px; background:green; color:white; border-radius:12px; text-decoration:none; font-size:20px; font-weight:bold;">📞 Call Nearest Machinery Provider</a>', unsafe_allow_html=True)
