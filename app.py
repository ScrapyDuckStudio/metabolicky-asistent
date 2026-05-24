import streamlit as st
import pandas as pd
from datetime import date
import os

# --- NASTAVENIE STRÁNKY ---
st.set_page_config(page_title="Metabolický Asistent & Inteligentný Kouč", layout="wide")

HISTORY_FILE = "zdravotna_historia_global.csv"

# --- JAZYKOVÝ SLOVNÍK ---
lang = st.sidebar.radio("🌐 Jazyk / Language", ["SK", "EN"])

TXT = {
    "SK": {
        "title": "🩺 Inteligentný Metabolický & Hormonálny Tracker Pro",
        "profile": "🧬 Krok 1: Zdravotný profil",
        "gain_weight_tendency": "📉 Sklon k priberaniu / Blokácia chudnutia:",
        "pcos": "PCOS (Inzulínová rezistencia)",
        "hashi": "Hashimoto (Spomalený metabolizmus)",
        "db2": "Cukrovka 2. types",
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
        "goals": ["Zdravé chudnutie", "Udržanie váhy & Regenerácia", "Zdravé pribratie"],
        
        "antropo": "👤 Krok 3: Tvoje údaje",
        "weight": "Váha (kg):",
        "height": "Výška (cm):",
        "age": "Vek:",
        "target_info": "🎯 **Optimálne cieľové makrá:**\n* 🔥 **Kalórie:** {cal} kcal\n* 🥩 **Bielkoviny:** {prot} g\n* 🥑 **Tuky:** {fat} g\n* 🌾 **Čisté sacharidy:** {carbs} g\n* 💧 **Pitný režim:** {water:.2f} L",
        
        "tabs": ["🍽️ Potravinový asistent", "📊 Dnešný denník & Diagnostika", "📈 Korelácie & Vývoj", "🛒 Nákupný košík na mieru"],
        "search_hdr": "🔍 Vyhľadať a analyzovať jedlo",
        "search_lbl": "Zadaj názov potraviny (napr. hovädzie, špenát, beef):",
        "select_food": "Vyber presnú potravinu:",
        "grams": "Množstvo v gramoch (g):",
        "analysis": "#### 📊 Nutričná analýza porcie ({g}g):",
        "cal": "Kalórie",
        "prot": "Bielkoviny",
        "carbs": "Sacharidy",
        "fiber": "Vláknina",
        
        "warnings_hdr": "### 🚨 Zdravotné varovania pre toto jedlo:",
        "warn_gluten": "🌾 **LEPOK / GLUTEN:** Riziko zápalu čriev pre celiatika.",
        "warn_milk": "🥛 **Mlieko/Sója:** Možný skrížený strumigén pre štítnu žľazu (Hashimoto).",
        "warn_hit": "⚠️ **Vysoký Histamín:** Pozor na uvoľnenie histamínu u HIT.",
        "warn_gastritis": "🔥 **Iritant žalúdka:** Môže vyvolať pálenie záhy alebo bolesť.",
        "warn_sugar": "🚨 **Vysoký cukor:** Nevhodné pre inzulínovú rezistenciu.",
        "warn_purines": "🥩 **Vysoké puríny:** Riziko záchvatu dny.",
        "warn_oxalates": "🌱 **Vysoké oxaláty:** Podporuje tvorbu obličkových kameňov.",
        "warn_high_fat": "🧈 **Vysoký tuk:** Záťaž pre žlčník a stukovatenú pečeň.",
        
        "add_btn": "➕ Pridať do denného záznamu",
        "add_success": "Jedlo bolo úspešne pridané.",
        "not_found": "Potravina sa v databáze nenašla.",
        
        "diary_hdr": "📊 Denný prehľad a bio-spätná väzba",
        "status": "#### Sumár skonzumovaných živín:",
        "feedback_hdr": "💬 Inteligentné vyhodnotenie dňa",
        "save_btn": "💾 Uzatvoriť a uložiť dnešný deň",
        "save_success": "Deň bol úspešne zapísaný do histórie!",
        "no_meals": "Dnes si zatiaľ nič nezjedol.",
        
        "symptoms_hdr": "🩺 Ako sa dnes cíti tvoje telo?",
        "sym_energy": "Energia (1-10):",
        "sym_sleep": "Kvalita spánku (1-10):",
        "history_hdr": "📈 Analýza dlhodobých trendov a korelácií",
        "history_empty": "História je zatiaľ prázdna. Ulož si prvý deň.",
        "superfoods_hdr": "🛒 Odporúčaný nákupný zoznam pre tvoje telo",
        "superfoods_desc": "Tieto potraviny aktívne pomáhajú liečiť tvoje vybrané symptómy a diagnózy:",
        "db_status_ok": "✅ Databáza potravín je aktívna."
    },
    "EN": {
        "title": "🩺 Smart Metabolic & Hormonal Tracker Pro",
        "profile": "🧬 Step 1: Health Profile",
        "gain_weight_tendency": "📉 Weight Gain / Weight Loss Block:",
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
        
        "goal_hdr": "🎯 Step 2: Your Goal",
        "goal_q": "What is your goal?",
        "goals": ["Healthy Weight Loss", "Maintenance & Recovery", "Healthy Weight Gain"],
        
        "antropo": "👤 Step 3: Your Data",
        "weight": "Weight (kg):",
        "height": "Height (cm):",
        "age": "Age:",
        "target_info": "🎯 **Optimal Target Macros:**\n* 🔥 **Calories:** {cal} kcal\n* 🥩 **Protein:** {prot} g\n* 🥑 **Fat:** {fat} g\n* 🌾 **Net Carbs:** {carbs} g\n* 💧 **Water Intake:** {water:.2f} L",
        
        "tabs": ["🍽️ Food Assistant", "📊 Diary & Diagnostics", "📈 Correlations & Trends", "🛒 Tailored Shopping List"],
        "search_hdr": "🔍 Search and Analyze Food",
        "search_lbl": "Enter food name (e.g. beef, spinach):",
        "select_food": "Select exact food:",
        "grams": "Amount in grams (g):",
        "analysis": "#### 📊 Nutritional Analysis of Portion ({g}g):",
        "cal": "Calories",
        "prot": "Protein",
        "carbs": "Carbs",
        "fiber": "Fiber",
        
        "warnings_hdr": "### 🚨 Health Warnings for this Food:",
        "warn_gluten": "🌾 **GLUTEN:** Risk of intestinal inflammation for celiacs.",
        "warn_milk": "🥛 **Milk/Soy:** Possible goitrogen for thyroid (Hashimoto).",
        "warn_hit": "⚠️ **High Histamine:** Watch for histamine release in HIT.",
        "warn_gastritis": "🔥 **Stomach Irritator:** May cause reflux or ache.",
        "warn_sugar": "🚨 **High Sugar:** Not suitable for insulin resistance.",
        "warn_purines": "🥩 **High Purines:** Risk of gout flare-up.",
        "warn_oxalates": "🌱 **High Oxalates:** Promotes kidney stones.",
        "warn_high_fat": "🧈 **High Fat:** Strain on gallbladder and fatty liver.",
        
        "add_btn": "➕ Add to Daily Log",
        "add_success": "Food successfully added.",
        "not_found": "Food not found in database.",
        
        "diary_hdr": "📊 Daily Overview & Bio-Feedback",
        "status": "#### Nutrient Summary:",
        "feedback_hdr": "💬 Smart Daily Evaluation",
        "save_btn": "💾 Close and Save Day",
        "save_success": "Day successfully saved to history!",
        "no_meals": "You haven't eaten anything today.",
        
        "symptoms_hdr": "🩺 How does your body feel today?",
        "sym_energy": "Energy (1-10):",
        "sym_sleep": "Sleep Quality (1-10):",
        "history_hdr": "📈 Long-term Trends & Correlations Analysis",
        "history_empty": "History is empty. Save your first day.",
        "superfoods_hdr": "🛒 Tailored Shopping List for Your Body",
        "superfoods_desc": "These foods actively support healing your selected symptoms and conditions:",
        "db_status_ok": "✅ Food database is active."
    }
}

