import streamlit as st
import pandas as pd
from datetime import date

from data import load_history, save_history_row
from logic import get_lang, nutrient_score, progress_bar_html, get_metabolism_status, txt


def render_diary_tab(df, meta_goal, target_cal, target_protein, target_carbs, target_water, health_conditions, weight):
    st.markdown(f"<h3 style='color:#059669;'>{txt('diary_hdr')}</h3>", unsafe_allow_html=True)

    if 'daily_meals' not in st.session_state:
        st.session_state.daily_meals = []
    if 'water_glasses' not in st.session_state:
        st.session_state.water_glasses = 0

    has_meals = bool(st.session_state.daily_meals)
    if has_meals:
        df_today = pd.DataFrame(st.session_state.daily_meals)
        h = st.columns([5, 1.4, 1, 1, 1, 1, 0.5])
        for col, label in zip(h, ["JEDLO", "g ✏️", "kcal", "P(g)", "C(g)", "F(g)", ""]):
            col.markdown(
                f"<span style='font-size:0.72rem;color:#6b8a85;font-weight:700;letter-spacing:1px;'>{label}</span>",
                unsafe_allow_html=True,
            )

        for i, row in df_today.iterrows():
            c = st.columns([5, 1.4, 1, 1, 1, 1, 0.5])
            parts = row['Jedlo'].split('/')
            food_display = parts[1].strip()[:45] if get_lang() == "SK" and len(parts) > 1 else parts[0].strip()[:45]
            c[0].markdown(f"<span style='font-size:0.83rem;color:#ecfeff;'>{food_display}</span>", unsafe_allow_html=True)

            with c[1]:
                new_grams = st.number_input(
                    "", min_value=1, value=int(row['Gramy']), step=5,
                    key=f"grams_{i}", label_visibility="collapsed"
                )
                if new_grams != int(row['Gramy']):
                    orig = df[
                        (df['name_en'] + ' / ' + df['name_sk'] == row['Jedlo']) |
                        (df['name_en'] == row['Jedlo'].split('/')[0].strip()) |
                        (df['name_sk'] == row['Jedlo'].split('/')[-1].strip())
                    ]
                    if not orig.empty:
                        fd2 = orig.iloc[0]
                        r2 = new_grams / 100.0
                        st.session_state.daily_meals[i].update({
                            "Gramy": new_grams,
                            "Kalórie": round(fd2.get('Calories', 0) * r2, 1),
                            "Bielkoviny": round(fd2.get('Protein (g)', 0) * r2, 1),
                            "Tuky": round(fd2.get('Fat (g)', 0) * r2, 1),
                            "Čisté Sacharidy": round(fd2.get('Net-Carbs (g)', 0) * r2, 1),
                            "Cukor": round(fd2.get('Sugars (g)', 0) * r2, 1),
                            "Vláknina": round(fd2.get('Fiber (g)', 0) * r2, 1),
                            "Železo": round(fd2.get('Iron, Fe (mg)', 0) * r2, 2),
                            "Zinok": round(fd2.get('Zinc, Zn (mg)', 0) * r2, 2),
                            "Vitamín D": round(fd2.get('Vitamin D (mcg)', 0) * r2, 2),
                            "Horčík": round(float(fd2.get('Magnesium (mg)', 0) or 0) * r2, 1),
                            "Vápnik": round(float(fd2.get('Calcium (mg)', 0) or 0) * r2, 1),
                            "Omega3": round(float(fd2.get('Omega 3s (mg)', 0) or 0) * r2, 0),
                            "Selén": round(float(fd2.get('Selenium, Se (mcg)', 0) or 0) * r2, 1),
                        })
                        st.rerun()

            cur = st.session_state.daily_meals[i]
            c[2].markdown(f"<span style='font-size:0.83rem;color:#2dd4bf;font-weight:700;'>{cur['Kalórie']}</span>", unsafe_allow_html=True)
            c[3].markdown(f"<span style='font-size:0.83rem;color:#9fb7b3;'>{cur['Bielkoviny']}</span>", unsafe_allow_html=True)
            c[4].markdown(f"<span style='font-size:0.83rem;color:#9fb7b3;'>{cur['Čisté Sacharidy']}</span>", unsafe_allow_html=True)
            c[5].markdown(f"<span style='font-size:0.83rem;color:#9fb7b3;'>{cur['Tuky']}</span>", unsafe_allow_html=True)
            with c[6]:
                if st.button("🗑️", key=f"del_{i}", help=txt("remove_meal")):
                    st.session_state.daily_meals.pop(i)
                    st.rerun()
            st.markdown("<hr style='margin:1px 0;border:none;border-top:1px solid rgba(45,212,191,0.06);'>", unsafe_allow_html=True)

        totals = {
            "calories": round(df_today["Kalórie"].sum(), 1),
            "carbs": round(df_today["Čisté Sacharidy"].sum(), 1),
            "protein": round(df_today["Bielkoviny"].sum(), 1),
            "fiber": round(df_today["Vláknina"].sum(), 1),
            "sugar": round(df_today["Cukor"].sum(), 1),
            "iron": round(df_today["Železo"].sum(), 2),
            "zinc": round(df_today["Zinok"].sum(), 2),
            "vitd": round(df_today["Vitamín D"].sum(), 2),
            "magnesium": round(df_today["Horčík"].sum(), 1),
            "calcium": round(df_today["Vápnik"].sum(), 1),
            "omega3": round(df_today["Omega3"].sum(), 0),
            "selenium": round(df_today["Selén"].sum(), 1),
            "risks": round(df_today["Rizikové"].sum(), 0),
        }
    else:
        st.info(txt("no_meals"))
        totals = {k: 0 for k in ["calories", "carbs", "protein", "fiber", "sugar", "iron", "zinc", "vitd", "magnesium", "calcium", "omega3", "selenium", "risks"]}

    if has_meals:
        if st.button(txt("clear_day")):
            st.session_state.daily_meals = []
            st.rerun()

    st.markdown(txt("status"))
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(txt("cal"), f"{totals['calories']} kcal")
    m2.metric(txt("prot"), f"{totals['protein']} g")
    m3.metric(txt("carbs"), f"{totals['carbs']} g")
    m4.metric(txt("fiber"), f"{totals['fiber']} g")

    bars_html = (
        '<div style="background:rgba(15,25,23,0.7);border:1px solid rgba(45,212,191,0.10);'
        'border-radius:18px;padding:20px 24px;margin:12px 0;'>'
        '<div style="font-size:0.7rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
        'color:#6b8a85;margin-bottom:16px;">'
        + ("Denný pokrok" if get_lang() == "SK" else "Daily Progress") +
        '</div>'
    )
    bars_html += progress_bar_html(totals['calories'], target_cal, "kcal", "🔥 " + ("Kalórie" if get_lang() == "SK" else "Calories"))
    bars_html += progress_bar_html(totals['protein'], target_protein, "g", "💪 " + ("Bielkoviny" if get_lang() == "SK" else "Protein"))
    bars_html += progress_bar_html(totals['carbs'], target_carbs, "g", "🌾 " + ("Sacharidy" if get_lang() == "SK" else "Net Carbs"))
    bars_html += progress_bar_html(totals['fiber'], 25, "g", "🥦 " + ("Vláknina" if get_lang() == "SK" else "Fiber"))
    bars_html += progress_bar_html(totals['iron'], 18, "mg", "🩸 " + ("Železo" if get_lang() == "SK" else "Iron"))
    bars_html += progress_bar_html(totals['zinc'], 12, "mg", "🦋 " + ("Zinok" if get_lang() == "SK" else "Zinc"))
    bars_html += progress_bar_html(totals['magnesium'], 350, "mg", "⚡ " + ("Horčík" if get_lang() == "SK" else "Magnesium"))
    bars_html += progress_bar_html(totals['calcium'], 1000, "mg", "🦴 " + ("Vápnik" if get_lang() == "SK" else "Calcium"))
    bars_html += progress_bar_html(totals['vitd'], 15, "mcg", "☀️ " + ("Vitamín D" if get_lang() == "SK" else "Vitamin D"))
    bars_html += progress_bar_html(int(totals['omega3'] or 0), 1500, "mg", "🐟 " + ("Omega-3" if get_lang() == "SK" else "Omega-3"))
    bars_html += '</div>'
    st.markdown(bars_html, unsafe_allow_html=True)

    targets_for_score = {"cal": target_cal, "prot": target_protein}
    ns = nutrient_score(totals, targets_for_score)
    ns_color = "#10b981" if ns >= 70 else ("#f59e0b" if ns >= 40 else "#fb7185")
    st.markdown(
        f"<div style='text-align:center;margin:10px 0;'>"
        f"<span style='font-size:2.5rem;font-weight:800;color:{ns_color};'>{ns}/100</span>"
        f"<div style='color:#9fb7b3;font-size:0.9rem;'>{txt('nutrient_score')}</div></div>",
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown(f"<h4 style='color:#0d9488;'>{txt('water_hdr')}</h4>", unsafe_allow_html=True)
    wc1, wc2, wc3 = st.columns(3)
    with wc1:
        if st.button(f"💧 +250ml", use_container_width=True):
            st.session_state.water_glasses += 1
    with wc2:
        if st.button("➖", use_container_width=True):
            st.session_state.water_glasses = max(0, st.session_state.water_glasses - 1)
    with wc3:
        if st.button("🔄", use_container_width=True):
            st.session_state.water_glasses = 0

    water_total = round(st.session_state.water_glasses * 0.25, 2)
    st.metric(txt("water_total"), f"{water_total} / {target_water} L")
    st.markdown(progress_bar_html(water_total, target_water, "L", "💧 " + ("Voda" if get_lang() == "SK" else "Water")), unsafe_allow_html=True)

    st.divider()
    st.markdown(f"<h4>{txt('feedback_hdr')}</h4>", unsafe_allow_html=True)
    feedbacks = []

    if health_conditions.get('has_pcos') or health_conditions.get('has_db2'):
        feedbacks.append(txt('fb_pcos_fiber_low').format(fiber=totals['fiber']) if totals['fiber'] < 25 else txt('fb_pcos_fiber_ok'))
    if (health_conditions.get('has_pcos') or health_conditions.get('has_db2') or health_conditions.get('has_nafld') or health_conditions.get('has_candida')) and totals['sugar'] > 35:
        feedbacks.append(txt('fb_pcos_sugar_high').format(sugar=totals['sugar']))
    if health_conditions.get('has_anemia'):
        feedbacks.append(txt('fb_anemia_iron_low').format(iron=totals['iron']) if totals['iron'] < 15 else txt('fb_anemia_iron_ok'))
    if health_conditions.get('has_hashi'):
        feedbacks.append(txt('fb_hashi_zinc_low').format(zinc=totals['zinc']) if totals['zinc'] < 11 else txt('fb_hashi_zinc_ok'))
        feedbacks.append(txt('fb_hashi_selenium_low').format(sel=totals['selenium']) if totals['selenium'] < 55 else txt('fb_hashi_selenium_ok'))
        if totals['risks'] > 0:
            feedbacks.append(txt('fb_hashi_risks').format(risks=int(totals['risks'])))
    if health_conditions.get('has_celiakia') and totals['risks'] > 0:
        feedbacks.append(txt('fb_celiakia_risk'))
    if health_conditions.get('has_gastritis') and totals['risks'] > 0:
        feedbacks.append(txt('fb_gastritis_risk'))
    if health_conditions.get('has_gout') and totals['risks'] > 0:
        feedbacks.append(txt('fb_gout_risk'))
    feedbacks.append(txt('fb_vitd_low').format(vitd=totals['vitd']) if totals['vitd'] < 10 else txt('fb_vitd_ok'))
    feedbacks.append(txt('fb_magnesium_low').format(mag=totals['magnesium']) if totals['magnesium'] < 200 else txt('fb_magnesium_ok'))
    if health_conditions.get('has_osteo') or health_conditions.get('has_menopause'):
        feedbacks.append(txt('fb_calcium_low').format(cal=totals['calcium']) if totals['calcium'] < 700 else txt('fb_calcium_ok'))
    feedbacks.append(txt('fb_omega3_low').format(o3=int(totals['omega3'] or 0)) if (totals['omega3'] or 0) < 500 else txt('fb_omega3_ok'))

    water_upper = round(max(4.5, target_water + 1.5), 1)
    if water_total < target_water * 0.8:
        feedbacks.append(txt('fb_water_low').format(water=round(water_total, 1), target=target_water))
    elif water_total > water_upper:
        feedbacks.append(txt('fb_water_high').format(water=water_total, limit=water_upper))
    else:
        feedbacks.append(txt('fb_water_ok'))

    if not feedbacks:
        feedbacks.append(txt('fb_perfect'))

    fb_html = '<div style="display:flex;flex-direction:column;gap:8px;margin:4px 0;">'
    for fb in feedbacks:
        if any(x in fb for x in ["🚨"]):
            left = "#fb7185"
            bg = "rgba(251,113,133,0.07)"
            border = "rgba(251,113,133,0.25)"
        elif any(x in fb for x in ["⚠️"]):
            left = "#f59e0b"
            bg = "rgba(245,158,11,0.07)"
            border = "rgba(245,158,11,0.22)"
        elif any(x in fb for x in ["✨", "💪", "☀️"]):
            left = "#10b981"
            bg = "rgba(16,185,129,0.07)"
            border = "rgba(16,185,129,0.20)"
        else:
            left = "#2dd4bf"
            bg = "rgba(45,212,191,0.05)"
            border = "rgba(45,212,191,0.15)"
        fb_html += (
            f'<div style="background:{bg};border:1px solid {border};border-left:3px solid {left};'
            f'border-radius:12px;padding:12px 16px;font-size:0.88rem;color:#d1faf5;line-height:1.6;' 
            f'>{fb}</div>'
        )
    fb_html += '</div>'
    st.markdown(fb_html, unsafe_allow_html=True)

    st.divider()
    metab_score, metab_level = get_metabolism_status(
        totals['calories'], target_cal, totals['protein'], target_protein,
        totals['fiber'], health_conditions.get('has_pcos'), health_conditions.get('has_hashi'),
        totals['iron'], totals['zinc'], totals['risks'], water_total, target_water,
    )

    _METAB = {
        "excellent": {
            "emoji": "🟢", "icon": "✦",
            "title_sk": "Metabolizmus v top forme", "title_en": "Metabolism in top shape",
            "sub_sk": "Dnes si dal/a telu presne to, čo potrebuje. Výborná práca.",
            "sub_en": "You gave your body exactly what it needs today. Outstanding.",
            "grad": "linear-gradient(135deg, rgba(16,185,129,0.18), rgba(5,150,105,0.08))",
            "border": "#10b981", "score_color": "#10b981",
        },
        "good": {
            "emoji": "🔵", "icon": "◈",
            "title_sk": "Dobrý deň pre tvoje telo", "title_en": "A good day for your body",
            "sub_sk": "Väčšina metrík je na cieli. Pár malých úprav a bude to perfektné.",
            "sub_en": "Most metrics are on target. A few small tweaks and it'll be perfect.",
            "grad": "linear-gradient(135deg, rgba(59,130,246,0.18), rgba(37,99,235,0.08))",
            "border": "#3b82f6", "score_color": "#60a5fa",
        },
        "warning": {
            "emoji": "🟡", "icon": "⚠",
            "title_sk": "Metabolizmus potrebuje pozornosť", "title_en": "Metabolism needs attention",
            "sub_sk": "Niektoré živiny sú mimo cieľa. Pozri si spätné väzby vyššie.",
            "sub_en": "Some nutrients are off target. Check the feedback above.",
            "grad": "linear-gradient(135deg, rgba(245,158,11,0.18), rgba(217,119,6,0.08))",
            "border": "#f59e0b", "score_color": "#fbbf24",
        },
        "critical": {
            "emoji": "🔴", "icon": "✕",
            "title_sk": "Kritický stav — konaj hneď", "title_en": "Critical — act now",
            "sub_sk": "Tvoj príjem dnes výrazne zaostáva za potrebami tela. Uprav jedálniček.",
            "sub_en": "Your intake today is significantly below your body's needs. Adjust your diet.",
            "grad": "linear-gradient(135deg, rgba(251,113,133,0.18), rgba(225,29,72,0.08))",
            "border": "#fb7185", "score_color": "#fb7185",
        },
        "neutral": {
            "emoji": "⚪", "icon": "○",
            "title_sk": "Neutrálny deň", "title_en": "Neutral day",
            "sub_sk": "Nič zlé, ale ani nič výnimočné. Zajtra to zlepši.",
            "sub_en": "Nothing bad, but nothing exceptional. Do better tomorrow.",
            "grad": "linear-gradient(135deg, rgba(107,138,133,0.14), rgba(75,85,99,0.08))",
            "border": "#6b8a85", "score_color": "#9fb7b3",
        },
        "empty": {
            "emoji": "⚪", "icon": "◌",
            "title_sk": "Zatiaľ žiadne jedlo", "title_en": "No food logged yet",
            "sub_sk": "Pridaj prvé jedlo do denníka a skóre sa začne počítať.",
            "sub_en": "Add your first meal to the diary and the score will start calculating.",
            "grad": "linear-gradient(135deg, rgba(107,138,133,0.10), rgba(75,85,99,0.05))",
            "border": "#4b5563", "score_color": "#6b8a85",
        },
    }

    m = _METAB[metab_level]
    lang = get_lang()
    m_title = m["title_sk"] if lang == "SK" else m["title_en"]
    m_sub = m["sub_sk"] if lang == "SK" else m["sub_en"]
    score_label = "Skóre dňa" if lang == "SK" else "Day score"

    radius = 44
    circ = 2 * 3.14159 * radius
    dash = round(circ * metab_score / 100, 1)
    gap = round(circ - dash, 1)

    metab_html = (
        f'<div style="background:{m['grad']};border:1px solid {m['border']}33;'
        f'border-left:4px solid {m['border']};border-radius:22px;'
        f'padding:28px 32px;margin:16px 0;box-shadow:0 8px 32px rgba(0,0,0,0.28);'>
        f'<div style="display:flex;align-items:center;gap:32px;">'
        f'<div style="flex-shrink:0;text-align:center;">'
        f'<svg width="110" height="110" viewBox="0 0 110 110">'
        f'<circle cx="55" cy="55" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>'
        f'<circle cx="55" cy="55" r="{radius}" fill="none" stroke="{m['score_color']}" stroke-width="10"'
        f' stroke-dasharray="{dash} {gap}" stroke-dashoffset="{round(circ*0.25,1)}"'
        f' stroke-linecap="round" style="filter:drop-shadow(0 0 6px {m['score_color']}88);"/>'
        f'<text x="55" y="50" text-anchor="middle" fill="{m['score_color']}" '
        f'font-size="22" font-weight="800" font-family="Inter,sans-serif">{metab_score}</text>'
        f'<text x="55" y="66" text-anchor="middle" fill="#6b8a85" '
        f'font-size="9" font-family="Inter,sans-serif" letter-spacing="1">{score_label.upper()}</text>'
        f'</svg>'
        f'</div>'
        f'<div style="flex:1;">'
        f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
        f'color:{m['score_color']};margin-bottom:6px;">🧬 ' +
        ("STAV METABOLIZMU" if lang == "SK" else "METABOLISM STATUS") +
        f'</div>'
        f'<div style="font-size:1.6rem;font-weight:800;color:#f0fdfa;line-height:1.2;margin-bottom:8px;">'
        f'{m['icon']} {m_title}</div>'
        f'<div style="font-size:0.92rem;color:#9fb7b3;line-height:1.6;">{m_sub}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(metab_html, unsafe_allow_html=True)

    st.divider()
    st.markdown(f"<h4>{txt('symptoms_hdr')}</h4>", unsafe_allow_html=True)
    sym_cols = st.columns(3)
    selected_symptoms = []
    with sym_cols[0]:
        st.markdown(txt('sym_gain_fatigue'))
        if st.checkbox(txt('sym_hunger'), key='hunger'):
            selected_symptoms.append('Hunger')
        if st.checkbox(txt('sym_weakness'), key='weakness'):
            selected_symptoms.append('Weakness')
        if st.checkbox(txt('sym_bloating'), key='bloating'):
            selected_symptoms.append('Bloating')
    with sym_cols[1]:
        st.markdown(txt('sym_lose_weight'))
        if st.checkbox(txt('sym_palpitations'), key='palpitations'):
            selected_symptoms.append('Palpitations')
        if st.checkbox(txt('sym_cramps'), key='cramps'):
            selected_symptoms.append('Cramps')
        if st.checkbox(txt('sym_gout_pain'), key='gout_pain'):
            selected_symptoms.append('Gout Pain')
    with sym_cols[2]:
        st.markdown(txt('sym_subjective'))
        energy_score = st.slider(txt('sym_energy'), 1, 10, 7, key='energy')
        sleep_score = st.slider(txt('sym_sleep'), 1, 10, 7, key='sleep')

    if st.button(txt('save_btn'), use_container_width=True, type='primary'):
        diag_map = {
            'PCOS': health_conditions.get('has_pcos'),
            'Hashimoto': health_conditions.get('has_hashi'),
            'Anemia': health_conditions.get('has_anemia'),
            'Celiac': health_conditions.get('has_celiakia'),
            'Gout': health_conditions.get('has_gout'),
            'NAFLD': health_conditions.get('has_nafld'),
            'Adrenal': health_conditions.get('has_adrenal'),
            'Leaky Gut': health_conditions.get('has_leaky_gut'),
            'Candida': health_conditions.get('has_candida'),
            'Menopause': health_conditions.get('has_menopause'),
            'Osteoporosis': health_conditions.get('has_osteo'),
        }
        active_diag = [d for d, v in diag_map.items() if v]
        save_history_row({
            'Dátum': str(date.today()),
            'Diagnózy': ', '.join(active_diag) if active_diag else 'None',
            'Cieľ': meta_goal,
            'Váha (kg)': weight,
            'Energia': energy_score,
            'Spánok': sleep_score,
            'Kalórie': totals['calories'],
            'Sacharidy (g)': totals['carbs'],
            'Voda (L)': water_total,
            'Symptómy': ', '.join(selected_symptoms) if selected_symptoms else 'None',
        })
        st.success(txt('save_success'))
