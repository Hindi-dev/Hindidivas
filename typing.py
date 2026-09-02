import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client
import datetime

# --- 1. पेज सेटिंग ---
st.set_page_config(page_title="हिंदी टाइपिंग प्रतियोगिता 2026", page_icon="⌨️", layout="centered")

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

# --- 3. प्रतियोगिता की समय सारणी ---
COMPETITIONS = {
    "typing": {
        "name": "हिंदी टाइपिंग प्रतियोगिता (Inscript Layout)",
        "time_limit_mins": 20, 
        "competition_date": "2026-09-02",  # अपनी आवश्यकतानुसार तारीख बदलें
        "start_time": "15:05",             # शुरू होने का समय
        "end_time": "15:25"                # 30 मिनट की विंडो
    }
}

# --- 4. यूआरएल (URL) से प्रतियोगिता चेक करना (उदा: ?comp=typing) ---
query_params = st.query_params
comp_slug = query_params.get("comp", "typing") # डिफ़ॉल्ट रूप से 'typing' सेट किया है

if comp_slug not in COMPETITIONS:
    st.error("अमान्य प्रतियोगिता लिंक!")
    st.stop()

competition_info = COMPETITIONS[comp_slug]
st.markdown(f"<h2 style='text-align: center; color: #004B87;'>⌨️ {competition_info['name']}</h2><hr>", unsafe_allow_html=True)

# --- 5. दिनांक और समय विंडो जांच (IST) ---
ist_offset = datetime.timedelta(hours=5, minutes=30)
now = datetime.datetime.utcnow() + ist_offset

today_str = now.strftime("%Y-%m-%d")
current_time_str = now.strftime("%H:%M")

comp_date = competition_info["competition_date"]
start_time = competition_info["start_time"]
end_time = competition_info["end_time"]

if today_str != comp_date:
    st.warning(f"🚫 यह प्रतियोगिता वर्तमान में बंद है। इसकी निर्धारित तिथि **{comp_date}** है।")
    st.stop()
elif current_time_str < start_time:
    st.warning(f"⏳ **प्रतियोगिता अभी शुरू नहीं हुई है!**")
    st.info(f"यह टेस्ट आज **{start_time} बजे** से **{end_time} बजे** के बीच ही सक्रिय रहेगा।")
    st.stop()
elif current_time_str > end_time:
    st.error(f"❌ **समय समाप्त!**")
    st.warning(f"यह प्रतियोगिता आज **{end_time} बजे** बंद हो चुकी है। अब आप इसमें भाग नहीं ले सकते।")
    st.stop()
else:
    st.success(f"✅ प्रतियोगिता सक्रिय है। कृपया लॉगिन करें।")

# --- 6. लॉगिन और सुरक्षा जांच ---
st.markdown("### 🔑 अपना 4-अंकीय कोड दर्ज करें")
unique_code = st.text_input("पंजीकरण के समय प्राप्त कोड (Unique Code):", max_chars=4, type="password")

