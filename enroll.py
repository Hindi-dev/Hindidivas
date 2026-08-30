import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client
import datetime

# --- 1. पेज सेटिंग ---
st.set_page_config(page_title="परीक्षा पोर्टल | हिंदी पखवाड़ा 2026", page_icon="📝", layout="centered")

# --- इंटरनेट जांच बटन ---
if st.button("🌐 इंटरनेट कनेक्शन जांचें"):
    st.toast("आपका इंटरनेट सही ढंग से काम कर रहा है!", icon="✅")

st.markdown("<br>", unsafe_allow_html=True)

# --- 2. डेटाबेस कनेक्शन ---
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error("डेटाबेस से जुड़ने में त्रुटि। कृपया इंटरनेट कनेक्शन या Secrets की जांच करें।")
    st.stop()

# --- 3. 50 बहुविकल्पीय प्रश्नों की सूची (MCQs) ---
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

# --- 4. प्रतियोगिताओं की समय सारणी ---
COMPETITIONS = {
    "idioms": {
        "name": "हिंदी मुहावरें, लोकोक्तियां एवं प्रशासनिक शब्दावली",
        "time_limit_mins": 25, 
        "competition_date": "2026-08-30",
        "start_time": "15.50",
        "end_time": "16.15:", # 35 मिनट की विंडो (25 मिनट के टेस्ट के लिए)
        "is_mcq": True
    },
    # आप भविष्य में यहाँ अन्य प्रतियोगिताएं भी जोड़ सकते हैं
}

# --- 5. यूआरएल (URL) से प्रतियोगिता चेक करना ---
query_params = st.query_params
comp_slug = query_params.get("comp")

if not comp_slug or comp_slug not in COMPETITIONS:
    st.error("अमान्य प्रतियोगिता लिंक! कृपया सही लिंक का उपयोग करें।")
    st.stop()

competition_info = COMPETITIONS[comp_slug]

