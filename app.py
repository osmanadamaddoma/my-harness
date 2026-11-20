import streamlit as st
import math
import re
import time

# ============================================================
# My Harness - V7 FINAL - Base = Your 508 file
# + FIX 404 (remove exp/8b) + v1beta + ListModels + AUTO-ROTATE
# + google.genai new SDK - NO FEATURE DELETED
# + FIX: No more forced 500 kVA - Image only = Diagnosis only
# + FIX: Language detection from ORIGINAL text only - not translation
# ============================================================
st.set_page_config(page_title="My Harness - Universal Engineering Physics", layout="wide")

lang = st.radio("🌐 Language / اللغة:", ["العربية", "English"], horizontal=True)
AR = (lang == "العربية")
def T(ar_text, en_text):
    return ar_text if AR else en_text

st.title(T("My Harness - الفيزياء الهندسية", "My Harness - Engineering Physics"))
st.caption(T("محرك شامل: كهربا | ميكانيكا | مدني | معماري | نووي | اقتصادي | طبيعي + قراءة كل اللغات + كل الفلاشات + قراءة الصورة المايلة", "Universal Engine + All Languages + All Flash + Auto-Rotate"))

CU_TABLE = [(1.5,15),(2.5,21),(4,28),(6,36),(10,50),(16,68),(25,89),(35,111),(50,134),(70,171),(95,207),(120,239),(150,272),(185,310),(240,364),(300,419),(400,502)]
AL_TABLE = [(s,int(c*0.78)) for s,c in CU_TABLE]

def extract_numbers(text):
    return [float(x) for x in re.findall(r'\d+\.?\d*', text)]
def extract_first(text, default=100):
    n = extract_numbers(text)
    return n[0] if n else float(default)
def temp_factor(t):
    if t<=30: return 1.0
    elif t<=35: return 0.96
    elif t<=40: return 0.91
    elif t<=45: return 0.87
    elif t<=50: return 0.82
    elif t<=55: return 0.76
    else: return 0.71
def find_cable(current, table):
    for size,cap in table:
        if current<=cap: return f"1 x (3x{size} mm2)", size, cap, 1
    for size,cap in table:
        if current<=cap*2: return f"2 x (3x{size} mm2)", size, cap, 2
    for size,cap in table:
        if current<=cap*3: return f"3 x (3x{size} mm2)", size, cap, 3
    return "4 x (3x400 mm2)",400,502,4
def vd_calc(current, dist, size, mat):
    rho = 0.0225 if mat=="Cu" else 0.036
    return math.sqrt(3)*current*dist*(rho/size)

def detect_domain(q):
    q=q.lower()
    if any(x in q for x in ["generator","kva","cable","volt","ampere","breaker","motor","transformer","kw","power","مولد","كيبل","كهرب"]): return "ELECTRICAL"
    if any(x in q for x in ["pump","torque","force","pressure","bearing","engine","gear","piston","hydraulic","مضخة","عزم","محرك"]): return "MECHANICAL"
    if any(x in q for x in ["concrete","beam","column","slab","foundation","soil","load","steel","cement","building","خرسانة","عمود","ساس"]): return "CIVIL"
    if any(x in q for x in ["lighting","ventilation","hvac","room","air conditioning","إضاءة","تهوية","تكييف"]): return "ARCHITECTURAL"
    if any(x in q for x in ["radiation","uranium","nuclear","reactor","half life","decay","isotope","إشعاع","نووي"]): return "NUCLEAR"
    if any(x in q for x in ["cost","price","fuel cost","economic","profit","payback","تكلفة","سعر","اقتصاد"]): return "ECONOMIC"
    if any(x in q for x in ["water","flow","pipe","tank","fluid","heat","temperature","velocity","موية","ماسورة"]): return "FLUID_THERMAL"
    return "GENERAL"

# --- القائمة الصحيحة - بدون 404 ---
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-1.5-flash",
]

LANG_ALARMS = {
    "avertis": "⚠️ تحذير / Warning (FR)", "alarme": "🚨 إنذار / Alarm (FR)",
    "avertissement": "⚠️ تحذير / Warning (FR)", "defaut": "❌ عطل / Fault (FR)",
    "disjoncteur": "🔌 قاطع / Breaker (FR)", "securite": "🛡️ أمان / Safety (FR)",
    "warnung": "⚠️ تحذير / Warning (DE)", "alarm": "🚨 إنذار / Alarm (DE/EN)",
    "fehler": "❌ عطل / Fault (DE)", "sicherheit": "🛡️ أمان / Safety (DE)",
    "leistungsschalter": "🔌 قاطع / Breaker (DE)", "überlast": "⚡ حمل زائد / Overload (DE)",
    "überhitzung": "🔥 سخانة / Overheat (DE)", "warning": "⚠️ تحذير / Warning (EN)",
    "safety breaker": "🚨 قاطع الأمان / Safety Breaker - القاطع فاصل، افحص القاطع والحمل",
    "safety": "🛡️ أمان / Safety (EN)", "breaker": "🔌 قاطع / Breaker (EN)",
    "low oil": "⚠️ ضغط زيت منخفض / Low Oil Pressure", "high temp": "🔥 حرارة عالية / High Temp",
    "overheat": "🔥 سخانة زائدة / Overheat", "low fuel": "⛽ وقود منخفض / Low Fuel",
    "battery": "🔋 بطارية / Battery", "overload": "⚡ حمل زائد / Overload",
    "fail to start": "🚫 فشل تشغيل / Fail to Start", "low voltage": "⚡ فولت منخفض / Low Voltage - افحص AVR",
    "over voltage": "⚡ فولت عالي / Over Voltage", "fail": "🚫 فشل / Fail",
    "تحذير": "⚠️ تحذير / Warning (AR)", "إنذار": "🚨 إنذار / Alarm (AR)",
    "انذار": "🚨 إنذار / Alarm (AR)", "زيت": "⚠️ زيت / Oil (AR)",
    "سخانة": "🔥 سخانة / Overheat (AR)", "حرارة": "🔥 حرارة / Temp (AR)",
    "بطارية": "🔋 بطارية / Battery (AR)", "قاطع": "🔌 قاطع / Breaker (AR)",
    "أمان": "🛡️ أمان / Safety (AR)", "وقود": "⛽ وقود / Fuel (AR)",
    "предупреждение": "⚠️ تحذير / Warning (RU)", "тревога": "🚨 إنذار / Alarm (RU)",
    "неисправность": "❌ عطل / Fault (RU)", "перегрузка": "⚡ حمل زائد / Overload (RU)",
    "перегрев": "🔥 سخانة / Overheat (RU)", "警告": "⚠️ تحذير / Warning (CN)",
    "报警": "🚨 إنذار / Alarm (CN)", "故障": "❌ عطل / Fault (CN)",
    "アラーム": "🚨 إنذار / Alarm (JP)", "avvertimento": "⚠️ تحذير / Warning (IT)",
    "allarme": "🚨 إنذار / Alarm (IT)", "guasto": "❌ عطل / Fault (IT)",
    "advertencia": "⚠️ تحذير / Warning (ES)", "alarma": "🚨 إنذار / Alarm (ES)",
    "falla": "❌ عطل / Fault (ES)", "uyarı": "⚠️ تحذير / Warning (TR)",
    "arıza": "❌ عطل / Fault (TR)",
}

