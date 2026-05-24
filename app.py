import streamlit as st
import pandas as pd
from datetime import date
import os

# --- NASTAVENIE STRÁNKY ---
st.set_page_config(page_title="Metabolický Asistent & Inteligentný Kouč", layout="wide", page_icon="🩺")

# --- CUSTOM CSS (VIZUÁLNE VYLEPŠENIA) ---
# --- CUSTOM CSS (VIZUÁLNE VYLEPŠENIA - THEME ADAPTIVE) ---
custom_css = """
<style>
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        background-color: #2ecc71;
        color: white !important;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #27ae60;
        box-shadow: 0 4px 12px rgba(46, 204, 113, 0.4);
        color: white !important;
    }
    
    /* Metrics / Cards - Adapts to Dark/Light Mode */
    div[data-testid="metric-container"] {
        background-color: rgba(127, 140, 141, 0.1); /* Transparent grey */
        border: 1px solid rgba(127, 140, 141, 0.2);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #3498db !important; /* Medical blue */
        font-weight: bold;
    }
    
    /* Tabs - Adapts to Dark/Light Mode */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(52, 152, 219, 0.1);
        border-top: 3px solid #3498db;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

HISTORY_FILE = "zdravotna_historia_global.csv"

# --- JAZYKOVÝ SLOVNÍK (TRANSLATIONS) ---
lang = st.sidebar.radio("🌐 Jazyk / Language", ["SK", "EN"], horizontal=True)

TXT = {
    "SK": {
        "title": "🩺 Inteligentný Metabolický & Hormonálny Tracker",
        "profile": "🧬 Krok 1: Zdravotný profil",
        "gain_weight_tendency": "📉 Sklon k priberaniu / Blokácia chudnutia:",
        "pcos": "PCOS (Inzulínová rezistencia)",
        "hashi": "Hashimoto (Spomalený metabolizmus)",
        "db2": "Cukrovka 2. typu",
        "anemia": "Anémia (Nedostatok železa)",
        "cushing": "Cushingov syndróm (Vysoký kortizol)",
        "lepid": "Lipedém / Lymfedém",
        "lose_weight_tendency": "📈 Sklon k chudnutiu / Problém pribrať:",
        "hyper": "Hypertyreóza (Zrýchlený metabolizmus)",
        "celiakia": "Celiakia / IBD (Porucha vstrebávania)",
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
        "goal_hdr": "🎯 Krok 2: Tvoj cieľ",
        "goal_q": "Čo chceš dosiahnuť?",
        "goals": ["Zdravé chudnutie", "Udržanie váhy & Regenerácia", "Zdravé pribratie (Budovanie hmoty)"],
        "antropo": "👤 Krok 3: Tvoje údaje",
        "weight": "Váha (kg):",
        "height": "Výška (cm):",
        "age": "Vek:",
        "target_info": "🎯 **Tvoj cieľový príjem:**\n* **Kalórie:** {cal} kcal\n* **Bielkoviny:** {prot} g\n* **Čisté sacharidy:** {carbs} g\n* **Tuky:** {fat} g",
        "tabs": ["🍽️ Potravinový asistent", "📊 Dnešný denník", "📈 Dlhodobý vývoj"],
        "search_hdr": "🔍 Hľadať potravinu",
        "search_lbl": "Zadaj názov v slovenčine alebo angličtine:",
        "select_food": "Vyber potravinu:",
        "grams": "Gramáž (g):",
        "analysis": "#### 📊 Analýza pre {g}g:",
        "cal": "Kalórie",
        "prot": "Bielkoviny",
        "carbs": "Sacharidy",
        "fiber": "Vláknina",
        "warnings_hdr": "### 🚨 Zdravotné upozornenia:",
        "warn_gluten": "🌾 **Obsahuje LEPKOVKU:** Riziko zápalovej reakcie čreva.",
        "warn_milk": "🥛/🫛 **Mlieko/Sója:** Možný skrížený alergén pre štítnu žľazu.",
        "warn_hit": "⚠️ **Vysoký Histamín:** Sleduj reakciu tela.",
        "warn_gastritis": "🔥 **Žalúdočný iritant:** Môže dráždiť žalúdok.",
        "warn_sugar": "🚨 **Pozor na cukor:** Vysoká inzulínová špička.",
        "warn_purines": "🥩 **Vysoké puríny (Dna):** Riziko záchvatu dny a zvýšenia kyseliny močovej.",
        "warn_oxalates": "🌱 **Vysoké oxaláty:** Nebezpečenstvo vzniku obličkových kameňov.",
        "warn_high_fat": "🧈 **Vysoký obsah tuku:** Môže podráždiť žlčník alebo zhoršiť steatózu pečene.",
        "add_btn": "➕ Pridať do dňa",
        "add_success": "Pridané do dnešného prehľadu.",
        "not_found": "Slovo sa v databáze nenašlo.",
        "encyclopedia": "### 💡 Encyklopédia metabolizmu",
        "enc_pcos_t": "🌾 Inzulínový blok",
        "enc_pcos_b": "**PCOS & Cukrovka 2. typu:** Vláknina a nízky cukor sú kľúč k obnove citlivosti na inzulín.",
        "enc_hashi_t": "🦋 Spomalený motor (Hashimoto)",
        "enc_hashi_b": "**Hypotyreóza:** Bielkoviny, zinok a selén chránia svaly a stimulujú metabolizmus.",
        "enc_hyper_t": "🔥 Prehriaty motor (Hypertyreóza)",
        "enc_hyper_b": "**Zvýšená funkcia:** Telo rýchlo odbúrava hmotu. Potrebuješ zdravý kalorický prebytok.",
        "enc_anemia_t": "🩸 Kyslíkový dlh (Anémia)",
        "enc_anemia_b": "**Chýbajúce železo:** Bez železa chýba bunkám kyslík a chudnutie/regenerácia sa zaseknú.",
        "enc_gout_t": "🦴 Kyselina močová (Dna)",
        "enc_gout_b": "**Dna:** Vyhýbaj sa červenému mäsu, vnútornostiam, alkoholu a nadmernej fruktóze.",
        "enc_nafld_t": "🍏 Tuk v pečeni (NAFLD)",
        "enc_nafld_b": "**Steatóza:** Minimalizuj priemyselné cukry a trans-tuky.",
        "diary_hdr": "📊 Tvoj dnešný denník",
        "status": "#### Aktuálny stav dňa:",
        "feedback_hdr": "💬 Personalizované spätné väzby",
        "fb_pcos_fiber_low": "🌾 **PCOS/Cukrovka:** Dnes máš nízky príjem vlákniny (menej ako 25g).",
        "fb_pcos_fiber_ok": "✨ **PCOS/Cukrovka:** Skvelé! Dosiahla si parádny príjem vlákniny.",
        "fb_pcos_sugar_high": "🚨 **PCOS/Pečeň:** Pozor, cukor prekročil bezpečnú hranicu (nad 35g).",
        "fb_anemia_iron_low": "🩸 **Anémia:** Dnes si prijala len {iron} mg železa.",
        "fb_anemia_iron_ok": "💪 **Anémia:** Perfektné! Máš bohatý príjem železa.",
        "fb_hashi_zinc_low": "🦋 **Hashimoto:** Tvoj zinok je dnes nízky ({zinc} mg).",
        "fb_hashi_risks": "⚠️ **Hashimoto:** Zjedla si dnes {risks} potravín so spúšťačom.",
        "fb_celiakia_risk": "🚨 **Celiakia:** V denníku máš jedlo s obsahom lepku!",
        "fb_gastritis_risk": "🔥 **Gastritída:** Zaznamenala si potravinu dráždiacu žalúdok.",
        "fb_gout_risk": "🦴 **Dna:** Pozor, jedlo s purínmi môže vyvolať bolesť.",
        "fb_perfect": "☀️ Tvoj dnešný jedálniček perfektne rešpektuje tvoj zdravotný stav.",
        "no_meals": "Zatiaľ si nezadala žiadne potraviny.",
        "symptoms_hdr": "🩺 Sledovanie príznakov",
        "sym_gain_fatigue": "**Symptómy príberania/Únavy:**",
        "sym_hunger": "Náhly vlčí hlad",
        "sym_weakness": "Extrémna svalová slabosť",
        "sym_bloating": "Nadúvanie/Plynatosť",
        "sym_lose_weight": "**Symptómy straty hmotnosti/Zápalov:**",
        "sym_palpitations": "Búšenie srdca",
        "sym_cramps": "Kŕče v bruchu",
        "sym_gout_pain": "Bolesť kĺbov (Dna)",
        "sym_subjective": "**Subjektívne pocity:**",
        "sym_energy": "Energia (1-10):",
        "sym_sleep": "Spánok (1-10):",
        "save_btn": "💾 Ukončiť a uložiť deň",
        "save_success": "Záznam uložený!",
        "history_hdr": "📈 Dlhodobé sledovanie vývoja tela",
        "history_empty": "Žiadne historické záznamy neboli zatiaľ vytvorené.",
        "chart_title": "Graf: Pohyb telesnej hmotnosti (kg)",
        "none": "Žiadne",
        "err_save": "Nepodarilo sa uložiť na server",
        "db_status_ok": "✅ Databáza úspešne spárovaná.",
        "db_status_upload": "📁 Databáza nenájdená. Nahraj 'food_data_en_sk.csv':"
    },
    "EN": {
        "title": "🩺 Smart Metabolic & Hormonal Tracker",
        "profile": "🧬 Step 1: Health Profile",
        "gain_weight_tendency": "📉 Weight Gain / Loss Block:",
        "pcos": "PCOS (Insulin Resistance)",
        "hashi": "Hashimoto (Slow Metabolism)",
        "db2": "Type 2 Diabetes",
        "anemia": "Anemia (Iron Deficiency)",
        "cushing": "Cushing's Syndrome",
        "lepid": "Lipedema / Lymphedema",
        "lose_weight_tendency": "📈 Weight Loss / Problem Gaining:",
        "hyper": "Hyperthyroidism",
        "celiakia": "Celiac Disease / IBD",
        "addison": "Addison's Disease",
        "digestion": "🍽️ Digestive Sensitivities:",
        "hit": "HIT (Histamine Intolerance)",
        "gastritis": "Gastritis",
        "sibo": "SIBO / IBS",
        "gallbladder": "Gallbladder Issues",
        "metabolic_syndromes": "🧬 Metabolic & Organ Disorders:",
        "gout": "Gout (High Uric Acid)",
        "nafld": "Fatty Liver (NAFLD)",
        "hypertension": "Hypertension",
        "kidney_stones": "Kidney Stones",
        "goal_hdr": "🎯 Step 2: Your Goal",
        "goal_q": "What do you want to achieve?",
        "goals": ["Healthy Weight Loss", "Weight Maintenance & Recovery", "Healthy Weight Gain (Bulking)"],
        "antropo": "👤 Step 3: Your Data",
        "weight": "Weight (kg):",
        "height": "Height (cm):",
        "age": "Age:",
        "target_info": "🎯 **Your Target Intake:**\n* **Calories:** {cal} kcal\n* **Protein:** {prot} g\n* **Net Carbs:** {carbs} g\n* **Fat:** {fat} g",
        "tabs": ["🍽️ Food Assistant", "📊 Daily Diary", "📈 Long-term Progress"],
        "search_hdr": "🔍 Search Food",
        "search_lbl": "Enter name in Slovak or English:",
        "select_food": "Select food:",
        "grams": "Weight (g):",
        "analysis": "#### 📊 Analysis for {g}g:",
        "cal": "Calories",
        "prot": "Protein",
        "carbs": "Net Carbs",
        "fiber": "Fiber",
        "warnings_hdr": "### 🚨 Health Warnings:",
        "warn_gluten": "🌾 **Contains GLUTEN:** Risk of reaction.",
        "warn_milk": "🥛/🫛 **Milk/Soy:** Possible allergen.",
        "warn_hit": "⚠️ **High Histamine:** Monitor reaction.",
        "warn_gastritis": "🔥 **Stomach Irritant:** May irritate.",
        "warn_sugar": "🚨 **Watch out for sugar:** Insulin spike.",
        "warn_purines": "🥩 **High Purines (Gout):** Risk of attack.",
        "warn_oxalates": "🌱 **High Oxalates:** Risk of stones.",
        "warn_high_fat": "🧈 **High Fat:** May worsen gallbladder/NAFLD.",
        "add_btn": "➕ Add to Day",
        "add_success": "Added to today's overview.",
        "not_found": "Word not found in the database.",
        "encyclopedia": "### 💡 Metabolism Encyclopedia",
        "enc_pcos_t": "🌾 Insulin Block",
        "enc_pcos_b": "**PCOS & Diabetes:** Fiber is key to restoring sensitivity.",
        "enc_hashi_t": "🦋 Slow Motor (Hashimoto)",
        "enc_hashi_b": "**Hypothyroidism:** Protein and zinc protect muscles.",
        "enc_hyper_t": "🔥 Overheated Motor",
        "enc_hyper_b": "**Hyperthyroidism:** You need a caloric surplus.",
        "enc_anemia_t": "🩸 Oxygen Debt",
        "enc_anemia_b": "**Anemia:** Without iron, cells lack oxygen.",
        "enc_gout_t": "🦴 Uric Acid",
        "enc_gout_b": "**Gout:** Avoid red meat, organ meats, alcohol.",
        "enc_nafld_t": "🍏 Fatty Liver",
        "enc_nafld_b": "**Steatosis:** Minimize processed sugars.",
        "diary_hdr": "📊 Your Daily Diary",
        "status": "#### Current Daily Status:",
        "feedback_hdr": "💬 Personalized Feedback",
        "fb_pcos_fiber_low": "🌾 **PCOS/Diabetes:** Fiber intake is low (<25g).",
        "fb_pcos_fiber_ok": "✨ **PCOS/Diabetes:** Solid fiber intake today.",
        "fb_pcos_sugar_high": "🚨 **PCOS/NAFLD:** Sugar exceeded limit (>35g).",
        "fb_anemia_iron_low": "🩸 **Anemia:** Only {iron} mg of iron consumed.",
        "fb_anemia_iron_ok": "💪 **Anemia:** Rich iron intake today.",
        "fb_hashi_zinc_low": "🦋 **Hashimoto:** Zinc is low ({zinc} mg).",
        "fb_hashi_risks": "⚠️ **Hashimoto:** You ate {risks} foods with triggers.",
        "fb_celiakia_risk": "🚨 **Celiac:** Gluten-containing food logged!",
        "fb_gastritis_risk": "🔥 **Gastritis:** Stomach irritant logged.",
        "fb_gout_risk": "🦴 **Gout:** Purines can trigger joint pain.",
        "fb_perfect": "☀️ Your meal plan perfectly respects your health.",
        "no_meals": "No foods logged yet today.",
        "symptoms_hdr": "🩺 Symptom Tracking",
        "sym_gain_fatigue": "**Gain / Fatigue Symptoms:**",
        "sym_hunger": "Sudden ravenous hunger",
        "sym_weakness": "Extreme muscle weakness",
        "sym_bloating": "Bloating / Gas",
        "sym_lose_weight": "**Loss / Inflammation Symptoms:**",
        "sym_palpitations": "Heart palpitations",
        "sym_cramps": "Abdominal cramps",
        "sym_gout_pain": "Joint pain (Gout)",
        "sym_subjective": "**Subjective Feelings:**",
        "sym_energy": "Energy (1-10):",
        "sym_sleep": "Sleep quality (1-10):",
        "save_btn": "💾 Finish and Save Day",
        "save_success": "Log saved!",
        "history_hdr": "📈 Long-term Body Progress",
        "history_empty": "No history logs created yet.",
        "chart_title": "Chart: Body Weight Progress (kg)",
        "none": "None",
        "err_save": "Failed to save to server",
        "db_status_ok": "✅ Food database linked.",
        "db_status_upload": "📁 Upload 'food_data_en_sk.csv':"
    }
}

HIST_COLS = ["Dátum", "Diagnózy", "Cieľ", "Váha (kg)", "Energia", "Spánok", "Kalórie", "Sacharidy (g)", "Symptómy"]

# --- INTELIGENTNÉ NAČÍTANIE DATABÁZY POTRAVÍN ---
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, skiprows=3)
            df.columns = df.columns.str.strip()
            return df, True
        except Exception:
            pass

    file_name = "food_data_en_sk.csv"
    if os.path.exists(file_name):
        try:
            df = pd.read_csv(file_name, skiprows=3)
            df.columns = df.columns.str.strip()
            return df, True
        except Exception:
            pass
            
    mock_df = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'name_en': ['Oats', 'Spinach', 'Beef', 'Chocolate', 'Liver'],
        'name_sk': ['Ovsene vlocky', 'Spenat', 'Hovadzie maso', 'Cokolada', 'Pecen'],
        'Calories': [389, 23, 250, 546, 175],
        'Protein (g)': [16.9, 2.9, 26.0, 4.9, 27.0],
        'Fat (g)': [6.9, 0.4, 15.0, 31.0, 5.0],
        'Net-Carbs (g)': [66.3, 1.4, 0.0, 54.0, 4.0],
        'Sugars (g)': [0.0, 0.4, 0.0, 48.0, 0.0],
        'Fiber (g)': [10.6, 2.2, 0.0, 7.0, 0.0],
        'Iron, Fe (mg)': [4.7, 2.7, 2.6, 8.0, 18.0],
        'Zinc, Zn (mg)': [4.0, 0.5, 4.3, 2.3, 4.0]
    })
    return mock_df, False

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            return pd.read_csv(HISTORY_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=HIST_COLS)

def save_history_row(row_dict):
    history_df = load_history()
    new_row = pd.DataFrame([row_dict])
    history_df = pd.concat([history_df, new_row], ignore_index=True)
    try:
        history_df.to_csv(HISTORY_FILE, index=False)
    except Exception as e:
        st.error(f"{TXT[lang]['err_save']}: {e}")

# --- ROZHRANIE APPky ---
st.title(TXT[lang]["title"])
st.markdown("---")

# --- BOČNÝ PANEL ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100) # Decorative Icon
st.sidebar.markdown(f"### {TXT[lang]['profile']}")

with st.sidebar.expander("🧬 Zdravotné Kategórie", expanded=True):
    st.markdown(f"**{TXT[lang]['gain_weight_tendency']}**")
    has_pcos = st.checkbox(TXT[lang]["pcos"])
    has_hashi = st.checkbox(TXT[lang]["hashi"])
    has_db2 = st.checkbox(TXT[lang]["db2"])
    has_anemia = st.checkbox(TXT[lang]["anemia"])
    has_cushing = st.checkbox(TXT[lang]["cushing"])
    has_lipedema = st.checkbox(TXT[lang]["lepid"])

    st.markdown(f"**{TXT[lang]['lose_weight_tendency']}**")
    has_hyper = st.checkbox(TXT[lang]["hyper"])
    has_celiakia = st.checkbox(TXT[lang]["celiakia"])
    has_addison = st.checkbox(TXT[lang]["addison"])

    st.markdown(f"**{TXT[lang]['digestion']}**")
    has_hit = st.checkbox(TXT[lang]["hit"])
    has_gastritis = st.checkbox(TXT[lang]["gastritis"])
    has_sibo = st.checkbox(TXT[lang]["sibo"])
    has_gallbladder = st.checkbox(TXT[lang]["gallbladder"])

    st.markdown(f"**{TXT[lang]['metabolic_syndromes']}**")
    has_gout = st.checkbox(TXT[lang]["gout"])
    has_nafld = st.checkbox(TXT[lang]["nafld"])
    has_hypertension = st.checkbox(TXT[lang]["hypertension"])
    has_kidney_stones = st.checkbox(TXT[lang]["kidney_stones"])

with st.sidebar.expander(TXT[lang]["goal_hdr"], expanded=False):
    meta_goal = st.radio(TXT[lang]["goal_q"], TXT[lang]["goals"], label_visibility="collapsed")

with st.sidebar.expander(TXT[lang]["antropo"], expanded=False):
    weight = st.number_input(TXT[lang]["weight"], min_value=30.0, value=70.0, step=0.1)
    height = st.number_input(TXT[lang]["height"], min_value=120, value=165)
    age = st.number_input(TXT[lang]["age"], min_value=15, value=30)

bmr = round(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
base_maintenance = round(bmr * 1.2)

if has_cushing: base_maintenance = round(base_maintenance * 0.9)
if has_addison: base_maintenance = round(base_maintenance * 1.1)

if meta_goal in ["Zdravé chudnutie", "Healthy Weight Loss"]: target_cal = base_maintenance - 350
elif meta_goal in ["Zdravé pribratie (Budovanie hmoty)", "Healthy Weight Gain (Bulking)"]: target_cal = base_maintenance + 400
else: target_cal = base_maintenance

if has_gout or has_kidney_stones: target_protein = round(weight * 1.2)
elif has_hyper or meta_goal in ["Zdravé pribratie (Budovanie hmoty)", "Healthy Weight Gain (Bulking)"]: target_protein = round(weight * 1.8)
else: target_protein = round(weight * 1.5)

carbs_percentage = 0.25 if (has_pcos or has_db2 or has_nafld) else 0.45
target_carbs = round((target_cal * carbs_percentage) / 4)
target_fat = round((target_cal * (1.0 - (carbs_percentage + 0.25))) / 9)

st.sidebar.info(TXT[lang]["target_info"].format(cal=target_cal, prot=target_protein, carbs=target_carbs, fat=target_fat))

uploaded_file = None
if not os.path.exists("food_data_en_sk.csv"):
    st.sidebar.warning(TXT[lang]["db_status_upload"])
    uploaded_file = st.sidebar.file_uploader("", type=["csv"])
else:
    st.sidebar.caption(TXT[lang]["db_status_ok"])

df, is_real_db = load_data(uploaded_file)

# --- HLAVNÉ ROZHRANIE ---
tab1, tab2, tab3 = st.tabs(TXT[lang]["tabs"])

t_cal, t_carbs, t_prot, t_sugar, t_fiber, t_iron, t_zinc, t_risks = 0, 0, 0, 0, 0, 0, 0, 0

if 'daily_meals' not in st.session_state:
    st.session_state.daily_meals = []

with tab1:
    col_l, col_r = st.columns([2, 1], gap="large")
    
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
                
                cal = round(food_details.get('Calories', 0) * ratio, 1)
                prot = round(food_details.get('Protein (g)', 0) * ratio, 1)
                fat = round(food_details.get('Fat (g)', 0) * ratio, 1)
                carbs = round(food_details.get('Net-Carbs (g)', 0) * ratio, 1)
                sugar = round(food_details.get('Sugars (g)', 0) * ratio, 1)
                fiber = round(food_details.get('Fiber (g)', 0) * ratio, 1)
                iron = round(food_details.get('Iron, Fe (mg)', 0) * ratio, 2)
                zinc = round(food_details.get('Zinc, Zn (mg)', 0) * ratio, 2)
                
                full_name_lower = f"{food_details['name_en']} {food_details['name_sk']}".lower()
                warnings = []
                
                if has_celiakia or has_hashi:
                    if any(x in full_name_lower for x in ['wheat', 'barley', 'rye', 'flour', 'bread', 'gluten', 'psenica', 'jacmen', 'raz', 'muka', 'chlieb', 'lepok']): warnings.append(TXT[lang]["warn_gluten"])
                if has_hashi and any(x in full_name_lower for x in ['milk', 'cheese', 'yogurt', 'cream', 'soy', 'mlieko', 'syr', 'jogurt', 'smotana', 'soja']): warnings.append(TXT[lang]["warn_milk"])
                if has_hit and any(x in full_name_lower for x in ['tomato', 'spinach', 'avocado', 'eggplant', 'cheese', 'wine', 'vinegar', 'sauerkraut', 'fermented', 'shrimp', 'tuna', 'paradaj', 'spenat', 'avokado', 'baklazan', 'syr', 'vino', 'ocot', 'kapusta', 'ferment', 'krevet', 'tunia']): warnings.append(TXT[lang]["warn_hit"])
                if (has_gastritis or has_sibo) and any(x in full_name_lower for x in ['chili', 'pepper', 'coffee', 'lemon', 'onion', 'garlic', 'fried', 'korenie', 'kava', 'citron', 'cesnak', 'cibula', 'vypraz']): warnings.append(TXT[lang]["warn_gastritis"])
                if has_gout and any(x in full_name_lower for x in ['beef', 'pork', 'liver', 'beer', 'shrimp', 'sardine', 'hovadz', 'bravcov', 'pecen', 'pivo', 'krevet', 'sardyn']): warnings.append(TXT[lang]["warn_purines"])
                if has_kidney_stones and any(x in full_name_lower for x in ['spinach', 'rhubarb', 'chocolate', 'nuts', 'spenat', 'rebarbora', 'cokolada', 'orech']): warnings.append(TXT[lang]["warn_oxalates"])
                if (has_gallbladder or has_nafld) and (fat > 15 or 'fried' in full_name_lower or 'vypraz' in full_name_lower): warnings.append(TXT[lang]["warn_high_fat"])

                st.markdown(TXT[lang]["analysis"].format(g=grams))
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(TXT[lang]["cal"], f"{cal} kcal")
                c2.metric(TXT[lang]["prot"], f"{prot} g")
                c3.metric(TXT[lang]["carbs"], f"{carbs} g")
                c4.metric(TXT[lang]["fiber"], f"{fiber} g")
                
                st.write("") # Spacer
                if warnings:
                    st.markdown(TXT[lang]["warnings_hdr"])
                    for w in warnings: st.warning(w)
                
                if (has_pcos or has_db2 or has_nafld) and sugar > 10: st.error(TXT[lang]["warn_sugar"])

                if st.button(TXT[lang]["add_btn"], use_container_width=True):
                    st.session_state.daily_meals.append({
                        "Jedlo": selected_option, "Gramy": grams, "Kalórie": cal, 
                        "Bielkoviny": prot, "Tuky": fat, "Čisté Sacharidy": carbs, 
                        "Cukor": sugar, "Vláknina": fiber, "Železo": iron, "Zinok": zinc,
                        "Rizikové": 1 if warnings else 0
                    })
                    st.success(TXT[lang]["add_success"])
            else:
                st.info(TXT[lang]["not_found"])

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

with tab2:
    st.header(TXT[lang]["diary_hdr"])
    
    if st.session_state.daily_meals:
        df_today = pd.DataFrame(st.session_state.daily_meals)
        df_display = df_today.copy()
        
        if lang == "SK": df_display.columns = ["Jedlo", "Gramy", "Kalórie", "Bielkoviny", "Tuky", "Čisté Sacharidy", "Cukor", "Vláknina", "Železo", "Zinok", "Riziko"]
        else: df_display.columns = ["Food", "Grams", "Calories", "Protein", "Fat", "Net Carbs", "Sugar", "Fiber", "Iron", "Zinc", "Risk"]
            
        st.dataframe(df_display.iloc[:, :8], use_container_width=True)
        
        t_cal, t_carbs, t_prot, t_sugar = df_today["Kalórie"].sum(), df_today["Čisté Sacharidy"].sum(), df_today["Bielkoviny"].sum(), df_today["Cukor"].sum()
        t_fiber, t_iron, t_zinc, t_risks = df_today["Vláknina"].sum(), df_today["Železo"].sum(), df_today["Zinok"].sum(), df_today["Rizikové"].sum()
        
        st.markdown(TXT[lang]["status"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(TXT[lang]["cal"], f"{round(t_cal)} / {target_cal} kcal")
        c2.metric(TXT[lang]["prot"], f"{round(t_prot, 1)} / {target_protein} g")
        c3.metric(TXT[lang]["carbs"], f"{round(t_carbs, 1)} / {target_carbs} g")
        c4.metric(TXT[lang]["fiber"], f"{round(t_fiber, 1)} g")
        
        st.write("---")
        st.subheader(TXT[lang]["feedback_hdr"])
        
        feedbacks = []
        if has_pcos or has_db2:
            if t_fiber < 25: feedbacks.append(TXT[lang]["fb_pcos_fiber_low"])
            else: feedbacks.append(TXT[lang]["fb_pcos_fiber_ok"])
        if has_pcos or has_db2 or has_nafld:
            if t_sugar > 35: feedbacks.append(TXT[lang]["fb_pcos_sugar_high"])
        if has_anemia:
            if t_iron < 15: feedbacks.append(TXT[lang]["fb_anemia_iron_low"].format(iron=round(t_iron, 1)))
            else: feedbacks.append(TXT[lang]["fb_anemia_iron_ok"])
        if has_hashi:
            if t_zinc < 11: feedbacks.append(TXT[lang]["fb_hashi_zinc_low"].format(zinc=round(t_zinc, 1)))
            if t_risks > 0: feedbacks.append(TXT[lang]["fb_hashi_risks"].format(risks=t_risks))
        if has_celiakia and t_risks > 0: feedbacks.append(TXT[lang]["fb_celiakia_risk"])
        if has_gastritis and t_risks > 0: feedbacks.append(TXT[lang]["fb_gastritis_risk"])
        if has_gout and t_risks > 0: feedbacks.append(TXT[lang]["fb_gout_risk"])

        if not feedbacks: st.success(TXT[lang]["fb_perfect"])
        else:
            for f in feedbacks: st.info(f)
    else:
        st.info(TXT[lang]["no_meals"])

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

    st.write("") # Spacer
    if st.button(TXT[lang]["save_btn"], use_container_width=True):
        diag_list = []
        if has_pcos: diag_list.append("PCOS")
        if has_hashi: diag_list.append("Hashimoto")
        if has_anemia: diag_list.append("Anemia")
        if has_celiakia: diag_list.append("Celiakia")
        if has_gout: diag_list.append("Gout")
        if has_nafld: diag_list.append("NAFLD")
        
        row_data = {
            "Dátum": str(date.today()),
            "Diagnózy": ", ".join(diag_list) if diag_list else "Žiadne/None",
            "Cieľ": meta_goal,
            "Váha (kg)": weight,
            "Energia": energy_score,
            "Spánok": sleep_score,
            "Kalórie": round(t_cal, 1),
            "Sacharidy (g)": round(t_carbs, 1),
            "Symptómy": ", ".join(s_list) if s_list else "Žiadne/None"
        }
        save_history_row(row_data)
        st.session_state.daily_meals = []
        st.success(TXT[lang]["save_success"])
        st.rerun()

with tab3:
    st.header(TXT[lang]["history_hdr"])
    h_df = load_history()
    if not h_df.empty:
        st.dataframe(h_df, use_container_width=True)
        st.subheader(TXT[lang]["chart_title"])
        st.line_chart(h_df.set_index("Dátum")["Váha (kg)"])
    else:
        st.info(TXT[lang]["history_empty"])
