import streamlit as st
import pandas as pd
from datetime import date

# 1. NASTAVENIE STRÁNKY - Responzívne a moderné rozloženie pre PC aj mobil
st.set_page_config(
    page_title="Metabolický Asistent", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Vlastný CSS štýl pre moderný vzhľad (zaoblené rohy, responzívne boxy)
st.markdown("""
<style>
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700;
    }
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    .stExpander {
        border-radius: 12px !important;
        border: 1px solid #e9ecef !important;
    }
    h1 { font-size: 2.0rem !important; font-weight: 800 !important; color: #1e293b; }
    h2 { font-size: 1.5rem !important; color: #334155; }
    h3 { font-size: 1.1rem !important; color: #475569; }
</style>
""", unsafe_allow_html=True)

# 2. NAČÍTANIE DÁT PRIAMO Z TVOJHO GITHUB-U
@st.cache_data
def load_data():
    # Surová (Raw) linka na tvoj súbor food_data.csv
    url = "https://raw.githubusercontent.com/ScrapyDuckStudio/metabolicky-asistent/main/food_data.csv"
    
    # Načítanie dát (bez vynechávania riadkov, keďže hlavička je na začiatku)
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Nepodarilo sa načítať súbor food_data.csv z tvojho GitHubu. Chyba: {e}")
    st.stop()

# --- BEZPEČNÉ UKLADANIE PRE DEPLOYMENT (Session State & Pamäť) ---
if 'daily_meals' not in st.session_state:
    st.session_state.daily_meals = []

if 'cloud_history' not in st.session_state:
    st.session_state.cloud_history = pd.DataFrame(
        columns=["Dátum", "Diagnózy", "Cieľ", "Váha (kg)", "Energia", "Spánok", "Kalórie", "Sacharidy (g)", "Symptómy"]
    )

# --- BOČNÝ PANEL: DIAGNÓZY A CIELE ---
st.sidebar.header("🧬 1. Zdravotný profil")
st.sidebar.markdown("**Sklon k priberaniu / Blokácia:**")
has_pcos = st.sidebar.checkbox("PCOS (Inzulín)", value=False)
has_hashi = st.sidebar.checkbox("Hashimoto (Štítna žľaza ↓)", value=False)
has_db2 = st.sidebar.checkbox("Cukrovka 2. typu", value=False)
has_anemia = st.sidebar.checkbox("Anémia (Nedostatok železa)", value=False)

st.sidebar.markdown("**Sklon k chudnutiu / Problém pribrať:**")
has_hyper = st.sidebar.checkbox("Hypertyreóza (Štítna žľaza ↑)", value=False)
has_hyper_ibd = st.sidebar.checkbox("Celiakia / IBD (Tenké črevo)", value=False)

st.sidebar.markdown("**Tráviace citlivosti:**")
has_hit = st.sidebar.checkbox("HIT (Histamín)", value=False)
has_gastritis = st.sidebar.checkbox("Gastritída (Žalúdok)", value=False)

st.sidebar.write("---")
st.sidebar.header("🎯 2. Tvoj cieľ")
meta_goal = st.sidebar.radio("Čo chceš dosiahnuť?", ["Zdravé chudnutie", "Udržanie váhy", "Zdravé pribratie"])

st.sidebar.write("---")
st.sidebar.header("👤 3. Miery")
weight = st.sidebar.number_input("Váha (kg):", min_value=30.0, value=70.0, step=0.1)
height = st.sidebar.number_input("Výška (cm):", min_value=120, value=165)
age = st.sidebar.number_input("Vek:", min_value=15, value=30)

# Výpočty kalórií
bmr = round(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
base_maintenance = round(bmr * 1.2)

if meta_goal == "Zdravé chudnutie":
    target_cal = base_maintenance - 350
elif meta_goal == "Zdravé pribratie":
    target_cal = base_maintenance + 400
else:
    target_cal = base_maintenance

target_protein = round(weight * 1.8) if (has_hyper or meta_goal == "Zdravé pribratie") else round(weight * 1.5)
carbs_percentage = 0.30 if (has_pcos or has_db2) else 0.42
target_carbs = round((target_cal * carbs_percentage) / 4)
target_fat = round((target_cal * (1.0 - (carbs_percentage + 0.25))) / 9)

st.sidebar.info(f"""
🎯 **Optimálny denný cieľ:**
* 💎 **Kalórie:** {target_cal} kcal
* 🥩 **Bielkoviny:** {target_protein} g
* 🥖 **Čisté sacharidy:** {target_carbs} g
* 🥑 **Tuky:** {target_fat} g
""")

# --- HLAVNÁ STRÁNKA ---
st.title("🌸 Hormonálny & Metabolický Asistent")

tab1, tab2, tab3 = st.tabs(["🍽️ Pridať jedlo & Výuka", "📊 Dnešný prehľad & Kouč", "📈 Dlhodobá história"])

with tab1:
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.subheader("🔍 Vyhľadať v databáze")
        search_query = st.text_input("Zadaj názov jedla v angličtine (napr. oats, avocado, beef):", "", placeholder="Sem napíš názov...")
        
        if search_query:
            results = df[df['name'].str.contains(search_query, case=False, na=False)]
            if not results.empty:
                food_list = results['name'].tolist()
                selected_food = st.selectbox("Vyber presnú položku:", food_list)
                food_details = results[results['name'] == selected_food].iloc[0]
                
                grams = st.number_input("Množstvo v gramoch (g):", min_value=1, value=100, step=10)
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
                
                if has_hyper_ibd or has_hashi:
                    if any(x in name_lower for x in ['wheat', 'barley', 'rye', 'flour', 'bread', 'gluten']):
                        warnings.append("🌾 **Lepok (Gluten):** Riziko podráždenia sliznice čreva.")
                
                if has_hashi and any(x in name_lower for x in ['milk', 'cheese', 'yogurt', 'cream', 'soy']):
                    warnings.append("🥛/🫛 **Mlieko/Sója:** Možný zápalový faktor pre štítnu žľazu.")

                if has_hit and any(x in name_lower for x in ['tomato', 'spinach', 'avocado', 'cheese', 'fermented', 'tuna']):
                    warnings.append("⚠️ **Vysoký Histamín:** Pozor pri histamínovej intolerancii.")
                
                if has_gastritis and any(x in name_lower for x in ['chili', 'pepper', 'coffee', 'lemon', 'fried']):
                    warnings.append("🔥 **Žalúdočný iritant:** Môže vyvolať pálenie záhy a bolesť.")

                st.write("---")
                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.metric("Kalórie", f"{cal} kcal")
                mc2.metric("Bielkoviny", f"{prot} g")
                mc3.metric("Sacharidy", f"{carbs} g")
                mc4.metric("Vláknina", f"{fiber} g")
                
                if warnings:
                    st.markdown("### 🚨 Zdravotné upozornenia:")
                    for w in warnings:
                        st.warning(w)
                
                if (has_pcos or has_db2) and sugar > 10:
                    st.error("🚨 **Pozor na cukor:** Vysoká inzulínová nálož.")

                if st.button("➕ Pridať do dnešného dňa", use_container_width=True):
                    st.session_state.daily_meals.append({
                        "Jedlo": selected_food, "Gramy": grams, "Kalórie": cal, 
                        "Bielkoviny": prot, "Tuky": fat, "Čisté Sacharidy": carbs, 
                        "Cukor": sugar, "Vláknina": fiber, "Železo": iron, "Zinok": zinc,
                        "Rizikové": 1 if warnings else 0
                    })
                    st.success("Úspešne pridané do tvojho denníka!")
            else:
                st.info("Slovo sa v databáze nenašlo. Zadaj anglický výraz (napr. oats, apple, beef).")

    with col_r:
        st.subheader("💡 Encyklopédia tela")
        if has_pcos or has_db2:
            with st.expander("🌾 Inzulín & Vláknina"):
                st.write("Vláknina spomaľuje cukry v krvi. Bunky lepšie reagujú na inzulín, čo uľahčuje chudnutie.")
        if has_hashi:
            with st.expander("🦋 Hashimoto & Zinok"):
                st.write("Zinok pomáha premieňať hormóny štítnej žľazy na aktívnu formu T3 a zrýchľuje metabolizmus.")
        if has_anemia:
            with st.expander("🩸 Železo & Kyslík"):
                st.write("Bez železa mitochondria nedokáže spáliť tuk. Ak chýba kyslík, metabolizmus kompletne stojí.")

with tab2:
    st.header("📊 Dnešný jedálniček")
    
    if st.session_state.daily_meals:
        df_today = pd.DataFrame(st.session_state.daily_meals)
        st.dataframe(df_today[["Jedlo", "Gramy", "Kalórie", "Bielkoviny", "Čisté Sacharidy", "Vláknina"]], use_container_width=True)
        
        t_cal = df_today["Kalórie"].sum()
        t_carbs = df_today["Čisté Sacharidy"].sum()
        t_prot = df_today["Bielkoviny"].sum()
        t_sugar = df_today["Cukor"].sum()
        t_fiber = df_today["Vláknina"].sum()
        t_iron = df_today["Železo"].sum()
        t_zinc = df_today["Zinok"].sum()
        t_risks = df_today["Rizikové"].sum()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Kalórie celkom", f"{round(t_cal)} / {target_cal} kcal")
        c2.metric("Bielkoviny", f"{round(t_prot, 1)} / {target_protein} g")
        c3.metric("Čisté Sacharidy", f"{round(t_carbs, 1)} / {target_carbs} g")
        c4.metric("Vláknina", f"{round(t_fiber, 1)} g")
        
        st.write("---")
        st.subheader("💬 Inteligentný koučing na dnes")
        
        feedbacks = []
        if has_pcos or has_db2:
            if t_fiber < 25:
                feedbacks.append("🌾 **PCOS / Cukrovka:** Dnes máš **málo vlákniny** (pod 25g). Pridaj ovsené vločky, chia alebo brokolicu.")
            if t_sugar > 35:
                feedbacks.append("🚨 **PCOS / Cukrovka:** Celkový **cukor prekročil 35g**. Blokuje to spaľovanie tukov.")
        if has_anemia and t_iron < 15:
            feedbacks.append(f"🩸 **Anémia:** Málo železa ({round(t_iron, 1)} mg). Bunky nemajú kyslík na tvorbu energie.")
        if has_hashi and t_zinc < 11:
            feedbacks.append(f"🦋 **Hashimoto:** Nízky zinok ({round(t_zinc, 1)} mg). Štítna žľaza spomaľuje tvoj motor.")

        if not feedbacks:
            st.success("☀️ Tvoj dnešný jedálniček je v dokonalom súlade s tvojím telom!")
        else:
            for f in feedbacks:
                st.info(f)
    else:
        st.info("Zatiaľ si dnes nepridala žiadne jedlo.")
        t_cal, t_carbs, t_prot, t_fiber, t_iron, t_zinc, t_risks = 0, 0, 0, 0, 0, 0, 0

    st.write("---")
    st.subheader("🩺 Večerný zápis pocitov")
    s_cols = st.columns(3)
    s_list = []
    with s_cols[0]:
        if st.checkbox("Náhly vlčí hlad (Inzulín)"): s_list.append("VlčíHlad")
        if st.checkbox("Ťažká slabosť svalov (Anémia)"): s_list.append("Slabosť")
    with s_cols[1]:
        if st.checkbox("Triaška / Búšenie srdca (Hyper)"): s_list.append("Triaška")
        if st.checkbox("Kŕče v bruchu (Celiakia)"): s_list.append("KŕčeBrucha")
    with s_cols[2]:
        energy_score = st.slider("Energia dňa (1-10):", 1, 10, 7)
        sleep_score = st.slider("Spánok dňa (1-10):", 1, 10, 7)

    if st.button("💾 Uzavrieť deň a uložiť", use_container_width=True):
        diag_list = []
        if has_pcos: diag_list.append("PCOS")
        if has_hashi: diag_list.append("Hashimoto")
        if has_anemia: diag_list.append("Anemia")
        
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
        
        st.session_state.cloud_history = pd.concat([st.session_state.cloud_history, new_row], ignore_index=True)
        st.session_state.daily_meals = []
        st.success("Dnešný deň bol úspešne zapísaný do cloudu!")
        st.rerun()

with tab3:
    st.header("📈 Dlhodobý vývoj")
    if not st.session_state.cloud_history.empty:
        st.dataframe(st.session_state.cloud_history, use_container_width=True)
        st.subheader("Graf: Vývoj telesnej hmotnosti")
        st.line_chart(st.session_state.cloud_history.set_index("Dátum")["Váha (kg)"])
    else:
        st.info("História zatiaľ neobsahuje žiadne uložené dni.")