HIST_COLS = ["Dátum", "Diagnózy", "Cieľ", "Váha (kg)", "Energia", "Spánok", "Kalórie", "Sacharidy (g)", "Symptómy", "Rizikove_Dni"]

# --- MOCK DATA / NAČÍTANIE ---
@st.cache_data
def load_data():
    mock_df = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5, 6, 7],
        'name_en': ['Oats', 'Spinach', 'Beef', 'Chocolate', 'Liver', 'Tomato', 'Greek Yogurt'],
        'name_sk': ['Ovsene vlocky', 'Spenat', 'Hovadzie maso', 'Cokolada', 'Pecen', 'Paradajka', 'Grecky jogurt'],
        'Calories': [389, 23, 250, 546, 175, 18, 97],
        'Protein (g)': [16.9, 2.9, 26.0, 4.9, 27.0, 0.9, 10.0],
        'Fat (g)': [6.9, 0.4, 15.0, 31.0, 5.0, 0.2, 5.0],
        'Net-Carbs (g)': [66.3, 1.4, 0.0, 54.0, 4.0, 3.9, 3.6],
        'Sugars (g)': [0.0, 0.4, 0.0, 48.0, 0.0, 2.6, 3.6],
        'Fiber (g)': [10.6, 2.2, 0.0, 7.0, 0.0, 1.2, 0.0],
        'Iron, Fe (mg)': [4.7, 2.7, 2.6, 8.0, 18.0, 0.3, 0.1],
        'Zinc, Zn (mg)': [4.0, 0.5, 4.3, 2.3, 4.0, 0.2, 0.6]
    })
    return mock_df

