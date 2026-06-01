import streamlit as st

from data import get_history_file, load_history
from logic import get_lang, txt


def render_progress_tab():
    lang = get_lang()
    hist = load_history()

    st.markdown(f"<div style='margin-bottom:28px;'>"
                f"<div style='font-size:0.7rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;"
                f"color:#6b8a85;margin-bottom:8px;'>"
                f"{'📈 DLHODOBÝ VÝVOJ' if lang == 'SK' else '📈 LONG-TERM PROGRESS'}"
                f"</div>"
                f"<div style='font-size:2rem;font-weight:800;color:#f0fdfa;letter-spacing:-0.5px;'>"
                f"{'Tvoja cesta v číslach' if lang == 'SK' else 'Your journey in numbers'}"
                f"</div>"
                f"<div style='font-size:0.88rem;color:#6b8a85;margin-top:6px;'>"
                f"{'Každý uložený deň sa zobrazí tu. Sleduj trendy a zlepšuj sa.' if lang == 'SK' else 'Every saved day appears here. Track trends and keep improving.'}"
                f"</div>"
                f"</div>", unsafe_allow_html=True)

    if hist.empty:
        st.markdown(
            '<div style="background:rgba(45,212,191,0.03);border:1.5px dashed rgba(45,212,191,0.15);'
            'border-radius:22px;padding:60px 40px;text-align:center;'>
            '<div style="font-size:3rem;margin-bottom:14px;">📭</div>'
            '<div style="font-size:1.1rem;font-weight:700;color:#9fb7b3;margin-bottom:8px;">'
            f"{'Zatiaľ žiadne záznamy' if lang == 'SK' else 'No records yet'}"
            '</div>'
            '<div style="font-size:0.85rem;color:#6b8a85;">'
            f"{'Ulož prvý deň v záložke Dnešný denník → tlačidlo Ukončiť a uložiť deň.' if lang == 'SK' else 'Save your first day in the Daily Diary tab → Finish and Save Day button.'}"
            '</div>'
            '</div>', unsafe_allow_html=True)
        return

    days = len(hist)
    avg_cal = round(hist['Kalórie'].mean(), 0) if 'Kalórie' in hist.columns else None
    avg_w = round(hist['Váha (kg)'].mean(), 1) if 'Váha (kg)' in hist.columns else None
    avg_e = round(hist['Energia'].mean(), 1) if 'Energia' in hist.columns else None
    avg_sl = round(hist['Spánok'].mean(), 1) if 'Spánok' in hist.columns else None

    def trend(col):
        if col not in hist.columns or len(hist) < 2:
            return ""
        diff = hist[col].iloc[-1] - hist[col].iloc[0]
        if diff > 0:
            return '<span style="color:#10b981;font-size:0.8rem;"> ▲</span>'
        if diff < 0:
            return '<span style="color:#fb7185;font-size:0.8rem;"> ▼</span>'
        return '<span style="color:#6b8a85;font-size:0.8rem;"> —</span>'

    stat_items = [
        ("📅", str(days), "", "Dní" if lang == 'SK' else "Days"),
        ("🔥", f"{int(avg_cal or 0)}", trend('Kalórie'), "Ø kcal"),
        ("⚖️", f"{avg_w or '—'} kg", trend('Váha (kg)'), "Ø " + ('váha' if lang == 'SK' else 'weight')),
        ("⚡", f"{avg_e or '—'}/10", trend('Energia'), "Ø " + ('energia' if lang == 'SK' else 'energy')),
        ("😴", f"{avg_sl or '—'}/10", trend('Spánok'), "Ø " + ('spánok' if lang == 'SK' else 'sleep')),
    ]

    cards_html = '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:32px;">'
    for icon, val, tr, lbl in stat_items:
        cards_html += (
            f'<div style="background:linear-gradient(135deg,rgba(15,28,26,0.95),rgba(10,20,18,0.98));'
            f'border:1px solid rgba(45,212,191,0.12);border-radius:18px;padding:20px 12px;text-align:center;'
            f'box-shadow:0 4px 20px rgba(0,0,0,0.22);'>
            f'<div style="font-size:1.6rem;margin-bottom:8px;">{icon}</div>'
            f'<div style="font-size:1.25rem;font-weight:800;color:#2dd4bf;line-height:1;">{val}{tr}</div>'
            f'<div style="font-size:0.68rem;color:#6b8a85;margin-top:5px;text-transform:uppercase;letter-spacing:1px;">{lbl}</div>'
            f'</div>'
        )
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    if 'Váha (kg)' in hist.columns and 'Dátum' in hist.columns:
        st.markdown(
            '<div style="background:rgba(15,28,26,0.7);border:1px solid rgba(45,212,191,0.10);'
            'border-radius:18px;padding:20px 20px 8px 20px;margin-bottom:16px;">'
            '<div style="font-size:0.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
            'color:#6b8a85;margin-bottom:12px;">⚖️ ' +
            ("TELESNÁ HMOTNOSŤ (kg)" if lang == 'SK' else "BODY WEIGHT (kg)") +
            '</div>',
            unsafe_allow_html=True,
        )
        w_data = (hist[['Dátum', 'Váha (kg)']].dropna().rename(columns={'Dátum': 'index', 'Váha (kg)': 'kg'}).set_index('index'))
        st.line_chart(w_data, height=180, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap='large')
    with col_a:
        if 'Kalórie' in hist.columns:
            st.markdown(
                '<div style="background:rgba(15,28,26,0.7);border:1px solid rgba(45,212,191,0.10);'
                'border-radius:18px;padding:20px 20px 8px 20px;">'
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
                'color:#6b8a85;margin-bottom:12px;">🔥 ' +
                ("KALÓRIE / DEŇ (kcal)" if lang == 'SK' else "CALORIES / DAY (kcal)") +
                '</div>',
                unsafe_allow_html=True,
            )
            c_data = (hist[['Dátum', 'Kalórie']].dropna().rename(columns={'Dátum': 'index', 'Kalórie': 'kcal'}).set_index('index'))
            st.bar_chart(c_data, height=200, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        if 'Energia' in hist.columns and 'Spánok' in hist.columns:
            st.markdown(
                '<div style="background:rgba(15,28,26,0.7);border:1px solid rgba(45,212,191,0.10);'
                'border-radius:18px;padding:20px 20px 8px 20px;">'
                '<div style="font-size:0.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
                'color:#6b8a85;margin-bottom:12px;">⚡ ' +
                ("ENERGIA & SPÁNOK (1–10)" if lang == 'SK' else "ENERGY & SLEEP (1–10)") +
                '</div>',
                unsafe_allow_html=True,
            )
            es_data = hist[['Dátum', 'Energia', 'Spánok']].dropna().set_index('Dátum')
            st.line_chart(es_data, height=200, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:0.68rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
        'color:#6b8a85;margin:24px 0 12px 0;">🗓️ ' +
        ("ZÁZNAMY" if lang == 'SK' else "ENTRIES") + '</div>',
        unsafe_allow_html=True,
    )

    hist_all = load_history().iloc[::-1].reset_index(drop=True)
    for i, row in hist_all.iterrows():
        e_val = row.get('Energia', '—')
        sl_val = row.get('Spánok', '—')
        kcal = row.get('Kalórie', '—')
        w_val = row.get('Váha (kg)', '—')
        diag = str(row.get('Diagnózy', '')).strip()
        if not diag or diag in ('nan', 'None', 'Žiadne'):
            diag = ''
        goal = str(row.get('Cieľ', '')).strip()

        card_col, del_col = st.columns([11, 1])
        with card_col:
            st.markdown(
                f'<div style="background:rgba(15,28,26,0.85);border:1px solid rgba(45,212,191,0.10);'
                f'border-left:3px solid rgba(45,212,191,0.35);border-radius:14px;'
                f'padding:14px 20px;margin-bottom:2px;'>
                f'<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:5px;">'
                f'<span style="font-size:1rem;font-weight:700;color:#2dd4bf;">{row.get('Dátum', '')}</span>'
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
                unsafe_allow_html=True,
            )
        with del_col:
            if st.button('🗑️', key=f'hist_del_{i}', help='Odstrániť' if lang == 'SK' else 'Delete'):
                full = load_history()
                orig_idx = len(full) - 1 - i
                full = full.drop(index=orig_idx).reset_index(drop=True)
                full.to_csv(get_history_file(), index=False)
                st.rerun()
        st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