if unique_code:
    try:
        # कोड की जांच करें
        user_check = supabase.table("registrations").select("*").eq("unique_code", unique_code).execute()
        if len(user_check.data) == 0:
            st.error("❌ अमान्य कोड!")
            st.stop()
            
        # चेक करें कि क्या पहले टेस्ट दे चुका है
        attempt_check = supabase.table("competition_enrollments").select("*").eq("unique_code", unique_code).eq("competition_slug", comp_slug).execute()
        if len(attempt_check.data) > 0:
            st.error("🛑 आप पहले ही यह टाइपिंग टेस्ट जमा कर चुके हैं!")
            st.stop()
            
        user_name = user_check.data[0].get('name', 'प्रतिभागी')
        st.info(f"स्वागत है **{user_name}**! नीचे दिए गए बॉक्स में टाइप करना शुरू करते ही आपका 20 मिनट का समय शुरू हो जाएगा।")
        
    except Exception as e:
        st.error(f"सत्यापन में त्रुटि: {e}")
        st.stop()

    # --- 7. आपका HTML टाइपिंग टेस्ट (Streamlit में एम्बेड) ---
    
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    
    # आपका ओरिजिनल HTML कोड (लॉगिन स्क्रीन को छिपाकर और ऑटो-सेव API लगाकर)
    html_code = f"""
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <title>20-Minute Hindi Typing Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 0; margin: 0; background-color: #f4f6f8; overflow-x: hidden; }}
            .container {{ max-width: 900px; margin: auto; padding: 10px; }}
            #login-screen {{ display: none !important; }} /* लॉगिन स्क्रीन छिपा दी गई है क्योंकि स्ट्रीमलिट लॉगिन कर रहा है */
            #main-app {{ display: block; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 10px; }}
            .header {{ display: flex; justify-content: space-between; margin-bottom: 20px; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 15px; }}
            .candidate-info {{ font-size: 18px; font-weight: bold; color: #555; }}
            .layout-info {{ font-size: 16px; font-weight: bold; color: #666; background: #e0f7fa; padding: 6px 12px; border-radius: 4px; }}
            .timer-container {{ display: flex; align-items: center; }}
            #timer {{ font-size: 28px; font-weight: bold; color: #d32f2f; margin-left:15px; }}
            
            #text-display {{ 
                font-size: 22px; line-height: 1.8; padding: 15px; border: 1px solid #ccc; 
                border-radius: 5px; margin-bottom: 20px; background: #f9f9f9; user-select: none; 
                display: flex; flex-wrap: wrap; gap: 5px; height: 160px; overflow-y: hidden; position: relative;
            }}
            .word {{ padding: 2px 4px; border-radius: 3px; transition: background 0.2s; }}
            .current-word {{ background-color: #e0f7fa; font-weight: bold; border-bottom: 3px solid #00acc1; }}
            .correct {{ color: #2e7d32; }}
            .incorrect {{ color: #d32f2f; text-decoration: underline; background-color: #ffebee; }}
            
            #input-box {{ width: 100%; font-size: 22px; padding: 12px; box-sizing: border-box; border: 2px solid #00acc1; border-radius: 5px; outline: none; }}
            #input-box:disabled {{ background: #eeeeee; border-color: #cccccc; cursor: not-allowed; }}
            .submit-btn {{ background:#d32f2f; color:white; border:none; padding: 10px 15px; font-size:16px; border-radius:5px; cursor:pointer; display:none; }}
            
            #results-screen {{ display: none; flex-direction: column; align-items: center; justify-content: center; padding: 40px 0; background: #f4f6f8; }}
            .results-card {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.15); width: 100%; max-width: 700px; text-align: center; }}
            .results-title {{ font-size: 32px; color: #2e7d32; margin-top: 0; margin-bottom: 10px; }}
            .metrics-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }}
            .metric-box {{ background: #e8f5e9; padding: 20px; border-radius: 8px; border: 1px solid #c8e6c9; }}
            .metric-title {{ font-size: 18px; color: #555; }}
            .metric-value {{ font-size: 42px; font-weight: bold; color: #2e7d32; margin-top: 10px; }}
            .balloon {{ position: absolute; bottom: -120px; width: 50px; height: 70px; background-color: red; border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%; opacity: 0.9; z-index: 1000; animation: floatUp linear forwards; }}
            .balloon::before {{ content: ""; position: absolute; width: 2px; height: 60px; background: #999; top: 70px; left: 24px; }}
            @keyframes floatUp {{ 0% {{ transform: translateY(0) rotate(0deg); }} 100% {{ transform: translateY(-120vh) rotate(15deg); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div id="main-app">
                <div class="header">
                    <div class="candidate-info">ID: <span id="display-candidate-id" style="color: #00acc1;">{unique_code}</span></div>
                    <div class="layout-info">Layout: Hindi Inscript</div>
                    <div class="timer-container">
                        <button id="submit-btn" class="submit-btn" onclick="endTest()">Submit Early</button>
                        <div id="timer">20:00</div>
                    </div>
                </div>
                <div id="text-display"></div>
                <input type="text" id="input-box" placeholder="यहाँ टाइप करना शुरू करें (Start typing here)..." autocomplete="off">
            </div>
        </div>

        <div id="results-screen">
            <div class="results-card">
                <h1 class="results-title">Test Submitted!</h1>
                <p style="color:#555; font-size:18px; font-weight:bold;">✅ आपका स्कोर सफलतापूर्वक डेटाबेस में सुरक्षित कर लिया गया है।</p>
                <div class="metrics-grid">
                    <div class="metric-box"><div class="metric-title">Gross WPM</div><div class="metric-value" id="gross-wpm">0</div></div>
                    <div class="metric-box"><div class="metric-title">Net WPM</div><div class="metric-value" id="net-wpm">0</div></div>
                    <div class="metric-box"><div class="metric-title">Accuracy</div><div class="metric-value"><span id="accuracy">0</span>%</div></div>
                </div>
            </div>
        </div>

    <script>
        // Anti-Cheat (कॉपी-पेस्ट रोकना)
        document.addEventListener('contextmenu', e => e.preventDefault());
        document.addEventListener('copy', e => e.preventDefault());
        document.addEventListener('paste', e => e.preventDefault());

        let candidateID = "{unique_code}";
        const corpus = `भारत का इतिहास बहुत समृद्ध और प्राचीन है। यह सिंधु घाटी सभ्यता से शुरू होता है, जो दुनिया की सबसे पुरानी सभ्यताओं में से एक है। भारतीय संविधान दुनिया का सबसे लंबा लिखित संविधान है, जिसे २६ जनवरी १९५० को लागू किया गया था। इसमें नागरिकों के मौलिक अधिकारों और कर्तव्यों का स्पष्ट वर्णन है। भौगोलिक दृष्टि से, भारत विविधताओं वाला देश है। इसके उत्तर में विशाल हिमालय पर्वत श्रृंखला है, जो देश को ठंडी हवाओं से बचाती है। दक्षिण में विशाल हिंद महासागर है। गंगा, यमुना, गोदावरी, और नर्मदा जैसी नदियाँ कृषि के लिए जीवनदायिनी हैं। आधुनिक युग में, भारतीय अंतरिक्ष अनुसंधान संगठन (इसरो) ने अंतरिक्ष विज्ञान के क्षेत्र में अभूतपूर्व प्रगति की है। चंद्रयान और मंगलयान मिशन भारत की वैज्ञानिक क्षमता के उत्कृष्ट उदाहरण हैं। कृषि आज भी भारतीय अर्थव्यवस्था की रीढ़ है, जहाँ लगभग ५० प्रतिशत से अधिक आबादी प्रत्यक्ष या अप्रत्यक्ष रूप से खेती पर निर्भर है। सूचना प्रौद्योगिकी (आईटी) के क्षेत्र में भी भारत ने वैश्विक स्तर पर अपनी पहचान बनाई है। विविधता में एकता भारत की सबसे बड़ी ताकत है। यहाँ विभिन्न धर्मों, जातियों, और भाषाओं के लोग एक साथ शांतिपूर्ण तरीके से रहते हैं। हमें अपने देश की अखंडता और संप्रभुता की रक्षा के लिए हमेशा तत्पर रहना चाहिए। शिक्षा, स्वास्थ्य, और रोजगार के क्षेत्र में निरंतर विकास ही एक सशक्त राष्ट्र के निर्माण का मार्ग प्रशस्त करेगा।`;

        function generateTestPassage(targetWordCount) {{
            const baseWords = corpus.replace(/\\n/g, ' ').trim().split(/\s+/).filter(w => w.length > 0);
            let testWords = [];
            while (testWords.length < targetWordCount) testWords = testWords.concat(baseWords);
            return testWords.slice(0, targetWordCount);
        }}

        let referenceText = generateTestPassage(1500);
        let TIME_LIMIT = 1200; 
        let timeLeft = TIME_LIMIT;
        let timerInterval = null;
        let testActive = false;
        let currentWordIndex = 0;
        let typedWordsArray = []; 

        const displayEl = document.getElementById("text-display");
        const inputEl = document.getElementById("input-box");
        const timerEl = document.getElementById("timer");

        function renderText() {{
            displayEl.innerHTML = referenceText.map((word, index) => 
                `<span class="word ${{index === 0 ? 'current-word' : ''}}" id="word-${{index}}">${{word}}</span>`
            ).join("");
        }}
        renderText();

        function scrollToCurrentWord() {{
            const activeWordEl = document.getElementById(`word-${{currentWordIndex}}`);
            if (activeWordEl) activeWordEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}

        const inscriptMap = {{
            "q": "ौ", "Q": "औ", "w": "ै", "W": "ऐ", "e": "ा", "E": "आ", "r": "ी", "R": "ई",
            "t": "ू", "T": "ऊ", "y": "ब", "Y": "भ", "u": "ह", "U": "ङ", "i": "ग", "I": "घ",
            "o": "द", "O": "ध", "p": "ज", "P": "झ", "[": "ड", "{{": "ढ", "]": "़", "}}": "ञ",
            "a": "ो", "A": "ओ", "s": "े", "S": "ए", "d": "्", "D": "अ", "f": "ि", "F": "इ",
            "g": "ु", "G": "उ", "h": "प", "H": "फ", "j": "र", "J": "ऱ", "k": "क", "K": "ख",
            "l": "त", "L": "थ", ";": "च", ":": "छ", "'": "ट", "\\"": "ठ", "z": "े", "Z": "ॆ",
            "x": "ं", "X": "ँ", "c": "म", "C": "ण", "v": "न", "V": "ऩ", "b": "व", "B": "ऴ",
            "n": "ल", "N": "ळ", "m": "स", "M": "श", ",": ",", "<": "ष", ".": ".", ">": "।",
            "/": "य", "?": "य़", "1": "१", "2": "२", "3": "३", "4": "४", "5": "५", 
            "6": "६", "7": "७", "8": "८", "9": "९", "0": "०"
        }};

        inputEl.addEventListener("keydown", function(e) {{
            if (e.ctrlKey && (e.key === 'c' || e.key === 'v')) {{ e.preventDefault(); return; }}

            if (!testActive && timeLeft === TIME_LIMIT && e.key.length === 1) {{
                startTimer();
                testActive = true;
                document.getElementById("submit-btn").style.display = "inline-block";
            }}

            if (inscriptMap[e.key]) {{
                e.preventDefault(); 
                const start = this.selectionStart;
                const end = this.selectionEnd;
                const text = this.value;
                this.value = text.slice(0, start) + inscriptMap[e.key] + text.slice(end);
                this.selectionStart = this.selectionEnd = start + 1;
            }}
        }});

        inputEl.addEventListener("keyup", function(e) {{
            if (e.key === " ") {{
                let typedWord = this.value.trim(); 
                if (typedWord === "") {{ this.value = ""; return; }}

                typedWordsArray.push(typedWord);
                const targetWord = referenceText[currentWordIndex];
                const wordSpan = document.getElementById(`word-${{currentWordIndex}}`);

                if (typedWord === targetWord) {{ wordSpan.classList.add("correct"); }} 
                else {{ wordSpan.classList.add("incorrect"); }}

                wordSpan.classList.remove("current-word");
                currentWordIndex++;
                this.value = ""; 

                if (currentWordIndex < referenceText.length) {{
                    document.getElementById(`word-${{currentWordIndex}}`).classList.add("current-word");
                    scrollToCurrentWord();
                }} else {{ endTest(); }}
            }} 
        }});

        function startTimer() {{
            timerInterval = setInterval(() => {{
                timeLeft--;
                let minutes = Math.floor(timeLeft / 60);
                let seconds = timeLeft % 60;
                timerEl.innerText = `${{minutes}}:${{seconds < 10 ? '0' : ''}}${{seconds}}`;
                if (timeLeft <= 0) endTest();
            }}, 1000);
        }}

        function endTest() {{
            clearInterval(timerInterval);
            inputEl.disabled = true;
            testActive = false;

            const finalWord = inputEl.value.trim();
            if (finalWord) typedWordsArray.push(finalWord);

            let timeElapsedInMinutes = (TIME_LIMIT - timeLeft) / 60;
            let grossWPM = 0, netWPM = 0, accuracy = 0;

            if (timeElapsedInMinutes > 0 && typedWordsArray.length > 0) {{
                let totalTypedChars = 0;
                let totalErrors = 0;

                for (let i = 0; i < typedWordsArray.length; i++) {{
                    let typed = typedWordsArray[i];
                    let target = referenceText[i] || "";
                    totalTypedChars += typed.length + 1; 
                    if (typed !== target) totalErrors++; 
                }}

                grossWPM = Math.round((totalTypedChars / 5) / timeElapsedInMinutes);
                netWPM = Math.round(grossWPM - (totalErrors / timeElapsedInMinutes));
                let correctWords = typedWordsArray.length - totalErrors;
                accuracy = Math.round((correctWords / typedWordsArray.length) * 100);
            }}
            
            document.getElementById("gross-wpm").innerText = grossWPM;
            document.getElementById("net-wpm").innerText = Math.max(0, netWPM); 
            document.getElementById("accuracy").innerText = Math.max(0, accuracy);
            
            // --- Supabase API: रिजल्ट को सीधे डेटाबेस में भेजना ---
            fetch("{supabase_url}/rest/v1/competition_enrollments", {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json",
                    "apikey": "{supabase_key}",
                    "Authorization": "Bearer {supabase_key}",
                    "Prefer": "return=minimal"
                }},
                body: JSON.stringify({{
                    unique_code: "{unique_code}",
                    competition_slug: "{comp_slug}",
                    typing_wpm: Math.max(0, netWPM),
                    typing_accuracy: Math.max(0, accuracy)
                }})
            }})
            .then(response => console.log("Score Saved Successfully!"))
            .catch(error => console.error("Database Error:", error));
            
            // स्क्रीन बदलना और गुब्बारे उड़ाना
            document.getElementById("main-app").style.display = "none";
            document.getElementById("results-screen").style.display = "flex";
            releaseBalloons();
        }}

        function releaseBalloons() {{
            const colors = ['#e57373', '#81c784', '#64b5f6', '#fff176', '#ba68c8', '#ffb74d', '#4db6ac'];
            for (let i = 0; i < 35; i++) {{
                let balloon = document.createElement('div');
                balloon.classList.add('balloon');
                balloon.style.left = Math.random() * 100 + 'vw';
                balloon.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                let duration = (Math.random() * 3 + 4);
                balloon.style.animationDuration = duration + 's';
                balloon.style.animationDelay = (Math.random() * 2) + 's';
                document.getElementById("results-screen").appendChild(balloon);
                setTimeout(() => {{ balloon.remove(); }}, (duration + 2) * 1000);
            }}
        }}
    </script>
    </body>
    </html>
    """
    
    # HTML को स्ट्रीमलिट पेज पर एम्बेड (Embed) करना
    components.html(html_code, height=700)
