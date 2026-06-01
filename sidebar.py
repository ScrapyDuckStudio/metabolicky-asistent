import os

import streamlit as st

from data import load_food_database
from logic import ACTIVITY_MULTIPLIERS, calculate_bmi, calculate_water_target, bmi_category, get_lang, txt
from translation import TRANSLATIONS


def render_sidebar(auth_enabled=False) -> dict:
    if 'lang' not in st.session_state:
        st.session_state.lang = 'SK'

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=80)

        if auth_enabled and st.session_state.get("_user_email"):
            uname = st.session_state.get("_user_name", st.session_state["_user_email"])
            uemail = st.session_state["_user_email"]
            st.markdown(
                f'<div style="background:rgba(45,212,191,0.06);border:1px solid rgba(45,212,191,0.12);'
                f'border-radius:14px;padding:10px 14px;margin-bottom:12px;">'
                f'<div style="font-size:0.78rem;font-weight:700;color:#2dd4bf;">👤 {uname}</div>'
                f'<div style="font-size:0.7rem;color:#6b8a85;margin-top:2px;">{uemail}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.logout()

        with st.expander(f"🧬 {txt('profile')}", expanded=True):
            st.markdown(f"**{txt('gain_weight_tendency')}**")
            has_pcos = st.checkbox(txt("pcos"), key="pcos")
            has_hashi = st.checkbox(txt("hashi"), key="hashi")
            has_db2 = st.checkbox(txt("db2"), key="db2")
            has_anemia = st.checkbox(txt("anemia"), key="anemia")
            has_cushing = st.checkbox(txt("cushing"), key="cushing")
            has_lipedema = st.checkbox(txt("lepid"), key="lipedema")
            st.markdown(f"**{txt('lose_weight_tendency')}**")
            has_hyper = st.checkbox(txt("hyper"), key="hyper")
            has_celiakia = st.checkbox(txt("celiakia"), key="celiakia")
            has_addison = st.checkbox(txt("addison"), key="addison")
            st.markdown(f"**{txt('digestion')}**")
            has_hit = st.checkbox(txt("hit"), key="hit")
            has_gastritis = st.checkbox(txt("gastritis"), key="gastritis")
            has_sibo = st.checkbox(txt("sibo"), key="sibo")
            has_gallbladder = st.checkbox(txt("gallbladder"), key="gallbladder")
            st.markdown(f"**{txt('metabolic_syndromes')}**")
            has_gout = st.checkbox(txt("gout"), key="gout")
            has_nafld = st.checkbox(txt("nafld"), key="nafld")
            has_hypertension = st.checkbox(txt("hypertension"), key="hypertension")
            has_kidney_stones = st.checkbox(txt("kidney_stones"), key="kidney_stones")
            has_adrenal = st.checkbox(txt("adrenal_fatigue"), key="adrenal")
            has_leaky_gut = st.checkbox(txt("leaky_gut"), key="leaky_gut")
            has_candida = st.checkbox(txt("candida"), key="candida")
            has_menopause = st.checkbox(txt("menopause"), key="menopause")
            has_osteo = st.checkbox(txt("osteo"), key="osteo")

        with st.expander(txt("goal_hdr"), expanded=False):
            meta_goal = st.radio(txt("goal_q"), TRANSLATIONS[get_lang()]["goals"], label_visibility="collapsed")

        with st.expander(txt("antropo"), expanded=False):
            sex_opts = [txt("sex_f"), txt("sex_m")]
            sex = st.radio(txt("sex"), sex_opts, horizontal=True)
            weight = st.number_input(txt("weight"), min_value=30.0, value=70.0, step=0.1)
            height = st.number_input(txt("height"), min_value=120, value=165)
            age = st.number_input(txt("age"), min_value=15, value=30)
            act_opts = TRANSLATIONS[get_lang()]["activity_opts"]
            act_idx = st.selectbox(txt("activity"), range(len(act_opts)), format_func=lambda i: act_opts[i])

            bmi = calculate_bmi(weight, height)
            bmi_cat = bmi_category(bmi, get_lang())
            bmi_color = "#10b981" if 18.5 <= bmi < 25 else ("#f59e0b" if bmi < 30 else "#fb7185")
            st.markdown(
                f"**{txt('bmi_label')}:** <span style='color:{bmi_color};font-weight:700;'>{bmi} — {bmi_cat}</span>",
                unsafe_allow_html=True
            )

        is_female = sex == txt("sex_f")
        bmr = round(10 * weight + 6.25 * height - 5 * age - 161) if is_female else round(10 * weight + 6.25 * height - 5 * age + 5)
        act_mult = ACTIVITY_MULTIPLIERS[act_idx]
        base_maintenance = round(bmr * act_mult)

        if has_cushing:
            base_maintenance = round(base_maintenance * 0.9)
        if has_addison:
            base_maintenance = round(base_maintenance * 1.1)

        goal_low_carb = [
            "Zdravé chudnutie",
            "Healthy Weight Loss",
        ]
        goal_bulk = [
            "Zdravé pribratie (Budovanie hmoty)",
            "Healthy Weight Gain (Bulking)",
        ]

        if meta_goal in goal_low_carb:
            target_cal = base_maintenance - 350
        elif meta_goal in goal_bulk:
            target_cal = base_maintenance + 400
        else:
            target_cal = base_maintenance

        if has_gout or has_kidney_stones:
            target_protein = round(weight * 1.2)
        elif has_hyper or meta_goal in goal_bulk:
            target_protein = round(weight * 1.8)
        else:
            target_protein = round(weight * 1.5)

        carbs_pct = 0.25 if (has_pcos or has_db2 or has_nafld or has_candida) else 0.45
        target_carbs = round((target_cal * carbs_pct) / 4)
        target_fat = round((target_cal * (1.0 - (carbs_pct + 0.25))) / 9)
        target_water = calculate_water_target(weight, has_hyper, has_hypertension)

        st.info(txt("target_info").format(
            cal=target_cal,
            prot=target_protein,
            carbs=target_carbs,
            fat=target_fat,
            water=target_water,
        ))

        uploaded_file = None
        if not os.path.exists("food_data_en_sk.csv"):
            st.warning(txt("db_status_upload"))
            uploaded_file = st.file_uploader("", type=["csv"])
        else:
            st.caption(txt("db_status_ok"))

        df, is_real_db = load_food_database(uploaded_file)

    health_conditions = {
        'has_pcos': has_pcos,
        'has_hashi': has_hashi,
        'has_db2': has_db2,
        'has_anemia': has_anemia,
        'has_celiakia': has_celiakia,
        'has_hit': has_hit,
        'has_gastritis': has_gastritis,
        'has_sibo': has_sibo,
        'has_gout': has_gout,
        'has_kidney_stones': has_kidney_stones,
        'has_gallbladder': has_gallbladder,
        'has_nafld': has_nafld,
        'has_adrenal': has_adrenal,
        'has_leaky_gut': has_leaky_gut,
        'has_candida': has_candida,
        'has_menopause': has_menopause,
        'has_osteo': has_osteo,
        'has_hyper': has_hyper,
        'has_hypertension': has_hypertension,
        'has_hashi': has_hashi,
    }

    return {
        'df': df,
        'is_real_db': is_real_db,
        'health_conditions': health_conditions,
        'meta_goal': meta_goal,
        'weight': weight,
        'target_cal': target_cal,
        'target_protein': target_protein,
        'target_carbs': target_carbs,
        'target_fat': target_fat,
        'target_water': target_water,
    }
