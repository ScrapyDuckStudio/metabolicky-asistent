import os

import pandas as pd
import streamlit as st

from logic import txt

HISTORY_COLUMNS = [
    "Dátum", "Diagnózy", "Cieľ", "Váha (kg)", "Energia", "Spánok",
    "Kalórie", "Sacharidy (g)", "Voda (L)", "Symptómy"
]


def get_history_file() -> str:
    try:
        if st.user and st.user.is_logged_in:
            safe = st.user.email.replace("@", "_at_").replace(".", "_")
            return f"history_{safe}.csv"
    except Exception:
        pass
    return "zdravotna_historia_global.csv"


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
    f = get_history_file()
    if os.path.exists(f):
        try:
            return pd.read_csv(f)
        except Exception:
            pass
    return pd.DataFrame(columns=HISTORY_COLUMNS)


def save_history_row(row_dict):
    f = get_history_file()
    history_df = load_history()
    new_row = pd.DataFrame([row_dict])
    history_df = pd.concat([history_df, new_row], ignore_index=True)
    try:
        history_df.to_csv(f, index=False)
    except Exception as e:
        st.error(f"{txt('err_save')}: {e}")