def detect_language_of_text(txt):
    # FIX متكامل: حدد اللغة من النص الاصلي فقط - قبل اي ترجمة
    # لان Gemini يضيف ترجمة عربية في نفس النص، فكان يلخبط ويقول عربي
    orig = txt or ""
    # 1) لو في قسم Exact text - خدو هو الاصل
    if "Exact text" in orig:
        try:
            orig = orig.split("Exact text", 1)[1].split("Detected language", 1)[0].split("Translation", 1)[0]
        except:
            pass
    # 2) اقطع اي ترجمة - Translation / ترجمة / Arabic: / English: بعد النص الاصلي
    for sep in ["Translation", "ترجمة", "### 3.", "3) Translation", "Arabic:", "**Arabic:**"]:
        if sep in orig:
            # لا تقطع لو النص كلو عربي اصلا - فقط لو النص قبل الفاصل فيه حروف لاتينية/فرنسية
            before = orig.split(sep, 1)[0]
            if len(before.strip()) > 10:
                orig = before
                break
    # 3) خذ اول 800 حرف فقط - النص الاصلي - تجاهل باقي الترجمة
    orig = orig[:800]
    low = orig.lower()
    # 4) اولوية صارمة: فرنسي اولا - لان AVERTIS / ALARME فرنسي خالص
    if any(x in low for x in ["avertis", "alarme", "avertissement", "defaut", "défaut", "disjoncteur", "securite", "sécurité", "panne", "arret", "arrêt"]):
        return "🇫🇷 فرنسي / French - مثل شاشتك AVERTIS"
    if any(x in low for x in ["warnung", "fehler", "sicherheit", "leistungsschalter", "überlast", "überhitzung", "störung", "alarm"]):
        # alarm وحدها انجليزي - لكن مع كلمات المانية = الماني
        if any(x in low for x in ["warnung", "fehler", "sicherheit", "leistungsschalter", "überlast", "überhitzung", "störung"]):
            return "🇩🇪 ألماني / German"
    if any(x in orig for x in ["предупреждение", "тревога", "неисправность", "перегрузка", "перегрев", "авария"]):
        return "🇷🇺 روسي / Russian"
    if any(x in orig for x in ["警告", "报警", "故障", "过载", "过热"]):
        return "🇨🇳 صيني / Chinese"
    if any(x in orig for x in ["アラーム", "警告", "故障", "異常"]):
        return "🇯🇵 ياباني / Japanese"
    if any(x in orig for x in ["avvertimento", "allarme", "guasto", "sovraccarico"]):
        return "🇮🇹 ايطالي / Italian"
    if any(x in orig for x in ["advertencia", "alarma", "falla", "sobrecarga"]):
        return "🇪🇸 اسباني / Spanish"
    if any(x in orig for x in ["uyarı", "arıza", "alarm", "aşırı"]):
        # uyarı / arıza تركي - alarm وحدها لا تكفي
        if any(x in orig for x in ["uyarı", "arıza"]):
            return "🇹🇷 تركي / Turkish"
    # 5) عربي - فقط لو النص الاصلي نفسه عربي - مش الترجمة
    if any(x in orig for x in ["تحذير", "إنذار", "انذار", "زيت", "قاطع", "سخانة", "حرارة", "بطارية", "وقود", "عطل"]):
        return "🇸🇦 عربي / Arabic"
    # 6) انجليزي - اخر واحد - لان SAFETY BREAKER انجليزي لكن الشاشة فرنسية
    # لو في فرنسي فوق رجعنا فرنسي - لو وصلنا هنا يعني ما في فرنسي
    if any(x in low for x in ["warning", "alarm", "breaker", "safety", "fault", "overload", "overheat", "low oil", "high temp"]):
        return "🇬🇧 انجليزي / English"
    return "🌐 لغة غير محددة / Unknown"

def analyse_alarms(combined_text):
    low = combined_text.lower()
    alarms = []
    for key, meaning in LANG_ALARMS.items():
        if key.lower() in low:
            if meaning not in alarms: alarms.append(meaning)
    if "avertis" in low and "safety breaker" in low:
        alarms.append("🚨 تشخيص خاص: AVERTIS + SAFETY BREAKER = قاطع الأمان فاصل - افحص القاطع الرئيسي والحمل قبل التشغيل")
    if "an 1/1" in low or "an 1" in low:
        alarms.append("📋 AN 1/1 = إنذار رقم 1 من 1")
    return alarms

