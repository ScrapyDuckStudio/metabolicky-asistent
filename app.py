import streamlit as st

# --- KONFIGURÁCIA STRÁNKY ---
st.set_page_config(page_title="Metabolický Tracker", layout="wide", page_icon="🩺")

# --- CSS PRE VIZUÁL ---
custom_css = """
<style>
    .pet-box { text-align: center; padding: 20px; background: rgba(127, 140, 141, 0.1); border-radius: 15px; margin-bottom: 20px; font-size: 60px; }
    .stButton>button { border-radius: 8px; font-weight: 600; width: 100%; }
    .metric-card { background: rgba(52, 152, 219, 0.1); padding: 15px; border-radius: 10px; text-align: center; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- INICIALIZÁCIA PAMÄTE (SESSION STATE) ---
# Toto zabezpečí, že sa nič nevymaže pri zmene jazyka
if 'lang' not in st.session_state: st.session_state.lang = 'SK'
if 'water_glasses' not in st.session_state: st.session_state.water_glasses = 0
if 'pet_mood' not in st.session_state: st.session_state.pet_mood = '😊'
if 'pet_msg' not in st.session_state: st.session_state.pet_msg = "Som hladný po zdravom jedle!"

# --- DATABÁZA ---
DISEASES = {
    "pcos": {
        "SK": "PCOS (Inzulínová rezistencia)", "EN": "PCOS (Insulin Resistance)",
        "tips_SK": "💡 Zvýš vlákninu (30g+), inozitol pomáha.", "tips_EN": "💡 Increase fiber (30g+), inositol helps.",
        "foods_SK": ["Škorica", "Zelená zelenina", "Bobule"], "foods_EN": ["Cinnamon", "Leafy greens", "Berries"]
    },
    "hashimoto": {
        "SK": "Hashimoto (Spomalený metabolizmus)", "EN": "Hashimoto's (Slow Metabolism)",
        "tips_SK": "💡 Selén a Zinok sú kľúčové. Pozor na lepok.", "tips_EN": "💡 Selenium and Zinc are key. Watch gluten.",
        "foods_SK": ["Para orechy", "Losos", "Vajcia"], "foods_EN": ["Brazil nuts", "Salmon", "Eggs"]
    },
    "anemia": {
        "SK": "Anémia (Nedostatok železa)", "EN": "Anemia (Iron Deficiency)",
        "tips_SK": "💡 Kombinuj železo s Vitamínom C.", "tips_EN": "💡 Pair iron with Vitamin C.",
        "foods_SK": ["Hovädzie", "Šošovica", "Špenát"], "foods_EN": ["Beef", "Lentils", "Spinach"]
    }
}

UI = {
    'title': {'SK': '🩺 Metabolický Kamoš Tracker', 'EN': '🩺 Metabolic Buddy Tracker'},
    'pet_title': {'SK': '🐾 Tvoj metabolický kamoš', 'EN': '🐾 Your metabolic buddy'},
    'food_log': {'SK': 'Loguj stravu:', 'EN': 'Log food:'},
    'btn_bad': {'SK': 'Zjesť "Zlé" jedlo (Cukor/Fast food)', 'EN': 'Eat "Bad" food (Sugar/Fast food)'},
    'btn_good': {'SK': 'Zjesť zdravé jedlo', 'EN': 'Eat healthy food'},
    'water': {'SK': 'Poháre vody', 'EN': 'Glasses of water'},
    'tips_header': {'SK': '🧠 Pripomienky pre zdravie:', 'EN': '🧠 Health reminders:'},
    'basket_header': {'SK': '🛒 Nákupný košík', 'EN': '🛒 Shopping Basket'}
}

# --- FUNKCIE PRE PET LOGIKU ---
def update_pet(action):
    if action == "bad":
        st.session_state.pet_mood = "🤢"
        st.session_state.pet_msg = "Au! To nebolo dobré pre metabolizmus."
    elif action == "good":
        st.session_state.pet_mood = "😊"
        st.session_state.pet_msg = "Mňam! Toto mi chutí."
    elif action == "water":
        if st.session_state.water_glasses > 5:
            st.session_state.pet_mood = "🤩"
            st.session_state.pet_msg = "Super hydratácia!"
        else:
            st.session_state.pet_mood = "😊"
            st.session_state.pet_msg = "Ďakujem za vodičku."

# --- BOČNÝ PANEL (SIDEBAR) ---
with st.sidebar:
    # Prepínač jazyka
    c1, c2 = st.columns(2)
    if c1.button("🇸🇰 SK"): st.session_state.lang = 'SK'
    if c2.button("🇬🇧 EN"): st.session_state.lang = 'EN'
    
    st.divider()
    
    # 🐾 METABOLICKÝ KAMOŠ
    st.markdown(f"### {UI['pet_title'][st.session_state.lang]}")
    st.markdown(f"<div class='pet-box'>{st.session_state.pet_mood}</div>", unsafe_allow_html=True)
    st.caption(st.session_state.pet_msg)
    
    st.divider()
    
    # Zdravotný profil (Kľúče sú statické, takže sa nevymažú)
    for d_id, d_info in DISEASES.items():
        st.checkbox(d_info[st.session_state.lang], key=f"chk_{d_id}")

# --- HLAVNÁ STRÁNKA ---
st.title(UI['title'][st.session_state.lang])

tab1, tab2 = st.tabs(["📊 Tracker", UI['basket_header'][st.session_state.lang]])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💧 Pitný režim")
        if st.button("➕ Pridať vodu"):
            st.session_state.water_glasses += 1
            update_pet("water")
        st.metric(label=UI['water'][st.session_state.lang], value=st.session_state.water_glasses)
    
    with col2:
        st.subheader("🍔 Logovanie jedla")
        if st.button(UI['btn_bad'][st.session_state.lang]):
            update_pet("bad")
        if st.button(UI['btn_good'][st.session_state.lang]):
            update_pet("good")

    st.markdown("---")
    
    # Zobrazenie pripomienok
    active_diseases = [d_id for d_id in DISEASES.keys() if st.session_state.get(f"chk_{d_id}", False)]
    if active_diseases:
        st.subheader(UI['tips_header'][st.session_state.lang])
        for d_id in active_diseases:
            st.info(DISEASES[d_id][f"tips_{st.session_state.lang}"])

with tab2:
    st.subheader(UI['basket_header'][st.session_state.lang])
    if not active_diseases:
        st.write("Vyber si diagnózu v bočnom paneli.")
    else:
        # Zoskupenie potravín
        for d_id in active_diseases:
            st.markdown(f"**{DISEASES[d_id][st.session_state.lang]}**")
            cols = st.columns(3)
            for i, food in enumerate(DISEASES[d_id][f"foods_{st.session_state.lang}"]):
                cols[i % 3].checkbox(food, key=f"food_{d_id}_{food}")
