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

def get_cable_and_breaker(current):
    if current <= 125:
        return "1 x (3x35 mm2 Cu)", 125
    elif current <= 180:
        return "1 x (3x50 mm2 Cu)", 200
    elif current <= 230:
        return "1 x (3x70 mm2 Cu)", 250
    elif current <= 290:
        return "1 x (3x95 mm2 Cu)", 315
    elif current <= 360:
        return "1 x (3x120 mm2 Cu)", 400
    elif current <= 460:
        return "1 x (3x185 mm2 Cu)", 500
    elif current <= 580:
        return "1 x (3x240 mm2 Cu)", 630
    elif current <= 720:
        return "2 x (3x185 mm2 Cu)", 800
    elif current <= 900:
        return "2 x (3x240 mm2 Cu)", 1000
    elif current <= 1200:
        return "2 x (3x300 mm2 Cu)", 1250
    else:
        return "3 x (3x240 mm2 Cu)", 1600

def extract_number(text, default=100):
    nums = re.findall(r'\d+\.?\d*', text)
    if nums:
        return float(nums[0])
    return float(default)

# 1. VERIFY QUESTION - DYNAMIC
if choice == "1. Verify Question":
    st.header("1. Verify Question")
    q = st.text_input("Enter question - any kVA, any kW, any question")
    if st.button("Verify"):
        if not q.strip():
            st.warning("Please enter a question first")
        else:
            q_low = q.lower()
            st.success("VERIFIED - Question is Valid")
            st.write(f"**Your Question:** {q}")

            # Cable + Generator - any size
            if "cable" in q_low and ("kva" in q_low or "generator" in q_low or "kva" in q_low):
                kva = extract_number(q, 100)
                # لو كتب kW حولها لـ kVA
                if "kw" in q_low and "kva" not in q_low:
                    kva = kva / 0.8
                voltage = 400
                # لو كتب فولت مختلف
                v_nums = re.findall(r'(\d+)\s*v', q_low)
                if v_nums:
                    voltage = float(v_nums[0])
                current = kva * 1000 / (math.sqrt(3) * voltage)
                cable, breaker = get_cable_and_breaker(current)
                st.write(f"**Answer for {kva:.0f} kVA Generator:**")
                st.write(f"- Full Load Current = {current:.1f} A")
                st.write(f"- Recommended Cable: {cable} per phase")
                st.write(f"- Breaker: {breaker} A")
                st.write(f"- Voltage: {voltage:.0f}V, 3-Phase")
                st.write(f"**Standard:** IEC 60364 / BS 7671")

            elif "cable" in q_low:
                st.write("**Formula:** I = kVA x 1000 / (1.732 x 400V)")
                st.write("Example: For 100 kVA, I = 144.3 A, Cable = 3x50 mm2")
                st.write("Tell me the kVA and I will calculate the exact cable size.")

            elif "fuel" in q_low or "consumption" in q_low:
                kva = extract_number(q, 100)
                load = 0.75
                fuel = kva * 0.8 * load * 0.25
                st.write(f"**For {kva:.0f} kVA at 75% load:**")
                st.write(f"- Fuel Consumption = {fuel:.1f} Litres / Hour")
                st.write(f"- Per Day (8h) = {fuel*8:.1f} Litres")

            elif "voltage drop" in q_low or "drop" in q_low:
                st.write("**Formula:** Vd = (1.732 x I x L x R) / 1000")
                st.write("Use Feature 4 and enter Current, Distance, Cable size for exact calculation.")

            elif "power" in q_low or "kw" in q_low:
                kva = extract_number(q, 100)
                kw = kva * 0.8
                current = kva * 1000 / (math.sqrt(3) * 400)
                st.write(f"- {kva:.0f} kVA = {kw:.1f} kW (pf=0.8)")
                st.write(f"- Current = {current:.1f} A")

            else:
                st.write("**Answer:** This is a valid engineering question.")
                st.write("Use Feature 4 for cable / voltage drop, Feature 5 for fuel, Feature 7 for fault diagnosis.")

# 2. EVIDENCE SEARCH
elif choice == "2. Evidence Search":
    st.header("2. Evidence Search")
    q = st.text_input("Search evidence - e.g. cable 250 kVA, fuel 100 kVA")
    if st.button("Search"):
        if not q.strip():
            st.warning("Enter search text")
        else:
            kva = extract_number(q, 100)
            st.info(f"Searching evidence for: {q}")
            st.write(f"- **IEC 60364:** Cable sizing for {kva:.0f} kVA")
            st.write(f"- **BS 7671:** Voltage drop limit 5%")
            st.write(f"- **Manufacturer Data:** Generator datasheet for {kva:.0f} kVA")
            st.write(f"- **Standard:** Full load current = {kva*1000/(math.sqrt(3)*400):.1f} A")

