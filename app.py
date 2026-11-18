import streamlit as st
from physics_engine import voltage_drop_3phase, fuel_consumption, predictive_score, diagnose_generator, power_3phase, torque_from_power

st.set_page_config(page_title="My Harness - Engineering", layout="wide")
st.title("⚡ My Harness - Engineering + Verify-First")

# ===== الميزات القديمة 3 - زي ما هي =====
tab_old, tab_new = st.tabs(["الميزات القديمة 3", "الميزات الهندسية الجديدة 4"])

with tab_old:
    st.subheader("1. Verify-First - التحقق")
    q = st.text_input("اكتب سؤال للتحقق", key="old1")
    if st.button("تحقق"):
        st.info("Verify-First شغال - جاري التحقق...")

    st.subheader("2. Evidence - الأدلة")
    st.write("جلب الأدلة من الإنترنت - شغال")

    st.subheader("3. Verifier - المدقق")
    st.write("مدقق النتائج - شغال")

# ===== الميزات الجديدة 4 - دي الكانت ما ظاهرة =====
with tab_new:
    st.subheader("4. حساب المولد - هبوط الجهد + قدرة")
    c1, c2, c3 = st.columns(3)
    cur = c1.number_input("التيار A", value=150.0)
    dist = c2.number_input("المسافة m", value=80.0)
    cable = c3.number_input("الكابل mm2", value=50.0)
    if st.button("احسب هبوط الجهد"):
        vd = voltage_drop_3phase(cur, dist, cable)
        p = power_3phase(400, cur)
        st.success(f"هبوط الجهد = {vd:.2f} V | القدرة = {p/1000:.2f} kW")

    st.subheader("5. استهلاك الوقود - Fuel")
    kw = st.number_input("الحمل kW", value=100.0)
    hrs = st.number_input("ساعات التشغيل", value=8.0)
    if st.button("احسب الوقود"):
        r = fuel_consumption(kw, hrs)
        st.success(f"وقود = {r['fuel_l']} L | CO2 = {r['co2_kg']} kg | كفاءة = {r['efficiency_pct']}%")

    st.subheader("6. الصيانة التنبؤية")
    u = st.number_input("ساعات مستخدمة", value=800.0)
    life = st.number_input("عمر المولد", value=1000.0)
    temp = st.number_input("حرارة المبرد C", value=85.0)
    oil = st.number_input("ضغط الزيت bar", value=3.0)
    if st.button("افحص الصيانة"):
        r = predictive_score(u, life, temp, oil)
        st.warning(f"Score = {r['score']}% | الحالة: {r['status']} | متبقي: {r['remaining_hours']}h")

    st.subheader("7. تشخيص الأعطال")
    if st.button("شخص العطل"):
        faults = diagnose_generator(temp, oil, 400, cur, 200)
        for f in faults:
            st.error(f) if "System Normal" not in f else st.success(f)
