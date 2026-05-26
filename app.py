import streamlit as st
import pandas as pd
from datetime import date
import os
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root {
        --bg-primary: #07110f; --bg-secondary: #0b1715;
        --bg-card: rgba(15,23,23,0.82); --bg-elevated: rgba(20,32,31,0.92);
        --primary: #14b8a6; --primary-glow: #2dd4bf; --secondary: #0f766e;
        --text-main: #ecfeff; --text-soft: #9fb7b3; --text-muted: #6b8a85;
        --border: rgba(45,212,191,0.10);
        --success: #10b981; --warning: #f59e0b; --danger: #fb7185;
        --shadow-sm: 0 4px 20px rgba(0,0,0,0.18);
        --shadow-md: 0 12px 40px rgba(0,0,0,0.30);
        --shadow-lg: 0 20px 60px rgba(0,0,0,0.42);
        --radius-lg: 24px; --radius-md: 18px; --radius-sm: 14px;
    }
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at top left, rgba(20,184,166,0.12), transparent 28%),
            radial-gradient(circle at bottom right, rgba(45,212,191,0.08), transparent 30%),
            linear-gradient(180deg, #07110f 0%, #081413 100%);
        color: var(--text-main);
    }
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px; }
    [data-testid="stSidebar"] {
        background: rgba(8,18,17,0.82); backdrop-filter: blur(22px);
        border-right: 1px solid rgba(45,212,191,0.08);
    }
    [data-testid="stSidebar"] * { color: var(--text-main); }
    h1 { font-size: 3.2rem !important; font-weight: 800 !important; letter-spacing: -2px !important; color: #ffffff !important; margin-bottom: 0.5rem !important; }
    h2 { font-size: 1.9rem !important; font-weight: 700 !important; color: #f0fdfa !important; }
    h3 { font-size: 1.2rem !important; font-weight: 700 !important; color: #ccfbf1 !important; }
    p, label, span { color: var(--text-soft) !important; }
    div[data-testid="metric-container"] {
        background: var(--bg-card); backdrop-filter: blur(18px);
        border: 1px solid rgba(255,255,255,0.04); border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md); transition: all 0.3s ease; padding: 1.5rem !important;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px); border-color: rgba(45,212,191,0.16);
        box-shadow: 0 0 0 1px rgba(45,212,191,0.08), 0 18px 50px rgba(0,0,0,0.45);
    }
    [data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.95rem !important; font-weight: 600 !important; }
    [data-testid="stMetricValue"] { color: var(--primary-glow) !important; font-size: 2.6rem !important; font-weight: 800 !important; letter-spacing: -2px; text-shadow: 0 0 18px rgba(45,212,191,0.22); }
    .stButton > button {
        border-radius: 999px !important;
        background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%) !important;
        color: white !important; border: 1px solid rgba(255,255,255,0.04) !important;
        padding: 0.85rem 1.6rem !important; font-weight: 700 !important; font-size: 0.95rem !important;
        box-shadow: 0 10px 30px rgba(20,184,166,0.16), inset 0 1px 0 rgba(255,255,255,0.08);
        transition: all 0.28s ease;
    }
    .stButton > button:hover { transform: translateY(-3px); box-shadow: 0 16px 36px rgba(20,184,166,0.28), 0 0 20px rgba(45,212,191,0.18); }
    .stButton > button:active { transform: scale(0.98); }
    .stTextInput > div > div > input, .stNumberInput > div > div > input,
    .stTextArea textarea {
        background: rgba(13,23,23,0.92) !important; color: #ecfeff !important;
        border-radius: var(--radius-md) !important; border: 1px solid rgba(45,212,191,0.10) !important;
        padding: 0.9rem 1rem !important; transition: all 0.25s ease;
    }

    /* ===== Selectbox — closed trigger box ===== */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div > div {
        background: rgba(13,23,23,0.92) !important;
        border: 1px solid rgba(45,212,191,0.10) !important;
        border-radius: var(--radius-md) !important;
    }
    /* The actual text value shown in the closed box */
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div[class*="ValueContainer"] span,
    .stSelectbox [data-baseweb="select"] div[class*="SingleValue"],
    .stSelectbox [data-baseweb="select"] div[class*="Placeholder"],
    .stSelectbox [data-baseweb="select"] input,
    .stSelectbox [data-baseweb="select"] * {
        color: #ecfeff !important;
    }

    /* ===== Dropdown popup panel ===== */
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    ul[data-baseweb="menu"] {
        background: #0d1f1e !important;
        border: 1px solid rgba(45,212,191,0.20) !important;
        border-radius: var(--radius-md) !important;
    }
    /* Each option row */
    [data-baseweb="option"] {
        background: #0d1f1e !important;
        color: #ecfeff !important;
    }
    [data-baseweb="option"]:hover,
    [data-baseweb="option"][aria-selected="true"] {
        background: rgba(45,212,191,0.14) !important;
        color: #ffffff !important;
    }
    /* Catch-all: any text inside the popup */
    [data-baseweb="popover"] span,
    [data-baseweb="popover"] div,
    [data-baseweb="popover"] li {
        color: #ecfeff !important;
    }
    .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: rgba(45,212,191,0.45) !important;
        box-shadow: 0 0 0 4px rgba(20,184,166,0.10), 0 0 24px rgba(20,184,166,0.10) !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 0.7rem; border-bottom: 1px solid rgba(45,212,191,0.08); padding-bottom: 0.5rem; }
    .stTabs [data-baseweb="tab"] { background: transparent; border-radius: 14px; color: var(--text-muted); height: 52px; font-weight: 600; transition: all 0.25s ease; }
    .stTabs [data-baseweb="tab"]:hover { background: rgba(20,184,166,0.08); color: var(--primary-glow); }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(20,184,166,0.18), rgba(15,118,110,0.10)) !important;
        color: #ffffff !important; border: 1px solid rgba(45,212,191,0.12) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 0 18px rgba(20,184,166,0.10);
    }
    .stAlert { background: rgba(14,24,24,0.88) !important; border: 1px solid rgba(45,212,191,0.08) !important; border-radius: var(--radius-md) !important; box-shadow: var(--shadow-sm); }
    .streamlit-expanderHeader {
        background: rgba(13,23,23,0.92) !important; border-radius: var(--radius-md) !important;
        border: 1px solid rgba(45,212,191,0.08) !important; color: #e6fffb !important;
        font-weight: 700 !important; transition: all 0.25s ease;
    }
    .streamlit-expanderHeader:hover { border-color: rgba(45,212,191,0.18) !important; box-shadow: 0 0 20px rgba(20,184,166,0.08); }
    .stDataFrame { border-radius: 18px !important; overflow: hidden !important; border: 1px solid rgba(45,212,191,0.08) !important; }
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(45,212,191,0.18); border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(45,212,191,0.34); }
    hr { border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(45,212,191,0.28), transparent); }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0px); } }
    .element-container { animation: fadeInUp 0.4s ease; }
    .progress-bar-bg { background: rgba(45,212,191,0.08); border-radius: 999px; height: 10px; margin: 4px 0 12px 0; }
    .progress-bar-fill { height: 10px; border-radius: 999px; background: linear-gradient(90deg, #0f766e, #2dd4bf); transition: width 0.5s ease; }
    .progress-bar-fill.over { background: linear-gradient(90deg, #f59e0b, #fb7185); }
    .nutrient-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; margin: 10px 0; }
    .nutrient-chip {
        background: rgba(20,32,31,0.85); border: 1px solid rgba(45,212,191,0.10);
        border-radius: 14px; padding: 10px 14px; text-align: center;
    }
    .nutrient-chip .val { font-size: 1.2rem; font-weight: 700; color: #2dd4bf; }
    .nutrient-chip .lbl { font-size: 0.75rem; color: #6b8a85; margin-top: 2px; }
    .score-ring { font-size: 3rem; text-align: center; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==================== TRANSLATIONS ====================
TRANSLATIONS = {
    "SK": {
        "title": "🌿 Inteligentný Metabolický & Hormonálny Tracker",
        "profile": "🧬 Krok 1: Zdravotný profil",
        "goal_hdr": "🎯 Krok 2: Tvoj cieľ",
        "goal_q": "Čo chceš dosiahnuť?",
        "antropo": "👤 Krok 3: Tvoje údaje",
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
        "goals": ["Zdravé chudnutie", "Udržanie váhy & Regenerácia", "Zdravé pribratie (Budovanie hmoty)"],
        "weight": "Váha (kg):", "height": "Výška (cm):", "age": "Vek:",
        "sex": "Pohlavie:", "sex_f": "Žena", "sex_m": "Muž",
        "activity": "Úroveň aktivity:",
        "activity_opts": ["Sedavý (kancelária)", "Mierne aktívny (1-3x/týždeň)", "Aktívny (4-5x/týždeň)", "Veľmi aktívny (každý deň)"],
        "bmi_label": "BMI",
        "target_info": "🎯 **Tvoj cieľový príjem:**\n* **Kalórie:** {cal} kcal\n* **Bielkoviny:** {prot} g\n* **Čisté sacharidy:** {carbs} g\n* **Tuky:** {fat} g\n* **Voda:** {water} L",
        "tabs": ["🍽️ Potravinový asistent", "📊 Dnešný denník", "📈 Dlhodobý vývoj", "🛒 Nákupný košík"],
        "search_hdr": "🔍 Hľadať potravinu",
        "search_lbl": "Zadaj názov v slovenčine alebo angličtine:",
        "food_group_filter": "Filtrovať podľa skupiny potravín:",
        "all_groups": "Všetky skupiny",
        "select_food": "Vyber potravinu:",
        "grams": "Gramáž (g):",
        "analysis": "#### 📊 Analýza pre {g}g:",
        "cal": "Kalórie", "prot": "Bielkoviny", "carbs": "Sacharidy", "fiber": "Vláknina",
        "fat": "Tuky", "sugar": "Cukor",
        "micros_hdr": "🔬 Mikronutrienty",
        "warnings_hdr": "### 🚨 Zdravotné upozornenia:",
        "warn_gluten": "🌾 **Obsahuje LEPKOVKU:** Riziko zápalovej reakcie čreva.",
        "warn_milk": "🥛/🫛 **Mlieko/Sója:** Možný skrížený alergén pre štítnu žľazu.",
        "warn_hit": "⚠️ **Vysoký Histamín:** Sleduj reakciu tela.",
        "warn_gastritis": "🔥 **Žalúdočný iritant:** Môže dráždiť žalúdok.",
        "warn_sugar": "🚨 **Pozor na cukor:** Vysoká inzulínová špička.",
        "warn_purines": "🥩 **Vysoké puríny (Dna):** Riziko záchvatu dny.",
        "warn_oxalates": "🌱 **Vysoké oxaláty:** Nebezpečenstvo obličkových kameňov.",
        "warn_high_fat": "🧈 **Vysoký obsah tuku:** Môže podráždiť žlčník.",
        "warn_candida": "🍄 **Candida:** Vysoký obsah cukrov podporuje kvasinky.",
        "warn_leaky_gut": "🛡️ **Leaky Gut:** Pozor na dráždivé bielkoviny.",
        "warn_osteo": "🦴 **Osteoporóza:** Kofeín môže zhoršovať vstrebávanie vápnika.",
        "add_btn": "➕ Pridať do dňa",
        "add_success": "✅ Pridané do dnešného prehľadu.",
        "not_found": "❌ Slovo sa v databáze nenašlo.",
        "encyclopedia": "### 💡 Encyklopédia metabolizmu",
        "enc_pcos_t": "🌾 Inzulínový blok", "enc_pcos_b": "**PCOS & Cukrovka 2. typu:** Vláknina a nízky cukor sú kľúč k obnove inzulínovej citlivosti.",
        "enc_hashi_t": "🦋 Spomalený motor (Hashimoto)", "enc_hashi_b": "**Hypotyreóza:** Bielkoviny, zinok a selén chránia svaly a stimulujú metabolizmus.",
        "enc_hyper_t": "🔥 Prehriaty motor (Hypertyreóza)", "enc_hyper_b": "**Zvýšená funkcia:** Telo rýchlo odbúrava hmotu. Potrebuješ zdravý kalorický prebytok.",
        "enc_anemia_t": "🩸 Kyslíkový dlh (Anémia)", "enc_anemia_b": "**Chýbajúce železo:** Bez dostatočného množstva železa bunky nemajú dostatok kyslíka.",
        "enc_gout_t": "🦴 Kyselina močová (Dna)", "enc_gout_b": "**Dna:** Vyhýbaj sa červenému mäsu, vnútornostiam, alkoholu a nadmernej fruktóze.",
        "enc_nafld_t": "🍏 Tuk v pečeni (NAFLD)", "enc_nafld_b": "**Steatóza:** Minimalizuj priemyselné cukry, fruktózový sirup a trans-tuky.",
        "enc_menopause_t": "🌸 Menopauza", "enc_menopause_b": "**Perimenopauza:** Zvýš príjem vápnika, vitamínu D a fytoestrogénov (ľan, sója).",
        "enc_osteo_t": "🦴 Osteoporóza", "enc_osteo_b": "**Kosti:** Vápnik + vitamín D + K2 sú základ. Vyhýbaj sa nadmernému kofeínu.",
        "enc_adrenal_t": "⚡ Adrenálna únava", "enc_adrenal_b": "**Kortizol:** Horčík, vitamín C a adaptogény pomáhajú regulovať stresovú os.",
        "diary_hdr": "📊 Tvoj dnešný denník",
        "status": "#### 📈 Aktuálny stav dňa:",
        "progress_of": "z",
        "feedback_hdr": "💬 Personalizované spätné väzby",
        "fb_pcos_fiber_low": "🌾 **PCOS/Cukrovka — pridaj vlákninu:** Dnes len {fiber}g z 25g. Vláknina spomaľuje vstrebávanie cukru a zabraňuje inzulínovým špičkám. Skús ovsené vločky, šošovicu, brokolicu alebo chia semienka.",
        "fb_pcos_fiber_ok": "✨ **PCOS/Cukrovka:** Výborný príjem vlákniny! Pomáha udržiavať stabilnú hladinu cukru v krvi.",
        "fb_pcos_sugar_high": "🚨 **PCOS/Pečeň — znížiť cukor:** Dnes {sugar}g cukru (limit 35g). Vysoký cukor spúšťa inzulínovú špičku a ukladanie tuku v pečeni. Vymeň sladkosti za ovocie s nízkym GI (bobule, jablko).",
        "fb_anemia_iron_low": "🩸 **Anémia — doplniť železo:** Dnes len {iron}mg z 18mg. Bez železa červené krvinky nenesú dostatok kyslíka → únava, bledosť. Skús hovädziu pečeň, šošovicu alebo špenát s vitamínom C.",
        "fb_anemia_iron_ok": "💪 **Anémia:** Skvelý príjem železa! Červené krvinky majú dostatok paliva.",
        "fb_hashi_zinc_low": "🦋 **Hashimoto — doplniť zinok:** Dnes len {zinc}mg z 11–15mg. Zinok je nevyhnutný pre premenu T4 na aktívny T3 hormón. Skús tekvicové semienka, kešu alebo hovädzie mäso.",
        "fb_hashi_zinc_ok": "✨ **Hashimoto:** Zinok v poriadku — štítna žľaza má podporu pre syntézu hormónov.",
        "fb_hashi_selenium_low": "🦋 **Hashimoto — doplniť selén:** Dnes len {sel}mcg z 55–200mcg. Selén chráni štítnu žľazu pred zápalom a oxidačným stresom. Stačia 2 para orechy denne alebo porcia lososa.",
        "fb_hashi_selenium_ok": "✨ **Hashimoto:** Selén v poriadku — štítna žľaza je chránená pred zápalom.",
        "fb_hashi_risks": "⚠️ **Hashimoto:** Dnes {risks}x spúšťač (lepok/mlieko). Tieto bielkoviny môžu napodobňovať tkanivo štítnej žľazy a zosilňovať autoimunitnú reakciu.",
        "fb_celiakia_risk": "🚨 **Celiakia:** V denníku je jedlo s lepkom! Lepok poškodzuje klky tenkého čreva a blokuje vstrebávanie živín.",
        "fb_gastritis_risk": "🔥 **Gastritída:** Zaznamenal/a si dráždivú potravinu. Môže zvýšiť produkciu žalúdočnej kyseliny a zhoršiť zápal sliznice.",
        "fb_gout_risk": "🦴 **Dna:** Puríny v jedálničku sa rozkladajú na kyselinu močovú, ktorá sa ukladá v kĺboch. Pij viac vody a vyhni sa alkoholu.",
        "fb_vitd_low": "☀️ **Vitamín D — doplniť:** Dnes len {vitd}mcg z 15–20mcg. Vitamín D reguluje imunitu, náladu aj vstrebávanie vápnika. Skús lososa, vajcia alebo doplnok 1000–2000 IU.",
        "fb_vitd_ok": "☀️ **Vitamín D:** Výborný príjem! Imunita, kosti aj nálada majú podporu.",
        "fb_magnesium_low": "⚡ **Horčík — doplniť:** Dnes len {mag}mg z 300–400mg. Horčík reguluje stres, spánok a svalové kŕče. Skús mandle, tmavú čokoládu 85%, tekvicové semienka alebo špenát.",
        "fb_magnesium_ok": "⚡ **Horčík:** Príjem v poriadku — nervový systém a svaly sú v pohode.",
        "fb_calcium_low": "🦴 **Vápnik — doplniť:** Dnes len {cal}mg z 1000–1200mg. Vápnik je základ hustoty kostí. Skús grécky jogurt, sardinky, mandle alebo brokolicu.",
        "fb_calcium_ok": "🦴 **Vápnik:** Výborný príjem! Kosti a zuby majú dostatočnú výživu.",
        "fb_omega3_low": "🐟 **Omega-3 — doplniť:** Dnes len {o3}mg z 1000–2000mg. Omega-3 znižujú zápal, chránia srdce a mozog. Skús lososa, sardinky, ľanové alebo chia semienka.",
        "fb_omega3_ok": "🐟 **Omega-3:** Skvelý príjem! Zápal je pod kontrolou, srdce a mozog majú podporu.",
        "fb_perfect": "☀️ Tvoj dnešný jedálniček perfektne rešpektuje tvoj zdravotný stav. Tak ďalej!",
        "fb_water_low": "💧 **Hydratácia — piť viac:** Dnes len {water}L z {target}L. Voda transportuje živiny, čistí obličky a pomáha metabolizmu. Daj si pohár hneď teraz.",
        "fb_water_high": "⚠️ **Nadmerná hydratácia:** Dnes už {water}L (limit {limit}L). Príliš veľa vody vyplavuje sodík a minerály — riziko hyponatriémie.",
        "fb_water_ok": "💧 **Hydratácia:** Výborná! Telo je dobre hydratované.",
        "no_meals": "📭 Zatiaľ si nezadal/nezadala žiadne potraviny.",
        "remove_meal": "🗑️ Odstrániť",
        "water_hdr": "💧 Sledovanie hydratácie",
        "water_intake": "Pohár vody (250ml):",
        "water_total": "Celkovo vody dnes:",
        "symptoms_hdr": "🩺 Sledovanie príznakov",
        "sym_gain_fatigue": "**Symptómy príberania/Únavy:**",
        "sym_hunger": "Náhly vlčí hlad", "sym_weakness": "Extrémna svalová slabosť", "sym_bloating": "Nadúvanie/Plynatosť",
        "sym_lose_weight": "**Symptómy straty hmotnosti/Zápalov:**",
        "sym_palpitations": "Búšenie srdca", "sym_cramps": "Kŕče v bruchu", "sym_gout_pain": "Bolesť kĺbov (Dna)",
        "sym_subjective": "**Subjektívne pocity:**",
        "sym_energy": "Energia (1-10):", "sym_sleep": "Spánok (1-10):",
        "save_btn": "💾 Ukončiť a uložiť deň",
        "save_success": "✅ Záznam úspešne uložený!",
        "history_hdr": "📈 Dlhodobé sledovanie vývoja tela",
        "history_empty": "📭 Žiadne historické záznamy neboli zatiaľ vytvorené.",
        "chart_weight": "📊 Pohyb telesnej hmotnosti (kg)",
        "chart_calories": "📊 Denný príjem kalórií (kcal)",
        "chart_energy": "📊 Energia & Spánok",
        "metabolism_status": "### 🧬 Stav metabolizmu:",
        "metab_excellent": "✅ Vynikajúci! Tvoj metabolizmus je v poriadku.",
        "metab_good": "😊 Dobré! Dnes si robil/robila výborné rozhodnutia.",
        "metab_warning": "⚠️ Pozor! Niektoré nutričné metriky si minul/minula.",
        "metab_critical": "🚨 KRITICKÉ! Potrebuješ urgentne zmeniť svoj príjem.",
        "metab_neutral": "😐 Neutrálny deň. Skús sa zajtra zlepšiť.",
        "none": "Žiadne", "err_save": "❌ Nepodarilo sa uložiť",
        "db_status_ok": "✅ Databáza úspešne spárovaná.",
        "db_status_upload": "📁 Databáza nenájdená. Nahraj 'food_data_en_sk.csv':",
        "nutrient_score": "Nutričné skóre dňa",
        "clear_day": "🗑️ Vymazať celý deň",
    },
    "EN": {
        "title": "🌿 Smart Metabolic & Hormonal Tracker",
        "profile": "🧬 Step 1: Health Profile",
        "goal_hdr": "🎯 Step 2: Your Goal",
        "goal_q": "What do you want to achieve?",
        "antropo": "👤 Step 3: Your Data",
        "gain_weight_tendency": "📉 Weight Gain / Loss Block:",
        "pcos": "PCOS (Insulin Resistance)", "hashi": "Hashimoto (Slow Metabolism)",
        "db2": "Type 2 Diabetes", "anemia": "Anemia (Iron Deficiency)",
        "cushing": "Cushing's Syndrome", "lepid": "Lipedema / Lymphedema",
        "lose_weight_tendency": "📈 Weight Loss / Problem Gaining:",
        "hyper": "Hyperthyroidism", "celiakia": "Celiac Disease / IBD", "addison": "Addison's Disease",
        "digestion": "🍽️ Digestive Sensitivities:",
        "hit": "HIT (Histamine Intolerance)", "gastritis": "Gastritis",
        "sibo": "SIBO / IBS", "gallbladder": "Gallbladder Issues",
        "metabolic_syndromes": "🧬 Metabolic, Organ & Hormonal Disorders:",
        "gout": "Gout (High Uric Acid)", "nafld": "Fatty Liver (NAFLD)",
        "hypertension": "Hypertension", "kidney_stones": "Kidney Stones",
        "adrenal_fatigue": "Adrenal Fatigue", "leaky_gut": "Leaky Gut Syndrome",
        "candida": "Candida Overgrowth", "menopause": "Perimenopause / Menopause",
        "osteo": "Osteoporosis / Osteopenia",
        "goals": ["Healthy Weight Loss", "Weight Maintenance & Recovery", "Healthy Weight Gain (Bulking)"],
        "weight": "Weight (kg):", "height": "Height (cm):", "age": "Age:",
        "sex": "Sex:", "sex_f": "Female", "sex_m": "Male",
        "activity": "Activity level:",
        "activity_opts": ["Sedentary (desk job)", "Lightly active (1-3x/week)", "Active (4-5x/week)", "Very active (daily)"],
        "bmi_label": "BMI",
        "target_info": "🎯 **Your Target Intake:**\n* **Calories:** {cal} kcal\n* **Protein:** {prot} g\n* **Net Carbs:** {carbs} g\n* **Fat:** {fat} g\n* **Water:** {water} L",
        "tabs": ["🍽️ Food Assistant", "📊 Daily Diary", "📈 Long-term Progress", "🛒 Shopping Cart"],
        "search_hdr": "🔍 Search Food",
        "search_lbl": "Enter name in Slovak or English:",
        "food_group_filter": "Filter by food group:",
        "all_groups": "All groups",
        "select_food": "Select food:", "grams": "Weight (g):",
        "analysis": "#### 📊 Analysis for {g}g:",
        "cal": "Calories", "prot": "Protein", "carbs": "Net Carbs", "fiber": "Fiber",
        "fat": "Fat", "sugar": "Sugar",
        "micros_hdr": "🔬 Micronutrients",
        "warnings_hdr": "### 🚨 Health Warnings:",
        "warn_gluten": "🌾 **Contains GLUTEN:** Risk of intestinal reaction.",
        "warn_milk": "🥛/🫛 **Milk/Soy:** Possible thyroid allergen.",
        "warn_hit": "⚠️ **High Histamine:** Monitor your reaction.",
        "warn_gastritis": "🔥 **Stomach Irritant:** May irritate the stomach.",
        "warn_sugar": "🚨 **Watch sugar:** High insulin spike.",
        "warn_purines": "🥩 **High Purines (Gout):** Risk of gout attack.",
        "warn_oxalates": "🌱 **High Oxalates:** Risk of kidney stones.",
        "warn_high_fat": "🧈 **High Fat:** May worsen gallbladder/NAFLD.",
        "warn_candida": "🍄 **Candida:** High simple sugars feed yeast.",
        "warn_leaky_gut": "🛡️ **Leaky Gut:** Beware of irritating proteins.",
        "warn_osteo": "🦴 **Osteoporosis:** Caffeine can impair calcium absorption.",
        "add_btn": "➕ Add to Day", "add_success": "✅ Added to today's overview.",
        "not_found": "❌ Word not found in the database.",
        "encyclopedia": "### 💡 Metabolism Encyclopedia",
        "enc_pcos_t": "🌾 Insulin Block", "enc_pcos_b": "**PCOS & Diabetes:** Fiber is key to restoring insulin sensitivity.",
        "enc_hashi_t": "🦋 Slow Motor (Hashimoto)", "enc_hashi_b": "**Hypothyroidism:** Protein, zinc and selenium protect muscles and stimulate metabolism.",
        "enc_hyper_t": "🔥 Overheated Motor", "enc_hyper_b": "**Hyperthyroidism:** Your body burns mass fast. You need a healthy caloric surplus.",
        "enc_anemia_t": "🩸 Oxygen Debt", "enc_anemia_b": "**Anemia:** Without enough iron, cells lack oxygen.",
        "enc_gout_t": "🦴 Uric Acid (Gout)", "enc_gout_b": "**Gout:** Avoid red meat, organ meats, alcohol and excess fructose.",
        "enc_nafld_t": "🍏 Fatty Liver", "enc_nafld_b": "**Steatosis:** Minimize processed sugars, fructose syrup and trans fats.",
        "enc_menopause_t": "🌸 Menopause", "enc_menopause_b": "**Perimenopause:** Increase calcium, vitamin D and phytoestrogens (flax, soy).",
        "enc_osteo_t": "🦴 Osteoporosis", "enc_osteo_b": "**Bones:** Calcium + Vitamin D + K2 are the foundation. Avoid excess caffeine.",
        "enc_adrenal_t": "⚡ Adrenal Fatigue", "enc_adrenal_b": "**Cortisol:** Magnesium, vitamin C and adaptogens help regulate the stress axis.",
        "diary_hdr": "📊 Your Daily Diary",
        "status": "#### 📈 Current Daily Status:",
        "progress_of": "of",
        "feedback_hdr": "💬 Personalized Feedback",
        "fb_pcos_fiber_low": "🌾 **PCOS/Diabetes — add fiber:** Only {fiber}g of 25g today. Fiber slows sugar absorption and prevents insulin spikes. Try oats, lentils, broccoli or chia seeds.",
        "fb_pcos_fiber_ok": "✨ **PCOS/Diabetes:** Great fiber intake! Helps keep blood sugar stable throughout the day.",
        "fb_pcos_sugar_high": "🚨 **PCOS/Liver — reduce sugar:** {sugar}g today (limit 35g). High sugar triggers insulin spikes and promotes fat storage in the liver. Swap sweets for low-GI fruit (berries, apple).",
        "fb_anemia_iron_low": "🩸 **Anemia — boost iron:** Only {iron}mg of 18mg today. Without iron, red blood cells can't carry enough oxygen → fatigue, pallor. Try beef liver, lentils or spinach with vitamin C.",
        "fb_anemia_iron_ok": "💪 **Anemia:** Great iron intake! Red blood cells have enough fuel.",
        "fb_hashi_zinc_low": "🦋 **Hashimoto — add zinc:** Only {zinc}mg of 11–15mg today. Zinc is essential for converting T4 into active T3 hormone. Try pumpkin seeds, cashews or beef.",
        "fb_hashi_zinc_ok": "✨ **Hashimoto:** Zinc is good — thyroid has support for hormone synthesis.",
        "fb_hashi_selenium_low": "🦋 **Hashimoto — add selenium:** Only {sel}mcg of 55–200mcg today. Selenium protects the thyroid from inflammation and oxidative stress. Just 2 Brazil nuts a day or a portion of salmon.",
        "fb_hashi_selenium_ok": "✨ **Hashimoto:** Selenium is good — thyroid is protected from inflammation.",
        "fb_hashi_risks": "⚠️ **Hashimoto:** {risks} trigger food(s) today (gluten/dairy). These proteins can mimic thyroid tissue and amplify the autoimmune response.",
        "fb_celiakia_risk": "🚨 **Celiac:** Gluten-containing food in your diary! Gluten damages intestinal villi and blocks nutrient absorption.",
        "fb_gastritis_risk": "🔥 **Gastritis:** Irritant food logged. May increase stomach acid production and worsen mucosal inflammation.",
        "fb_gout_risk": "🦴 **Gout:** Purines in your diet break down into uric acid which deposits in joints. Drink more water and avoid alcohol.",
        "fb_vitd_low": "☀️ **Vitamin D — boost:** Only {vitd}mcg of 15–20mcg today. Vitamin D regulates immunity, mood and calcium absorption. Try salmon, eggs or a 1000–2000 IU supplement.",
        "fb_vitd_ok": "☀️ **Vitamin D:** Excellent! Immunity, bones and mood all have support.",
        "fb_magnesium_low": "⚡ **Magnesium — boost:** Only {mag}mg of 300–400mg today. Magnesium regulates stress, sleep and muscle cramps. Try almonds, 85% dark chocolate, pumpkin seeds or spinach.",
        "fb_magnesium_ok": "⚡ **Magnesium:** Good intake — nervous system and muscles are supported.",
        "fb_calcium_low": "🦴 **Calcium — boost:** Only {cal}mg of 1000–1200mg today. Calcium is the foundation of bone density. Try Greek yogurt, sardines, almonds or broccoli.",
        "fb_calcium_ok": "🦴 **Calcium:** Excellent! Bones and teeth are well nourished.",
        "fb_omega3_low": "🐟 **Omega-3 — boost:** Only {o3}mg of 1000–2000mg today. Omega-3 reduces inflammation and protects the heart and brain. Try salmon, sardines, flaxseed or chia seeds.",
        "fb_omega3_ok": "🐟 **Omega-3:** Great intake! Inflammation is under control, heart and brain are supported.",
        "fb_perfect": "☀️ Your meal plan perfectly respects your health profile. Keep it up!",
        "fb_water_low": "💧 **Hydration — drink more:** Only {water}L of {target}L today. Water transports nutrients, flushes kidneys and supports metabolism. Have a glass right now.",
        "fb_water_high": "⚠️ **Overhydration:** Already {water}L today (limit {limit}L). Too much water flushes sodium and minerals — risk of hyponatremia.",
        "fb_water_ok": "💧 **Hydration:** Excellent! Your body is well hydrated.",
        "no_meals": "📭 No foods logged yet today.",
        "remove_meal": "🗑️ Remove",
        "water_hdr": "💧 Hydration Tracking",
        "water_intake": "Glass of water (250ml):",
        "water_total": "Total water today:",
        "symptoms_hdr": "🩺 Symptom Tracking",
        "sym_gain_fatigue": "**Gain / Fatigue Symptoms:**",
        "sym_hunger": "Sudden ravenous hunger", "sym_weakness": "Extreme muscle weakness", "sym_bloating": "Bloating / Gas",
        "sym_lose_weight": "**Loss / Inflammation Symptoms:**",
        "sym_palpitations": "Heart palpitations", "sym_cramps": "Abdominal cramps", "sym_gout_pain": "Joint pain (Gout)",
        "sym_subjective": "**Subjective Feelings:**",
        "sym_energy": "Energy (1-10):", "sym_sleep": "Sleep quality (1-10):",
        "save_btn": "💾 Finish and Save Day", "save_success": "✅ Log saved!",
        "history_hdr": "📈 Long-term Body Progress",
        "history_empty": "📭 No history logs yet.",
        "chart_weight": "📊 Body Weight Progress (kg)",
        "chart_calories": "📊 Daily Calorie Intake (kcal)",
        "chart_energy": "📊 Energy & Sleep",
        "metabolism_status": "### 🧬 Metabolism Status:",
        "metab_excellent": "✅ Excellent! Your metabolism is on track.",
        "metab_good": "😊 Good! You made great choices today.",
        "metab_warning": "⚠️ Caution! Some metrics are off target.",
        "metab_critical": "🚨 CRITICAL! You need to urgently change your intake.",
        "metab_neutral": "😐 Neutral day. Try to improve tomorrow.",
        "none": "None", "err_save": "❌ Failed to save",
        "db_status_ok": "✅ Food database linked.",
        "db_status_upload": "📁 Upload 'food_data_en_sk.csv':",
        "nutrient_score": "Daily Nutrient Score",
        "clear_day": "🗑️ Clear entire day",
    }
}

# ==================== CONSTANTS ====================
HISTORY_FILE = "zdravotna_historia_global.csv"
HISTORY_COLUMNS = ["Dátum", "Diagnózy", "Cieľ", "Váha (kg)", "Energia", "Spánok",
                   "Kalórie", "Sacharidy (g)", "Voda (L)", "Symptómy"]

ACTIVITY_MULTIPLIERS = {
    0: 1.2,   # Sedentary
    1: 1.375, # Lightly active
    2: 1.55,  # Active
    3: 1.725, # Very active
}

# ==================== UTILITY FUNCTIONS ====================
def get_lang():
    if "lang" not in st.session_state:
        st.session_state.lang = "SK"
    return st.session_state.lang

def txt(key: str):
    lang = get_lang()
    return TRANSLATIONS[lang].get(key, key)

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
        if bmi < 18.5: return "Podváha"
        if bmi < 25.0: return "Normálna váha"
        if bmi < 30.0: return "Nadváha"
        return "Obezita"
    else:
        if bmi < 18.5: return "Underweight"
        if bmi < 25.0: return "Normal weight"
        if bmi < 30.0: return "Overweight"
        return "Obese"

def progress_bar_html(value, target, unit="", label=""):
    """Render a labeled progress bar with icon and name. Over 100% turns orange/red."""
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
    # Nothing logged yet — don't score, return a special "empty" level
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
    if score >= 85: level = "excellent"
    elif score >= 70: level = "good"
    elif score >= 50: level = "warning"
    elif score >= 30: level = "critical"
    else: level = "neutral"
    return score, level

def nutrient_score(totals, targets):
    """Return 0-100 score based on how many key nutrients hit their target."""
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

# ==================== DATA LOADING ====================
@st.cache_data
def load_food_database(uploaded_file=None):
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
    # Fallback mock data
    return pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'name_en': ['Oats', 'Spinach', 'Beef', 'Chocolate', 'Liver'],
        'name_sk': ['Ovsene vlocky', 'Spenat', 'Hovadzie maso', 'Cokolada', 'Pecen'],
        'Food Group': ['Grains', 'Vegetables', 'Meat', 'Sweets', 'Meat'],
        'Calories': [389, 23, 250, 546, 175],
        'Protein (g)': [16.9, 2.9, 26.0, 4.9, 27.0],
        'Fat (g)': [6.9, 0.4, 15.0, 31.0, 5.0],
        'Net-Carbs (g)': [66.3, 1.4, 0.0, 54.0, 4.0],
        'Sugars (g)': [0.0, 0.4, 0.0, 48.0, 0.0],
        'Fiber (g)': [10.6, 2.2, 0.0, 7.0, 0.0],
        'Iron, Fe (mg)': [4.7, 2.7, 2.6, 8.0, 18.0],
        'Zinc, Zn (mg)': [4.0, 0.5, 4.3, 2.3, 4.0],
        'Vitamin D (mcg)': [0.0, 0.0, 0.1, 0.0, 1.2],
        'Magnesium (mg)': [138, 79, 21, 228, 18],
        'Calcium (mg)': [54, 99, 18, 73, 11],
        'Omega 3s (mg)': [111, 138, 62, 30, 0],
        'Selenium, Se (mcg)': [34, 1, 14, 6, 39],
        'Vitamin C (mg)': [0, 28, 0, 0, 27],
        'Vitamin B-12 (mcg)': [0, 0, 2.6, 0, 59],
        'Potassium, K (mg)': [429, 558, 318, 715, 313],
        'Sodium (mg)': [6, 79, 72, 24, 68],
        'Caffeine (mg)': [0, 0, 0, 43, 0],
    }), False

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            return pd.read_csv(HISTORY_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=HISTORY_COLUMNS)

def save_history_row(row_dict):
    history_df = load_history()
    new_row = pd.DataFrame([row_dict])
    history_df = pd.concat([history_df, new_row], ignore_index=True)
    try:
        history_df.to_csv(HISTORY_FILE, index=False)
    except Exception as e:
        st.error(f"{txt('err_save')}: {e}")

# ==================== WARNING DETECTION ====================
def detect_food_warnings(food_name: str, health_conditions: dict) -> list:
    name_lower = food_name.lower()
    warnings = []
    gluten_kw = ['wheat','barley','rye','flour','bread','gluten','psenica','jacmen','raz','muka','chlieb','lepok']
    dairy_kw  = ['milk','cheese','yogurt','cream','soy','mlieko','syr','jogurt','smotana','soja']
    histamine_kw = ['tomato','spinach','avocado','eggplant','cheese','wine','vinegar','sauerkraut',
                    'fermented','shrimp','tuna','paradaj','spenat','sir','vino']
    gastritis_kw = ['chili','pepper','coffee','lemon','onion','garlic','fried','korenie','kava',
                    'citron','cesnak','cibuľa','vypraz']
    purine_kw  = ['beef','pork','liver','beer','shrimp','sardine','hovadz','bravcov','pecen','pivo','krevet','sardyn']
    oxalate_kw = ['spinach','rhubarb','chocolate','nuts','spenat','rebarbora','cokolada','orech']
    candida_kw = ['sugar','cukor','fruit','ovocie','honey','med','sirup','syrup','chocolate','cokolada']
    osteo_kw   = ['caffeine','coffee','kava','soda','cola','energy','limonada']

    if (health_conditions.get('has_celiakia') or health_conditions.get('has_hashi')) and any(x in name_lower for x in gluten_kw):
        warnings.append(txt("warn_gluten"))
    if health_conditions.get('has_hashi') and any(x in name_lower for x in dairy_kw):
        warnings.append(txt("warn_milk"))
    if health_conditions.get('has_hit') and any(x in name_lower for x in histamine_kw):
        warnings.append(txt("warn_hit"))
    if (health_conditions.get('has_gastritis') or health_conditions.get('has_sibo')) and any(x in name_lower for x in gastritis_kw):
        warnings.append(txt("warn_gastritis"))
    if health_conditions.get('has_gout') and any(x in name_lower for x in purine_kw):
        warnings.append(txt("warn_purines"))
    if health_conditions.get('has_kidney_stones') and any(x in name_lower for x in oxalate_kw):
        warnings.append(txt("warn_oxalates"))
    if health_conditions.get('has_candida') and any(x in name_lower for x in candida_kw):
        warnings.append(txt("warn_candida"))
    if health_conditions.get('has_leaky_gut') and any(x in name_lower for x in gluten_kw + dairy_kw):
        warnings.append(txt("warn_leaky_gut"))
    if health_conditions.get('has_osteo') and any(x in name_lower for x in osteo_kw):
        warnings.append(txt("warn_osteo"))
    return warnings

# ==================== MAIN APP HEADER ====================
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"<h1 style='color:#0d9488;margin-bottom:0px;'>{txt('title')}</h1>", unsafe_allow_html=True)
with col2:
    new_lang = st.radio("🌐", ["SK", "EN"], horizontal=True, label_visibility="collapsed")
    st.session_state.lang = new_lang
st.divider()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=80)

    # Health profile
    with st.expander(f"🧬 {txt('profile')}", expanded=True):
        st.markdown(f"**{txt('gain_weight_tendency')}**")
        has_pcos      = st.checkbox(txt("pcos"),     key="pcos")
        has_hashi     = st.checkbox(txt("hashi"),    key="hashi")
        has_db2       = st.checkbox(txt("db2"),      key="db2")
        has_anemia    = st.checkbox(txt("anemia"),   key="anemia")
        has_cushing   = st.checkbox(txt("cushing"),  key="cushing")
        has_lipedema  = st.checkbox(txt("lepid"),    key="lipedema")
        st.markdown(f"**{txt('lose_weight_tendency')}**")
        has_hyper     = st.checkbox(txt("hyper"),    key="hyper")
        has_celiakia  = st.checkbox(txt("celiakia"), key="celiakia")
        has_addison   = st.checkbox(txt("addison"),  key="addison")
        st.markdown(f"**{txt('digestion')}**")
        has_hit        = st.checkbox(txt("hit"),        key="hit")
        has_gastritis  = st.checkbox(txt("gastritis"),  key="gastritis")
        has_sibo       = st.checkbox(txt("sibo"),       key="sibo")
        has_gallbladder= st.checkbox(txt("gallbladder"),key="gallbladder")
        st.markdown(f"**{txt('metabolic_syndromes')}**")
        has_gout        = st.checkbox(txt("gout"),         key="gout")
        has_nafld       = st.checkbox(txt("nafld"),        key="nafld")
        has_hypertension= st.checkbox(txt("hypertension"), key="hypertension")
        has_kidney_stones=st.checkbox(txt("kidney_stones"),key="kidney_stones")
        has_adrenal     = st.checkbox(txt("adrenal_fatigue"),key="adrenal")
        has_leaky_gut   = st.checkbox(txt("leaky_gut"),    key="leaky_gut")
        has_candida     = st.checkbox(txt("candida"),      key="candida")
        has_menopause   = st.checkbox(txt("menopause"),    key="menopause")
        has_osteo       = st.checkbox(txt("osteo"),        key="osteo")

    # Goal
    with st.expander(txt("goal_hdr"), expanded=False):
        meta_goal = st.radio(txt("goal_q"), TRANSLATIONS[get_lang()]["goals"], label_visibility="collapsed")

    # User data
    with st.expander(txt("antropo"), expanded=False):
        sex_opts = [txt("sex_f"), txt("sex_m")]
        sex = st.radio(txt("sex"), sex_opts, horizontal=True)
        weight = st.number_input(txt("weight"), min_value=30.0, value=70.0, step=0.1)
        height = st.number_input(txt("height"), min_value=120, value=165)
        age    = st.number_input(txt("age"),    min_value=15,  value=30)
        act_opts = TRANSLATIONS[get_lang()]["activity_opts"]
        act_idx  = st.selectbox(txt("activity"), range(len(act_opts)), format_func=lambda i: act_opts[i])

        # BMI display
        bmi = calculate_bmi(weight, height)
        bmi_cat = bmi_category(bmi, get_lang())
        bmi_color = "#10b981" if 18.5 <= bmi < 25 else ("#f59e0b" if bmi < 30 else "#fb7185")
        st.markdown(f"**{txt('bmi_label')}:** <span style='color:{bmi_color};font-weight:700;'>{bmi} — {bmi_cat}</span>", unsafe_allow_html=True)

    # ---- Calorie calculation (Mifflin-St Jeor) ----
    is_female = (sex == txt("sex_f"))
    if is_female:
        bmr = round(10 * weight + 6.25 * height - 5 * age - 161)
    else:
        bmr = round(10 * weight + 6.25 * height - 5 * age + 5)

    act_mult = ACTIVITY_MULTIPLIERS[act_idx]
    base_maintenance = round(bmr * act_mult)

    if has_cushing:  base_maintenance = round(base_maintenance * 0.9)
    if has_addison:  base_maintenance = round(base_maintenance * 1.1)

    goal_low_carb = ["Zdravé chudnutie", "Healthy Weight Loss"]
    goal_bulk     = ["Zdravé pribratie (Budovanie hmoty)", "Healthy Weight Gain (Bulking)"]

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
    target_fat   = round((target_cal * (1.0 - (carbs_pct + 0.25))) / 9)
    target_water = calculate_water_target(weight, has_hyper, has_hypertension)

    st.info(txt("target_info").format(
        cal=target_cal, prot=target_protein,
        carbs=target_carbs, fat=target_fat, water=target_water))

    # Database
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

health_conditions = {
    'has_pcos': has_pcos, 'has_hashi': has_hashi, 'has_db2': has_db2,
    'has_anemia': has_anemia, 'has_celiakia': has_celiakia, 'has_hit': has_hit,
    'has_gastritis': has_gastritis, 'has_sibo': has_sibo, 'has_gout': has_gout,
    'has_kidney_stones': has_kidney_stones, 'has_gallbladder': has_gallbladder,
    'has_nafld': has_nafld, 'has_adrenal': has_adrenal, 'has_leaky_gut': has_leaky_gut,
    'has_candida': has_candida, 'has_menopause': has_menopause, 'has_osteo': has_osteo,
}

# ==================== MAIN TABS ====================
tab1, tab2, tab3, tab4 = st.tabs(TRANSLATIONS[get_lang()]["tabs"])

# ============================================================
# TAB 1 — FOOD ASSISTANT
# ============================================================
with tab1:
    col_l, = st.columns([1])  # full width

    with col_l:
        st.markdown(f"<h3 style='color:#059669;'>{txt('search_hdr')}</h3>", unsafe_allow_html=True)

        # Food group filter — translated when SK
        FOOD_GROUP_SK = {
            "American Indian":       "Americká indiánska kuchyňa",
            "Baby Foods":            "Detská výživa",
            "Baked Foods":           "Pečivo a pekárenské výrobky",
            "Beans and Lentils":     "Fazuľa a šošovica",
            "Beverages":             "Nápoje",
            "Breakfast Cereals":     "Raňajkové cereálie",
            "Dairy and Egg Products":"Mliečne výrobky a vajcia",
            "Dairy and Egg Products ":"Mliečne výrobky a vajcia",
            "Fast Foods":            "Rýchle občerstvenie",
            "Fats and Oils":         "Tuky a oleje",
            "Fish":                  "Ryby",
            "Fruits":                "Ovocie",
            "Grains and Pasta":      "Obilniny a cestoviny",
            "Meats":                 "Mäso",
            "Nuts and Seeds":        "Orechy a semienka",
            "Prepared Meals":        "Hotové jedlá",
            "Restaurant Foods":      "Reštauračné jedlá",
            "Snacks":                "Snacky",
            "Soups and Sauces":      "Polievky a omáčky",
            "Spices and Herbs":      "Koreniny a bylinky",
            "Sweets":                "Sladkosti",
            "Vegetables":            "Zelenina",
        }

        def translate_group(en_name):
            if get_lang() == "SK":
                return FOOD_GROUP_SK.get(en_name.strip(), en_name)
            return en_name

        raw_groups = sorted(df['Food Group'].dropna().unique().tolist()) if 'Food Group' in df.columns else []
        # Build display list (translated) and a map back to original EN name
        group_display = [txt("all_groups")] + [translate_group(g) for g in raw_groups]
        group_en_map  = {translate_group(g): g for g in raw_groups}

        selected_group_display = st.selectbox(txt("food_group_filter"), group_display)
        # Resolve back to EN for filtering
        selected_group = group_en_map.get(selected_group_display, None)  # None = all

        search_query = st.text_input(txt("search_lbl"), "", placeholder="Napr. Ovsene vlocky / Oats...")

        if search_query:
            mask = (
                df['name_en'].str.contains(search_query, case=False, na=False) |
                df['name_sk'].str.contains(search_query, case=False, na=False)
            )
            if selected_group is not None and 'Food Group' in df.columns:
                mask = mask & (df['Food Group'].str.strip() == selected_group.strip())
            results = df[mask]

            if not results.empty:
                # Show food name in current language only
                if get_lang() == "SK":
                    food_options = results['name_sk'].tolist()
                else:
                    food_options = results['name_en'].tolist()
                selected_option = st.selectbox(txt("select_food"), food_options)
                selected_idx = food_options.index(selected_option)
                fd = results.iloc[selected_idx]
                # Always store bilingual label internally
                stored_label = f"{fd['name_en']} / {fd['name_sk']}"

                grams = st.number_input(txt("grams"), min_value=1, value=100, step=10)
                r = grams / 100.0

                # Macros
                cal   = round(fd.get('Calories', 0) * r, 1)
                prot  = round(fd.get('Protein (g)', 0) * r, 1)
                fat   = round(fd.get('Fat (g)', 0) * r, 1)
                carbs = round(fd.get('Net-Carbs (g)', 0) * r, 1)
                sugar = round(fd.get('Sugars (g)', 0) * r, 1)
                fiber = round(fd.get('Fiber (g)', 0) * r, 1)
                # Micros — use pd.to_numeric with fillna(0) to handle NaN safely
                def _n(val, decimals=1):
                    import math
                    try:
                        v = float(val)
                        return round(0.0 if math.isnan(v) else v, decimals)
                    except (TypeError, ValueError):
                        return 0.0

                iron  = _n(fd.get('Iron, Fe (mg)', 0) * r, 2)
                zinc  = _n(fd.get('Zinc, Zn (mg)', 0) * r, 2)
                vitd  = _n(fd.get('Vitamin D (mcg)', 0) * r, 2)
                mag   = _n(fd.get('Magnesium (mg)', 0) * r, 1)
                calc  = _n(fd.get('Calcium (mg)', 0) * r, 1)
                omega3= _n(fd.get('Omega 3s (mg)', 0) * r, 0)
                sel   = _n(fd.get('Selenium, Se (mcg)', 0) * r, 1)
                vitc  = _n(fd.get('Vitamin C (mg)', 0) * r, 1)
                b12   = _n(fd.get('Vitamin B-12 (mcg)', 0) * r, 2)
                potass= _n(fd.get('Potassium, K (mg)', 0) * r, 0)
                sodium= _n(fd.get('Sodium (mg)', 0) * r, 0)
                caff  = _n(fd.get('Caffeine (mg)', 0) * r, 1)

                # ── Build nutrition card HTML in Python, then render ──
                food_group_label = fd.get('Food Group', '')

                macro_items = [
                    (txt("prot"),  f"{prot} g"),
                    (txt("carbs"), f"{carbs} g"),
                    (txt("fat"),   f"{fat} g"),
                    (txt("fiber"), f"{fiber} g"),
                ]
                macro_html = ""
                for lbl, val in macro_items:
                    macro_html += (
                        f'<div style="background:rgba(45,212,191,0.06);border:1px solid rgba(45,212,191,0.10);'
                        f'border-radius:14px;padding:12px;text-align:center;">'
                        f'<div style="font-size:1.4rem;font-weight:800;color:#2dd4bf;">{val}</div>'
                        f'<div style="font-size:0.72rem;color:#6b8a85;margin-top:3px;text-transform:uppercase;letter-spacing:0.5px;">{lbl}</div>'
                        f'</div>'
                    )

                micro_items = [
                    ("🩸 Iron",   f"{iron} mg"),
                    ("⚡ Mg",     f"{mag} mg"),
                    ("🦴 Ca",     f"{calc} mg"),
                    ("☀️ Vit D",  f"{vitd} mcg"),
                    ("🐟 Ω-3",   f"{int(omega3)} mg"),
                    ("🦋 Zn",    f"{zinc} mg"),
                    ("🔬 Se",    f"{sel} mcg"),
                    ("🍊 Vit C", f"{vitc} mg"),
                    ("💊 B12",   f"{b12} mcg"),
                    ("🫀 K",     f"{int(potass)} mg"),
                    ("🧂 Na",    f"{int(sodium)} mg"),
                ]
                if caff > 0:
                    micro_items.append(("☕ Caff", f"{caff} mg"))

                micro_html = ""
                for lbl, val in micro_items:
                    micro_html += (
                        f'<div style="background:rgba(20,32,31,0.9);border:1px solid rgba(45,212,191,0.09);'
                        f'border-radius:12px;padding:9px 10px;text-align:center;">'
                        f'<div style="font-size:1.05rem;font-weight:700;color:#2dd4bf;">{val}</div>'
                        f'<div style="font-size:0.7rem;color:#6b8a85;margin-top:2px;">{lbl}</div>'
                        f'</div>'
                    )

                card_html = (
                    f'<div style="background:linear-gradient(135deg,rgba(15,30,28,0.95),rgba(10,22,20,0.98));'
                    f'border:1px solid rgba(45,212,191,0.18);border-radius:22px;'
                    f'padding:24px 28px 20px 28px;margin:16px 0 8px 0;box-shadow:0 8px 32px rgba(0,0,0,0.35);">'

                    # Header
                    f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">'
                    f'<div>'
                    f'<div style="font-size:1.35rem;font-weight:800;color:#f0fdfa;letter-spacing:-0.5px;">{fd["name_en"]}</div>'
                    f'<div style="font-size:0.85rem;color:#6b8a85;margin-top:2px;">{fd["name_sk"]} &nbsp;·&nbsp; {food_group_label} &nbsp;·&nbsp; {grams} g</div>'
                    f'</div>'
                    f'<div style="background:linear-gradient(135deg,#0f766e,#14b8a6);border-radius:14px;'
                    f'padding:10px 18px;text-align:center;box-shadow:0 4px 16px rgba(20,184,166,0.25);">'
                    f'<div style="font-size:1.8rem;font-weight:800;color:#fff;line-height:1;">{cal}</div>'
                    f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.75);letter-spacing:1px;text-transform:uppercase;">kcal</div>'
                    f'</div></div>'

                    # Macros grid
                    f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px;">'
                    + macro_html +
                    f'</div>'

                    # Sugar
                    f'<div style="margin-bottom:18px;">'
                    f'<div style="background:rgba(251,113,133,0.08);border:1px solid rgba(251,113,133,0.15);'
                    f'border-radius:12px;padding:10px 18px;text-align:center;">'
                    f'<span style="font-size:1.1rem;font-weight:700;color:#fb7185;">{sugar} g</span>'
                    f'<span style="font-size:0.72rem;color:#6b8a85;margin-left:8px;text-transform:uppercase;">{txt("sugar")}</span>'
                    f'</div></div>'

                    # Micros label
                    f'<div style="font-size:0.75rem;font-weight:700;color:#6b8a85;letter-spacing:1.5px;'
                    f'text-transform:uppercase;margin-bottom:10px;">🔬 {txt("micros_hdr")}</div>'

                    # Micros grid
                    f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;">'
                    + micro_html +
                    f'</div></div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

                # Warnings
                full_name = f"{fd['name_en']} {fd['name_sk']}"
                warnings = detect_food_warnings(full_name, health_conditions)
                if warnings:
                    st.markdown(txt("warnings_hdr"))
                    for w in warnings:
                        st.warning(w)
                if (has_pcos or has_db2 or has_nafld or has_candida) and sugar > 10:
                    st.error(txt("warn_sugar"))

                if st.button(txt("add_btn"), use_container_width=True):
                    st.session_state.daily_meals.append({
                        "Jedlo": stored_label, "Gramy": grams,
                        "Kalórie": cal, "Bielkoviny": prot, "Tuky": fat,
                        "Čisté Sacharidy": carbs, "Cukor": sugar, "Vláknina": fiber,
                        "Železo": iron, "Zinok": zinc, "Vitamín D": vitd,
                        "Horčík": mag, "Vápnik": calc, "Omega3": omega3,
                        "Selén": sel, "Rizikové": 1 if warnings else 0,
                    })
                    st.success(txt("add_success"))
            else:
                st.info(txt("not_found"))

    # ---- Encyclopedia — full width at the bottom of Tab 1 ----
    st.divider()
    st.markdown(f"""
<div style="margin-bottom:8px;">
  <span style="font-size:0.75rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:#6b8a85;">
    💡 {"Encyklopédia metabolizmu" if get_lang()=="SK" else "Metabolism Encyclopedia"}
  </span>
  <div style="font-size:1.5rem; font-weight:800; color:#f0fdfa; margin-top:4px;">
    {"Tvoje diagnózy — čo to znamená pre tvoje telo" if get_lang()=="SK" else "Your conditions — what they mean for your body"}
  </div>
</div>
""", unsafe_allow_html=True)

    # Icon map for each condition
    ENC_ICONS = {
        "enc_pcos_t": "🌾", "enc_hashi_t": "🦋", "enc_hyper_t": "🔥",
        "enc_anemia_t": "🩸", "enc_gout_t": "🦴", "enc_nafld_t": "🍏",
        "enc_menopause_t": "🌸", "enc_osteo_t": "🦴", "enc_adrenal_t": "⚡",
    }
    ENC_COLORS = {
        "enc_pcos_t":    ("#14b8a6", "#0f766e"),
        "enc_hashi_t":   ("#818cf8", "#4f46e5"),
        "enc_hyper_t":   ("#fb923c", "#c2410c"),
        "enc_anemia_t":  ("#f43f5e", "#be123c"),
        "enc_gout_t":    ("#a78bfa", "#7c3aed"),
        "enc_nafld_t":   ("#4ade80", "#15803d"),
        "enc_menopause_t":("#f472b6","#be185d"),
        "enc_osteo_t":   ("#fbbf24", "#b45309"),
        "enc_adrenal_t": ("#38bdf8", "#0369a1"),
    }

    enc_items = []
    if has_pcos or has_db2:    enc_items.append(("enc_pcos_t",     "enc_pcos_b"))
    if has_hashi:              enc_items.append(("enc_hashi_t",    "enc_hashi_b"))
    if has_hyper:              enc_items.append(("enc_hyper_t",    "enc_hyper_b"))
    if has_anemia:             enc_items.append(("enc_anemia_t",   "enc_anemia_b"))
    if has_gout:               enc_items.append(("enc_gout_t",     "enc_gout_b"))
    if has_nafld:              enc_items.append(("enc_nafld_t",    "enc_nafld_b"))
    if has_menopause:          enc_items.append(("enc_menopause_t","enc_menopause_b"))
    if has_osteo:              enc_items.append(("enc_osteo_t",    "enc_osteo_b"))
    if has_adrenal:            enc_items.append(("enc_adrenal_t",  "enc_adrenal_b"))

    if not enc_items:
        st.markdown("""
<div style="background:rgba(20,184,166,0.06); border:1px solid rgba(45,212,191,0.12);
     border-radius:16px; padding:20px 24px; color:#9fb7b3; font-size:0.95rem;">
  ✅ {"Žiadne aktívne diagnózy. Vyber diagnózy v ľavom paneli." if get_lang()=="SK" else "No active conditions. Select conditions in the left panel."}
</div>""", unsafe_allow_html=True)
    else:
        cols_per_row = 3
        for row_start in range(0, len(enc_items), cols_per_row):
            row_items = enc_items[row_start:row_start + cols_per_row]
            enc_cols = st.columns(cols_per_row)
            for i, (t_key, b_key) in enumerate(row_items):
                icon = ENC_ICONS.get(t_key, "💡")
                c1, c2 = ENC_COLORS.get(t_key, ("#14b8a6", "#0f766e"))
                title = txt(t_key)
                body  = txt(b_key)
                with enc_cols[i]:
                    st.markdown(f"""
<div style="
    background: linear-gradient(135deg, rgba(15,28,26,0.95), rgba(10,20,18,0.98));
    border: 1px solid rgba(45,212,191,0.12);
    border-top: 3px solid {c1};
    border-radius: 18px;
    padding: 20px 22px;
    margin-bottom: 12px;
    min-height: 140px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.28);
    transition: all 0.3s ease;
">
  <div style="font-size:2rem; margin-bottom:8px;">{icon}</div>
  <div style="font-size:1rem; font-weight:700; color:#f0fdfa; margin-bottom:8px;">{title}</div>
  <div style="font-size:0.85rem; color:#9fb7b3; line-height:1.6;">{body}</div>
</div>""", unsafe_allow_html=True)

# ============================================================
# TAB 2 — DAILY DIARY
# ============================================================
with tab2:
    st.markdown(f"<h3 style='color:#059669;'>{txt('diary_hdr')}</h3>", unsafe_allow_html=True)

    has_meals = bool(st.session_state.daily_meals)
    if has_meals:
        df_today = pd.DataFrame(st.session_state.daily_meals)

        # Compact table: food name + key macros + gram edit + delete
        # Header
        h = st.columns([5, 1.4, 1, 1, 1, 1, 0.5])
        for col, label in zip(h, ["JEDLO", "g ✏️", "kcal", "P(g)", "C(g)", "F(g)", ""]):
            col.markdown(f"<span style='font-size:0.72rem;color:#6b8a85;font-weight:700;letter-spacing:1px;'>{label}</span>", unsafe_allow_html=True)

        for i, row in df_today.iterrows():
            c = st.columns([5, 1.4, 1, 1, 1, 1, 0.5])

            # Show name in current language
            parts = row['Jedlo'].split('/')
            if get_lang() == "SK" and len(parts) > 1:
                food_display = parts[1].strip()[:45]
            else:
                food_display = parts[0].strip()[:45]

            c[0].markdown(f"<span style='font-size:0.83rem;color:#ecfeff;'>{food_display}</span>", unsafe_allow_html=True)

            # Editable grams — recalculate macros on change
            with c[1]:
                new_grams = st.number_input(
                    "", min_value=1, value=int(row['Gramy']), step=5,
                    key=f"grams_{i}", label_visibility="collapsed"
                )
                if new_grams != int(row['Gramy']):
                    # Find original food in df to recalculate
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
                            "Kalórie":        round(fd2.get('Calories', 0) * r2, 1),
                            "Bielkoviny":     round(fd2.get('Protein (g)', 0) * r2, 1),
                            "Tuky":           round(fd2.get('Fat (g)', 0) * r2, 1),
                            "Čisté Sacharidy":round(fd2.get('Net-Carbs (g)', 0) * r2, 1),
                            "Cukor":          round(fd2.get('Sugars (g)', 0) * r2, 1),
                            "Vláknina":       round(fd2.get('Fiber (g)', 0) * r2, 1),
                            "Železo":         round(fd2.get('Iron, Fe (mg)', 0) * r2, 2),
                            "Zinok":          round(fd2.get('Zinc, Zn (mg)', 0) * r2, 2),
                            "Vitamín D":      round(fd2.get('Vitamin D (mcg)', 0) * r2, 2),
                            "Horčík":         round(float(fd2.get('Magnesium (mg)', 0) or 0) * r2, 1),
                            "Vápnik":         round(float(fd2.get('Calcium (mg)', 0) or 0) * r2, 1),
                            "Omega3":         round(float(fd2.get('Omega 3s (mg)', 0) or 0) * r2, 0),
                            "Selén":          round(float(fd2.get('Selenium, Se (mcg)', 0) or 0) * r2, 1),
                        })
                        st.rerun()

            # Recalculate display values from current session state (after possible edit)
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
            "carbs":    round(df_today["Čisté Sacharidy"].sum(), 1),
            "protein":  round(df_today["Bielkoviny"].sum(), 1),
            "fiber":    round(df_today["Vláknina"].sum(), 1),
            "sugar":    round(df_today["Cukor"].sum(), 1),
            "iron":     round(df_today["Železo"].sum(), 2),
            "zinc":     round(df_today["Zinok"].sum(), 2),
            "vitd":     round(df_today["Vitamín D"].sum(), 2),
            "magnesium":round(df_today["Horčík"].sum(), 1),
            "calcium":  round(df_today["Vápnik"].sum(), 1),
            "omega3":   round(df_today["Omega3"].sum(), 0),
            "selenium": round(df_today["Selén"].sum(), 1),
            "risks":    round(df_today["Rizikové"].sum(), 0),
        }
    else:
        st.info(txt("no_meals"))
        totals = {k: 0 for k in ["calories","carbs","protein","fiber","sugar","iron","zinc",
                                  "vitd","magnesium","calcium","omega3","selenium","risks"]}

    # Clear day button
    if has_meals:
        if st.button(txt("clear_day")):
            st.session_state.daily_meals = []
            st.rerun()

    # ---- Macro metrics + progress bars ----
    st.markdown(txt("status"))
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(txt("cal"),   f"{totals['calories']} kcal")
    m2.metric(txt("prot"),  f"{totals['protein']} g")
    m3.metric(txt("carbs"), f"{totals['carbs']} g")
    m4.metric(txt("fiber"), f"{totals['fiber']} g")

    pof = txt("progress_of")
    # Macro + micro progress bars — labeled with name, value, target and %
    lang = get_lang()
    bars_html = (
        '<div style="background:rgba(15,25,23,0.7);border:1px solid rgba(45,212,191,0.10);'
        'border-radius:18px;padding:20px 24px;margin:12px 0;">'
        '<div style="font-size:0.7rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
        'color:#6b8a85;margin-bottom:16px;">📊 ' +
        ("Denný pokrok" if lang == "SK" else "Daily Progress") +
        '</div>'
    )
    bars_html += progress_bar_html(totals['calories'], target_cal,    "kcal", "🔥 " + ("Kalórie"    if lang=="SK" else "Calories"))
    bars_html += progress_bar_html(totals['protein'],  target_protein,"g",    "💪 " + ("Bielkoviny" if lang=="SK" else "Protein"))
    bars_html += progress_bar_html(totals['carbs'],    target_carbs,  "g",    "🌾 " + ("Sacharidy"  if lang=="SK" else "Net Carbs"))
    bars_html += progress_bar_html(totals['fiber'],    25,            "g",    "🥦 " + ("Vláknina"   if lang=="SK" else "Fiber"))
    bars_html += progress_bar_html(totals['iron'],     18,            "mg",   "🩸 " + ("Železo"     if lang=="SK" else "Iron"))
    bars_html += progress_bar_html(totals['zinc'],     12,            "mg",   "🦋 " + ("Zinok"      if lang=="SK" else "Zinc"))
    bars_html += progress_bar_html(totals['magnesium'],350,           "mg",   "⚡ " + ("Horčík"     if lang=="SK" else "Magnesium"))
    bars_html += progress_bar_html(totals['calcium'],  1000,          "mg",   "🦴 " + ("Vápnik"     if lang=="SK" else "Calcium"))
    bars_html += progress_bar_html(totals['vitd'],     15,            "mcg",  "☀️ " + ("Vitamín D"  if lang=="SK" else "Vitamin D"))
    bars_html += progress_bar_html(int(totals['omega3'] or 0), 1500,       "mg",   "🐟 " + ("Omega-3"    if lang=="SK" else "Omega-3"))
    bars_html += '</div>'
    st.markdown(bars_html, unsafe_allow_html=True)

    # ---- Nutrient score ----
    targets_for_score = {"cal": target_cal, "prot": target_protein}
    ns = nutrient_score(totals, targets_for_score)
    ns_color = "#10b981" if ns >= 70 else ("#f59e0b" if ns >= 40 else "#fb7185")
    st.markdown(
        f"<div style='text-align:center;margin:10px 0;'>"
        f"<span style='font-size:2.5rem;font-weight:800;color:{ns_color};'>{ns}/100</span>"
        f"<div style='color:#9fb7b3;font-size:0.9rem;'>{txt('nutrient_score')}</div></div>",
        unsafe_allow_html=True
    )

    st.divider()

    # ---- Water tracker ----
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
    st.markdown(progress_bar_html(water_total, target_water, "L", "💧 " + ("Voda" if get_lang()=="SK" else "Water")), unsafe_allow_html=True)

    st.divider()

    # ---- Personalized feedback ----
    st.markdown(f"<h4>{txt('feedback_hdr')}</h4>", unsafe_allow_html=True)
    feedbacks = []

    if has_pcos or has_db2:
        feedbacks.append(txt("fb_pcos_fiber_low").format(fiber=totals["fiber"]) if totals["fiber"] < 25 else txt("fb_pcos_fiber_ok"))
    if (has_pcos or has_db2 or has_nafld or has_candida) and totals["sugar"] > 35:
        feedbacks.append(txt("fb_pcos_sugar_high").format(sugar=totals["sugar"]))
    if has_anemia:
        feedbacks.append(txt("fb_anemia_iron_low").format(iron=totals["iron"]) if totals["iron"] < 15 else txt("fb_anemia_iron_ok"))
    if has_hashi:
        feedbacks.append(txt("fb_hashi_zinc_low").format(zinc=totals["zinc"]) if totals["zinc"] < 11 else txt("fb_hashi_zinc_ok"))
        feedbacks.append(txt("fb_hashi_selenium_low").format(sel=totals["selenium"]) if totals["selenium"] < 55 else txt("fb_hashi_selenium_ok"))
        if totals["risks"] > 0:
            feedbacks.append(txt("fb_hashi_risks").format(risks=int(totals["risks"])))
    if has_celiakia and totals["risks"] > 0:
        feedbacks.append(txt("fb_celiakia_risk"))
    if has_gastritis and totals["risks"] > 0:
        feedbacks.append(txt("fb_gastritis_risk"))
    if has_gout and totals["risks"] > 0:
        feedbacks.append(txt("fb_gout_risk"))
    # Vitamin D
    feedbacks.append(txt("fb_vitd_low").format(vitd=totals["vitd"]) if totals["vitd"] < 10 else txt("fb_vitd_ok"))
    # Magnesium
    feedbacks.append(txt("fb_magnesium_low").format(mag=totals["magnesium"]) if totals["magnesium"] < 200 else txt("fb_magnesium_ok"))
    # Calcium — only when relevant condition active
    if has_osteo or has_menopause:
        feedbacks.append(txt("fb_calcium_low").format(cal=totals["calcium"]) if totals["calcium"] < 700 else txt("fb_calcium_ok"))
    # Omega-3
    feedbacks.append(txt("fb_omega3_low").format(o3=int(totals["omega3"] or 0)) if (totals["omega3"] or 0) < 500 else txt("fb_omega3_ok"))

    # Water
    water_upper = round(max(4.5, target_water + 1.5), 1)
    if water_total < target_water * 0.8:
        feedbacks.append(txt("fb_water_low").format(water=round(water_total,1), target=target_water))
    elif water_total > water_upper:
        feedbacks.append(txt("fb_water_high").format(water=water_total, limit=water_upper))
    else:
        feedbacks.append(txt("fb_water_ok"))

    if not feedbacks:
        feedbacks.append(txt("fb_perfect"))

    # Render all feedbacks as consistent custom cards — no random Streamlit colors
    fb_html = '<div style="display:flex;flex-direction:column;gap:8px;margin:4px 0;">'
    for fb in feedbacks:
        if any(x in fb for x in ["🚨"]):
            left = "#fb7185"; bg = "rgba(251,113,133,0.07)"; border = "rgba(251,113,133,0.25)"
        elif any(x in fb for x in ["⚠️"]):
            left = "#f59e0b"; bg = "rgba(245,158,11,0.07)"; border = "rgba(245,158,11,0.22)"
        elif any(x in fb for x in ["✨", "💪", "☀️", "�", "�"]) and "doplniť" not in fb and "boost" not in fb and "low" not in fb.lower() and "nízky" not in fb.lower() and "piješ príliš" not in fb and "drinking too" not in fb:
            left = "#10b981"; bg = "rgba(16,185,129,0.07)"; border = "rgba(16,185,129,0.20)"
        else:
            left = "#2dd4bf"; bg = "rgba(45,212,191,0.05)"; border = "rgba(45,212,191,0.15)"
        fb_html += (
            f'<div style="background:{bg};border:1px solid {border};border-left:3px solid {left};'
            f'border-radius:12px;padding:12px 16px;font-size:0.88rem;color:#d1faf5;line-height:1.6;">'
            f'{fb}</div>'
        )
    fb_html += '</div>'
    st.markdown(fb_html, unsafe_allow_html=True)

    st.divider()

    # ---- Metabolism status — immersive card ----
    metab_score, metab_level = get_metabolism_status(
        totals["calories"], target_cal, totals["protein"], target_protein,
        totals["fiber"], has_pcos, has_hashi, totals["iron"], totals["zinc"],
        totals["risks"], water_total, target_water
    )

    _METAB = {
        "excellent": {
            "emoji": "🟢", "icon": "✦",
            "title_sk": "Metabolizmus v top forme",       "title_en": "Metabolism in top shape",
            "sub_sk":   "Dnes si dal/a telu presne to, čo potrebuje. Výborná práca.",
            "sub_en":   "You gave your body exactly what it needs today. Outstanding.",
            "grad": "linear-gradient(135deg, rgba(16,185,129,0.18), rgba(5,150,105,0.08))",
            "border": "#10b981", "score_color": "#10b981",
        },
        "good": {
            "emoji": "🔵", "icon": "◈",
            "title_sk": "Dobrý deň pre tvoje telo",       "title_en": "A good day for your body",
            "sub_sk":   "Väčšina metrík je na cieli. Pár malých úprav a bude to perfektné.",
            "sub_en":   "Most metrics are on target. A few small tweaks and it'll be perfect.",
            "grad": "linear-gradient(135deg, rgba(59,130,246,0.18), rgba(37,99,235,0.08))",
            "border": "#3b82f6", "score_color": "#60a5fa",
        },
        "warning": {
            "emoji": "🟡", "icon": "⚠",
            "title_sk": "Metabolizmus potrebuje pozornosť", "title_en": "Metabolism needs attention",
            "sub_sk":   "Niektoré živiny sú mimo cieľa. Pozri si spätné väzby vyššie.",
            "sub_en":   "Some nutrients are off target. Check the feedback above.",
            "grad": "linear-gradient(135deg, rgba(245,158,11,0.18), rgba(217,119,6,0.08))",
            "border": "#f59e0b", "score_color": "#fbbf24",
        },
        "critical": {
            "emoji": "🔴", "icon": "✕",
            "title_sk": "Kritický stav — konaj hneď",     "title_en": "Critical — act now",
            "sub_sk":   "Tvoj príjem dnes výrazne zaostáva za potrebami tela. Uprav jedálniček.",
            "sub_en":   "Your intake today is significantly below your body's needs. Adjust your diet.",
            "grad": "linear-gradient(135deg, rgba(251,113,133,0.18), rgba(225,29,72,0.08))",
            "border": "#fb7185", "score_color": "#fb7185",
        },
        "neutral": {
            "emoji": "⚪", "icon": "○",
            "title_sk": "Neutrálny deň",                  "title_en": "Neutral day",
            "sub_sk":   "Nič zlé, ale ani nič výnimočné. Zajtra to zlepši.",
            "sub_en":   "Nothing bad, but nothing exceptional. Do better tomorrow.",
            "grad": "linear-gradient(135deg, rgba(107,138,133,0.14), rgba(75,85,99,0.08))",
            "border": "#6b8a85", "score_color": "#9fb7b3",
        },
        "empty": {
            "emoji": "⚪", "icon": "◌",
            "title_sk": "Zatiaľ žiadne jedlo",            "title_en": "No food logged yet",
            "sub_sk":   "Pridaj prvé jedlo do denníka a skóre sa začne počítať.",
            "sub_en":   "Add your first meal to the diary and the score will start calculating.",
            "grad": "linear-gradient(135deg, rgba(107,138,133,0.10), rgba(75,85,99,0.05))",
            "border": "#4b5563", "score_color": "#6b8a85",
        },
    }
    m = _METAB[metab_level]
    lang = get_lang()
    m_title = m["title_sk"] if lang == "SK" else m["title_en"]
    m_sub   = m["sub_sk"]   if lang == "SK" else m["sub_en"]
    score_label = "Skóre dňa" if lang == "SK" else "Day score"

    # Arc progress ring via SVG
    radius = 44
    circ = 2 * 3.14159 * radius
    dash = round(circ * metab_score / 100, 1)
    gap  = round(circ - dash, 1)

    metab_html = (
        f'<div style="background:{m["grad"]};border:1px solid {m["border"]}33;'
        f'border-left:4px solid {m["border"]};border-radius:22px;'
        f'padding:28px 32px;margin:16px 0;box-shadow:0 8px 32px rgba(0,0,0,0.28);">'

        f'<div style="display:flex;align-items:center;gap:32px;">'

        # SVG ring
        f'<div style="flex-shrink:0;text-align:center;">'
        f'<svg width="110" height="110" viewBox="0 0 110 110">'
        f'<circle cx="55" cy="55" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>'
        f'<circle cx="55" cy="55" r="{radius}" fill="none" stroke="{m["score_color"]}" stroke-width="10"'
        f' stroke-dasharray="{dash} {gap}" stroke-dashoffset="{round(circ*0.25,1)}"'
        f' stroke-linecap="round" style="filter:drop-shadow(0 0 6px {m["score_color"]}88);"/>'
        f'<text x="55" y="50" text-anchor="middle" fill="{m["score_color"]}" '
        f'font-size="22" font-weight="800" font-family="Inter,sans-serif">{metab_score}</text>'
        f'<text x="55" y="66" text-anchor="middle" fill="#6b8a85" '
        f'font-size="9" font-family="Inter,sans-serif" letter-spacing="1">{score_label.upper()}</text>'
        f'</svg>'
        f'</div>'

        # Text block
        f'<div style="flex:1;">'
        f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
        f'color:{m["score_color"]};margin-bottom:6px;">🧬 ' +
        ("STAV METABOLIZMU" if lang=="SK" else "METABOLISM STATUS") +
        f'</div>'
        f'<div style="font-size:1.6rem;font-weight:800;color:#f0fdfa;line-height:1.2;margin-bottom:8px;">'
        f'{m["icon"]} {m_title}</div>'
        f'<div style="font-size:0.92rem;color:#9fb7b3;line-height:1.6;">{m_sub}</div>'
        f'</div>'

        f'</div>'
        f'</div>'
    )
    st.markdown(metab_html, unsafe_allow_html=True)

    st.divider()

    # ---- Symptom tracking ----
    st.markdown(f"<h4>{txt('symptoms_hdr')}</h4>", unsafe_allow_html=True)
    sym_cols = st.columns(3)
    selected_symptoms = []
    with sym_cols[0]:
        st.markdown(txt("sym_gain_fatigue"))
        if st.checkbox(txt("sym_hunger"),   key="hunger"):   selected_symptoms.append("Hunger")
        if st.checkbox(txt("sym_weakness"), key="weakness"): selected_symptoms.append("Weakness")
        if st.checkbox(txt("sym_bloating"), key="bloating"): selected_symptoms.append("Bloating")
    with sym_cols[1]:
        st.markdown(txt("sym_lose_weight"))
        if st.checkbox(txt("sym_palpitations"), key="palpitations"): selected_symptoms.append("Palpitations")
        if st.checkbox(txt("sym_cramps"),       key="cramps"):       selected_symptoms.append("Cramps")
        if st.checkbox(txt("sym_gout_pain"),    key="gout_pain"):    selected_symptoms.append("Gout Pain")
    with sym_cols[2]:
        st.markdown(txt("sym_subjective"))
        energy_score = st.slider(txt("sym_energy"), 1, 10, 7, key="energy")
        sleep_score  = st.slider(txt("sym_sleep"),  1, 10, 7, key="sleep")

    if st.button(txt("save_btn"), use_container_width=True, type="primary"):
        diag_map = {
            "PCOS": has_pcos, "Hashimoto": has_hashi, "Anemia": has_anemia,
            "Celiac": has_celiakia, "Gout": has_gout, "NAFLD": has_nafld,
            "Adrenal": has_adrenal, "Leaky Gut": has_leaky_gut,
            "Candida": has_candida, "Menopause": has_menopause, "Osteoporosis": has_osteo,
        }
        active_diag = [d for d, v in diag_map.items() if v]
        save_history_row({
            "Dátum": str(date.today()),
            "Diagnózy": ", ".join(active_diag) if active_diag else "None",
            "Cieľ": meta_goal,
            "Váha (kg)": weight,
            "Energia": energy_score,
            "Spánok": sleep_score,
            "Kalórie": totals["calories"],
            "Sacharidy (g)": totals["carbs"],
            "Voda (L)": water_total,
            "Symptómy": ", ".join(selected_symptoms) if selected_symptoms else "None",
        })
        st.success(txt("save_success"))

