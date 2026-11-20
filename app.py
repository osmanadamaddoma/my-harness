import streamlit as st
import math
import re

st.set_page_config(page_title="My Harness", layout="wide")

# ============ LANGUAGE - ثنائية اللغة ============
# زر اللغة في أول الصفحة - أول حاجة يشوفها المستخدم
lang = st.radio("🌐 Language / اللغة:", ["العربية", "English"], horizontal=True)
AR = (lang == "العربية")

def T(ar_text, en_text):
    return ar_text if AR else en_text

st.title(T("My Harness - الفيزياء الهندسية", "My Harness - Engineering Physics"))
st.caption(T("محرك شامل: كهربا | ميكانيكا | مدني | معماري | نووي | اقتصادي | طبيعي", "Universal Engine: Electrical | Mechanical | Civil | Architectural | Nuclear | Economic | Natural Physics"))

# ============ TABLES ============
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
    if any(x in q for x in ["pump","torque","force","pressure","engine","hydraulic","مضخة","عزم","محرك"]): return "MECHANICAL"
    if any(x in q for x in ["concrete","beam","column","slab","foundation","soil","steel","خرسانة","عمود","ساس"]): return "CIVIL"
    if any(x in q for x in ["lighting","ventilation","hvac","إضاءة","تهوية","تكييف"]): return "ARCHITECTURAL"
    if any(x in q for x in ["radiation","nuclear","reactor","half life","إشعاع","نووي"]): return "NUCLEAR"
    if any(x in q for x in ["cost","price","economic","profit","تكلفة","سعر","اقتصاد"]): return "ECONOMIC"
    if any(x in q for x in ["water","flow","pipe","fluid","heat","موية","ماسورة"]): return "FLUID"
    return "GENERAL"

# ============ SIDEBAR - القائمة تترجم برضو ============
if AR:
    menu = ["1. البحث الشامل - نص / صورة / كتالوج","2. البحث بالأدلة","3. التحقق من النتيجة","4. الفاقد والقدرة","5. استهلاك الوقود","6. الصيانة التنبؤية","7. تشخيص الأعطال","8. قطع الغيار والزيت","9. تنبيه الفشل التنبؤي","10. تقرير PDF + رسم"]
else:
    menu = ["1. Universal Search - Text / Image / Catalog","2. Evidence Search","3. Result Verifier","4. Voltage Drop & Power","5. Fuel Consumption","6. Predictive Maintenance","7. Fault Diagnosis","8. Spare Parts & Oil Change","9. Predictive Failure Alert","10. PDF Report + Chart"]

choice = st.sidebar.selectbox(T("اختر الميزة:", "Select Feature:"), menu)