def load_history():
    if os.path.exists(HISTORY_FILE):
        try: return pd.read_csv(HISTORY_FILE)
        except Exception: pass
    return pd.DataFrame(columns=HIST_COLS)

def save_history_row(row_dict):
    history_df = load_history()
    new_row = pd.DataFrame([row_dict])
    history_df = pd.concat([history_df, new_row], ignore_index=True)
    history_df.to_csv(HISTORY_FILE, index=False)

df = load_data()

# --- REORGANIZOVANÝ BOČNÝ PANEL ---
st.sidebar.write("---")

# Krok 1
with st.sidebar.expander(TXT[lang]["profile"], expanded=True):
    st.markdown(f"<small>{TXT[lang]['gain_weight_tendency']}</small>", unsafe_allow_html=True)
    has_pcos = st.checkbox(TXT[lang]["pcos"])
    has_hashi = st.checkbox(TXT[lang]["hashi"])
    has_db2 = st.checkbox(TXT[lang]["db2"])
    has_anemia = st.checkbox(TXT[lang]["anemia"])
    has_cushing = st.checkbox(TXT[lang]["cushing"])
    has_lipedema = st.checkbox(TXT[lang]["lepid"])

    st.markdown(f"<small>{TXT[lang]['lose_weight_tendency']}</small>", unsafe_allow_html=True)
    has_hyper = st.checkbox(TXT[lang]["hyper"])
    has_celiakia = st.checkbox(TXT[lang]["celiakia"])
    has_addison = st.checkbox(TXT[lang]["addison"])

    st.markdown(f"<small>{TXT[lang]['digestion']}</small>", unsafe_allow_html=True)
    has_hit = st.checkbox(TXT[lang]["hit"])
    has_gastritis = st.checkbox(TXT[lang]["gastritis"])
    has_sibo = st.checkbox(TXT[lang]["sibo"])
    has_gallbladder = st.checkbox(TXT[lang]["gallbladder"])

    st.markdown(f"<small>{TXT[lang]['metabolic_syndromes']}</small>", unsafe_allow_html=True)
    has_gout = st.checkbox(TXT[lang]["gout"])
    has_nafld = st.checkbox(TXT[lang]["nafld"])
    has_hypertension = st.checkbox(TXT[lang]["hypertension"])
    has_kidney_stones = st.checkbox(TXT[lang]["kidney_stones"])

# Krok 2
with st.sidebar.expander(TXT[lang]["goal_hdr"], expanded=False):
    meta_goal = st.radio(TXT[lang]["goal_q"], TXT[lang]["goals"], label_visibility="collapsed")

# Krok 3
with st.sidebar.expander(TXT[lang]["antropo"], expanded=False):
    weight = st.number_input(TXT[lang]["weight"], min_value=30.0, value=70.0)
    height = st.number_input(TXT[lang]["height"], min_value=120, value=165)
    age = st.number_input(TXT[lang]["age"], min_value=15, value=30)

# Výpočty cieľov (Kalórie & Makrá)
bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
base_maintenance = round(bmr * 1.2)
if has_cushing: base_maintenance = round(base_maintenance * 0.9)
if has_addison: base_maintenance = round(base_maintenance * 1.1)

if meta_goal in ["Zdravé chudnutie", "Healthy Weight Loss"]: target_cal = base_maintenance - 350
elif meta_goal in ["Zdravé pribratie", "Healthy Weight Gain"]: target_cal = base_maintenance + 400
else: target_cal = base_maintenance

# Úprava makier na základe diagnóz
target_protein = round(weight * 1.2) if (has_gout or has_kidney_stones) else round(weight * 1.5)
if has_hyper: target_protein = round(weight * 1.9)

carbs_percentage = 0.25 if (has_pcos or has_db2 or has_nafld) else 0.40
if has_sibo: carbs_percentage = 0.20 # Low FODMAP smer

