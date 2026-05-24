import streamlit as st
import pandas as pd
from datetime import date
import os

# --- NASTAVENIE STRÁNKY ---
st.set_page_config(page_title="Metabolický Asistent & Inteligentný Kouč", layout="wide")

HISTORY_FILE = "zdravotna_historia_global.csv"

# --- JAZYKOVÝ SLOVNÍK (TRANSLATIONS) ---
# Výber jazyka hneď na začiatku, aby bol prístupný pre celý zvyšok kódu
lang = st.sidebar.radio("🌐 Jazyk / Language", ["SK", "EN"])

TXT = {
    "SK": {
        "title": "🩺 Inteligentný Metabolický & Hormonálny Tracker",
        "profile": "🧬 Krok 1: Zdravotný profil",
        
        # Kategórie ochorení
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
        
        # Ciele a antropometria
        "goal_hdr": "🎯 Krok 2: Tvoj cieľ",
        "goal_q": "Čo chceš dosiahnuť?",
        "goals": ["Zdravé chudnutie", "Udržanie váhy & Regenerácia", "Zdravé pribratie (Budovanie hmoty)"],
        "antropo": "👤 Krok 3: Tvoje údaje",
        "weight": "Váha (kg):",
        "height": "Výška (cm):",
        "age": "Vek:",
        "target_info": "🎯 **Tvoj cieľový príjem:**\n* **Kalórie:** {cal} kcal\n* **Bielkoviny:** {prot} g\n* **Čisté sacharidy:** {carbs} g\n* **Tuky:** {fat} g",
        
        # Rozhranie tabov
        "tabs": ["🍽️ Potravinový asistent & Diagnostika", "📊 Dnešný denník & Inteligentný feedback", "📈 Dlhodobý vývoj"],
        "search_hdr": "🔍 Hľadať potravinu",
        "search_lbl": "Zadaj názov v slovenčine alebo angličtine (napr. hovädzie, beef, špenát):",
        "select_food": "Vyber potravinu:",
        "grams": "Gramáž (g):",
        "analysis": "#### 📊 Analýza pre {g}g:",
        "cal": "Kalórie",
        "prot": "Bielkoviny",
        "carbs": "Čisté Sacharidy",
        "fiber": "Vláknina",
        
        # Varovania
        "warnings_hdr": "### 🚨 Zdravotné upozornenia:",
        "warn_gluten": "🌾 **Obsahuje LEPKOVKU / GLUTEN:** Riziko zápalovej reakcie čreva.",
        "warn_milk": "🥛/🫛 **Mlieko/Sója:** Možný skrížený alergén pre štítnu žľazu.",
        "warn_hit": "⚠️ **Vysoký Histamín:** Sleduj reakciu tela.",
        "warn_gastritis": "🔥 **Žalúdočný iritant:** Môže dráždiť žalúdok.",
        "warn_sugar": "🚨 **Pozor na cukor:** Vysoká inzulínová špička.",
        "warn_purines": "🥩 **Vysoké puríny (Dna):** Riziko záchvatu dny a zvýšenia kyseliny močovej.",
        "warn_oxalates": "🌱 **Vysoké oxaláty:** Nebezpečenstvo vzniku obličkových kameňov.",
        "warn_high_fat": "🧈 **Vysoký obsah tuku:** Môže podráždiť žlčník alebo zhoršiť steatózu pečene.",
        
        # Tlačidlá
        "add_btn": "➕ Pridať do dňa",
        "add_success": "Pridané do dnešného prehľadu.",
        "not_found": "Slovo sa v databáze nenašlo.",
        
        # Encyklopédia
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
        "enc_nafld_b": "**Steatóza:** Minimalizuj priemyselné cukry (najmä glukózovo-fruktózový sirup) a trans-tuky.",
        
        # Denník a Feedback
        "diary_hdr": "📊 Tvoj dnešný denník",
        "status": "#### Aktuálny stav dňa:",
        "feedback_hdr": "💬 Personalizované spätné väzby a odporúčania",
        "fb_pcos_fiber_low": "🌾 **PCOS / Cukrovka:** Dnes máš **nízky príjem vlákniny** (menej ako 25g). Vláknina spomaľuje vstrebávanie sacharidov.",
        "fb_pcos_fiber_ok": "✨ **PCOS / Cukrovka:** Skvelé! Dosiahla si parádny príjem vlákniny.",
        "fb_pcos_sugar_high": "🚨 **PCOS / Cukrovka / Pečeň:** Pozor, celkový **cukor dnes prekročil bezpečnú hranicu** (nad 35g).",
        "fb_anemia_iron_low": "🩸 **Anémia:** Dnes si prijala len **{iron} mg železa**.",
        "fb_anemia_iron_ok": "💪 **Anémia:** Perfektné! Máš dnes bohatý príjem železa.",
        "fb_hashi_zinc_low": "🦋 **Hashimoto:** Tvoj **zinok je dnes nízky ({zinc} mg)**.",
        "fb_hashi_risks": "⚠️ **Hashimoto:** Zjedla si dnes {risks} potravín s potenciálnym autoimunitným spúšťačom.",
        "fb_celiakia_risk": "🚨 **Celiakia:** V denníku máš jedlo s obsahom lepku!",
        "fb_gastritis_risk": "🔥 **Gastritída:** Zaznamenala si potravinu, ktorá dráždi sliznicu žalústka.",
        "fb_gout_risk": "🦴 **Dna:** Pozor, jedlo s vysokým obsahom purínov môže vyvolať akútnu bolesť kĺbov.",
        "fb_perfect": "☀️ Tvoj dnešný jedálniček perfektne rešpektuje tvoj zdravotný stav.",
        "no_meals": "Zatiaľ si dnes nezadala žiadne potraviny.",
        
        # Symptómy
        "symptoms_hdr": "🩺 Sledovanie priebehu príznakov",
        "sym_gain_fatigue": "**Symptómy príberania / Únavy / Trávenia:**",
        "sym_hunger": "Náhly vlčí hlad (Inzulín)",
        "sym_weakness": "Extrémna svalová slabosť / Únava",
        "sym_bloating": "Nadúvanie / Plynatosť (SIBO/IBS)",
        "sym_lose_weight": "**Symptómy straty hmotnosti & Zápalov:**",
        "sym_palpitations": "Búšenie srdca / Triaška (Hyper)",
        "sym_cramps": "Kŕče v bruchu / Hnačka",
        "sym_gout_pain": "Bolesť a opuch kĺbov (Dna)",
        "sym_subjective": "**Subjektívne pocity:**",
        "sym_energy": "Energia počas dňa (1-10):",
        "sym_sleep": "Spánok (1-10):",
        "save_btn": "💾 Ukončiť a uložiť deň",
        "save_success": "Záznam uložený!",
        
        # História
        "history_hdr": "📈 Dlhodobé sledovanie vývoja tela",
        "history_empty": "Žiadne historické záznamy neboli zatiaľ vytvorené.",
        "chart_title": "Graf: Pohyb telesnej hmotnosti (kg)",
        "none": "Žiadne",
        "err_save": "Nepodarilo sa uložiť na server",
        "db_status_ok": "✅ Databáza úspešne spárovaná.",
        "db_status_upload": "📁 Databáza nenájdená. Nahraj 'food_data_en_sk.csv' tu:"
    },
    "EN": {
        "title": "🩺 Smart Metabolic & Hormonal Tracker",
        "profile": "🧬 Step 1: Health Profile",
        
        # Disease Categories
        "gain_weight_tendency": "📉 Weight Gain Tendency / Weight Loss Block:",
        "pcos": "PCOS (Insulin Resistance)",
        "hashi": "Hashimoto (Slow Metabolism)",
        "db2": "Type 2 Diabetes",
        "anemia": "Anemia (Iron Deficiency)",
        "cushing": "Cushing's Syndrome (High Cortisol)",
        "lepid": "Lipedema / Lymphedema",
        
        "lose_weight_tendency": "📈 Weight Loss Tendency / Problem Gaining:",
        "hyper": "Hyperthyroidism (Fast Metabolism)",
        "celiakia": "Celiac Disease / IBD (Malabsorption)",
        "addison": "Addison's Disease",
        
        "digestion": "🍽️ Digestive Sensitivities & Intolerances:",
        "hit": "HIT (Histamine Intolerance)",
        "gastritis": "Gastritis (Stomach Inflammation)",
        "sibo": "SIBO / IBS (Irritable Bowel)",
        "gallbladder": "Gallbladder Stones / Dysfunction",
        
        "metabolic_syndromes": "🧬 Metabolic & Organ Disorders:",
        "gout": "Gout (High Uric Acid)",
        "nafld": "Fatty Liver Disease (NAFLD)",
        "hypertension": "Hypertension (High Blood Pressure)",
        "kidney_stones": "Kidney Stones",
        
        # Goals and Anthropometrics
        "goal_hdr": "🎯 Step 2: Your Goal",
        "goal_q": "What do you want to achieve?",
        "goals": ["Healthy Weight Loss", "Weight Maintenance & Recovery", "Healthy Weight Gain (Bulking)"],
        "antropo": "👤 Step 3: Your Data",
        "weight": "Weight (kg):",
        "height": "Height (cm):",
        "age": "Age:",
        "target_info": "🎯 **Your Target Intake:**\n* **Calories:** {cal} kcal\n* **Protein:** {prot} g\n* **Net Carbs:** {carbs} g\n* **Fat:** {fat} g",
        
        # Tabs UI
        "tabs": ["🍽️ Food Assistant & Diagnostics", "📊 Daily Diary & Smart Feedback", "📈 Long-term Progress"],
        "search_hdr": "🔍 Search Food",
        "search_lbl": "Enter name in Slovak or English (e.g. hovävzie, beef, spinach):",
        "select_food": "Select food:",
        "grams": "Weight (g):",
        "analysis": "#### 📊 Analysis for {g}g:",
        "cal": "Calories",
        "prot": "Protein",
        "carbs": "Net Carbs",
        "fiber": "Fiber",
        
        # Warnings
        "warnings_hdr": "### 🚨 Health Warnings:",
        "warn_gluten": "🌾 **Contains GLUTEN:** Risk of inflammatory bowel reaction.",
        "warn_milk": "🥛/🫛 **Milk/Soy:** Possible cross-reactive allergen for the thyroid.",
        "warn_hit": "⚠️ **High Histamine:** Monitor your body's reaction.",
        "warn_gastritis": "🔥 **Stomach Irritant:** May irritate stomach lining.",
        "warn_sugar": "🚨 **Watch out for sugar:** High insulin spike.",
        "warn_purines": "🥩 **High Purines (Gout):** Risk of gout attack and high uric acid.",
        "warn_oxalates": "🌱 **High Oxalates:** Risk of kidney stone formation.",
        "warn_high_fat": "🧈 **High Fat Content:** May irritate gallbladder or worsen fatty liver.",
        
        # Buttons
        "add_btn": "➕ Add to Day",
        "add_success": "Added to today's overview.",
        "not_found": "Word not found in the database.",
        
        # Encyclopedia
        "encyclopedia": "### 💡 Metabolism Encyclopedia",
        "enc_pcos_t": "🌾 Insulin Block",
        "enc_pcos_b": "**PCOS & Type 2 Diabetes:** Fiber and low sugar are key to restoring insulin sensitivity.",
        "enc_hashi_t": "🦋 Slow Motor (Hashimoto)",
        "enc_hashi_b": "**Hypothyroidism:** Protein, zinc, and selenium protect muscles and stimulate metabolism.",
        "enc_hyper_t": "🔥 Overheated Motor (Hyperthyroidism)",
        "enc_hyper_b": "**Increased Function:** The body breaks down mass quickly. You need a healthy caloric surplus.",
        "enc_anemia_t": "🩸 Oxygen Debt (Anemia)",
        "enc_anemia_b": "**Missing Iron:** Without iron, cells lack oxygen and weight loss/recovery stalls.",
        "enc_gout_t": "🦴 Uric Acid (Gout)",
        "enc_gout_b": "**Gout:** Avoid red meat, organ meats, alcohol, and excessive high-fructose corn syrup.",
        "enc_nafld_t": "🍏 Fatty Liver (NAFLD)",
        "enc_nafld_b": "**Steatosis:** Minimize processed sugars (especially high-fructose corn syrup) and trans fats.",
        
        # Diary and Feedback
        "diary_hdr": "📊 Your Daily Diary",
        "status": "#### Current Daily Status:",
        "feedback_hdr": "💬 Personalized Feedback and Recommendations",
        "fb_pcos_fiber_low": "🌾 **PCOS / Diabetes:** Your **fiber intake is low** today (under 25g). Fiber slows carb absorption.",
        "fb_pcos_fiber_ok": "✨ **PCOS / Diabetes:** Great! You hit a solid fiber intake today.",
        "fb_pcos_sugar_high": "🚨 **PCOS / Diabetes / NAFLD:** Warning, your total **sugar exceeded the safe limit** today (above 35g).",
        "fb_anemia_iron_low": "🩸 **Anemia:** You only consumed **{iron} mg of iron** today.",
        "fb_anemia_iron_ok": "💪 **Anemia:** Perfect! You have a rich iron intake today.",
        "fb_hashi_zinc_low": "🦋 **Hashimoto:** Your **zinc is low today ({zinc} mg)**.",
        "fb_hashi_risks": "⚠️ **Hashimoto:** You ate {risks} foods today with a potential autoimmune trigger.",
        "fb_celiakia_risk": "🚨 **Celiac Disease:** There is gluten-containing food in your log!",
        "fb_gastritis_risk": "🔥 **Gastritis:** You logged a food that irritates the stomach lining.",
        "fb_gout_risk": "🦴 **Gout:** Watch out, foods high in purines can trigger acute joint pain.",
        "fb_perfect": "☀️ Your meal plan today perfectly respects your health condition.",
        "no_meals": "No foods logged yet today.",
        
        # Symptoms
        "symptoms_hdr": "🩺 Symptom Tracking",
        "sym_gain_fatigue": "**Weight Gain / Fatigue / Digestion Symptoms:**",
        "sym_hunger": "Sudden ravenous hunger (Insulin)",
        "sym_weakness": "Extreme muscle weakness / Fatigue",
        "sym_bloating": "Bloating / Gas (SIBO/IBS)",
        "sym_lose_weight": "**Weight Loss & Inflammation Symptoms:**",
        "sym_palpitations": "Heart palpitations / Internal tremors (Hyper)",
        "sym_cramps": "Abdominal cramps / Diarrhea",
        "sym_gout_pain": "Joint pain and swelling (Gout)",
        "sym_subjective": "**Subjective Feelings:**",
        "sym_energy": "Energy during the day (1-10):",
        "sym_sleep": "Sleep quality (1-10):",
        "save_btn": "💾 Finish and Save Day",
        "save_success": "Log saved!",
        
        # History
        "history_hdr": "📈 Long-term Body Progress Tracking",
        "history_empty": "No history logs created yet.",
        "chart_title": "Chart: Body Weight Progress (kg)",
        "none": "None",
        "err_save": "Failed to save to server",
        "db_status_ok": "✅ Food database linked.",
        "db_status_upload": "📁 Database not found. Upload 'food_data_en_sk.csv' here:"
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

# --- KONTROLA HISTÓRIE ---
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

# --- REORGANIZOVANÝ BOČNÝ PANEL (KROKY POD ŠÍPKAMI) ---
st.sidebar.write("---")

# KROK 1: Zdravotný profil
with st.sidebar.expander(TXT[lang]["profile"], expanded=True):
    st.markdown(f"<small>{TXT[lang]['gain_weight_tendency']}</small>", unsafe_allow_html=True)
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

# KROK 2: Tvoj cieľ
with st.sidebar.expander(TXT[lang]["goal_hdr"], expanded=False):
    meta_goal = st.radio(TXT[lang]["goal_q"], TXT[lang]["goals"], label_visibility="collapsed")

# KROK 3: Antropometrické údaje
with st.sidebar.expander(TXT[lang]["antropo"], expanded=False):
    weight = st.number_input(TXT[lang]["weight"], min_value=30.0, value=70.0, step=0.1)
    height = st.number_input(TXT[lang]["height"], min_value=120, value=165)
    age = st.number_input(TXT[lang]["age"], min_value=15, value=30)

# Výpočet metabolických cieľov
bmr = round(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
base_maintenance = round(bmr * 1.2)

if has_cushing: base_maintenance = round(base_maintenance * 0.9)
if has_addison: base_maintenance = round(base_maintenance * 1.1)

if meta_goal in ["Zdravé chudnutie", "Healthy Weight Loss"]:
    target_cal = base_maintenance - 350
elif meta_goal in ["Zdravé pribratie (Budovanie hmoty)", "Healthy Weight Gain (Bulking)"]:
    target_cal = base_maintenance + 400
else:
    target_cal = base_maintenance

if has_gout or has_kidney_stones:
    target_protein = round(weight * 1.2)
elif has_hyper or meta_goal in ["Zdravé pribratie (Budovanie hmoty)", "Healthy Weight Gain (Bulking)"]:
    target_protein = round(weight * 1.8)
else:
    target_protein = round(weight * 1.5)

carbs_percentage = 0.25 if (has_pcos or has_db2 or has_nafld) else 0.45
target_carbs = round((target_cal * carbs_percentage) / 4)
target_fat = round((target_cal * (1.0 - (carbs_percentage + 0.25))) / 9)

st.sidebar.info(TXT[lang]["target_info"].format(cal=target_cal, prot=target_protein, carbs=target_carbs, fat=target_fat))

# --- SPRÁVA DATABÁZY NA SPODKU BOČNÉHO PANELA ---
st.sidebar.write("---")
uploaded_file = None
if not os.path.exists("food_data_en_sk.csv"):
    st.sidebar.warning(TXT[lang]["db_status_upload"])
    uploaded_file = st.sidebar.file_uploader("", type=["csv"])
else:
    st.sidebar.caption(TXT[lang]["db_status_ok"])

df, is_real_db = load_data(uploaded_file)


# --- HLAVNÉ ROZHRANIE APPky ---
st.title(TXT[lang]["title"])

tab1, tab2, tab3 = st.tabs(TXT[lang]["tabs"])

t_cal, t_carbs, t_prot, t_sugar, t_fiber, t_iron, t_zinc, t_risks = 0, 0, 0, 0, 0, 0, 0, 0

if 'daily_meals' not in st.session_state:
    st.session_state.daily_meals = []

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
                    if any(x in full_name_lower for x in ['wheat', 'barley', 'rye', 'flour', 'bread', 'gluten', 'psenica', 'jacmen', 'raz', 'muka', 'chlieb', 'lepok']):
                        warnings.append(TXT[lang]["warn_gluten"])
                
                if has_hashi and any(x in full_name_lower for x in ['milk', 'cheese', 'yogurt', 'cream', 'soy', 'mlieko', 'syr', 'jogurt', 'smotana', 'soja']):
                    warnings.append(TXT[lang]["warn_milk"])

                if has_hit and any(x in full_name_lower for x in ['tomato', 'spinach', 'avocado', 'eggplant', 'cheese', 'wine', 'vinegar', 'sauerkraut', 'fermented', 'shrimp', 'tuna', 'paradaj', 'spenat', 'avokado', 'baklazan', 'syr', 'vino', 'ocot', 'kapusta', 'ferment', 'krevet', 'tunia']):
                    warnings.append(TXT[lang]["warn_hit"])
                
                if (has_gastritis or has_sibo) and any(x in full_name_lower for x in ['chili', 'pepper', 'coffee', 'lemon', 'onion', 'garlic', 'fried', 'korenie', 'kava', 'citron', 'cesnak', 'cibula', 'vypraz']):
                    warnings.append(TXT[lang]["warn_gastritis"])

                if has_gout and any(x in full_name_lower for x in ['beef', 'pork', 'liver', 'beer', 'shrimp', 'sardine', 'hovadz', 'bravcov', 'pecen', 'pivo', 'krevet', 'sardyn']):
                    warnings.append(TXT[lang]["warn_purines"])

                if has_kidney_stones and any(x in full_name_lower for x in ['spinach', 'rhubarb', 'chocolate', 'nuts', 'spenat', 'rebarbora', 'cokolada', 'orech']):
                    warnings.append(TXT[lang]["warn_oxalates"])

                if (has_gallbladder or has_nafld) and (fat > 15 or 'fried' in full_name_lower or 'vypraz' in full_name_lower):
                    warnings.append(TXT[lang]["warn_high_fat"])

                st.write(TXT[lang]["analysis"].format(g=grams))
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(TXT[lang]["cal"], f"{cal} kcal")
                c2.metric(TXT[lang]["prot"], f"{prot} g")
                c3.metric(TXT[lang]["carbs"], f"{carbs} g")
                c4.metric(TXT[lang]["fiber"], f"{fiber} g")
                
                if warnings:
                    st.markdown(TXT[lang]["warnings_hdr"])
                    for w in warnings:
                        st.warning(w)
                
                if (has_pcos or has_db2 or has_nafld) and sugar > 10:
                    st.error(TXT[lang]["warn_sugar"])

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
        
        if lang == "SK":
            df_display.columns = ["Jedlo", "Gramy", "Kalórie", "Bielkoviny", "Tuky", "Čisté Sacharidy", "Cukor", "Vláknina", "Železo", "Zinok", "Riziko"]
        else:
            df_display.columns = ["Food", "Grams", "Calories", "Protein", "Fat", "Net Carbs", "Sugar", "Fiber", "Iron", "Zinc", "Risk"]
            
        st.dataframe(df_display.iloc[:, :8])
        
        t_cal = df_today["Kalórie"].sum()
        t_carbs = df_today["Čisté Sacharidy"].sum()
        t_prot = df_today["Bielkoviny"].sum()
        t_sugar = df_today["Cukor"].sum()
        t_fiber = df_today["Vláknina"].sum()
        t_iron = df_today["Železo"].sum()
        t_zinc = df_today["Zinok"].sum()
        t_risks = df_today["Rizikové"].sum()
        
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

        if not feedbacks:
            st.success(TXT[lang]["fb_perfect"])
        else:
            for f in feedbacks: st.markdown(f)
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

    if st.button(TXT[lang]["save_btn"]):
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
        st.dataframe(h_df)
        st.subheader(TXT[lang]["chart_title"])
        st.line_chart(h_df.set_index("Dátum")["Váha (kg)"])
    else:
        st.info(TXT[lang]["history_empty"])
