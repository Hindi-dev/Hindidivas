import streamlit as st
from supabase import create_client, Client
import datetime
import time
import streamlit.components.v1 as components

# --- पेज सेटिंग ---
st.set_page_config(page_title="हिंदी पखवाड़ा परीक्षा पोर्टल", page_icon="📝", layout="centered")

# --- डेटाबेस कनेक्शन ---
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error("डेटाबेस से जुड़ने में त्रुटि। कृपया बाद में प्रयास करें।")
    st.stop()

# --- बेस URL (Supabase Storage) ---
# .rstrip('/') यह सुनिश्चित करता है कि URL के अंत में कोई अतिरिक्त स्लैश न हो
base_url = f"{st.secrets.get('SUPABASE_URL', '').rstrip('/')}/storage/v1/object/public/competition_documents/"

# --- प्रतियोगिताओं का विवरण और तिथियां ---
COMPETITIONS = {
    "idioms": {
        "name": "हिंदी मुहावरें, लोकोक्तियां एवं प्रशासनिक शब्दावली",
        "time_limit_mins": 10,
        "competition_date": "2026-09-17",
        "question": f"{base_url}idioms_question.pdf"
    },
    "dictionary": {
        "name": "हिंदी शब्दकोश से शब्द खोजना",
        "time_limit_mins": 10,
        "competition_date": "2026-09-18",
        "question": f"{base_url}dictionary_question.pdf"
    },
    "typing": {
        "name": "हिंदी टंकण प्रतियोगिता",
        "time_limit_mins": 10,
        "competition_date": "2026-09-21", # यदि अभी टेस्ट कर रहे हैं तो इसे "2026-08-27" कर लें
        "question": f"{base_url}typing.html"
    },
    "essay": {
        "name": "हिंदी निबंध प्रतियोगिता",
        "time_limit_mins": 10,
        "competition_date": "2026-09-23",
        "question": f"{base_url}essay_question.pdf"
    },
    "debate": {
        "name": "हिंदी वाद-विवाद प्रतियोगिता",
        "time_limit_mins": 10,
        "competition_date": "2026-09-24",
        "question": f"{base_url}debate_question.pdf"
    },
    "picture": {
        "name": "तस्वीर देखकर कहानी लिखना",
        "time_limit_mins": 10,
        "competition_date": "2026-09-25",
        "question": f"{base_url}picture_question.pdf"
    },
    "drafting": {
        "name": "मसौदा लेखन प्रतियोगिता (Drafting)",
        "time_limit_mins": 10,
        "competition_date": "2026-09-28",
        "question": f"{base_url}drafting_question.pdf"
    }
}

# --- यूआरएल से प्रतियोगिता जांचना ---
query_params = st.query_params
comp_slug = query_params.get("comp")

if not comp_slug or comp_slug not in COMPETITIONS:
    st.error("❌ अमान्य प्रतियोगिता लिंक (Invalid Competition Link)")
    st.warning("कृपया सुनिश्चित करें कि आपने व्यवस्थापक द्वारा दिए गए सही लिंक पर क्लिक किया है। (उदाहरण: ?comp=idioms)")
    st.stop()

competition_info = COMPETITIONS[comp_slug]
comp_name = competition_info["name"]
comp_date = competition_info["competition_date"]
time_limit = competition_info["time_limit_mins"]

st.title(f"🏆 {comp_name}")
st.divider()

# --- दिनांक जांच (Date Validation) ---
today_str = datetime.datetime.now().strftime("%Y-%m-%d")

if today_str != comp_date:
    st.warning(f"🚫 यह प्रतियोगिता वर्तमान में बंद है। इसकी निर्धारित तिथि **{comp_date}** है।")
    st.stop()
else:
    st.success("✅ यह प्रतियोगिता आज सक्रिय (ACTIVE) है।")

# --- इंटरनेट जांच बटन ---
if st.button("🌐 इंटरनेट कनेक्शन जांचें"):
    st.toast("आपका इंटरनेट सही ढंग से काम कर रहा है!", icon="✅")

st.markdown("### अपना 4-अंकीय कोड दर्ज करें")
unique_code = st.text_input("पंजीकरण के समय प्राप्त कोड (Unique Code):", max_chars=4)