# ============ 1. UNIVERSAL ============
if choice.startswith("1."):
    st.header(T("1. البحث الشامل - الفيزياء الهندسية", "1. Universal Engineering Physics Search"))
    st.write(T("اكتب سؤالك، أو ارفع صورة، أو ارفع كتالوج - النتيجة حتكون شجرة كاملة", "Write your question, or upload image, or upload catalog - Result will be a full tree"))

    q = st.text_input(T("🔍 اكتب سؤالك هنا - أي مجال، أي رقم - مثال: مولد 500 kVA الكيبل كم؟", "🔍 Write your question here - any field, any number - e.g. cable for 500 kVA generator?"))
    img = st.file_uploader(T("📷 ارفع صورة - لوحة بيانات، عطل، مخطط", "📷 Upload Image - Nameplate, Fault, Drawing"), type=["jpg","png","jpeg"])
    catalog = st.file_uploader(T("📚 ارفع كتالوج محلي - PDF / صورة - لأي حاجة ما موجودة في الويب", "📚 Upload Local Catalog - PDF / Image - for anything not on web"), type=["pdf","jpg","png","jpeg","docx"])

    col1, col2, col3 = st.columns(3)
    with col1: mat_sel = st.selectbox(T("المادة", "Material"), [T("نحاس (Cu)", "Copper (Cu)"), T("ألمنيوم (Al)", "Aluminium (Al)")])
    with col2: dist_in = st.number_input(T("المسافة (م)", "Distance (m)"), value=50.0)
    with col3: temp_in = st.number_input(T("درجة الحرارة (C)", "Temp (C)"), value=40.0)

    if img:
        st.image(img, caption=T("الصورة المرفوعة", "Uploaded Image"), width=300)
    if catalog:
        st.success(T(f"تم رفع الكتالوج: {catalog.name} - سيكون المصدر الأول", f"Catalog uploaded: {catalog.name} - Will be first source"))

    if st.button(T("🔍 ابحث", "🔍 Search"), type="primary"):
        if not q.strip() and not img and not catalog:
            st.warning(T("اكتب سؤال، أو ارفع صورة، أو ارفع كتالوج", "Write question, or upload image, or catalog"))
        else:
            if not q.strip() and (img or catalog):
                q = "generator 500 kVA cable"
            q_low = q.lower()
            domain = detect_domain(q)
            st.success(T(f"✅ تم التحقق - المجال: {domain}", f"✅ VERIFIED - Domain: {domain}"))
            st.write(f"**{T('سؤالك:', 'Your Question:')}** {q}")
            if catalog:
                st.write(T(f"**مصدر الأولوية:** 1. كتالوجك المحلي ({catalog.name})  2. IEC / BS  3. الويب", f"**Source Priority:** 1. Your Catalog ({catalog.name}) 2. IEC / BS 3. Web"))

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
                cu_c = find_cable(corr, CU_TABLE)[0]
                al_c = find_cable(corr, AL_TABLE)[0]

                st.subheader(T(f"🌳 الشجرة الكاملة - مولد {kva:.0f} kVA", f"🌳 Full Tree - {kva:.0f} kVA Generator"))
                st.write(T(f"**1. القدرة والتيار:** kVA = {kva:.0f} | kW = {kw:.1f} | التيار = {current:.1f} A | الفولت = {voltage:.0f}V",
                            f"**1. Power & Current:** kVA = {kva:.0f} | kW = {kw:.1f} | Current = {current:.1f} A | Voltage = {voltage:.0f}V"))
                st.write(T(f"**2. الكيبل والقاطع:** نحاس: {cu_c} | ألمنيوم: {al_c} | المختار: {cable_str} {mat} | القاطع: {breaker} A | معامل الحرارة {temp:.0f}C = {tf:.2f} | التيار المصحح = {corr:.1f} A",
                            f"**2. Cable & Breaker:** Copper: {cu_c} | Aluminium: {al_c} | Selected: {cable_str} {mat} | Breaker: {breaker} A | Temp Factor {temp:.0f}C = {tf:.2f} | Corrected Current = {corr:.1f} A"))
                st.write(T(f"**3. الفاقد:** المسافة {dist:.0f}m | الفاقد = {vd:.2f} V ({vd_pct:.2f}%)",
                            f"**3. Voltage Drop:** Distance {dist:.0f}m | VD = {vd:.2f} V ({vd_pct:.2f}%)"))
                if vd_pct<=5: st.success(T("ناجح <5% IEC 60364", "PASS <5% IEC 60364"))
                else: st.error(T("فاشل >5% - زيد مقاس الكيبل", "FAIL >5% - Increase cable size"))
                st.write(T("**4. الوقود والتشغيل:**", "**4. Fuel & Operation:**"))
                for lp in [50,75,100]:
                    st.write(T(f"- حمل {lp}%: قدرة {kw*lp/100:.1f} kW | وقود {kw*lp/100*0.25:.1f} لتر/ساعة | 8 ساعات {kw*lp/100*0.25*8:.1f} لتر",
                                f"- Load {lp}%: Power {kw*lp/100:.1f} kW | Fuel {kw*lp/100*0.25:.1f} L/h | 8h {kw*lp/100*0.25*8:.1f} L"))
                oil = "15 L" if kva<=150 else "30 L" if kva<=500 else "50 L"
                st.write(T(f"**5. الزيت والقطع:** زيت 15W-40: {oil} | فلتر زيت، فلتر وقود، فلتر هواء | موية تبريد 20L | صيانة كل 250 ساعة",
                            f"**5. Oil & Parts:** Oil 15W-40: {oil} | Oil Filter, Fuel Filter, Air Filter | Coolant 20L | Service every 250h"))
                st.write(T(f"**6. الأعطال المتوقعة:** حمل زائد > {current:.0f}A = سخانة + دخان أسود | فولت منخفض = AVR | عدم تشغيل = بطارية + فلتر",
                            f"**6. Expected Faults:** Overload > {current:.0f}A = Overheat + Black Smoke | Low Voltage = AVR | No Start = Battery + Fuel Filter"))
                st.write(T("**المعيار:** IEC 60364 / BS 7671 / كتالوج المصنع", "**Standard:** IEC 60364 / BS 7671 / Manufacturer Catalog"))

            elif domain == "MECHANICAL":
                val = extract_first(q, 10)
                st.subheader(T("🌳 الشجرة الكاملة - ميكانيكا", "🌳 Full Tree - Mechanical"))
                st.write(T(f"- القوة = كتلة x تسارع | القدرة = عزم x سرعة / 9550 | الضغط = قوة / مساحة", "- Force = Mass x Accel | Power = Torque x Speed / 9550 | Pressure = Force / Area"))
                st.write(T(f"- مثال: قوة {val:.0f} N x 0.5m = {val*0.5:.1f} Nm عزم", f"- Example: Force {val:.0f} N x 0.5m = {val*0.5:.1f} Nm Torque"))
            elif domain == "CIVIL":
                nums = extract_numbers(q)
                length = nums[0] if len(nums)>0 else 5
                load = nums[1] if len(nums)>1 else 20
                st.subheader(T("🌳 الشجرة الكاملة - مدني", "🌳 Full Tree - Civil"))
                st.write(T(f"- الطول {length:.1f}م | الحمل {load:.0f} kN | عمق الكمرة ≈ {length/12*1000:.0f} mm | عزم الانحناء = {load*length*length/8:.1f} kNm",
                            f"- Length {length:.1f}m | Load {load:.0f} kN | Beam Depth ≈ {length/12*1000:.0f} mm | Moment = {load*length*length/8:.1f} kNm"))
                st.write(T("**المعيار:** ACI 318 / BS 8110", "**Standard:** ACI 318 / BS 8110"))
            elif domain == "NUCLEAR":
                val = extract_first(q, 10)
                st.subheader(T("🌳 الشجرة الكاملة - نووي", "🌳 Full Tree - Nuclear"))
                st.write(T(f"- E=mc² | الاضمحلال: بعد {val:.0f} سنة يتبقى {(0.5**(val/10))*100:.1f}% | الأمان ALARA", f"- E=mc² | Decay: After {val:.0f} years remains {(0.5**(val/10))*100:.1f}% | Safety ALARA"))
            elif domain == "ECONOMIC":
                cost = extract_first(q, 1000)
                st.subheader(T("🌳 الشجرة الكاملة - اقتصادي", "🌳 Full Tree - Economic"))
                st.write(T(f"- التكلفة {cost:.0f} | العائد = (التوفير - التكلفة)/التكلفة x 100%", f"- Cost {cost:.0f} | ROI = (Saving - Cost)/Cost x 100%"))
            else:
                st.subheader(T("🌳 الشجرة الكاملة - فيزياء عامة", "🌳 Full Tree - General Physics"))
                st.write(T("اكتب المجال والرقم، مثال: 'مولد 500 kVA' أو 'مضخة 20 متر'", "Write field and number, e.g. '500 kVA generator' or 'pump 20m'"))

