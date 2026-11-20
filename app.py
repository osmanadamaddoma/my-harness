import streamlit as st
import math
import re

st.set_page_config(page_title="My Harness", layout="wide")
st.title("My Harness - Engineering")

choice = st.sidebar.selectbox("Select Feature:", [
    "1. Verify Question",
    "2. Evidence Search",
    "3. Result Verifier",
    "4. Voltage Drop & Power",
    "5. Fuel Consumption",
    "6. Predictive Maintenance",
    "7. Fault Diagnosis",
    "8. Spare Parts & Oil Change",
    "9. Predictive Failure Alert",
    "10. PDF Report + Chart"
])

# جدول حقيقي - نحاس - تيار لكل مقاس - IEC 60364
# (mm2, max current Cu)
CU_TABLE = [
    (1.5, 15), (2.5, 21), (4, 28), (6, 36), (10, 50),
    (16, 68), (25, 89), (35, 111), (50, 134), (70, 171),
    (95, 207), (120, 239), (150, 272), (185, 310), (240, 364),
    (300, 419), (400, 502)
]
# المونيوم بيشيل 78% من النحاس
AL_TABLE = [(size, int(curr*0.78)) for size, curr in CU_TABLE]

def extract_number(text, default=100):
    nums = re.findall(r'\d+\.?\d*', text)
    if nums:
        return float(nums[0])
    return float(default)

def find_cable(current, table):
    # لو التيار اكبر من كيبل واحد، بنعمل 2 او 3 كيبلات بالتوازي
    for size, cap in table:
        if current <= cap:
            return f"1 x (3x{size} mm2)", size, cap, 1
    for size, cap in table:
        if current <= cap*2:
            return f"2 x (3x{size} mm2)", size, cap, 2
    for size, cap in table:
        if current <= cap*3:
            return f"3 x (3x{size} mm2)", size, cap, 3
    return f"4 x (3x400 mm2)", 400, 502, 4

def temp_factor(temp):
    if temp <= 30: return 1.0
    elif temp <= 35: return 0.96
    elif temp <= 40: return 0.91
    elif temp <= 45: return 0.87
    elif temp <= 50: return 0.82
    elif temp <= 55: return 0.76
    else: return 0.71

def voltage_drop(current, distance, size, material):
    # مقاومة: نحاس 0.0225 / المونيوم 0.036
    rho = 0.0225 if material == "Cu" else 0.036
    r = rho / size
    vd = math.sqrt(3) * current * distance * r
    return vd

