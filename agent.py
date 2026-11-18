from physics_engine import *
import re

def extract_numbers(text):
    return [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", text)]

def solve(question: str) -> str:
    q = question.lower()
    nums = extract_numbers(question)

    # مولد - هبوط جهد
    if "voltage drop" in q or "هبوط" in q or "v_drop" in q:
        # نتوقع: current, distance, cable
        if len(nums) >= 3:
            v = voltage_drop_3phase(nums[0], nums[1], nums[2])
            return f"Voltage Drop = {v:.2f} V | Formula: Vd = sqrt(3)*I*L*rho*cos_phi / A"

    # قدرة 3-phase
    if "3-phase" in q or "power" in q or "قدرة" in q and "voltage" in q:
        if len(nums) >= 2:
            p = power_3phase(nums[0], nums[1])
            return f"3-Phase Power = {p:.2f} W = {p/1000:.2f} kW"

    # عزم
    if "torque" in q or "عزم" in q:
        if len(nums) >= 2:
            t = torque_from_power(nums[0], nums[1])
            return f"Torque = {t:.2f} N.m | T = P / omega, omega = 2*pi*RPM/60"

    # قوة نيوتن
    if "force" in q or "f=ma" in q or "قوة" in q:
        if len(nums) >= 2:
            f = force_newton(nums[0], nums[1])
            return f"Force = {f:.2f} N | F = m*a"

    # طاقة حركية
    if "kinetic" in q or "طاقة حركية" in q:
        if len(nums) >= 2:
            ke = kinetic_energy(nums[0], nums[1])
            return f"Kinetic Energy = {ke:.2f} J | KE = 0.5*m*v^2"

    # وقود مولد
    if "fuel" in q or "وقود" in q:
        if len(nums) >= 2:
            r = fuel_consumption(nums[0], nums[1])
            return f"Fuel = {r['fuel_l']} L, CO2 = {r['co2_kg']} kg, Efficiency = {r['efficiency_pct']}%"

    # صيانة تنبؤية
    if "predictive" in q or "صيانة" in q:
        if len(nums) >= 4:
            r = predictive_score(nums[0], nums[1], nums[2], nums[3])
            return f"Predictive Score = {r['score']}% | Status: {r['status']} | Remaining: {r['remaining_hours']}h"

    return "I need numbers and a clear physics / generator question. Example: Calculate 3-phase power for 400V, 100A"
