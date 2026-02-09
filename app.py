import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
import os

# --- 1. PAGE CONFIG & STYLING (Member 2) ---
st.set_page_config(page_title="ASES: Agri-Smart Solutions", layout="wide", page_icon="🌾")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #2e7d32; color: white; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #1b5e20; border: 2px solid #a5d6a7; }
    .card { padding: 20px; border-radius: 10px; background-color: white; border-left: 5px solid #2e7d32; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA SCIENCE ENGINE (Member 1) ---
@st.cache_data
def get_master_data():
    # Columns: Crop Name, Soil Type, Water (mm), Season, Sowing Month, Cost/Acre
    data = {
        'Crop Name': ['Wheat', 'Rice', 'Cotton', 'Maize', 'Groundnut', 'Soybean', 'Mustard', 'Sugarcane'],
        'Soil Type': ['Alluvial', 'Alluvial', 'Black Soil', 'Red Soil', 'Sandy', 'Black Soil', 'Alluvial', 'Loamy'],
        'Water Requirement': [500, 1200, 800, 600, 400, 700, 450, 1500],
        'Ideal Season': ['Rabi', 'Kharif', 'Kharif', 'Kharif', 'Kharif', 'Kharif', 'Rabi', 'Annual'],
        'Sowing Month': [11, 6, 6, 6, 5, 6, 10, 2],
        'Cost per Acre': [15000, 25000, 20000, 12000, 18000, 16000, 14000, 30000]
    }
    df = pd.DataFrame(data)
    # Cleaning (Member 1 Task)
    df['Soil Type'] = df['Soil Type'].str.strip().str.title()
    return df

df = get_master_data()
le_soil = LabelEncoder()
df['Soil_Idx'] = le_soil.fit_transform(df['Soil Type'])

# --- 3. NAVIGATION ---
st.sidebar.title("🍀 ASES Platform")
st.sidebar.markdown("Group 32 | IIT Patna")
page = st.sidebar.radio("Navigate to:", 
    ["AgriAI Engine", "Pest & Resilience", "Kisan Sampark (Market)", "Knowledge Hub & Schemes"])

# --- MODULE A & B: AI & UI (Member 1 & 2) ---
if page == "AgriAI Engine":
    st.title("🌾 AgriAI Recommendation Engine")
    st.info("Member 2: Zero-Typing Interface active. Select your conditions visually.")

    # Visual Soil Selection
    st.subheader("1. Select Soil Type")
    soil_opts = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
    # Change these paths to your local './assets/filename.jpg' once uploaded
    soil_imgs = [
        "https://raw.githubusercontent.com/google-gemini/ASES-Project/main/assets/alluvial.jpg",
        "https://raw.githubusercontent.com/google-gemini/ASES-Project/main/assets/black.jpg",
        "https://raw.githubusercontent.com/google-gemini/ASES-Project/main/assets/red.jpg",
        "https://raw.githubusercontent.com/google-gemini/ASES-Project/main/assets/sandy.jpg"
    ]

    if 'selected_soil' not in st.session_state: st.session_state.selected_soil = "Alluvial"
    
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.image(soil_imgs[i], caption=soil_opts[i], use_container_width=True)
            if st.button(f"Select {soil_opts[i]}", key=f"s_{i}"):
                st.session_state.selected_soil = soil_opts[i]

    st.write(f"**Selected Foundation:** {st.session_state.selected_soil}")

    st.markdown("---")
    st.subheader("2. Environmental Inputs")
    c1, c2 = st.columns(2)
    with c1:
        u_month = st.select_slider("Select Sowing Month", options=list(range(1, 13)), value=6)
    with c2:
        u_budget = st.number_input("Max Budget (₹/Acre)", min_value=5000, value=20000)

    if st.button("🚀 GENERATE RECOMMENDATIONS (KNN Logic)"):
        # KNN Implementation (Member 1)
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=3, metric='euclidean').fit(X)
        
        try:
            u_soil_idx = le_soil.transform([st.session_state.selected_soil])[0]
        except:
            u_soil_idx = 0
            
        distances, indices = knn.kneighbors([[u_soil_idx, u_month, u_budget]])
        recs = df.iloc[indices[0]].copy()

        # Suitability Score Logic (Member 1 Detail)
        def get_score(row):
            score = 100
            if row['Soil Type'] != st.session_state.selected_soil: score -= 30
            m_diff = abs(row['Sowing Month'] - u_month)
            score -= (m_diff * 10) # 10% penalty per month off
            return max(score, 5)

        recs['Match'] = recs.apply(get_score, axis=1)
        
        st.subheader("AI Analysis Results:")
        for _, row in recs.iterrows():
            st.markdown(f"""
            <div class="card">
                <h3>{row['Crop Name']}: {row['Match']}% Match</h3>
                <p><b>Water:</b> {row['Water Requirement']}mm | <b>Season:</b> {row['Ideal Season']}</p>
                <p><b>Estimated Cost:</b> ₹{row['Cost per Acre']}</p>
            </div><br>
            """, unsafe_allow_html=True)

