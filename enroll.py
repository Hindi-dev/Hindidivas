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
        "time_limit_mins": 20,
        "competition_date": "2026-08-30",
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
        "competition_date": "2026-08-27", # यदि अभी टेस्ट कर रहे हैं तो इसे "2026-08-27" कर लें
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
# --- हिंदी मुहावरें, लोकोक्तियां एवं प्रशासनिक शब्दावली MCQ प्रश्न सेट ---

IDIOMS_QUESTIONS = [
    {
        "q": "1. अपनी डफली अपना राग",
        "options": ["स्वतंत्र होना", "अपना दुखड़ा रोना", "संगठन का अभाव", "सबका अपने-अपने मन के अनुसार चलना"],
        "ans": "सबका अपने-अपने मन के अनुसार चलना"
    },
    {
        "q": "2. कोई इर घाट तो कोई बीर घाट",
        "options": ["बार-बार कथन बदलना", "ताल-मेल ना होना", "तितर-बितर होना", "बहुत चालाक होना"],
        "ans": "ताल-मेल ना होना"
    },
    {
        "q": "3. गए थे रोजा छुड़ाने ,नमाज गले पड़ी",
        "options": ["मुश्किल में पड़ जाना", "कष्ट पहुँचाना", "गरीब हो जाना", "उपकार करने के बदले स्वयं दुख भोगना पड़ा"],
        "ans": "उपकार करने के बदले स्वयं दुख भोगना पड़ा"
    },
    {
        "q": "4. फिसल पड़े तो हर गंगे",
        "options": ["मजबूरी में काम करना", "नुकसान उठाना", "एक साथ दो काम", "विपत्ति पड़ने पर ईश्वर का स्मरण करना"],
        "ans": "मजबूरी में काम करना"
    },
    {
        "q": "5. अंग–अंग खिल उठना",
        "options": ["बहुत प्रसन्न होना", "खिल उठना", "बहुत क्रोधित होना", "बहुत चिल्लाना"],
        "ans": "बहुत प्रसन्न होना"
    },
    {
        "q": "6. हँसुए के ब्याह में खुरपी का गीत",
        "options": ["शादी का गीत गाना", "जश्न मनाना", "असंगत बातें करना", "निचले स्तर का कार्य करना"],
        "ans": "असंगत बातें करना"
    },
    {
        "q": "7. आसमान पर चढ़ाना",
        "options": ["अत्यधिक  अभिमान करना", "कठिन काम के लिए  प्रेरित करना", "बहुत शोर करना", "अत्यघिक प्रशंसा करना"],
        "ans": "अत्यघिक प्रशंसा करना"
    },
    {
        "q": "8. प्रवर समिति",
        "options": ["High power committee", "low power committee", "select committee", "selection committee"],
        "ans": "select committee"
    },
    {
        "q": "9. सिर हथेली पर रखना",
        "options": ["वीरता का प्रदर्शन करना", "पराजय स्वीकार कर लेना", "मरने के तैयार होना", "अहं का विसर्जन करना"],
        "ans": "मरने के तैयार होना"
    },
    {
        "q": "10. मुँह का निवाला होना",
        "options": ["स्वादिष्ट एवं प्रियकर", "बहुत आसान काम", "अत्यंत प्रिय", "बहुत कठिन काम"],
        "ans": "बहुत आसान काम"
    },
    {
        "q": "11. अगर-मगर करना",
        "options": ["इधर की बात उधर करना", "कपट करना", "व्यर्थ समय गँवाना", "बहाने बनाना"],
        "ans": "बहाने बनाना"
    },
    {
        "q": "12. सर्वोत्तम सेवा",
        "options": ["best work", "best services", "worst work", "worst service"],
        "ans": "best services"
    },
    {
        "q": "13. सूचनार्थ",
        "options": ["for information", "for action", "for perusal", "for submission"],
        "ans": "for information"
    },
    {
        "q": "14. के अनुपालन में",
        "options": ["in consultation", "in pursuance of", "in exercise of", "in obedience of"],
        "ans": "in pursuance of"
    },
    {
        "q": "15. आपके अनुमोदन की प्रत्याशा में",
        "options": ["in reply of your approval", "for information of your approval", "in anticipation of your approval", "in submission of your approval"],
        "ans": "in anticipation of your approval"
    },
    {
        "q": "16. कृपया इसे सर्वथा गोपनीय समझा जाए ।",
        "options": ["please treat this as strictly common", "please treat this as very common", "please treat this as strictly confidential", "please treat this as strictly convenient"],
        "ans": "please treat this as strictly confidential"
    },
    {
        "q": "17. आवश्यक कार्रवाई करने के लिए",
        "options": ["for doing urgent work", "for doing urgent action", "for doing the needful", "for doing the immediate action"],
        "ans": "for doing the needful"
    },
    {
        "q": "18. आगे की प्रगति से अवगत कराएँ।",
        "options": ["inform further development", "advise further development", "advise earlier development", "notice further development"],
        "ans": "advise further development"
    },
    {
        "q": "19. Data entry operator",
        "options": ["आंकड़ा प्रविष्ठि चालक", "आंकड़ा प्रविष्ठि प्रचालक", "डाटा प्रविष्टि प्रचालक", "आंकड़ा प्रविष्टि प्रचालक"],
        "ans": "आंकड़ा प्रविष्टि प्रचालक"
    },
    {
        "q": "20. debarred from the benefit",
        "options": ["लाभ से वंचित", "हितलाभ से वर्जित", "लाभ से विवर्जित", "हितलाभ से विवर्जित"],
        "ans": "लाभ से वंचित"
    },
    {
        "q": "21. commutation of pension",
        "options": ["पेंशन का राशीकरण", "पेंशन की वृद्धि", "पेंशन की कटौती", "पेंशन का संराशीकरण"],
        "ans": "पेंशन का संराशीकरण"
    },
    {
        "q": "22. attested true copy",
        "options": ["प्रमाणित ठीक प्रतिलिपि", "प्रमाणित सत्य प्रति", "अनुप्रमाणित उचित प्रति", "अनुप्रमाणित सही प्रतिलिपि"],
        "ans": "अनुप्रमाणित सही प्रतिलिपि"
    },
    {
        "q": "23. इंद्र का अखाड़ा",
        "options": ["बहुत अच्छी जगह", "बहुत अलग जगह", "नाचने का स्थान", "ऐश- मौज की जगह"],
        "ans": "ऐश- मौज की जगह"
    },
    {
        "q": "24. हाथ ऊंचा होना",
        "options": ["युद्ध में विजय प्राप्त कर लेना", "दान आदि के लिए मन में उदारता का भाव", "अत्यधिक प्रतिष्ठित", "किसी को मारने के लिए हाथ उठाना"],
        "ans": "दान आदि के लिए मन में उदारता का भाव"
    },
    {
        "q": "25. तीन लोक से मथुरा न्यारी",
        "options": ["बहुत सुंदर होना", "दूर की वस्तु सुंदर लगना", "सबसे निराला स्थान", "कृष्ण भक्त होना"],
        "ans": "सबसे निराला स्थान"
    },
    {
        "q": "26. temporary appointment",
        "options": ["स्थायी नियुक्ति", "अस्थायी प्रतिनियुक्ति", "अस्थायी नियुक्ति"],
        "ans": "अस्थायी नियुक्ति"
    },
    {
        "q": "27. विहंगम दृष्टि",
        "options": ["सरसरी दृष्टि", "गहरी दृष्टि", "सम्यक् दृष्टि", "पैनी दृष्टि"],
        "ans": "सरसरी दृष्टि"
    },
    {
        "q": "28. the file in question is not traceable",
        "options": ["प्रश्न वाली फाइल नही मिल रही है", "उपेक्षित फाइल खो गई है", "अपेक्षित फाइल नहीं मिल रही है", "संदर्भित फाइल नहीं मिल रही है"],
        "ans": "संदर्भित फाइल नहीं मिल रही है"
    },
    {
        "q": "29. निष्पादन लेखापरीक्षा",
        "options": ["assessment audit", "excess audit", "performance audit", "compliance audit"],
        "ans": "performance audit"
    },
    {
        "q": "30. provisional assessment",
        "options": ["अंतरिम नियतन", "अंतिम निर्धारण", "अनंतिम निर्धारण", "अंतरिम निर्धारण"],
        "ans": "अनंतिम निर्धारण"
    },
    {
        "q": "31. under one's hand",
        "options": ["अपने हाथ से", "अपनी क्षमता अनुसार", "अपनी मुहर से", "अपने हस्ताक्षर सहित"],
        "ans": "अपने हस्ताक्षर सहित"
    },
    {
        "q": "32. on probation",
        "options": ["प्रतिनियुक्ति पर", "नियुक्ति पर", "परिवीक्षाधीन", "जमानत पर"],
        "ans": "परिवीक्षाधीन"
    },
    {
        "q": "33. overall position",
        "options": ["सही स्थिति", "उचित स्थिति", "समग्र स्थिति"],
        "ans": "समग्र स्थिति"
    },
    {
        "q": "34. नगर राजभाषा कार्यान्वयन समिति",
        "options": ["Town official language implementation committee", "Town rajbhasha implement committee", "committee for official language", "town official performance committee"],
        "ans": "Town official language implementation committee"
    },
    {
        "q": "35. Draft for approval",
        "options": ["अनुमोदन हेतु मसौदा", "अवलोकन  हेतु मसौदा", "आदेश हेतु मसौदा"],
        "ans": "अनुमोदन हेतु मसौदा"
    },
    {
        "q": "36. Circulate and then file",
        "options": ["फाइल कर दीजिए", "संबद्धित व्यक्तियों को दिखाकर फाइल कर दीजिए", "घुमाकर फाइल कर दीजिए"],
        "ans": "संबद्धित व्यक्तियों को दिखाकर फाइल कर दीजिए"
    },
    {
        "q": "37. sanctioned budget",
        "options": ["अनुमोदित बजट", "समेकित बजट", "परिकल्पित बजट", "संस्वीकृत बजट"],
        "ans": "संस्वीकृत बजट"
    },
    {
        "q": "38. service sheet",
        "options": ["सेवा शीट", "सेवा पत्र", "सेवा क्रम", "सेवा रोल"],
        "ans": "सेवा पत्र"
    },
    {
        "q": "39. seniority-cum-merit",
        "options": ["वरिष्ठता कम मैरिट", "वरिष्ठता कम योग्यता", "वरिष्ठता सह योग्यताक्रम", "वरिष्ठता सह योग्यता"],
        "ans": "वरिष्ठता सह योग्यता"
    },
    {
        "q": "40. अनिवार्य अर्हता",
        "options": ["necessary requirement", "mandatory qualification", "essential qualification", "essential requirement"],
        "ans": "essential qualification"
    },
    {
        "q": "41. प्रशासनिक शब्दावली में 'Post Audit' का सटीक हिन्दी पर्याय क्या है?", 
        "options": ["पूर्व लेखापरीक्षा", "पश्च लेखापरीक्षा", "बाद की लेखापरीक्षा", "अंतिम लेखापरीक्षा"],
        "ans": "पश्च लेखापरीक्षा" #[cite: 1]
    },
    {
        "q": "42. 'Piece meal clearance' के लिए सही पारिभाषिक शब्द चुनें:", 
        "options": ["आंशिक निकासी", "टुकड़ों में निकासी", "खण्डशः निकासी", "थोड़ी-थोड़ी निकासी"],
        "ans": "खण्डशः निकासी" #[cite: 1]
    },
    {
        "q": "43. 'Proforma adjustment' का अधिकृत अनुवाद क्या होगा?", 
        "options": ["प्रारूप समायोजन", "प्रोफार्मा समायोजन", "अस्थायी समायोजन", "तदर्थ समायोजन"],
        "ans": "प्रोफार्मा समायोजन" #[cite: 1]
    },
    {
        "q": "44. 'Re-appropriation' को प्रशासनिक हिन्दी में क्या कहा जाता है?", 
        "options": ["पुनर्विनियोग", "पुनरावंटन", "पुनः नियोजन", "पुर्नानयोजन"],
        "ans": "पुर्नानयोजन" #[cite: 1]
    },
    {
        "q": "45. 'Reconciliation Statement' का सही अर्थ क्या है?", 
        "options": ["मिलान विवरण", "समझौता विवरण", "समाधान विवरण", "सामंजस्य विवरण"],
        "ans": "समाधान विवरण" #[cite: 1]
    },
    {
        "q": "46. 'Self liquidating advance' के लिए सटीक शब्द कौन सा है?", 
        "options": ["स्वतः समाप्त ऋण", "स्वनिर्भर पेशगी", "स्वपरिपोषक ऋण", "स्वतः चुकाने योग्य उधार"],
        "ans": "स्वपरिपोषक ऋण" #[cite: 1]
    },
    {
        "q": "47. 'Short term capital gain' का हिन्दी पर्याय क्या है?", 
        "options": ["अल्पावधि पूंजी प्राप्ति", "अल्पकालिक पूंजी अभिलाभ", "अल्पकालिक पूंजीगत लाभ", "थोड़े समय का पूंजी लाभ"],
        "ans": "अल्पकालिक पूंजी अभिलाभ" #[cite: 1]
    },
    {
        "q": "48. 'Stores issued book' को कार्यालयीन हिन्दी में क्या कहेंगे?", 
        "options": ["निर्गत भंडार बही", "जावक भंडार बही", "जारी सामान बही", "प्रेषित भंडार बही"],
        "ans": "जावक भंडार बही" #[cite: 1]
    },
    {
        "q": "49. 'Test audit' का पारिभाषिक अर्थ क्या है?", 
        "options": ["परीक्षण लेखापरीक्षा", "जांच लेखापरीक्षा", "प्रायोगिक लेखापरीक्षा", "नमूना लेखापरीक्षा"],
        "ans": "नमूना लेखापरीक्षा" #[cite: 1]
    },
    {
        "q": "50. 'Propriety Audit' का हिन्दी में सही अनुवाद क्या है?", 
        "options": ["औचित्य लेखापरीक्षा", "संपत्ति लेखापरीक्षा", "यथार्थ लेखापरीक्षा", "उपयुक्तता लेखापरीक्षा"],
        "ans": "औचित्य लेखापरीक्षा" #[cite: 1]
    }
]

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
        
        # टाइपिंग के लिए HTML को पेज के अंदर ही चलाएं
        if comp_slug == "typing":
            st.info("👇 नीचे दिए गए बॉक्स में अपना टंकण (Typing) टेस्ट दें:")
            # --> यह नई लाइन जोड़ें <--
            st.warning("📸 **महत्वपूर्ण:** टेस्ट पूरा होने के बाद, अपने अंतिम 'स्कोर कार्ड' का स्क्रीनशॉट (Screenshot) लें और उसे नीचे दिए गए अपलोड बॉक्स में जमा करें!")
            try:
                with open("typing.html", "r", encoding="utf-8") as f:
                    html_content = f.read()
                components.html(html_content, height=600, scrolling=True)
            except FileNotFoundError:
                st.error("❌ typing.html फ़ाइल नहीं मिली!")
            
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