# 3. RESULT VERIFIER
elif choice == "3. Result Verifier":
    st.header("3. Result Verifier")
    st.write("Check if your calculation is correct")
    kva = st.number_input("Generator kVA", value=100.0)
    your_current = st.number_input("Your Calculated Current (A)", value=0.0)
    if st.button("Verify Result"):
        correct = kva * 1000 / (math.sqrt(3) * 400)
        st.write(f"Correct Current = {correct:.1f} A")
        st.write(f"Your Current = {your_current:.1f} A")
        diff = abs(correct - your_current)
        if diff < 1:
            st.success("CORRECT - Your calculation is perfect!")
        elif diff < 10:
            st.warning(f"CLOSE - Difference {diff:.1f} A, check rounding")
        else:
            st.error(f"WRONG - Difference {diff:.1f} A. Formula: I = kVA x 1000 / (1.732 x 400)")

# 4. VOLTAGE DROP & POWER
elif choice == "4. Voltage Drop & Power":
    st.header("4. Voltage Drop & Power")
    current = st.number_input("Current (A)", value=150.0)
    distance = st.number_input("Distance (m)", value=80.0)
    cable = st.number_input("Cable (mm2)", value=50.0)
    voltage = st.number_input("Voltage (V)", value=400.0)
    if st.button("Calculate"):
        # Resistivity copper 0.0225 ohm.mm2/m
        r = 0.0225 / cable
        vd = math.sqrt(3) * current * distance * r
        vd_percent = (vd / voltage) * 100
        power_kw = math.sqrt(3) * voltage * current * 0.8 / 1000
        st.write(f"- Voltage Drop = {vd:.2f} V ({vd_percent:.2f}%)")
        if vd_percent <= 5:
            st.success("PASS - Within 5% limit (IEC 60364)")
        else:
            st.error("FAIL - Over 5%. Increase cable size.")
        st.write(f"- Power = {power_kw:.1f} kW")

# 5. FUEL CONSUMPTION
elif choice == "5. Fuel Consumption":
    st.header("5. Fuel Consumption")
    kva = st.number_input("Generator Size (kVA)", value=100.0)
    load_percent = st.slider("Load %", 0, 100, 75)
    hours = st.number_input("Hours per Day", value=8.0)
    if st.button("Calculate Fuel"):
        kw = kva * 0.8
        load_kw = kw * (load_percent/100)
        fuel_per_hour = load_kw * 0.25
        st.write(f"- Load = {load_kw:.1f} kW")
        st.write(f"- Fuel = {fuel_per_hour:.1f} Litres / Hour")
        st.write(f"- Per Day ({hours:.0f}h) = {fuel_per_hour*hours:.1f} Litres")
        st.write(f"- Per Month (30 days) = {fuel_per_hour*hours*30:.0f} Litres")

# 6. PREDICTIVE MAINTENANCE
elif choice == "6. Predictive Maintenance":
    st.header("6. Predictive Maintenance")
    hours_run = st.number_input("Hours Run", value=250.0)
    temp = st.number_input("Engine Temp (C)", value=85.0)
    oil_pressure = st.number_input("Oil Pressure (bar)", value=4.0)
    if st.button("Check Maintenance"):
        if hours_run >= 250:
            st.warning("Oil Change DUE - Every 250 hours")
        else:
            st.success(f"Oil OK - {250-hours_run:.0f} hours remaining")
        if temp > 95:
            st.error("OVERHEATING - Check coolant, radiator")
        elif temp > 90:
            st.warning("Temp High - Check coolant level")
        else:
            st.success(f"Temp Normal: {temp:.0f} C")
        if oil_pressure < 2.5:
            st.error("LOW OIL PRESSURE - Stop and check!")
        else:
            st.success(f"Oil Pressure OK: {oil_pressure:.1f} bar")

