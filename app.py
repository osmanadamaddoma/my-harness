import streamlit as st
from physics_engine import voltage_drop_3phase, fuel_consumption, predictive_score, diagnose_generator, power_3phase, torque_from_power

st.set_page_config(page_title="My Harness Engineering", layout="wide")

st.sidebar.title("My Harness")
st.sidebar.markdown("Engineering Harness")
choice = st.sidebar.radio("Select Feature:", [
    "1. Verify Question",
    "2. Evidence Search",
    "3. Result Verifier",
    "4. Generator - Voltage Drop & Power",
    "5. Generator - Fuel Consumption",
    "6. Predictive Maintenance",
    "7. Fault Diagnosis"
])

st.title("My Harness - Engineering")

# --- OLD 1 ---
if choice == "1. Verify Question":
    st.header("1. Verify Question")
    st.write("Verify any claim with evidence.")
    q = st.text_input("Enter question")
    if st.button("Verify"):
        st.success(f"Checking: {q}")

# --- OLD 2 ---
elif choice == "2. Evidence Search":
    st.header("2. Evidence Search")
    st.write("Search evidence from web sources.")
    q = st.text_input("Search evidence")
    if st.button("Search"):
        st.info("Searching evidence...")

# --- OLD 3 ---
elif choice == "3. Result Verifier":
    st.header("3. Result Verifier")
    st.write("Verify calculation result.")
    val = st.number_input("Enter value to verify", value=0.0)
    if st.button("Verify Result"):
        st.success(f"Value {val} checked.")

# --- NEW 4 ---
elif choice == "4. Generator - Voltage Drop & Power":
    st.header("4. Generator - Voltage Drop & Power")
    st.write("Calculate voltage drop and 3-phase power for generator.")
    current = st.number_input("Current (A)", value=150.0)
    distance = st.number_input("Distance (m)", value=80.0)
    cable = st.number_input("Cable Size (mm2)", value=50.0)
    voltage = st.number_input("Voltage (V)", value=400.0)
    if st.button("Calculate"):
        vd = voltage_drop_3phase(current, distance, cable)
        p = power_3phase(voltage, current)
        st.metric("Voltage Drop", f"{vd:.2f} V")
        st.metric("Power", f"{p/1000:.2f} kW")
        st.code(f"Vd = sqrt(3)*I*L*rho*cos_phi / A = {vd:.2f} V")

# --- NEW 5 ---
elif choice == "5. Generator - Fuel Consumption":
    st.header("5. Generator - Fuel Consumption")
    kw = st.number_input("Load (kW)", value=100.0)
    hours = st.number_input("Run Hours", value=8.0)
    if st.button("Calculate Fuel"):
        r = fuel_consumption(kw, hours)
        st.metric("Fuel", f"{r['fuel_l']} L")
        st.metric("CO2", f"{r['co2_kg']} kg")
        st.metric("Efficiency", f"{r['efficiency_pct']}%")

# --- NEW 6 ---
elif choice == "6. Predictive Maintenance":
    st.header("6. Predictive Maintenance")
    used = st.number_input("Used Hours", value=800.0)
    life = st.number_input("Life Hours", value=1000.0)
    temp = st.number_input("Coolant Temp (C)", value=85.0)
    oil = st.number_input("Oil Pressure (bar)", value=3.0)
    if st.button("Check Maintenance"):
        r = predictive_score(used, life, temp, oil)
        st.metric("Health Score", f"{r['score']}%")
        st.metric("Status", r['status'])
        st.metric("Remaining Hours", f"{r['remaining_hours']}h")

# --- NEW 7 ---
elif choice == "7. Fault Diagnosis":
    st.header("7. Fault Diagnosis")
    st.write("Diagnose generator faults from sensors.")
    temp = st.number_input("Coolant Temp (C)", value=85.0, key="diag_temp")
    oil = st.number_input("Oil Pressure (bar)", value=3.0, key="diag_oil")
    volt = st.number_input("Voltage (V)", value=400.0, key="diag_volt")
    curr = st.number_input("Current (A)", value=150.0, key="diag_curr")
    rated = st.number_input("Rated Current (A)", value=200.0)
    if st.button("Diagnose"):
        faults = diagnose_generator(temp, oil, volt, curr, rated)
        for f in faults:
            if "Normal" in f:
                st.success(f)
            else:
                st.error(f)
