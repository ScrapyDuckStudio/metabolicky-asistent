import streamlit as st
import pandas as pd
from datetime import date
import os

# --- Basic setup ---
st.set_page_config(page_title="Metabolický Asistent & Inteligentný Kouč", layout="wide")

HISTORY_FILE = "zdravotna_historia_global.csv"

# --- Language selection ---
lang = st.sidebar.radio("🌐 Jazyk / Language", ["SK", "EN"])

TXT = {
    # ... (your existing translation dictionaries here, omitted for brevity)
}

HIST_COLS = ["Dátum", "Diagnózy", "Cieľ", "Váha (kg)", "Energia", "Spánok", "Kalórie", "Sacharidy (g)", "Symptómy"]

# --- Load data function ---
@st.cache_data
def load_data(uploaded_file=None):
    # ... (your existing load_data function, omitted for brevity)
    pass

# --- Load or initialize history ---
def load_history():
    # ... (your existing load_history function)
    pass

def save_history_row(row_dict):
    # ... (your existing save_history_row function)
    pass

# --- Custom CSS for styling ---
st.markdown(
    """
    <style>
    /* Change font */
    html, body, [class*="css"] {
        font-family: 'Arial', sans-serif;
    }
    /* Add padding */
    .css-1d391kg {
        padding: 1rem 2rem;
    }
    /* Style headers */
    h2 {
        color: #4CAF50;
        font-size: 1.8rem;
    }
    /* Style buttons */
    button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        margin-top: 10px;
        cursor: pointer;
        border-radius: 5px;
    }
    button:hover {
        background-color: #45a049;
    }
    /* Add spacing between sections */
    .section {
        margin-bottom: 2rem;
        padding: 1rem;
        background-color: #f9f9f9;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True
)

# --- Sidebar steps ---
st.sidebar.write("---")
# Step 1: Health profile
with st.sidebar.expander(TXT[lang]["profile"], expanded=True):
    # Existing health checkboxes
    has_pcos = st.checkbox(TXT[lang]["pcos"], value=False)
    has_hashi = st.checkbox(TXT[lang]["hashi"], value=False)
    has_db2 = st.checkbox(TXT[lang]["db2"], value=False)
    has_anemia = st.checkbox(TXT[lang]["anemia"], value=False)
    has_cushing = st.checkbox(TXT[lang]["cushing"], value=False)
    has_lipedema = st.checkbox(TXT[lang]["lepid"], value=False)

    st.markdown(f"<small>{TXT[lang]['lose_weight_tendency']}</small>", unsafe_allow_html=True)
    has_hyper = st.checkbox(TXT[lang]["hyper"], value=False)
    has_celiakia = st.checkbox(TXT[lang]["celiakia"], value=False)
    has_addison = st.checkbox(TXT[lang]["addison"], value=False)

    st.markdown(f"<small>{TXT[lang]['digestion']}</small>", unsafe_allow_html=True)
    has_hit = st.checkbox(TXT[lang]["hit"], value=False)
    has_gastritis = st.checkbox(TXT[lang]["gastritis"], value=False)
    has_sibo = st.checkbox(TXT[lang]["sibo"], value=False)
    has_gallbladder = st.checkbox(TXT[lang]["gallbladder"], value=False)

    st.markdown(f"<small>{TXT[lang]['metabolic_syndromes']}</small>", unsafe_allow_html=True)
    has_gout = st.checkbox(TXT[lang]["gout"], value=False)
    has_nafld = st.checkbox(TXT[lang]["nafld"], value=False)
    has_hypertension = st.checkbox(TXT[lang]["hypertension"], value=False)
    has_kidney_stones = st.checkbox(TXT[lang]["kidney_stones"], value=False)

# Step 2: Goal
with st.sidebar.expander(TXT[lang]["goal_hdr"], expanded=False):
    meta_goal = st.radio(TXT[lang]["goal_q"], TXT[lang]["goals"], label_visibility="collapsed")

# Step 3: Anthropometrics
with st.sidebar.expander(TXT[lang]["antropo"], expanded=False):
    weight = st.number_input(TXT[lang]["weight"], min_value=30.0, max_value=200.0, value=70.0, step=0.1)
    height = st.number_input(TXT[lang]["height"], min_value=120, max_value=250, value=165)
    age = st.number_input(TXT[lang]["age"], min_value=15, max_value=120)

# Calculate metabolic targets
bmr = round(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
base_maintenance = round(bmr * 1.2)

# Adjustments
if has_cushing: base_maintenance = round(base_maintenance * 0.9)
if has_addison: base_maintenance = round(base_maintenance * 1.1)

# Targets based on goal
if meta_goal in ["Zdravé chudnutie", "Healthy Weight Loss"]:
    target_cal = base_maintenance - 350
elif meta_goal in ["Zdravé pribratie (Budovanie hmoty)", "Healthy Weight Gain (Bulking)"]:
    target_cal = base_maintenance + 400
else:
    target_cal = base_maintenance

# Protein
if has_gout or has_kidney_stones:
    target_protein = round(weight * 1.2)
elif has_hyper or meta_goal in ["Zdravé pribratie (Budovanie hmoty)", "Healthy Weight Gain (Bulking)"]:
    target_protein = round(weight * 1.8)
else:
    target_protein = round(weight * 1.5)

# Carbs & Fat
carbs_percentage = 0.25 if (has_pcos or has_db2 or has_nafld) else 0.45
target_carbs = round((target_cal * carbs_percentage) / 4)
target_fat = round((target_cal * (1.0 - (carbs_percentage + 0.25))) / 9)

st.sidebar.info(TXT[lang]["target_info"].format(cal=target_cal, prot=target_protein, carbs=target_carbs, fat=target_fat))

# --- Database upload ---
st.sidebar.write("---")
uploaded_file = None
if not os.path.exists("food_data_en_sk.csv"):
    st.sidebar.warning(TXT[lang]["db_status_upload"])
    uploaded_file = st.sidebar.file_uploader("", type=["csv"])
else:
    st.sidebar.caption(TXT[lang]["db_status_ok"])

df, is_real_db = load_data(uploaded_file)

# --- Main app ---
st.title(TXT[lang]["title"])

tab1, tab2, tab3 = st.tabs(TXT[lang]["tabs"])

# Initialize session state
if 'daily_meals' not in st.session_state:
    st.session_state.daily_meals = []

# --- TAB 1: Food Search ---
with tab1:
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader(TXT[lang]["search_hdr"])
        search_query = st.text_input(TXT[lang]["search_lbl"], "")

        if search_query:
            results = df[
                df['name_en'].str.contains(search_query, case=False, na=False) | 
                df['name_sk'].str.contains(search_query, case=False, na=False)
            ]
            if not results.empty:
                food_options = results.apply(lambda row: f"{row['name_en']} / {row['name_sk']}", axis=1).tolist()
                selected_option = st.selectbox(TXT[lang]["select_food"], food_options)
                selected_idx = food_options.index(selected_option)
                food_details = results.iloc[selected_idx]
                grams = st.number_input(TXT[lang]["grams"], min_value=1, value=100, step=10)
                ratio = grams / 100.0

                # Nutrients calculation
                cal = round(food_details.get('Calories', 0) * ratio, 1)
                prot = round(food_details.get('Protein (g)', 0) * ratio, 1)
                fat = round(food_details.get('Fat (g)', 0) * ratio, 1)
                carbs = round(food_details.get('Net-Carbs (g)', 0) * ratio, 1)
                sugar = round(food_details.get('Sugars (g)', 0) * ratio, 1)
                fiber = round(food_details.get('Fiber (g)', 0) * ratio, 1)
                iron = round(food_details.get('Iron, Fe (mg)', 0) * ratio, 2)
                zinc = round(food_details.get('Zinc, Zn (mg)', 0) * ratio, 2)

                # Warnings
                full_name_lower = f"{food_details['name_en']} {food_details['name_sk']}".lower()
                warnings = []

                # Example warning checks
                if has_celiakia or has_hashi:
                    if any(x in full_name_lower for x in ['wheat', 'barley', 'rye', 'flour', 'bread', 'gluten']):
                        warnings.append(TXT[lang]["warn_gluten"])
                if has_hashi and any(x in full_name_lower for x in ['milk', 'cheese', 'yogurt']):
                    warnings.append(TXT[lang]["warn_milk"])
                if has_hit and any(x in full_name_lower for x in ['tomato', 'spinach']):
                    warnings.append(TXT[lang]["warn_hit"])
                if (has_gastritis or has_sibo) and any(x in full_name_lower for x in ['chili', 'coffee']):
                    warnings.append(TXT[lang]["warn_gastritis"])
                if has_gout and any(x in full_name_lower for x in ['beef', 'liver']):
                    warnings.append(TXT[lang]["warn_purines"])
                if has_kidney_stones and any(x in full_name_lower for x in ['spinach', 'chocolate']):
                    warnings.append(TXT[lang]["warn_oxalates"])
                if (has_gallbladder or has_nafld) and (fat > 15):
                    warnings.append(TXT[lang]["warn_high_fat"])

                # Show nutrients
                st.markdown(TXT[lang]["analysis"].format(g=grams))
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(TXT[lang]["cal"], f"{cal} kcal")
                c2.metric(TXT[lang]["prot"], f"{prot} g")
                c3.metric(TXT[lang]["carbs"], f"{carbs} g")
                c4.metric(TXT[lang]["fiber"], f"{fiber} g")

                # Warnings display
                if warnings:
                    st.markdown(TXT[lang]["warnings_hdr"])
                    for w in warnings:
                        st.warning(w)

                # Sugar warning
                if (has_pcos or has_db2 or has_nafld) and sugar > 10:
                    st.error(TXT[lang]["warn_sugar"])

                # Add to daily meals
                if st.button(TXT[lang]["add_btn"]):
                    st.session_state.daily_meals.append({
                        "Jedlo": selected_option, "Gramy": grams, "Kalórie": cal,
                        "Bielkoviny": prot, "Tuky": fat, "Čisté Sacharidy": carbs,
                        "Cukor": sugar, "Vláknina": fiber, "Železo": iron, "Zinok": zinc,
                        "Rizikové": 1 if warnings else 0
                    })
                    st.success(TXT[lang]["add_success"])
            else:
                st.info(TXT[lang]["not_found"])

    # Encyclopedia
    with col_r:
        st.markdown(TXT[lang]["encyclopedia"])
        if has_pcos or has_db2:
            with st.expander(TXT[lang]["enc_pcos_t"]): st.write(TXT[lang]["enc_pcos_b"])
        if has_hashi:
            with st.expander(TXT[lang]["enc_hashi_t"]): st.write(TXT[lang]["enc_hashi_b"])
        if has_hyper:
            with st.expander(TXT[lang]["enc_hyper_t"]): st.write(TXT[lang]["enc_hyper_b"])
        if has_anemia:
            with st.expander(TXT[lang]["enc_anemia_t"]): st.write(TXT[lang]["enc_anemia_b"])
        if has_gout:
            with st.expander(TXT[lang]["enc_gout_t"]): st.write(TXT[lang]["enc_gout_b"])
        if has_nafld:
            with st.expander(TXT[lang]["enc_nafld_t"]): st.write(TXT[lang]["enc_nafld_b"])

# --- TAB 2: Daily Diary & Tracking ---
with tab2:
    st.header(TXT[lang]["diary_hdr"])

    # Display today's meals
    if st.session_state.get('daily_meals'):
        df_today = pd.DataFrame(st.session_state['daily_meals'])
        df_display = df_today.copy()
        if lang == "SK":
            df_display.columns = ["Jedlo", "Gramy", "Kalórie", "Bielkoviny", "Tuky", "Čisté Sacharidy", "Cukor", "Vláknina", "Železo", "Zinok", "Riziko"]
        else:
            df_display.columns = ["Food", "Grams", "Calories", "Protein", "Fat", "Net Carbs", "Sugar", "Fiber", "Iron", "Zinc", "Risk"]
        st.dataframe(df_display.iloc[:, :8])

        # Totals
        t_cal = df_today["Kalórie"].sum()
        t_carbs = df_today["Čisté Sacharidy"].sum()
        t_prot = df_today["Bielkoviny"].sum()
        t_sugar = df_today["Cukor"].sum()
        t_fiber = df_today["Vláknina"].sum()
        t_iron = df_today["Železo"].sum()
        t_zinc = df_today["Zinok"].sum()
        t_risks = df_today["Rizikové"].sum()

        # Show totals
        st.markdown(TXT[lang]["status"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(TXT[lang]["cal"], f"{round(t_cal)} / {target_cal} kcal")
        c2.metric(TXT[lang]["prot"], f"{round(t_prot, 1)} / {target_protein} g")
        c3.metric(TXT[lang]["carbs"], f"{round(t_carbs, 1)} / {target_carbs} g")
        c4.metric(TXT[lang]["fiber"], f"{round(t_fiber, 1)} g")

        # Feedback based on intake
        st.write("---")
        st.subheader(TXT[lang]["feedback_hdr"])
        feedbacks = []

        if has_pcos or has_db2:
            if t_fiber < 25:
                feedbacks.append(TXT[lang]["fb_pcos_fiber_low"])
            else:
                feedbacks.append(TXT[lang]["fb_pcos_fiber_ok"])

        if has_pcos or has_db2 or has_nafld:
            if t_sugar > 35:
                feedbacks.append(TXT[lang]["fb_pcos_sugar_high"])

        if has_anemia:
            if t_iron < 15:
                feedbacks.append(TXT[lang]["fb_anemia_iron_low"].format(iron=round(t_iron, 1)))
            else:
                feedbacks.append(TXT[lang]["fb_anemia_iron_ok"])

        if has_hashi:
            if t_zinc < 11:
                feedbacks.append(TXT[lang]["fb_hashi_zinc_low"].format(zinc=round(t_zinc, 1)))
            if t_risks > 0:
                feedbacks.append(TXT[lang]["fb_hashi_risks"].format(risks=t_risks))

        if has_celiakia and t_risks > 0:
            feedbacks.append(TXT[lang]["fb_celiakia_risk"])
        if has_gastritis and t_risks > 0:
            feedbacks.append(TXT[lang]["fb_gastritis_risk"])
        if has_gout and t_risks > 0:
            feedbacks.append(TXT[lang]["fb_gout_risk"])

        if not feedbacks:
            st.success(TXT[lang]["fb_perfect"])
        else:
            for f in feedbacks:
                st.markdown(f)
    else:
        st.info(TXT[lang]["no_meals"])

    # --- Symptoms input ---
    st.write("---")
    st.subheader(TXT[lang]["symptoms_hdr"])
    s_cols = st.columns(3)
    s_list = []

    with s_cols[0]:
        st.markdown(TXT[lang]["sym_gain_fatigue"])
        if st.checkbox(TXT[lang]["sym_hunger"]): s_list.append("VlčíHlad/Hunger")
        if st.checkbox(TXT[lang]["sym_weakness"]): s_list.append("Slabosť/Weakness")
        if st.checkbox(TXT[lang]["sym_bloating"]): s_list.append("Nadúvanie/Bloating")
    with s_cols[1]:
        st.markdown(TXT[lang]["sym_lose_weight"])
        if st.checkbox(TXT[lang]["sym_palpitations"]): s_list.append("Triaška/Tremor")
        if st.checkbox(TXT[lang]["sym_cramps"]): s_list.append("KŕčeBrucha/Cramps")
        if st.checkbox(TXT[lang]["sym_gout_pain"]): s_list.append("BolesťKĺbov/GoutPain")
    with s_cols[2]:
        st.markdown(TXT[lang]["sym_subjective"])
        energy_score = st.slider(TXT[lang]["sym_energy"], 1, 10, 7)
        sleep_score = st.slider(TXT[lang]["sym_sleep"], 1, 10, 7)

    # Save symptoms & daily log
    if st.button(TXT[lang]["save_btn"]):
        row_data = {
            "Dátum": str(date.today()),
            "Diagnózy": ", ".join([d for d in ["PCOS", "Hashimoto", "Anemia", "Celiakia", "Gout", "NAFLD"] if locals().get(f"has_{d.lower()}", False)]),
            "Cieľ": meta_goal,
            "Váha (kg)": weight,
            "Energia": energy_score,
            "Spánok": sleep_score,
            "Kalórie": round(t_cal, 1),
            "Sacharidy (g)": round(t_carbs, 1),
            "Symptómy": ", ".join(s_list) if s_list else "Žiadne/None"
        }
        save_history_row(row_data)
        # Clear daily meals
        st.session_state['daily_meals'] = []
        st.success(TXT[lang]["save_success"])
        st.rerun()

# --- TAB 3: Progress & History ---
with tab3:
    st.header(TXT[lang]["history_hdr"])
    h_df = load_history()
    if not h_df.empty:
        st.dataframe(h_df)
        st.subheader(TXT[lang]["chart_title"])
        st.line_chart(h_df.set_index("Dátum")["Váha (kg)"])
    else:
        st.info(TXT[lang]["history_empty"])

# --- Additional: Water & Exercise Tracking ---
st.write("---")
st.header("💧🏃 " + ("Water & Exercise Tracking" if lang=="EN" else "Sledovanie vody a cvičenia"))

# Water Intake
with st.expander("💧 Water Intake" if lang=="EN" else "Príjem vody", expanded=True):
    water_intake = st.number_input(
        label="💧 Water Intake (liters)" if lang=="EN" else "Príjem vody (litre)",
        min_value=0.0,
        max_value=5.0,
        value=2.0,
        step=0.1,
        help="Log your daily water consumption in liters."
    )
    if st.button("💾 Save Water Intake" if lang=="EN" else "Uložiť príjem vody"):
        if 'water_log' not in st.session_state:
            st.session_state.water_log = []
        st.session_state.water_log.append({
            "Date": str(date.today()),
            "Water (L)": water_intake
        })
        st.success(f"Water intake of {water_intake} L saved!")

# Exercise Logging
with st.expander("🏃 Exercise Log" if lang=="EN" else "Cvičenie", expanded=True):
    exercise_type = st.selectbox("Exercise Type" if lang=="EN" else "Typ cvičenia", ["Running", "Walking", "Cycling", "Gym", "Yoga", "Other"])
    duration = st.number_input("Duration (minutes)" if lang=="EN" else "Dĺžka (min)", min_value=0, max_value=180, value=30)
    calories_burned = st.number_input("Calories Burned" if lang=="EN" else "Počet spálených kalórií", min_value=0, max_value=1000)
    if st.button("💾 Log Exercise" if lang=="EN" else "Zaznamenať cvičenie"):
        if 'exercise_log' not in st.session_state:
            st.session_state.exercise_log = []
        st.session_state.exercise_log.append({
            "Date": str(date.today()),
            "Type": exercise_type,
            "Duration": duration,
            "Calories": calories_burned
        })
        st.success(f"{exercise_type} of {duration} min logged!")

# Display Water & Exercise logs
if 'water_log' in st.session_state:
    df_water = pd.DataFrame(st.session_state.water_log)
    st.subheader("💧 Water Intake History" if lang=="EN" else "História príjmu vody")
    st.dataframe(df_water)

if 'exercise_log' in st.session_state:
    df_ex = pd.DataFrame(st.session_state.exercise_log)
    st.subheader("🏃 Exercise History" if lang=="EN" else "História cvičenia")
    st.dataframe(df_ex)
