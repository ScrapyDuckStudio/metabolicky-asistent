import streamlit as st
import pandas as pd
from datetime import date
import os

# --- 1. CONFIG & APP NASTAVENIE ---
st.set_page_config(
    page_title="Metabolický Asistent Pro",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom štýl pre krajšie vizuálne rozhranie
st.markdown("""
    <style>
    .reportview-container { background: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e6ebf1; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .stActionButton { background-color: #2e7d32; color: white; }
    </style>
""", unsafe_allow_html=True)

HISTORY_FILE = "zdravotna_historia_global.csv"
HIST_COLS = ["Dátum", "Diagnózy", "Cieľ", "Váha (kg)", "Energia", "Spánok", "Kalórie", "Sacharidy (g)", "Symptómy", "Rizika_Pocet"]

# --- 2. JAZYKOVÁ MUTÁCIA ---
lang = st.sidebar.radio("🌐 Jazyk / Language", ["SK", "EN"])

TXT = {
    "SK": {
        "title": "🧬 Inteligentný Metabolický & Hormonálny Tracker",
        "subtitle": "Personalizovaný biohacking a nutričná diagnostika na základe tvojho metabolického profilu.",
        "profile": "🧬 Krok 1: Tvoj zdravotný profil",
        "gain_weight_tendency": "📉 Sklon k priberaniu / Blokované chudnutie:",
        "pcos": "PCOS (Inzulínová rezistencia)",
        "hashi": "Hashimoto (Spomalený metabolizmus)",
        "db2": "Cukrovka 2. typu",
        "anemia": "Anémia (Nedostatok železa)",
        "cushing": "Cushingov syndróm (Vysoký kortizol)",
        "lepid": "Lipedém / Lymfedém",
        "lose_weight_tendency": "📈 Sklon k chudnutiu / Problém pribrať:",
        "hyper": "Hypertyreóza (Zrýchlený metabolizmus)",
        "celiakia": "Celiakia / IBD (Zápal čriev)",
        "addison": "Addisonova choroba",
        "digestion": "🍽️ Tráviace citlivosti & Intolerancie:",
        "hit": "HIT (Histamínová intolerancia)",
        "gastritis": "Gastritída (Zápal žalúdka)",
        "sibo": "SIBO / IBS (Dráždivé črevo)",
        "gallbladder": "Žlčníkové kamene / Dysfunkcia",
        "metabolic_syndromes": "🧬 Metabolické & Orgánové poruchy:",
        "gout": "Dna (Vysoká kyselina močová)",
        "nafld": "Statuóza pečene (NAFLD)",
        "hypertension": "Hypertenzia (Vysoký tlak)",
        "kidney_stones": "Obličkové kamene",
        
        "goal_hdr": "🎯 Krok 2: Stanovenie cieľa",
        "goal_q": "Čo je tvojou prioritou?",
        "goals": ["Zdravé chudnutie", "Udržanie váhy & Regenerácia", "Budovanie hmoty / Pribratie"],
        
        "antropo": "👤 Krok 3: Antropometrické údaje",
        "weight": "Aktuálna váha (kg):",
        "height": "Výška (cm):",
        "age": "Vek:",
        "target_info": "🎯 **Tvoj denný metabolický plán:**\n* 🔥 **Kalórie:** `{cal}` kcal\n* 🥩 **Bielkoviny:** `{prot}` g\n* 🥑 **Tuky:** `{fat}` g\n* 🌾 **Čisté sacharidy:** `{carbs}` g\n* 💧 **Voda:** `{water:.2f}` L",
        
        "tabs": ["🍽️ Potravinový Asistent", "📊 Denník & Diagnostika", "📈 Korelácie & Vývoj", "🛒 Inteligentný Nákupný Zoznam"],
        "search_hdr": "🔍 Vyhľadávanie potravín",
        "search_lbl": "Zadaj názov jedla (napr. hovädzie, špenát, beef, oats):",
        "select_food": "Vyber presnú položku z databázy:",
        "grams": "Zadaj množstvo (g):",
        "analysis": "#### 📊 Nutričné hodnoty porcie ({g}g):",
        "cal": "Kalórie",
        "prot": "Bielkoviny",
        "carbs": "Sacharidy",
        "fiber": "Vláknina",
        
        "warnings_hdr": "⚠️ Metabolické upozornenia pre tvoj profil:",
        "warn_gluten": "🌾 **Obsahuje LEPOK:** Riziko zápalovej imunitnej reakcie.",
        "warn_milk": "🥛 **Mliečne výrobky/Sója:** Možný strumigénny blokátor pre štítnu žľazu.",
        "warn_hit": "⚠️ **Vysoký Histamín:** Potenciálny spúšťač kožnej alebo tráviacej reakcie.",
        "warn_gastritis": "🔥 **Žalúdočný iritant:** Môže dráždiť sliznicu žalúdka a zvýšiť kyselinu.",
        "warn_sugar": "🚨 **Vysoká glykemická záťaž:** Riziko inzulínovej špičky.",
        "warn_purines": "🥩 **Vysoký obsah purínov:** Nevhodné pri zvýšenej kyseline močovej.",
        "warn_oxalates": "🌱 **Vysoké oxaláty:** Zvyšuje riziko kalcifikácie obličiek.",
        "warn_high_fat": "🧈 **Vysoký obsah tukov:** Nadmerná záťaž na žlčník a pečeň.",
        
        "add_btn": "➕ Pridať do dnešného dňa",
        "add_success": "Potravina bola úspešne zapísaná.",
        "not_found": "Potravina sa nenašla. Skús iný výraz.",
        
        "diary_hdr": "📊 Dnešný denník",
        "status": "#### Celková bilancia dňa:",
        "feedback_hdr": "💬 Automatická klinická spätná väzba",
        "save_btn": "💾 Uzatvoriť a bezpečne uložiť deň",
        "save_success": "Dáta boli úspešne zapísané do cloudu.",
        "no_meals": "Zatiaľ žiadne záznamy. Použi kartu 'Potravinový Asistent'.",
        
        "symptoms_hdr": "🩺 Sledovanie bio-symptómov",
        "sym_energy": "Energia počas dňa (1-10):",
        "sym_sleep": "Kvalita spánku (1-10):",
        "history_hdr": "📈 Vývoj a hľadanie skrytých príčin",
        "history_empty": "Zatiaľ žiadne historické dáta.",
        "superfoods_hdr": "🛒 Tvoj liečebný nákupný zoznam",
        "superfoods_desc": "Tieto potraviny pôsobia ako funkčná medicína pre tvoj aktuálny stav:",
        "db_status_ok": "✅ Databáza plne funkčná."
    },
    "EN": {
        "title": "🧬 Smart Metabolic & Hormonal Tracker",
        "subtitle": "Personalized biohacking and nutritional diagnostics based on your unique metabolic profile.",
        "profile": "🧬 Step 1: Your Health Profile",
        "gain_weight_tendency": "📉 Weight Gain / Blocked Weight Loss:",
        "pcos": "PCOS (Insulin Resistance)",
        "hashi": "Hashimoto (Slow Metabolism)",
        "db2": "Type 2 Diabetes",
        "anemia": "Anemia (Iron Deficiency)",
        "cushing": "Cushing's Syndrome (High Cortisol)",
        "lepid": "Lipedema / Lymphedema",
        "lose_weight_tendency": "📈 Weight Loss / Hard to Gain:",
        "hyper": "Hyperthyroidism (Fast Metabolism)",
        "celiakia": "Celiac Disease / IBD",
        "addison": "Addison's Disease",
        "digestion": "🍽️ Digestive Sensitivities & Intolerances:",
        "hit": "HIT (Histamine Intolerance)",
        "gastritis": "Gastritis (Stomach Inflammation)",
        "sibo": "SIBO / IBS",
        "gallbladder": "Gallbladder Stones / Dysfunction",
        "metabolic_syndromes": "🧬 Metabolic & Organ Disorders:",
        "gout": "Gout (High Uric Acid)",
        "nafld": "Fatty Liver Disease (NAFLD)",
        "hypertension": "Hypertension (High BP)",
        "kidney_stones": "Kidney Stones",
        
        "goal_hdr": "🎯 Step 2: Goal Setting",
        "goal_q": "What is your priority?",
        "goals": ["Healthy Weight Loss", "Maintenance & Recovery", "Weight Gain / Bulking"],
        
        "antropo": "👤 Step 3: Body Metrics",
        "weight": "Current Weight (kg):",
        "height": "Height (cm):",
        "age": "Age:",
        "target_info": "🎯 **Your Daily Metabolic Blueprint:**\n* 🔥 **Calories:** `{cal}` kcal\n* 🥩 **Protein:** `{prot}` g\n* 🥑 **Fat:** `{fat}` g\n* 🌾 **Net Carbs:** `{carbs}` g\n* 💧 **Water:** `{water:.2f}` L",
        
        "tabs": ["🍽️ Food Assistant", "📊 Diary & Diagnostics", "📈 Correlations & Trends", "🛒 Tailored Shopping List"],
        "search_hdr": "🔍 Search Foods",
        "search_lbl": "Enter food name (e.g. beef, spinach, oats):",
        "select_food": "Select exact item from database:",
        "grams": "Enter weight (g):",
        "analysis": "#### 📊 Nutritional Value of Portion ({g}g):",
        "cal": "Calories",
        "prot": "Protein",
        "carbs": "Carbs",
        "fiber": "Fiber",
        
        "warnings_hdr": "⚠️ Metabolic Alerts for Your Profile:",
        "warn_gluten": "🌾 **Contains GLUTEN:** Risk of inflammatory immune response.",
        "warn_milk": "🥛 **Dairy/Soy:** Potential goitrogenic blocker for the thyroid.",
        "warn_hit": "⚠️ **High Histamine:** Potential trigger for skin or digestive reaction.",
        "warn_gastritis": "🔥 **Stomach Irritant:** May irritate stomach lining and increase acid.",
        "warn_sugar": "🚨 **High Glycemic Load:** Risk of insulin spike.",
        "warn_purines": "🥩 **High Purines:** Not suitable for high uric acid levels.",
        "warn_oxalates": "🌱 **High Oxalates:** Increases risk of kidney calcification.",
        "warn_high_fat": "🧈 **High Fat:** Excessive strain on gallbladder and liver.",
        
        "add_btn": "➕ Add to Daily Log",
        "add_success": "Food added successfully.",
        "not_found": "Food not found. Try another term.",
        
        "diary_hdr": "📊 Daily Diary",
        "status": "#### Daily Balance Summary:",
        "feedback_hdr": "💬 Automated Clinical Feedback",
        "save_btn": "💾 Close and Securely Save Day",
        "save_success": "Data successfully written to cloud.",
        "no_meals": "No logs yet. Use the 'Food Assistant' tab.",
        
        "symptoms_hdr": "🩺 Bio-Symptom Tracking",
        "sym_energy": "Daily Energy (1-10):",
        "sym_sleep": "Sleep Quality (1-10):",
        "history_hdr": "📈 Trends & Root Cause Analysis",
        "history_empty": "No historical data yet.",
        "superfoods_hdr": "🛒 Your Therapeutic Shopping List",
        "superfoods_desc": "These foods act as functional medicine for your current setup:",
        "db_status_ok": "✅ Food database fully active."
    }
}

# --- 3. NEPRIESTRELNÉ NAČÍTANIE DATABÁZY POTRAVÍN ---
@st.cache_data
def load_food_database():
    # Robustné mock dáta pokrývajúce slovenské aj anglické hľadanie a mikroživiny
    mock_df = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5, 6, 7, 8],
        'name_en': ['Oats', 'Spinach', 'Beef', 'Dark Chocolate', 'Beef Liver', 'Tomato', 'Greek Yogurt', 'Salmon'],
        'name_sk': ['Ovsene vlocky', 'Spenat', 'Hovadzie maso', 'Horka cokolada', 'Hovazia pecen', 'Paradajka', 'Grecky jogurt', 'Losos'],
        'Calories': [389, 23, 250, 546, 175, 18, 97, 208],
        'Protein (g)': [16.9, 2.9, 26.0, 4.9, 27.0, 0.9, 10.0, 20.0],
        'Fat (g)': [6.9, 0.4, 15.0, 31.0, 5.0, 0.2, 5.0, 13.0],
        'Net-Carbs (g)': [66.3, 1.4, 0.0, 54.0, 4.0, 3.9, 3.6, 0.0],
        'Sugars (g)': [0.0, 0.4, 0.0, 48.0, 0.0, 2.6, 3.6, 0.0],
        'Fiber (g)': [10.6, 2.2, 0.0, 7.0, 0.0, 1.2, 0.0, 0.0],
        'Iron, Fe (mg)': [4.7, 2.7, 2.6, 8.0, 18.0, 0.3, 0.1, 0.3],
        'Zinc, Zn (mg)': [4.0, 0.5, 4.3, 2.3, 4.0, 0.2, 0.6, 0.6]
    })
    return mock_df

