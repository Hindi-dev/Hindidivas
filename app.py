import streamlit as st
from supabase import create_client, Client
import random
import pandas as pd

# --- 1. पेज सेटिंग और प्रोफेशनल CSS ---
st.set_page_config(page_title="पंजीकरण | हिंदी पखवाड़ा 2026", page_icon="🇮🇳", layout="centered")

st.markdown("""
    <style>
    /* स्ट्रीमलिट का डिफ़ॉल्ट मेनू और वॉटरमार्क छिपाएं */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* पेज का हल्का बैकग्राउंड रंग */
    /* (बाकी का CSS वैसा ही रहेगा) */
    
    /* पेज का हल्का बैकग्राउंड रंग */
    .stApp {
        background-color: #F4F6F9;
    }
    
    /* मेन फॉर्म का बॉक्स (Card style) */
    .block-container {
        background-color: white;
        padding: 2rem 3rem;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        margin-top: 30px;
        margin-bottom: 30px;
    }

    /* सबमिट बटन को शानदार बनाना */
    .stButton>button {
        width: 100%;
        background-color: #004B87;
        color: white;
        font-weight: bold;
        font-size: 16px;
        border-radius: 8px;
        border: none;
        padding: 10px 0px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #003366;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        color: white;
    }
    
    /* इनपुट बॉक्स का डिज़ाइन */
    div[data-baseweb="input"] > div {
        background-color: #f9fbfd;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. डेटाबेस कनेक्शन ---
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error("डेटाबेस से जुड़ने में त्रुटि। कृपया अपने Streamlit Secrets की जांच करें।")
    st.stop()

# --- 3. प्रोफेशनल हेडर (Banner) ---
st.markdown("""
    <div style='text-align: center; padding: 10px; margin-bottom: 20px;'>
        <h1 style='color: #FF9933; margin-bottom: 5px; font-size: 34px;'>हिंदी पखवाड़ा 2026</h1>
        <h3 style='color: #138808; margin-top: 0px; font-size: 22px;'>प्रतियोगिता पंजीकरण पोर्टल</h3>
        <hr style='border: 1px solid #e0e0e0; margin-top: 15px; margin-bottom: 15px;'>
        <p style='color: #555; font-size: 15px; margin-bottom: 0;'>कृपया नीचे दी गई जानकारी भरें और परीक्षा के लिए अपना <strong>विशिष्ट 4-अंकीय कोड</strong> प्राप्त करें।</p>
    </div>
""", unsafe_allow_html=True)

import datetime # (यदि ऊपर इम्पोर्ट नहीं है, तो इसे सबसे ऊपर रखें)

# --- 4. प्रतियोगिताओं की तारीखों का डेटा (Mapping) ---
COMPETITION_DATES = {
    "हिंदी मुहावरें, लोकोक्तियां एवं प्रशासनिक शब्दावली": "17 सितम्बर 2026",
    "हिंदी शब्दकोश से शब्द खोजना": "18 सितम्बर 2026",
    "हिंदी टंकण प्रतियोगिता": "21 सितम्बर 2026",
    "हिंदी निबंध प्रतियोगिता": "23 सितम्बर 2026",
    "हिंदी वाद-विवाद प्रतियोगिता": "24 सितम्बर 2026",
    "तस्वीर देखकर कहानी लिखना": "25 सितम्बर 2026",
    "मसौदा लेखन प्रतियोगिता (Drafting)": "28 सितम्बर 2026"
}

st.markdown("#### 👤 अपनी व्यक्तिगत जानकारी दर्ज करें")

col1, col2 = st.columns(2)

# बायीं ओर के 3 बॉक्स
with col1:
    name = st.text_input("पूरा नाम (Full Name) *")
    designation = st.text_input("पदनाम (Designation) *")
    place = st.text_input("स्थान/कार्यालय (Place) *")

# दायीं ओर के 3 बॉक्स
with col2:
    department = st.text_input("अनुभाग/विभाग (Department) *")
    railway_zone = st.selectbox("रेलवे ज़ोन/मंडल (Railway Zone) *", ["मध्य रेल (CR)", "पश्चिम रेल (WR)", "उत्तर रेल (NR)", "अन्य"])
    phone = st.text_input("मोबाइल नंबर (Mobile) *", max_chars=10)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### 🎯 प्रतियोगिता चुनें")

selected_competitions = st.multiselect(
    "आप किन-किन प्रतियोगिताओं में भाग लेना चाहते हैं? (एक साथ कई चुन सकते हैं) *",
    options=list(COMPETITION_DATES.keys()) # लिस्ट अपने आप ऊपर से आ जाएगी
)

# --- नया फीचर: ऑटोमैटिक तारीख दिखाना ---
if selected_competitions:
    st.markdown("📅 **आपकी चयनित प्रतियोगिताओं की तिथियां (Dates):**")
    for comp in selected_competitions:
        st.info(f"🔹 {comp} ➔ **{COMPETITION_DATES[comp]}**")

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. पंजीकरण और कोड जनरेशन लॉजिक ---
if st.button("पंजीकरण करें (Register Now)"):
    if not name or not designation or not department or not phone or not place or not railway_zone or len(selected_competitions) == 0:
        st.error("⚠️ कृपया सभी आवश्यक फ़ील्ड (*) भरें और कम से कम एक प्रतियोगिता चुनें।")
    elif len(phone) < 10:
        st.error("⚠️ कृपया सही 10-अंकों का मोबाइल नंबर दर्ज करें।")
    else:
        with st.spinner("पंजीकरण हो रहा है... कृपया प्रतीक्षा करें"):
            try:
                # रजिस्ट्रेशन की आज की तारीख (डेटाबेस के 'date' कॉलम का एरर रोकने के लिए)
                today_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                
                existing_user = supabase.table("registrations").select("unique_code").eq("phone", phone).execute()
                
                # प्रतियोगिता के साथ उसकी तारीख भी डेटाबेस में सेव करने के लिए:
                comps_with_dates = [f"{c} ({COMPETITION_DATES[c]})" for c in selected_competitions]
                comps_string = " | ".join(comps_with_dates)

                if len(existing_user.data) > 0:
                    # पुराना यूजर: डेटा अपडेट करें
                    unique_code = existing_user.data[0]["unique_code"]
                    supabase.table("registrations").update({
                        "competition": comps_string,
                        "name": name,
                        "designation": designation,
                        "department": department,
                        "place": place,
                        "railway_zone": railway_zone,
                        "date": today_date_str             
                    }).eq("phone", phone).execute()
                    
                    st.info("📌 आपका मोबाइल नंबर पहले से पंजीकृत है। आपकी जानकारी अपडेट कर दी गई है।")
                    st.success(f"🔑 आपका 4-अंकीय कोड है: **{unique_code}**")
                    st.warning("परीक्षा के दिन लॉग इन करने के लिए कृपया इसी कोड का उपयोग करें।")
                
                else:
                    # नया यूजर: डेटा इन्सर्ट करें
                    unique_code = str(random.randint(1000, 9999))
                    supabase.table("registrations").insert({
                        "unique_code": unique_code,
                        "name": name,
                        "designation": designation,
                        "department": department,
                        "phone": phone,
                        "competition": comps_string,
                        "place": place,
                        "railway_zone": railway_zone,
                        "date": today_date_str            
                    }).execute()
                    
                    st.success(f"🎉 पंजीकरण सफल! आपका 4-अंकीय कोड है: **{unique_code}**")
                    st.warning("परीक्षा के दिन लॉग इन करने के लिए कृपया इस कोड को डायरी या फोन में सुरक्षित लिख लें।")
                    st.balloons()
                    
            except Exception as e:
                st.error(f"पंजीकरण में त्रुटि: {e}")
