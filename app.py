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

# --- 2. UNIVERSAL CONTRAST CSS ---
st.markdown("""
    <style>
    .main-card { 
        padding: 25px; border-radius: 12px; 
        background-color: #FFFFFF !important; 
        border: 1px solid #2481CC; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        margin-bottom: 20px;
    }
    .main-card h1, .main-card h2, .main-card h3, .main-card h4, .main-card p, .main-card b, .main-card div {
        color: #1c1c1c !important;
    }
    [data-testid="stSidebar"] { background-color: #243139 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .highlight-text { color: #2481CC !important; font-weight: bold; }
    
    /* MEMBER 4: Green Button Styling for Call Links */
    .call-btn {
        background-color: #28a745 !important;
        color: white !important;
        padding: 12px;
        border-radius: 8px;
        text-decoration: none;
        display: block;
        text-align: center;
        font-weight: bold;
        margin-top: 10px;
    }
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
if 'soil' not in st.session_state: st.session_state.soil = "Alluvial"
if 'recs_list' not in st.session_state: st.session_state.recs_list = []

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/5/52/Indian_Institute_of_Technology_Patna_Logo.png", width=120)
    st.title("ASES NAVIGATION")
    tab = st.radio("SELECT SERVICE", ["🌾 Crop Engine", "🛡️ Pest & Fertilizer", "🚜 Rental Hub", "📜 Govt Schemes", "📊 Farmer Report"])
    st.markdown("---")
    india_map = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Tirupati"],
    "Arunachal Pradesh": ["Itanagar", "Tawang", "Ziro", "Pasighat"],
    "Assam": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Tezpur"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba"],
    "Goa": ["Panaji", "Margao", "Vasco da Gama", "Mapusa"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
    "Haryana": ["Gurgaon", "Faridabad", "Panipat", "Ambala", "Hisar"],
    "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala", "Solan"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Belagavi", "Mangaluru"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur"],
    "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Manipur": ["Imphal", "Churachandpur", "Thoubal"],
    "Meghalaya": ["Shillong", "Tura", "Jowai"],
    "Mizoram": ["Aizawl", "Lunglei", "Champhai"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Sambalpur"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner"],
    "Sikkim": ["Gangtok", "Namchi", "Geyzing"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Khammam"],
    "Tripura": ["Agartala", "Udaipur", "Dharmanagar"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Prayagraj"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Roorkee", "Haldwani"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol"],
    "A&N Islands": ["Port Blair"],
    "Chandigarh": ["Chandigarh"],
    "Dadra & Nagar Haveli": ["Silvassa"],
    "Daman & Diu": ["Daman", "Diu"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "West Delhi"],
    "Jammu & Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla"],
    "Ladakh": ["Leh", "Kargil"],
    "Lakshadweep": ["Kavaratti"],
    "Puducherry": ["Puducherry", "Karaikal"]
}
    st_loc = st.selectbox("Your State", list(india_map.keys()))
    dt_loc = st.selectbox("Your District", india_map[st_loc])
    
    if st.button("Update Local Weather"):
        try:
            w_url = f"http://api.openweathermap.org/data/2.5/weather?q={dt_loc},IN&appid={API_KEY}&units=metric"
            res = requests.get(w_url).json()
            st.session_state.temp, st.session_state.hum = res['main']['temp'], res['main']['humidity']
            st.success("Weather Synced!")
        except: st.error("Weather API Error")

# --- 5. TABS LOGIC ---

if tab == "🌾 Crop Engine":
    st.title("AgriAI Smart Recommendations")
    st.info(f"📍 Location: {dt_loc} | Temp: {st.session_state.temp}°C | Humidity: {st.session_state.hum}%")
    soil_opts = ["Alluvial", "Black Soil", "Red Soil", "Sandy"]
    s_cols = st.columns(4)
    for i, s in enumerate(soil_opts):
        with s_cols[i]:
            if st.button(s): st.session_state.soil = s
    
    st.markdown(f"<b>Current Soil Selection:</b> <span class='highlight-text'>{st.session_state.soil}</span>", unsafe_allow_html=True)
    bud = st.slider("Investment Budget (₹/Acre)", 5000, 50000, 15000)
    
    if st.button("🚀 FIND BEST CROPS"):
        X = df[['Soil_Idx', 'Sowing Month', 'Cost per Acre']]
        knn = NearestNeighbors(n_neighbors=2).fit(X)
        u_idx = le.transform([st.session_state.soil])[0]
        dist, idx = knn.kneighbors([[u_idx, 6, bud]])
        recs = df.iloc[idx[0]]
        st.session_state.recs_list = recs['Crop Name'].tolist()
        
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
    target_crop = st.selectbox("Select Crop", pest_df['Crop'].unique())
    data = pest_df[pest_df['Crop'] == target_crop].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="main-card">
        <h3>🛡️ Pest Control</h3>
        <p><b>Common Threat:</b> {data['Common Pest']}</p>
        <p><b>Recommended Pesticide:</b> {data['Pesticide']}</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="main-card">
        <h3>🧪 Nutrition Plan</h3>
        <p><b>Fertilizer Mix:</b> {data['Fertilizer']}</p>
        </div>""", unsafe_allow_html=True)

