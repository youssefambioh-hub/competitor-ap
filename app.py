# app.py
import streamlit as st
import pandas as pd
import folium
import plotly.graph_objects as go
from streamlit_folium import st_folium
import math

import config
from data_loader import load_data
import helpers
import charts

st.set_page_config(
    page_title="PT of the City | Market Intelligence",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="auto",
)

# Load CSS with UTF-8 encoding
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────────────────────
try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Failed to load data from Snowflake: {e}")
    st.stop()

if df.empty:
    st.error("No data returned from Snowflake.")
    st.stop()

us_df   = df[df["_is_us"]]
comp_df = df[~df["_is_us"]]

def get_insurance_options(df_in):
    ai = set()
    for txt in df_in["_insurance"]:
        for it in str(txt).replace(";", ",").split(","):
            it = it.strip()
            if it and len(it) > 1 and it.lower() not in ("nan", "none", ""):
                ai.add(it)
    return sorted(ai)

AREA_OPTIONS      = ["All Areas"] + sorted([a for a in df["Neighborhood / Area"].unique() if a])
INSURANCE_OPTIONS = get_insurance_options(df)
ALL_CLINIC_NAMES  = sorted([n for n in df["Clinic Name"].unique() if n])

# ── Session State & Navigation ─────────────────────────────────────────────
for key, default in [
    ("page", "dashboard"),
    ("clinic", None),
    ("selected_clinic", None),
    ("compare_a", None),
    ("compare_b", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

def open_clinic(name):
    st.session_state.clinic = name
    st.session_state.page = "profile"
    st.rerun()

def go_dash():
    st.session_state.page = "dashboard"
    st.session_state.clinic = None
    st.session_state.selected_clinic = None
    st.rerun()

def go_map():
    st.session_state.page = "map"
    st.rerun()

def go_compare():
    st.session_state.page = "compare"
    st.rerun()

def render_filter_widgets(key_prefix):
    st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([2, 1.3, 1.3, 1.5, 0.8, 1.1])
    with fc1:
        search_q = st.text_input("Search Clinics", placeholder="🔍  Search clinic name or area…", label_visibility="collapsed", key=f"{key_prefix}_search")
    with fc2:
        f_area = st.selectbox("Select Area", AREA_OPTIONS, label_visibility="collapsed", key=f"{key_prefix}_area")
    with fc3:
        f_threat = st.selectbox("Select Threat Level", ["All Threats", "5 — Critical", "4 — High", "3 — Medium", "2 — Low", "1 — Minimal"], label_visibility="collapsed", key=f"{key_prefix}_threat")
    with fc4:
        f_ins = st.selectbox("Select Insurance", ["All Insurances"] + INSURANCE_OPTIONS, label_visibility="collapsed", key=f"{key_prefix}_ins")
    with fc5:
        show_us = st.checkbox("Ours only", key=f"{key_prefix}_us")
    with fc6:
        sort_by = st.selectbox("Sort By", ["Sort: Threat ↓", "Sort: Rating ↓", "Sort: Reviews ↓", "Sort: Score ↓", "Sort: A–Z"], label_visibility="collapsed", key=f"{key_prefix}_sort")
    st.markdown('</div>', unsafe_allow_html=True)
    return search_q, f_area, f_threat, f_ins, show_us, sort_by

def render_sidebar(name):
    rows = df[df["Clinic Name"] == name]
    if rows.empty: return
    r = rows.iloc[0]
    is_us = r["_is_us"]
    t_val = r["_threat"]
    gs_val = r["_google_score"]

    with st.sidebar:
        if st.button("✕  Close", key="sb_close"):
            st.session_state.selected_clinic = None
            st.rerun()

        st.markdown(f"""
        <div class="sb-hdr">
            <div class="sb-name">{helpers.v(r,'Clinic Name')}</div>
            <div class="sb-area">🏙️ {helpers.v(r,'Neighborhood / Area')}</div>
            <div class="sb-addr">📍 {helpers.v(r,'Address')}</div>
            <div class="sb-addr">📞 {helpers.v(r,'Phone')}</div>
            <div class="sb-badges">{helpers.threat_badge(t_val,is_us)}{helpers.flag_badge(r)}</div>
        </div>
        """, unsafe_allow_html=True)

        yelp = helpers.v(r, "Yelp_Rating")
        yr   = helpers.v(r, "Yelp_Reviews")
        try:
            ti = int(float(t_val))
            tc = {5: "#DC2626", 4: "#F59E0B", 3: "#EAB308", 2: "#60A5FA", 1: "#10B981"}.get(ti, "#CBD5E1")
        except Exception:
            tc = "#CBD5E1"; ti = None

        gs_display = helpers.fmt_gscore(gs_val)

        st.markdown(f"""
        <div class="sb-stats">
            <div class="sb-stat"><div class="sb-stat-val">⭐ {helpers.v(r,'Google Rating')}</div><div class="sb-stat-lbl">Google Rating</div></div>
            <div class="sb-stat"><div class="sb-stat-val">{helpers.v(r,'# Reviews')}</div><div class="sb-stat-lbl">Reviews</div></div>
            <div class="sb-stat gscore"><div class="sb-stat-val">📊 {gs_display}</div><div class="sb-stat-lbl">Google Score</div></div>
            <div class="sb-stat"><div class="sb-stat-val" style="color:{tc};">{(str(ti)+'/5') if ti else '—'}</div><div class="sb-stat-lbl">Threat</div></div>
            <div class="sb-stat"><div class="sb-stat-val">{helpers.v(r,'Distance from PTotC (mi)')} mi</div><div class="sb-stat-lbl">Distance</div></div>
            <div class="sb-stat"><div class="sb-stat-val">{helpers.v(r,'Estimated_Daily_Volume')}</div><div class="sb-stat-lbl">Daily Volume</div></div>
        </div>
        """, unsafe_allow_html=True)

        if yelp != "—":
            st.markdown(f"""
            <div class="sb-stats" style="margin-top:-6px;">
                <div class="sb-stat"><div class="sb-stat-val">⭐ {yelp}</div><div class="sb-stat-lbl">Yelp ({yr} rev.)</div></div>
            </div>
            """, unsafe_allow_html=True)

        website = helpers.v(r, "Website"); gmaps = helpers.v(r, "Google Maps Link"); social = helpers.v(r, "Social_Media")
        links = ""
        if website != "—" and "Not found" not in website:
            url = website if website.startswith("http") else f"https://{website}"
            links += f'<a class="sb-link" href="{url}" target="_blank">🌐 Website</a>'
        if gmaps.startswith("http"):
            links += f'<a class="sb-link" href="{gmaps}" target="_blank">📍 Maps</a>'
        if social.startswith("http"):
            links += f'<a class="sb-link" href="{social}" target="_blank">📱 Social</a>'
        if links:
            st.markdown(f'<div class="sb-links">{links}</div>', unsafe_allow_html=True)

        nearest = helpers.v(r, "Nearest_PT_of_The_City")
        dist_near = helpers.v(r, "Distance_to_Nearest_PTotC_miles")
        if nearest != "—":
            st.markdown(f"""
            <div class="sb-sec"><div class="sb-sec-title">🏥 Nearest PT of the City</div>
            <div class="sb-f-val" style="color:#7DC4FF;">{nearest}</div>
            <div class="sb-area" style="margin-top:2px;">{dist_near} mi away</div></div>
            """, unsafe_allow_html=True)

        insights = helpers.generate_insights(r, comp_df)
        if insights:
            st.markdown('<div class="sb-sec"><div class="sb-sec-title">🔍 Intelligence</div>', unsafe_allow_html=True)
            for ins in insights:
                st.markdown(f'<div class="sb-insight"><div class="sb-insight-txt">{ins}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        usp  = helpers.v(r, "Unique_Selling_Proposition_USP")
        notes= helpers.v(r, "Competitor Notes")
        rag  = helpers.v(r, "RAG_Summary")
        deep = helpers.v(r, "Deep_Search_Extra_Notes")
        intel_parts = ""
        if usp != "—": intel_parts += f"<div class='sb-f' style='margin-bottom:8px;'><div class='sb-f-lbl'>USP</div><div class='sb-text'>{usp}</div></div>"
        if notes != "—": intel_parts += f"<div class='sb-f' style='margin-bottom:8px;'><div class='sb-f-lbl'>Notes</div><div class='sb-text'>{notes}</div></div>"
        if rag != "—": intel_parts += f"<div class='sb-f' style='margin-bottom:8px;'><div class='sb-f-lbl'>RAG Summary</div><div class='sb-text'>{rag}</div></div>"
        if deep != "—": intel_parts += f"<div class='sb-f'><div class='sb-f-lbl'>Deep Search</div><div class='sb-text'>{deep}</div></div>"
        if intel_parts:
            st.markdown(f'<div class="sb-sec"><div class="sb-sec-title">🎯 Competitive Intel</div>{intel_parts}</div>', unsafe_allow_html=True)

        spec  = helpers.v(r, "Specializations")
        equip = helpers.v(r, "Key_Equipment")
        langs = helpers.v(r, "Languages_Spoken")
        spec_html  = f"<div class='sb-f' style='margin-top:6px;'><div class='sb-f-lbl'>Specializations</div><div class='sb-tags'>{helpers.tags_html(spec,sb=True)}</div></div>" if spec != "—" else ""
        equip_html = f"<div class='sb-f' style='margin-top:6px;'><div class='sb-f-lbl'>Equipment</div><div class='sb-tags'>{helpers.tags_html(equip,sb=True)}</div></div>" if equip != "—" else ""
        langs_html = f"<div class='sb-f' style='margin-top:6px;'><div class='sb-f-lbl'>Languages</div><div class='sb-tags'>{helpers.tags_html(langs,sb=True)}</div></div>" if langs != "—" else ""

        st.markdown(f"""
        <div class="sb-sec"><div class="sb-sec-title">⚕️ Services</div>
        <div class="sb-row">
            <div class="sb-f"><div class="sb-f-lbl">Telehealth</div><div class="sb-f-val">{helpers.v(r,'Telehealth')}</div></div>
            <div class="sb-f"><div class="sb-f-lbl">Home Care</div><div class="sb-f-val">{helpers.v(r,'Home_Care')}</div></div>
        </div>
        {spec_html}{equip_html}{langs_html}
        </div>
        """, unsafe_allow_html=True)

        ins_text = helpers.v(r, "_insurance")
        ins_note = helpers.v(r, "Insurance_Verification_Notes")
        st.markdown(
            f'<div class="sb-sec"><div class="sb-sec-title">🛡️ Insurance</div>'
            f'<div class="sb-tags">{helpers.tags_html(ins_text,sb=True)}</div>'
            + (f'<div class="sb-text" style="margin-top:6px;font-size:10px;color:#60A5FA;">{ins_note}</div>' if ins_note != "—" else "")
            + '</div>',
            unsafe_allow_html=True,
        )

        days = [("Mon","Mon"), ("Tue","Tue"), ("Wed","Wed"), ("Thu","Thu"), ("Fri","Fri"), ("Sat","Sat"), ("Sun","Sun")]
        boxes = ""
        for dn, dk in days:
            dv     = helpers.day_hours(r, dk)
            closed = dv in ("—", "Closed", "")
            bg  = "rgba(239,68,68,.08)" if closed else "rgba(16,185,129,.06)"
            bc  = "rgba(239,68,68,.15)" if closed else "rgba(16,185,129,.15)"
            disp = "Closed" if closed else dv.replace(" – ", "\n").replace(" AM", "a").replace(" PM", "p")
            boxes += (
                f'<div class="sb-day" style="background:{bg};border-color:{bc};">'
                f'<div class="sb-day-n">{dn}</div>'
                f'<div class="sb-day-v" style="white-space:pre-wrap;">{disp}</div></div>'
            )

        st.markdown(f"""
        <div class="sb-sec"><div class="sb-sec-title">🕐 Schedule</div>
        <div class="sb-row" style="margin-bottom:8px;">
            <div class="sb-f"><div class="sb-f-lbl">Total Hrs/Wk</div><div class="sb-f-val">{helpers.v(r,'Total Hrs/Wk')}</div></div>
            <div class="sb-f"><div class="sb-f-lbl">Wkday / Wkend</div><div class="sb-f-val">{helpers.v(r,'Weekday Hrs/Wk')} / {helpers.v(r,'Weekend Hrs/Wk')}</div></div>
        </div>
        <div class="sb-sch">{boxes}</div></div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
        if st.button("📋  Open Full Profile →", key="sb_full", use_container_width=True):
            open_clinic(name)

# ── TOP NAV ───────────────────────────────────────────────────────────────────
if st.session_state.page == "dashboard":
    page_label = "Market Intelligence"
elif st.session_state.page == "map":
    page_label = "Live Map"
elif st.session_state.page == "compare":
    page_label = "Clinic Compare"
else:
    page_label = st.session_state.clinic or ""

st.markdown(f"""
<div class="topnav">
    <div class="topnav-brand">🏥 PT of the City &nbsp;<span class="topnav-pill">Market Intelligence</span></div>
    <div class="topnav-right">
        <span><span class="live-dot"></span>Live data</span>
        <span style="color:#475569;">{len(df)} clinics</span>
        <span style="background:rgba(255,255,255,.08);padding:4px 12px;border-radius:6px;font-weight:700;color:#e2e8f0;">{page_label}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  COMPARE PAGE
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.page == "compare":
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    bc, _ = st.columns([1, 4])
    with bc:
        if st.button("← Back to Dashboard", key="cmp_back"): go_dash()

    # ── Header ──
    st.markdown("""
    <div class="cmp-hero">
        <div class="cmp-hero-icon">⚔️</div>
        <div>
            <div class="cmp-hero-title">Clinic Head-to-Head</div>
            <div class="cmp-hero-sub">Select any two clinics to reveal a full side-by-side competitive breakdown</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Selector row ──
    st.markdown('<div class="cmp-selector-wrap">', unsafe_allow_html=True)
    col_a, col_vs, col_b = st.columns([5, 1, 5])
    with col_a:
        st.markdown('<div class="cmp-selector-label cmp-label-a">⚔ Clinic A</div>', unsafe_allow_html=True)
        default_a = ALL_CLINIC_NAMES.index(st.session_state.compare_a) if st.session_state.compare_a in ALL_CLINIC_NAMES else 0
        chosen_a  = st.selectbox("Clinic A", ALL_CLINIC_NAMES, index=default_a, label_visibility="collapsed", key="cmp_sel_a")
    with col_vs:
        st.markdown('<div class="cmp-vs-badge">VS</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="cmp-selector-label cmp-label-b">⚔ Clinic B</div>', unsafe_allow_html=True)
        default_b_idx = 1 if len(ALL_CLINIC_NAMES) > 1 else 0
        if st.session_state.compare_b in ALL_CLINIC_NAMES:
            default_b_idx = ALL_CLINIC_NAMES.index(st.session_state.compare_b)
        chosen_b = st.selectbox("Clinic B", ALL_CLINIC_NAMES, index=default_b_idx, label_visibility="collapsed", key="cmp_sel_b")
    st.markdown('</div>', unsafe_allow_html=True)

    # Persist selections
    st.session_state.compare_a = chosen_a
    st.session_state.compare_b = chosen_b

    if chosen_a == chosen_b:
        st.markdown('<div class="cmp-same-warning">⚠️ Please select two different clinics to compare.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    ra = df[df["Clinic Name"] == chosen_a].iloc[0]
    rb = df[df["Clinic Name"] == chosen_b].iloc[0]

    # ── Helper: get float safely ──
    def fv(row, col):
        try:
            val = row.get(col, "")
            if pd.isna(val) or str(val).strip().lower() in ("nan", "none", ""):
                return None
            val_float = float(str(val).replace(",", "").strip())
            if math.isnan(val_float):
                return None
            return val_float
        except Exception:
            return None

    def sv(row, col):
        v = row.get(col, "")
        return str(v).strip() if pd.notna(v) and str(v).strip().lower() not in ("", "nan", "none") else "—"

    # ── Winner logic ──
    def winner(va, vb, higher_is_better=True):
        """Returns 'a', 'b', or 'tie'"""
        if va is None and vb is None: return "tie"
        if va is None: return "b"
        if vb is None: return "a"
        if va == vb:   return "tie"
        return ("a" if va > vb else "b") if higher_is_better else ("a" if va < vb else "b")

    # Pre-compute metric values
    rat_a  = fv(ra, "_rating");        rat_b  = fv(rb, "_rating")
    rev_a  = fv(ra, "_reviews");       rev_b  = fv(rb, "_reviews")
    gs_a   = fv(ra, "_google_score");  gs_b   = fv(rb, "_google_score")
    thr_a  = fv(ra, "_threat");        thr_b  = fv(rb, "_threat")
    hrs_a  = fv(ra, "Total Hrs/Wk");   hrs_b  = fv(rb, "Total Hrs/Wk")
    wknd_a = fv(ra, "Weekend Hrs/Wk"); wknd_b = fv(rb, "Weekend Hrs/Wk")
    dist_a = fv(ra, "Distance from PTotC (mi)"); dist_b = fv(rb, "Distance from PTotC (mi)")

    w_rat  = winner(rat_a,  rat_b)
    w_rev  = winner(rev_a,  rev_b)
    w_gs   = winner(gs_a,   gs_b)
    w_thr  = winner(thr_a,  thr_b, higher_is_better=False)
    w_hrs  = winner(hrs_a,  hrs_b)
    w_wknd = winner(wknd_a, wknd_b)
    w_dist = winner(dist_a, dist_b, higher_is_better=False)

    score_a = sum(1 for w in [w_rat,w_rev,w_gs,w_thr,w_hrs,w_wknd] if w == "a")
    score_b = sum(1 for w in [w_rat,w_rev,w_gs,w_thr,w_hrs,w_wknd] if w == "b")

    overall_winner = "a" if score_a > score_b else ("b" if score_b > score_a else "tie")

    def crown(side):
        return "👑 " if overall_winner == side else ""

    # ── Overall winner banner ──
    if overall_winner == "tie":
        ow_html = f"""
        <div class="cmp-banner cmp-banner-tie">
            <div class="cmp-banner-icon">🤝</div>
            <div class="cmp-banner-txt">
                <div class="cmp-banner-title">It's a Draw</div>
                <div class="cmp-banner-sub">{chosen_a} and {chosen_b} are evenly matched across key metrics</div>
            </div>
        </div>"""
    elif overall_winner == "a":
        ow_html = f"""
        <div class="cmp-banner cmp-banner-a">
            <div class="cmp-banner-icon">👑</div>
            <div class="cmp-banner-txt">
                <div class="cmp-banner-title">{chosen_a} Wins</div>
                <div class="cmp-banner-sub">Leads on {score_a} of 6 metrics vs {score_b} for {chosen_b}</div>
            </div>
        </div>"""
    else:
        ow_html = f"""
        <div class="cmp-banner cmp-banner-b">
            <div class="cmp-banner-icon">👑</div>
            <div class="cmp-banner-txt">
                <div class="cmp-banner-title">{chosen_b} Wins</div>
                <div class="cmp-banner-sub">Leads on {score_b} of 6 metrics vs {score_a} for {chosen_a}</div>
            </div>
        </div>"""
    st.markdown(ow_html, unsafe_allow_html=True)

    # ── Stat strip ──
    def stat_chip(label, val_a, val_b, w, fmt_a=None, fmt_b=None):
        fa = fmt_a if fmt_a else (f"{val_a}" if val_a is not None else "—")
        fb = fmt_b if fmt_b else (f"{val_b}" if val_b is not None else "—")
        cls_a = "cmp-chip-win" if w == "a" else ("cmp-chip-lose" if w == "b" else "")
        cls_b = "cmp-chip-win" if w == "b" else ("cmp-chip-lose" if w == "a" else "")
        win_a = "🏅 " if w == "a" else ""
        win_b = "🏅 " if w == "b" else ""
        return f"""
        <div class="cmp-chip">
            <div class="cmp-chip-val {cls_a}">{win_a}{fa}</div>
            <div class="cmp-chip-lbl">{label}</div>
            <div class="cmp-chip-val {cls_b}">{win_b}{fb}</div>
        </div>"""

    chips_html = (
        stat_chip("⭐ Rating",      rat_a,  rat_b,  w_rat,  f"{rat_a:.1f}" if rat_a is not None else "—", f"{rat_b:.1f}" if rat_b is not None else "—") +
        stat_chip("💬 Reviews",     rev_a,  rev_b,  w_rev,  f"{int(rev_a):,}" if rev_a is not None else "—", f"{int(rev_b):,}" if rev_b is not None else "—") +
        stat_chip("📊 Google Score",gs_a,   gs_b,   w_gs,   f"{gs_a:.2f}" if gs_a is not None else "—", f"{gs_b:.2f}" if gs_b is not None else "—") +
        stat_chip("⚠️ Threat",      thr_a,  thr_b,  w_thr,  f"{int(thr_a)}/5" if thr_a is not None else "—", f"{int(thr_b)}/5" if thr_b is not None else "—") +
        stat_chip("⏰ Total Hrs/Wk",hrs_a,  hrs_b,  w_hrs,  f"{hrs_a:.0f}h" if hrs_a is not None else "—", f"{hrs_b:.0f}h" if hrs_b is not None else "—") +
        stat_chip("📅 Weekend Hrs", wknd_a, wknd_b, w_wknd, f"{wknd_a:.0f}h" if wknd_a is not None else "—", f"{wknd_b:.0f}h" if wknd_b is not None else "—")
    )

    st.markdown(f"""
    <div class="cmp-chips-header">
        <div class="cmp-chip-name cmp-chip-name-a">{crown('a')}{chosen_a}</div>
        <div class="cmp-chip-name cmp-chip-name-mid">Metric</div>
        <div class="cmp-chip-name cmp-chip-name-b">{crown('b')}{chosen_b}</div>
    </div>
    <div class="cmp-chips">{chips_html}</div>
    """, unsafe_allow_html=True)

    # ── Radar chart ──
    metrics_radar = ["Rating", "Reviews (norm)", "Google Score", "Hrs/Wk (norm)", "Weekend Hrs (norm)"]
    def norm(val, max_val):
        if val is None or max_val == 0: return 0
        return min(round((val / max_val) * 5, 2), 5)

    max_rev  = max(rev_a or 0, rev_b or 0, 1)
    max_hrs  = max(hrs_a or 0, hrs_b or 0, 1)
    max_wknd = max(wknd_a or 0, wknd_b or 0, 1)

    vals_a = [rat_a or 0, norm(rev_a, max_rev), gs_a or 0, norm(hrs_a, max_hrs), norm(wknd_a, max_wknd)]
    vals_b = [rat_b or 0, norm(rev_b, max_rev), gs_b or 0, norm(hrs_b, max_hrs), norm(wknd_b, max_wknd)]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_a + [vals_a[0]], theta=metrics_radar + [metrics_radar[0]],
        fill="toself", name=chosen_a[:28],
        line=dict(color="#F0B429", width=2),
        fillcolor="rgba(240,180,41,.15)",
        marker=dict(color="#F0B429", size=7),
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_b + [vals_b[0]], theta=metrics_radar + [metrics_radar[0]],
        fill="toself", name=chosen_b[:28],
        line=dict(color="#A8B8FF", width=2),
        fillcolor="rgba(168,184,255,.13)",
        marker=dict(color="#A8B8FF", size=7),
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(17,20,51,.6)",
            radialaxis=dict(visible=True, range=[0,5], tickfont=dict(color="#5A6090", size=9), gridcolor="rgba(201,146,10,.12)", linecolor="rgba(201,146,10,.12)"),
            angularaxis=dict(tickfont=dict(color="#CDD5F3", size=11), linecolor="rgba(201,146,10,.15)", gridcolor="rgba(201,146,10,.1)"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#CDD5F3"),
        legend=dict(font=dict(color="#CDD5F3", size=11), bgcolor="rgba(17,20,51,.6)", bordercolor="rgba(201,146,10,.2)", borderwidth=1),
        margin=dict(l=40, r=40, t=40, b=40),
        height=380,
    )

    # ── Bar comparison chart ──
    bar_labels  = ["Rating (/5)", "Google Score", "Threat (/5)"]
    bar_vals_a  = [rat_a or 0, gs_a or 0, thr_a or 0]
    bar_vals_b  = [rat_b or 0, gs_b or 0, thr_b or 0]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name=chosen_a[:24], x=bar_labels, y=bar_vals_a,
        marker=dict(color="rgba(240,180,41,.85)", line=dict(color="#F0B429", width=1)),
        hovertemplate="<b>%{x}</b><br>" + chosen_a[:24] + ": %{y:.2f}<extra></extra>",
    ))
    fig_bar.add_trace(go.Bar(
        name=chosen_b[:24], x=bar_labels, y=bar_vals_b,
        marker=dict(color="rgba(168,184,255,.85)", line=dict(color="#A8B8FF", width=1)),
        hovertemplate="<b>%{x}</b><br>" + chosen_b[:24] + ": %{y:.2f}<extra></extra>",
    ))
    fig_bar.update_layout(
        barmode="group", bargap=0.25, bargroupgap=0.08,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#CDD5F3"),
        xaxis=dict(tickfont=dict(color="#CDD5F3", size=11), gridcolor="rgba(201,146,10,.08)", linecolor="rgba(201,146,10,.15)"),
        yaxis=dict(tickfont=dict(color="#5A6090", size=10), gridcolor="rgba(201,146,10,.08)", zeroline=False, linecolor="rgba(201,146,10,.15)"),
        legend=dict(font=dict(color="#CDD5F3", size=11), bgcolor="rgba(17,20,51,.6)", bordercolor="rgba(201,146,10,.2)", borderwidth=1),
        margin=dict(l=20, r=20, t=20, b=20),
        height=380,
    )

    ch_l, ch_r = st.columns(2)
    with ch_l:
        st.markdown('<div class="chart-card"><div class="chart-hdr"><span class="chart-hdr-title">Performance Radar</span><span class="chart-hdr-sub">normalized 0–5 scale</span></div><div class="chart-body">', unsafe_allow_html=True)
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False}, theme=None)
        st.markdown("</div></div>", unsafe_allow_html=True)
    with ch_r:
        st.markdown('<div class="chart-card"><div class="chart-hdr"><span class="chart-hdr-title">Key Metrics Comparison</span><span class="chart-hdr-sub">side-by-side bars</span></div><div class="chart-body">', unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False}, theme=None)
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.write("")

    # ── Deep comparison cards ──
    def cmp_row(label, val_a, val_b, w=None):
        """Render one detail row without markdown-breaking indentation"""
        cls_a = "cmp-detail-win" if w == "a" else ""
        cls_b = "cmp-detail-win" if w == "b" else ""
        badge_a = '<span class="cmp-win-dot"></span>' if w == "a" else ""
        badge_b = '<span class="cmp-win-dot cmp-win-dot-b"></span>' if w == "b" else ""
        return (
f'<div class="cmp-detail-row">'
f'<div class="cmp-detail-cell cmp-detail-a {cls_a}">{badge_a}{val_a}</div>'
f'<div class="cmp-detail-label">{label}</div>'
f'<div class="cmp-detail-cell cmp-detail-b {cls_b}">{badge_b}{val_b}</div>'
f'</div>'
        )

    def tags_compare(val):
        if not val or val == "—": return '<span style="color:#5A6090;">—</span>'
        items = [t.strip() for t in str(val).replace(";",",").split(",") if t.strip() and t.strip().lower() not in ("nan","none","")]
        return " ".join(f'<span class="cmp-tag">{t}</span>' for t in items[:8])

    # Section: Identity
    identity_rows = (
        cmp_row("🏙️ Area",       sv(ra,"Neighborhood / Area"), sv(rb,"Neighborhood / Area")) +
        cmp_row("📍 Address",     sv(ra,"Address"),            sv(rb,"Address")) +
        cmp_row("📞 Phone",       sv(ra,"Phone"),              sv(rb,"Phone")) +
        cmp_row("🌐 Website",     sv(ra,"Website"),            sv(rb,"Website")) +
        cmp_row("🏢 Parent Org",  sv(ra,"Parent Organization"),sv(rb,"Parent Organization")) +
        cmp_row("📅 Founded",     sv(ra,"Founded / Est."),     sv(rb,"Founded / Est.")) +
        cmp_row("🔗 Chain Size",  sv(ra,"Chain_Size"),         sv(rb,"Chain_Size"))
    )

    # Section: Scores
    scores_rows = (
        cmp_row("⭐ Google Rating",   f"{rat_a:.1f}"  if rat_a is not None else "—", f"{rat_b:.1f}"  if rat_b is not None else "—", w_rat) +
        cmp_row("💬 Reviews",         f"{int(rev_a):,}" if rev_a is not None else "—", f"{int(rev_b):,}" if rev_b is not None else "—", w_rev) +
        cmp_row("📊 Google Score",    f"{gs_a:.2f}"   if gs_a is not None else "—", f"{gs_b:.2f}"   if gs_b is not None else "—", w_gs) +
        cmp_row("⭐ Yelp Rating",     sv(ra,"Yelp_Rating"),  sv(rb,"Yelp_Rating")) +
        cmp_row("⚠️ Threat Level",   f"{int(thr_a)}/5" if thr_a is not None else "—", f"{int(thr_b)}/5" if thr_b is not None else "—", w_thr) +
        cmp_row("📏 Distance (mi)",   f"{dist_a:.1f}" if dist_a is not None else "—", f"{dist_b:.1f}" if dist_b is not None else "—", w_dist) +
        cmp_row("🏥 Daily Volume",    sv(ra,"Estimated_Daily_Volume"), sv(rb,"Estimated_Daily_Volume"))
    )

    # Section: Services
    services_rows = (
        cmp_row("💻 Telehealth",   sv(ra,"Telehealth"),  sv(rb,"Telehealth")) +
        cmp_row("🏠 Home Care",    sv(ra,"Home_Care"),   sv(rb,"Home_Care")) +
        cmp_row("🌍 Languages",    tags_compare(sv(ra,"Languages_Spoken")), tags_compare(sv(rb,"Languages_Spoken"))) +
        cmp_row("⚕️ Specializations", tags_compare(sv(ra,"Specializations")), tags_compare(sv(rb,"Specializations"))) +
        cmp_row("🔧 Key Equipment", tags_compare(sv(ra,"Key_Equipment")), tags_compare(sv(rb,"Key_Equipment")))
    )

    # Section: Schedule
    schedule_rows = (
        cmp_row("⏰ Total Hrs/Wk",   f"{hrs_a:.0f}h"  if hrs_a is not None else "—", f"{hrs_b:.0f}h"  if hrs_b is not None else "—", w_hrs) +
        cmp_row("📅 Weekend Hrs/Wk", f"{wknd_a:.0f}h" if wknd_a is not None else "—", f"{wknd_b:.0f}h" if wknd_b is not None else "—", w_wknd) +
        cmp_row("🗓️ Weekday Hrs/Wk", sv(ra,"Weekday Hrs/Wk"), sv(rb,"Weekday Hrs/Wk")) +
        "".join(cmp_row(day, helpers.day_hours(ra, day), helpers.day_hours(rb, day)) for day in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
    )

    # Section: Insurance
    ins_rows = (
        cmp_row("🛡️ Insurances", tags_compare(sv(ra,"_insurance")), tags_compare(sv(rb,"_insurance"))) +
        cmp_row("📝 Notes", sv(ra,"Insurance_Verification_Notes"), sv(rb,"Insurance_Verification_Notes"))
    )

    # Section: Intelligence
    intel_rows = (
        cmp_row("🎯 USP",       sv(ra,"Unique_Selling_Proposition_USP"), sv(rb,"Unique_Selling_Proposition_USP")) +
        cmp_row("📋 Notes",     sv(ra,"Competitor Notes"), sv(rb,"Competitor Notes")) +
        cmp_row("🤖 RAG Summary",sv(ra,"RAG_Summary"),    sv(rb,"RAG_Summary")) +
        cmp_row("✓ Strengths",  sv(ra,"Strengths"),        sv(rb,"Strengths")) +
        cmp_row("✗ Weaknesses", sv(ra,"Weaknesses"),       sv(rb,"Weaknesses"))
    )

    def detail_section(icon, title, rows_html):
        return (
f'<div class="cmp-section">'
f'<div class="cmp-section-hdr">'
f'<span class="cmp-section-icon">{icon}</span>'
f'<span class="cmp-section-title">{title}</span>'
f'</div>'
f'<div class="cmp-detail-header">'
f'<div class="cmp-detail-name-a">{"👑 " if overall_winner=="a" else ""}{chosen_a}</div>'
f'<div class="cmp-detail-name-mid"> </div>'
f'<div class="cmp-detail-name-b">{"👑 " if overall_winner=="b" else ""}{chosen_b}</div>'
f'</div>'
f'{rows_html}'
f'</div>'
        )

    st.markdown(
        detail_section("🏢", "Identity & Location", identity_rows) +
        detail_section("📊", "Ratings & Scores", scores_rows) +
        detail_section("⚕️", "Services & Capabilities", services_rows) +
        detail_section("🕐", "Schedule & Hours", schedule_rows) +
        detail_section("🛡️", "Insurance Coverage", ins_rows) +
        detail_section("🔍", "Competitive Intelligence", intel_rows),
        unsafe_allow_html=True,
    )

    # ── Quick-open profile buttons ──
    st.write("")
    bl, br = st.columns(2)
    with bl:
        if st.button(f"📋 Open Full Profile: {chosen_a[:30]}…", key="cmp_open_a", use_container_width=True):
            open_clinic(chosen_a)
    with br:
        if st.button(f"📋 Open Full Profile: {chosen_b[:30]}…", key="cmp_open_b", use_container_width=True):
            open_clinic(chosen_b)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
#  PROFILE PAGE
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "profile" and st.session_state.clinic:
    rows = df[df["Clinic Name"] == st.session_state.clinic]
    if rows.empty:
        st.warning("Clinic not found.")
        st.stop()
    r      = rows.iloc[0]
    is_us  = r["_is_us"]
    t_val  = r["_threat"]
    gs_val = r["_google_score"]

    st.markdown('<div class="profile-wrap">', unsafe_allow_html=True)
    bc, _ = st.columns([1, 4])
    with bc:
        if st.button("← Back to Dashboard"): go_dash()

    website = helpers.v(r, "Website"); gmaps = helpers.v(r, "Google Maps Link"); social = helpers.v(r, "Social_Media")
    wb  = f'<a href="{("https://"+website) if not website.startswith("http") else website}" target="_blank"><button class="btn-p">🌐 Website</button></a>' if website != "—" and "Not found" not in website else ""
    mb  = f'<a href="{gmaps}" target="_blank"><button class="btn-o">📍 Maps</button></a>' if gmaps.startswith("http") else ""
    sb2 = f'<a href="{social}" target="_blank"><button class="btn-o">📱 Social</button></a>' if social.startswith("http") else ""

    st.markdown(f"""
    <div class="profile-hdr">
        <div>
            <div style="margin-bottom:10px;">{helpers.threat_badge(t_val,is_us)} {helpers.flag_badge(r)}</div>
            <div class="profile-title">{helpers.v(r,'Clinic Name')}</div>
            <div class="profile-meta">
                <div class="profile-meta-item">📍 {helpers.v(r,'Address')}</div>
                <div class="profile-meta-item">🏙️ {helpers.v(r,'Neighborhood / Area')}</div>
                <div class="profile-meta-item">📞 {helpers.v(r,'Phone')}</div>
                <div class="profile-meta-item">📮 {helpers.v(r,'Zip_Code')}</div>
            </div>
        </div>
        <div class="profile-actions">{wb}{mb}{sb2}</div>
    </div>
    """, unsafe_allow_html=True)

    yelp = helpers.v(r, "Yelp_Rating")
    yd   = f"⭐ {yelp}" if yelp != "—" else "—"
    gs_display = helpers.fmt_gscore(gs_val)

    def ps(lbl, val, highlight=False):
        style = ' style="color:#15803D;"' if highlight else ''
        return f'<div class="pstat"><div class="pstat-val"{style}>{val}</div><div class="pstat-lbl">{lbl}</div></div>'

    st.markdown(f"""
    <div class="pstats">
        {ps("Google Rating", f"⭐ {helpers.v(r,'Google Rating')}")}
        {ps("Reviews", helpers.v(r,'# Reviews'))}
        {ps("Google Score", f"📊 {gs_display}", highlight=True)}
        {ps("Yelp", yd)}
        {ps("Threat", helpers.v(r,'Competitive_Threat_1to5')+"/5")}
        {ps("Daily Volume", helpers.v(r,'Estimated_Daily_Volume'))}
        {ps("Distance", helpers.v(r,'Distance from PTotC (mi)')+" mi")}
    </div>
    """, unsafe_allow_html=True)

    ins2 = helpers.generate_insights(r, comp_df)
    if ins2:
        html = "".join(f'<div class="insight-item">{i}</div>' for i in ins2)
        st.markdown(f'<div class="insight-box"><div class="insight-box-title">🔍 Quick Intelligence</div>{html}</div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5, t6 = st.tabs(["Intelligence", "Competitive View", "Services", "Insurance", "Schedule", "About"])

    with t1:
        st.write("")
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="info-card"><div class="info-card-title">Unique Selling Proposition</div><div class="info-card-body">{helpers.v(r,"Unique_Selling_Proposition_USP")}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="info-card"><div class="info-card-title">Competitor Notes</div><div class="info-card-body">{helpers.v(r,"Competitor Notes")}</div></div>', unsafe_allow_html=True)
        
        st.write("")
        c3, c4 = st.columns(2)
        with c3: st.markdown(f'<div class="info-card"><div class="info-card-title">RAG Summary</div><div class="info-card-body">{helpers.v(r,"RAG_Summary")}</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="info-card"><div class="info-card-title">Deep Search Notes</div><div class="info-card-body">{helpers.v(r,"Deep_Search_Extra_Notes")}</div></div>', unsafe_allow_html=True)

        st.write("")
        c_str, c_wk = st.columns(2)
        with c_str:
            st.markdown(f'<div class="info-card" style="border-top:3px solid #10B981;"><div class="info-card-title" style="color:#10B981;">✓ Strengths</div><div class="info-card-body" style="white-space:pre-wrap;">{helpers.v(r,"Strengths")}</div></div>', unsafe_allow_html=True)
        with c_wk:
            st.markdown(f'<div class="info-card" style="border-top:3px solid #EF4444;"><div class="info-card-title" style="color:#EF4444;">✗ Weaknesses</div><div class="info-card-body" style="white-space:pre-wrap;">{helpers.v(r,"Weaknesses")}</div></div>', unsafe_allow_html=True)

        st.write("")
        nearest   = helpers.v(r, "Nearest_PT_of_The_City")
        dist_near = helpers.v(r, "Distance_to_Nearest_PTotC_miles")
        if nearest != "—":
            st.markdown(f"""
            <div class="info-card" style="background:linear-gradient(135deg,#EFF6FF,#F0FDF4);">
                <div class="info-card-title">🏥 Nearest PT of the City Location</div>
                <div class="info-card-body"><b>{nearest}</b> &nbsp;·&nbsp; {dist_near} miles away</div>
            </div>
            """, unsafe_allow_html=True)

        if pd.notna(r["Latitude"]) and pd.notna(r["Longitude"]):
            st.write("")
            if is_us: cc = "#2563EB"
            elif t_val and t_val >= 4: cc = "#DC2626"
            elif t_val == 3: cc = "#F59E0B"
            else: cc = "#60A5FA"
            mm = folium.Map(location=[r["Latitude"], r["Longitude"]], zoom_start=15, tiles="CartoDB Positron")
            folium.CircleMarker(
                location=[r["Latitude"], r["Longitude"]], radius=14,
                color=cc, fill=True, fill_color=cc, fill_opacity=0.85, tooltip=helpers.v(r, "Clinic Name"),
            ).add_to(mm)
            for _, nr in df.iterrows():
                if nr["Clinic Name"] == r["Clinic Name"] or pd.isna(nr["Latitude"]) or pd.isna(nr["Longitude"]): continue
                nc = "#2563EB" if nr["_is_us"] else "#94A3B8"
                folium.CircleMarker(
                    location=[nr["Latitude"], nr["Longitude"]], radius=5,
                    color=nc, fill=True, fill_color=nc, fill_opacity=0.5, tooltip=nr["Clinic Name"],
                ).add_to(mm)
            st_folium(mm, width="100%", height=280)

    with t2:
        st.write("")
        area = r.get("Neighborhood / Area", "")
        adf  = df[df["Neighborhood / Area"] == area] if area else df
        cl, cr = st.columns([1.2, 1])
        with cl:
            st.markdown('<div class="chart-card"><div class="chart-hdr"><span class="chart-hdr-title">Rating Comparison</span><span class="chart-hdr-sub">vs same area</span></div><div class="chart-body">', unsafe_allow_html=True)
            cn  = adf["Clinic Name"].tolist()
            rb2 = adf["_rating"].tolist()
            iu  = adf["_is_us"].tolist()
            bc2 = ["#2563EB" if u else "#E2E8F0" for u in iu]
            bb2 = ["#2563EB" if u else "#94A3B8" for u in iu]
            fig_rb = go.Figure(go.Bar(
                x=rb2, y=cn, orientation="h",
                marker=dict(color=bc2, line=dict(color=bb2, width=1)), hovertemplate="<b>%{y}</b>: %{x:.1f}⭐<extra></extra>",
            ))
            fig_rb.update_layout(
                **config.PL, height=max(220, len(cn) * 34),
                xaxis=dict(range=[0, 5.5], dtick=1, tickfont_size=10, gridcolor="#F1F5F9"),
                yaxis=dict(tickfont_size=10), bargap=0.35, showlegend=False,
            )
            st.plotly_chart(fig_rb, width="stretch", config={"displayModeBar": False}, theme=None)
            st.markdown("</div></div>", unsafe_allow_html=True)
        with cr:
            sa = adf.sort_values("_rating", ascending=False).reset_index(drop=True)
            try: rank = sa[sa["Clinic Name"] == r["Clinic Name"]].index[0] + 1
            except Exception: rank = "—"
            st.markdown(f'<div class="rank-card"><div class="rank-num">#{rank}</div><div class="rank-lbl">Rank by Rating</div><div class="rank-ctx">out of {len(adf)} clinics in {area}</div></div>', unsafe_allow_html=True)
            st.write("")
            st.markdown(f'<div class="info-card"><div class="info-card-title">Rating Breakdown</div>{helpers.star_bar(helpers.v(r,"Google Rating"))}<div style="margin-top:12px;font-size:12px;color:#64748B;"><b style="color:#0F1E3D;">{helpers.v(r,"# Reviews")}</b> reviews · Yelp: <b style="color:#0F1E3D;">{yd}</b> · Google Score: <b style="color:#15803D;">{gs_display}</b></div></div>', unsafe_allow_html=True)

    with t3:
        st.write("")
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="info-card"><div class="info-card-title">Specializations</div><div class="tags">{helpers.tags_html(helpers.v(r,"Specializations"))}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="info-card"><div class="info-card-title">Key Equipment</div><div class="tags">{helpers.tags_html(helpers.v(r,"Key_Equipment"))}</div></div>', unsafe_allow_html=True)
        st.write("")
        c3, c4 = st.columns(2)
        with c3: st.markdown(f'<div class="info-card"><div class="info-card-title">Languages</div><div class="tags">{helpers.tags_html(helpers.v(r,"Languages_Spoken"))}</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="info-card"><div class="info-card-title">Additional Services</div><div class="dg"><div class="di"><div class="di-lbl">Telehealth</div><div class="di-val">{helpers.v(r,"Telehealth")}</div></div><div class="di"><div class="di-lbl">Home Care</div><div class="di-val">{helpers.v(r,"Home_Care")}</div></div></div></div>', unsafe_allow_html=True)

    with t4:
        st.write("")
        ins_text = helpers.v(r, "_insurance")
        ins_raw  = helpers.v(r, "Insurances_Accepted_Clean")
        ins_note = helpers.v(r, "Insurance_Verification_Notes")
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="info-card"><div class="info-card-title">Insurances Accepted</div><div class="tags">{helpers.tags_html(ins_text)}</div></div>', unsafe_allow_html=True)
        with c2:
            note_html = f'<div style="margin-top:12px;font-size:11px;color:#64748B;border-top:1px solid #F1F5F9;padding-top:10px;"><b>Verification Notes:</b> {ins_note}</div>' if ins_note != "—" else ""
            st.markdown(f'<div class="info-card"><div class="info-card-title">Insurance Details</div><div class="info-card-body" style="font-size:12px;">{ins_raw}{note_html}</div></div>', unsafe_allow_html=True)

    with t5:
        st.write("")
        chips2 = "".join(f'<div class="di"><div class="di-lbl">{d}</div><div class="di-val" style="font-size:12px;">{helpers.day_hours(r, d)}</div></div>' for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-title">Weekly Hours</div>
            <div class="dg" style="margin-bottom:16px;">
                <div class="di"><div class="di-lbl">Total Hrs/Wk</div><div class="di-val">{helpers.v(r,"Total Hrs/Wk")}</div></div>
                <div class="di"><div class="di-lbl">Weekend Hrs</div><div class="di-val">{helpers.v(r,"Weekend Hrs/Wk")}</div></div>
                <div class="di"><div class="di-lbl">Weekend Advantage</div><div class="di-val">{helpers.v(r,"Weekend_Advantage")}</div></div>
            </div>
            <div class="dg">{chips2}</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.code(helpers.v(r, "Full Weekly Schedule", "Not available"), language=None)

    with t6:
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="info-card"><div class="info-card-title">Organization</div>
            <div class="dg">
                <div class="di"><div class="di-lbl">Parent Org</div><div class="di-val">{helpers.v(r,'Parent Organization')}</div></div>
                <div class="di"><div class="di-lbl">Owner/Founder</div><div class="di-val">{helpers.v(r,'Owner_Founder')}</div></div>
                <div class="di"><div class="di-lbl">Established</div><div class="di-val">{helpers.v(r,'Founded / Est.')}</div></div>
                <div class="di"><div class="di-lbl">Chain Size</div><div class="di-val">{helpers.v(r,'Chain_Size')}</div></div>
                <div class="di"><div class="di-lbl">Zip Code</div><div class="di-val">{helpers.v(r,'Zip_Code')}</div></div>
            </div></div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="info-card"><div class="info-card-title">Information Sources</div><div class="info-card-body" style="word-break:break-all;font-size:12px;">{helpers.v(r,"Information_Sources (URLs)")}</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
#  MAP PAGE
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "map":
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    bc, _ = st.columns([1, 4])
    with bc:
        if st.button("← Back to Dashboard", key="map_back_btn"): go_dash()

    st.markdown("""
    <div class="map-card">
      <div class="map-hdr">
        <span>📍 Clinic Map &nbsp;<span style="font-size:11px;color:#94A3B8;font-weight:500;">hover = info · click a pin = open side panel</span></span>
        <div class="map-legend">
          <span><span class="dot" style="background:#2563EB"></span>PT of the City</span>
          <span><span class="dot" style="background:#DC2626"></span>Critical</span>
          <span><span class="dot" style="background:#F59E0B"></span>High</span>
          <span><span class="dot" style="background:#EAB308"></span>Medium</span>
          <span><span class="dot" style="background:#60A5FA"></span>Low</span>
          <span><span class="dot" style="background:#CBD5E1"></span>Unknown</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    search_q, f_area, f_threat, f_ins, show_us, sort_by = render_filter_widgets("map")
    fdf_map = helpers.apply_filters(df, search_q, f_area, f_threat, f_ins, show_us, sort_by)

    m = folium.Map(location=[40.75, -73.99], zoom_start=11, tiles="CartoDB Positron")
    for _, row in fdf_map.iterrows():
        if pd.isna(row["Latitude"]) or pd.isna(row["Longitude"]): continue
        if row["_is_us"]: c, sz = "#2563EB", 12
        else:
            t = row["_threat"]
            if pd.isna(t) or t is None:   c, sz = "#CBD5E1", 6
            elif t >= 5:                  c, sz = "#DC2626", 10
            elif t >= 4:                  c, sz = "#F59E0B", 9
            elif t == 3:                  c, sz = "#EAB308", 7
            else:                         c, sz = "#60A5FA", 6
        try:
            ti = int(float(row["_threat"]))
            tl = {5: "Critical", 4: "High", 3: "Medium", 2: "Low", 1: "Minimal"}.get(ti, "Unknown")
        except Exception:
            tl = "Unknown"

        gs_tip  = helpers.fmt_gscore(row.get("_google_score"))
        gs_line = f"<span style='font-size:11px;color:#64748B;'>Google Score: <b style='color:#15803D;'>{gs_tip}</b></span><br>" if gs_tip != "—" else ""
        ins_prev = str(row.get("_insurance", ""))[:70]
        sp_prev  = str(row.get("Specializations", ""))[:55]
        nearest  = str(row.get("Nearest_PT_of_The_City", ""))
        nearest_line = f"<span style='font-size:10px;color:#60A5FA;'>🏥 Nearest us: {nearest}</span><br>" if nearest and nearest not in ("", "nan") else ""

        tip = (
            f"<div style='font-family:Inter,sans-serif;padding:12px 14px;min-width:220px;max-width:290px;'>"
            f"<b style='font-size:13px;color:#0F1E3D;'>{row['Clinic Name']}</b><br>"
            f"<span style='color:#64748B;font-size:11px;'>📍 {row.get('Neighborhood / Area','')}</span><br><br>"
            f"<span style='font-size:12px;'>⭐ {row['_rating'] if pd.notna(row['_rating']) else 'N/A'} &nbsp;·&nbsp; {int(row['_reviews']) if pd.notna(row['_reviews']) else 0} reviews</span><br>"
            f"{gs_line}"
            f"<span style='font-size:11px;color:#64748B;'>Threat: <b>{tl}</b> · {row.get('Estimated_Daily_Volume','—')}</span><br>"
            f"{nearest_line}"
            f"<div style='margin-top:6px;font-size:10px;color:#94A3B8;border-top:1px solid #F1F5F9;padding-top:5px;'>"
            f"<b>Insurance:</b> {ins_prev}…<br><b>Specs:</b> {sp_prev}</div>"
            f"<div style='margin-top:5px;font-size:10px;color:#2563EB;font-weight:700;'>Click → Open side panel</div></div>"
        )
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=sz, color=c, fill=True, fill_color=c, fill_opacity=0.88, weight=2,
            tooltip=folium.Tooltip(tip, permanent=False, sticky=True),
            popup=folium.Popup(row["Clinic Name"], max_width=1),
        ).add_to(m)

    map_data = st_folium(m, width="100%", height=560, key="main_map", returned_objects=["last_object_clicked_tooltip", "last_object_clicked_popup"])

    clicked = None
    if map_data:
        pv = map_data.get("last_object_clicked_popup")
        if pv and isinstance(pv, dict): clicked = pv.get("__html", "").replace("<div>", "").replace("</div>", "").strip()
        elif pv and isinstance(pv, str): clicked = pv.strip()

    if clicked and clicked in df["Clinic Name"].values:
        if st.session_state.selected_clinic != clicked:
            st.session_state.selected_clinic = clicked
            st.rerun()

    if st.session_state.selected_clinic: render_sidebar(st.session_state.selected_clinic)

    st.markdown(f'<div class="sec-pill" style="display:inline-block;margin-top:4px;">{len(fdf_map)} clinics shown</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

avg_us   = round(us_df["_rating"].mean(),   2) if not us_df["_rating"].isna().all()   else "—"
avg_comp = round(comp_df["_rating"].mean(), 2) if not comp_df["_rating"].isna().all() else "—"
high_t   = len(comp_df[comp_df["_threat"] >= 4])
cov      = df["Neighborhood / Area"].nunique()

try:
    dr = round(float(avg_us) - float(avg_comp), 2) if avg_us != "—" and avg_comp != "—" else None
    if dr is not None and not pd.isna(dr):
        dhtml = f'<div class="stat-delta {"delta-up" if dr>=0 else "delta-dn"}">{"▲" if dr>=0 else "▼"} {abs(dr):.2f} vs competitors</div>'
    else:
        dhtml = ""
except Exception:
    dhtml = ""

st.markdown(f"""
<div class="stat-row">
    <div class="stat-card c1"><div class="stat-icon">🏥</div><div class="stat-lbl">Total Clinics</div><div class="stat-val">{len(df)}</div><div class="stat-sub">{len(us_df)} ours · {len(comp_df)} competitors</div></div>
    <div class="stat-card c2"><div class="stat-icon">⚠️</div><div class="stat-lbl">Critical / High Threat</div><div class="stat-val">{high_t}</div><div class="stat-sub">Threat level 4–5 — priority monitoring</div></div>
    <div class="stat-card c3"><div class="stat-icon">⭐</div><div class="stat-lbl">Our Avg Rating</div><div class="stat-val">{avg_us}</div>{dhtml}</div>
    <div class="stat-card c4"><div class="stat-icon">📍</div><div class="stat-lbl">Neighborhoods</div><div class="stat-val">{cov}</div><div class="stat-sub">Distinct areas tracked</div></div>
    <div class="stat-card c5"><div class="stat-icon">🏆</div><div class="stat-lbl">Comp Avg Rating</div><div class="stat-val">{avg_comp}</div><div class="stat-sub">All {len(comp_df)} competitors</div></div>
</div>
""", unsafe_allow_html=True)

# ── CTA Banners ──
col_map, col_cmp = st.columns(2)
with col_map:
    st.markdown(f"""
    <div class="map-cta-banner">
        <div class="map-cta-icon">🗺️</div>
        <div class="map-cta-text">
            <div class="map-cta-title">Interactive Market Map</div>
            <div class="map-cta-sub">Plot all {len(df)} clinics across NYC, filter by area / threat / insurance.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🗺️  OPEN LIVE MARKET MAP  →", type="primary", use_container_width=True, key="goto_map_btn"): go_map()

with col_cmp:
    st.markdown(f"""
    <div class="map-cta-banner" style="border-color:rgba(168,184,255,.55);box-shadow:0 8px 40px rgba(0,0,0,.5),0 0 60px rgba(168,184,255,.12);">
        <div class="map-cta-icon">⚔️</div>
        <div class="map-cta-text">
            <div class="map-cta-title">Clinic Head-to-Head</div>
            <div class="map-cta-sub">Pick any two clinics for a full side-by-side competitive breakdown.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚔️  COMPARE TWO CLINICS  →", use_container_width=True, key="goto_cmp_btn"): go_compare()

st.write("")
st.markdown('<div class="sec-hdr"><div class="sec-title">Market Analytics</div><div class="sec-pill">NYC Physical Therapy Landscape</div></div>', unsafe_allow_html=True)

ch1, ch2, ch3 = st.columns([1, 1.35, 1.35])
with ch1:
    st.markdown('<div class="chart-card"><div class="chart-hdr"><span class="chart-hdr-title">Threat Distribution</span><span class="chart-hdr-sub">all competitors</span></div><div class="chart-body">', unsafe_allow_html=True)
    st.plotly_chart(charts.chart_threat_donut(df), width="stretch", config={"displayModeBar": False}, theme=None)
    st.markdown("</div></div>", unsafe_allow_html=True)

with ch2:
    st.markdown('<div class="chart-card"><div class="chart-hdr"><span class="chart-hdr-title">Clinics by Borough</span><span class="chart-hdr-sub">PT of the City vs competitors</span></div><div class="chart-body">', unsafe_allow_html=True)
    fb = charts.chart_borough_breakdown(df)
    if fb: st.plotly_chart(fb, width="stretch", config={"displayModeBar": False}, theme=None)
    else: st.markdown('<div style="padding:20px;color:#94A3B8;text-align:center;">No data</div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

with ch3:
    st.markdown('<div class="chart-card"><div class="chart-hdr"><span class="chart-hdr-title">Top 20 Competitors</span><span class="chart-hdr-sub">by review count · color = threat level</span></div><div class="chart-body">', unsafe_allow_html=True)
    ft = charts.chart_top20_reviews(df)
    if ft: st.plotly_chart(ft, width="stretch", config={"displayModeBar": False}, theme=None)
    else: st.markdown('<div style="padding:20px;color:#94A3B8;text-align:center;">No data</div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

st.write("")
st.markdown('<div class="sec-hdr"><div class="sec-title">🏆 Top 7 Competitor Clinics in NYC</div><div class="sec-pill">Strength &amp; Weakness Analysis</div></div>', unsafe_allow_html=True)

rank_cls      = {1: "r1", 2: "r2", 3: "r3"}
threat_labels = {5: "Critical", 4: "High", 3: "Medium", 2: "Low", 1: "Minimal"}

st.markdown("""
<div class="t7-wrap">
  <div class="t7-hdr">
    <span>#</span>
    <span>Clinic</span>
    <span>Rating</span>
    <span>✓ Strengths</span>
    <span>✗ Weaknesses</span>
  </div>
""", unsafe_allow_html=True)

for cl in config.TOP7_DATA:
    rk = cl["rank"]
    ti = cl["threat"]
    tl = threat_labels.get(ti, "")
    strengths_html  = "".join(f'<div class="t7-point s">{s}</div>' for s in cl["strengths"])
    weaknesses_html = "".join(f'<div class="t7-point w">{w}</div>' for w in cl["weaknesses"])
    st.markdown(f"""
    <div class="t7-row">
      <div class="t7-rank {rank_cls.get(rk,'')}">{rk}</div>
      <div>
        <div class="t7-clinic-name">{cl['name']}</div>
        <div class="t7-area">📍 {cl['area']}</div>
        <div style="margin-top:6px;"><span class="badge b{ti}" style="font-size:9px;">{tl}</span></div>
      </div>
      <div>
        <div class="t7-rating">⭐ {cl['rating']}</div>
        <div class="t7-reviews">💬 {cl['reviews']} reviews</div>
      </div>
      <div class="t7-strengths-col">
        <div class="t7-section-label" style="color:#10B981;">✓ Strengths</div>
        {strengths_html}
      </div>
      <div class="t7-weaknesses-col">
        <div class="t7-section-label" style="color:#EF4444;">✗ Weaknesses</div>
        {weaknesses_html}
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.write("")

st.markdown('<div class="sec-hdr"><div class="sec-title">All Clinics</div><div class="sec-pill">Filter and browse the full roster</div></div>', unsafe_allow_html=True)

search_q, f_area, f_threat, f_ins, show_us, sort_by = render_filter_widgets("dash")
fdf = helpers.apply_filters(df, search_q, f_area, f_threat, f_ins, show_us, sort_by)

st.markdown(f'<div class="sec-hdr" style="margin-top:-4px;"><div></div><div class="sec-pill">{len(fdf)} results</div></div>', unsafe_allow_html=True)
st.markdown('<div class="tbl-wrap"><div class="tbl-head"><span>Clinic Name</span><span>Neighborhood</span><span>Rating</span><span>Reviews</span><span>G. Score</span><span>Threat</span><span></span></div>', unsafe_allow_html=True)

for i, (_, row) in enumerate(fdf.iterrows()):
    name   = row["Clinic Name"]
    iu     = row["_is_us"]
    t      = row["_threat"]
    area   = row["Neighborhood / Area"] or "—"
    rating = f"⭐ {row['_rating']}" if pd.notna(row["_rating"]) else "—"
    revs   = f"{int(row['_reviews']):,}" if pd.notna(row["_reviews"]) else "—"
    gscore = helpers.fmt_gscore(row.get("_google_score"))
    bdg    = helpers.threat_badge(t, iu)
    nc     = "row-name us" if iu else "row-name"

    c1, c2, c3, c4, c5, c6, c7 = st.columns([2.5, 1.5, 0.8, 0.8, 0.8, 1, 0.7])
    c1.markdown(f'<div class="{nc}">{name}</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="row-cell">{area}</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="row-cell" style="font-weight:700;color:#0F1E3D;">{rating}</div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="row-cell">{revs}</div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="row-cell" style="font-weight:700;color:#15803D;">{gscore}</div>', unsafe_allow_html=True)
    c6.markdown(f'<div class="row-cell">{bdg}</div>', unsafe_allow_html=True)
    with c7:
        st.write("")
        if st.button("View →", key=f"v_{name}_{i}", width="stretch"): open_clinic(name)
    if i < len(fdf) - 1:
        st.markdown('<div class="div-row"></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.write("")
st.markdown('</div>', unsafe_allow_html=True)
# Trigger Railway Rebuild
