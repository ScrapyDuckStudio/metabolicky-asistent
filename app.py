import streamlit as st
import pandas as pd
from datetime import date
import os
from functools import lru_cache
from fpdf import FPDF

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Metabolický Asistent & Inteligentný Kouč",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM PREMIUM STYLING ====================
CUSTOM_CSS = """
<style>
    /* Google Fonts Import for clean aesthetics */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: #fcfdfd;
    }
    
    /* Global design tokens for Health & Balance Theme */
    :root {
        --primary-health: #059669; /* Emerald Green */
        --primary-glow: #10b981;
        --accent-balance: #0d9488; /* Calm Teal */
        --energy-orange: #f59e0b; /* Warm Amber */
        --alert-coral: #f43f5e; /* Soft Coral Red */
        --bg-gradient: linear-gradient(135deg, #f0fdf4 0%, #f0fdfa 100%);
    }

    /* Elegant sidebar custom styling */
    [data-testid="stSidebar"] {
        background-color: #f7faf9;
        border-right: 1px solid rgba(5, 150, 105, 0.08);
    }
    
    /* Styled headings with gradient accents */
    h1, h2, h3 {
        color: #0f2d24 !important;
        font-weight: 700 !important;
    }
    
    /* Smooth buttons with fluid energy gradient */
    .stButton > button {
        border-radius: 14px !important;
        background: linear-gradient(135deg, #059669 0%, #0d9488 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 26px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(13, 148, 136, 0.18) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0d9488 0%, #059669 100%) !important;
        box-shadow: 0 6px 20px rgba(5, 150, 105, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Premium health metrics styling */
    div[data-testid="metric-container"] {
        background: var(--bg-gradient);
        border: 1px solid rgba(13, 148, 136, 0.12) !important;
        padding: 22px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(13, 148, 136, 0.03) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="metric-container"]:hover {
        border-color: rgba(5, 150, 105, 0.3) !important;
        box-shadow: 0 12px 28px rgba(5, 150, 105, 0.08) !important;
        transform: translateY(-3px);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        color: #0d9488 !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    [data-testid="stMetricLabel"] {
        color: #3f6257 !important;
        font-weight: 600 !important;
    }
    
    /* Elevated and sleek custom tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: 2px solid rgba(5, 150, 105, 0.08);
        padding-bottom: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 52px;
        border-radius: 12px 12px 0px 0px;
        padding: 12px 24px;
        font-weight: 600;
        color: #627d74;
        transition: all 0.25s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(13, 148, 136, 0.07) !important;
        color: #0d9488 !important;
        border-top: 3px solid #0d9488 !important;
        border-radius: 12px 12px 0px 0px;
    }
    
    /* Input fields luxury borders and soft focus effects */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 2px solid rgba(13, 148, 136, 0.12) !important;
        padding: 11px 14px !important;
        background-color: #ffffff !important;
        transition: all 0.25s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #0d9488 !important;
        box-shadow: 0 0 0 4px rgba(13, 148, 136, 0.08) !important;
    }
    
    /* Alert cards custom visual styling */
    .stAlert {
        border-radius: 16px !important;
        border: 1px solid rgba(13, 148, 136, 0.08) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.01) !important;
    }
    
    .stAlert [data-testid="stNotificationContent"] {
        color: #1e3d33 !important;
    }

    /* Expander styling for clean layouts */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border: 1px solid rgba(5, 150, 105, 0.06) !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        color: #0f2d24 !important;
    }

    /* Elegant custom card backgrounds */
    .health-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 24px;
        border: 1px solid rgba(13, 148, 136, 0.08);
        box-shadow: 0 8px 24px rgba(13, 148, 136, 0.02);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==================== TRANSLATIONS ====================
TRANSLATIONS = {
    "SK": {
        # Headers & titles
        "title": "🌿 Inteligentný Metabolický & Hormonálny Tracker",
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
        "metabolic_syndromes": "🧬 Metabolické, Orgánové & Hormonálne poruchy:",
        "gout": "Dna (Vysoká kyselina močová)",
        "nafld": "Steatóza pečene (NAFLD)",
        "hypertension": "Hypertenzia (Vysoký tlak)",
        "kidney_stones": "Obličkové kamene",
        "adrenal_fatigue": "Adrenálna únava (Chronický stres)",
        "leaky_gut": "Leaky Gut (Priepustné črevo)",
        "candida": "Premnožená Candida (Mykózy)",
        "menopause": "Perimenopauza / Menopauza",
        "osteo": "Osteoporóza / Osteopénia",
        
        # Goals
        "goals": ["Zdravé chudnutie", "Udržanie váhy & Regenerácia", "Zdravé pribratie (Budovanie hmoty)"],
        
        # User inputs
        "weight": "Váha (kg):",
        "height": "Výška (cm):",
        "age": "Vek:",
        "target_info": "🎯 **Tvoj cieľový príjem:**\n* **Kalórie:** {cal} kcal\n* **Bielkoviny:** {prot} g\n* **Čisté sacharidy:** {carbs} g\n* **Tuky:** {fat} g\n* **Voda:** {water} L",
        
        # Tabs
        "tabs": ["🍽️ Potravinový asistent", "📊 Dnešný denník", "📈 Dlhodobý vývoj", "🛒 Nákupný košík"],
        
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
        "warn_candida": "🍄 **Candida:** Vysoký obsah jednoduchých cukrov podporuje kvasinky.",
        "warn_leaky_gut": "🛡️ **Leaky Gut:** Pozor na dráždivé bielkoviny (lepok/mlieko).",
        "warn_osteo": "🦴 **Osteoporóza:** Kofeín a fosfáty môžu zhoršovať vstrebávanie vápnika.",
        
        # Actions
        "add_btn": "➕ Pridať do dňa",
        "add_success": "✅ Pridané do dnešného prehľadu.",
        "not_found": "❌ Slovo sa v databáze nenašlo.",
        
        # Encyclopedia
        "encyclopedia": "### 💡 Encyklopédia metabolizmu",
        "enc_pcos_t": "🌾 Inzulínový blok",
        "enc_pcos_b": "**PCOS & Cukrovka 2. typu:** Vláknina a nízky cukor sú kľúč k obnove inzulínovej citlivosti.",
        "enc_hashi_t": "🦋 Spomalený motor (Hashimoto)",
        "enc_hashi_b": "**Hypotyreóza:** Bielkoviny, zinok a selén chránia svaly a stimulujú metabolizmus.",
        "enc_hyper_t": "🔥 Prehriaty motor (Hypertyreóza)",
        "enc_hyper_b": "**Zvýšená funkcia:** Telo rýchlo odbúrava hmotu. Potrebuješ zdravý kalorický prebytok.",
        "enc_anemia_t": "🩸 Kyslíkový dlh (Anémia)",
        "enc_anemia_b": "**Chýbajúce železo:** Bez dostatočného množstva železa bunky nemajú dostatok kyslíka.",
        "enc_gout_t": "🦴 Kyselina močová (Dna)",
        "enc_gout_b": "**Dna:** Vyhýbaj sa červenému mäsu, vnútornostiam, alkoholu a nadmernej fruktóze.",
        "enc_nafld_t": "🍏 Tuk v pečeni (NAFLD)",
        "enc_nafld_b": "**Steatóza:** Minimalizuj priemyselné cukry, fruktózový sirup a trans-tuky.",
        
        # Diary
        "diary_hdr": "📊 Tvoj dnešný denník",
        "status": "#### 📈 Aktuálny stav dňa:",
        "feedback_hdr": "💬 Personalizované spätné väzby",
        "fb_pcos_fiber_low": "🌾 **PCOS/Cukrovka:** Dnes máš nízky príjem vlákniny (menej ako 25g).",
        "fb_pcos_fiber_ok": "✨ **PCOS/Cukrovka:** Skvelé! Dosiahol/dosiahla si parádny príjem vlákniny.",
        "fb_pcos_sugar_high": "🚨 **PCOS/Pečeň:** Pozor, cukor prekročil bezpečnú hranicu (nad 35g).",
        "fb_anemia_iron_low": "🩸 **Anémia:** Dnes si prijal/prijala len {iron} mg železa.",
        "fb_anemia_iron_ok": "💪 **Anémia:** Perfektné! Máš bohatý príjem železa.",
        "fb_hashi_zinc_low": "🦋 **Hashimoto:** Tvoj zinok je dnes nízky ({zinc} mg). Pre optimálnu syntézu hormónov štítnej žľazy by si mal/mala prijať **11 až 15 mg zinku denne**.",
        "fb_hashi_zinc_ok": "✨ **Hashimoto:** Skvelé, tvoj príjem zinku je dostatočný pre tvoj metabolizmus.",
        "fb_hashi_risks": "⚠️ **Hashimoto:** Zjedol/zjedla si dnes {risks} potravín so spúšťačom.",
        "fb_celiakia_risk": "🚨 **Celiakia:** V denníku máš jedlo s obsahom lepku!",
        "fb_gastritis_risk": "🔥 **Gastritída:** Zaznamenal/zaznamenala si potravinu dráždiacu žalúdok.",
        "fb_gout_risk": "🦴 **Dna:** Pozor, jedlo s purínmi môže vyvolať záchvat.",
        "fb_perfect": "☀️ Tvoj dnešný jedálniček perfektne rešpektuje tvoj zdravotný stav.",
        "fb_water_low": "💧 **Hydratácia:** Piješ príliš málo vody! Cieľ je {target}L.",
        "fb_water_high": "⚠️ **Nadmerná hydratácia:** Piješ príliš veľa vody! (Dnes už {water}L). Nadmerný jednorazový alebo celkový príjem vody (nad {limit}L denne) môže preťažiť obličky a spôsobiť nebezpečné vyplavenie sodíka a dôležitých minerálov (hyponatriémia).",
        "fb_water_ok": "💧 **Hydratácia:** Výborná úroveň pitia vody!",
        "no_meals": "📭 Zatiaľ si nezadal/nezadala žiadne potraviny.",
        
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
        "save_success": "✅ Záznam úspešne uložený!",
        "history_hdr": "📈 Dlhodobé sledovanie vývoja tela",
        "history_empty": "📭 Žiadne historické záznamy neboli zatiaľ vytvorené.",
        "chart_title": "📊 Graf: Pohyb telesnej hmotnosti (kg)",
        
        # Metabolism status
        "metabolism_status": "### 🧬 Stav metabolizmu:",
        "metab_excellent": "✅ Vynikajúci! Tvoj metabolizmus je v poriadku.",
        "metab_good": "😊 Dobré! Dnes si robil/robila výborné rozhodnutia.",
        "metab_warning": "⚠️ Pozor! Niektoré nutričné metriky si minul/minula.",
        "metab_critical": "🚨 KRITICKÉ! Potrebuješ urgentne zmeniť svoj príjem.",
        "metab_neutral": "😐 Neutrálny deň. Skús sa zajtra zlepšiť.",
        
        # Database
        "none": "Žiadne",
        "err_save": "❌ Nepodarilo sa uložiť na server",
        "db_status_ok": "✅ Databáza úspešne spárovaná.",
        "db_status_upload": "📁 Databáza nenájdená. Nahraj 'food_data_en_sk.csv':"
    },
    "EN": {
        # Headers & titles
        "title": "🌿 Smart Metabolic & Hormonal Tracker",
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
        "metabolic_syndromes": "🧬 Metabolic, Organ & Hormonal Disorders:",
        "gout": "Gout (High Uric Acid)",
        "nafld": "Fatty Liver (NAFLD)",
        "hypertension": "Hypertension",
        "kidney_stones": "Kidney Stones",
        "adrenal_fatigue": "Adrenal Fatigue (Chronic Stress)",
        "leaky_gut": "Leaky Gut Syndrome",
        "candida": "Candida Overgrowth",
        "menopause": "Perimenopause / Menopause",
        "osteo": "Osteoporosis / Osteopenia",
        
        # Goals
        "goals": ["Healthy Weight Loss", "Weight Maintenance & Recovery", "Healthy Weight Gain (Bulking)"],
        
        # User inputs
        "weight": "Weight (kg):",
        "height": "Height (cm):",
        "age": "Age:",
        "target_info": "🎯 **Your Target Intake:**\n* **Calories:** {cal} kcal\n* **Protein:** {prot} g\n* **Net Carbs:** {carbs} g\n* **Fat:** {fat} g\n* **Water:** {water} L",
        
        # Tabs
        "tabs": ["🍽️ Food Assistant", "📊 Daily Diary", "📈 Long-term Progress", "🛒 Shopping Cart"],
        
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
        "warn_candida": "🍄 **Candida:** High simple sugars feed yeast.",
        "warn_leaky_gut": "🛡️ **Leaky Gut:** Beware of irritating proteins (gluten/dairy).",
        "warn_osteo": "🦴 **Osteoporosis:** Caffeine and phosphates can impair calcium absorption.",
        
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
        "fb_hashi_zinc_low": "🦋 **Hashimoto:** Your zinc is low ({zinc} mg). For optimal thyroid hormone synthesis, aim for **11 to 15 mg of zinc daily**.",
        "fb_hashi_zinc_ok": "✨ **Hashimoto:** Great! Zinc levels are ideal for your metabolism.",
        "fb_hashi_risks": "⚠️ **Hashimoto:** You ate {risks} foods with triggers.",
        "fb_celiakia_risk": "🚨 **Celiac:** Gluten-containing food logged!",
        "fb_gastritis_risk": "🔥 **Gastritis:** Stomach irritant logged.",
        "fb_gout_risk": "🦴 **Gout:** Purines can trigger joint pain.",
        "fb_perfect": "☀️ Your meal plan perfectly respects your health.",
        "fb_water_low": "💧 **Hydration:** You're drinking too little water! Target is {target}L.",
        "fb_water_high": "⚠️ **Overhydration Warning:** You are drinking too much water! (Currently {water}L). Consuming too much water (over {limit}L per day) can strain your kidneys and lead to electrolyte loss (hyponatremia).",
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
    
    # Mock data fallback with richer vitamin profiles
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
    
    candida_keywords = ['sugar', 'cukor', 'fruit', 'ovocie', 'honey', 'med', 'sirup', 'syrup', 'chocolate', 'cokolada']
    osteo_keywords = ['caffeine', 'coffee', 'kava', 'soda', 'cola', 'energy', 'limonada']
    
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
        
    if health_conditions.get('has_candida') and any(x in name_lower for x in candida_keywords):
        warnings.append(txt("warn_candida"))
        
    if health_conditions.get('has_leaky_gut') and any(x in name_lower for x in gluten_keywords + dairy_keywords):
        warnings.append(txt("warn_leaky_gut"))
        
    if health_conditions.get('has_osteo') and any(x in name_lower for x in osteo_keywords):
        warnings.append(txt("warn_osteo"))
    
    return warnings

# ==================== MAIN APP ====================
# Language selector in sidebar
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"<h1 style='color: #0d9488; margin-bottom: 0px;'>{txt('title')}</h1>", unsafe_allow_html=True)
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
        has_adrenal = st.checkbox(txt("adrenal_fatigue"), key="adrenal")
        has_leaky_gut = st.checkbox(txt("leaky_gut"), key="leaky_gut")
        has_candida = st.checkbox(txt("candida"), key="candida")
        has_menopause = st.checkbox(txt("menopause"), key="menopause")
        has_osteo = st.checkbox(txt("osteo"), key="osteo")
    
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
    
    carbs_percentage = 0.25 if (has_pcos or has_db2 or has_nafld or has_candida) else 0.45
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
    'has_kidney_stones': has_kidney_stones, 'has_gallbladder': has_gallbladder, 'has_nafld': has_nafld,
    'has_adrenal': has_adrenal, 'has_leaky_gut': has_leaky_gut, 'has_candida': has_candida,
    'has_menopause': has_menopause, 'has_osteo': has_osteo
}

# ==================== MAIN TABS ====================
tab1, tab2, tab3, tab4 = st.tabs(TRANSLATIONS[get_lang()]["tabs"])

# --- TAB 1: FOOD ASSISTANT ---
with tab1:
    col_l, col_r = st.columns([2, 1], gap="large")
    
    with col_l:
        st.markdown(f"<h3 style='color: #059669;'>{txt('search_hdr')}</h3>", unsafe_allow_html=True)
        search_query = st.text_input(txt("search_lbl"), "", placeholder="Napr. Ovsene vlocky / Oats...")
        
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
                
                if (has_pcos or has_db2 or has_nafld or has_candida) and sugar > 10:
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
        st.markdown(f"<div class='health-card'><h4>{txt('encyclopedia')}</h4>", unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: DAILY DIARY ---
with tab2:
    st.markdown(f"<h3 style='color: #059669;'>{txt('diary_hdr')}</h3>", unsafe_allow_html=True)

    # DAILY MEALS TABLE
    has_meals = bool(st.session_state.daily_meals)
    if has_meals:
        df_today = pd.DataFrame(st.session_state.daily_meals)
        st.dataframe(df_today, use_container_width=True, hide_index=True)

        totals = {
            "calories": round(df_today["Kalórie"].sum(), 1),
            "carbs": round(df_today["Čisté Sacharidy"].sum(), 1),
            "protein": round(df_today["Bielkoviny"].sum(), 1),
            "fiber": round(df_today["Vláknina"].sum(), 1),
            "sugar": round(df_today["Cukor"].sum(), 1),
            "iron": round(df_today["Železo"].sum(), 1),
            "zinc": round(df_today["Zinok"].sum(), 1),
            "risks": round(df_today["Rizikové"].sum(), 1)
        }
    else:
        st.info(txt("no_meals"))
        totals = {"calories": 0, "carbs": 0, "protein": 0, "fiber": 0, "sugar": 0, "iron": 0, "zinc": 0, "risks": 0}

    # METRICS DISPLAY
    st.markdown(txt("status"))
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(txt("cal"), f"{totals['calories']} / {target_cal} kcal")
    m2.metric(txt("prot"), f"{totals['protein']} / {target_protein} g")
    m3.metric(txt("carbs"), f"{totals['carbs']} / {target_carbs} g")
    m4.metric(txt("fiber"), f"{totals['fiber']} g")

    st.divider()

    # WATER TRACKER WITH SAFETY CHECKS
    st.markdown(f"<h4 style='color: #0d9488;'>{txt('water_hdr')}</h4>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(f"{txt('water_intake')} 💧", use_container_width=True):
            st.session_state.water_glasses += 1
    with c2:
        if st.button("➖", use_container_width=True):
            st.session_state.water_glasses = max(0, st.session_state.water_glasses - 1)
    with c3:
        if st.button("🔄", use_container_width=True):
            st.session_state.water_glasses = 0

    water_total = round(st.session_state.water_glasses * 0.25, 2)
    st.metric(txt("water_total"), f"{water_total} / {target_water} L")

    st.divider()

    # PERSONALIZED CLINICAL FEEDBACK
    st.markdown(f"<h4>{txt('feedback_hdr')}</h4>", unsafe_allow_html=True)
    feedbacks = []

    if has_pcos or has_db2:
        if totals["fiber"] < 25:
            feedbacks.append(txt("fb_pcos_fiber_low"))
        else:
            feedbacks.append(txt("fb_pcos_fiber_ok"))

    if (has_pcos or has_db2 or has_nafld or has_candida) and totals["sugar"] > 35:
        feedbacks.append(txt("fb_pcos_sugar_high"))

    if has_anemia:
        if totals["iron"] < 15:
            feedbacks.append(txt("fb_anemia_iron_low").format(iron=totals["iron"]))
        else:
            feedbacks.append(txt("fb_anemia_iron_ok"))

    if has_hashi:
        if totals["zinc"] < 11:
            feedbacks.append(txt("fb_hashi_zinc_low").format(zinc=totals["zinc"]))
        else:
            feedbacks.append(txt("fb_hashi_zinc_ok"))

    if has_gout and totals["risks"] > 0:
        feedbacks.append(txt("fb_gout_risk"))

    # Water overhydration / underhydration dynamic checks
    water_upper_limit = round(max(4.5, target_water + 1.5), 1)
    if water_total < target_water * 0.8:
        feedbacks.append(txt("fb_water_low").format(target=target_water))
    elif water_total > water_upper_limit:
        feedbacks.append(txt("fb_water_high").format(water=water_total, limit=water_upper_limit))
    else:
        feedbacks.append(txt("fb_water_ok"))

    if not feedbacks:
        feedbacks.append(txt("fb_perfect"))

    # Render feedbacks dynamically inside beautiful styled containers
    for fb in feedbacks:
        if "⚠️" in fb or "🚨" in fb:
            st.warning(fb)
        elif "✨" in fb or "☀️" in fb or "💪" in fb:
            st.success(fb)
        else:
            st.info(fb)

    st.divider()

    # SYMPTOM TRACKING BLOCK
    st.markdown(f"<h4>{txt('symptoms_hdr')}</h4>", unsafe_allow_html=True)
    sym_cols = st.columns(3)
    selected_symptoms = []

    with sym_cols[0]:
        st.markdown(txt("sym_gain_fatigue"))
        if st.checkbox(txt("sym_hunger"), key="hunger"): selected_symptoms.append("Hunger")
        if st.checkbox(txt("sym_weakness"), key="weakness"): selected_symptoms.append("Weakness")
        if st.checkbox(txt("sym_bloating"), key="bloating"): selected_symptoms.append("Bloating")

    with sym_cols[1]:
        st.markdown(txt("sym_lose_weight"))
        if st.checkbox(txt("sym_palpitations"), key="palpitations"): selected_symptoms.append("Palpitations")
        if st.checkbox(txt("sym_cramps"), key="cramps"): selected_symptoms.append("Cramps")
        if st.checkbox(txt("sym_gout_pain"), key="gout_pain"): selected_symptoms.append("Gout Pain")

    with sym_cols[2]:
        st.markdown(txt("sym_subjective"))
        energy_score = st.slider(txt("sym_energy"), 1, 10, 7, key="energy")
        sleep_score = st.slider(txt("sym_sleep"), 1, 10, 7, key="sleep")

    # SAVE AND RERUN ACTION
    if st.button(txt("save_btn"), use_container_width=True, type="primary"):
        diagnosis_map = {
            "PCOS": has_pcos, "Hashimoto": has_hashi, "Anemia": has_anemia,
            "Celiac": has_celiakia, "Gout": has_gout, "NAFLD": has_nafld,
            "Adrenal Fatigue": has_adrenal, "Leaky Gut": has_leaky_gut,
            "Candida": has_candida, "Menopause": has_menopause, "Osteoporosis": has_osteo
        }
        active_diagnoses = [diag for diag, active in diagnosis_map.items() if active]
        
        row_data = {
            "Dátum": str(date.today()),
            "Diagnózy": ", ".join(active_diagnoses) if active_diagnoses else "None",
            "Cieľ": meta_goal,
            "Váha (kg)": weight,
            "Energia": energy_score,
            "Spánok": sleep_score,
            "Kalórie": totals["calories"],
            "Sacharidy (g)": totals["carbs"],
            "Voda (L)": water_total,
            "Symptómy": ", ".join(selected_symptoms) if selected_symptoms else "None"
# --- TAB 4: SHOPPING CART ---
with tab4:
    st.markdown(f"<h3 style='color: #059669;'>🛒 {txt('tabs')[3]}</h3>", unsafe_allow_html=True)
    
    # Database of recommendations
    RECOMMENDATIONS_DB = [
        ("Tekvicové semienka", "Zinok", "Zinok", False, False),
        ("Hovädzie mäso", "Železo/B12", "Hovädzie", False, False),
        ("Špenát", "Železo", "Zelenina", False, False),
        ("Hovädzia pečeň", "Železo", "Železo", False, False),
        ("Chia semienka", "Vláknina", "Semienka", False, False),
        ("Avokádo", "Vláknina", "Ovocie", False, False),
        ("Vaječné žĺtka", "Vitamín D", "Vajcia", False, False),
        ("Šampiňóny (UV)", "Vitamín D", "Huby", False, False),
        ("Lahôdkové droždie", "Vitamín B12", "Doplnky", False, False),
        ("Kuracie prsia", "Vitamín B12", "Hydina", False, False),
        ("Sezamové semienka", "Zinok", "Semienka", False, False),
        ("Kešu orechy", "Zinok", "Orechy", False, False),
        ("Cícer", "Zinok", "Strukoviny", False, False),
        ("Šošovica", "Železo", "Strukoviny", False, False),
        ("Quinoa", "Železo", "Obilniny", False, False),
        ("Mak siaty", "Železo", "Semienka", False, False),
        ("Maliny", "Vláknina", "Ovocie", False, False),
        ("Ľanové semienka", "Vláknina", "Semienka", False, False),
        ("Brokolica", "Vláknina", "Zelenina", False, False),
        ("Ovsené vločky", "Vláknina", "Obilniny", False, False),
        ("Divoký losos", "Vitamín D", "Ryby", True, False),
        ("Sardinky", "Vitamín D", "Ryby", True, False),
        ("Tresčia pečeň", "Vitamín D", "Ryby", True, False),
        ("Tuniak", "Vitamín B12", "Ryby", True, False),
        ("Kefír", "Vitamín B12", "Mliečne", False, True)
    ]

    # Filter only based on safety conditions (HIT, Hashimoto/Celiac)
    all_suggestions = []
    for food, benefit, category, is_fish, is_dairy in RECOMMENDATIONS_DB:
        if is_fish and has_hit: continue
        if is_dairy and (has_hashi or has_celiakia): continue
        all_suggestions.append((food, benefit, category))

    if 'shopping_list' not in st.session_state:
        st.session_state.shopping_list = []

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.subheader("Vyber si potraviny")
        for food, benefit, category in all_suggestions:
            if st.checkbox(f"**[{category}]** {food}", key=f"shop_{food}"):
                if food not in st.session_state.shopping_list:
                    st.session_state.shopping_list.append(food)
            else:
                if food in st.session_state.shopping_list:
                    st.session_state.shopping_list.remove(food)

    with col_r:
        st.subheader("📋 Tvoj Nákupný Zoznam")
        if st.session_state.shopping_list:
            for item in st.session_state.shopping_list:
                st.write(f"✅ {item}")
            
            # PDF Generation
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Nakupny zoznam", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", size=12)
            for item in st.session_state.shopping_list:
                pdf.cell(200, 10, txt=f"- {item}", ln=True)
            
            st.download_button(
                label="📥 Exportovať do PDF",
                data=pdf.output(dest='S').encode('latin-1'),
                file_name="nakupny_zoznam.pdf",
                mime="application/pdf"
            )
            if st.button("🗑️ Vyčistiť košík"):
                st.session_state.shopping_list = []
                st.rerun()
        else:
            st.info("Košík je prázdny. Vyber si potraviny vľavo.")