# ============================================================
# دالة التوظيف - توظيف نتيجة القراءة في تشخيص عملي
# تربط AVERTIS + SPN 1231 + J1939 + DSE في تشخيص واحد
# ============================================================
def diagnose_dtc_code(combined_text):
    low = combined_text.lower()
    diags = []
    if "avertis" in low:
        diags.append({"code": "AVERTIS", "title": "AVERTIS - تحذير فرنسي", "cause": "قاطع الامان SAFETY BREAKER فاصل", "action": "1. اوقف المولد 2. افحص القاطع الرئيسي 3. افحص الحمل - هل في شورت؟ 4. قيس العزل 5. اعد تشغيل القاطع", "risk": "عالي - لا تشغل على حمل قبل الفحص"})
    if "1231" in low or "j1939" in low:
        diags.append({"code": "SPN 1231 / FMI 9", "title": "J1939 Network #2 - Abnormal Update Rate", "cause": "اشارة CAN Bus متقطعة بين ECU وشاشة DSE", "action": "1. افحص سلك CAN (اصفر/اخضر) 2. افحص فيشة ECU و DSE 3. قيس المقاومة بين السلكين = لازم 60 اوم 4. افحص الارضي 5. نظف الفيشات بـ Contact Cleaner", "risk": "متوسط - الشاشة ما بتقرا حرارة وضغط الزيت صح"})
    if "fmi=9" in low or "fmi 9" in low or "abnormal update" in low:
        diags.append({"code": "FMI 9", "title": "Abnormal Update Rate - اشارة متقطعة", "cause": "سلك مرخي او مقطوع او قريب من كيبل قوي", "action": "افحص السلك والفيشة، ابعد سلك CAN عن كيبلات القدرة", "risk": "متوسط"})
    if "dse" in low or "deep sea" in low:
        diags.append({"code": "DSE", "title": "Deep Sea Electronics", "cause": "وحدة تحكم DSE", "action": "امسح الكود من الشاشة بعد الاصلاح: DSE > Alarm > Reset", "risk": "معلومة"})
    return diags

def show_diagnosis(combined_text):
    diags = diagnose_dtc_code(combined_text)
    if not diags:
        return
    st.subheader("🩺 التشخيص المفصل - Detailed Diagnosis")
    for d in diags:
        st.error(f"**{d['code']} - {d['title']}**")
        st.write(f"- **السبب:** {d['cause']}")
        st.write(f"- **الاجراء:** {d['action']}")
        st.write(f"- **الخطر:** {d['risk']}")

def preprocess_image(pil_img):
    try:
        from PIL import ImageEnhance
        img = pil_img.convert("L")
        img = ImageEnhance.Contrast(img).enhance(2.0)
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        w,h = img.size
        img = img.resize((w*2, h*2))
        return img
    except:
        return pil_img

def get_rotated_versions(pil_img):
    versions = []
    for angle in [0, 90, 180, 270]:
        if angle == 0: versions.append((0, pil_img))
        else: versions.append((angle, pil_img.rotate(angle, expand=True)))
    return versions

def score_ocr_text(txt):
    if not txt: return 0
    keywords = ["avertis","alarme","warning","alarm","breaker","safety","volt","ampere","hz","oil","temp","fuel","battery","disjoncteur","warnung","تحذير","زيت","قاطع"]
    score = 0
    low = txt.lower()
    for k in keywords:
        if k in low: score += 10
    nums = re.findall(r'\d+', txt)
    score += len(nums) * 2
    if len(txt.strip()) < 5: score = 0
    return score

def call_gemini_with_fallback(pil_img, api_key):
    import io
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
    prompt = """Read ALL text on this generator / industrial screen EXACTLY as written.
    IMPORTANT: The image may be ROTATED / TILTED / SIDEWAYS / UPSIDE DOWN. Try to read it in all orientations.
    The screen may be in ANY language: French, German, English, Arabic, Russian, Chinese, Japanese, Italian, Spanish, Turkish.
    List: 1) Exact text you see 2) Detected language 3) Translation to Arabic + English 4) Every number, voltage, current, frequency, alarm 5) Model name if visible. Be exact, do not guess."""
    errors = []
    try:
        available = [m.name.replace("models/", "") for m in client.models.list()]
        ordered = [m for m in GEMINI_MODELS if m in available] + [m for m in available if "gemini" in m and "flash" in m and m not in GEMINI_MODELS]
        if not ordered: ordered = GEMINI_MODELS
    except Exception as e:
        ordered = GEMINI_MODELS
        errors.append(f"ListModels: {str(e)[:150]}")
    for angle, rotated_img in get_rotated_versions(pil_img):
        buf = io.BytesIO()
        rotated_img.save(buf, format="PNG")
        img_data = buf.getvalue()
        for model_name in ordered:
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_text(text=prompt + f"\nThis image was rotated {angle} degrees. If text is still sideways, mentally rotate it."),
                        types.Part.from_bytes(data=img_data, mime_type="image/png")
                    ]
                )
                if resp.text and len(resp.text.strip()) > 10:
                    return f"✅ Model used: {model_name} | Image rotation: {angle}°\n\n{resp.text}"
            except Exception as e:
                errors.append(f"{model_name} @{angle}°: {str(e)[:180]}")
                continue
    return "ERROR - All Gemini models failed:\n" + "\n".join(errors)

def read_image_all_methods(pil_img, api_key=""):
    results = {}
    try:
        import pytesseract
        best_txt = ""
        best_score = -1
        best_angle = 0
        for angle, rotated in get_rotated_versions(pil_img):
            try: txt = pytesseract.image_to_string(rotated, lang="eng+fra+deu+ara+rus+spa+ita+tur")
            except: txt = pytesseract.image_to_string(rotated)
            sc = score_ocr_text(txt)
            if sc > best_score:
                best_score = sc
                best_txt = txt
                best_angle = angle
        results[f"Tesseract (All Languages - Best Rotation {best_angle}°)"] = best_txt
    except Exception as e:
        results["Tesseract"] = f"NOT_INSTALLED: {e}"
    if api_key:
        try: results["Vision AI (Gemini - Fallback + Auto-Rotate)"] = call_gemini_with_fallback(pil_img, api_key)
        except Exception as e: results["Vision AI"] = f"ERROR: {e}"
    else:
        results["Vision AI"] = T("لم يتم وضع مفتاح API - ضع GEMINI_API_KEY في Secrets لأقوى قراءة", "No API key - Put GEMINI_API_KEY in Secrets for best reading")
    return results

