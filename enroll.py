import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Competition Enrollment / प्रतियोगिता नामांकन", layout="centered")

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

# --- COMPETITION CONFIGURATION (07 EVENTS) ---
base_url = f"{st.secrets.get('SUPABASE_URL', '').rstrip('/')}/storage/v1/object/public/competition_documents/"

COMPETITIONS = {
    "idioms": {
        "name": "हिंदी मुहावरें, लोकोक्तियां एवं प्रशासनिक शब्दावली", 
        "time_limit_mins": 10,
        "competition_date": "2026-09-18",
        "question": f"{base_url}idioms_question.pdf"
    },
    "dictionary": {
        "name": "शब्दकोश प्रतियोगिता", 
        "time_limit_mins": 45,
        "competition_date": "2026-09-18",
        "question": f"{base_url}dictionary_question.pdf"
    },
    "typing": {
        "name": "हिंदी टंकण प्रतियोगिता", 
        "time_limit_mins": 10,
        "competition_date": "2026-09-21",
        "question": f"{base_url}typing_question.pdf"
    },
    "essay": {
        "name": "निबंध लेखन", 
        "time_limit_mins": 60,
        "competition_date": "2026-09-23",
        "question": f"{base_url}essay_question.pdf"
    },
    "debate": {
        "name": "वाद-विवाद प्रतियोगिता", 
        "time_limit_mins": 60,
        "competition_date": "2026-09-24",
        "question": f"{base_url}debate_question.pdf"
    },
    "picture": {
        "name": "तस्वीर क्या बोलती है", 
        "time_limit_mins": 30,
        "competition_date": "2026-09-25",
        "question": f"{base_url}picture_question.pdf"
    },
    "drafting": {
        "name": "टिप्पणी एवं पत्र मसौदा लेखन", 
        "time_limit_mins": 45,
        "competition_date": "2026-09-28",
        "question": f"{base_url}drafting_question.pdf"
    }
}

# --- GET URL PARAMETER ---
comp_slug = st.query_params.get("comp")

if comp_slug not in COMPETITIONS:
    st.error("Invalid Competition Link / अमान्य प्रतियोगिता लिंक")
    st.info("Please make sure you clicked the correct link provided by the administrator. / कृपया सुनिश्चित करें कि आपने व्यवस्थापक द्वारा दिए गए सही लिंक पर क्लिक किया है।")
    st.stop()

comp_details = COMPETITIONS[comp_slug]
st.title(comp_details["name"])
st.write(f"**Time Limit / समय सीमा:** {comp_details['time_limit_mins']} Minutes / मिनट")
st.divider()

# --- DATE VALIDATION LOGIC (IST TIMEZONE) ---
IST = timezone(timedelta(hours=5, minutes=30))
today = datetime.now(IST).date()
scheduled_date = datetime.strptime(comp_details["competition_date"], "%Y-%m-%d").date()
formatted_scheduled_date = scheduled_date.strftime('%d/%m/%Y')

if today < scheduled_date:
    st.warning("This competition has not started yet. / यह प्रतियोगिता अभी शुरू नहीं हुई है।")
    st.info(f"📅 **Scheduled Date / निर्धारित तिथि:** {formatted_scheduled_date}")
    st.stop()
elif today > scheduled_date:
    st.error("This competition is closed. / यह प्रतियोगिता बंद हो चुकी है।")
    st.info(f"📅 **Concluded On / समाप्त तिथि:** {formatted_scheduled_date}")
    st.stop()
else:
    st.success("This competition is currently ACTIVE. / यह प्रतियोगिता वर्तमान में सक्रिय है।")

st.divider()

# --- LOGIN & TIMER SYSTEM ---
unique_code = st.text_input("Enter your 4-digit Registration Code / अपना 4-अंकीय पंजीकरण कोड दर्ज करें", max_chars=4)

if unique_code:
    # 1. Verify code exists in registrations
    user_check = supabase.table("registrations").select("name").eq("unique_code", unique_code).execute()
    
    if len(user_check.data) == 0:
        st.error("Invalid Code. Please register first. / अमान्य कोड। कृपया पहले पंजीकरण करें।")
        st.stop()
        
    user_name = user_check.data[0]['name']
    st.success(f"Welcome / स्वागत है, **{user_name}**!")
    
    # 2. Check if timer has started for this competition
    enroll_check = supabase.table("competition_enrollments").select("*").eq("unique_code", unique_code).eq("competition_slug", comp_slug).execute()
    
    if len(enroll_check.data) == 0:
        st.warning("Once you click 'Start', your timer will begin. / 'प्रारंभ' पर क्लिक करने के बाद, आपका समय शुरू हो जाएगा।")
        if st.button("Start Competition / प्रतियोगिता प्रारंभ करें"):
            data = {"unique_code": unique_code, "competition_slug": comp_slug}
            supabase.table("competition_enrollments").insert(data).execute()
            st.rerun()
    else:
        start_time_str = enroll_check.data[0]['start_time']
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        end_time = start_time + timedelta(minutes=comp_details["time_limit_mins"])
        now = datetime.now(timezone.utc)
        
        time_left = end_time - now
        minutes_left = int(time_left.total_seconds() // 60)
        
        if now >= end_time:
            st.error("Your time is up! Submissions are now closed. / आपका समय समाप्त हो गया है! प्रस्तुतियाँ अब बंद कर दी गई हैं।")
        else:
            st.info(f"⏳ **Time Remaining / शेष समय:** Approx {minutes_left} minutes.")
            
            # Question Paper Download Section
            st.divider()
            st.subheader("Question Paper / प्रश्न पत्र")
            st.markdown(f"**[📄 Click here to view/download the Question Paper / प्रश्न पत्र देखने/डाउनलोड करने के लिए यहाँ क्लिक करें]({comp_details['question']})**")
            st.divider()
            
            # File Upload Section
            uploaded_file = st.file_uploader(
                "Upload your final answer file (PDF, DOC, DOCX, JPG, JPEG) / अपनी अंतिम उत्तर फ़ाइल अपलोड करें", 
                type=["pdf", "doc", "docx", "jpg", "jpeg"]
            )
            
            if uploaded_file is not None:
                if st.button("Submit Document / दस्तावेज़ जमा करें"):
                    with st.spinner("Uploading... / अपलोड हो रहा है..."):
                        try:
                            file_extension = uploaded_file.name.split(".")[-1]
                            file_path = f"{unique_code}_{comp_slug}.{file_extension}"
                            
                            file_bytes = uploaded_file.getvalue()
                            supabase.storage.from_("competition_documents").upload(
                                file_path, 
                                file_bytes, 
                                file_options={"x-upsert": "true"}
                            )
                            
                            file_url = supabase.storage.from_("competition_documents").get_public_url(file_path)
                            
                            supabase.table("competition_enrollments").update(
                                {"file_url": file_url}
                            ).eq("unique_code", unique_code).eq("competition_slug", comp_slug).execute()
                            
                            st.success("File uploaded successfully! / फ़ाइल सफलतापूर्वक अपलोड की गई!")
                        except Exception as e:
                            st.error(f"Upload failed / अपलोड विफल: {e}")
