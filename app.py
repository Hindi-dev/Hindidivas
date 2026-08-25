import streamlit as st
import random
import pandas as pd
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Registration / पंजीकरण", layout="centered")

# --- DATABASE CONNECTION ---
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Database connection failed / डेटाबेस कनेक्शन विफल: {e}")
    st.stop()

# --- COMPETITIONS & DATES ---
COMPETITIONS = {
    "हिंदी मुहावरें, लोकोक्तियां एवं प्रशासनिक शब्दावली": "2026-09-17",
    "शब्दकोश प्रतियोगिता": "2026-09-18",
    "हिंदी टंकण प्रतियोगिता": "2026-09-21",
    "निबंध लेखन": "2026-09-23",
    "वाद-विवाद प्रतियोगिता": "2026-09-24",
    "तस्वीर क्या बोलती है": "2026-09-25",
    "टिप्पणी एवं पत्र मसौदा लेखन": "2026-09-28"
}

# --- ADMIN DASHBOARD (SIDEBAR) ---
with st.sidebar:
    st.header("Admin Dashboard")
    admin_pass = st.text_input("Enter Admin Password", type="password")
    
    if admin_pass:
        if admin_pass == st.secrets["ADMIN_PASSWORD"]:
            st.success("Access Granted")
            if st.button("Refresh Data"):
                st.rerun()
                
            # Fetch all registrations
            res = supabase.table("registrations").select("*").execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df = df[['unique_code', 'name', 'designation', 'place', 'railway_zone', 'competition', 'date', 'created_at']]
                
                # Show total participants
                st.write(f"**Total Registrations:** {len(df)}")
                st.dataframe(df)
                
                # Download button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Data as CSV",
                    data=csv,
                    file_name='registrations.csv',
                    mime='text/csv',
                )
            else:
                st.info("No registrations yet.")
        else:
            st.error("Incorrect Password")

# --- MAIN REGISTRATION UI ---
st.title("Hindi Divas Registration / हिंदी दिवस पंजीकरण")
st.markdown("Please fill out the form below to generate your unique 4-digit enrollment code. / अपना विशिष्ट 4-अंकीय नामांकन कोड प्राप्त करने के लिए कृपया नीचे दिया गया फॉर्म भरें।")
st.divider()

# 1. Slide-down Menu for Competition
competition_selection = st.selectbox(
    "Select Competition / प्रतियोगिता चुनें *",
    options=list(COMPETITIONS.keys())
)

# 2. Automatically Display Corresponding Date
event_date = COMPETITIONS[competition_selection]
# Format the date for Indian standard viewing (DD/MM/YYYY)
display_date = f"{event_date[-2:]}/{event_date[5:7]}/{event_date[:4]}"
st.info(f"📅 **Scheduled Date / निर्धारित तिथि:** {display_date}")
st.divider()

# 3. User Details
name = st.text_input("Full Name / पूरा नाम *")
designation = st.text_input("Designation / पदनाम *")
place = st.text_input("Place of Posting / तैनाती का स्थान *")

railway_zone = st.radio(
    "Railway Zone / रेलवे जोन *",
    options=["Central Railway (CR)", "Western Railway (WR)"]
)

# 4. Submit Button
if st.button("Register & Generate Code / पंजीकरण करें और कोड बनाएं", type="primary"):
    if not name or not designation or not place:
        st.error("Please fill in all mandatory fields. / कृपया सभी अनिवार्य फ़ील्ड भरें।")
    else:
        with st.spinner("Generating Code... / कोड जनरेट हो रहा है..."):
            # Generate a unique 4-digit code
            code_is_unique = False
            while not code_is_unique:
                new_code = str(random.randint(1000, 9999))
                # Check if code already exists in database
                check = supabase.table("registrations").select("id").eq("unique_code", new_code).execute()
                if len(check.data) == 0:
                    code_is_unique = True

            # Save to Database
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
                
                st.success("Registration Successful! / पंजीकरण सफल!")
                st.info(f"### Your Unique Code / आपका विशिष्ट कोड: **{new_code}**")
                st.warning("Please write this code down. You will need it to start your exam. / कृपया यह कोड लिख लें। अपनी परीक्षा शुरू करने के लिए आपको इसकी आवश्यकता होगी।")
                
            except Exception as e:
                st.error(f"Failed to register / पंजीकरण विफल: {e}")