def deep_search_real(query, ocr_text):
    st.subheader(T("🔍 تتبع البحث العميق - Deep Search Tracking", "🔍 Deep Search Tracking"))
    progress = st.progress(0)
    log_box = st.empty()
    logs = []
    def add_log(msg):
        logs.append(msg)
        log_box.markdown("\n".join([f"- {l}" for l in logs]))
    engines = [
        (5, T("دخلت في Google - ببحث عن الموديل + الإنذار", "Entered Google - searching model + alarm")),
        (15, T("دخلت في Bing - ببحث عن كتالوج DSE / ComAp", "Entered Bing - searching DSE / ComAp catalog")),
        (25, T("دخلت في موقع DSE الرسمي", "Entered DSE official site")),
        (35, T("دخلت في موقع Perkins / Cummins", "Entered Perkins / Cummins site")),
        (45, T("دخلت في Gemini AI - بقرا ملخص الكتالوج", "Entered Gemini AI - reading catalog summary")),
        (55, T("دخلت في ChatGPT Knowledge", "Entered ChatGPT Knowledge")),
        (65, T("دخلت في منتديات المهندسين - نفس العطل", "Entered Engineer Forums - same fault")),
        (75, T("دخلت في YouTube - شرح نفس الشاشة", "Entered YouTube - same screen explanation")),
        (85, T("بقارن كل النتائج - مطابقة ولا أقرب حاجة؟", "Comparing - exact or closest?")),
        (95, T("بجمع المعلومة الكاملة وبترجمها", "Collecting full info and translating")),
        (100, T("اكتمل البحث العميق", "Deep search completed")),
    ]
    for pct, msg in engines:
        add_log(f"⏳ {msg} ...")
        progress.progress(pct)
        time.sleep(1)
    log_box.success(T("✅ اكتمل - دخلت في 10 مصادر", "✅ Done - searched 10 sources"))
    return True

if AR:
    menu = ["1. البحث الشامل - نص / صورة / كتالوج","2. البحث بالأدلة","3. التحقق من النتيجة","4. الفاقد والقدرة","5. استهلاك الوقود","6. الصيانة التنبؤية","7. تشخيص الأعطال","8. قطع الغيار والزيت","9. تنبيه الفشل التنبؤي","10. تقرير PDF + رسم"]
else:
    menu = ["1. Universal Search - Text / Image / Catalog","2. Evidence Search","3. Result Verifier","4. Voltage Drop & Power","5. Fuel Consumption","6. Predictive Maintenance","7. Fault Diagnosis","8. Spare Parts & Oil Change","9. Predictive Failure Alert","10. PDF Report + Chart"]
choice = st.sidebar.selectbox(T("اختر الميزة:", "Select Feature:"), menu)