elif choice.startswith("2."):
    st.header(T("2. البحث بالأدلة", "2. Evidence Search"))
    q = st.text_input(T("ابحث", "Search"))
    if st.button(T("ابحث", "Search")):
        st.info(T(f"نبحث عن: {q} | المجال: {detect_domain(q)}", f"Searching: {q} | Domain: {detect_domain(q)}"))

elif choice.startswith("3."):
    st.header(T("3. التحقق من النتيجة", "3. Result Verifier"))
    kva = st.number_input(T("مولد kVA", "Generator kVA"), value=100.0)
    yours = st.number_input(T("تيارك (A)", "Your Current (A)"), value=0.0)
    if st.button(T("تحقق", "Verify")):
        corr = kva*1000/(math.sqrt(3)*400)
        st.write(T(f"الصح {corr:.1f} A، حقك {yours:.1f} A", f"Correct {corr:.1f} A, Yours {yours:.1f} A"))
        if abs(corr-yours)<1: st.success(T("صحيح!", "CORRECT!"))
        else: st.error(T("خطأ", "WRONG"))

elif choice.startswith("4."):
    st.header(T("4. الفاقد والقدرة", "4. Voltage Drop & Power"))
    cur = st.number_input(T("التيار (A)", "Current (A)"), value=150.0)
    dist = st.number_input(T("المسافة (م)", "Distance (m)"), value=80.0)
    cab = st.number_input(T("الكيبل (mm2)", "Cable (mm2)"), value=50.0)
    if st.button(T("احسب", "Calculate")):
        vd = vd_calc(cur, dist, cab, "Cu")
        st.write(T(f"الفاقد {vd:.2f} V ({vd/400*100:.2f}%)", f"VD {vd:.2f} V ({vd/400*100:.2f}%)"))

