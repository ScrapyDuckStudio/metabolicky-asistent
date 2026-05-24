import streamlit as st
import pandas as pd
from datetime import date

# 1. NASTAVENIE STRÁNKY - Responzívne a moderné rozloženie pre PC aj mobil
st.set_page_config(
    page_title="Metabolický Asistent & Inteligentný Kouč", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Vlastný CSS štýl pre krajší vzhľad v prehliadači a na mobile
st.markdown("""
<style>
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700; }
    div[data-testid="stMetric"] {
        background-color: #f8f9fa; padding: 12px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e9ecef;
    }
    .stExpander { border-radius: 12px !important; border: 1px solid #e9ecef !important; }
    h1 { font-size: 2.0rem !important; font-weight: 800 !important; color: #1e293b; }
    h2 { font-size: 1.5rem !important; color: #334155; }
    h3 { font-size: 1.1rem !important; color: #475569; }
</style>
""", unsafe_allow_html=True)

# 2. BEZPEČNÉ NAČÍTANIE DÁT Z TVOJHO GITHUB REPOZITÁRA
@st.cache_data
def load_data():
    # Surová (Raw) linka na tvoj súbor food_data.csv na GitHube
    url = "https://raw.githubusercontent.com/ScrapyDuckStudio/metabolicky-asistent/main/food_data.csv"
    
    # Načítame bez skiprows, keďže hlavička je na prvom riadku
    df = pd.read_csv(url)
    
    # Vyčistíme názvy stĺpcov od prípadných medzier (napr. " name " -> "name")
    df.columns = df.columns.str.strip()
    
    # Pre istotu premenujeme stĺpec, ak by bol zapísaný ako Name alebo NAME
    for col in df.columns:
        if col.lower() == 'name':
            df = df.rename(columns={col: 'name'})
    return df

try:
    df = load_data()
    if 'name' not in df.columns:
        st.error(f"🚨 V súbore chýba stĺpec 'name'. Nájdené stĺpce: {list(df.columns)}")
        st.stop()
except Exception as e:
    st.error(f"Nepodarilo sa načítať súbor food_data.csv z GitHubu. Chyba: {e}")
    st.stop()

# --- BEZPEČNÉ UKLADANIE PRE DEPLOYMENT (Cloudová pamäť / Session State) ---
if 'daily_meals' not in st.session_state:
    st.session_state.daily_meals = []

if 'cloud_history' not in st.session_state:
    st.session_state.cloud_history = pd.DataFrame(
        columns=["Dátum", "Diagnózy", "Cieľ", "Váha (kg)", "Energia", "Spánok", "Kalórie", "Sacharidy (g)", "Symptómy"]
    )

# --- BOČNÝ PANEL: DIAGNÓZY A CIELE ---
st.sidebar.header("🧬 1. Výber zdravotného profilu")

st.sidebar.markdown("**Sklon k priberaniu / Blokácia chudnutia:**")
has_pcos = st.sidebar.checkbox("PCOS (Inzulínová rezistencia)", value=False)
has_hashi = st.sidebar.checkbox("Hashimoto (Spomalený metabolizmus)", value=False)
has_db2 = st.sidebar.checkbox("Cukrovka 2. typu", value=False)
has_anemia = st.sidebar.checkbox("Anémia (Nedostatok železa/kyslíka)", value=False)

st.sidebar.markdown("**Sklon k chudnutiu / Problém pribrať:**")
has_hyper = st.sidebar.checkbox("Hypertyreóza (Zrýchlený metabolizmus)", value=False)
has_celiakia = st.sidebar.checkbox("Celiakia / IBD (Porucha vstrebávania)", value=False)

st.sidebar.markdown("**Tráviace citlivosti:**")
has_hit = st.sidebar.checkbox("HIT (Histamínová intolerancia)", value=False)
has_gastritis = st.sidebar.checkbox("Gastritída (Zápal žalúdka)", value=False)

st.sidebar.write("---")
st.sidebar.header("🎯 2. Tvoj cieľ")
meta_goal = st.sidebar.radio("Čo chceš dosiahnuť?", ["Zdravé chudnutie", "Udržanie váhy & Regenerácia", "Zdravé pribratie (Budovanie hmoty)"])

st.sidebar.write("---")
st.sidebar.header("👤 3. Antropometrické údaje")
weight = st.sidebar.number_input("Váha (kg):", min_value=30.0, value=70.0, step=0.1)
height = st.sidebar.number_input("Výška (cm):", min_value=120, value=165)
age = st.sidebar.number_input("Vek:", min_value=15, value=30)

# Výpočet kalórií (BMR)
bmr = round(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
base_maintenance = round(bmr * 1.2)

if meta_goal == "Zdravé chudnutie":
    target_cal = base_maintenance - 350
elif meta_goal == "Zdravé pribratie (Budovanie hmoty)":
    target_cal = base_maintenance + 400
else:
    target_cal = base_maintenance

target_protein = round(weight * 1.8) if (has_hyper or meta_goal == "Zdravé pribratie (Budovanie hmoty)") else round(weight * 1.5)
carbs_percentage = 0.30 if (has_pcos or has_db2) else 0.45
target_carbs = round((target_cal * carbs_percentage) / 4)
target_fat = round((target_cal * (1.0 - (carbs_percentage + 0.25))) / 9)

st.sidebar.info(f"""
🎯 **Tvoj cieľový príjem:**
* 💎 **Kalórie:** {target_cal} kcal
* 🥩 **Bielkoviny:** {target_protein} g
* 🥖 **Čisté sacharidy:** {target_carbs} g
* 🥑 **Tuky:** {target_fat} g
""")

# --- HLAVNÁ STRÁNKA ---
st.title("🔬 Inteligentný Metabolický & Hormonálny Tracker")

tab1, tab2, tab3 = st.tabs(["🍽️ Potravinový asistent & Diagnostika", "📊 Dnešný denník & Inteligentný feedback", "📈 Dlhodobý vývoj"])

with tab1:
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.subheader("🔍 Hľadať potravinu")
        search_query = st.text_input("Zadaj názov v angličtine (napr. beef, oats, spinach, milk):", "")
        
        if search_query:
            results = df[df['name'].str.contains(search_query, case=False, na=False)]
            if not results.empty:
                food_list = results['name'].tolist()
                selected_food = st.selectbox("Vyber potravinu:", food_list)
                food_details = results[results['name'] == selected_food].iloc[0]
                
                grams = st.number_input("Gramáž (g):", min_value=1, value=100, step=10)
                ratio = grams / 100.0
                
                cal = round(food_details.get('Calories', 0) * ratio, 1)
                prot = round(food_details.get('Protein (g)', 0) * ratio, 1)
                fat = round(food_details.get('Fat (g)', 0) * ratio, 1)
                carbs = round(food_details.get('Net-Carbs (g)', 0) * ratio, 1)
                sugar = round(food_details.get('Sugars (g)', 0) * ratio, 1)
                fiber = round(food_details.get('Fiber (g)', 0) * ratio, 1)
                iron = round(food_details.get('Iron, Fe (mg)', 0) * ratio, 2)
                zinc = round(food_details.get('Zinc, Zn (mg)', 0) * ratio, 2)
                
                name_lower = selected_food.lower()
                warnings = []
                
                if has_celiakia or has_hashi:
                    if any(x in name_lower for x in ['wheat', 'barley', 'rye', 'flour', 'bread', 'gluten']):
                        warnings.append("🌾 **Obsahuje LEPKOVKU / GLUTEN:** Riziko zápalovej reakcie čreva.")
                
                if has_hashi and any(x in name_lower for x in ['milk', 'cheese', 'yogurt', 'cream', 'soy']):
                    warnings.append("🥛/🫛 **Mlieko/Sója:** Možný skrížený alergén pre štítnu žľazu.")

                if has_hit and any(x in name_lower for x in ['tomato', 'spinach', 'avocado', 'eggplant', 'cheese', 'wine', 'vinegar', 'sauerkraut', 'fermented', 'shrimp', 'tuna']):
                    warnings.append("⚠️ **Vysoký Histamín:** Sleduj reakciu tela.")
                
                if has_gastritis and any(x in name_lower for x in ['chili', 'pepper', 'coffee', 'lemon', 'lime', 'onion', 'garlic', 'fried']):
                    warnings.append("🔥 **Žalúdočný iritant:** Môže dráždiť žalúdok.")

                st.write(f"#### 📊 Analýza pre {grams}g:")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Kalórie", f"{cal} kcal")
                c2.metric("Bielkoviny", f"{prot} g")
                c3.metric("Čisté Sacharidy", f"{carbs} g")
                c4.metric("Vláknina", f"{fiber} g")
                
                if warnings:
                    st.markdown("### 🚨 Zdravotné upozornenia:")
                    for w in warnings:
                        st.warning(w)
                
                if (has_pcos or has_db2) and sugar > 10:
                    st.error("🚨 **Pozor na cukor:** Vysoká inzulínová špička.")

                if st.button("➕ Pridať do dňa", use_container_width=True):
                    st.session_state.daily_meals.append({
                        "Jedlo": selected_food, "Gramy": grams, "Kalórie": cal, 
                        "Bielkoviny": prot, "Tuky": fat, "Čisté Sacharidy": carbs, 
                        "Cukor": sugar, "Vláknina": fiber, "Železo": iron, "Zinok": zinc,
                        "Rizikové": 1 if warnings else 0
                    })
                    st.success("Pridané do dnešného prehľadu.")
            else:
                st.info("Slovo sa v databáze nenašlo.")

    with col_r:
        st.markdown("### 💡 Encyklopédia metabolizmu")
        if has_pcos or has_db2:
            with st.expander("🌾 Inzulínový blok"):
                st.write("**PCOS & Cukrovka 2. typu:** Vláknina a nízky cukor sú kľúč k obnove citlivosti na inzulín.")
        if has_hashi:
            with st.expander("🦋 Spomalený motor (Hashimoto)"):
                st.write("**Hypotyreóza:** Bielkoviny, zinok a selén chránia svaly a stimulujú metabolizmus.")
        if has_hyper:
            with st.expander("🔥 Prehriaty motor (Hypertyreóza)"):
                st.write("**Zvýšená funkcia:** Telo rýchlo odbúrava hmotu. Potrebuješ zdravý kalorický prebytok.")
        if has_anemia:
            with st.expander("🩸 Kyslíkový dlh (Anémia)"):
                st.write("**Chýbajúce železo:** Bez železa chýba bunkám kyslík a chudnutie/regenerácia sa zaseknú.")

with tab2:
    st.header("📊 Tvoj dnešný denník")
    
    if st.session_state.daily_meals:
        df_today = pd.DataFrame(st.session_state.daily_meals)
        st.dataframe(df_today[["Jedlo", "Gramy", "Kalórie", "Bielkoviny", "Čisté Sacharidy", "Cukor", "Vláknina"]], use_container_width=True)
        
        t_cal = df_today["Kalórie"].sum()
        t_carbs = df_today["Čisté Sacharidy"].sum()
        t_prot = df_today["Bielkoviny"].sum()
        t_sugar = df_today["Cukor"].sum()
        t_fiber = df_today["Vláknina"].sum()
        t_iron = df_today["Železo"].sum()
        t_zinc = df_today["Zinok"].sum()
        t_risks = df_today["Rizikové"].sum()
        
        st.markdown(f"#### Aktuálny stav dňa:")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Kalórie celkom", f"{round(t_cal)} / {target_cal} kcal")
        c2.metric("Bielkoviny", f"{round(t_prot, 1)} / {target_protein} g")
        c3.metric("Čisté Sacharidy", f"{round(t_carbs, 1)} / {target_carbs} g")
        c4.metric("Vláknina", f"{round(t_fiber, 1)} g")
        
        st.write("---")
        st.subheader("💬 Personalizované spätné väzby a odporúčania")
        
        feedbacks = []
        
        if has_pcos or has_db2:
            if t_fiber < 25:
                feedbacks.append("🌾 **PCOS / Cukrovka:** Dnes máš **nízky príjem vlákniny** (menej ako 25g). Vláknina je kľúčová, pretože spomaľuje vstrebávanie sacharidov a bráni prudkým výkyvom inzulínu. Skús pridať chia semienka, ľanové semienka alebo brokolicu.")
            else:
                feedbacks.append("✨ **PCOS / Cukrovka:** Skvelé! Dosiahla si parádny príjem vlákniny. Tvoj inzulín ti ďakuje za stabilné prostredie.")
                
            if t_sugar > 35:
                feedbacks.append("🚨 **PCOS / Cukrovka:** Pozor, celkový **cukor dnes prekročil bezpečnú hranicu** (nad 35g). To môže vyvolať inzulínovú rezistenciu, zablokovať spaľovanie tukov a vyvolať vlčí hlad.")

        if has_anemia:
            if t_iron < 15:
                feedbacks.append(f"🩸 **Anémia:** Dnes si prijala len **{round(t_iron, 1)} mg železa** (odporúčaný cieľ pri anémii je aspoň 15-18mg). Bez železa bunky nemajú dostatok kyslíka na metabolické procesy. Pridaj nabudúce hovädzie mäso, tekvicové semienka alebo tmavú listovú zeleninu s kvapkou citrónu (kvôli vstrebávaniu).")
            else:
                feedbacks.append("💪 **Anémia:** Perfektné! Máš dnes bohatý príjem železa. Tvoje bunky majú dostatok kyslíka pre energiu a metabolizmus.")

        if has_hashi:
            if t_zinc < 11:
                feedbacks.append(f"🦋 **Hashimoto:** Tvoj **zinok je dnes nízky ({round(t_zinc, 1)} mg)**. Štítna žľaza nutne potrebuje zinok na konverziu neaktívneho hormónu T4 na aktívny T3. Skús do stravy doplniť tekvicové semienka, kešu orechy, hovädzie mäso alebo morské polody.")
            if t_risks > 0:
                feedbacks.append(f"⚠️ **Hashimoto:** Zjedla si dnes {t_risks} potravín s potenciálnym autoimunitným spúšťačom (lepok, sója alebo mlieko). Pozorne si večer odleduj, či sa neobjaví únava alebo mozgová hmla.")

        if has_celiakia and t_risks > 0:
            feedbacks.append("🚨 **Celiakia:** V denníku máš jedlo s obsahom lepku! Pri celiakii dochádza k okamžitému poškodeniu klkov čreva, čo kompletne zastaví vstrebávanie živín a spôsobí podvýživu.")
            
        if has_gastritis and t_risks > 0:
            feedbacks.append("🔥 **Gastritída:** Zaznamenala si potravinu, ktorá dráždi sliznicu žalúdka. Ak ucítiš pálenie alebo ťažobu, vieš, ktoré jedlo to spôsobilo. Nabudúce zvoľ radšej zásaditejšie potraviny.")

        if not feedbacks:
            st.success("☀️ Tvoj dnešný jedálniček perfektne rešpektuje tvoj zdravotný stav. Žiadne riziká ani deficity neboli nájdené!")
        else:
            for f in feedbacks:
                st.info(f)
                
    else:
        st.info("Zatiaľ si dnes nezadala žiadne potraviny. Komentár a analýza deficitov sa zobrazia hneď po pridaní prvého jedla.")

    st.write("---")
    st.subheader("🩺 Sledovanie priebehu príznakov")
    s_cols = st.columns(3)
    s_list = []
    
    with s_cols[0]:
        st.markdown("**Symptómy príberania / Únavy:**")
        if st.checkbox("Náhly vlčí hlad (Inzulín)"): s_list.append("VlčíHlad")
        if st.checkbox("Extrémna svalová slabosť (Anémia)"): s_list.append("Slabosť")
    with s_cols[1]:
        st.markdown("**Symptómy straty hmotnosti:**")
        if st.checkbox("Búšenie srdca / Vnútorná triaška (Hyper)"): s_list.append("Triaška")
        if st.checkbox("Kŕče v bruchu / Hnačka (Celiakia)"): s_list.append("KŕčeBrucha")
    with s_cols[2]:
        st.markdown("**Subjektívne pocity:**")
        energy_score = st.slider("Energia počas dňa (1-10):", 1, 10, 7)
        sleep_score = st.slider("Spánok (1-10):", 1, 10, 7)

    if st.button("💾 Ukončiť a uložiť deň", use_container_width=True):
        diag_list = []
        if has_pcos: diag_list.append("PCOS")
        if has_hashi: diag_list.append("Hashimoto")
        if has_anemia: diag_list.append("Anemia")
        if has_celiakia: diag_list.append("Celiakia")
        
        new_row = pd.DataFrame([{
            "Dátum": str(date.today()),
            "Diagnózy": ", ".join(diag_list) if diag_list else "Žiadne",
            "Cieľ": meta_goal,
            "Váha (kg)": weight,
            "Energia": energy_score,
            "Spánok": sleep_score,
            "Kalórie": round(t_cal, 1),
            "Sacharidy (g)": round(t_carbs, 1),
            "Symptómy": ", ".join(s_list) if s_list else "Žiadne"
        }])
        
        # Zápis do session_state histórie
        st.session_state.cloud_history = pd.concat([st.session_state.cloud_history, new_row], ignore_index=True)
        st.session_state.daily_meals = []
        st.success("Záznam úspešne uložený do cloudu!")
        st.rerun()

with tab3:
    st.header("📈 Dlhodobé sledovanie vývoja tela")
    if not st.session_state.cloud_history.empty:
        st.dataframe(st.session_state.cloud_history, use_container_width=True)
        st.subheader("Graf: Pohyb telesnej hmotnosti (kg)")
        st.line_chart(st.session_state.cloud_history.set_index("Dátum")["Váha (kg)"])
    else:
        st.info("Žiadne historické záznamy neboli zatiaľ vytvorené.")
