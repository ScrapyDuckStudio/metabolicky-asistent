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

# ── Google auth — only activate when client_id is explicitly configured ──────
_auth_configured = False
try:
    client_id = st.secrets["auth"]["google"]["client_id"]
    _auth_configured = bool(client_id and len(str(client_id)) > 10)
except Exception:
    _auth_configured = False

if _auth_configured:
    _logged_in = False
    try:
        _logged_in = bool(st.user.is_logged_in)
    except Exception:
        _logged_in = False

    if not _logged_in:
        _lang_pre = st.session_state.get("lang", "SK")
        st.markdown("""
<div style="background:linear-gradient(135deg,rgba(15,30,28,0.97),rgba(10,22,20,0.99));
     border:1px solid rgba(45,212,191,0.18);border-radius:22px;
     padding:48px 40px;max-width:480px;margin:80px auto;text-align:center;
     box-shadow:0 16px 48px rgba(0,0,0,0.4);">
  <div style="font-size:3rem;margin-bottom:16px;">🌿</div>
  <div style="font-size:1.6rem;font-weight:800;color:#f0fdfa;margin-bottom:8px;">
    Metabolický Asistent
  </div>
  <div style="font-size:0.9rem;color:#9fb7b3;margin-bottom:28px;">
    Prihlás sa Google účtom — tvoje dáta sa synchronizujú na všetkých zariadeniach.<br>
    <span style="font-size:0.82rem;color:#6b8a85;">Sign in with Google to sync your data across devices.</span>
  </div>
</div>""", unsafe_allow_html=True)
        _, col_btn, _ = st.columns([1, 2, 1])
        with col_btn:
            st.login("google")
        st.stop()
    else:
        try:
            st.session_state["_user_email"] = st.user.email
            st.session_state["_user_name"] = getattr(st.user, "name", st.user.email)
        except Exception:
            pass

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
    render_food_tab(df, health_conditions, sidebar_data)

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
