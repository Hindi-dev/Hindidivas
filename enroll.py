import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timezone, timedelta
import urllib.request
import time
from supabase import create_client, Client

# --- 1. PAGE CONFIGURATION & ANTI-COPY CSS ---
st.set_page_config(page_title="प्रतियोगिता नामांकन / Competition Enrollment", layout="centered", page_icon="📝")

st.markdown("""
<style>
* { -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION ---
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

# --- 3. COMPETITION CONFIGURATION (07 EVENTS) ---
base_url = f"{st.secrets.get('SUPABASE_URL', '')}/storage/v1/object/public/competition_documents/"

COMPETITIONS = {
    "idioms": {"name": "हिंदी मुहावरें, लोकोक्तियां एवं प्रशासनिक शब्दावली", "time_limit_mins": 25, "competition_date": "2026-09-17", "start_time": "10:00", "end_time": "23:59", "question": f"{base_url}idioms_question.pdf"},
    "dictionary": {"name": "शब्दकोश प्रतियोगिता", "time_limit_mins": 45, "competition_date": "2026-09-18", "start_time": "10:00", "end_time": "23:59", "question": f"{base_url}dictionary_question.pdf"},
    "typing": {"name": "हिंदी टंकण प्रतियोगिता", "time_limit_mins": 20, "competition_date": "2026-09-21", "start_time": "10:00", "end_time": "23:59", "question": f"{base_url}typing_question.pdf"},
    "essay": {"name": "निबंध लेखन", "time_limit_mins": 60, "competition_date": "2026-09-23", "start_time": "10:00", "end_time": "23:59", "question": f"{base_url}essay_question.pdf"},
    "debate": {"name": "वाद-विवाद प्रतियोगिता", "time_limit_mins": 60, "competition_date": "2026-09-24", "start_time": "10:00", "end_time": "23:59", "question": f"{base_url}debate_question.pdf"},
    "picture": {"name": "तस्वीर क्या बोलती है", "time_limit_mins": 30, "competition_date": "2026-09-25", "start_time": "10:00", "end_time": "23:59", "question": f"{base_url}picture_question.pdf"},
    "drafting": {"name": "टिप्पणी एवं पत्र मसौदा लेखन", "time_limit_mins": 45, "competition_date": "2026-09-28", "start_time": "10:00", "end_time": "23:59", "question": f"{base_url}drafting_question.pdf"}
}

# --- 4. FULL 50 QUESTIONS ---
IDIOMS_QUESTIONS = [
    {"q": "1. अपनी डफली अपना राग", "options": ["स्वतंत्र होना", "अपना दुखड़ा रोना", "संगठन का अभाव", "सबका अपने-अपने मन के अनुसार चलना"], "ans": "सबका अपने-अपने मन के अनुसार चलना"},
    {"q": "2. कोई इर घाट तो कोई बीर घाट", "options": ["बार-बार कथन बदलना", "ताल-मेल ना होना", "तितर-बितर होना", "बहुत चालाक होना"], "ans": "ताल-मेल ना होना"},
    {"q": "3. गए थे रोजा छुड़ाने ,नमाज गले पड़ी", "options": ["मुश्किल में पड़ जाना", "कष्ट पहुँचाना", "गरीब हो जाना", "उपकार करने के बदले स्वयं दुख भोगना पड़ा"], "ans": "उपकार करने के बदले स्वयं दुख भोगना पड़ा"},
    {"q": "4. फिसल पड़े तो हर गंगे", "options": ["मजबूरी में काम करना", "नुकसान उठाना", "एक साथ दो काम", "विपत्ति पड़ने पर ईश्वर का स्मरण करना"], "ans": "मजबूरी में काम करना"},
    {"q": "5. अंग–अंग खिल उठना", "options": ["बहुत प्रसन्न होना", "खिल उठना", "बहुत क्रोधित होना", "बहुत चिल्लाना"], "ans": "बहुत प्रसन्न होना"},
    {"q": "6. हँसुए के ब्याह में खुरपी का गीत", "options": ["शादी का गीत गाना", "जश्न मनाना", "असंगत बातें करना", "निचले स्तर का कार्य करना"], "ans": "असंगत बातें करना"},
    {"q": "7. आसमान पर चढ़ाना", "options": ["अत्यधिक  अभिमान करना", "कठिन काम के लिए  प्रेरित करना", "बहुत शोर करना", "अत्यघिक प्रशंसा करना"], "ans": "अत्यघिक प्रशंसा करना"},
    {"q": "8. प्रवर समिति", "options": ["High power committee", "low power committee", "select committee", "selection committee"], "ans": "select committee"},
    {"q": "9. सिर हथेली पर रखना", "options": ["वीरता का प्रदर्शन करना", "पराजय स्वीकार कर लेना", "मरने के तैयार होना", "अहं का विसर्जन करना"], "ans": "मरने के तैयार होना"},
    {"q": "10. मुँह का निवाला होना", "options": ["स्वादिष्ट एवं प्रियकर", "बहुत आसान काम", "अत्यंत प्रिय", "बहुत कठिन काम"], "ans": "बहुत आसान काम"},
    {"q": "11. अगर-मगर करना", "options": ["इधर की बात उधर करना", "कपट करना", "व्यर्थ समय गँवाना", "बहाने बनाना"], "ans": "बहाने बनाना"},
    {"q": "12. सर्वोत्तम सेवा", "options": ["best work", "best services", "worst work", "worst service"], "ans": "best services"},
    {"q": "13. सूचनार्थ", "options": ["for information", "for action", "for perusal", "for submission"], "ans": "for information"},
    {"q": "14. के अनुपालन में", "options": ["in consultation", "in pursuance of", "in exercise of", "in obedience of"], "ans": "in pursuance of"},
    {"q": "15. आपके अनुमोदन की प्रत्याशा में", "options": ["in reply of your approval", "for information of your approval", "in anticipation of your approval", "in submission of your approval"], "ans": "in anticipation of your approval"},
    {"q": "16. कृपया इसे सर्वथा गोपनीय समझा जाए ।", "options": ["please treat this as strictly common", "please treat this as very common", "please treat this as strictly confidential", "please treat this as strictly convenient"], "ans": "please treat this as strictly confidential"},
    {"q": "17. आवश्यक कार्रवाई करने के लिए", "options": ["for doing urgent work", "for doing urgent action", "for doing the needful", "for doing the immediate action"], "ans": "for doing the needful"},
    {"q": "18. आगे की प्रगति से अवगत कराएँ।", "options": ["inform further development", "advise further development", "advise earlier development", "notice further development"], "ans": "advise further development"},
    {"q": "19. Data entry operator", "options": ["आंकड़ा प्रविष्ठि चालक", "आंकड़ा प्रविष्ठि प्रचालक", "डाटा प्रविष्टि प्रचालक", "आंकड़ा प्रविष्टि प्रचालक"], "ans": "आंकड़ा प्रविष्टि प्रचालक"},
    {"q": "20. debarred from the benefit", "options": ["लाभ से वंचित", "हितलाभ से वर्जित", "लाभ से विवर्जित", "हितलाभ से विवर्जित"], "ans": "लाभ से वंचित"},
    {"q": "21. commutation of pension", "options": ["पेंशन का राशीकरण", "पेंशन की वृद्धि", "पेंशन की कटौती", "पेंशन का संराशीकरण"], "ans": "पेंशन का संराशीकरण"},
    {"q": "22. attested true copy", "options": ["प्रमाणित ठीक प्रतिलिपि", "प्रमाणित सत्य प्रति", "अनुप्रमाणित उचित प्रति", "अनुप्रमाणित सही प्रतिलिपि"], "ans": "अनुप्रमाणित सही प्रतिलिपि"},
    {"q": "23. इंद्र का अखाड़ा", "options": ["बहुत अच्छी जगह", "बहुत अलग जगह", "नाचने का स्थान", "ऐश- मौज की जगह"], "ans": "ऐश- मौज की जगह"},
    {"q": "24. हाथ ऊंचा होना", "options": ["युद्ध में विजय प्राप्त कर लेना", "दान आदि के लिए मन में उदारता का भाव", "अत्यधिक प्रतिष्ठित", "किसी को मारने के लिए हाथ उठाना"], "ans": "दान आदि के लिए मन में उदारता का भाव"},
    {"q": "25. तीन लोक से मथुरा न्यारी", "options": ["बहुत सुंदर होना", "दूर की वस्तु सुंदर लगना", "सबसे निराला स्थान", "कृष्ण भक्त होना"], "ans": "सबसे निराला स्थान"},
    {"q": "26. temporary appointment", "options": ["स्थायी नियुक्ति", "अस्थायी प्रतिनियुक्ति", "अस्थायी नियुक्ति"], "ans": "अस्थायी नियुक्ति"},
    {"q": "27. विहंगम दृष्टि", "options": ["सरसरी दृष्टि", "गहरी दृष्टि", "सम्यक् दृष्टि", "पैनी दृष्टि"], "ans": "सरसरी दृष्टि"},
    {"q": "28. the file in question is not traceable", "options": ["प्रश्न वाली फाइल नही मिल रही है", "उपेक्षित फाइल खो गई है", "अपेक्षित फाइल नहीं मिल रही है", "संदर्भित फाइल नहीं मिल रही है"], "ans": "संदर्भित फाइल नहीं मिल रही है"},
    {"q": "29. निष्पादन लेखापरीक्षा", "options": ["assessment audit", "excess audit", "performance audit", "compliance audit"], "ans": "performance audit"},
    {"q": "30. provisional assessment", "options": ["अंतरिम नियतन", "अंतिम निर्धारण", "अनंतिम निर्धारण", "अंतरिम निर्धारण"], "ans": "अनंतिम निर्धारण"},
    {"q": "31. under one's hand", "options": ["अपने हाथ से", "अपनी क्षमता अनुसार", "अपनी मुहर से", "अपने हस्ताक्षर सहित"], "ans": "अपने हस्ताक्षर सहित"},
    {"q": "32. on probation", "options": ["प्रतिनियुक्ति पर", "नियुक्ति पर", "परिवीक्षाधीन", "जमानत पर"], "ans": "परिवीक्षाधीन"},
    {"q": "33. overall position", "options": ["सही स्थिति", "उचित स्थिति", "समग्र स्थिति"], "ans": "समग्र स्थिति"},
    {"q": "34. नगर राजभाषा कार्यान्वयन समिति", "options": ["Town official language implementation committee", "Town rajbhasha implement committee", "committee for official language", "town official performance committee"], "ans": "Town official language implementation committee"},
    {"q": "35. Draft for approval", "options": ["अनुमोदन हेतु मसौदा", "अवलोकन  हेतु मसौदा", "आदेश हेतु मसौदा"], "ans": "अनुमोदन हेतु मसौदा"},
    {"q": "36. Circulate and then file", "options": ["फाइल कर दीजिए", "संबद्धित व्यक्तियों को दिखाकर फाइल कर दीजिए", "घुमाकर फाइल कर दीजिए"], "ans": "संबद्धित व्यक्तियों को दिखाकर फाइल कर दीजिए"},
    {"q": "37. sanctioned budget", "options": ["अनुमोदित बजट", "समेकित बजट", "परिकल्पित बजट", "संस्वीकृत बजट"], "ans": "संस्वीकृत बजट"},
    {"q": "38. service sheet", "options": ["सेवा शीट", "सेवा पत्र", "सेवा क्रम", "सेवा रोल"], "ans": "सेवा पत्र"},
    {"q": "39. seniority-cum-merit", "options": ["वरिष्ठता कम मैरिट", "वरिष्ठता कम योग्यता", "वरिष्ठता सह योग्यताक्रम", "वरिष्ठता सह योग्यता"], "ans": "वरिष्ठता सह योग्यता"},
    {"q": "40. अनिवार्य अर्हता", "options": ["necessary requirement", "mandatory qualification", "essential qualification", "essential requirement"], "ans": "essential qualification"},
    {"q": "41. प्रशासनिक शब्दावली में 'Post Audit' का सटीक हिन्दी पर्याय क्या है?", "options": ["पूर्व लेखापरीक्षा", "पश्च लेखापरीक्षा", "बाद की लेखापरीक्षा", "अंतिम लेखापरीक्षा"], "ans": "पश्च लेखापरीक्षा"},
    {"q": "42. 'Piece meal clearance' के लिए सही पारिभाषिक शब्द चुनें:", "options": ["आंशिक निकासी", "टुकड़ों में निकासी", "खण्डशः निकासी", "थोड़ी-थोड़ी निकासी"], "ans": "खण्डशः निकासी"},
    {"q": "43. 'Proforma adjustment' का अधिकृत अनुवाद क्या होगा?", "options": ["प्रारूप समायोजन", "प्रोफार्मा समायोजन", "अस्थायी समायोजन", "तदर्थ समायोजन"], "ans": "प्रोफार्मा समायोजन"},
    {"q": "44. 'Re-appropriation' को प्रशासनिक हिन्दी में क्या कहा जाता है?", "options": ["पुनर्विनियोग", "पुनरावंटन", "पुनः नियोजन", "पुर्नानयोजन"], "ans": "पुर्नानयोजन"},
    {"q": "45. 'Reconciliation Statement' का सही अर्थ क्या है?", "options": ["मिलान विवरण", "समझौता विवरण", "समाधान विवरण", "सामंजस्य विवरण"], "ans": "समाधान विवरण"},
    {"q": "46. 'Self liquidating advance' के लिए सटीक शब्द कौन सा है?", "options": ["स्वतः समाप्त ऋण", "स्वनिर्भर पेशगी", "स्वपरिपोषक ऋण", "स्वतः चुकाने योग्य उधार"], "ans": "स्वपरिपोषक ऋण"},
    {"q": "47. 'Short term capital gain' का हिन्दी पर्याय क्या है?", "options": ["अल्पावधि पूंजी प्राप्ति", "अल्पकालिक पूंजी अभिलाभ", "अल्पकालिक पूंजीगत लाभ", "थोड़े समय का पूंजी लाभ"], "ans": "अल्पकालिक पूंजी अभिलाभ"},
    {"q": "48. 'Stores issued book' को कार्यालयीन हिन्दी में क्या कहेंगे?", "options": ["निर्गत भंडार बही", "जावक भंडार बही", "जारी सामान बही", "प्रेषित भंडार बही"], "ans": "जावक भंडार बही"},
    {"q": "49. 'Test audit' का पारिभाषिक अर्थ क्या है?", "options": ["परीक्षण लेखापरीक्षा", "जांच लेखापरीक्षा", "प्रायोगिक लेखापरीक्षा", "नमूना लेखापरीक्षा"], "ans": "नमूना लेखापरीक्षा"},
    {"q": "50. 'Propriety Audit' का हिन्दी में सही अनुवाद क्या है?", "options": ["औचित्य लेखापरीक्षा", "संपत्ति लेखापरीक्षा", "यथार्थ लेखापरीक्षा", "उपयुक्तता लेखापरीक्षा"], "ans": "औचित्य लेखापरीक्षा"}
]

# --- 5. URL ROUTING & VALIDATION ---
comp_slug = st.query_params.get("comp")

if not comp_slug or comp_slug not in COMPETITIONS:
    st.error("अमान्य प्रतियोगिता लिंक / Invalid Competition Link")
    st.stop()

comp_details = COMPETITIONS[comp_slug]
st.title(comp_details["name"])
st.write(f"**समय सीमा / Time Limit:** {comp_details['time_limit_mins']} मिनट / Minutes")
st.divider()

IST = timezone(timedelta(hours=5, minutes=30))
now = datetime.now(IST)
today_str = now.strftime("%Y-%m-%d")
current_time_str = now.strftime("%H:%M")

comp_date = comp_details["competition_date"]
start_time = comp_details.get("start_time", "00:00")
end_time = comp_details.get("end_time", "23:59")
formatted_scheduled_date = datetime.strptime(comp_date, "%Y-%m-%d").strftime('%d/%m/%Y')

if today_str < comp_date:
    st.warning("यह प्रतियोगिता अभी शुरू नहीं हुई है। / This competition has not started yet.")
    st.info(f"📅 **निर्धारित तिथि / Scheduled Date:** {formatted_scheduled_date}")
    st.stop()
elif today_str > comp_date:
    st.error("यह प्रतियोगिता बंद हो चुकी है। / This competition is closed.")
    st.stop()
else:
    if current_time_str < start_time:
        st.warning("⏳ **प्रतियोगिता अभी शुरू नहीं हुई है!**")
        st.info(f"यह टेस्ट आज **{start_time} बजे** से **{end_time} बजे** के बीच ही सक्रिय रहेगा।")
        st.info("🔄 **कृपया प्रतीक्षा करें:** यह पेज अपने आप रिफ्रेश हो रहा है। समय होते ही टेस्ट स्वतः खुल जाएगा।")
        components.html("<script>setTimeout(function() { window.parent.location.reload(); }, 30000);</script>", height=0)
        st.stop()
    elif current_time_str > end_time:
        st.error("❌ **समय समाप्त!** यह प्रतियोगिता बंद हो चुकी है।")
        st.stop()
    else:
        st.success("यह प्रतियोगिता वर्तमान में सक्रिय है। / This competition is currently ACTIVE.")

st.divider()

col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("लॉगिन / Login")
with col2:
    if st.button("🌐 इंटरनेट जांचें / Check Internet"):
        with st.spinner("जांच हो रही है..."):
            try:
                start_t = time.time()
                urllib.request.urlopen('https://www.google.com', timeout=3)
                latency = round((time.time() - start_t) * 1000)
                if latency < 800: st.success(f"Speed: {latency}ms - Good")
                else: st.warning(f"Speed: {latency}ms - Slow")
            except:
                st.error("इंटरनेट काम नही कर रहा है।")

unique_code = st.text_input("अपना 4-अंकीय पंजीकरण कोड दर्ज करें / Enter 4-digit Code", max_chars=4, type="password")

if unique_code:
    user_check = supabase.table("registrations").select("name").eq("unique_code", unique_code).execute()
    
    if len(user_check.data) == 0:
        st.error("अमान्य कोड। कृपया पहले पंजीकरण करें। / Invalid Code. Please register first.")
        st.stop()
        
    user_name = user_check.data[0]['name']
    st.success(f"स्वागत है / Welcome, **{user_name}**!")
    
    enroll_check = supabase.table("competition_enrollments").select("*").eq("unique_code", unique_code).eq("competition_slug", comp_slug).execute()
    has_attempted = len(enroll_check.data) > 0
    st.markdown("---")

    # ==========================================
    # ROUTE 1: IDIOMS (LIVE MCQ + ANTI CHEAT)
    # ==========================================
    if comp_slug == "idioms":
        if "idioms_submitted" not in st.session_state:
            st.session_state.idioms_submitted = False
            st.session_state.idioms_results = {}

        if has_attempted or st.session_state.idioms_submitted:
            if st.session_state.idioms_submitted:
                res = st.session_state.idioms_results
                st.balloons()
                st.markdown("<h2 style='text-align: center; color: #4CAF50;'>🎉 परीक्षा सफलतापूर्वक जमा हो गई!</h2>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                c1.info(f"✅ सही उत्तर: {res['correct']}")
                c2.error(f"❌ गलत उत्तर: {res['wrong']}")
                c3.warning(f"⚪ छोड़े गए: {res['unanswered']}")
                st.markdown(f"<h3 style='text-align:center; color:#004B87;'>🏆 स्कोर: {res['final_score']}</h3>", unsafe_allow_html=True)
                st.stop()
            else:
                st.error("🛑 आप पहले ही यह परीक्षा जमा कर चुके हैं।")
                st.stop()

        st.markdown("### 📝 बहुविकल्पीय प्रश्न (MCQs) - नेगेटिव मार्किंग (-0.25)")
        
        timer_html = f"""
        <div id="timer-container" style="background-color: rgba(227, 242, 253, 0.95); border: 2px solid #2196F3; border-radius: 8px; padding: 10px; text-align: center; font-family: Arial, sans-serif; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <h3 style="margin: 0; color: #004B87; font-size: 15px;">⏳ समय शेष</h3>
            <div id="clock" style="font-size: 28px; font-weight: bold; color: #D32F2F; margin: 5px 0;">--:--</div>
        </div>
        <script>
            window.parent.document.addEventListener('contextmenu', e => e.preventDefault());
            window.parent.document.addEventListener('copy', e => e.preventDefault());
            window.parent.document.addEventListener('paste', e => e.preventDefault());

            var warnings = 0;
            function autoSubmitTest() {{
                var buttons = window.parent.document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {{
                    if (buttons[i].innerText.includes('अपना टेस्ट जमा करें')) {{ buttons[i].click(); break; }}
                }}
            }}

            function enforceSecurity() {{
                if (window.parent.document.hidden || (!window.parent.document.fullscreenElement && !window.parent.document.webkitIsFullScreen)) {{
                    warnings++;
                    alert("⚠️ चेतावनी: टैब बदलना वर्जित है! उल्लंघन: " + warnings + "/2");
                    if (warnings >= 2) {{ autoSubmitTest(); }}
                    else {{ window.parent.document.documentElement.requestFullscreen().catch(e => console.log(e)); }}
                }}
            }}
            window.parent.document.addEventListener('visibilitychange', enforceSecurity);
            window.parent.document.addEventListener('fullscreenchange', enforceSecurity);

            navigator.mediaDevices.getUserMedia({{ audio: true, video: false }}).then(function(stream) {{
                var audioContext = new (window.AudioContext || window.webkitAudioContext)();
                var analyser = audioContext.createAnalyser();
                var microphone = audioContext.createMediaStreamSource(stream);
                var javascriptNode = audioContext.createScriptProcessor(2048, 1, 1);
                analyser.smoothingTimeConstant = 0.8; analyser.fftSize = 1024;
                microphone.connect(analyser); analyser.connect(javascriptNode); javascriptNode.connect(audioContext.destination);

                var talkingTime = 0;
                javascriptNode.onaudioprocess = function() {{
                    var array = new Uint8Array(analyser.frequencyBinCount);
                    analyser.getByteFrequencyData(array);
                    var values = 0; for (var i = 0; i < array.length; i++) {{ values += (array[i]); }}
                    if ((values / array.length) > 40) {{
                        talkingTime++;
                        if (talkingTime > 150) {{ alert("⚠️ बोलना मना है!"); talkingTime = 0; warnings++; if(warnings>=2) autoSubmitTest(); }}
                    }} else {{ talkingTime = 0; }}
                }}
            }}).catch(err => {{ alert("⚠️ माइक्रोफोन की अनुमति दें!"); autoSubmitTest(); }});

            var time_limit = {comp_details['time_limit_mins']} * 60;
            var x = setInterval(function() {{
                time_limit--;
                var m = Math.floor(time_limit / 60); var s = time_limit % 60;
                document.getElementById("clock").innerHTML = (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
                if (time_limit <= 0) {{ clearInterval(x); alert("समय समाप्त! ऑटो-सबमिट हो रहा है..."); autoSubmitTest(); }}
            }}, 1000);
        </script>
        """
        components.html(timer_html, height=100)

        with st.form("mcq_quiz_form"):
            user_answers = {}
            st.markdown("<style>div.row-widget.stRadio > div { gap: 12px; padding-left: 10px; }</style>", unsafe_allow_html=True)
            for i, q_data in enumerate(IDIOMS_QUESTIONS):
                with st.container():
                    st.markdown(f"<div style='font-family: Arial, sans-serif; font-size: 16px; font-weight: 600; margin-bottom: 10px; padding-top: 15px; border-top: 1px solid #e0e0e0;'>{q_data['q']}</div>", unsafe_allow_html=True)
                    user_answers[i] = st.radio(f"Select {i}", q_data['options'], key=f"q_{i}", index=None, label_visibility="collapsed")
                
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("✅ अपना टेस्ट जमा करें (Submit Test)", use_container_width=True)
            
            if submitted:
                correct_answers = 0; wrong_answers = 0; unanswered = 0
                for i, q_data in enumerate(IDIOMS_QUESTIONS):
                    if user_answers[i] == q_data['ans']: correct_answers += 1
                    elif user_answers[i] is not None: wrong_answers += 1
                    else: unanswered += 1
                
                final_score = correct_answers - (wrong_answers * 0.25)
                with st.spinner("सुरक्षित किया जा रहा है..."):
                    try:
                        supabase.table("competition_enrollments").insert({"unique_code": unique_code, "competition_slug": comp_slug, "score": final_score, "correct_answers": correct_answers, "wrong_answers": wrong_answers, "unanswered": unanswered}).execute()
                    except Exception as e: st.error(f"त्रुटि: {e}"); st.stop()
                
                st.session_state.idioms_results = {"correct": correct_answers, "wrong": wrong_answers, "unanswered": unanswered, "final_score": final_score}
                st.session_state.idioms_submitted = True
                st.rerun()

    # ==========================================
    # ROUTE 2: TYPING (HTML TEST)
    # ==========================================
    elif comp_slug == "typing":
        if has_attempted:
            st.error("🛑 आप पहले ही टाइपिंग टेस्ट जमा कर चुके हैं।")
            st.stop()

        st.info("नीचे बॉक्स में टाइप करना शुरू करते ही समय शुरू हो जाएगा। (Hindi Inscript)")
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        
        html_code = f"""
        <!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f6f8; margin:0; padding:0; }}
            #main-app {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            #text-display {{ font-size: 22px; line-height: 1.8; padding: 15px; border: 1px solid #ccc; background: #f9f9f9; user-select: none; display: flex; flex-wrap: wrap; gap: 5px; height: 160px; overflow-y: hidden; }}
            .word {{ padding: 2px 4px; border-radius: 3px; }} .current-word {{ background-color: #e0f7fa; font-weight: bold; border-bottom: 3px solid #00acc1; }}
            .correct {{ color: #2e7d32; }} .incorrect {{ color: #d32f2f; text-decoration: underline; background-color: #ffebee; }}
            #input-box {{ width: 100%; font-size: 22px; padding: 12px; margin-top: 15px; border: 2px solid #00acc1; border-radius: 5px; outline: none; box-sizing: border-box; }}
            #timer {{ font-size: 28px; font-weight: bold; color: #d32f2f; float: right; margin-top: -5px; }}
            .header-info {{ font-size: 18px; font-weight: bold; color: #555; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        </style></head>
        <body>
            <div id="main-app">
                <div class="header-info">ID: <span style="color:#00acc1;">{unique_code}</span> <span id="timer">{comp_details['time_limit_mins']}:00</span></div>
                <div id="text-display"></div>
                <input type="text" id="input-box" placeholder="यहाँ टाइप करना शुरू करें..." autocomplete="off">
            </div>
            <script>
                document.addEventListener('contextmenu', e => e.preventDefault()); document.addEventListener('copy', e => e.preventDefault()); document.addEventListener('paste', e => e.preventDefault());
                const corpus = `भारत का इतिहास बहुत समृद्ध और प्राचीन है। यह सिंधु घाटी सभ्यता से शुरू होता है, जो दुनिया की सबसे पुरानी सभ्यताओं में से एक है। भारतीय संविधान दुनिया का सबसे लंबा लिखित संविधान है, जिसे २६ जनवरी १९५० को लागू किया गया था। इसमें नागरिकों के मौलिक अधिकारों और कर्तव्यों का स्पष्ट वर्णन है। भौगोलिक दृष्टि से, भारत विविधताओं वाला देश है। इसके उत्तर में विशाल हिमालय पर्वत श्रृंखला है, जो देश को ठंडी हवाओं से बचाती है। दक्षिण में विशाल हिंद महासागर है। गंगा, यमुना, गोदावरी, और नर्मदा जैसी नदियाँ कृषि के लिए जीवनदायिनी हैं। आधुनिक युग में, भारतीय अंतरिक्ष अनुसंधान संगठन (इसरो) ने अंतरिक्ष विज्ञान के क्षेत्र में अभूतपूर्व प्रगति की है। चंद्रयान और मंगलयान मिशन भारत की वैज्ञानिक क्षमता के उत्कृष्ट उदाहरण हैं। कृषि आज भी भारतीय अर्थव्यवस्था की रीढ़ है, जहाँ लगभग ५० प्रतिशत से अधिक आबादी प्रत्यक्ष या अप्रत्यक्ष रूप से खेती पर निर्भर है। सूचना प्रौद्योगिकी (आईटी) के क्षेत्र में भी भारत ने वैश्विक स्तर पर अपनी पहचान बनाई है। विविधता में एकता भारत की सबसे बड़ी ताकत है। यहाँ विभिन्न धर्मों, जातियों, और भाषाओं के लोग एक साथ शांतिपूर्ण तरीके से रहते हैं। हमें अपने देश की अखंडता और संप्रभुता की रक्षा के लिए हमेशा तत्पर रहना चाहिए। शिक्षा, स्वास्थ्य, और रोजगार के क्षेत्र में निरंतर विकास ही एक सशक्त राष्ट्र के निर्माण का मार्ग प्रशस्त करेगा।`;
                const baseWords = corpus.replace(/\\n/g, ' ').trim().split(/\s+/).filter(w => w.length > 0);
                let referenceText = []; while(referenceText.length < 1500) referenceText = referenceText.concat(baseWords);
                const inscriptMap = {{"q":"ौ","Q":"औ","w":"ै","W":"ऐ","e":"ा","E":"आ","r":"ी","R":"ई","t":"ू","T":"ऊ","y":"ब","Y":"भ","u":"ह","U":"ङ","i":"ग","I":"घ","o":"द","O":"ध","p":"ज","P":"झ","[":"ड","{{":"ढ","]":"़","}}":"ञ","a":"ो","A":"ओ","s":"े","S":"ए","d":"्","D":"अ","f":"ि","F":"इ","g":"ु","G":"उ","h":"प","H":"फ","j":"र","J":"ऱ","k":"क","K":"ख","l":"त","L":"थ",";":"च",":":"छ","'":"ट","\\"": "ठ","z":"े","Z":"ॆ","x":"ं","X":"ँ","c":"म","C":"ण","v":"न","V":"ऩ","b":"व","B":"ऴ","n":"ल","N":"ळ","m":"स","M":"श",",":",","<":"ष",".":".",">":"।","/":"य","?":"य़","1":"१","2":"२","3":"३","4":"४","5":"५","6":"६","7":"७","8":"८","9":"९","0":"०"}};
                let TIME_LIMIT = {comp_details['time_limit_mins']} * 60; let timeLeft = TIME_LIMIT; let timerInterval = null; let testActive = false; let currentWordIndex = 0; let typedWordsArray = [];
                const displayEl = document.getElementById("text-display"); const inputEl = document.getElementById("input-box");
                displayEl.innerHTML = referenceText.map((word, index) => `<span class="word ${{index === 0 ? 'current-word' : ''}}" id="word-${{index}}">${{word}}</span>`).join("");
                inputEl.addEventListener("keydown", function(e) {{
                    if (e.ctrlKey && (e.key === 'c' || e.key === 'v')) {{ e.preventDefault(); return; }}
                    if (!testActive && timeLeft === TIME_LIMIT && e.key.length === 1) {{
                        testActive = true; timerInterval = setInterval(() => {{ timeLeft--; let m = Math.floor(timeLeft/60); let s = timeLeft%60; document.getElementById("timer").innerText = m + ":" + (s < 10 ? '0' : '') + s; if (timeLeft <= 0) endTest(); }}, 1000);
                    }}
                    if (inscriptMap[e.key]) {{ e.preventDefault(); const start = this.selectionStart; const end = this.selectionEnd; this.value = this.value.slice(0, start) + inscriptMap[e.key] + this.value.slice(end); this.selectionStart = this.selectionEnd = start + 1; }}
                }});
                inputEl.addEventListener("keyup", function(e) {{
                    if (e.key === " ") {{
                        let typedWord = this.value.trim(); if (typedWord === "") {{ this.value = ""; return; }}
                        typedWordsArray.push(typedWord); const wordSpan = document.getElementById(`word-${{currentWordIndex}}`);
                        if (typedWord === referenceText[currentWordIndex]) wordSpan.classList.add("correct"); else wordSpan.classList.add("incorrect");
                        wordSpan.classList.remove("current-word"); currentWordIndex++; this.value = "";
                        const nextWord = document.getElementById(`word-${{currentWordIndex}}`);
                        if (nextWord) {{ nextWord.classList.add("current-word"); nextWord.scrollIntoView({{behavior: 'smooth', block: 'center'}}); }}
                    }}
                }});
                function endTest() {{
                    clearInterval(timerInterval); inputEl.disabled = true; testActive = false; let finalWord = inputEl.value.trim(); if(finalWord) typedWordsArray.push(finalWord);
                    let timeElapsedInMinutes = (TIME_LIMIT - timeLeft) / 60; let totalErrors = 0, totalTypedChars = 0;
                    for (let i = 0; i < typedWordsArray.length; i++) {{ totalTypedChars += typedWordsArray[i].length + 1; if (typedWordsArray[i] !== referenceText[i]) totalErrors++; }}
                    let grossWPM = Math.round((totalTypedChars / 5) / timeElapsedInMinutes); let netWPM = Math.max(0, Math.round(grossWPM - (totalErrors / timeElapsedInMinutes))); let accuracy = Math.max(0, Math.round(((typedWordsArray.length - totalErrors) / typedWordsArray.length) * 100));
                    document.getElementById("main-app").innerHTML = `<h2 style="color:#2e7d32; text-align:center;">Test Submitted!</h2><div style="text-align:center; padding:20px; background:#e8f5e9; border-radius:8px;"><h3>Net WPM: ${{netWPM}}</h3><h3>Accuracy: ${{accuracy}}%</h3></div>`;
                    fetch("{supabase_url}/rest/v1/competition_enrollments", {{ method: "POST", headers: {{ "Content-Type": "application/json", "apikey": "{supabase_key}", "Authorization": "Bearer {supabase_key}" }}, body: JSON.stringify({{ unique_code: "{unique_code}", competition_slug: "{comp_slug}", typing_wpm: netWPM, typing_accuracy: accuracy }}) }});
                }}
            </script>
        </body></html>
        """
        components.html(html_code, height=600)

    # ==========================================
    # ROUTE 3: ESSAY, DEBATE, ETC. (PDF UPLOAD)
    # ==========================================
    else:
        if not has_attempted:
            st.warning("'प्रारंभ' पर क्लिक करने के बाद, आपका समय शुरू हो जाएगा। / Once you click 'Start', your timer will begin.")
            if st.button("प्रतियोगिता प्रारंभ करें / Start Competition"):
                supabase.table("competition_enrollments").insert({"unique_code": unique_code, "competition_slug": comp_slug}).execute()
                st.rerun()
        else:
            start_time_str = enroll_check.data[0]['start_time']
            start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            end_time_val = start_time + timedelta(minutes=comp_details["time_limit_mins"])
            now_utc = datetime.now(timezone.utc)
            
            time_left = end_time_val - now_utc
            minutes_left = int(time_left.total_seconds() // 60)
            
            if now_utc >= end_time_val:
                st.error("आपका समय समाप्त हो गया है! प्रस्तुतियाँ अब बंद कर दी गई हैं।")
            else:
                st.info(f"⏳ **शेष समय:** लगभग {minutes_left} मिनट।")
                st.divider()
                st.subheader("प्रश्न पत्र / Question Paper")
                st.markdown(f"**[📄 प्रश्न पत्र देखने/डाउनलोड करने के लिए यहाँ क्लिक करें]({comp_details['question']})**")
                st.divider()
                
                uploaded_file = st.file_uploader("अपनी अंतिम उत्तर फ़ाइल अपलोड करें (PDF, DOC, DOCX, JPG, JPEG)", type=["pdf", "doc", "docx", "jpg", "jpeg"])
                if uploaded_file is not None:
                    if st.button("दस्तावेज़ जमा करें / Submit Document"):
                        with st.spinner("अपलोड हो रहा है..."):
                            try:
                                file_ext = uploaded_file.name.split(".")[-1]
                                file_path = f"{unique_code}_{comp_slug}.{file_ext}"
                                supabase.storage.from_("competition_documents").upload(file_path, uploaded_file.getvalue(), file_options={"x-upsert": "true"})
                                file_url = supabase.storage.from_("competition_documents").get_public_url(file_path)
                                supabase.table("competition_enrollments").update({"file_url": file_url}).eq("unique_code", unique_code).eq("competition_slug", comp_slug).execute()
                                st.success("फ़ाइल सफलतापूर्वक अपलोड की गई!")
                            except Exception as e:
                                st.error(f"अपलोड विफल: {e}")