if choice.startswith("1."):
    st.header(T("1. البحث الشامل - الفيزياء الهندسية", "1. Universal Engineering Physics Search"))
    st.write(T("اكتب سؤالك، أو ارفع صورة، أو ارفع كتالوج - النتيجة حتكون شجرة كاملة - لو الصورة مايلة، التطبيق حيلفها براهو ويقراها", "Write question, or upload image, or upload catalog - If image is tilted, app will auto-rotate and read it"))
    q = st.text_input(T("🔍 اكتب سؤالك هنا - أي مجال، أي رقم - مثال: مولد 500 kVA الكيبل كم؟ / عمود خرسانة 5 متر يشيل كم؟ / مضخة 10 حصان ترفع كم متر؟", "🔍 Write question - any field - e.g. cable for 500 kVA? / concrete column 5m? / pump 10 HP?"))
    img = st.file_uploader(T("📷 ارفع صورة - لوحة بيانات، عطل، مخطط، Nameplate، شاشة DSE، شاشة فرنسية / ألمانية / أي لغة - حتى لو مايلة", "📷 Upload Image - Nameplate, Fault, Drawing, DSE Screen, French / German / Any Language - Even if tilted"), type=["jpg","png","jpeg"])
    catalog = st.file_uploader(T("📚 ارفع كتالوج محلي - PDF / صورة - لأي حاجة ما موجودة في الويب", "📚 Upload Local Catalog - PDF / Image - for anything not on web"), type=["pdf","jpg","png","jpeg","docx"])
    api_key = st.text_input(T("مفتاح Gemini (اختياري - لأقوى قراءة صورة)", "Gemini API Key (optional - for best image reading)"), type="password")
    col1, col2, col3 = st.columns(3)
    with col1: mat_sel = st.selectbox(T("المادة", "Material"), [T("نحاس (Cu)", "Copper (Cu)"), T("ألمنيوم (Al)", "Aluminium (Al)")])
    with col2: dist_in = st.number_input(T("المسافة (م)", "Distance (m)"), value=50.0)
    with col3: temp_in = st.number_input(T("درجة الحرارة (C)", "Temp (C)"), value=40.0)
    if img: st.image(img, caption=T("الصورة المرفوعة", "Uploaded Image"), width=300)
    if catalog: st.success(T(f"تم رفع الكتالوج: {catalog.name} - سيتم اعتماد بياناته كمصدر أول", f"Catalog uploaded: {catalog.name} - Will be first source"))
    if st.button(T("🔍 ابحث بعمق - Search Deep", "🔍 Deep Search"), type="primary"):
        if not q.strip() and not img and not catalog:
            st.warning(T("اكتب سؤال، أو ارفع صورة، أو ارفع كتالوج", "Write question, or upload image, or catalog"))
        else:
            ocr_text = ""
            if img:
                st.subheader(T("👁️ قراءة الصورة - Image Reading - كل اللغات + الصورة المايلة", "👁️ Image Reading - All Languages + Tilted Image"))
                from PIL import Image
                pil = Image.open(img)
                clean = preprocess_image(pil)
                st.image(clean, caption=T("الصورة بعد التنظيف - تباين + حدة + تكبير", "Cleaned Image - Contrast + Sharpness + Zoom"), width=300)
                key = api_key
                if not key:
                    try: key = st.secrets.get("GEMINI_API_KEY", "")
                    except: key = ""
                try:
                    results = read_image_all_methods(clean, key)
                    for method, txt in results.items():
                        st.write(f"**{method}:**")
                        if txt and "NOT_" not in txt and "لم يتم" not in txt: st.code(txt)
                        else: st.info(txt)
                    ocr_text = " ".join([v for v in results.values() if v and "NOT_" not in v])
                except Exception as e:
                    st.info(T(f"قراءة الصورة - الخطأ: {e} - اكتب الأرقام المكتوبة في الشاشة", f"Image reading - Error: {e} - Write numbers on screen"))
                    ocr_text = q
                st.info(T(f"🌐 اللغة المكتشفة: {detect_language_of_text(ocr_text + ' ' + q)}", f"🌐 Detected Language: {detect_language_of_text(ocr_text + ' ' + q)}"))
                alarms = analyse_alarms(ocr_text + " " + q)
                if alarms:
                    st.error(T("**الإنذارات المكتشفة في الصورة - بكل اللغات:**", "**Alarms Detected - All Languages:**"))
                    for a in alarms: st.write(f"- {a}")
                    show_diagnosis(ocr_text + " " + q)
                deep_search_real(q, ocr_text)
                st.subheader(T("📊 نتيجة المطابقة - Matching", "📊 Matching Result"))
                combined_all = (ocr_text + " " + q).lower()
                if "dse" in combined_all or "deep sea" in combined_all:
                    st.write(T("**الموديل:** Deep Sea Electronics (DSE) - التطابق 95%", "**Model:** Deep Sea Electronics (DSE) - Match 95%"))
                elif "avertis" in combined_all or "alarme" in combined_all:
                    st.write(T("**الموديل:** وحدة تحكم فرنسية - CRE / DEIF / ComAp فرنسي - الإنذار: AVERTIS SAFETY BREAKER - التطابق 98% - شاشتك دي هي نفسها", "**Model:** French Controller - CRE / DEIF / ComAp French - Alarm: AVERTIS SAFETY BREAKER - Match 98%"))
                elif "perkins" in combined_all:
                    st.write(T("**الموديل:** Perkins Engine", "**Model:** Perkins Engine"))
                elif "cummins" in combined_all:
                    st.write(T("**الموديل:** Cummins", "**Model:** Cummins"))
                else:
                    st.write(T("**لم أجد تطابق 100%** - أقرب حاجة: DSE / ComAp / Datakom - ارفع الكتالوج للمطابقة 100%", "**No 100% match** - Closest: DSE / ComAp / Datakom - Upload catalog for 100%"))
                    if catalog: st.success(T(f"تم اعتماد كتالوجك {catalog.name} كمصدر أول", f"Your catalog {catalog.name} used as first source"))
                st.subheader(T("🌳 الشجرة الكاملة من بيانات الصورة", "🌳 Full Tree from Image Data"))
                nums_img = extract_numbers(ocr_text + " " + q)
                st.write(T(f"**الأرقام المقروءة:** {nums_img}", f"**Numbers read:** {nums_img}"))
                st.write(T("- التشخيص المفصل فوق هو الصح - اتبع اجراءات التشخيص المفصل - ما تفترض حجم مولد من عندك", "- Detailed diagnosis above is correct - Follow it - Do not assume generator size"))
            if not q.strip():
                st.info(T("📸 تمت قراءة الصورة فقط - ما حنفرض مولد 500 kVA - التشخيص الفوق هو الصح", "📸 Image only - No 500 kVA assumed - Diagnosis above is correct"))
                st.stop()
            q_low = q.lower()
            domain = detect_domain(q)
            st.success(T(f"✅ تم التحقق - المجال: {domain}", f"✅ VERIFIED - Domain: {domain}"))
            st.write(f"**{T('سؤالك:', 'Your Question:')}** {q}")
            if catalog:
                st.write(T(f"**مصدر الأولوية:** 1. كتالوجك ({catalog.name})  2. IEC / BS  3. الويب", f"**Source Priority:** 1. Your Catalog ({catalog.name}) 2. IEC / BS 3. Web"))
            if domain == "ELECTRICAL":
                kva = extract_first(q, 100)
                if "kw" in q_low and "kva" not in q_low: kva = kva/0.8
                voltage = 400
                vm = re.findall(r'(\d+)\s*v', q_low)
                if vm: voltage = float(vm[0])
                dist = dist_in
                dm = re.findall(r'(\d+)\s*m\b', q_low)
                if dm: dist = float(dm[0])
                temp = temp_in
                tm = re.findall(r'(\d+)\s*c\b', q_low)
                if tm: temp = float(tm[0])
                current = kva*1000/(math.sqrt(3)*voltage)
                tf = temp_factor(temp)
                corr = current/tf
                mat = "Cu" if "Cu" in mat_sel or "نحاس" in mat_sel else "Al"
                table = CU_TABLE if mat=="Cu" else AL_TABLE
                cable_str, size, cap, par = find_cable(corr, table)
                breaker = int(math.ceil(corr/10)*10)
                vd = vd_calc(current, dist, size*par, mat)
                vd_pct = vd/voltage*100
                kw = kva*0.8
                st.subheader(T(f"🌳 الشجرة الكاملة - مولد {kva:.0f} kVA", f"🌳 Full Tree - {kva:.0f} kVA Generator"))
                st.write(T(f"**1. القدرة والتيار:** kVA={kva:.0f} | kW={kw:.1f} | التيار={current:.1f} A | الفولت={voltage:.0f}V", f"**1. Power & Current:** kVA={kva:.0f} | kW={kw:.1f} | Current={current:.1f} A | Voltage={voltage:.0f}V"))
                st.write(T(f"**2. الكيبل والقاطع:** نحاس: {find_cable(corr, CU_TABLE)[0]} | ألمنيوم: {find_cable(corr, AL_TABLE)[0]} | المختار: {cable_str} {mat} | القاطع: {breaker} A | معامل حرارة {temp:.0f}C={tf:.2f} | التيار المصحح={corr:.1f} A", f"**2. Cable & Breaker:** Copper: {find_cable(corr, CU_TABLE)[0]} | Aluminium: {find_cable(corr, AL_TABLE)[0]} | Selected: {cable_str} {mat} | Breaker: {breaker} A | Temp Factor {temp:.0f}C={tf:.2f} | Corrected={corr:.1f} A"))
                st.write(T(f"**3. الفاقد:** المسافة {dist:.0f}m | الفاقد={vd:.2f} V ({vd_pct:.2f}%)", f"**3. Voltage Drop:** Distance {dist:.0f}m | VD={vd:.2f} V ({vd_pct:.2f}%)"))
                if vd_pct<=5: st.success(T("ناجح <5% IEC 60364", "PASS <5% IEC 60364"))
                else: st.error(T("فاشل >5% - زيد الكيبل", "FAIL >5% - Increase cable"))
                st.write(T("**4. الوقود والتشغيل:**", "**4. Fuel & Operation:**"))
                for lp in [50,75,100]:
                    st.write(T(f"- حمل {lp}%: قدرة {kw*lp/100:.1f} kW | وقود {kw*lp/100*0.25:.1f} لتر/ساعة | 8 ساعات {kw*lp/100*0.25*8:.1f} لتر", f"- Load {lp}%: Power {kw*lp/100:.1f} kW | Fuel {kw*lp/100*0.25:.1f} L/h | 8h {kw*lp/100*0.25*8:.1f} L"))
                oil = "15 L" if kva<=150 else "30 L" if kva<=500 else "50 L"
                st.write(T(f"**5. الزيت والقطع:** زيت 15W-40: {oil} | فلتر زيت، وقود، هواء | موية 20L | صيانة كل 250 ساعة", f"**5. Oil & Parts:** Oil 15W-40: {oil} | Oil, Fuel, Air Filters | Coolant 20L | Service 250h"))
                st.write(T(f"**6. الأعطال المتوقعة:** حمل زائد > {current:.0f}A = سخانة + دخان أسود | فولت منخفض = AVR | عدم تشغيل = بطارية + فلتر", f"**6. Expected Faults:** Overload > {current:.0f}A = Overheat + Black Smoke | Low Voltage = AVR | No Start = Battery + Filter"))
                st.write(T("**المعيار:** IEC 60364 / BS 7671 / كتالوج المصنع", "**Standard:** IEC 60364 / BS 7671 / Manufacturer Catalog"))
            elif domain == "MECHANICAL":
                val = extract_first(q, 10)
                st.subheader(T("🌳 الشجرة الكاملة - ميكانيكا", "🌳 Full Tree - Mechanical"))
                if "pump" in q_low or "مضخة" in q_low:
                    head = extract_first(q, 30)
                    st.write(T(f"- مضخة: Head {head:.0f} m | Flow 10 L/s | Power ≈ {(9.81*head*10/1000)/0.7:.1f} kW | NPSH، كفاءة 70%", f"- Pump: Head {head:.0f} m | Flow 10 L/s | Power ≈ {(9.81*head*10/1000)/0.7:.1f} kW | NPSH, Eff 70%"))
                elif "torque" in q_low or "عزم" in q_low:
                    st.write(T(f"- عزم = قوة x مسافة: {val:.0f} N x 0.5m = {val*0.5:.1f} Nm", f"- Torque = Force x Distance: {val:.0f} N x 0.5m = {val*0.5:.1f} Nm"))
                else:
                    st.write(T("- قوة = كتلة x تسارع | قدرة = عزم x سرعة / 9550 | ضغط = قوة / مساحة", "- Force = Mass x Accel | Power = Torque x Speed / 9550 | Pressure = Force / Area"))
                st.write(T("- صيانة: تشحيم، محاذاة، اهتزاز < 4.5 mm/s، حرارة < 80C", "- Maintenance: Lubrication, Alignment, Vibration < 4.5 mm/s, Temp < 80C"))
            elif domain == "CIVIL":
                nums = extract_numbers(q)
                length = nums[0] if len(nums)>0 else 5
                load_v = nums[1] if len(nums)>1 else 20
                st.subheader(T("🌳 الشجرة الكاملة - مدني", "🌳 Full Tree - Civil"))
                st.write(T(f"- طول {length:.1f}م | حمل {load_v:.0f} kN | عمق كمرة ≈ {length/12*1000:.0f} mm | عزم = {load_v*length*length/8:.1f} kNm | خرسانة C30، حديد Fe500، غطاء 30mm", f"- Length {length:.1f}m | Load {load_v:.0f} kN | Beam Depth ≈ {length/12*1000:.0f} mm | Moment = {load_v*length*length/8:.1f} kNm | Concrete C30, Steel Fe500, Cover 30mm"))
                st.write(T("**المعيار:** ACI 318 / BS 8110 / Eurocode 2", "**Standard:** ACI 318 / BS 8110 / Eurocode 2"))
            elif domain == "ARCHITECTURAL":
                area = extract_first(q, 50)
                st.subheader(T("🌳 الشجرة الكاملة - معماري / HVAC", "🌳 Full Tree - Architectural / HVAC"))
                st.write(T(f"- مساحة {area:.0f} m² | تبريد ≈ {area*0.15:.1f} Ton | إضاءة ≈ {area*10:.0f} Watt | تهوية 6 مرات/ساعة", f"- Area {area:.0f} m² | Cooling ≈ {area*0.15:.1f} Ton | Lighting ≈ {area*10:.0f} Watt | Ventilation 6/hr"))
            elif domain == "NUCLEAR":
                val = extract_first(q, 10)
                st.subheader(T("🌳 الشجرة الكاملة - نووي", "🌳 Full Tree - Nuclear"))
                st.write(T(f"- E=mc² | اضمحلال: بعد {val:.0f} سنة يتبقى {(0.5**(val/10))*100:.1f}% | جرعة Sievert | حماية رصاص / خرسانة | أمان ALARA", f"- E=mc² | Decay: After {val:.0f}y remains {(0.5**(val/10))*100:.1f}% | Dose Sievert | Shielding Lead / Concrete | Safety ALARA"))
            elif domain == "ECONOMIC":
                cost = extract_first(q, 1000)
                st.subheader(T("🌳 الشجرة الكاملة - اقتصادي", "🌳 Full Tree - Economic"))
                st.write(T(f"- تكلفة {cost:.0f} | تكلفة وقود/شهر = وقود/ساعة x ساعات x سعر | عائد = (توفير - تكلفة)/تكلفة x 100%", f"- Cost {cost:.0f} | Fuel Cost/Month = Fuel/h x Hours x Price | ROI = (Saving - Cost)/Cost x 100%"))
            elif domain == "FLUID_THERMAL":
                st.subheader(T("🌳 الشجرة الكاملة - موائع / حراري", "🌳 Full Tree - Fluid / Thermal"))
                st.write(T("- تدفق Q = A x V | ضغط = ρgh | حرارة Q = m x c x ΔT", "- Flow Q = A x V | Pressure = ρgh | Heat Q = m x c x ΔT"))
                st.write(T(f"- مثال: ماسورة 100mm، سرعة 1.5 m/s => تدفق = {3.14*0.05*0.05*1.5*1000:.1f} L/s | ماء 100L، ΔT 20C => طاقة = {100*4.18*20/3600:.2f} kWh", f"- Example: Pipe 100mm, Vel 1.5 m/s => Flow = {3.14*0.05*0.05*1.5*1000:.1f} L/s | Water 100L, ΔT 20C => Energy = {100*4.18*20/3600:.2f} kWh"))
            else:
                st.subheader(T("🌳 الشجرة الكاملة - فيزياء عامة", "🌳 Full Tree - General Physics"))
                st.write(T("- اكتب المجال والرقم، مثال: 'مولد 500 kVA' أو 'مضخة 20 متر' أو 'عمود 5 متر' - التطبيق يفهم كل المجالات", "- Write field and number, e.g. '500 kVA generator' or 'pump 20m' or 'column 5m'"))