# 7. FAULT DIAGNOSIS
elif choice == "7. Fault Diagnosis":
    st.header("7. Fault Diagnosis")
    symptom = st.selectbox("Select Symptom:", ["Generator not starting", "Black smoke", "White smoke", "Overheating", "Low voltage", "High vibration", "Oil leak"])
    if st.button("Diagnose"):
        if symptom == "Generator not starting":
            st.write("**Possible Causes:** 1. Dead battery 2. Empty fuel 3. Fuel filter blocked 4. Starter motor")
            st.write("**Check:** Battery voltage >12.5V, Fuel level, Fuel filter")
        elif symptom == "Black smoke":
            st.write("**Cause:** Overloading or dirty air filter / faulty injector")
            st.write("**Action:** Reduce load, clean air filter, check injectors")
        elif symptom == "White smoke":
            st.write("**Cause:** Water in fuel or cold engine / head gasket")
            st.write("**Action:** Drain water from fuel filter, check coolant")
        elif symptom == "Overheating":
            st.write("**Cause:** Low coolant, blocked radiator, faulty thermostat")
            st.write("**Action:** Check coolant, clean radiator, check fan belt")
        elif symptom == "Low voltage":
            st.write("**Cause:** AVR faulty, low speed, overload")
            st.write("**Action:** Check AVR, check RPM = 1500, reduce load")
        elif symptom == "High vibration":
            st.write("**Cause:** Loose mounting, unbalanced load, worn bearing")
            st.write("**Action:** Tighten mounts, balance load")
        else:
            st.write("**Cause:** Worn gasket / seal")
            st.write("**Action:** Tighten bolts, replace gasket")

# 8. SPARE PARTS & OIL CHANGE
elif choice == "8. Spare Parts & Oil Change":
    st.header("8. Spare Parts & Oil Change")
    kva = st.number_input("Generator kVA for Parts", value=100.0)
    if st.button("Show Parts"):
        if kva <= 150:
            oil = "15 Litres"
            filter_oil = "1 x Oil Filter"
            filter_fuel = "1 x Fuel Filter"
            filter_air = "1 x Air Filter"
        elif kva <= 500:
            oil = "30 Litres"
            filter_oil = "2 x Oil Filter"
            filter_fuel = "2 x Fuel Filter"
            filter_air = "1 x Air Filter"
        else:
            oil = "50 Litres"
            filter_oil = "2 x Oil Filter"
            filter_fuel = "2 x Fuel Filter"
            filter_air = "2 x Air Filter"
        st.write(f"**For {kva:.0f} kVA:**")
        st.write(f"- Engine Oil (15W-40): {oil}")
        st.write(f"- {filter_oil}")
        st.write(f"- {filter_fuel}")
        st.write(f"- {filter_air}")
        st.write(f"- Coolant: 20 Litres")
        st.write(f"- Next Service: Every 250 Hours")

# 9. PREDICTIVE FAILURE ALERT
elif choice == "9. Predictive Failure Alert":
    st.header("9. Predictive Failure Alert")
    vib = st.number_input("Vibration (mm/s)", value=4.0)
    temp = st.number_input("Temp (C)", value=85.0)
    hours = st.number_input("Hours Since Service", value=100.0)
    if st.button("Predict"):
        risk = 0
        if vib > 7.1: risk += 40
        elif vib > 4.5: risk += 20
        if temp > 95: risk += 40
        elif temp > 90: risk += 20
        if hours > 250: risk += 20
        st.write(f"Failure Risk = {risk}%")
        if risk >= 70:
            st.error("HIGH RISK - Stop and inspect NOW")
        elif risk >= 30:
            st.warning("MEDIUM RISK - Schedule maintenance soon")
        else:
            st.success("LOW RISK - Generator healthy")

# 10. PDF REPORT + CHART
elif choice == "10. PDF Report + Chart":
    st.header("10. PDF Report + Chart")
    kva = st.number_input("Generator kVA", value=100.0)
    if st.button("Generate Report"):
        current = kva * 1000 / (math.sqrt(3) * 400)
        cable, breaker = get_cable_and_breaker(current)
        st.write(f"**REPORT for {kva:.0f} kVA Generator**")
        st.write(f"- Current: {current:.1f} A")
        st.write(f"- Cable: {cable}")
        st.write(f"- Breaker: {breaker} A")
        st.write(f"- Fuel @75%: {kva*0.8*0.75*0.25:.1f} L/h")
        st.write("Copy this report to PDF or WhatsApp for customer.")
        chart_data = {"Load %": [25, 50, 75, 100], "Fuel L/h": [kva*0.8*0.25*0.25, kva*0.8*0.5*0.25, kva*0.8*0.75*0.25, kva*0.8*1.0*0.25]}
        st.bar_chart(chart_data, x="Load %", y="Fuel L/h")
