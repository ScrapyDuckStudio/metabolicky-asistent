import math

import streamlit as st

from food_warnings import detect_food_warnings
from logic import get_lang, txt

FOOD_GROUP_SK = {
    "American Indian":        "Americká indiánska kuchyňa",
    "Baby Foods":             "Detská výživa",
    "Baked Foods":            "Pečivo a pekárenské výrobky",
    "Beans and Lentils":      "Fazuľa a šošovica",
    "Beverages":              "Nápoje",
    "Breakfast Cereals":      "Raňajkové cereálie",
    "Dairy and Egg Products": "Mliečne výrobky a vajcia",
    "Dairy and Egg Products ":"Mliečne výrobky a vajcia",
    "Fast Foods":             "Rýchle občerstvenie",
    "Fats and Oils":          "Tuky a oleje",
    "Fish":                   "Ryby",
    "Fruits":                 "Ovocie",
    "Grains and Pasta":       "Obilniny a cestoviny",
    "Meats":                  "Mäso",
    "Nuts and Seeds":         "Orechy a semienka",
    "Prepared Meals":         "Hotové jedlá",
    "Restaurant Foods":       "Reštauračné jedlá",
    "Snacks":                 "Snacky",
    "Soups and Sauces":       "Polievky a omáčky",
    "Spices and Herbs":       "Koreniny a bylinky",
    "Sweets":                 "Sladkosti",
    "Vegetables":             "Zelenina",
}


def _n(val, decimals=1):
    try:
        v = float(val)
        return round(0.0 if math.isnan(v) else v, decimals)
    except (TypeError, ValueError):
        return 0.0