if unique_code:
    # चेक करें कि क्या यह कोड registrations टेबल में है
    try:
        user_check = supabase.table("registrations").select("*").eq("unique_code", unique_code).execute()
        
        if len(user_check.data) == 0:
            st.error("अमान्य कोड! कृपया सही 4-अंकीय पंजीकरण कोड दर्ज करें।")
            st.stop()
        else:
            user_data = user_check.data[0]
            st.success(f"स्वागत है, {user_data.get('name', 'प्रतिभागी')}!")
    except Exception as e:
        st.error(f"सत्यापन में त्रुटि: {e}")
        st.stop()

    # परीक्षा शुरू करने का सेशन (Session State)
    if "exam_started" not in st.session_state:
        st.session_state.exam_started = False

    if not st.session_state.exam_started:
        if st.button("🚀 प्रतियोगिता प्रारंभ करें (Start Exam)"):
            st.session_state.exam_started = True
            st.session_state.start_time = time.time()
            st.rerun()

    # जब परीक्षा शुरू हो जाए
    if st.session_state.exam_started:
        st.divider()
        
        # --- प्रश्न पत्र दिखाना ---
        st.markdown("### 📝 प्रश्न पत्र / निर्देश")
        
        # टाइपिंग के लिए HTML को पेज के अंदर ही चलाएं (iframe में)
        if comp_slug == "typing":
            st.info("👇 नीचे दिए गए बॉक्स में अपना टंकण (Typing) टेस्ट दें:")
            typing_url = f"{base_url}typing.html"
            components.iframe(typing_url, height=600, scrolling=True)
        else:
            # बाकी PDF प्रतियोगिताओं के लिए लिंक दिखाएं
            question_link = competition_info["question"]
            st.markdown(f"**[📄 प्रश्न पत्र देखने/डाउनलोड करने के लिए यहाँ क्लिक करें]({question_link})**")
            
        st.divider()

        # --- टाइमर और फाइल अपलोड ---
        elapsed_time = time.time() - st.session_state.start_time
        time_left = (time_limit * 60) - elapsed_time

        if time_left > 0:
            mins, secs = divmod(int(time_left), 60)
            st.warning(f"⏳ **बचा हुआ समय:** {mins:02d}:{secs:02d}")
            time.sleep(1)
            st.rerun()  # टाइमर को हर सेकंड अपडेट करने के लिए
        else:
            st.error("समय समाप्त! (Time's Up!)")
            st.warning("अब आप दस्तावेज़ जमा नहीं कर सकते।")
            st.stop()

        st.markdown("### 📤 अपनी उत्तर-पुस्तिका जमा करें")
        uploaded_file = st.file_uploader("यहाँ अपना PDF या फोटो (JPG/PNG) अपलोड करें", type=["pdf", "jpg", "jpeg", "png"])

        if uploaded_file is not None:
            if st.button("दस्तावेज़ जमा करें (Submit)"):
                with st.spinner("फ़ाइल अपलोड हो रही है... कृपया प्रतीक्षा करें"):
                    try:
                        # फाइल का नाम सुरक्षित बनाना
                        file_ext = uploaded_file.name.split('.')[-1]
                        file_name = f"{unique_code}_{comp_slug}.{file_ext}"
                        
                        # Storage में फाइल अपलोड (x-upsert से पुरानी फाइल ओवरराइट हो जाएगी)
                        res = supabase.storage.from_("competition_documents").upload(
                            file_name,
                            uploaded_file.getvalue(),
                            file_options={"content-type": uploaded_file.type, "x-upsert": "true"}
                        )
                        
                        file_public_url = f"{base_url}{file_name}"
                        
                        # Database में एंट्री करना
                        supabase.table("competition_enrollments").upsert({
                            "unique_code": unique_code,
                            "competition_slug": comp_slug,
                            "file_url": file_public_url
                        }).execute()

                        st.success("🎉 फ़ाइल सफलतापूर्वक अपलोड की गई! आपकी प्रतियोगिता पूरी हो गई है।")
                        st.balloons()
                    except Exception as e:
                        st.error(f"फ़ाइल अपलोड करने में त्रुटि: {e}")