# ============================================================
# TAB 3 — LONG-TERM PROGRESS
# ============================================================
with tab3:
    lang = get_lang()
    hist = load_history()

    # ── Page header ─────────────────────────────────────────
    st.markdown(f"""
<div style="margin-bottom:28px;">
  <div style="font-size:0.7rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;
       color:#6b8a85;margin-bottom:8px;">
    {"📈 DLHODOBÝ VÝVOJ" if lang=="SK" else "📈 LONG-TERM PROGRESS"}
  </div>
  <div style="font-size:2rem;font-weight:800;color:#f0fdfa;letter-spacing:-0.5px;">
    {"Tvoja cesta v číslach" if lang=="SK" else "Your journey in numbers"}
  </div>
  <div style="font-size:0.88rem;color:#6b8a85;margin-top:6px;">
    {"Každý uložený deň sa zobrazí tu. Sleduj trendy a zlepšuj sa." if lang=="SK"
     else "Every saved day appears here. Track trends and keep improving."}
  </div>
</div>
""", unsafe_allow_html=True)

    if hist.empty:
        st.markdown(f"""
<div style="background:rgba(45,212,191,0.03);border:1.5px dashed rgba(45,212,191,0.15);
     border-radius:22px;padding:60px 40px;text-align:center;">
  <div style="font-size:3rem;margin-bottom:14px;">📭</div>
  <div style="font-size:1.1rem;font-weight:700;color:#9fb7b3;margin-bottom:8px;">
    {"Zatiaľ žiadne záznamy" if lang=="SK" else "No records yet"}
  </div>
  <div style="font-size:0.85rem;color:#6b8a85;">
    {"Ulož prvý deň v záložke Dnešný denník → tlačidlo Ukončiť a uložiť deň." if lang=="SK"
     else "Save your first day in the Daily Diary tab → Finish and Save Day button."}
  </div>
</div>""", unsafe_allow_html=True)

    else:
        # ── Compute stats ────────────────────────────────────
        days    = len(hist)
        avg_cal = round(hist["Kalórie"].mean(), 0)   if "Kalórie"   in hist.columns else None
        avg_w   = round(hist["Váha (kg)"].mean(), 1) if "Váha (kg)" in hist.columns else None
        avg_e   = round(hist["Energia"].mean(), 1)   if "Energia"   in hist.columns else None
        avg_sl  = round(hist["Spánok"].mean(), 1)    if "Spánok"    in hist.columns else None

        # Trend arrows (compare last entry vs first)
        def trend(col):
            if col not in hist.columns or len(hist) < 2: return ""
            diff = hist[col].iloc[-1] - hist[col].iloc[0]
            if diff > 0:  return '<span style="color:#10b981;font-size:0.8rem;"> ▲</span>'
            if diff < 0:  return '<span style="color:#fb7185;font-size:0.8rem;"> ▼</span>'
            return '<span style="color:#6b8a85;font-size:0.8rem;"> —</span>'

        # ── Stat cards ───────────────────────────────────────
        stat_items = [
            ("📅", str(days),              "",          "Dní" if lang=="SK" else "Days"),
            ("🔥", f"{int(avg_cal or 0)}", trend("Kalórie"),   "Ø kcal"),
            ("⚖️", f"{avg_w or '—'} kg",  trend("Váha (kg)"), "Ø " + ("váha" if lang=="SK" else "weight")),
            ("⚡", f"{avg_e or '—'}/10",  trend("Energia"),    "Ø " + ("energia" if lang=="SK" else "energy")),
            ("😴", f"{avg_sl or '—'}/10", trend("Spánok"),     "Ø " + ("spánok" if lang=="SK" else "sleep")),
        ]
        cards_html = (
            '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:32px;">'
        )
        for icon, val, tr, lbl in stat_items:
            cards_html += (
                f'<div style="background:linear-gradient(135deg,rgba(15,28,26,0.95),rgba(10,20,18,0.98));'
                f'border:1px solid rgba(45,212,191,0.12);border-radius:18px;padding:20px 12px;text-align:center;'
                f'box-shadow:0 4px 20px rgba(0,0,0,0.22);">'
                f'<div style="font-size:1.6rem;margin-bottom:8px;">{icon}</div>'
                f'<div style="font-size:1.25rem;font-weight:800;color:#2dd4bf;line-height:1;">{val}{tr}</div>'
                f'<div style="font-size:0.68rem;color:#6b8a85;margin-top:5px;text-transform:uppercase;'
                f'letter-spacing:1px;">{lbl}</div>'
                f'</div>'
            )
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

        # ── Weight chart — full width with styled wrapper ────
        if "Váha (kg)" in hist.columns and "Dátum" in hist.columns:
            st.markdown(
                '<div style="background:rgba(15,28,26,0.7);border:1px solid rgba(45,212,191,0.10);'
                'border-radius:18px;padding:20px 20px 8px 20px;margin-bottom:16px;">'
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
                'color:#6b8a85;margin-bottom:12px;">⚖️ ' +
                ("TELESNÁ HMOTNOSŤ (kg)" if lang=="SK" else "BODY WEIGHT (kg)") +
                '</div>',
                unsafe_allow_html=True
            )
            w_data = (hist[["Dátum","Váha (kg)"]].dropna()
                      .rename(columns={"Dátum":"index","Váha (kg)":"kg"})
                      .set_index("index"))
            st.line_chart(w_data, height=180, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Calories + Energy side by side ───────────────────
        col_a, col_b = st.columns(2, gap="large")

        with col_a:
            if "Kalórie" in hist.columns:
                st.markdown(
                    '<div style="background:rgba(15,28,26,0.7);border:1px solid rgba(45,212,191,0.10);'
                    'border-radius:18px;padding:20px 20px 8px 20px;">'
                    '<div style="font-size:0.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
                    'color:#6b8a85;margin-bottom:12px;">🔥 ' +
                    ("KALÓRIE / DEŇ (kcal)" if lang=="SK" else "CALORIES / DAY (kcal)") +
                    '</div>',
                    unsafe_allow_html=True
                )
                c_data = (hist[["Dátum","Kalórie"]].dropna()
                          .rename(columns={"Dátum":"index","Kalórie":"kcal"})
                          .set_index("index"))
                st.bar_chart(c_data, height=200, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            if "Energia" in hist.columns and "Spánok" in hist.columns:
                st.markdown(
                    '<div style="background:rgba(15,28,26,0.7);border:1px solid rgba(45,212,191,0.10);'
                    'border-radius:18px;padding:20px 20px 8px 20px;">'
                    '<div style="font-size:0.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
                    'color:#6b8a85;margin-bottom:12px;">⚡ ' +
                    ("ENERGIA & SPÁNOK (1–10)" if lang=="SK" else "ENERGY & SLEEP (1–10)") +
                    '</div>',
                    unsafe_allow_html=True
                )
                es_data = hist[["Dátum","Energia","Spánok"]].dropna().set_index("Dátum")
                st.line_chart(es_data, height=200, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # ── All entries — scrollable cards with delete ───────
        st.markdown(
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
            'color:#6b8a85;margin:24px 0 12px 0;">🗓️ ' +
            ("ZÁZNAMY" if lang=="SK" else "ENTRIES") + '</div>',
            unsafe_allow_html=True
        )

        # Load fresh so deletes reflect immediately
        hist_all = load_history().iloc[::-1].reset_index(drop=True)  # newest first

        for i, row in hist_all.iterrows():
            e_val  = row.get("Energia","—")
            sl_val = row.get("Spánok","—")
            kcal   = row.get("Kalórie","—")
            w_val  = row.get("Váha (kg)","—")
            diag   = str(row.get("Diagnózy","")).strip()
            if not diag or diag in ("nan","None","Žiadne","None"): diag = ""
            goal   = str(row.get("Cieľ","")).strip()

            card_col, del_col = st.columns([11, 1])
            with card_col:
                st.markdown(
                    f'<div style="background:rgba(15,28,26,0.85);border:1px solid rgba(45,212,191,0.10);'
                    f'border-left:3px solid rgba(45,212,191,0.35);border-radius:14px;'
                    f'padding:14px 20px;margin-bottom:2px;">'
                    f'<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:5px;">'
                    f'<span style="font-size:1rem;font-weight:700;color:#2dd4bf;">{row.get("Dátum","")}</span>'
                    f'<span style="font-size:0.75rem;color:#6b8a85;">{goal}</span>'
                    f'</div>'
                    f'<div style="display:flex;gap:18px;flex-wrap:wrap;">'
                    f'<span style="font-size:0.82rem;color:#9fb7b3;">⚖️ <b style="color:#ecfeff;">{w_val} kg</b></span>'
                    f'<span style="font-size:0.82rem;color:#9fb7b3;">🔥 <b style="color:#ecfeff;">{kcal} kcal</b></span>'
                    f'<span style="font-size:0.82rem;color:#9fb7b3;">⚡ <b style="color:#ecfeff;">{e_val}/10</b></span>'
                    f'<span style="font-size:0.82rem;color:#9fb7b3;">😴 <b style="color:#ecfeff;">{sl_val}/10</b></span>'
                    + (f'<span style="font-size:0.75rem;color:#6b8a85;">🏷️ {diag}</span>' if diag else '') +
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with del_col:
                if st.button("�️", key=f"hist_del_{i}",
                             help="Odstrániť" if lang=="SK" else "Delete"):
                    # Delete this row from the CSV (match by original index = len-1-i)
                    full = load_history()
                    orig_idx = len(full) - 1 - i
                    full = full.drop(index=orig_idx).reset_index(drop=True)
                    full.to_csv(HISTORY_FILE, index=False)
                    st.rerun()
            st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

# ============================================================
# TAB 4 — SHOPPING CART
# ============================================================
with tab4:
    st.markdown(f"<h3 style='color:#059669;'>🛒 {txt('tabs')[3]}</h3>", unsafe_allow_html=True)

    # (food_sk, food_en, benefit_sk, benefit_en, category, is_fish, is_dairy)
    RECS = [
        ("Tekvicové semienka",  "Pumpkin seeds",    "Zinok",       "Zinc",        "Semienka/Seeds",    False, False),
        ("Hovädzie mäso",       "Beef",             "Železo/B12",  "Iron/B12",    "Mäso/Meat",         False, False),
        ("Špenát",              "Spinach",          "Železo",      "Iron",        "Zelenina/Veg",      False, False),
        ("Hovädzia pečeň",      "Beef liver",       "Železo/B12",  "Iron/B12",    "Mäso/Meat",         False, False),
        ("Chia semienka",       "Chia seeds",       "Vláknina/Ω3", "Fiber/Ω3",   "Semienka/Seeds",    False, False),
        ("Avokádo",             "Avocado",          "Vláknina/K",  "Fiber/K",     "Ovocie/Fruit",      False, False),
        ("Vaječné žĺtka",       "Egg yolks",        "Vitamín D",   "Vitamin D",   "Vajcia/Eggs",       False, False),
        ("Šampiňóny (UV)",      "Mushrooms (UV)",   "Vitamín D",   "Vitamin D",   "Huby/Mushrooms",    False, False),
        ("Lahôdkové droždie",   "Nutritional yeast","B12/Zinok",   "B12/Zinc",    "Doplnky/Suppl.",    False, False),
        ("Kuracie prsia",       "Chicken breast",   "B12/Bielk.",  "B12/Protein", "Hydina/Poultry",    False, False),
        ("Sezamové semienka",   "Sesame seeds",     "Zinok/Vápnik","Zinc/Calcium","Semienka/Seeds",    False, False),
        ("Kešu orechy",         "Cashews",          "Zinok/Mg",    "Zinc/Mg",     "Orechy/Nuts",       False, False),
        ("Cícer",               "Chickpeas",        "Zinok/Vlák.", "Zinc/Fiber",  "Strukoviny/Legumes",False, False),
        ("Šošovica",            "Lentils",          "Železo/Vlák.","Iron/Fiber",  "Strukoviny/Legumes",False, False),
        ("Quinoa",              "Quinoa",           "Železo/Bielk.","Iron/Protein","Obilniny/Grains",  False, False),
        ("Ľanové semienka",     "Flaxseeds",        "Vláknina/Ω3", "Fiber/Ω3",   "Semienka/Seeds",    False, False),
        ("Brokolica",           "Broccoli",         "Vláknina/C",  "Fiber/C",     "Zelenina/Veg",      False, False),
        ("Ovsené vločky",       "Oats",             "Vláknina/Mg", "Fiber/Mg",    "Obilniny/Grains",   False, False),
        ("Para orechy",         "Brazil nuts",      "Selén",       "Selenium",    "Orechy/Nuts",       False, False),
        ("Tmavá čokoláda 85%",  "Dark chocolate 85%","Mg/Železo",  "Mg/Iron",     "Iné/Other",         False, False),
        ("Divoký losos",        "Wild salmon",      "Vitamín D/Ω3","Vitamin D/Ω3","Ryby/Fish",         True,  False),
        ("Sardinky",            "Sardines",         "Vitamín D/Ca","Vitamin D/Ca","Ryby/Fish",         True,  False),
        ("Tresčia pečeň",       "Cod liver",        "Vitamín D/A", "Vitamin D/A", "Ryby/Fish",         True,  False),
        ("Tuniak",              "Tuna",             "B12/Selén",   "B12/Selenium","Ryby/Fish",         True,  False),
        ("Kefír",               "Kefir",            "B12/Probiot.","B12/Probiotics","Mliečne/Dairy",   False, True),
        ("Grécky jogurt",       "Greek yogurt",     "Vápnik/Bielk.","Calcium/Prot.","Mliečne/Dairy",  False, True),
        ("Mandle",              "Almonds",          "Vápnik/Mg",   "Calcium/Mg",  "Orechy/Nuts",       False, False),
        ("Sladké zemiaky",      "Sweet potatoes",   "Vitamín A/K", "Vitamin A/K", "Zelenina/Veg",      False, False),
    ]

    lang = get_lang()
    all_suggestions = []
    for food_sk, food_en, ben_sk, ben_en, cat, is_fish, is_dairy in RECS:
        if is_fish and has_hit: continue
        if is_dairy and (has_hashi or has_celiakia): continue
        food_label = food_sk if lang == "SK" else food_en
        ben_label  = ben_sk  if lang == "SK" else ben_en
        all_suggestions.append((food_label, ben_label, cat))

    if 'shopping_list' not in st.session_state:
        st.session_state.shopping_list = []

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.subheader("Vyber si potraviny" if lang == "SK" else "Select foods")
        for food, benefit, category in all_suggestions:
            checked = st.checkbox(f"**[{category}]** {food} — *{benefit}*", key=f"shop_{food}")
            if checked and food not in st.session_state.shopping_list:
                st.session_state.shopping_list.append(food)
            elif not checked and food in st.session_state.shopping_list:
                st.session_state.shopping_list.remove(food)

    with col_r:
        st.subheader("📋 " + ("Tvoj Nákupný Zoznam" if lang == "SK" else "Your Shopping List"))
        if st.session_state.shopping_list:
            for item in st.session_state.shopping_list:
                st.write(f"✅ {item}")

            # PDF export
            FONT_PATH = "DejaVuSans.ttf"
            if not os.path.isfile(FONT_PATH):
                st.warning("⚠️ Missing DejaVuSans.ttf for PDF export. Add it to the project folder.")
            else:
                pdf = FPDF()
                pdf.add_page()
                pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
                pdf.set_font("DejaVu", size=16)
                title_text = "Nákupný zoznam" if lang == "SK" else "Shopping List"
                pdf.cell(200, 10, txt=title_text, ln=True, align='C')
                pdf.ln(10)
                pdf.set_font("DejaVu", size=12)
                for item in st.session_state.shopping_list:
                    pdf.cell(200, 10, txt=f"- {item}", ln=True)
                st.download_button(
                    label="📥 " + ("Exportovať do PDF" if lang == "SK" else "Export to PDF"),
                    data=pdf.output(dest='S').encode('latin-1', errors='replace'),
                    file_name="shopping_list.pdf",
                    mime="application/pdf",
                )

            if st.button("🗑️ " + ("Vyčistiť košík" if lang == "SK" else "Clear cart")):
                st.session_state.shopping_list = []
                st.rerun()
        else:
            st.info("Košík je prázdny. Vyber si potraviny vľavo." if lang == "SK" else "Cart is empty. Select foods on the left.")