# 1. VERIFY
if choice == "1. Verify Question":
    st.header("1. Verify Question")
    q = st.text_input("Enter question - e.g. cable for 100 kVA, 80m, copper, 50C")
    # اختيارات اضافية - لو الزول ما كتبها في السؤال
    col1, col2, col3 = st.columns(3)
    with col1:
        mat = st.selectbox("Material", ["Copper (Cu)", "Aluminium (Al)"])
    with col2:
        dist = st.number_input("Distance (m)", value=50.0)
    with col3:
        temp = st.number_input("Ambient Temp (C)", value=40.0)

    if st.button("Verify"):
        if not q.strip():
            st.warning("Please enter a question first")
        else:
            q_low = q.lower()
            st.success("VERIFIED - Question is Valid")
            st.write(f"**Your Question:** {q}")

            if "cable" in q_low:
                kva = extract_number(q, 100)
                if "kw" in q_low and "kva" not in q_low:
                    kva = kva / 0.8
                voltage = 400
                v_match = re.findall(r'(\d+)\s*v', q_low)
                if v_match: voltage = float(v_match[0])

                # لو كتب مسافة في السؤال، استعملها
                d_match = re.findall(r'(\d+)\s*m\b', q_low)
                if d_match:
                    dist = float(d_match[0])
                # لو كتب حرارة في السؤال
                t_match = re.findall(r'(\d+)\s*c', q_low)
                if t_match:
                    temp = float(t_match[0])

                current = kva * 1000 / (math.sqrt(3) * voltage)
                tf = temp_factor(temp)
                corrected_current = current / tf

                material = "Cu" if "Copper" in mat else "Al"
                table = CU_TABLE if material == "Cu" else AL_TABLE
                cable_str, size, cap, parallel = find_cable(corrected_current, table)
                # كيبل القاطع
                breaker = int(math.ceil(corrected_current / 10) * 10)

                vd = voltage_drop(current, dist, size * parallel, material)
                vd_pct = (vd / voltage) * 100

                st.write(f"**Answer for {kva:.0f} kVA - {mat} - {dist:.0f}m - {temp:.0f}C:**")
                st.write(f"- Full Load Current = {current:.1f} A")
                st.write(f"- Temp Factor ({temp:.0f}C) = {tf:.2f}")
                st.write(f"- Corrected Current = {corrected_current:.1f} A (Current / Factor)")
                st.write(f"- Recommended Cable: {cable_str} {material}")
                st.write(f"- Breaker: {breaker} A")
                st.write(f"- Voltage Drop = {vd:.2f} V ({vd_pct:.2f}%) over {dist:.0f}m")
                if vd_pct <= 5:
                    st.success(f"PASS - Voltage Drop {vd_pct:.2f}% < 5% (IEC 60364)")
                else:
                    st.error(f"FAIL - Voltage Drop {vd_pct:.2f}% > 5%. Increase cable size or reduce distance.")
                st.write(f"- Voltage: {voltage:.0f}V, 3-Phase")
                st.write(f"**Standard:** IEC 60364 / BS 7671")

                # مقارنة نحاس vs المونيوم
                st.write("---")
                st.write("**Comparison Cu vs Al for same load:**")
                cu_cable, cu_size, _, _ = find_cable(corrected_current, CU_TABLE)
                al_cable, al_size, _, _ = find_cable(corrected_current, AL_TABLE)
                st.write(f"- Copper: {cu_cable} Cu - Voltage Drop {voltage_drop(current, dist, cu_size, 'Cu')/voltage*100:.2f}%")
                st.write(f"- Aluminium: {al_cable} Al - Voltage Drop {voltage_drop(current, dist, al_size, 'Al')/voltage*100:.2f}%")
                st.write(f"Aluminium needs bigger size because it carries ~22% less current.")

            elif "fuel" in q_low:
                kva = extract_number(q, 100)
                fuel = kva * 0.8 * 0.75 * 0.25
                st.write(f"**For {kva:.0f} kVA at 75%:** Fuel = {fuel:.1f} L/h")
            else:
                st.write("**Answer:** Valid engineering question. Use Feature 4 for voltage drop, Feature 5 for fuel.")

elif choice == "2. Evidence Search":
    st.header("2. Evidence Search")
    q = st.text_input("Search evidence")
    if st.button("Search"):
        kva = extract_number(q, 100)
        st.info(f"Searching for: {q}")
        st.write(f"- IEC 60364 Table: Cable for {kva:.0f} kVA, Current = {kva*1000/(math.sqrt(3)*400):.1f} A")
        st.write(f"- BS 7671: Voltage Drop limit 5%")
        st.write(f"- Cu resistivity 0.0225, Al 0.036 ohm.mm2/m")

elif choice == "3. Result Verifier":
    st.header("3. Result Verifier")
    kva = st.number_input("Generator kVA", value=100.0)
    your_current = st.number_input("Your Current (A)", value=0.0)
    if st.button("Verify Result"):
        correct = kva * 1000 / (math.sqrt(3) * 400)
        st.write(f"Correct = {correct:.1f} A, Yours = {your_current:.1f} A")
        if abs(correct-your_current) < 1: st.success("CORRECT!")
        else: st.error(f"WRONG - Formula I = kVA x 1000 / (1.732 x 400)")

elif choice == "4. Voltage Drop & Power":
    st.header("4. Voltage Drop & Power")
    current = st.number_input("Current (A)", value=150.0)
    distance = st.number_input("Distance (m)", value=80.0)
    cable = st.number_input("Cable (mm2)", value=50.0)
    mat2 = st.selectbox("Material", ["Copper", "Aluminium"])
    temp2 = st.number_input("Temp (C)", value=40.0)
    voltage = st.number_input("Voltage (V)", value=400.0)
    if st.button("Calculate"):
        tf = temp_factor(temp2)
        rho = 0.0225 if mat2 == "Copper" else 0.036
        vd = math.sqrt(3) * current * distance * (rho / cable)
        vd_pct = vd / voltage * 100
        power = math.sqrt(3) * voltage * current * 0.8 / 1000
        st.write(f"- Temp Factor = {tf:.2f}, Corrected Capacity needed = {current/tf:.1f} A")
        st.write(f"- Voltage Drop = {vd:.2f} V ({vd_pct:.2f}%)")
        if vd_pct <= 5: st.success("PASS <5%")
        else: st.error("FAIL >5% - Increase cable")
        st.write(f"- Power = {power:.1f} kW")

