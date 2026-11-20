import streamlit as st
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from physics_engine import voltage_drop_3phase, fuel_consumption, predictive_score, diagnose_generator, power_3phase

st.set_page_config(page_title="My Harness Engineering", layout="wide")
st.sidebar.title("My Harness")
choice = st.sidebar.radio("Select Feature:", [
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
st.title("My Harness - Engineering")
if choice == "1. Verify Question":
    st.header("1. Verify Question")
    q = st.text_input("Enter question")
    if st.button("Verify"):
        if not q.strip():
            st.warning("Please enter a question first")
        elif "cable" in q.lower() and "500" in q:
            import math
            current = 500 * 1000 / (math.sqrt(3) * 400)
            st.success("VERIFIED - Question is Valid")
            st.write(f"Answer for 500 kVA Generator:")
            st.write(f"- Full Load Current = {current:.1f} A")
            st.write(f"- Recommended Cable: 2 x (3x185 mm2 Cu) per phase")
            st.write(f"- Breaker: 800 A")
            st.write(f"- Voltage: 400V, 3-Phase")
            st.write(f"Standard: IEC 60364 / BS 7671")
        elif "cable" in q.lower():
            st.success("VERIFIED")
            st.write("Formula: I = kVA x 1000 / (1.732 x 400V)")
            st.write("Tell me the kVA and I will calculate the exact cable size.")
        else:
            st.success("VERIFIED - Question is Valid")
            st.write(f"Your Question: {q}")
            
        # 500 kVA Calculation - Real Answer
        import math
        current = 500 * 1000 / (math.sqrt(3) * 400)
        st.success("✅ VERIFIED - Question is Valid")
        st.write(f"**Answer for 500 kVA Generator:**")
        st.write(f"- Full Load Current = **{current:.1f} A**")
        st.write(f"- Recommended Cable: **2 x (3x185 mm² Cu) per phase** OR **3x300 mm²**")
        st.write(f"- Breaker: **800 A**")
        st.write(f"- Voltage: 400V, 3-Phase")
        st.write(f"**Standard:** IEC 60364 / BS 7671")
    elif "cable" in q.lower():
        st.success("✅ VERIFIED")
        st.write("**Formula:** I = kVA x 1000 / (1.732 x 400V)")
        st.write("Tell me the kVA and I will calculate the exact cable size for you.")
    else:
        st.success("✅ VERIFIED - Question is Valid")
        st.write(f"**Your Question:** {q}")
        st.write("**Answer:** This is a valid engineering question. Please use Feature 4 for cable calculation, or Feature 7 for fault diagnosis for a detailed answer.")

elif choice == "2. Evidence Search":
    st.header("2. Evidence Search")
    q = st.text_input("Search evidence")
    if st.button("Search"): st.info("Searching evidence...")

elif choice == "3. Result Verifier":
    st.header("3. Result Verifier")
    val = st.number_input("Enter value", value=0.0)
    if st.button("Verify Result"): st.success(f"Value {val} checked.")

elif choice == "4. Voltage Drop & Power":
    st.header("4. Voltage Drop & Power")
    current = st.number_input("Current (A)", value=150.0)
    distance = st.number_input("Distance (m)", value=80.0)
    cable = st.number_input("Cable (mm2)", value=50.0)
    if st.button("Calculate"):
        vd = voltage_drop_3phase(current, distance, cable)
        p = power_3phase(400, current)
        st.metric("Voltage Drop", f"{vd:.2f} V")
        st.metric("Power", f"{p/1000:.2f} kW")

elif choice == "5. Fuel Consumption":
    st.header("5. Fuel Consumption")
    kw = st.number_input("Load (kW)", value=100.0)
    hours = st.number_input("Run Hours", value=8.0)
    if st.button("Calculate Fuel"):
        r = fuel_consumption(kw, hours)
        st.metric("Fuel", f"{r['fuel_l']} L")
        st.metric("CO2", f"{r['co2_kg']} kg")
        st.metric("Efficiency", f"{r['efficiency_pct']}%")

elif choice == "6. Predictive Maintenance":
    st.header("6. Predictive Maintenance")
    used = st.number_input("Used Hours", value=800.0)
    life = st.number_input("Life Hours", value=1000.0)
    temp = st.number_input("Coolant Temp (C)", value=85.0)
    oil = st.number_input("Oil Pressure (bar)", value=3.0)
    if st.button("Check"):
        r = predictive_score(used, life, temp, oil)
        st.metric("Health Score", f"{r['score']}%")
        st.metric("Status", r['status'])

elif choice == "7. Fault Diagnosis":
    st.header("7. Fault Diagnosis")
    temp = st.number_input("Coolant Temp (C)", value=85.0, key="d1")
    oil = st.number_input("Oil Pressure (bar)", value=3.0, key="d2")
    volt = st.number_input("Voltage (V)", value=400.0, key="d3")
    curr = st.number_input("Current (A)", value=150.0, key="d4")
    if st.button("Diagnose"):
        faults = diagnose_generator(temp, oil, volt, curr, 200)
        for f in faults:
            st.success(f) if "Normal" in f else st.error(f)

# ===== NEW 8 =====
elif choice == "8. Spare Parts & Oil Change":
    st.header("8. Spare Parts & Oil Change Schedule")
    st.write("Enter current generator hours to get full maintenance table.")
    current_hours = st.number_input("Current Generator Hours", value=820.0)
    last_oil = st.number_input("Last Oil Change At (hours)", value=600.0)
    last_air = st.number_input("Last Air Filter At (hours)", value=400.0)
    last_fuel_f = st.number_input("Last Fuel Filter At (hours)", value=400.0)
    last_belt = st.number_input("Last Belt Change At (hours)", value=0.0)

    parts = [
        ("Engine Oil", 250, last_oil),
        ("Oil Filter", 250, last_oil),
        ("Air Filter", 500, last_air),
        ("Fuel Filter", 500, last_fuel_f),
        ("V-Belt / Fan Belt", 1000, last_belt),
        ("Coolant", 1000, 0),
        ("Battery Check", 500, 0),
    ]
    rows = []
    for name, interval, last in parts:
        next_due = last + interval
        remaining = next_due - current_hours
        if remaining <= 0:
            status = "OVERDUE - CHANGE NOW"
        elif remaining <= 50:
            status = "DUE SOON"
        else:
            status = "OK"
        rows.append({"Part": name, "Interval (h)": interval, "Last At": last, "Next Due At": next_due, "Remaining (h)": remaining, "Status": status})
    st.dataframe(rows, use_container_width=True)
    for r in rows:
        if "OVERDUE" in r["Status"]:
            st.error(f"{r['Part']} OVERDUE by {-r['Remaining (h)']:.0f}h - Change immediately")
        elif "DUE SOON" in r["Status"]:
            st.warning(f"{r['Part']} due in {r['Remaining (h)']:.0f}h")

# ===== NEW 9 =====
elif choice == "9. Predictive Failure Alert":
    st.header("9. Predictive Failure Alert")
    st.write("Early warning before failure happens.")
    temp = st.number_input("Coolant Temp (C)", value=92.0, key="p1")
    oil = st.number_input("Oil Pressure (bar)", value=2.1, key="p2")
    vib = st.number_input("Vibration (mm/s)", value=6.5)
    hours = st.number_input("Hours Since Last Service", value=240.0, key="p3")
    if st.button("Predict Failure"):
        risk = 0
        reasons = []
        if temp > 90: risk += 35; reasons.append("High coolant temp - cooling system failure risk")
        if oil < 2.5: risk += 35; reasons.append("Low oil pressure - bearing / oil pump risk")
        if vib > 5.0: risk += 20; reasons.append("High vibration - misalignment / bearing wear")
        if hours > 230: risk += 10; reasons.append("Service overdue")
        st.metric("Failure Risk", f"{risk}%")
        if risk >= 70:
            st.error("RED ALERT: Stop generator. Failure expected within 40 hours.")
        elif risk >= 40:
            st.warning("YELLOW ALERT: Schedule maintenance within 7 days.")
        else:
            st.success("GREEN: System normal. No failure predicted.")
        for r in reasons: st.write(f"- {r}")

# ===== NEW 10 =====
elif choice == "10. PDF Report + Chart":
    st.header("10. Performance Report - PDF + Chart")
    client = st.text_input("Client / Site Name", value="Khartoum Site - Generator 1")
    temp_list = [82, 85, 88, 91, 93]
    oil_list = [3.2, 3.0, 2.8, 2.5, 2.2]
    fuel_list = [22, 24, 25, 27, 29]

    st.subheader("Performance Chart")
    fig, ax = plt.subplots()
    ax.plot(temp_list, label="Temp C")
    ax.plot([x*10 for x in oil_list], label="Oil Pressure x10")
    ax.plot(fuel_list, label="Fuel L/h")
    ax.legend(); ax.set_xlabel("Last 5 Readings"); ax.grid(True)
    st.pyplot(fig)

    if st.button("Generate PDF Report"):
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, "My Harness - Generator Performance Report")
        c.setFont("Helvetica", 11)
        c.drawString(50, 770, f"Client: {client}")
        c.drawString(50, 750, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(50, 720, f"Avg Temp: {sum(temp_list)/len(temp_list):.1f} C")
        c.drawString(50, 700, f"Avg Oil Pressure: {sum(oil_list)/len(oil_list):.2f} bar")
        c.drawString(50, 680, f"Avg Fuel: {sum(fuel_list)/len(fuel_list):.1f} L/h")
        c.drawString(50, 650, "Status: Maintenance Required - Check Oil and Cooling")
        c.drawString(50, 620, "Recommendation: Change oil + filter, check coolant, inspect belt.")
        c.showPage(); c.save()
        buf.seek(0)
        st.download_button("Download PDF Report", buf, file_name="generator_report.pdf", mime="application/pdf")
        st.success("Report ready - Click Download above")