def render_food_tab(df, health_conditions, sidebar_data=None):
    st.markdown(
        f"<h3 style='color:#059669;'>{txt('search_hdr')}</h3>",
        unsafe_allow_html=True,
    )

    # ── Food group filter ─────────────────────────────────────────────────────
    def translate_group(en):
        return FOOD_GROUP_SK.get(en.strip(), en) if get_lang() == "SK" else en

    raw_groups   = sorted(df["Food Group"].dropna().unique().tolist()) if "Food Group" in df.columns else []
    group_display = [txt("all_groups")] + [translate_group(g) for g in raw_groups]
    group_en_map  = {translate_group(g): g for g in raw_groups}

    selected_display = st.selectbox(txt("food_group_filter"), group_display)
    selected_group   = group_en_map.get(selected_display, None)

    search_query = st.text_input(txt("search_lbl"), "", placeholder="Napr. Ovsene vlocky / Oats...")

    if not search_query:
        return

    mask = (
        df["name_en"].str.contains(search_query, case=False, na=False) |
        df["name_sk"].str.contains(search_query, case=False, na=False)
    )
    if selected_group is not None and "Food Group" in df.columns:
        mask = mask & (df["Food Group"].str.strip() == selected_group.strip())
    results = df[mask]

    if results.empty:
        st.info(txt("not_found"))
        return

    # ── Food selector ─────────────────────────────────────────────────────────
    food_options = results["name_sk"].tolist() if get_lang() == "SK" else results["name_en"].tolist()
    selected_option = st.selectbox(txt("select_food"), food_options)
    selected_idx    = food_options.index(selected_option)
    fd = results.iloc[selected_idx]
    stored_label = f"{fd['name_en']} / {fd['name_sk']}"

    grams = st.number_input(txt("grams"), min_value=1, value=100, step=10)
    r = grams / 100.0

    # ── Macros ────────────────────────────────────────────────────────────────
    cal   = round(fd.get("Calories",     0) * r, 1)
    prot  = round(fd.get("Protein (g)",  0) * r, 1)
    fat   = round(fd.get("Fat (g)",      0) * r, 1)
    carbs = round(fd.get("Net-Carbs (g)",0) * r, 1)
    sugar = round(fd.get("Sugars (g)",   0) * r, 1)
    fiber = round(fd.get("Fiber (g)",    0) * r, 1)

    # ── Micros ────────────────────────────────────────────────────────────────
    iron   = _n(fd.get("Iron, Fe (mg)",          0) * r, 2)
    zinc   = _n(fd.get("Zinc, Zn (mg)",          0) * r, 2)
    vitd   = _n(fd.get("Vitamin D (mcg)",        0) * r, 2)
    mag    = _n(fd.get("Magnesium (mg)",          0) * r, 1)
    calc   = _n(fd.get("Calcium (mg)",            0) * r, 1)
    omega3 = _n(fd.get("Omega 3s (mg)",           0) * r, 0)
    sel    = _n(fd.get("Selenium, Se (mcg)",      0) * r, 1)
    vitc   = _n(fd.get("Vitamin C (mg)",          0) * r, 1)
    b12    = _n(fd.get("Vitamin B-12 (mcg)",      0) * r, 2)
    potass = _n(fd.get("Potassium, K (mg)",       0) * r, 0)
    sodium = _n(fd.get("Sodium (mg)",             0) * r, 0)
    caff   = _n(fd.get("Caffeine (mg)",           0) * r, 1)

    # ── Build macro HTML ──────────────────────────────────────────────────────
    macro_html = ""
    for lbl, val in [
        (txt("prot"),  f"{prot} g"),
        (txt("carbs"), f"{carbs} g"),
        (txt("fat"),   f"{fat} g"),
        (txt("fiber"), f"{fiber} g"),
    ]:
        macro_html += (
            '<div style="background:rgba(45,212,191,0.06);border:1px solid rgba(45,212,191,0.10);'
            'border-radius:14px;padding:12px;text-align:center;">'
            f'<div style="font-size:1.4rem;font-weight:800;color:#2dd4bf;">{val}</div>'
            f'<div style="font-size:0.72rem;color:#6b8a85;margin-top:3px;'
            f'text-transform:uppercase;letter-spacing:0.5px;">{lbl}</div>'
            '</div>'
        )

    # ── Build micro HTML ──────────────────────────────────────────────────────
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
            '<div style="background:rgba(20,32,31,0.9);border:1px solid rgba(45,212,191,0.09);'
            'border-radius:12px;padding:9px 10px;text-align:center;">'
            f'<div style="font-size:1.05rem;font-weight:700;color:#2dd4bf;">{val}</div>'
            f'<div style="font-size:0.7rem;color:#6b8a85;margin-top:2px;">{lbl}</div>'
            '</div>'
        )

    # ── Assemble card ─────────────────────────────────────────────────────────
    name_en     = str(fd["name_en"])
    name_sk     = str(fd["name_sk"])
    food_group  = str(fd.get("Food Group", ""))
    sugar_label = txt("sugar")
    micro_label = txt("micros_hdr")

    card_html = (
        '<div style="background:linear-gradient(135deg,rgba(15,30,28,0.95),rgba(10,22,20,0.98));'
        'border:1px solid rgba(45,212,191,0.18);border-radius:22px;'
        'padding:24px 28px 20px 28px;margin:16px 0 8px 0;box-shadow:0 8px 32px rgba(0,0,0,0.35);">'

        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">'
        '<div>'
        f'<div style="font-size:1.35rem;font-weight:800;color:#f0fdfa;letter-spacing:-0.5px;">{name_en}</div>'
        f'<div style="font-size:0.85rem;color:#6b8a85;margin-top:2px;">'
        f'{name_sk} &nbsp;·&nbsp; {food_group} &nbsp;·&nbsp; {grams} g</div>'
        '</div>'
        '<div style="background:linear-gradient(135deg,#0f766e,#14b8a6);border-radius:14px;'
        'padding:10px 18px;text-align:center;box-shadow:0 4px 16px rgba(20,184,166,0.25);">'
        f'<div style="font-size:1.8rem;font-weight:800;color:#fff;line-height:1;">{cal}</div>'
        '<div style="font-size:0.72rem;color:rgba(255,255,255,0.75);letter-spacing:1px;'
        'text-transform:uppercase;">kcal</div>'
        '</div></div>'

        '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px;">'
        + macro_html +
        '</div>'

        '<div style="margin-bottom:18px;">'
        '<div style="background:rgba(251,113,133,0.08);border:1px solid rgba(251,113,133,0.15);'
        'border-radius:12px;padding:10px 18px;text-align:center;">'
        f'<span style="font-size:1.1rem;font-weight:700;color:#fb7185;">{sugar} g</span>'
        f'<span style="font-size:0.72rem;color:#6b8a85;margin-left:8px;'
        f'text-transform:uppercase;">{sugar_label}</span>'
        '</div></div>'

        f'<div style="font-size:0.75rem;font-weight:700;color:#6b8a85;letter-spacing:1.5px;'
        f'text-transform:uppercase;margin-bottom:10px;">🔬 {micro_label}</div>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;">'
        + micro_html +
        '</div></div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # ── Warnings ──────────────────────────────────────────────────────────────
    full_name = f"{fd['name_en']} {fd['name_sk']}"
    warnings  = detect_food_warnings(full_name, health_conditions)
    if warnings:
        st.markdown(txt("warnings_hdr"))
        for w in warnings:
            st.warning(w)
    if (
        health_conditions.get("has_pcos") or health_conditions.get("has_db2") or
        health_conditions.get("has_nafld") or health_conditions.get("has_candida")
    ) and sugar > 10:
        st.error(txt("warn_sugar"))

    # ── Add to diary button ───────────────────────────────────────────────────
    if "daily_meals" not in st.session_state:
        st.session_state.daily_meals = []

    if st.button(txt("add_btn"), use_container_width=True):
        st.session_state.daily_meals.append({
            "Jedlo":           stored_label,
            "Gramy":           grams,
            "Kalórie":         cal,
            "Bielkoviny":      prot,
            "Tuky":            fat,
            "Čisté Sacharidy": carbs,
            "Cukor":           sugar,
            "Vláknina":        fiber,
            "Železo":          iron,
            "Zinok":           zinc,
            "Vitamín D":       vitd,
            "Horčík":          mag,
            "Vápnik":          calc,
            "Omega3":          omega3,
            "Selén":           sel,
            "Rizikové":        1 if warnings else 0,
        })
        st.success(txt("add_success"))

    # ── Encyclopedia ──────────────────────────────────────────────────────────
    has_pcos      = health_conditions.get("has_pcos")
    has_db2       = health_conditions.get("has_db2")
    has_hashi     = health_conditions.get("has_hashi")
    has_hyper     = health_conditions.get("has_hyper")
    has_anemia    = health_conditions.get("has_anemia")
    has_gout      = health_conditions.get("has_gout")
    has_nafld     = health_conditions.get("has_nafld")
    has_menopause = health_conditions.get("has_menopause")
    has_osteo     = health_conditions.get("has_osteo")
    has_adrenal   = health_conditions.get("has_adrenal")

    enc_items = []
    if has_pcos or has_db2:    enc_items.append(("enc_pcos_t",      "enc_pcos_b",      "🌾", "#14b8a6", "#0f766e"))
    if has_hashi:              enc_items.append(("enc_hashi_t",     "enc_hashi_b",     "🦋", "#818cf8", "#4f46e5"))
    if has_hyper:              enc_items.append(("enc_hyper_t",     "enc_hyper_b",     "🔥", "#fb923c", "#c2410c"))
    if has_anemia:             enc_items.append(("enc_anemia_t",    "enc_anemia_b",    "🩸", "#f43f5e", "#be123c"))
    if has_gout:               enc_items.append(("enc_gout_t",      "enc_gout_b",      "🦴", "#a78bfa", "#7c3aed"))
    if has_nafld:              enc_items.append(("enc_nafld_t",     "enc_nafld_b",     "🍏", "#4ade80", "#15803d"))
    if has_menopause:          enc_items.append(("enc_menopause_t", "enc_menopause_b", "🌸", "#f472b6", "#be185d"))
    if has_osteo:              enc_items.append(("enc_osteo_t",     "enc_osteo_b",     "🦴", "#fbbf24", "#b45309"))
    if has_adrenal:            enc_items.append(("enc_adrenal_t",   "enc_adrenal_b",   "⚡", "#38bdf8", "#0369a1"))

    if not enc_items:
        return

    st.divider()
    lang = get_lang()
    enc_title = "Tvoje diagnózy — čo to znamená pre tvoje telo" if lang == "SK" else "Your conditions — what they mean for your body"
    st.markdown(
        f'<div style="font-size:0.7rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;'
        f'color:#6b8a85;margin-bottom:8px;">💡 {"Encyklopédia metabolizmu" if lang == "SK" else "Metabolism Encyclopedia"}</div>'
        f'<div style="font-size:1.5rem;font-weight:800;color:#f0fdfa;margin-bottom:18px;">{enc_title}</div>',
        unsafe_allow_html=True,
    )

    cols_per_row = 3
    for row_start in range(0, len(enc_items), cols_per_row):
        row_items = enc_items[row_start:row_start + cols_per_row]
        enc_cols  = st.columns(cols_per_row)
        for col, (t_key, b_key, icon, c1, c2) in zip(enc_cols, row_items):
            with col:
                title_text = txt(t_key)
                body_text  = txt(b_key)
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,rgba(15,28,26,0.95),rgba(10,20,18,0.98));'
                    f'border:1px solid rgba(45,212,191,0.12);border-top:3px solid {c1};'
                    f'border-radius:18px;padding:20px 22px;margin-bottom:12px;min-height:140px;'
                    f'box-shadow:0 6px 24px rgba(0,0,0,0.28);">'
                    f'<div style="font-size:2rem;margin-bottom:8px;">{icon}</div>'
                    f'<div style="font-size:1rem;font-weight:700;color:#f0fdfa;margin-bottom:8px;">{title_text}</div>'
                    f'<div style="font-size:0.85rem;color:#9fb7b3;line-height:1.6;">{body_text}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