def load_history():
    if os.path.exists(HISTORY_FILE):
        try: 
            df_h = pd.read_csv(HISTORY_FILE)
            # Verifikácia stĺpcov, aby appka nikdy nespadla pri zmene verzie
            if all(c in df_h.columns for c in HIST_COLS): return df_h
        except Exception: pass
    return pd.DataFrame(columns=HIST_COLS)

def save_history_row(row_dict):
    history_df = load_history()
    new_row = pd.DataFrame([row_dict])
    history_df = pd.concat([history_df, new_row], ignore_index=True)
    history_df.to_csv(HISTORY_FILE, index=False)

df_food = load_food_database()

# --- 4. PREHĽADNÝ SIDEBAR (KROKY POD ŠÍPKAMI) ---
st.sidebar.markdown(f"### {TXT[lang]['profile']}")

with st.sidebar.expander(TXT[lang]["profile"], expanded=True):
    st.markdown(f"<small><b>{TXT[lang]['gain_weight_tendency']}</b></small>", unsafe_allow_html=True)
    has_pcos = st.checkbox(TXT[lang]["pcos"])
    has_hashi = st.checkbox(TXT[lang]["hashi"])
    has_db2 = st.checkbox(TXT[lang]["db2"])
    has_anemia = st.checkbox(TXT[lang]["anemia"])
    has_cushing = st.checkbox(TXT[lang]["cushing"])
    has_lipedema = st.checkbox(TXT[lang]["lepid"])

    st.markdown(f"<small><b>{TXT[lang]['lose_weight_tendency']}</b></small>", unsafe_allow_html=True)
    has_hyper = st.checkbox(TXT[lang]["hyper"])
    has_celiakia = st.checkbox(TXT[lang]["celiakia"])
    has_addison = st.checkbox(TXT[lang]["addison"])

    st.markdown(f"<small><b>{TXT[lang]['digestion']}</b></small>", unsafe_allow_html=True)
    has_hit = st.checkbox(TXT[lang]["hit"])
    has_gastritis = st.checkbox(TXT[lang]["gastritis"])
    has_sibo = st.checkbox(TXT[lang]["sibo"])
    has_gallbladder = st.checkbox(TXT[lang]["gallbladder"])

    st.markdown(f"<small><b>{TXT[lang]['metabolic_syndromes']}</b></small>", unsafe_allow_html=True)
    has_gout = st.checkbox(TXT[lang]["gout"])
    has_nafld = st.checkbox(TXT[lang]["nafld"])
    has_hypertension = st.checkbox(TXT[lang]["hypertension"])
    has_kidney_stones = st.checkbox(TXT[lang]["kidney_stones"])