st.markdown(f"<h2 style='text-align: center; color: #004B87;'>{competition_info['name']}</h2>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. दिनांक और समय विंडो जांच (Time Validation) ---
# Streamlit सर्वर (UTC) के समय को भारतीय मानक समय (IST) में बदलना:
ist_offset = datetime.timedelta(hours=5, minutes=30)
now = datetime.datetime.utcnow() + ist_offset

today_str = now.strftime("%Y-%m-%d")
current_time_str = now.strftime("%H:%M")

comp_date = competition_info["competition_date"]
start_time = competition_info["start_time"]
end_time = competition_info["end_time"]

if today_str != comp_date:
    st.warning("🚫 यह प्रतियोगिता वर्तमान में बंद है। इसकी निर्धारित तिथि **{30.08.2026}** है।")
    st.stop()
else:
    if current_time_str < start_time:
        st.warning(f"⏳ **प्रतियोगिता अभी शुरू नहीं हुई है!**")
        st.info(f"यह टेस्ट आज **{start_time} बजे** से **{end_time} बजे** के बीच ही सक्रिय रहेगा।")
        st.stop()
    elif current_time_str > end_time:
        st.error(f"❌ **समय समाप्त!**")
        st.warning(f"यह प्रतियोगिता आज **{end_time} बजे** बंद हो चुकी है। अब आप इसमें भाग नहीं ले सकते।")
        st.stop()
    else:
        st.success(f"✅ प्रतियोगिता सक्रिय है। यह विंडो **{end_time} बजे** बंद हो जाएगी। कृपया 25 मिनट के भीतर टेस्ट सबमिट करें।")
# --- 7. लॉगिन और सुरक्षा जांच (Unique Code & Cheat Prevention) ---
st.markdown("### 🔑 अपना 4-अंकीय कोड दर्ज करें")
unique_code = st.text_input("पंजीकरण के समय प्राप्त कोड (Unique Code):", max_chars=4, type="password")

if unique_code:
    try:
        user_check = supabase.table("registrations").select("*").eq("unique_code", unique_code).execute()
        
        if len(user_check.data) == 0:
            st.error("❌ अमान्य कोड! कृपया सही 4-अंकीय पंजीकरण कोड दर्ज करें।")
            st.stop()
        else:
            user_data = user_check.data[0]
            
            # चेक करें कि क्या प्रतिभागी ने पहले ही टेस्ट दे दिया है
            attempt_check = supabase.table("competition_enrollments").select("*").eq("unique_code", unique_code).eq("competition_slug", comp_slug).execute()
            
            if len(attempt_check.data) > 0:
                st.error(f"🛑 क्षमा करें {user_data.get('name', 'प्रतिभागी')}!")
                st.warning("आप पहले ही इस प्रतियोगिता की उत्तर-पुस्तिका जमा कर चुके हैं। एक प्रतिभागी को केवल एक ही प्रयास (Attempt) की अनुमति है।")
                st.stop()
            else:
                st.info(f"स्वागत है, **{user_data.get('name', 'प्रतिभागी')}**! आपके पास 50 प्रश्नों के लिए 25 मिनट हैं। **प्रत्येक गलत उत्तर के लिए 0.25 अंक काटे जाएंगे (Negative Marking)।**")
                
    except Exception as e:
        st.error(f"सत्यापन में त्रुटि: {e}")
        st.stop()

    # --- 8. परीक्षा फॉर्म (MCQ Section) ---
    st.markdown("---")
    st.markdown("### 📝 बहुविकल्पीय प्रश्न (MCQs)")
    
    # --- 🚀 नया लाइव टाइमर (ऑटो-सबमिट फीचर के साथ) ---
    timer_html = f"""
    <div id="timer-container" style="background-color: #E3F2FD; border: 3px solid #2196F3; border-radius: 12px; padding: 15px; text-align: center; font-family: Arial, sans-serif; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 10px;">
        <h3 style="margin: 0; color: #004B87; font-size: 20px;">⏳ समय शेष (Time Remaining)</h3>
        <div id="clock" style="font-size: 38px; font-weight: bold; color: #333; margin: 10px 0;">--:--</div>
        <div id="alert-msg" style="color: #D32F2F; font-weight: bold; font-size: 18px; display: none; margin: 0; animation: blinker 1s linear infinite;">
            ⚠️ अंतिम 1 मिनट शेष! कृपया तुरंत अपना टेस्ट सबमिट करें!
        </div>
    </div>
    <style>
        @keyframes blinker {{
            50% {{ opacity: 0; }}
        }}
    </style>
    <script>
        var endTimeStr = "{end_time}"; 
        var now = new Date();
        var parts = endTimeStr.split(":");
        var countDownDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), parseInt(parts[0]), parseInt(parts[1]), 0).getTime();

        var x = setInterval(function() {{
            var nowTime = new Date().getTime();
            var distance = countDownDate - nowTime;

            // समय समाप्त होने पर ऑटो-सबमिट लॉजिक
            if (distance <= 0) {{
                clearInterval(x);
                document.getElementById("clock").innerHTML = "00:00";
                document.getElementById("timer-container").style.backgroundColor = "#FFEBEE";
                document.getElementById("timer-container").style.borderColor = "#D32F2F";
                document.getElementById("alert-msg").innerHTML = "⏳ समय समाप्त! आपका टेस्ट ऑटो-सबमिट हो रहा है...";
                document.getElementById("alert-msg").style.display = "block";
                document.getElementById("alert-msg").style.animation = "none";
                
                // स्ट्रीमलिट के मेन पेज पर सबमिट बटन को खोजकर ऑटो-क्लिक करना
                var buttons = window.parent.document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {{
                    if (buttons[i].innerText.includes('अपना टेस्ट जमा करें')) {{
                        buttons[i].click();
                        break;
                    }}
                }}
                return;
            }}

            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);

            var m = minutes < 10 ? "0" + minutes : minutes;
            var s = seconds < 10 ? "0" + seconds : seconds;

            document.getElementById("clock").innerHTML = m + ":" + s;

            if (distance <= 60000) {{
                document.getElementById("timer-container").style.backgroundColor = "#FFCDD2";
                document.getElementById("timer-container").style.borderColor = "#D32F2F";
                document.getElementById("clock").style.color = "#D32F2F";
                document.getElementById("alert-msg").style.display = "block";
            }}
        }}, 1000);
    </script>
    """
    
    components.html(timer_html, height=170)
    
    # टाइमर को स्क्रीन पर दिखाना (height=170 सुनिश्चित करता है कि बॉक्स पूरा दिखे)
    components.html(timer_html, height=170)

    # --- इसके नीचे आपका पुराना फॉर्म वाला कोड रहेगा ---
    # --- इसके ऊपर आपका JavaScript टाइमर वाला कोड रहेगा ---
    
    with st.form("mcq_quiz_form"):
        user_answers = {}
        
        for i, q_data in enumerate(IDIOMS_QUESTIONS):
            st.markdown(f"**{q_data['q']}**")
            user_answers[i] = st.radio(
                f"Select {i}", 
                q_data['options'], 
                key=f"q_{i}", 
                index=None, 
                label_visibility="collapsed"
            )
            st.markdown("<hr style='margin: 10px 0; border: 0.5px solid #e0e0e0;'>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ⚠️ यह लाइन बहुत ज़रूरी है, यहीं से 'submitted' बनता है
        submitted = st.form_submit_button("✅ अपना टेस्ट जमा करें (Submit Test)", use_container_width=True)
        
        # --- 9. मार्किंग और डेटाबेस में सुरक्षित करना ---
        # ⚠️ ध्यान दें: यह 'if submitted:' फॉर्म के अंदर (Indented) होना चाहिए
        if submitted:
            correct_answers = 0
            wrong_answers = 0
            unanswered = 0
            
            for i, q_data in enumerate(IDIOMS_QUESTIONS):
                user_ans = user_answers[i]
                if user_ans == q_data['ans']:
                    correct_answers += 1
                elif user_ans is not None:
                    wrong_answers += 1
                else:
                    unanswered += 1
            
            negative_marks = wrong_answers * 0.25
            final_score = correct_answers - negative_marks
            
            # डेटाबेस में सेव करें
            with st.spinner("आपका परिणाम सुरक्षित किया जा रहा है..."):
                try:
                    supabase.table("competition_enrollments").insert({
                        "unique_code": unique_code,
                        "competition_slug": comp_slug,
                        "score": final_score,
                        "correct_answers": correct_answers,
                        "wrong_answers": wrong_answers,
                        "unanswered": unanswered
                    }).execute()
                    
                    st.success("✅ आपका परिणाम सुरक्षित रूप से एडमिन के पास दर्ज कर लिया गया है!")
                except Exception as e:
                    st.error(f"स्कोर सेव करने में तकनीकी त्रुटि: {e}")
                    st.stop()
            
            # स्कोरकार्ड दिखाना
            st.markdown("### 📊 आपका परीक्षा परिणाम:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"✅ **सही उत्तर:** {correct_answers}")
            with col2:
                st.error(f"❌ **गलत उत्तर:** {wrong_answers}")
            with col3:
                st.warning(f"⚪ **छोड़े गए:** {unanswered}")
                
            st.markdown(f"**काटे गए अंक (Negative Marks):** -{negative_marks}")
            st.markdown(f"### 🏆 आपका अंतिम स्कोर: **{final_score} / {len(IDIOMS_QUESTIONS)}**")
            
            st.balloons()
            st.stop()
