import os

import streamlit as st
from fpdf import FPDF

from logic import get_lang, txt


def render_shopping_cart(health_conditions):
    RECS = [
        ("Tekvicové semienka", "Pumpkin seeds", "Zinok", "Zinc", "Semienka/Seeds", False, False),
        ("Hovädzie mäso", "Beef", "Železo/B12", "Iron/B12", "Mäso/Meat", False, False),
        ("Špenát", "Spinach", "Železo", "Iron", "Zelenina/Veg", False, False),
        ("Hovädzia pečeň", "Beef liver", "Železo/B12", "Iron/B12", "Mäso/Meat", False, False),
        ("Chia semienka", "Chia seeds", "Vláknina/Ω3", "Fiber/Ω3", "Semienka/Seeds", False, False),
        ("Avokádo", "Avocado", "Vláknina/K", "Fiber/K", "Ovocie/Fruit", False, False),
        ("Vaječné žĺtka", "Egg yolks", "Vitamín D", "Vitamin D", "Vajcia/Eggs", False, False),
        ("Šampiňóny (UV)", "Mushrooms (UV)", "Vitamín D", "Vitamin D", "Huby/Mushrooms", False, False),
        ("Lahôdkové droždie", "Nutritional yeast", "B12/Zinok", "B12/Zinc", "Doplnky/Suppl.", False, False),
        ("Kuracie prsia", "Chicken breast", "B12/Bielk.", "B12/Protein", "Hydina/Poultry", False, False),
        ("Sezamové semienka", "Sesame seeds", "Zinok/Vápnik", "Zinc/Calcium", "Semienka/Seeds", False, False),
        ("Kešu orechy", "Cashews", "Zinok/Mg", "Zinc/Mg", "Orechy/Nuts", False, False),
        ("Cícer", "Chickpeas", "Zinok/Vlák.", "Zinc/Fiber", "Strukoviny/Legumes", False, False),
        ("Šošovica", "Lentils", "Železo/Vlák.", "Iron/Fiber", "Strukoviny/Legumes", False, False),
        ("Quinoa", "Quinoa", "Železo/Bielk.", "Iron/Protein", "Obilniny/Grains", False, False),
        ("Ľanové semienka", "Flaxseeds", "Vláknina/Ω3", "Fiber/Ω3", "Semienka/Seeds", False, False),
        ("Brokolica", "Broccoli", "Vláknina/C", "Fiber/C", "Zelenina/Veg", False, False),
        ("Ovsené vločky", "Oats", "Vláknina/Mg", "Fiber/Mg", "Obilniny/Grains", False, False),
        ("Para orechy", "Brazil nuts", "Selén", "Selenium", "Orechy/Nuts", False, False),
        ("Tmavá čokoláda 85%", "Dark chocolate 85%", "Mg/Železo", "Mg/Iron", "Iné/Other", False, False),
        ("Divoký losos", "Wild salmon", "Vitamín D/Ω3", "Vitamin D/Ω3", "Ryby/Fish", True, False),
        ("Sardinky", "Sardines", "Vitamín D/Ca", "Vitamin D/Ca", "Ryby/Fish", True, False),
        ("Tresčia pečeň", "Cod liver", "Vitamín D/A", "Vitamin D/A", "Ryby/Fish", True, False),
        ("Tuniak", "Tuna", "B12/Selén", "B12/Selenium", "Ryby/Fish", True, False),
        ("Kefír", "Kefir", "B12/Probiot.", "B12/Probiotics", "Mliečne/Dairy", False, True),
        ("Grécky jogurt", "Greek yogurt", "Vápnik/Bielk.", "Calcium/Prot.", "Mliečne/Dairy", False, True),
        ("Mandle", "Almonds", "Vápnik/Mg", "Calcium/Mg", "Orechy/Nuts", False, False),
        ("Sladké zemiaky", "Sweet potatoes", "Vitamín A/K", "Vitamin A/K", "Zelenina/Veg", False, False),
    ]

    lang = get_lang()
    all_suggestions = []
    for food_sk, food_en, ben_sk, ben_en, cat, is_fish, is_dairy in RECS:
        if is_fish and health_conditions.get('has_hit'):
            continue
        if is_dairy and (health_conditions.get('has_hashi') or health_conditions.get('has_celiakia')):
            continue
        food_label = food_sk if lang == "SK" else food_en
        ben_label = ben_sk if lang == "SK" else ben_en
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