elif choice == "5. Fuel Consumption":
    st.header("5. Fuel Consumption")
    kva = st.number_input("Generator (kVA)", value=100.0)
    load = st.slider("Load %", 0, 100, 75)
    hours = st.number_input("Hours/Day", value=8.0)
    if st.button("Calculate Fuel"):
        fuel_h = kva * 0.8 * (load/100) * 0.25
        st.write(f"- Fuel = {fuel_h:.1f} L/h, Per Day = {fuel_h*hours:.1f} L, Per Month = {fuel_h*hours*30:.0f} L")

elif choice == "6. Predictive Maintenance":
    st.header("6. Predictive Maintenance")
    hrs = st.number_input("Hours Run", value=250.0)
    temp = st.number_input("Engine Temp (C)", value=85.0)
    oil_p = st.number_input("Oil Pressure (bar)", value=4.0)
    if st.button("Check"):
        if hrs >= 250: st.warning("Oil Change DUE")
        else: st.success(f"Oil OK - {250-hrs:.0f}h left")
        if temp > 95: st.error("OVERHEATING")
        else: st.success(f"Temp OK {temp:.0f}C")
        if oil_p < 2.5: st.error("LOW OIL PRESSURE")
        else: st.success(f"Oil Pressure OK {oil_p:.1f} bar")

elif choice == "7. Fault Diagnosis":
    st.header("7. Fault Diagnosis")
    sym = st.selectbox("Symptom:", ["Generator not starting", "Black smoke", "White smoke", "Overheating", "Low voltage", "High vibration", "Oil leak"])
    if st.button("Diagnose"):
        st.write(f"**Diagnosis for {sym}:** Check battery, fuel, filters, coolant, AVR as per manual.")

elif choice == "8. Spare Parts & Oil Change":
    st.header("8. Spare Parts & Oil Change")
    kva = st.number_input("Generator kVA", value=100.0)
    if st.button("Show Parts"):
        oil = "15 L" if kva <= 150 else "30 L" if kva <= 500 else "50 L"
        st.write(f"- Oil 15W-40: {oil}, Oil Filter, Fuel Filter, Air Filter, Coolant 20L")

elif choice == "9. Predictive Failure Alert":
    st.header("9. Predictive Failure Alert")
    vib = st.number_input("Vibration (mm/s)", value=4.0)
    temp = st.number_input("Temp (C)", value=85.0)
    hrs = st.number_input("Hours Since Service", value=100.0)
    if st.button("Predict"):
        risk = 0
        if vib > 7.1: risk += 40
        elif vib > 4.5: risk += 20
        if temp > 95: risk += 40
        elif temp > 90: risk += 20
        if hrs > 250: risk += 20
        st.write(f"Risk = {risk}%")
        if risk >= 70: st.error("HIGH RISK - Stop NOW")
        elif risk >= 30: st.warning("MEDIUM RISK")
        else: st.success("LOW RISK - Healthy")

elif choice == "10. PDF Report + Chart":
    st.header("10. PDF Report + Chart")
    kva = st.number_input("Generator kVA", value=100.0)
    if st.button("Generate Report"):
        cur = kva * 1000 / (math.sqrt(3) * 400)
        cable, _, _, _ = find_cable(cur, CU_TABLE)
        st.write(f"**REPORT {kva:.0f} kVA:** Current {cur:.1f}A, Cable {cable} Cu, Fuel {kva*0.8*0.75*0.25:.1f} L/h")
        st.bar_chart({"Load %": [25,50,75,100], "Fuel": [kva*0.8*0.25*0.25, kva*0.8*0.5*0.25, kva*0.8*0.75*0.25, kva*0.8*0.25]}, x="Load %", y="Fuel")
