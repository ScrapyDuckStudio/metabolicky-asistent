import streamlit as st

from translation import TRANSLATIONS

ACTIVITY_MULTIPLIERS = {
    0: 1.2,
    1: 1.375,
    2: 1.55,
    3: 1.725,
}


def get_lang():
    if "lang" not in st.session_state:
        st.session_state.lang = "SK"
    return st.session_state.lang


def txt(key: str) -> str:
    lang = get_lang()
    return TRANSLATIONS.get(lang, {}).get(key, key)


def calculate_water_target(weight: float, has_hyper: bool = False, has_hypertension: bool = False) -> float:
    base = weight * 0.033
    if has_hyper:
        base *= 1.2
    if has_hypertension:
        base *= 1.1
    return round(base, 1)


def calculate_bmi(weight: float, height: float) -> float:
    if height <= 0:
        return 0.0
    return round(weight / ((height / 100) ** 2), 1)


def bmi_category(bmi: float, lang: str) -> str:
    if lang == "SK":
        if bmi < 18.5:
            return "Podváha"
        if bmi < 25.0:
            return "Normálna váha"
        if bmi < 30.0:
            return "Nadváha"
        return "Obezita"
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25.0:
        return "Normal weight"
    if bmi < 30.0:
        return "Overweight"
    return "Obese"


def progress_bar_html(value, target, unit="", label=""):
    pct = min(int((value / target * 100) if target > 0 else 0), 150)
    over = pct >= 100
    fill_pct = min(pct, 100)
    bar_color = "linear-gradient(90deg,#f59e0b,#fb7185)" if over else "linear-gradient(90deg,#0f766e,#2dd4bf)"
    status_color = "#fb7185" if over else ("#10b981" if fill_pct >= 80 else "#f59e0b" if fill_pct >= 50 else "#9fb7b3")
    status_text = f"{pct}%"
    display_label = label if label else unit
    return (
        f'<div style="margin-bottom:14px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:5px;">'
        f'<span style="font-size:0.85rem;font-weight:600;color:#ccfbf1;">{display_label}</span>'
        f'<span style="font-size:0.8rem;color:{status_color};font-weight:700;">'
        f'{value} {unit} <span style="color:#6b8a85;font-weight:400;">/ {target} {unit}</span>'
        f' &nbsp;·&nbsp; {status_text}</span>'
        f'</div>'
        f'<div style="background:rgba(45,212,191,0.08);border-radius:999px;height:8px;">'
        f'<div style="width:{fill_pct}%;height:8px;border-radius:999px;background:{bar_color};transition:width 0.5s ease;"></div>'
        f'</div>'
        f'</div>'
    )


def get_metabolism_status(t_cal, target_cal, t_prot, target_protein,
                          t_fiber, has_pcos, has_hashi, t_iron, t_zinc,
                          t_risks, t_water, target_water):
    if t_cal == 0 and t_prot == 0:
        return 0, "empty"

    issues = 0
    if target_cal > 0 and abs(t_cal - target_cal) / target_cal > 0.15:
        issues += 1
    if has_pcos and t_fiber < 25:
        issues += 1
    if target_protein > 0 and abs(t_prot - target_protein) / target_protein > 0.2:
        issues += 1
    if has_hashi and t_zinc < 11:
        issues += 1
    if target_water > 0 and t_water < target_water * 0.8:
        issues += 1
    if t_risks > 2:
        issues += 1

    score = round((1 - issues / 6) * 100)
    if score >= 85:
        level = "excellent"
    elif score >= 70:
        level = "good"
    elif score >= 50:
        level = "warning"
    elif score >= 30:
        level = "critical"
    else:
        level = "neutral"
    return score, level


def nutrient_score(totals, targets):
    checks = [
        (totals["calories"], targets["cal"], 0.85, 1.15),
        (totals["protein"], targets["prot"], 0.80, 1.20),
        (totals["fiber"], 25, 0.80, 9999),
        (totals["iron"], 18, 0.70, 9999),
        (totals["zinc"], 11, 0.70, 9999),
        (totals["vitd"], 15, 0.60, 9999),
        (totals["magnesium"], 300, 0.70, 9999),
        (totals["calcium"], 1000, 0.70, 9999),
        (totals["omega3"], 1000, 0.60, 9999),
    ]
    passed = sum(1 for val, tgt, lo, hi in checks if tgt > 0 and lo <= val / tgt <= hi)
    return round(passed / len(checks) * 100)
