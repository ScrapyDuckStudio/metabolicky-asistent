import streamlit as st

from sidebar import render_sidebar
from food_tab import render_food_tab
from diary_tab import render_diary_tab
from progress_tab import render_progress_tab
from shopping_tab import render_shopping_cart
from logic import get_lang, txt
from translation import TRANSLATIONS

st.set_page_config(
    page_title="Metabolický Asistent & Inteligentný Kouč",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded",
)


def load_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


load_css("style.css")

# ── Google auth disabled — enable when credentials are configured ─────────────
_auth_configured = False

# ── App header ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(
        f"<h1 style='color:#0d9488;margin-bottom:0px;'>{txt('title')}</h1>",
        unsafe_allow_html=True,
    )
with col2:
    new_lang = st.radio("🌐", ["SK", "EN"], horizontal=True, label_visibility="collapsed")
    st.session_state.lang = new_lang
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar_data = render_sidebar(_auth_configured)
health_conditions = sidebar_data["health_conditions"]
df = sidebar_data["df"]

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(TRANSLATIONS[get_lang()]["tabs"])

with tab1:
    render_food_tab(df, health_conditions)

with tab2:
    render_diary_tab(
        df=df,
        meta_goal=sidebar_data["meta_goal"],
        target_cal=sidebar_data["target_cal"],
        target_protein=sidebar_data["target_protein"],
        target_carbs=sidebar_data["target_carbs"],
        target_water=sidebar_data["target_water"],
        health_conditions=health_conditions,
        weight=sidebar_data["weight"],
    )

with tab3:
    render_progress_tab()

with tab4:
    render_shopping_cart(health_conditions)