# --- MODULE C & D: RESILIENCE (Member 3) ---
elif page == "Pest & Resilience":
    st.title("🛡️ Resilience & Protection")
    st.write("Visual Pest Diagnosis Library (Member 3)")
    
    crop = st.selectbox("Select Crop", df['Crop Name'].unique())
    
    # Member 3: Dictionary Logic for Pests
    pest_data = {
        "Wheat": {"Pest": "Brown Rust", "Chem": "Propiconazole 25% EC", "Org": "Neem Oil"},
        "Rice": {"Pest": "Stem Borer", "Chem": "Chlorantraniliprole", "Org": "Trichogramma Cards"},
        "Cotton": {"Pest": "Pink Bollworm", "Chem": "Indoxacarb", "Org": "Pheromone Traps"}
    }
    
    if crop in pest_data:
        st.error(f"Alert: {pest_data[crop]['Pest']} detected in this category.")
        st.write(f"**Chemical Remedy:** {pest_data[crop]['Chem']}")
        st.write(f"**Organic Remedy:** {pest_data[crop]['Org']}")
    
    st.markdown("---")
    st.subheader("⚙️ Maintenance Guides & Crisis Mode")
    with st.expander("🚨 CRISIS MODE: Water Shortage"):
        st.warning("If irrigation fails: Reduce fertilizer by 30% and apply mulch immediately.")
    st.info("Tractor Maintenance: Check air filters every 50 hours of use.")

# --- MODULE E & F: CONNECTIVITY (Member 4) ---
elif page == "Kisan Sampark (Market)":
    st.title("📞 Kisan Sampark Marketplace")
    st.write("Hybrid Connectivity: Rent Machinery (Member 4)")
    
    # machinery.csv Mock Data
    machinery = [
        {"Tool": "John Deere Tractor", "Owner": "Rajesh Kumar", "Phone": "9999911111"},
        {"Tool": "Power Tiller", "Owner": "Suresh Pal", "Phone": "8888822222"},
        {"Tool": "Borewell Pump", "Owner": "Amit Singh", "Phone": "7777733333"}
    ]
    
    for item in machinery:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.write(f"**{item['Tool']}** (Owner: {item['Owner']})")
        with c2:
            # Member 4: HTML Injection for One-Tap Call
            call_btn = f'<a href="tel:{item["Phone"]}"><button style="background-color:#007bff; color:white; border:none; padding:10px; border-radius:5px;">📞 Call Now</button></a>'
            st.markdown(call_btn, unsafe_allow_html=True)
        st.write("---")

else:
    st.title("📜 Knowledge Hub & Govt. Schemes")
    
    # Member 4: Filter System
    f_type = st.selectbox("I am a:", ["Small Farmer", "Large Scale Farmer", "New Startup"])
    
    if f_type == "Small Farmer":
        st.success("✅ PM-Kisan Samman Nidhi: ₹6,000 yearly income support.")
        st.success("✅ PM Fasal Bima Yojana: Crop insurance at 2% premium.")
    else:
        st.success("✅ Agri-Infrastructure Fund: Interest subvention on cold storage.")
    
    st.markdown("---")
    st.subheader("📚 Downloadable Seed Charts")
    st.download_button("Download Fertilizer Dosage PDF", data="Mock PDF Content", file_name="fert_chart.pdf")
