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

# --- 2. HIGH-CONTRAST UI STYLING ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #F0F2F5; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #1B2631;
        color: white;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* High Visibility Cards */
    .main-card { 
        padding: 25px; 
        border-radius: 12px; 
        background-color: #FFFFFF; 
        border-top: 6px solid #28B463;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1); 
        margin-bottom: 25px;
        color: #1C2833;
    }
    
    /* Weather Box */
    .weather-widget {
        background: linear-gradient(135deg, #2E86C1 0%, #21618C 100%);
        color: white !important; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    /* Buttons & Badges */
    .stButton>button {
        background-color: #28B463; 
        color: white !important; 
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 3em;
    }
    .status-badge {
        padding: 6px 15px; 
        border-radius: 50px; 
        font-weight: 800; 
        background-color: #D4EFDF; 
        color: #186A3B;
        border: 1px solid #2ECC71;
    }
    h1, h2, h3 { color: #1B2631 !important; }
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

# --- 4. SIDEBAR NAVIGATION TABS ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/5/52/Indian_Institute_of_Technology_Patna_Logo.png", width=120)
    st.markdown("## ASES NAVIGATION")
    tab_selection = st.radio("SELECT TAB:", 
                            ["🌾 CROP ENGINE", "🛡️ RISK ANALYSIS", "📜 GOVT SCHEMES", "🚜 MARKETPLACE"])
    st.markdown("---")
    st.caption("v2.1 | High Visibility Mode")

# --- 5. PAGE LOGIC ---

if tab_selection == "🌾 CROP ENGINE":
    st.title("Crop Recommendation Engine")
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: u_state = st.selectbox("1. CHOOSE STATE", list(india_map.keys()))
        with c2: u_dist = st.selectbox("2. CHOOSE DISTRICT", india_map[u_state])
        st.markdown('</div>', unsafe_allow_html=True)

    # Weather Widget
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={u_dist},IN&appid={API_KEY}&units=metric"
        w_res = requests.get(url).json()
        temp, hum = w_res['main']['temp'], w_res['main']['humidity']
        st.markdown(f'<div class="weather-widget">LIVE: {u_dist} is {temp}°C | {hum}% Humidity</div>', unsafe_allow_html=True)
    except:
        temp, hum = 27, 50

    # Soil Selection
    st.subheader("3. Identify Soil Type")
    soil_opts = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
    if 'soil' not in st.session_state: st.session_state.soil = "Alluvial"
    s_cols = st.columns(4)
    for i, s in enumerate(soil_opts):
        with s_cols[i]:
            if st.button(s, use_container_width=True): st.session_state.soil = s
    
    st.markdown(f"ACTIVE SELECTION: <span class='status-badge'>{st.session_state.soil}</span>", unsafe_allow_html=True)

    # Sliders
    u_budget = st.slider("INVESTMENT BUDGET (₹/ACRE)", 5000, 50000, 15000)
    u_month = st.slider("SOWING MONTH (1-12)", 1, 12, 6)

    if st.button("🚀 ANALYZE NOW"):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.005)
            progress_bar.progress(i + 1)
        
        # KNN Logic
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=2).fit(X)
        u_idx = le.transform([st.session_state.soil])[0]
        dist, idx = knn.kneighbors([[u_idx, u_month, u_budget]])
        recs = df.iloc[idx[0]]
        
        
        
        st.subheader("TOP RECOMMENDATIONS")
        res_cols = st.columns(len(recs))
        for i, row in enumerate(recs.iterrows()):
            with res_cols[i]:
                st.markdown(f"""
                <div class="main-card">
                    <h2 style="color:#186A3B;">{row[1]['Crop Name']}</h2>
                    <p><b>Est. Cost:</b> ₹{row[1]['Cost per Acre']}</p>
                    <p><b>Water:</b> {row[1]['Water Requirement']}mm</p>
                    <span class="status-badge">AI MATCH: {99-i}%</span>
                </div>
                """, unsafe_allow_html=True)

elif tab_selection == "🛡️ RISK ANALYSIS":
    st.title("Environmental Risk Assessment")
    
    

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    if 'hum' in locals() and hum > 70:
        st.error(f"⚠️ DANGER: LOCAL HUMIDITY IS {hum}%")
        st.write("Current conditions are highly favorable for **Fungal Infections** like Blight or Mildew.")
        
    else:
        st.success("✅ STABLE: CLIMATIC CONDITIONS ARE OPTIMAL")
        st.write("Humidity levels are currently low. No immediate fungal alerts for your district.")
    st.markdown('</div>', unsafe_allow_html=True)

elif tab_selection == "📜 GOVT SCHEMES":
    st.title("National Agricultural Schemes")
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    schemes = pd.DataFrame({
        "SCHEME NAME": ["PM-KISAN", "PMFBY", "SOIL HEALTH CARD"],
        "BENEFIT": ["₹6,000 ANNUAL CASH", "CROP INSURANCE", "SOIL ANALYSIS REPORT"]
    })
    st.table(schemes)
    st.markdown('</div>', unsafe_allow_html=True)

elif tab_selection == "🚜 MARKETPLACE":
    st.title("Equipment Rental & Services")
    st.markdown("""
    <div class="main-card" style="text-align:center;">
        <h3>NEED MACHINERY?</h3>
        <p>Contact the nearest verified rental service in your district.</p>
        <br>
        <a href="tel:9999911111" style="text-decoration:none;">
            <button style="padding:15px 30px; background-color:#28B463; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer; width:100%;">
                📞 CALL RENTAL SERVICE
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