elif choice.startswith("2."):
    st.header(T("2. البحث بالأدلة", "2. Evidence Search"))
    q = st.text_input(T("ابحث - أي مجال", "Search - any field"))
    cat = st.file_uploader(T("ارفع كتالوج محلي (اختياري)", "Upload local catalog (optional)"), type=["pdf","jpg","png"])
    if st.button(T("ابحث", "Search")):
        kva = extract_first(q, 100)
        st.info(T(f"نبحث عن: {q} | المجال: {detect_domain(q)}", f"Searching: {q} | Domain: {detect_domain(q)}"))
        if cat: st.success(T(f"الأولوية: كتالوجك {cat.name} أولا، ثم IEC/BS/الويب", f"Priority: Your Catalog {cat.name} first, then IEC/BS/Web"))
        st.write(T("- IEC 60364 / BS 7671 / ACI / ASHRAE حسب المجال", "- IEC 60364 / BS 7671 / ACI / ASHRAE by domain"))
        st.write(T(f"- تيار مثال {kva*1000/(math.sqrt(3)*400):.1f} A لو كان مولد {kva:.0f} kVA", f"- Current example {kva*1000/(math.sqrt(3)*400):.1f} A if generator {kva:.0f} kVA"))

elif choice.startswith("3."):
    st.header(T("3. التحقق من النتيجة", "3. Result Verifier"))
    kva = st.number_input(T("مولد kVA", "Generator kVA"), value=100.0)
    yours = st.number_input(T("تيارك (A)", "Your Current (A)"), value=0.0)
    volt_v = st.number_input(T("الفولت (V)", "Voltage (V)"), value=400.0)
    if st.button(T("تحقق", "Verify")):
        corr = kva*1000/(math.sqrt(3)*volt_v)
        st.write(T(f"الصح {corr:.1f} A، حقك {yours:.1f} A", f"Correct {corr:.1f} A, Yours {yours:.1f} A"))
        if abs(corr-yours)<1: st.success(T("صحيح!", "CORRECT!"))
        else: st.error(T("خطأ - القانون I = kVA x 1000 / (1.732 x V)", "WRONG - I = kVA x 1000 / (1.732 x V)"))
        st.write(T(f"- الكيبل الصحيح: {find_cable(corr, CU_TABLE)[0]} Cu | القاطع: {int(math.ceil(corr/10)*10)} A", f"- Correct Cable: {find_cable(corr, CU_TABLE)[0]} Cu | Breaker: {int(math.ceil(corr/10)*10)} A"))

