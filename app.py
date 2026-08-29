import streamlit as st
import random
import pandas as pd
import urllib.request
import time
import streamlit as st
import datetime
# ... (आपके बाकी imports जैसे supabase, random आदि) ...

# 1. पेज का नाम और आइकन (यह सबसे ऊपर होना चाहिए)
st.set_page_config(page_title="पंजीकरण | हिंदी पखवाड़ा 2026", page_icon="🇮🇳", layout="centered")

# 2. कस्टम CSS (प्रोफेशनल लुक के लिए)
st.markdown("""
    <style>
    /* स्ट्रीमलिट का डिफ़ॉल्ट मेनू और वॉटरमार्क छिपाएं */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* पेज का हल्का बैकग्राउंड रंग */
    .stApp {
        background-color: #F4F6F9;
    }
    
    /* मेन फॉर्म का बॉक्स (Card style) */
    .block-container {
        background-color: white;
        padding: 3rem 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-top: 30px;
    }

    /* सबमिट बटन को शानदार बनाना */
    .stButton>button {
        width: 100%;
        background-color: #004B87; /* नेवी ब्लू कलर */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #003366;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# ... (यहाँ आपका Supabase Database कनेक्शन वाला पुराना कोड रहेगा) ...
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="पंजीकरण / Registration", layout="centered")

# --- DATABASE CONNECTION ---
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"डेटाबेस कनेक्शन विफल / Database connection failed: {e}")
    st.stop()

# --- COMPETITIONS & DATES ---
COMPETITIONS = {
    "हिंदी मुहावरें, लोकोक्तियां एवं प्रशासनिक शब्दावली": "2026-09-17",
    "शब्दकोश प्रतियोगिता": "2026-09-18",
    "हिंदी टंकण प्रतियोगिता": "2026-08-27",
    "निबंध लेखन": "2026-09-23",
    "वाद-विवाद प्रतियोगिता": "2026-09-24",
    "तस्वीर क्या बोलती है": "2026-09-25",
    "टिप्पणी एवं पत्र मसौदा लेखन": "2026-09-28"
}

# --- ADMIN DASHBOARD (SIDEBAR) ---
with st.sidebar:
    st.header("व्यवस्थापक डैशबोर्ड / Admin Dashboard")
    admin_pass = st.text_input("व्यवस्थापक पासवर्ड दर्ज करें / Enter Admin Password", type="password")
    
    if admin_pass:
        if admin_pass == st.secrets["ADMIN_PASSWORD"]:
            st.success("पहुंच स्वीकृत / Access Granted")
            if st.button("डेटा रीफ्रेश करें / Refresh Data"):
                st.rerun()
                
            # Fetch all registrations
            res = supabase.table("registrations").select("*").execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df = df[['unique_code', 'name', 'designation', 'place', 'railway_zone', 'competition', 'date', 'created_at']]
                
                # Show total participants
                st.write(f"**कुल पंजीकरण / Total Registrations:** {len(df)}")
                st.dataframe(df)
                
                # Download button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="CSV के रूप में डेटा डाउनलोड करें / Download Data as CSV",
                    data=csv,
                    file_name='registrations.csv',
                    mime='text/csv',
                )
            else:
                st.info("अभी तक कोई पंजीकरण नहीं / No registrations yet.")
        else:
            st.error("गलत पासवर्ड / Incorrect Password")

# --- MAIN REGISTRATION UI ---
st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>हिंदी पखवाड़ा 2026 की प्रतियोगिताओं में आपका स्वागत है।</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Welcome to the competitions of Hindi Pakhwada 2026.</h4>", unsafe_allow_html=True)
st.divider()

# --- INTERNET SPEED TEST ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("हिंदी पखवाड़ा प्रतियोगिता पंजीकरण / Hindi Pakhwada Pratiyogita Registration")
with col2:
    if st.button("🌐 इंटरनेट जांचें / Check Internet"):
        with st.spinner("जांच हो रही है..."):
            try:
                start_time = time.time()
                # Attempt to connect to a reliable global server
                urllib.request.urlopen('https://www.google.com', timeout=3)
                end_time = time.time()
                latency = round((end_time - start_time) * 1000)
                
                # If it takes less than 800ms, it is a good connection
                if latency < 800:
                    st.success(f"आपका इंटरनेट काम कर रहा है।\n\n(Speed/Ping: {latency}ms - Good)")
                else:
                    st.warning(f"आपका इंटरनेट काम कर रहा है, लेकिन गति धीमी है।\n\n(Speed/Ping: {latency}ms - Slow)")
            except:
                st.error("इंटरनेट काम नही कर रहा है।")

st.markdown("अपना विशिष्ट 4-अंकीय नामांकन कोड प्राप्त करने के लिए कृपया नीचे दिया गया फॉर्म भरें। / Please fill out the form below to generate your unique 4-digit enrollment code.")
st.divider()

# 1. Slide-down Menu for Competition
competition_selection = st.selectbox(
    "प्रतियोगिता चुनें / Select Competition *",
    options=list(COMPETITIONS.keys())
)

# 2. Automatically Display Corresponding Date
event_date = COMPETITIONS[competition_selection]
display_date = f"{event_date[-2:]}/{event_date[5:7]}/{event_date[:4]}"
st.info(f"📅 **निर्धारित तिथि / Scheduled Date:** {display_date}")
st.divider()

# 3. User Details
name = st.text_input("पूरा नाम / Full Name *")
designation = st.text_input("पदनाम / Designation *")
place = st.text_input("तैनाती का स्थान / Place of Posting *")

railway_zone = st.radio(
    "रेलवे जोन / Railway Zone *",
    options=["मध्य रेलवे (CR) / Central Railway (CR)", "पश्चिम रेलवे (WR) / Western Railway (WR)"]
)

# 4. Submit Button
if st.button("पंजीकरण करें और कोड बनाएं / Register & Generate Code", type="primary"):
    if not name or not designation or not place:
        st.error("कृपया सभी अनिवार्य फ़ील्ड भरें। / Please fill in all mandatory fields.")
    else:
        with st.spinner("कोड जनरेट हो रहा है... / Generating Code..."):
            code_is_unique = False
            while not code_is_unique:
                new_code = str(random.randint(1000, 9999))
                check = supabase.table("registrations").select("id").eq("unique_code", new_code).execute()
                if len(check.data) == 0:
                    code_is_unique = True

            try:
                data = {
                    "name": name,
                    "designation": designation,
                    "place": place,
                    "railway_zone": railway_zone,
                    "competition": competition_selection,
                    "date": event_date,
                    "unique_code": new_code
                }
                supabase.table("registrations").insert(data).execute()
                
                st.success("पंजीकरण सफल! / Registration Successful!")
                st.info(f"### आपका विशिष्ट कोड / Your Unique Code: **{new_code}**")
                st.warning("कृपया यह कोड लिख लें। अपनी परीक्षा शुरू करने के लिए आपको इसकी आवश्यकता होगी। / Please write this code down. You will need it to start your exam.")
                
            except Exception as e:
                st.error(f"पंजीकरण विफल / Failed to register: {e}")
