import streamlit as st
import pandas as pd
from datetime import date
import os
from functools import lru_cache

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Metabolický Asistent & Inteligentný Kouč",
    layout="wide",
    page_icon="🩺",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM STYLING ====================
CUSTOM_CSS = """
<style>
    /* Primary color scheme */
    :root {
        --primary-color: #2ecc71;
        --primary-hover: #27ae60;
        --accent-color: #3498db;
        --danger-color: #e74c3c;
        --warning-color: #f39c12;
    }
    
    /* Smooth button styling */
    .stButton > button {
        border-radius: 8px;
        background-color: #2ecc71 !important;
        color: white !important;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(46, 204, 113, 0.2);
    }
    
    .stButton > button:hover {
        background-color: #27ae60 !important;
        box-shadow: 0 4px 16px rgba(46, 204, 113, 0.4);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Metric cards - theme adaptive */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.08) 0%, rgba(52, 152, 219, 0.03) 100%);
        border: 1px solid rgba(52, 152, 219, 0.2);
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        border-color: rgba(52, 152, 219, 0.4);
        box-shadow: 0 4px 16px rgba(52, 152, 219, 0.1);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #3498db !important;
        font-weight: 700;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(52, 152, 219, 0.1);
        border-top: 3px solid #3498db;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        border-radius: 8px;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 8px !important;
        border: 2px solid rgba(52, 152, 219, 0.2) !important;
        padding: 10px 12px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #3498db !important;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1) !important;
    }
    
    /* Alert styling */
    .stAlert {
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Dataframe styling */
    .streamlit-table {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0 !important;
        border-color: rgba(200, 200, 200, 0.2);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==================== TRANSLATIONS ====================
TRANSLATIONS = {
    "SK": {
        # Headers & titles
        "title": "🩺 Inteligentný Metabolický & Hormonálny Tracker",
        "profile": "🧬 Krok 1: Zdravotný profil",
        "goal_hdr": "🎯 Krok 2: Tvoj cieľ",
        "goal_q": "Čo chceš dosiahnuť?",
        "antropo": "👤 Krok 3: Tvoje údaje",
        
        # Health categories
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
        
        # Goals
        "goals": ["Zdravé chudnutie", "Udržanie váhy & Regenerácia", "Zdravé pribratie (Budovanie hmoty)"],
        
        # User inputs
        "weight": "Váha (kg):",
        "height": "Výška (cm):",
        "age": "Vek:",
        "target_info": "🎯 **Tvoj cieľový príjem:**\n* **Kalórie:** {cal} kcal\n* **Bielkoviny:** {prot} g\n* **Čisté sacharidy:** {carbs} g\n* **Tuky:** {fat} g\n* **Voda:** {water} L",
        
        # Tabs
        "tabs": ["🍽️ Potravinový asistent", "📊 Dnešný denník", "📈 Dlhodobý vývoj"],
        
        # Food search
        "search_hdr": "🔍 Hľadať potravinu",
        "search_lbl": "Zadaj názov v slovenčine alebo angličtine:",
        "select_food": "Vyber potravinu:",
        "grams": "Gramáž (g):",
        "analysis": "#### 📊 Analýza pre {g}g:",
        "cal": "Kalórie",
        "prot": "Bielkoviny",
        "carbs": "Sacharidy",
        "fiber": "Vláknina",
        
        # Warnings
        "warnings_hdr": "### 🚨 Zdravotné upozornenia:",
        "warn_gluten": "🌾 **Obsahuje LEPKOVKU:** Riziko zápalovej reakcie čreva.",
        "warn_milk": "🥛/🫛 **Mlieko/Sója:** Možný skrížený alergén pre štítnu žľazu.",
        "warn_hit": "⚠️ **Vysoký Histamín:** Sleduj reakciu tela.",
        "warn_gastritis": "🔥 **Žalúdočný iritant:** Môže dráždiť žalúdok.",
        "warn_sugar": "🚨 **Pozor na cukor:** Vysoká inzulínová špička.",
        "warn_purines": "🥩 **Vysoké puríny (Dna):** Riziko záchvatu dny a zvýšenia kyseliny močovej.",
        "warn_oxalates": "🌱 **Vysoké oxaláty:** Nebezpečenstvo vzniku obličkových kameňov.",
        "warn_high_fat": "🧈 **Vysoký obsah tuku:** Môže podráždiť žlčník alebo zhoršiť steatózu pečene.",
        
        # Actions
        "add_btn": "➕ Pridať do dňa",
        "add_success": "✅ Pridané do dnešného prehľadu.",
        "not_found": "❌ Slovo sa v databáze nenašlo.",
        
        # Encyclopedia
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
        
        # Diary
        "diary_hdr": "📊 Tvoj dnešný denník",
        "status": "#### 📈 Aktuálny stav dňa:",
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
        "fb_water_low": "💧 **Hydratácia:** Piješ príliš málo vody! Ciel je {target}L.",
        "fb_water_ok": "💧 **Hydratácia:** Výborná úroveň pitia vody!",
        "no_meals": "📭 Zatiaľ si nezadala žiadne potraviny.",
        
        # Water tracking
        "water_hdr": "💧 Sledovanie hydratácie",
        "water_intake": "Pohár vody (250ml):",
        "water_total": "Celkovo vody dnes:",
        
        # Symptoms
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
        
        # Save & history
        "save_btn": "💾 Ukončiť a uložiť deň",
        "save_success": "✅ Záznam uložený!",
        "history_hdr": "📈 Dlhodobé sledovanie vývoja tela",
        "history_empty": "📭 Žiadne historické záznamy neboli zatiaľ vytvorené.",
        "chart_title": "📊 Graf: Pohyb telesnej hmotnosti (kg)",
        
        # Metabolism status
        "metabolism_status": "### 🧬 Stav metabolizmu:",
        "metab_excellent": "✅ Vynikajúci! Tvoj metabolizmus je v poriadku.",
        "metab_good": "😊 Dobré! Dnes si robila dobré rozhodnutia.",
        "metab_warning": "⚠️ Pozor! Niektoré metriky si mimo cieľa.",
        "metab_critical": "🚨 KRITICKÉ! Potrebuješ urgentne zmeniť svoj príjem.",
        "metab_neutral": "😐 Neutrálny deň. Pokus sa zlepšiť.",
        
        # Database
        "none": "Žiadne",
        "err_save": "❌ Nepodarilo sa uložiť na server",
        "db_status_ok": "✅ Databáza úspešne spárovaná.",
        "db_status_upload": "📁 Databáza nenájdená. Nahraj 'food_data_en_sk.csv':"
    },
    "EN": {
        # Headers & titles
        "title": "🩺 Smart Metabolic & Hormonal Tracker",
        "profile": "🧬 Step 1: Health Profile",
        "goal_hdr": "🎯 Step 2: Your Goal",
        "goal_q": "What do you want to achieve?",
        "antropo": "👤 Step 3: Your Data",
        
        # Health categories
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
        
        # Goals
        "goals": ["Healthy Weight Loss", "Weight Maintenance & Recovery", "Healthy Weight Gain (Bulking)"],
        
        # User inputs
        "weight": "Weight (kg):",
        "height": "Height (cm):",
        "age": "Age:",
        "target_info": "🎯 **Your Target Intake:**\n* **Calories:** {cal} kcal\n* **Protein:** {prot} g\n* **Net Carbs:** {carbs} g\n* **Fat:** {fat} g\n* **Water:** {water} L",
        
        # Tabs
        "tabs": ["🍽️ Food Assistant", "📊 Daily Diary", "📈 Long-term Progress"],
        
        # Food search
        "search_hdr": "🔍 Search Food",
        "search_lbl": "Enter name in Slovak or English:",
        "select_food": "Select food:",
        "grams": "Weight (g):",
        "analysis": "#### 📊 Analysis for {g}g:",
        "cal": "Calories",
        "prot": "Protein",
        "carbs": "Net Carbs",
        "fiber": "Fiber",
        
        # Warnings
        "warnings_hdr": "### 🚨 Health Warnings:",
        "warn_gluten": "🌾 **Contains GLUTEN:** Risk of reaction.",
        "warn_milk": "🥛/🫛 **Milk/Soy:** Possible allergen.",
        "warn_hit": "⚠️ **High Histamine:** Monitor reaction.",
        "warn_gastritis": "🔥 **Stomach Irritant:** May irritate.",
        "warn_sugar": "🚨 **Watch out for sugar:** Insulin spike.",
        "warn_purines": "🥩 **High Purines (Gout):** Risk of attack.",
        "warn_oxalates": "🌱 **High Oxalates:** Risk of stones.",
        "warn_high_fat": "🧈 **High Fat:** May worsen gallbladder/NAFLD.",
        
        # Actions
        "add_btn": "➕ Add to Day",
        "add_success": "✅ Added to today's overview.",
        "not_found": "❌ Word not found in the database.",
        
        # Encyclopedia
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
        
        # Diary
        "diary_hdr": "📊 Your Daily Diary",
        "status": "#### 📈 Current Daily Status:",
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
        "fb_water_low": "💧 **Hydration:** You're drinking too little water! Target is {target}L.",
        "fb_water_ok": "💧 **Hydration:** Excellent water intake today!",
        "no_meals": "📭 No foods logged yet today.",
        
        # Water tracking
        "water_hdr": "💧 Hydration Tracking",
        "water_intake": "Glass of water (250ml):",
        "water_total": "Total water today:",
        
        # Symptoms
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
        
        # Save & history
        "save_btn": "💾 Finish and Save Day",
        "save_success": "✅ Log saved!",
        "history_hdr": "📈 Long-term Body Progress",
        "history_empty": "📭 No history logs created yet.",
        "chart_title": "📊 Chart: Body Weight Progress (kg)",
        
        # Metabolism status
        "metabolism_status": "### 🧬 Metabolism Status:",
        "metab_excellent": "✅ Excellent! Your metabolism is on track.",
        "metab_good": "😊 Good! You made great choices today.",
        "metab_warning": "⚠️ Caution! Some metrics are off target.",
        "metab_critical": "🚨 CRITICAL! You need to urgently change your intake.",
        "metab_neutral": "😐 Neutral day. Try to improve.",
        
        # Database
        "none": "None",
        "err_save": "❌ Failed to save to server",
        "db_status_ok": "✅ Food database linked.",
        "db_status_upload": "📁 Upload 'food_data_en_sk.csv':"
    }
}

# ==================== CONSTANTS ====================
HISTORY_FILE = "zdravotna_historia_global.csv"
HISTORY_COLUMNS = ["Dátum", "Diagnózy", "Cieľ", "Váha (kg)", "Energia", "Spánok", "Kalórie", "Sacharidy (g)", "Voda (L)", "Symptómy"]

# ==================== UTILITY FUNCTIONS ====================

def get_lang():
    """Get current language setting"""
    if "lang" not in st.session_state:
        st.session_state.lang = "SK"
    return st.session_state.lang

def txt(key: str):
    """Shorthand for getting translated text"""
    lang = get_lang()
    return TRANSLATIONS[lang].get(key, key)

def calculate_water_target(weight: float, has_hyper: bool = False, has_hypertension: bool = False) -> float:
    """Calculate daily water target (liters) based on weight and conditions"""
    base = weight * 0.033
    if has_hyper:
        base *= 1.2
    if has_hypertension:
        base *= 1.1
    return round(base, 1)

def get_metabolism_status(t_cal, target_cal, t_carbs, target_carbs, t_prot, target_protein,
                         t_fiber, has_pcos, has_hashi, t_iron, t_zinc, t_risks, t_water, target_water):
    """Calculate metabolism status and return emoji + message"""
    issues = 0
    max_issues = 6
    
    # Calorie check
    if target_cal > 0 and abs(t_cal - target_cal) / target_cal > 0.15:
        issues += 1
    
    # Fiber check for PCOS
    if has_pcos and t_fiber < 25:
        issues += 1
    
    # Protein check
    if target_protein > 0 and abs(t_prot - target_protein) / target_protein > 0.2:
        issues += 1
    
    # Zinc check for Hashimoto
    if has_hashi and t_zinc < 11:
        issues += 1
    
    # Water check
    if target_water > 0 and abs(t_water - target_water) / target_water > 0.2:
        issues += 1
    
    # Risks check
    if t_risks > 2:
        issues += 1
    
    # Determine status
    health_score = 1 - (issues / max_issues)
    
    if health_score >= 0.85:
        return "✅", txt("metab_excellent")
    elif health_score >= 0.70:
        return "😊", txt("metab_good")
    elif health_score >= 0.50:
        return "⚠️", txt("metab_warning")
    elif health_score >= 0.30:
        return "🚨", txt("metab_critical")
    else:
        return "😐", txt("metab_neutral")

# ==================== DATA LOADING ====================

@st.cache_data
def load_food_database(uploaded_file=None):
    """Load food database with caching"""
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, skiprows=3)
            df.columns = df.columns.str.strip()
            return df, True
        except Exception:
            pass
    
    if os.path.exists("food_data_en_sk.csv"):
        try:
            df = pd.read_csv("food_data_en_sk.csv", skiprows=3)
            df.columns = df.columns.str.strip()
            return df, True
        except Exception:
            pass
    
    # Mock data fallback
    return pd.DataFrame({
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
    }), False

def load_history():
    """Load historical data"""
    if os.path.exists(HISTORY_FILE):
        try:
            return pd.read_csv(HISTORY_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=HISTORY_COLUMNS)

def save_history_row(row_dict):
    """Save a row to history"""
    history_df = load_history()
    new_row = pd.DataFrame([row_dict])
    history_df = pd.concat([history_df, new_row], ignore_index=True)
    try:
        history_df.to_csv(HISTORY_FILE, index=False)
    except Exception as e:
        st.error(f"{txt('err_save')}: {e}")

# ==================== WARNING DETECTION ====================

def detect_food_warnings(food_name: str, health_conditions: dict) -> list:
    """Detect health warnings for a given food"""
    name_lower = food_name.lower()
    warnings = []
    
    gluten_keywords = ['wheat', 'barley', 'rye', 'flour', 'bread', 'gluten', 'psenica', 'jacmen', 'raz', 'muka', 'chlieb', 'lepok']
    dairy_keywords = ['milk', 'cheese', 'yogurt', 'cream', 'soy', 'mlieko', 'syr', 'jogurt', 'smotana', 'soja']
    histamine_keywords = ['tomato', 'spinach', 'avocado', 'eggplant', 'cheese', 'wine', 'vinegar', 'sauerkraut', 'fermented', 'shrimp', 'tuna', 'paradaj', 'spenat', 'sir', 'vino']
    gastritis_keywords = ['chili', 'pepper', 'coffee', 'lemon', 'onion', 'garlic', 'fried', 'korenie', 'kava', 'citron', 'cesnak', 'cibuľa', 'vypraz']
    purine_keywords = ['beef', 'pork', 'liver', 'beer', 'shrimp', 'sardine', 'hovadz', 'bravcov', 'pecen', 'pivo', 'krevet', 'sardyn']
    oxalate_keywords = ['spinach', 'rhubarb', 'chocolate', 'nuts', 'spenat', 'rebarbora', 'cokolada', 'orech']
    
    if (health_conditions.get('has_celiakia') or health_conditions.get('has_hashi')) and any(x in name_lower for x in gluten_keywords):
        warnings.append(txt("warn_gluten"))
    
    if health_conditions.get('has_hashi') and any(x in name_lower for x in dairy_keywords):
        warnings.append(txt("warn_milk"))
    
    if health_conditions.get('has_hit') and any(x in name_lower for x in histamine_keywords):
        warnings.append(txt("warn_hit"))
    
    if (health_conditions.get('has_gastritis') or health_conditions.get('has_sibo')) and any(x in name_lower for x in gastritis_keywords):
        warnings.append(txt("warn_gastritis"))
    
    if health_conditions.get('has_gout') and any(x in name_lower for x in purine_keywords):
        warnings.append(txt("warn_purines"))
    
    if health_conditions.get('has_kidney_stones') and any(x in name_lower for x in oxalate_keywords):
        warnings.append(txt("warn_oxalates"))
    
    return warnings

# ==================== MAIN APP ====================

# Language selector in sidebar
col1, col2 = st.columns([3, 1])
with col1:
    st.title(txt("title"))
with col2:
    new_lang = st.radio("🌐", ["SK", "EN"], horizontal=True, label_visibility="collapsed")
    st.session_state.lang = new_lang

st.divider()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100)
    st.markdown(f"### {txt('profile')}")
    
    # Health profile
    with st.expander("🧬 " + txt('profile'), expanded=True):
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
    
    # Goal
    with st.expander(txt("goal_hdr"), expanded=False):
        meta_goal = st.radio(txt("goal_q"), TRANSLATIONS[get_lang()]["goals"], label_visibility="collapsed")
    
    # User data
    with st.expander(txt("antropo"), expanded=False):
        weight = st.number_input(txt("weight"), min_value=30.0, value=70.0, step=0.1)
        height = st.number_input(txt("height"), min_value=120, value=165)
        age = st.number_input(txt("age"), min_value=15, value=30)
    
    # Calculate nutritional targets
    bmr = round(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
    base_maintenance = round(bmr * 1.2)
    
    if has_cushing:
        base_maintenance = round(base_maintenance * 0.9)
    if has_addison:
        base_maintenance = round(base_maintenance * 1.1)
    
    goal_low_carb = ["Zdravé chudnutie", "Healthy Weight Loss"]
    goal_bulk = ["Zdravé pribratie (Budovanie hmoty)", "Healthy Weight Gain (Bulking)"]
    
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
    
    carbs_percentage = 0.25 if (has_pcos or has_db2 or has_nafld) else 0.45
    target_carbs = round((target_cal * carbs_percentage) / 4)
    target_fat = round((target_cal * (1.0 - (carbs_percentage + 0.25))) / 9)
    target_water = calculate_water_target(weight, has_hyper, has_hypertension)
    
    st.info(txt("target_info").format(cal=target_cal, prot=target_protein, carbs=target_carbs, fat=target_fat, water=target_water))
    
    # Database status
    uploaded_file = None
    if not os.path.exists("food_data_en_sk.csv"):
        st.warning(txt("db_status_upload"))
        uploaded_file = st.file_uploader("", type=["csv"])
    else:
        st.caption(txt("db_status_ok"))
    
    df, is_real_db = load_food_database(uploaded_file)

# ==================== SESSION STATE ====================
if 'daily_meals' not in st.session_state:
    st.session_state.daily_meals = []

if 'water_glasses' not in st.session_state:
    st.session_state.water_glasses = 0

# Health conditions dict for warning detection
health_conditions = {
    'has_pcos': has_pcos, 'has_hashi': has_hashi, 'has_db2': has_db2,
    'has_anemia': has_anemia, 'has_celiakia': has_celiakia, 'has_hit': has_hit,
    'has_gastritis': has_gastritis, 'has_sibo': has_sibo, 'has_gout': has_gout,
    'has_kidney_stones': has_kidney_stones, 'has_gallbladder': has_gallbladder, 'has_nafld': has_nafld
}

# ==================== MAIN TABS ====================
tab1, tab2, tab3 = st.tabs(TRANSLATIONS[get_lang()]["tabs"])

# --- TAB 1: FOOD ASSISTANT ---
with tab1:
    col_l, col_r = st.columns([2, 1], gap="large")
    
    with col_l:
        st.subheader(txt("search_hdr"))
        search_query = st.text_input(txt("search_lbl"), "")
        
        if search_query:
            results = df[
                (df['name_en'].str.contains(search_query, case=False, na=False)) |
                (df['name_sk'].str.contains(search_query, case=False, na=False))
            ]
            
            if not results.empty:
                food_options = results.apply(lambda row: f"{row['name_en']} / {row['name_sk']}", axis=1).tolist()
                selected_option = st.selectbox(txt("select_food"), food_options)
                selected_idx = food_options.index(selected_option)
                food_details = results.iloc[selected_idx]
                
                grams = st.number_input(txt("grams"), min_value=1, value=100, step=10)
                ratio = grams / 100.0
                
                # Calculate macros
                cal = round(food_details.get('Calories', 0) * ratio, 1)
                prot = round(food_details.get('Protein (g)', 0) * ratio, 1)
                fat = round(food_details.get('Fat (g)', 0) * ratio, 1)
                carbs = round(food_details.get('Net-Carbs (g)', 0) * ratio, 1)
                sugar = round(food_details.get('Sugars (g)', 0) * ratio, 1)
                fiber = round(food_details.get('Fiber (g)', 0) * ratio, 1)
                iron = round(food_details.get('Iron, Fe (mg)', 0) * ratio, 2)
                zinc = round(food_details.get('Zinc, Zn (mg)', 0) * ratio, 2)
                
                # Display nutrition
                st.markdown(txt("analysis").format(g=grams))
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(txt("cal"), f"{cal} kcal")
                c2.metric(txt("prot"), f"{prot} g")
                c3.metric(txt("carbs"), f"{carbs} g")
                c4.metric(txt("fiber"), f"{fiber} g")
                
                st.write("")
                
                # Warnings
                full_name = f"{food_details['name_en']} {food_details['name_sk']}"
                warnings = detect_food_warnings(full_name, health_conditions)
                
                if warnings:
                    st.markdown(txt("warnings_hdr"))
                    for warning in warnings:
                        st.warning(warning)
                
                if (has_pcos or has_db2 or has_nafld) and sugar > 10:
                    st.error(txt("warn_sugar"))
                
                if st.button(txt("add_btn"), use_container_width=True):
                    st.session_state.daily_meals.append({
                        "Jedlo": selected_option, "Gramy": grams, "Kalórie": cal,
                        "Bielkoviny": prot, "Tuky": fat, "Čisté Sacharidy": carbs,
                        "Cukor": sugar, "Vláknina": fiber, "Železo": iron, "Zinok": zinc,
                        "Rizikové": 1 if warnings else 0
                    })
                    st.success(txt("add_success"))
            else:
                st.info(txt("not_found"))
    
    with col_r:
        st.markdown(txt("encyclopedia"))
        if has_pcos or has_db2:
            with st.expander(txt("enc_pcos_t")):
                st.write(txt("enc_pcos_b"))
        if has_hashi:
            with st.expander(txt("enc_hashi_t")):
                st.write(txt("enc_hashi_b"))
        if has_hyper:
            with st.expander(txt("enc_hyper_t")):
                st.write(txt("enc_hyper_b"))
        if has_anemia:
            with st.expander(txt("enc_anemia_t")):
                st.write(txt("enc_anemia_b"))
        if has_gout:
            with st.expander(txt("enc_gout_t")):
                st.write(txt("enc_gout_b"))
        if has_nafld:
            with st.expander(txt("enc_nafld_t")):
                st.write(txt("enc_nafld_b"))

# --- TAB 2: DAILY DIARY ---
with tab2:
    st.header(txt("diary_hdr"))
    
    if st.session_state.daily_meals:
        df_today = pd.DataFrame(st.session_state.daily_meals)
        df_display = df_today.copy()
        
        lang = get_lang()
        if lang == "SK":
            df_display.columns = ["Jedlo", "Gramy", "Kalórie", "Bielkoviny", "Tuky", "Čisté Sacharidy", "Cukor", "Vláknina", "Železo", "Zinok", "Riziko"]
        else:
            df_display.columns = ["Food", "Grams", "Calories", "Protein", "Fat", "Net Carbs", "Sugar", "Fiber", "Iron", "Zinc", "Risk"]
        
        st.dataframe(df_display.iloc[:, :8], use_container_width=True)
        
        # Calculate totals
        t_cal = df_today["Kalórie"].sum()
        t_carbs = df_today["Čisté Sacharidy"].sum()
        t_prot = df_today["Bielkoviny"].sum()
        t_sugar = df_today["Cukor"].sum()
        t_fiber = df_today["Vláknina"].sum()
        t_iron = df_today["Železo"].sum()
        t_zinc = df_today["Zinok"].sum()
        t_risks = df_today["Rizikové"].sum()
        
        # Status
        st.markdown(txt("status"))
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(txt("cal"), f"{round(t_cal)} / {target_cal} kcal")
        c2.metric(txt("prot"), f"{round(t_prot, 1)} / {target_protein} g")
        c3.metric(txt("carbs"), f"{round(t_carbs, 1)} / {target_carbs} g")
        c4.metric(txt("fiber"), f"{round(t_fiber, 1)} g")
        
        st.divider()
        st.subheader(txt("feedback_hdr"))
        
        # Generate feedback
        feedbacks = []
        if has_pcos or has_db2:
            if t_fiber < 25:
                feedbacks.append(txt("fb_pcos_fiber_low"))
            else:
                feedbacks.append(txt("fb_pcos_fiber_ok"))
        if (has_pcos or has_db2 or has_nafld) and t_sugar > 35:
            feedbacks.append(txt("fb_pcos_sugar_high"))
        if has_anemia:
            if t_iron < 15:
                feedbacks.append(txt("fb_anemia_iron_low").format(iron=round(t_iron, 1)))
            else:
                feedbacks.append(txt("fb_anemia_iron_ok"))
        if has_hashi:
            if t_zinc < 11:
                feedbacks.append(txt("fb_hashi_zinc_low").format(zinc=round(t_zinc, 1)))
            if t_risks > 0:
                feedbacks.append(txt("fb_hashi_risks").format(risks=int(t_risks)))
        if has_celiakia and t_risks > 0:
            feedbacks.append(txt("fb_celiakia_risk"))
        if has_gastritis and t_risks > 0:
            feedbacks.append(txt("fb_gastritis_risk"))
        if has_gout and t_risks > 0:
            feedbacks.append(txt("fb_gout_risk"))
        if st.session_state.water_glasses * 0.25 < target_water * 0.8:
            feedbacks.append(txt("fb_water_low").format(target=target_water))
        else:
            feedbacks.append(txt("fb_water_ok"))
        
        if not feedbacks:
            st.success(txt("fb_perfect"))
        else:
            for feedback in feedbacks:
                st.info(feedback)
    else:
        st.info(txt("no_meals"))
    
    st.divider()
    st.subheader(txt("water_hdr"))
    
    water_col1, water_col2, water_col3 = st.columns(3)
    with water_col1:
        if st.button(f"{txt('water_intake')} 💧", use_container_width=True):
            st.session_state.water_glasses += 1
    with water_col2:
        if st.button(f"➖ {txt('none')}", use_container_width=True):
            if st.session_state.water_glasses > 0:
                st.session_state.water_glasses -= 1
    with water_col3:
        if st.button(f"🔄 {txt('none')}", use_container_width=True):
            st.session_state.water_glasses = 0
    
    t_water = st.session_state.water_glasses * 0.25
    st.metric(txt("water_total"), f"{t_water} / {target_water} L", delta=f"{round(target_water - t_water, 2)} L")
    
    st.divider()
    st.subheader(txt("symptoms_hdr"))
    s_cols = st.columns(3)
    s_list = []
    
    with s_cols[0]:
        st.markdown(txt("sym_gain_fatigue"))
        if st.checkbox(txt("sym_hunger"), key="hunger"):
            s_list.append("Hunger")
        if st.checkbox(txt("sym_weakness"), key="weakness"):
            s_list.append("Weakness")
        if st.checkbox(txt("sym_bloating"), key="bloating"):
            s_list.append("Bloating")
    
    with s_cols[1]:
        st.markdown(txt("sym_lose_weight"))
        if st.checkbox(txt("sym_palpitations"), key="palpitations"):
            s_list.append("Palpitations")
        if st.checkbox(txt("sym_cramps"), key="cramps"):
            s_list.append("Cramps")
        if st.checkbox(txt("sym_gout_pain"), key="gout_pain"):
            s_list.append("Gout Pain")
    
    with s_cols[2]:
        st.markdown(txt("sym_subjective"))
        energy_score = st.slider(txt("sym_energy"), 1, 10, 7, key="energy")
        sleep_score = st.slider(txt("sym_sleep"), 1, 10, 7, key="sleep")
    
    st.write("")
    
    # Metabolism status
    status_emoji, status_msg = get_metabolism_status(
        t_cal if st.session_state.daily_meals else 0,
        target_cal, t_carbs if st.session_state.daily_meals else 0, target_carbs,
        t_prot if st.session_state.daily_meals else 0, target_protein,
        t_fiber if st.session_state.daily_meals else 0, has_pcos, has_hashi,
        t_iron if st.session_state.daily_meals else 0, t_zinc if st.session_state.daily_meals else 0,
        t_risks if st.session_state.daily_meals else 0, t_water, target_water
    )
    
    st.markdown(txt("metabolism_status"))
    st.markdown(f"### {status_emoji} {status_msg}")
    
    st.write("")
    if st.button(txt("save_btn"), use_container_width=True, type="primary"):
        diag_list = []
        if has_pcos:
            diag_list.append("PCOS")
        if has_hashi:
            diag_list.append("Hashimoto")
        if has_anemia:
            diag_list.append("Anemia")
        if has_celiakia:
            diag_list.append("Celiac")
        if has_gout:
            diag_list.append("Gout")
        if has_nafld:
            diag_list.append("NAFLD")
        
        row_data = {
            "Dátum": str(date.today()),
            "Diagnózy": ", ".join(diag_list) if diag_list else "None",
            "Cieľ": meta_goal,
            "Váha (kg)": weight,
            "Energia": energy_score,
            "Spánok": sleep_score,
            "Kalórie": round(t_cal, 1) if st.session_state.daily_meals else 0,
            "Sacharidy (g)": round(t_carbs, 1) if st.session_state.daily_meals else 0,
            "Voda (L)": t_water,
            "Symptómy": ", ".join(s_list) if s_list else "None"
        }
        save_history_row(row_data)
        st.session_state.daily_meals = []
        st.session_state.water_glasses = 0
        st.success(txt("save_success"))
        st.rerun()

# --- TAB 3: LONG-TERM PROGRESS ---
with tab3:
    st.header(txt("history_hdr"))
    h_df = load_history()
    
    if not h_df.empty:
        st.dataframe(h_df, use_container_width=True)
        st.subheader(txt("chart_title"))
        st.line_chart(h_df.set_index("Dátum")["Váha (kg)"])
    else:
        st.info(txt("history_empty"))