target_carbs = round((target_cal * carbs_percentage) / 4)
target_fat = round((target_cal * (1.0 - (carbs_percentage + 0.25))) / 9)

if has_gallbladder or has_nafld:
    target_fat = min(target_fat, 50) # Bezpečný strop tuku pre chorý žlčník

# Pitný režim s ohľadom na obličkové kamene
water_intake = (weight * 35) / 1000
if has_kidney_stones: water_intake += 0.6

st.sidebar.info(TXT[lang]["target_info"].format(cal=target_cal, prot=target_protein, carbs=target_carbs, fat=target_fat, water=water_intake))
st.sidebar.caption(TXT[lang]["db_status_ok"])

# --- HLAVNÉ ROZHRANIE ---
st.title(TXT[lang]["title"])
tab1, tab2, tab3, tab4 = st.tabs(TXT[lang]["tabs"])

if 'daily_meals' not in st.session_state:
    st.session_state.daily_meals = []

with tab1:
    st.subheader(TXT[lang]["search_hdr"])
    search_query = st.text_input(TXT[lang]["search_lbl"], "")
    
    if search_query:
        results = df[df['name_en'].str.contains(search_query, case=False, na=False) | df['name_sk'].str.contains(search_query, case=False, na=False)]
        
        if not results.empty:
            food_options = results.apply(lambda row: f"{row['name_en']} / {row['name_sk']}", axis=1).tolist()
            selected_option = st.selectbox(TXT[lang]["select_food"], food_options)
            food_details = results.iloc[food_options.index(selected_option)]
            
            grams = st.number_input(TXT[lang]["grams"], min_value=1, value=100)
            ratio = grams / 100.0
            
            cal = round(food_details['Calories'] * ratio, 1)
            prot = round(food_details['Protein (g)'] * ratio, 1)
            fat = round(food_details['Fat (g)'] * ratio, 1)
            carbs = round(food_details['Net-Carbs (g)'] * ratio, 1)
            sugar = round(food_details['Sugars (g)'] * ratio, 1)
            fiber = round(food_details['Fiber (g)'] * ratio, 1)
            iron = round(food_details['Iron, Fe (mg)'] * ratio, 2)
            zinc = round(food_details['Zinc, Zn (mg)'] * ratio, 2)
            
            st.write(TXT[lang]["analysis"].format(g=grams))
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(TXT[lang]["cal"], f"{cal} kcal")
            c2.metric(TXT[lang]["prot"], f"{prot} g")
            c3.metric(TXT[lang]["carbs"], f"{carbs} g")
            c4.metric(TXT[lang]["fiber"], f"{fiber} g")
            
            # Detekcia rizikových faktorov
            warnings = []
            f_name = f"{food_details['name_en']} {food_details['name_sk']}".lower()
            if (has_celiakia or has_hashi) and any(x in f_name for x in ['wheat', 'barley', 'rye', 'muka', 'chlieb', 'lepok']): warnings.append(TXT[lang]["warn_gluten"])
            if has_hit and any(x in f_name for x in ['tomato', 'spinach', 'cheese', 'wine', 'paradaj', 'spenat', 'syr']): warnings.append(TXT[lang]["warn_hit"])
            if has_gout and any(x in f_name for x in ['beef', 'liver', 'pecen', 'hovadz']): warnings.append(TXT[lang]["warn_purines"])
            if has_kidney_stones and any(x in f_name for x in ['spinach', 'chocolate', 'spenat', 'cokolada']): warnings.append(TXT[lang]["warn_oxalates"])
            
            if warnings:
                st.markdown(TXT[lang]["warnings_hdr"])
                for w in warnings: st.warning(w)
                
            if st.button(TXT[lang]["add_btn"]):
                st.session_state.daily_meals.append({
                    "Jedlo": selected_option, "Kalórie": cal, "Bielkoviny": prot, 
                    "Tuky": fat, "Čisté Sacharidy": carbs, "Cukor": sugar, 
                    "Vláknina": fiber, "Železo": iron, "Zinok": zinc, "Riziko": 1 if warnings else 0
                })
                st.success(TXT[lang]["add_success"])
        else:
            st.info(TXT[lang]["not_found"])