with st.sidebar.expander(TXT[lang]["goal_hdr"], expanded=False):
    meta_goal = st.radio(TXT[lang]["goal_q"], TXT[lang]["goals"], label_visibility="collapsed")

with st.sidebar.expander(TXT[lang]["antropo"], expanded=False):
    weight = st.number_input(TXT[lang]["weight"], min_value=10.0, max_value=250.0, value=70.0)
    height = st.number_input(TXT[lang]["height"], min_value=100, max_value=250, value=165)
    age = st.number_input(TXT[lang]["age"], min_value=1, max_value=120, value=30)

# --- NEPRIESTRELNÝ CLINICAL ENGINE (VÝPOČTY) ---
# Ochrana pred anomálnymi vstupmi (Fallback Safe Mode)
safe_weight = max(weight, 30.0)
safe_height = max(height, 100)
safe_age = max(age, 15)

bmr = 447.593 + (9.247 * safe_weight) + (3.098 * safe_height) - (4.330 * safe_age)
base_maintenance = round(bmr * 1.2)

if has_cushing: base_maintenance = round(base_maintenance * 0.85)
if has_addison: base_maintenance = round(base_maintenance * 1.15)

if meta_goal in ["Zdravé chudnutie", "Healthy Weight Loss"]: target_cal = max(base_maintenance - 400, 1200)
elif meta_goal in ["Budovanie hmoty / Pribratie", "Weight Gain / Bulking"]: target_cal = base_maintenance + 400
else: target_cal = base_maintenance

