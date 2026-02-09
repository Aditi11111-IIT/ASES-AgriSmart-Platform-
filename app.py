import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
import os

# --- PAGE CONFIGURATION (Member 2) ---
st.set_page_config(page_title="ASES: Agri-Smart Solutions", layout="wide", page_icon="🌾")

# --- CUSTOM CSS FOR UI (Member 2) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; }
    .status-box { padding: 20px; border-radius: 10px; background-color: #ffffff; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING & AI ENGINE (Member 1) ---
@st.cache_data
def load_data():
    # Creating the master dataset as per PDF requirements
    data = {
        'Crop Name': ['Wheat', 'Rice', 'Cotton', 'Maize', 'Groundnut', 'Soybean', 'Mustard', 'Sugarcane'],
        'Soil Type': ['Alluvial', 'Alluvial', 'Black Soil', 'Red Soil', 'Sandy', 'Black Soil', 'Alluvial', 'Loamy'],
        'Water Requirement': [500, 1200, 800, 600, 400, 700, 450, 1500],
        'Sowing Month': [11, 6, 6, 6, 5, 6, 10, 2],
        'Cost per Acre': [15000, 25000, 20000, 12000, 18000, 16000, 14000, 30000]
    }
    df = pd.DataFrame(data)
    # Cleaning data (Member 1 Task)
    df['Soil Type'] = df['Soil Type'].str.strip().str.title()
    return df

df = load_data()
le = LabelEncoder()
df['Soil_Idx'] = le.fit_transform(df['Soil Type'])

# --- APP NAVIGATION ---
st.sidebar.title("🍀 ASES Navigation")
page = st.sidebar.radio("Go to", ["Home & AI Recommendation", "Pest & Maintenance", "Kisan Sampark (Market)", "Govt. Schemes"])

# --- PAGE 1: AI RECOMMENDATION (Member 1 & 2) ---
if page == "Home & AI Recommendation":
    st.title("🌾 AgriAI Recommendation Engine")
    st.write("Enter your farm details to find the most suitable crops using KNN Logic.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        u_soil = st.selectbox("Select Soil Type", df['Soil Type'].unique())
    with col2:
        u_month = st.slider("Sowing Month (1=Jan, 12=Dec)", 1, 12, 6)
    with col3:
        u_budget = st.number_input("Budget per Acre (₹)", value=20000)

    if st.button("Run AI Analysis"):
        # KNN Implementation (Member 1 Task)
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=3, metric='euclidean')
        knn.fit(X)
        
        u_soil_idx = le.transform([u_soil])[0]
        distances, indices = knn.kneighbors([[u_soil_idx, u_month, u_budget]])
        
        st.subheader("Top 3 Recommendations")
        recs = df.iloc[indices[0]].copy()
        
        # Suitability Score Logic (Member 1 Task)
        def calculate_suitability(row):
            score = 100
            if row['Soil Type'] != u_soil: score -= 30
            month_diff = abs(row['Sowing Month'] - u_month)
            score -= (month_diff * 10)
            return max(score, 5)

        recs['Match %'] = recs.apply(calculate_suitability, axis=1)
        
        for i, row in recs.iterrows():
            st.success(f"**{row['Crop Name']}** - {row['Match %']}% Suitability Match")
            st.info(f"Water Req: {row['Water Requirement']}mm | Est. Cost: ₹{row['Cost per Acre']}")

# --- PAGE 2: PESTS & MAINTENANCE (Member 3) ---
elif page == "Pest & Maintenance":
    st.title("🛡️ Resilience & Protection")
    crop_choice = st.selectbox("Select Crop for Protection Guide", df['Crop Name'].unique())
    
    # Mock Pest Database (Member 3 Task)
    pest_db = {
        "Wheat": {"Pest": "Brown Rust", "Remedy": "Propiconazole 25% EC", "Organic": "Neem Oil Spray"},
        "Rice": {"Pest": "Stem Borer", "Remedy": "Chlorantraniliprole 0.4G", "Organic": "Pheromone Traps"},
        "Cotton": {"Pest": "Pink Bollworm", "Remedy": "Indoxacarb 14.5% SC", "Organic": "Light Traps"}
    }
    
    if crop_choice in pest_db:
        st.warning(f"Common Pest: {pest_db[crop_choice]['Pest']}")
        st.write(f"**Chemical Remedy:** {pest_db[crop_choice]['Remedy']}")
        st.write(f"**Organic Remedy:** {pest_db[crop_choice]['Organic']}")
    else:
        st.write("No major pests reported for this crop in the current database.")

    st.markdown("---")
    st.subheader("⚙️ Maintenance Guides")
    st.info("Crisis Mode: Use 20% less water for the first 3 weeks if irrigation is limited.")

# --- PAGE 3: KISAN SAMPARK (Member 4) ---
elif page == "Kisan Sampark (Market)":
    st.title("📞 Kisan Sampark Marketplace")
    st.write("Rent machinery directly from owners.")
    
    # Machinery Database (Member 4 Task)
    machinery = pd.DataFrame({
        'Equipment': ['Tractor', 'Harvester', 'Borewell Drill'],
        'Owner': ['Ram Singh', 'Amit Kumar', 'S. Patil'],
        'Contact': ['9999999999', '8888888888', '7777777777']
    })
    
    for i, row in machinery.iterrows():
        with st.container():
            st.write(f"### {row['Equipment']}")
            st.write(f"Owner: {row['Owner']}")
            # HTML Injection for Click-to-Call (Member 4 Task)
            st.markdown(f'<a href="tel:{row["Contact"]}"><button style="background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px;">📞 Call Owner ({row["Contact"]})</button></a>', unsafe_allow_html=True)
            st.write("---")

# --- PAGE 4: GOVT SCHEMES (Member 4) ---
else:
    st.title("📜 Government Schemes")
    farmer_type = st.radio("Select Farmer Category", ["Small/Marginal", "Large Scale"])
    
    if farmer_type == "Small/Marginal":
        st.success("1. PM-Kisan Samman Nidhi (₹6000/year)")
        st.success("2. PM Fasal Bima Yojana (Low Premium)")
    else:
        st.success("1. NABARD Subsidy for Cold Storage")
        st.success("2. Agri-Infrastructure Fund")