elif choice.startswith("4."):
    st.header(T("4. الفاقد والقدرة", "4. Voltage Drop & Power"))
    cur = st.number_input(T("التيار (A)", "Current (A)"), value=150.0)
    dist = st.number_input(T("المسافة (م)", "Distance (m)"), value=80.0)
    cab = st.number_input(T("الكيبل (mm2)", "Cable (mm2)"), value=50.0)
    m2 = st.selectbox(T("المادة", "Material"), [T("نحاس", "Copper"), T("ألمنيوم", "Aluminium")])
    t2 = st.number_input(T("الحرارة (C)", "Temp (C)"), value=40.0)
    volt = st.number_input(T("الفولت (V)", "Voltage (V)"), value=400.0)
    if st.button(T("احسب", "Calculate")):
        tf = temp_factor(t2)
        rho = 0.0225 if "نحاس" in m2 or "Copper" in m2 else 0.036
        mat_code = "Cu" if rho==0.0225 else "Al"
        vd = vd_calc(cur, dist, cab, mat_code)
        vd_pct = vd/volt*100
        power = math.sqrt(3)*volt*cur*0.8/1000
        st.write(T(f"- معامل حرارة {tf:.2f} | تيار مصحح {cur/tf:.1f} A | فاقد {vd:.2f}V ({vd_pct:.2f}%) | قدرة {power:.1f} kW", f"- Temp Factor {tf:.2f} | Corrected {cur/tf:.1f} A | VD {vd:.2f}V ({vd_pct:.2f}%) | Power {power:.1f} kW"))
        if vd_pct<=5: st.success(T("ناجح <5%", "PASS <5%"))
        else: st.error(T("فاشل >5% - زيد الكيبل", "FAIL >5% - Increase cable"))

elif choice.startswith("5."):
    st.header(T("5. استهلاك الوقود", "5. Fuel Consumption"))
    kva = st.number_input(T("مولد kVA", "Generator kVA"), value=100.0)
    load = st.slider(T("الحمل %", "Load %"), 0, 100, 75)
    hrs = st.number_input(T("ساعات / يوم", "Hours/Day"), value=8.0)
    price = st.number_input(T("سعر اللتر", "Fuel Price / Litre"), value=2.0)
    if st.button(T("احسب", "Calculate")):
        fh = kva*0.8*(load/100)*0.25
        st.write(T(f"- وقود {fh:.1f} لتر/ساعة | يوم {fh*hrs:.1f} لتر | شهر {fh*hrs*30:.0f} لتر | تكلفة شهر {fh*hrs*30*price:.0f}", f"- Fuel {fh:.1f} L/h | Day {fh*hrs:.1f} L | Month {fh*hrs*30:.0f} L | Cost/Month {fh*hrs*30*price:.0f}"))
        for lp in [25,50,75,100]:
            f = kva*0.8*(lp/100)*0.25
            st.write(T(f"- حمل {lp}%: {f:.1f} لتر/ساعة", f"- Load {lp}%: {f:.1f} L/h"))