elif tab == "🚜 Rental Hub":
    # --- MEMBER 4: THE OPERATOR LOGIC ---
    st.title(f"🚜 Rental Machinery Desk: {dt_loc}")
    st.markdown(f'<div class="main-card"><h3>Operator Desk:</h3><p>Finding tractor owners near <b>{dt_loc}, {st_loc}</b>.</p></div>', unsafe_allow_html=True)

    # Local Directory Database
    local_data = {
        "Patna": [
            {"Machine": "Mahindra 575 DI", "Owner": "Suresh Kumar", "Rate": "₹800/hr", "Contact": "9876543210"},
            {"Machine": "Power Tiller", "Owner": "Vijay Dev", "Rate": "₹400/hr", "Contact": "9122334455"}
        ],
        "Ludhiana": [
            {"Machine": "John Deere 5310", "Owner": "Amrit Singh", "Rate": "₹950/hr", "Contact": "9988776655"},
            {"Machine": "Combine Harvester", "Owner": "Gurmukh Gill", "Rate": "₹2500/hr", "Contact": "9812345678"}
        ],
        "Pune": [
            {"Machine": "Sonalika Tiger", "Owner": "Vikram Patil", "Rate": "₹750/hr", "Contact": "9444455555"}
        ]
    }

    results = local_data.get(dt_loc, [])

    if results:
        cols = st.columns(len(results))
        for i, r in enumerate(results):
            with cols[i]:
                st.markdown(f"""<div class="main-card">
                <h4>{r['Machine']}</h4>
                <p><b>Owner:</b> {r['Owner']}</p>
                <p class="highlight-text">Rate: {r['Rate']}</p>
                <hr>
                <a href="tel:{r['Contact']}" class="call-btn">📞 Call Now</a>
                </div>""", unsafe_allow_html=True)
    else:
        st.warning(f"No private owners listed in {dt_loc} yet.")

    st.markdown("---")
    st.subheader("🌐 Global Search (Google Maps Bridge)")
    
    # Corrected Google Maps Search URL
    search_query = f"Tractor+Rental+in+{dt_loc}+{st_loc}"
    google_url = f"https://www.google.com/maps/search/{search_query}"
    
    st.info(f"scanning Google Maps for commercial centers in {dt_loc}.")
    
    # Member 4's Fixed Search Button
    st.link_button(f"🔍 Search Commercial Centers in {dt_loc}", google_url, use_container_width=True)

    with st.expander("🆘 Need Government Help?"):
        st.markdown(f"""
            <a href="tel:18001801551" class="call-btn" style="background-color:#ffc107 !important; color:black !important;">
                📞 Call Govt CHC Helpline (1800-180-1551)
            </a>
        """, unsafe_allow_html=True)

elif tab == "📜 Govt Schemes":
    st.title("Agricultural Schemes")
    st.table(pd.DataFrame({
        "Scheme Name": ["PM-KISAN", "PMFBY", "KCC", "Soil Health Card"],
        "Financial Benefit": ["₹6000/yr Cash Support", "Crop Insurance Cover", "Low Interest Loan", "Lab Analysis Report"]
    }))

elif tab == "📊 Farmer Report":
    st.title("Personalized Farmer Report")
    st.markdown(f"""<div class="main-card">
        <h3>📍 Assessment Summary</h3>
        <p><b>Location:</b> {dt_loc}, {st_loc}</p>
        <p><b>Soil Profile:</b> {st.session_state.soil}</p>
        <p><b>Climate:</b> {st.session_state.temp}°C | {st.session_state.hum}% Humidity</p>
    </div>""", unsafe_allow_html=True)

    if st.button("📥 Generate PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="ASES: Farmer Strategy Report", ln=True, align='C')
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="💾 Download PDF", data=pdf_output, file_name="Farmer_Report.pdf", mime="application/pdf")