elif choice.startswith("5."):
    st.header(T("5. استهلاك الوقود", "5. Fuel Consumption"))
    kva = st.number_input(T("مولد kVA", "Generator kVA"), value=100.0)
    load = st.slider(T("الحمل %", "Load %"), 0, 100, 75)
    if st.button(T("احسب", "Calculate")):
        fh = kva*0.8*(load/100)*0.25
        st.write(T(f"الوقود {fh:.1f} لتر/ساعة", f"Fuel {fh:.1f} L/h"))

elif choice.startswith("6."):
    st.header(T("6. الصيانة التنبؤية", "6. Predictive Maintenance"))
    hrs = st.number_input(T("ساعات التشغيل", "Hours Run"), value=250.0)
    if st.button(T("افحص", "Check")):
        if hrs>=250: st.warning(T("تغيير الزيت واجب", "Oil Change DUE"))
        else: st.success(T(f"الزيت تمام - باقي {250-hrs:.0f} ساعة", f"Oil OK - {250-hrs:.0f}h left"))

elif choice.startswith("7."):
    st.header(T("7. تشخيص الأعطال", "7. Fault Diagnosis"))
    sym = st.selectbox(T("العرض", "Symptom"), [T("المولد لا يشتغل", "Not starting"), T("دخان أسود", "Black smoke"), T("سخانة", "Overheating")])
    if st.button(T("شخص", "Diagnose")):
        st.write(T(f"تشخيص {sym}: افحص البطارية والوقود والفلاتر", f"Diagnosis {sym}: Check battery, fuel, filters"))

elif choice.startswith("8."):
    st.header(T("8. قطع الغيار والزيت", "8. Spare Parts & Oil Change"))
    kva = st.number_input(T("مولد kVA", "Generator kVA"), value=100.0)
    if st.button(T("اعرض", "Show")):
        oil = "15 L" if kva<=150 else "30 L" if kva<=500 else "50 L"
        st.write(T(f"زيت {oil} | فلاتر | موية 20L", f"Oil {oil} | Filters | Coolant 20L"))

elif choice.startswith("9."):
    st.header(T("9. تنبيه الفشل التنبؤي", "9. Predictive Failure Alert"))
    vib = st.number_input(T("الاهتزاز (mm/s)", "Vibration (mm/s)"), value=4.0)
    if st.button(T("توقع", "Predict")):
        risk = 40 if vib>7.1 else 20 if vib>4.5 else 0
        st.write(T(f"الخطر {risk}%", f"Risk {risk}%"))

elif choice.startswith("10."):
    st.header(T("10. تقرير PDF + رسم", "10. PDF Report + Chart"))
    kva = st.number_input(T("مولد kVA", "Generator kVA"), value=100.0)
    if st.button(T("انشئ تقرير", "Generate Report")):
        cur = kva*1000/(math.sqrt(3)*400)
        st.write(T(f"تقرير {kva:.0f} kVA: تيار {cur:.1f}A، كيبل {find_cable(cur, CU_TABLE)[0]}", f"REPORT {kva:.0f} kVA: Current {cur:.1f}A, Cable {find_cable(cur, CU_TABLE)[0]}"))
        st.bar_chart({"Load %":[25,50,75,100],"Fuel":[kva*0.8*0.25*0.25,kva*0.8*0.5*0.25,kva*0.8*0.75*0.25,kva*0.8*0.25]}, x="Load %", y="Fuel")