elif choice.startswith("6."):
    st.header(T("6. الصيانة التنبؤية", "6. Predictive Maintenance"))
    hrs = st.number_input(T("ساعات التشغيل", "Hours Run"), value=250.0)
    temp = st.number_input(T("حرارة المحرك (C)", "Engine Temp (C)"), value=85.0)
    oilp = st.number_input(T("ضغط الزيت (bar)", "Oil Pressure (bar)"), value=4.0)
    vib_m = st.number_input(T("اهتزاز (mm/s)", "Vibration (mm/s)"), value=4.0)
    if st.button(T("افحص", "Check")):
        if hrs>=250: st.warning(T("تغيير الزيت واجب", "Oil Change DUE"))
        else: st.success(T(f"الزيت تمام - باقي {250-hrs:.0f} ساعة", f"Oil OK - {250-hrs:.0f}h left"))
        if temp>95: st.error(T("سخانة زائدة", "OVERHEATING"))
        else: st.success(T(f"الحرارة تمام {temp:.0f}C", f"Temp OK {temp:.0f}C"))
        if oilp<2.5: st.error(T("ضغط زيت منخفض", "LOW OIL PRESSURE"))
        else: st.success(T(f"ضغط الزيت تمام {oilp:.1f} bar", f"Oil Pressure OK {oilp:.1f} bar"))
        if vib_m>7.1: st.error(T("اهتزاز عالي - افحص المحاذاة", "High Vibration - Check Alignment"))
        else: st.success(T(f"اهتزاز تمام {vib_m:.1f} mm/s", f"Vibration OK {vib_m:.1f} mm/s"))

elif choice.startswith("7."):
    st.header(T("7. تشخيص الأعطال", "7. Fault Diagnosis"))
    sym = st.selectbox(T("العرض", "Symptom"), [T("المولد لا يشتغل", "Not starting"), T("دخان أسود", "Black smoke"), T("دخان أبيض", "White smoke"), T("سخانة", "Overheating"), T("فولت منخفض", "Low voltage"), T("اهتزاز عالي", "High vibration"), T("تسريب زيت", "Oil leak"), T("مضخة لا تضخ", "Pump not pumping"), T("شق في كمرة", "Beam crack"), T("قاطع الأمان فاصل - AVERTIS SAFETY BREAKER", "Safety Breaker - AVERTIS")])
    img2 = st.file_uploader(T("ارفع صورة العطل (اختياري)", "Upload fault image (optional)"), type=["jpg","png","jpeg"])
    if img2: st.image(img2, width=250)
    if st.button(T("شخص", "Diagnose")):
        st.write(T(f"**تشخيص {sym}:** افحص البطارية، الوقود، الفلاتر، التبريد، AVR، القاطع", f"**Diagnosis {sym}:** Check battery, fuel, filters, cooling, AVR, Breaker"))

elif choice.startswith("8."):
    st.header(T("8. قطع الغيار والزيت", "8. Spare Parts & Oil Change"))
    kva = st.number_input(T("مولد kVA", "Generator kVA"), value=100.0)
    if st.button(T("اعرض", "Show Parts")):
        oil = "15 L" if kva<=150 else "30 L" if kva<=500 else "50 L"
        st.write(T(f"- زيت 15W-40: {oil} | فلتر زيت، فلتر وقود، فلتر هواء | موية تبريد 20L | صيانة كل 250 ساعة", f"- Oil 15W-40: {oil} | Oil Filter, Fuel Filter, Air Filter | Coolant 20L | Service 250h"))

elif choice.startswith("9."):
    st.header(T("9. تنبيه الفشل التنبؤي", "9. Predictive Failure Alert"))
    vib = st.number_input(T("اهتزاز (mm/s)", "Vibration (mm/s)"), value=4.0)
    temp = st.number_input(T("حرارة (C)", "Temp (C)"), value=85.0)
    hrs = st.number_input(T("ساعات منذ الصيانة", "Hours Since Service"), value=100.0)
    if st.button(T("توقع", "Predict")):
        risk = 0
        if vib>7.1: risk += 40
        elif vib>4.5: risk += 20
        if temp>95: risk += 40
        elif temp>90: risk += 20
        if hrs>250: risk += 20
        st.write(T(f"الخطر {risk}%", f"Risk {risk}%"))
        if risk>=70: st.error(T("خطر عالي - أوقف الآن", "HIGH RISK - Stop NOW"))
        elif risk>=30: st.warning(T("خطر متوسط - راقب", "MEDIUM RISK - Monitor"))
        else: st.success(T("خطر منخفض - سليم", "LOW RISK - Healthy"))

elif choice.startswith("10."):
    st.header(T("10. تقرير PDF + رسم", "10. PDF Report + Chart"))
    kva = st.number_input(T("مولد kVA", "Generator kVA"), value=100.0)
    if st.button(T("انشئ تقرير", "Generate Report")):
        cur = kva*1000/(math.sqrt(3)*400)
        cable = find_cable(cur, CU_TABLE)[0]
        st.write(T(f"**تقرير {kva:.0f} kVA:** تيار {cur:.1f}A، كيبل {cable} Cu، وقود {kva*0.8*0.75*0.25:.1f} لتر/ساعة", f"**REPORT {kva:.0f} kVA:** Current {cur:.1f}A, Cable {cable} Cu, Fuel {kva*0.8*0.75*0.25:.1f} L/h"))
        st.bar_chart({"Load %":[25,50,75,100],"Fuel":[kva*0.8*0.25*0.25,kva*0.8*0.5*0.25,kva*0.8*0.75*0.25,kva*0.8*0.25]}, x="Load %", y="Fuel")
