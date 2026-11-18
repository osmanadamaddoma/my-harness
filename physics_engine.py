import math

# ===== 1. معادلاتك الأصلية - رجعناها زي ما هي =====

def voltage_drop_3phase(current_a, distance_m, cable_mm2, cos_phi=0.8, rho=0.0175):
    """هبوط الجهد 3-phase - من كودك الأصلي"""
    if cable_mm2 <= 0:
        return 0
    return (math.sqrt(3) * current_a * distance_m * rho * cos_phi) / cable_mm2

def fuel_consumption(kw_load, run_hours, gen_model="Cummins"):
    """استهلاك الوقود - من جدول Perkins / Cummins"""
    # SFC L/kWh تقريبي حسب الحمل
    if kw_load <= 0:
        return {"fuel_l": 0, "co2_kg": 0, "efficiency": 0}
    # استيفاء بسيط: كلما زاد الحمل قل الاستهلاك النوعي
    sfc = 0.32 - (0.08 * min(kw_load / 500, 1.0))  # L/kWh
    fuel = sfc * kw_load * run_hours
    co2 = fuel * 2.68
    efficiency = min(38, 28 + (kw_load / 500) * 10)
    return {"fuel_l": round(fuel, 2), "co2_kg": round(co2, 2), "efficiency_pct": round(efficiency, 1), "sfc": round(sfc, 3)}

def predictive_score(used_hours, life_hours, coolant_temp, oil_press):
    """الصيانة التنبؤية - من كودك الأصلي"""
    wear = (used_hours / life_hours) * 100 if life_hours > 0 else 0
    score = 100 - wear
    if coolant_temp >= 95:
        score -= 30
    elif coolant_temp >= 88:
        score -= 15
    if oil_press <= 1.8:
        score -= 30
    elif oil_press <= 2.5:
        score -= 10
    status = "OK" if score > 70 else "WARNING" if score > 40 else "CRITICAL - STOP"
    remaining = max(0, life_hours - used_hours)
    return {"score": round(max(0, score), 1), "wear_pct": round(wear, 1), "remaining_hours": remaining, "status": status}

def diagnose_generator(coolant_temp, oil_press, voltage, current_a, rated_current):
    """تشخيص قواعد حقيقي"""
    faults = []
    if coolant_temp >= 95:
        faults.append("OVERHEAT: Coolant >= 95C - Check radiator / fan")
    if oil_press <= 1.8:
        faults.append("LOW OIL PRESSURE: Stop engine - Check oil level")
    if voltage < 360:
        faults.append("LOW VOLTAGE: AVR fault")
    if rated_current > 0 and current_a > rated_current:
        faults.append("OVERCURRENT: Load exceeds rated current")
    return faults if faults else ["System Normal"]

# ===== 2. فيزياء عامة للمسابقة - ده الكان ناقص =====

def power_3phase(voltage, current_a, pf=0.8):
    return math.sqrt(3) * voltage * current_a * pf

def torque_from_power(power_w, rpm):
    if rpm <= 0:
        return 0
    omega = (2 * math.pi * rpm) / 60
    return power_w / omega

def force_newton(mass, accel):
    return mass * accel

def kinetic_energy(mass, velocity):
    return 0.5 * mass * velocity**2

def heat_energy(mass, specific_heat, delta_t):
    return mass * specific_heat * delta_t

def bernoulli_pressure(density, velocity, height, p0=101325):
    g = 9.81
    return p0 + 0.5 * density * velocity**2 + density * g * height

def ohms_law(v=None, i=None, r=None):
    if v is None and i is not None and r is not None:
        return i * r
    if i is None and v is not None and r is not None:
        return v / r if r != 0 else 0
    if r is None and v is not None and i is not None:
        return v / i if i != 0 else 0
    return 0