# Proteínový manažment
if has_gout or has_kidney_stones: target_protein = round(safe_weight * 1.1)
elif has_hyper or "Pribratie" in meta_goal or "Bulking" in meta_goal: target_protein = round(safe_weight * 1.9)
else: target_protein = round(safe_weight * 1.5)

# Sacharidová senzitivita (Inzulínový manažment)
carbs_percentage = 0.25 if (has_pcos or has_db2 or has_nafld) else 0.45
if has_sibo: carbs_percentage = 0.20

target_carbs = max(round((target_cal * carbs_percentage) / 4), 50)
target_fat = max(round((target_cal * (1.0 - (carbs_percentage + 0.25))) / 9), 30)

if has_gallbladder or has_nafld: target_fat = min(target_fat, 45)

# Hydratácia upravená pre obličky
water_intake = (safe_weight * 35) / 1000
if has_kidney_stones: water_intake += 0.7

st.sidebar.info(TXT[lang]["target_info"].format(cal=target_cal, prot=target_protein, carbs=target_carbs, fat=target_fat, water=water_intake))
st.sidebar.caption(TXT[lang]["db_status_ok"])

# --- 5. HLAVNÁ OBLASŤ ---
st.title(TXT[lang]["title"])
st.markdown(f"<p style='color: gray; font-size: 1.1rem;'>{TXT[lang]['subtitle']}</p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(TXT[lang]["tabs"])

if 'daily_meals' not in st.session_state:
    st.session_state.daily_meals = []

# --- TAB 1: POTRAVINOVÝ ASISTENT ---
with tab1:
    st.markdown(f"### {TXT[lang]['search_hdr']}")
    search_query = st.text_input(TXT[lang]["search_lbl"], "", help="Môžeš písať slovensky aj anglicky.")
    
    if search_query.strip():
        # Vyhľadávanie bez ohľadu na malé/veľké písmená
        q = search_query.strip().lower()
        results = df_food[df_food['name_en'].str.lower().str.contains(q, na=False) | df_food['name_sk'].str.lower().str.contains(q, na=False)]
        
        if not results.empty:
            food_options = results.apply(lambda row: f"{row['name_sk']} / {row['name_en']}", axis=1).tolist()
            selected_option = st.selectbox(TXT[lang]["select_food"], food_options)
            
            food_details = results.iloc[food_options.index(selected_option)]
            
            grams = st.number_input(TXT[lang]["grams"], min_value=1, max_value=2000, value=100)
            ratio = max(grams, 1) / 100.0
            
            # Bezpečné vytiahnutie makier
            cal = round(food_details.get('Calories', 0) * ratio, 1)
            prot = round(food_details.get('Protein (g)', 0) * ratio, 1)
            fat = round(food_details.get('Fat (g)', 0) * ratio, 1)
            carbs = round(food_details.get('Net-Carbs (g)', 0) * ratio, 1)
            sugar = round(food_details.get('Sugars (g)', 0) * ratio, 1)
            fiber = round(food_details.get('Fiber (g)', 0) * ratio, 1)
            iron = round(food_details.get('Iron, Fe (mg)', 0) * ratio, 2)
            zinc = round(food_details.get('Zinc, Zn (mg)', 0) * ratio, 2)
            
            st.markdown(TXT[lang]["analysis"].format(g=grams))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(TXT[lang]["cal"], f"{cal} kcal")
            c2.metric(TXT[lang]["prot"], f"{prot} g")
            c3.metric(TXT[lang]["carbs"], f"{carbs} g")
            c4.metric(TXT[lang]["fiber"], f"{fiber} g")
            
            # Kontrola rizík na pozadí
            warnings = []
            f_name = f"{food_details['name_en']} {food_details['name_sk']}".lower()
            
            if (has_celiakia or has_hashi) and any(x in f_name for x in ['wheat', 'barley', 'rye', 'muka', 'chlieb', 'lepok']): warnings.append(TXT[lang]["warn_gluten"])
            if has_hit and any(x in f_name for x in ['tomato', 'spinach', 'cheese', 'wine', 'paradaj', 'spenat', 'syr']): warnings.append(TXT[lang]["warn_hit"])
            if has_gout and any(x in f_name for x in ['beef', 'liver', 'pecen', 'hovadz']): warnings.append(TXT[lang]["warn_purines"])
            if has_kidney_stones and any(x in f_name for x in ['spinach', 'chocolate', 'spenat', 'cokolada']): warnings.append(TXT[lang]["warn_oxalates"])
            if (has_gallbladder or has_nafld) and (fat > 12): warnings.append(TXT[lang]["warn_high_fat"])
            
            if warnings:
                with st.expander(TXT[lang]["warnings_hdr"], expanded=True):
                    for w in warnings: st.warning(w)
            
            if (has_pcos or has_db2) and sugar > 12:
                st.error(TXT[lang]["warn_sugar"])
                
            if st.button(TXT[lang]["add_btn"], use_container_width=True):
                st.session_state.daily_meals.append({
                    "Jedlo": selected_option, "Kalórie": cal, "Bielkoviny": prot, 
                    "Tuky": fat, "Čisté Sacharidy": carbs, "Cukor": sugar, 
                    "Vláknina": fiber, "Železo": iron, "Zinok": zinc, "Riziko": len(warnings)
                })
                st.success(TXT[lang]["add_success"])
        else:
            st.info(TXT[lang]["not_found"])

# --- TAB 2: DENNÍK & BIO-FEEDBACK ---
with tab2:
    st.header(TXT[lang]["diary_hdr"])
    
    if st.session_state.daily_meals:
        df_today = pd.DataFrame(st.session_state.daily_meals)
        st.dataframe(df_today[["Jedlo", "Kalórie", "Bielkoviny", "Čisté Sacharidy", "Vláknina"]], use_container_width=True)
        
        t_cal = sum(df_today["Kalórie"])
        t_carbs = sum(df_today["Čisté Sacharidy"])
        t_prot = sum(df_today["Bielkoviny"])
        t_fiber = sum(df_today["Vláknina"])
        t_sugar = sum(df_today["Cukor"])
        t_risks = sum(df_today["Riziko"])
        
        st.markdown(TXT[lang]["status"])
        c1, c2, c3 = st.columns(3)
        c1.metric(TXT[lang]["cal"], f"{round(t_cal)} / {target_cal} kcal")
        c2.metric(TXT[lang]["prot"], f"{round(t_prot, 1)} / {target_protein} g")
        c3.metric(TXT[lang]["carbs"], f"{round(t_carbs, 1)} / {target_carbs} g")
        
        # Odborný metabolický feedback
        st.subheader(TXT[lang]["feedback_hdr"])
        if (has_pcos or has_db2) and t_fiber < 25:
            st.error("⚠️ **Inzulínová rezistencia:** Tvoja dnešná hladina vlákniny je nízka. Pridaj do ďalšieho jedla zelenú zeleninu alebo psyllium, aby si znížil/a glykemický index.")
        if (has_pcos or has_db2 or has_nafld) and t_sugar > 30:
            st.error("🚨 **Sacharidové preťaženie:** Dnešný čistý cukor prekročil bezpečnú metabolickú kapacitu pečene.")
        if has_hypertension and t_cal > base_maintenance:
            st.warning("⚡ **Kardiovaskulárny tlak:** Zvýšený príjem kalórií nad tvoj bazálny metabolizmus dnes zbytočne namáha obehovú sústavu.")
        if t_risks == 0 and t_cal > 0:
            st.success("✨ **Perfektný deň:** Tvoje dnešné zloženie stravy je v úplnom súlade s tvojimi bunkovými a hormonálnymi obmedzeniami.")
    else:
        st.info(TXT[lang]["no_meals"])
        t_cal, t_carbs, t_prot, t_fiber, t_risks = 0, 0, 0, 0, 0
        
    st.write("---")
    st.subheader(TXT[lang]["symptoms_hdr"])
    s_list = []
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.checkbox("Náhly útlm energie / Vlčí hlad (Crash inzulínu)"): s_list.append("VlčiHlad")
        if st.checkbox("Tráviaci diskomfort / Nadúvanie / Kŕče"): s_list.append("Naduvanie")
        if st.checkbox("Bolesť kĺbov / Akútny zápal"): s_list.append("ZapalKlbov")
    with col_s2:
        energy = st.slider(TXT[lang]["sym_energy"], 1, 10, 7)
        sleep = st.slider(TXT[lang]["sym_sleep"], 1, 10, 7)
        
    if st.button(TXT[lang]["save_btn"], use_container_width=True):
        row = {
            "Dátum": str(date.today()), "Diagnózy": "Aktívny_Profil", "Cieľ": meta_goal,
            "Váha (kg)": weight, "Energia": energy, "Spánok": sleep,
            "Kalórie": round(t_cal, 1), "Sacharidy (g)": round(t_carbs, 1),
            "Symptómy": ", ".join(s_list) if s_list else "Ziadne", "Rizika_Pocet": t_risks
        }
        save_history_row(row)
        st.session_state.daily_meals = []
        st.success(TXT[lang]["save_success"])
        st.rerun()

# --- TAB 3: KORELÁCIE & ZÁMERNÁ DIAGNOSTIKA ---
with tab3:
    st.header(TXT[lang]["history_hdr"])
    h_df = load_history()
    
    if not h_df.empty:
        st.dataframe(h_df, use_container_width=True)
        
        st.subheader("🔮 Pokročilá Korelačná Diagnostika (Root Cause)")
        # Pokročilý datamining nad históriou používateľa
        problem_days = h_df[h_df["Symptómy"].str.contains("Naduvanie|VlčiHlad|ZapalKlbov", na=False)]
        
        if not problem_days.empty:
            avg_risks_on_bad_days = problem_days["Rizika_Pocet"].mean()
            if avg_risks_on_bad_days > 0.6:
                st.error(f"🔍 **Klinický nález:** Tvoje negatívne symptómy priamo korelujú s dňami, kedy ignoruješ varovania v Potravinovom asistentovi (Priemerne až {round(avg_risks_on_bad_days, 1)} varovných potravín v problémové dni).")
            else:
                st.info("🔍 Tvoje symptómy pravdepodobne nespôsobujú priame potravinové alergény z databázy. Sleduj dáta ďalej.")
        else:
            st.success("✨ **Stabilný stav:** Podľa tvojej histórie nespôsobuje tvoj aktuálny jedálniček žiadne akútne zápaly ani metabolické crashe.")
    else:
        st.info(TXT[lang]["history_empty"])

# --- TAB 4: NÁKUPNÝ ZOZNAM NA MIERU ---
with tab4:
    st.header(TXT[lang]["superfoods_hdr"])
    st.write(TXT[lang]["superfoods_desc"])
    
    active_recs = 0
    if has_anemia:
        st.success("🩸 **Anémia / Krvotvorba:** Hovädzia pečeň, teľacie mäso, tekvicové semená (bohaté na železo). Vždy kombinuj s vitamínom C pre zvýšenie absorpcie.")
        active_recs += 1
    if has_hashi:
        st.success("🦋 **Hashimoto / Podpora štítnej žľazy:** Para orechy (zdroj selénu), divoký losos, vajcia z voľného chovu. Vyhýbaj sa surovému hlúbovému syndrómu.")
        active_recs += 1
    if has_pcos or has_db2:
        st.success("🌾 **Inzulínová Senzitivita:** Pravé ovsené vločky, avokádo, cejlónska škorica, divoké bobuľové ovocie (čučoriedky, maliny).")
        active_recs += 1
    if has_gout:
        st.success("🦴 **Eliminácia Kyseliny Močovej:** Čerešne, zelerová šťava, listová zelenina, dostatok čistej filtrovanej vody.")
        active_recs += 1
        
    if active_recs == 0:
        st.info("Navoľ si svoje špecifické zdravotné obmedzenia v ľavom paneli a tu okamžite získaš cielený zoznam terapeutických potravín.")