with tab2:
    st.header(TXT[lang]["diary_hdr"])
    if st.session_state.daily_meals:
        df_today = pd.DataFrame(st.session_state.daily_meals)
        st.dataframe(df_today[["Jedlo", "Kalórie", "Bielkoviny", "Čisté Sacharidy", "Vláknina"]])
        
        t_cal = df_today["Kalórie"].sum()
        t_carbs = df_today["Čisté Sacharidy"].sum()
        t_prot = df_today["Bielkoviny"].sum()
        t_fiber = df_today["Vláknina"].sum()
        t_risks = df_today["Riziko"].sum()
        
        st.markdown(TXT[lang]["status"])
        c1, c2, c3 = st.columns(3)
        c1.metric(TXT[lang]["cal"], f"{round(t_cal)} / {target_cal} kcal")
        c2.metric(TXT[lang]["prot"], f"{round(t_prot, 1)} / {target_protein} g")
        c3.metric(TXT[lang]["carbs"], f"{round(t_carbs, 1)} / {target_carbs} g")
        
        # Automatický feedback dňa
        st.subheader(TXT[lang]["feedback_hdr"])
        if (has_pcos or has_db2) and t_fiber < 25:
            st.error("⚠️ **Inzulínový manažment:** Dnes máš kriticky málo vlákniny. Hrozí rýchle kolísanie cukru v krvi.")
        if has_hypertension and t_cal > base_maintenance:
            st.warning("🚨 **Kardiovaskulárne riziko:** Kalorický nadbytok zvyšuje záťaž na krvný tlak.")
            
    else:
        st.info(TXT[lang]["no_meals"])
        
    st.write("---")
    st.subheader(TXT[lang]["symptoms_hdr"])
    s_list = []
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.checkbox("Náhly vlčí hlad (Crash inzulínu)"): s_list.append("VlčiHlad")
        if st.checkbox("Nadúvanie a ťažoba po jedle"): s_list.append("Naduvanie")
    with col_s2:
        energy = st.slider(TXT[lang]["sym_energy"], 1, 10, 7)
        sleep = st.slider(TXT[lang]["sym_sleep"], 1, 10, 7)
        
    if st.button(TXT[lang]["save_btn"]):
        row = {
            "Dátum": str(date.today()), "Diagnózy": "Profil", "Cieľ": meta_goal,
            "Váha (kg)": weight, "Energia": energy, "Spánok": sleep,
            "Kalórie": round(t_cal, 1), "Sacharidy (g)": round(t_carbs, 1),
            "Symptómy": ", ".join(s_list) if s_list else "Ziadne", "Rizikove_Dni": t_risks
        }
        save_history_row(row)
        st.session_state.daily_meals = []
        st.success(TXT[lang]["save_success"])
        st.rerun()

with tab3:
    st.header(TXT[lang]["history_hdr"])
    h_df = load_history()
    if not h_df.empty:
        st.dataframe(h_df)
        
        # PREDIKTÍVNA DIAGNOSTIKA (Hľadanie skrytých spúšťačov)
        st.subheader("🔮 Pokročilá AI Analýza Symptómov")
        naduvanie_dni = h_df[h_df["Symptómy"].str.contains("Naduvanie", na=False)]
        if not naduvanie_dni.empty:
            priemerne_riziko = naduvanie_dni["Rizikove_Dni"].mean()
            if priemerne_riziko > 0.5:
                st.error(f"🔍 **Objavená korelácia:** Tvoje nadúvanie sa štatisticky objavuje najmä v dni, kedy v záložke Asistent ignoruješ zdravotné varovania (priemerne {round(priemerne_riziko, 1)} varovaní na problémový deň).")
            else:
                st.info("🔍 Systém analyzuje dáta. Zatiaľ nie je dostatok záznamov na určenie presného spúšťača.")
    else:
        st.info(TXT[lang]["history_empty"])

with tab4:
    st.header(TXT[lang]["superfoods_hdr"])
    st.write(TXT[lang]["superfoods_desc"])
    
    if has_anemia:
        st.success("🩸 **Pre Anémiu (Železo):** Hovädzie mäso, hovädzia pečeň, tekvicové semienka, špenát + kombinovať s Vitamínom C.")
    if has_hashi:
        st.success("🦋 **Pre Hashimoto (Štítna žľaza):** Para orechy (selén), treska (jód), vajíčka, sinkom bohaté potraviny.")
    if has_pcos or has_db2:
        st.success("🌾 **Pre Stabilizáciu Inzulínu:** Ovsené vločky, avokádo, brokolica, škorica, strukoviny.")
    if not (has_anemia or has_hashi or has_pcos or has_db2):
        st.info("Zvoľ si diagnózy v bočnom paneli a tu sa ti vygeneruje nákupný lístok potravín, ktoré tvoje telo podporia.")
