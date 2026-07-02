import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="PT of the City | Market Intelligence",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="auto",
)

DATA_FILE = "Clinics_with_Insurances_Final.csv"

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{font-family:'Inter',-apple-system,sans-serif;font-size:14px;}
.stApp{background:#EDF0F7;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:0!important;max-width:100%!important;}
div[data-testid="stVerticalBlock"]>div{gap:0!important;}

/* NAV */
.topnav{background:linear-gradient(135deg,#0F1E3D 0%,#1B2A4A 60%,#1E3460 100%);padding:0 36px;height:64px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:999;box-shadow:0 2px 20px rgba(0,0,0,.25);}
.topnav-brand{color:#fff;font-size:16px;font-weight:800;letter-spacing:-.03em;display:flex;align-items:center;gap:12px;}
.topnav-pill{background:rgba(37,99,235,.3);border:1px solid rgba(74,158,255,.35);color:#7DC4FF;font-size:11px;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:.05em;text-transform:uppercase;}
.topnav-right{display:flex;align-items:center;gap:20px;color:#94A3B8;font-size:12px;}
.live-dot{width:7px;height:7px;background:#10B981;border-radius:50%;box-shadow:0 0 0 2px rgba(16,185,129,.25);animation:pulse 2s infinite;display:inline-block;margin-right:5px;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 2px rgba(16,185,129,.25);}50%{box-shadow:0 0 0 6px rgba(16,185,129,.06);}}

/* PAGE */
.page-wrap{padding:28px 32px;max-width:1520px;margin:0 auto;}

/* KPI */
.stat-row{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:24px;}
.stat-card{background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:20px 22px;display:flex;flex-direction:column;gap:5px;box-shadow:0 1px 4px rgba(0,0,0,.04),0 4px 16px rgba(0,0,0,.03);position:relative;overflow:hidden;}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;}
.stat-card.c1::before{background:linear-gradient(90deg,#2563EB,#60A5FA);}
.stat-card.c2::before{background:linear-gradient(90deg,#DC2626,#F87171);}
.stat-card.c3::before{background:linear-gradient(90deg,#10B981,#6EE7B7);}
.stat-card.c4::before{background:linear-gradient(90deg,#F59E0B,#FCD34D);}
.stat-card.c5::before{background:linear-gradient(90deg,#8B5CF6,#C4B5FD);}
.stat-icon{position:absolute;top:14px;right:18px;font-size:24px;opacity:.1;}
.stat-lbl{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:#64748B;}
.stat-val{font-size:32px;font-weight:900;color:#0F1E3D;line-height:1;letter-spacing:-.03em;}
.stat-sub{font-size:11px;color:#94A3B8;}
.stat-delta{font-size:11px;font-weight:700;margin-top:2px;}
.delta-up{color:#10B981;}.delta-dn{color:#EF4444;}

/* SECTION HEADER */
.sec-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;}
.sec-title{font-size:16px;font-weight:800;color:#0F1E3D;letter-spacing:-.02em;}
.sec-pill{font-size:11px;color:#64748B;background:#F1F5F9;padding:4px 12px;border-radius:20px;font-weight:600;border:1px solid #E2E8F0;}

/* CHART CARD */
.chart-card{background:#fff;border:1px solid #E2E8F0;border-radius:14px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.04),0 4px 16px rgba(0,0,0,.03);}
.chart-hdr{padding:16px 20px 12px;border-bottom:1px solid #F1F5F9;display:flex;align-items:baseline;gap:8px;}
.chart-hdr-title{font-size:13px;font-weight:800;color:#0F1E3D;}
.chart-hdr-sub{font-size:11px;color:#94A3B8;}
.chart-body{padding:4px 8px 8px;}

/* MAP */
.map-card{background:#fff;border:1px solid #E2E8F0;border-radius:14px;overflow:hidden;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,.04);}
.map-hdr{padding:14px 20px;border-bottom:1px solid #F1F5F9;font-size:13px;font-weight:800;color:#0F1E3D;display:flex;align-items:center;justify-content:space-between;background:#FAFBFD;}
.map-legend{display:flex;gap:14px;flex-wrap:wrap;}
.map-legend span{font-size:11px;color:#64748B;display:flex;align-items:center;gap:5px;font-weight:600;}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block;}

/* MAP CTA BANNER */
.map-cta-banner{background:linear-gradient(135deg,#0F1E3D 0%,#1B2A4A 55%,#1E3A6E 100%);border-radius:16px;padding:26px 32px;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;gap:24px;box-shadow:0 8px 28px rgba(15,30,61,.25);position:relative;overflow:hidden;}
.map-cta-banner::after{content:'';position:absolute;top:-50%;right:-8%;width:280px;height:280px;background:radial-gradient(circle,rgba(74,158,255,.20),transparent 70%);}
.map-cta-icon{font-size:34px;line-height:1;position:relative;z-index:1;}
.map-cta-text{position:relative;z-index:1;flex:1;}
.map-cta-title{font-size:18px;font-weight:800;color:#fff;letter-spacing:-.02em;margin-bottom:5px;}
.map-cta-sub{font-size:12.5px;color:#94A3B8;max-width:620px;line-height:1.55;}

/* Primary button override */
button[kind="primary"]{
    background:linear-gradient(135deg,#2563EB,#3B82F6)!important;
    border:none!important;border-radius:12px!important;font-size:15px!important;
    font-weight:800!important;padding:16px 28px!important;
    box-shadow:0 8px 22px rgba(37,99,235,.45)!important;letter-spacing:.01em!important;
    transition:transform .12s,box-shadow .12s!important;
}
button[kind="primary"]:hover{
    background:linear-gradient(135deg,#1D4ED8,#2563EB)!important;
    box-shadow:0 10px 28px rgba(37,99,235,.55)!important;transform:translateY(-1px);
}

/* FILTER */
.filter-wrap{background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:14px 20px;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,.03);}

/* TABLE */
.tbl-wrap{background:#fff;border:1px solid #E2E8F0;border-radius:14px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.04);}
.tbl-head{display:grid;grid-template-columns:2.4fr 1.4fr 0.75fr 0.75fr 0.75fr 1fr 0.65fr;padding:10px 20px;background:#F8FAFC;border-bottom:2px solid #E2E8F0;}
.tbl-head span{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:#64748B;}
.row-name{font-weight:700;color:#0F1E3D;font-size:13px;padding:13px 0;}
.row-name.us{color:#2563EB;}
.row-cell{color:#64748B;font-size:13px;padding:13px 0;display:flex;align-items:center;}
.div-row{height:1px;background:#F1F5F9;margin:0 20px;}

/* BADGES */
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:5px;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.06em;}
.b5{background:#FEE2E2;color:#B91C1C;border:1px solid #FECACA;}
.b4{background:#FEF3C7;color:#B45309;border:1px solid #FDE68A;}
.b3{background:#FEF9C3;color:#854D0E;border:1px solid #FEF08A;}
.b2{background:#DBEAFE;color:#1D4ED8;border:1px solid #BFDBFE;}
.b1{background:#DCFCE7;color:#15803D;border:1px solid #BBF7D0;}
.bus{background:#EFF6FF;color:#1D4ED8;border:1px solid #BFDBFE;}
.bna{background:#F1F5F9;color:#94A3B8;border:1px solid #E2E8F0;}

/* TOP 7 TABLE */
.t7-wrap{background:#fff;border:1px solid #E2E8F0;border-radius:14px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.04),0 6px 20px rgba(0,0,0,.05);margin-bottom:24px;}
.t7-hdr{display:grid;grid-template-columns:0.28fr 1.6fr 0.7fr 2fr 2fr;padding:12px 20px;background:#0F1E3D;gap:8px;}
.t7-hdr span{font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:#7DC4FF;}
.t7-row{display:grid;grid-template-columns:0.28fr 1.6fr 0.7fr 2fr 2fr;padding:16px 20px;gap:8px;border-bottom:1px solid #F1F5F9;align-items:start;}
.t7-row:last-child{border-bottom:none;}
.t7-row:hover{background:#F8FAFC;}
.t7-rank{font-size:22px;font-weight:900;color:#CBD5E1;line-height:1;padding-top:2px;}
.t7-rank.r1{color:#F59E0B;}.t7-rank.r2{color:#94A3B8;}.t7-rank.r3{color:#B45309;}
.t7-clinic-name{font-size:13px;font-weight:800;color:#0F1E3D;line-height:1.35;margin-bottom:4px;}
.t7-area{font-size:11px;color:#64748B;font-weight:500;}
.t7-rating{font-size:15px;font-weight:800;color:#0F1E3D;}
.t7-reviews{font-size:12px;color:#64748B;margin-top:2px;}
.t7-section-label{font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;margin-bottom:5px;}
.t7-point{display:flex;gap:5px;margin-bottom:4px;font-size:11px;color:#374151;line-height:1.5;}
.t7-point.s::before{content:'•';flex-shrink:0;font-size:10px;color:#10B981;}
.t7-point.w::before{content:'•';flex-shrink:0;font-size:10px;color:#EF4444;}
.t7-strengths-col{border-left:3px solid #10B981;padding-left:10px;}
.t7-weaknesses-col{border-left:3px solid #EF4444;padding-left:10px;}

/* PROFILE */
.profile-wrap{padding:28px 32px;max-width:1280px;margin:0 auto;}
.profile-hdr{background:linear-gradient(135deg,#0F1E3D 0%,#1B3A6B 100%);border-radius:14px;padding:30px 34px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:flex-start;gap:24px;box-shadow:0 4px 24px rgba(15,30,61,.2);}
.profile-title{font-size:26px;font-weight:900;color:#fff;margin-bottom:6px;letter-spacing:-.03em;}
.profile-meta{display:flex;gap:20px;flex-wrap:wrap;margin-top:10px;}
.profile-meta-item{font-size:13px;color:#94A3B8;}
.profile-actions{display:flex;gap:8px;flex-wrap:wrap;flex-shrink:0;}
.btn-p{background:#2563EB;color:#fff;border:none;border-radius:8px;padding:9px 16px;font-size:12px;font-weight:700;cursor:pointer;}
.btn-o{background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.25)!important;border-radius:8px;padding:9px 16px;font-size:12px;font-weight:700;cursor:pointer;}
.pstats{display:grid;grid-template-columns:repeat(7,1fr);gap:12px;margin-bottom:20px;}
.pstat{background:#fff;border:1px solid #E2E8F0;border-radius:10px;padding:14px 16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.04);}
.pstat-val{font-size:20px;font-weight:900;color:#0F1E3D;letter-spacing:-.02em;}
.pstat-lbl{font-size:9px;text-transform:uppercase;letter-spacing:.1em;color:#94A3B8;margin-top:4px;font-weight:700;}
.insight-box{background:linear-gradient(135deg,#EFF6FF,#F0FDF4);border:1px solid #BFDBFE;border-radius:10px;padding:14px 18px;margin-bottom:16px;}
.insight-box-title{font-size:10px;font-weight:800;color:#1D4ED8;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;}
.insight-item{font-size:12px;color:#374151;display:flex;gap:8px;margin-bottom:4px;line-height:1.55;}
.info-card{background:#fff;border:1px solid #E2E8F0;border-radius:10px;padding:20px 22px;height:100%;box-shadow:0 1px 3px rgba(0,0,0,.03);}
.info-card-title{font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:#64748B;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid #F1F5F9;}
.info-card-body{font-size:13px;color:#374151;line-height:1.7;}
.tags{display:flex;flex-wrap:wrap;gap:6px;}
.tag{background:#F1F5F9;color:#334155;border-radius:5px;padding:4px 10px;font-size:11px;font-weight:600;border:1px solid #E2E8F0;}
.dg{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;}
.di{display:flex;flex-direction:column;gap:3px;}
.di-lbl{font-size:9px;text-transform:uppercase;letter-spacing:.1em;color:#94A3B8;font-weight:700;}
.di-val{font-size:13px;color:#0F1E3D;font-weight:700;}
.rank-card{background:linear-gradient(135deg,#0F1E3D,#1B3A6B);border-radius:10px;padding:18px;color:#fff;}
.rank-num{font-size:44px;font-weight:900;color:#60A5FA;letter-spacing:-.04em;line-height:1;}
.rank-lbl{font-size:10px;color:#94A3B8;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-top:4px;}
.rank-ctx{font-size:12px;color:#7DC4FF;margin-top:6px;}
.rb-wrap{display:flex;flex-direction:column;gap:6px;margin-top:8px;}
.rb-row{display:flex;align-items:center;gap:8px;}
.rb-lbl{font-size:11px;color:#64748B;width:76px;font-weight:600;flex-shrink:0;}
.rb-bg{flex:1;background:#F1F5F9;border-radius:4px;height:8px;overflow:hidden;}
.rb-fill{height:100%;border-radius:4px;}
.rb-val{font-size:11px;color:#374151;font-weight:700;width:32px;text-align:right;flex-shrink:0;}

/* TABS */
.stTabs [data-baseweb="tab-list"]{background:transparent;gap:0;border-bottom:2px solid #E2E8F0;padding:0;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#64748B;font-size:12px;font-weight:700;padding:10px 18px;border-radius:0;border-bottom:2px solid transparent;margin-bottom:-2px;text-transform:uppercase;letter-spacing:.05em;}
.stTabs [aria-selected="true"]{background:transparent!important;color:#2563EB!important;border-bottom:2px solid #2563EB!important;}

/* STREAMLIT */
.stMetric{display:none!important;}
.stButton>button{background:#2563EB;color:#fff;border:none;border-radius:8px;font-size:12px;font-weight:700;padding:9px 20px;cursor:pointer;transition:background .15s;}
.stButton>button:hover{background:#1D4ED8;}
[data-testid="stSelectbox"]>div>div,[data-testid="stTextInput"]>div>div>input{background:#fff!important;border:1px solid #D1D5DB!important;border-radius:8px!important;color:#0F1E3D!important;font-size:13px!important;}

/* SIDEBAR */
section[data-testid="stSidebar"]{background:#0B1628!important;min-width:380px!important;max-width:400px!important;}
section[data-testid="stSidebar"] .stButton>button{background:#1E3A6E;color:#fff;width:100%;}
section[data-testid="stSidebar"] .stButton>button:hover{background:#2563EB;}
.sb-hdr{background:linear-gradient(135deg,#1E3A6E,#0F1E3D);border-radius:12px;padding:20px;margin-bottom:0;}
.sb-name{font-size:17px;font-weight:900;color:#fff;line-height:1.3;margin-bottom:6px;}
.sb-area{font-size:12px;color:#7DC4FF;font-weight:700;margin-bottom:3px;}
.sb-addr{font-size:11px;color:#94A3B8;margin-bottom:2px;}
.sb-badges{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px;}
.sb-stats{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin:14px 0;}
.sb-stat{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);border-radius:10px;padding:12px;text-align:center;}
.sb-stat-val{font-size:18px;font-weight:900;color:#fff;}
.sb-stat-lbl{font-size:9px;text-transform:uppercase;letter-spacing:.1em;color:#94A3B8;margin-top:3px;font-weight:700;}
.sb-stat.gscore .sb-stat-val{color:#6EE7B7;}
.sb-links{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0;}
.sb-link{display:inline-flex;align-items:center;gap:5px;background:rgba(37,99,235,.25);border:1px solid rgba(74,158,255,.3);color:#7DC4FF;padding:6px 12px;border-radius:7px;font-size:11px;font-weight:700;text-decoration:none;}
.sb-link:hover{background:rgba(37,99,235,.45);color:#fff;}
.sb-sec{margin-top:14px;padding-top:14px;border-top:1px solid rgba(255,255,255,.06);}
.sb-sec-title{font-size:9px;text-transform:uppercase;letter-spacing:.12em;color:#60A5FA;font-weight:800;margin-bottom:8px;}
.sb-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:6px;}
.sb-f{display:flex;flex-direction:column;gap:2px;}
.sb-f-lbl{font-size:9px;text-transform:uppercase;letter-spacing:.09em;color:#94A3B8;font-weight:700;}
.sb-f-val{font-size:12px;color:#E2E8F0;font-weight:700;line-height:1.4;}
.sb-text{font-size:11px;color:#CBD5E1;line-height:1.65;}
.sb-tags{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px;}
.sb-tag{display:inline-block;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);color:#CBD5E1;border-radius:4px;padding:3px 7px;font-size:10px;font-weight:600;}
.sb-sch{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-top:6px;}
.sb-day{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);border-radius:6px;padding:6px 4px;text-align:center;}
.sb-day-n{font-size:9px;text-transform:uppercase;letter-spacing:.08em;color:#94A3B8;font-weight:700;}
.sb-day-v{font-size:9px;color:#E2E8F0;margin-top:3px;line-height:1.3;font-weight:500;}
.sb-insight{background:rgba(37,99,235,.12);border:1px solid rgba(74,158,255,.2);border-radius:8px;padding:10px 12px;margin-bottom:6px;}
.sb-insight-txt{font-size:11px;color:#93C5FD;line-height:1.55;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  PLOTLY BASE LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
PL = dict(
    font_family="Inter, sans-serif",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=14, b=14, l=10, r=10),
    font_color="#374151",
)

# ─────────────────────────────────────────────────────────────────────────────
#  TOP 7 DATA (hardcoded)
# ─────────────────────────────────────────────────────────────────────────────
TOP7_DATA = [
    {
        "rank": 1, "name": "Hands-On PT — Astoria", "area": "Astoria, Queens",
        "rating": "4.9", "reviews": "1,339", "threat": 5,
        "strengths": [
            "1,339 reviews — 10× more than most competitors",
            "MSKUS & EMG diagnostic imaging on-site (unique differentiator)",
            "Partnered with MOTION Sports Medicine / Montefiore Einstein",
            "Open 7:30 AM daily + Saturdays 8 AM–4 PM",
            "Hospital referral pipeline since 1992 — deep community loyalty",
        ],
        "weaknesses": [
            "Recent merger into MOTION chain may dilute boutique identity",
            "Primarily Queens-focused — limited Manhattan/Brooklyn reach",
            "Large chain feel may reduce personalized care perception",
            "No Sunday hours",
        ],
    },
    {
        "rank": 2, "name": "Therapy-In-Motion PC", "area": "Sunset Park, Brooklyn",
        "rating": "5.0", "reviews": "1,009", "threat": 5,
        "strengths": [
            "Perfect 5.0 rating with 1,009 reviews — #1 Brooklyn by Consumer Reports 10 yrs",
            "PT + OT + home care under one roof (unique full-spectrum offering)",
            "Multilingual: Yiddish, Russian, Hebrew — strong immigrant community ties",
            "Open Sundays — rare competitive advantage",
            "Owner Dr. Abe Kopolovich holds DPT/MBA/JD-IP — elite credential",
            "Direct EMR integration with Montefiore via Epic for seamless referrals",
        ],
        "weaknesses": [
            "Single location — no geographic expansion yet",
            "Owner-dependent model: risk if founder steps back",
            "Very niche language focus may limit broader NYC appeal",
        ],
    },
    {
        "rank": 3, "name": "NY Therapy & Wellness", "area": "Sheepshead Bay, Brooklyn",
        "rating": "5.0", "reviews": "828", "threat": 5,
        "strengths": [
            "Perfect 5.0 rating with 828 reviews — dominant in Sheepshead Bay",
            "PT + OT + wellness whole-body model drives higher retention",
            "Telehealth + in-clinic + home visit — most delivery modes covered",
            "Multi-specialty rehabilitation attracts diverse patient base",
        ],
        "weaknesses": [
            "1–2 locations only — limited scalability",
            "No weekend hours listed — accessibility gap",
            "Wellness brand may confuse PT-seeking patients in search",
            "Less known outside southern Brooklyn",
        ],
    },
    {
        "rank": 4, "name": "Evolve PT — Marine Park", "area": "Midwood / Marine Park, Brooklyn",
        "rating": "5.0", "reviews": "676", "threat": 5,
        "strengths": [
            "676 reviews + perfect 5.0 across 4–5 Brooklyn locations",
            "Uses Prompt EMR + self-service kiosks — evals reduced to 10 mins",
            "Open until 8 PM weekdays + walk-ins welcome — highest convenience",
            "Pelvic floor + running/gait analysis + pediatric PT — high-demand niches",
            "20-provider practice with owner Lou Ezrick — strong local SEO",
        ],
        "weaknesses": [
            "Rapid expansion risks quality consistency across locations",
            "No telehealth — missing post-COVID digital patient base",
            "No Sunday or Saturday hours despite high volume",
            "Kiosk model may feel impersonal vs. boutique competitors",
        ],
    },
    {
        "rank": 5, "name": "Phoenix Physical Therapy", "area": "Bay Ridge, Brooklyn",
        "rating": "5.0", "reviews": "488", "threat": 5,
        "strengths": [
            "DPT-owned boutique — patients trust physician-run practice",
            "Mulligan + McKenzie methods — advanced manual therapy credentials",
            "Pelvic floor specialty with dedicated waitlist for postpartum rehab",
            "3 locations (Bay Ridge, Rosedale, Dix Hills) + 61 hrs/week open",
            "Open until 8 PM + Saturdays — strong access advantage",
        ],
        "weaknesses": [
            "Limited insurance panel (Aetna, BCBS, Cigna, Medicare, Emblem only)",
            "No telehealth — losing digital-first patients",
            "Boutique model caps patient volume vs. chain competitors",
            "Dix Hills location outside NYC core market",
        ],
    },
    {
        "rank": 6, "name": "Evolve PT — Upper East Side", "area": "Upper East Side, Manhattan",
        "rating": "5.0", "reviews": "301", "threat": 5,
        "strengths": [
            "Perfect 5.0 with 301 reviews — strongest on UES",
            "ONLY competitor open Saturdays 7 AM–2:30 PM in area",
            "Walk-ins accepted, no appointment needed — top convenience",
            "Open 7 AM all 6 days — earliest hours in neighborhood",
            "Multiple NYC locations + Syosset LI — broad geographic coverage",
        ],
        "weaknesses": [
            "No telehealth listed — digital gap",
            "High-end UES location means premium pricing expectations",
            "301 reviews lower than top Brooklyn competitors",
            "Chain model may reduce boutique appeal vs. independent practices",
        ],
    },
    {
        "rank": 7, "name": "Therapy-In-Motion (Sensory / OT)", "area": "Sunset Park / Sensory Clinic",
        "rating": "5.0", "reviews": "828", "threat": 5,
        "strengths": [
            "Dedicated pediatric sensory gym — top referral for local pediatricians",
            "High cash-pay conversion for out-of-network pediatric services",
            "PT + OT integration: birth-to-adult care pathway",
            "Parkinson's + cardiac rehab + geriatric PT — rare specializations",
        ],
        "weaknesses": [
            "Highly niche — pediatric sensory limits adult PT volume",
            "Out-of-network model excludes insurance-dependent patients",
            "Single location caps growth potential",
            "Niche brand name may not surface in standard PT searches",
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
#  DATA LOADING  — updated for new CSV column schema
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        st.error(f"Data file not found: {DATA_FILE}")
        return pd.DataFrame()
    df = pd.read_csv(DATA_FILE, dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]

    def to_float(v):
        try:
            return float(str(v).replace(",", ""))
        except:
            return None

    df["_rating"]       = df["Google Rating"].apply(to_float)
    df["_reviews"]      = df["# Reviews"].apply(to_float)
    df["_threat"]       = df["Competitive_Threat_1to5"].apply(to_float)
    df["_google_score"] = df["Google Score"].apply(to_float) if "Google Score" in df.columns else None
    df["Latitude"]      = df["Latitude"].apply(to_float)
    df["Longitude"]     = df["Longitude"].apply(to_float)
    df["_is_us"]        = df["Is PT of The City?"].str.strip().str.lower().isin(["yes", "y", "true", "1"])

    # ── Build combined hour strings from open/close column pairs ──────────────
    # New schema: "Mon Hours" = open time, "Mon Close" = close time
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        open_col  = f"{day} Hours"
        close_col = f"{day} Close"
        combo_col = f"_{day}_hours"   # internal combined column
        if open_col in df.columns and close_col in df.columns:
            df[combo_col] = df.apply(
                lambda r, oc=open_col, cc=close_col: _combine_hours(r[oc], r[cc]),
                axis=1,
            )
        elif open_col in df.columns:
            df[combo_col] = df[open_col]
        else:
            df[combo_col] = ""

    # ── Insurance: use Insurances_Accepted_Clean (new column name) ────────────
    ins_col = "Insurances_Accepted_Clean" if "Insurances_Accepted_Clean" in df.columns else (
              "insurances_companies"       if "insurances_companies" in df.columns else None)
    df["_ins_col"] = ins_col or ""
    if ins_col:
        df["_insurance"] = df[ins_col]
    else:
        df["_insurance"] = ""

    return df, ins_col


def _combine_hours(open_val, close_val):
    """Turn separate open / close strings into 'HH:MM AM – HH:MM PM' or 'Closed'."""
    o = str(open_val).strip()
    c = str(close_val).strip()
    closed_tokens = {"", "nan", "none", "closed", "n/a", "-"}
    if o.lower() in closed_tokens and c.lower() in closed_tokens:
        return "Closed"
    if o.lower() in closed_tokens:
        return c
    if c.lower() in closed_tokens:
        return o
    return f"{o} – {c}"


raw = load_data()
if isinstance(raw, pd.DataFrame) and raw.empty:
    st.stop()
df, INS_COL = raw

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

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for key, default in [("page", "dashboard"), ("clinic", None), ("selected_clinic", None)]:
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


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def v(r, key, fallback="—"):
    val = r.get(key, "")
    s = str(val).strip()
    return s if s and s not in ("nan", "None", "") else fallback


def day_hours(r, day):
    """Return combined hours string for a given day abbreviation."""
    return v(r, f"_{day}_hours", "Closed")


def fmt_gscore(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    try:
        return f"{float(val):.2f}"
    except:
        return "—"


def threat_badge(t, is_us=False):
    if is_us:
        return '<span class="badge bus">● Our Clinic</span>'
    if t is None or (isinstance(t, float) and pd.isna(t)):
        return '<span class="badge bna">Unknown</span>'
    try:
        ti = int(float(t))
    except:
        return '<span class="badge bna">Unknown</span>'
    labels = {5: "🔴 Critical", 4: "🟠 High", 3: "🟡 Medium", 2: "🔵 Low", 1: "🟢 Minimal"}
    return f'<span class="badge b{ti}">{labels.get(ti, str(ti))}</span>'


def flag_badge(r):
    f = v(r, "Top_Threat_Flag")
    if f not in ("Normal", "—"):
        return f'<span class="badge" style="background:#FFF7ED;color:#C2410C;border:1px solid #FED7AA;">⚑ {f}</span>'
    return ""


def tags_html(text, sb=False):
    if not text or text == "—":
        return '<span style="color:#94A3B8;font-size:12px;">No data</span>'
    items = [x.strip() for x in text.replace(";", ",").split(",") if x.strip()]
    cls = "sb-tag" if sb else "tag"
    return "".join(f'<span class="{cls}">{i}</span>' for i in items)


def star_bar(rating, color="#2563EB"):
    try:
        pct = (float(rating) / 5) * 100
        return (
            f'<div class="rb-wrap"><div class="rb-row">'
            f'<div class="rb-lbl">Google</div>'
            f'<div class="rb-bg"><div class="rb-fill" style="width:{pct:.1f}%;background:{color};"></div></div>'
            f'<div class="rb-val">{rating}</div></div></div>'
        )
    except:
        return ""


def generate_insights(r):
    ins = []
    try:
        rat = float(r["_rating"]) if pd.notna(r["_rating"]) else None
        if rat:
            avg = comp_df["_rating"].mean()
            diff = rat - avg
            ins.append(f"⭐ Rated {rat:.1f} — {'above' if diff > 0 else 'below'} competitor avg ({avg:.1f}) by {abs(diff):.2f} pts.")
    except:
        pass
    try:
        gs = float(r["_google_score"]) if pd.notna(r["_google_score"]) else None
        if gs is not None and comp_df["_google_score"].notna().any():
            avg_gs = comp_df["_google_score"].mean()
            diff_gs = gs - avg_gs
            ins.append(f"📊 Google Score {gs:.2f} — {'above' if diff_gs >= 0 else 'below'} competitor avg ({avg_gs:.2f}) by {abs(diff_gs):.2f}.")
    except:
        pass
    area = r.get("Neighborhood / Area", "")
    if area:
        n = len(comp_df[comp_df["Neighborhood / Area"] == area])
        if n:
            ins.append(f"📍 {n} competitor(s) in same neighborhood ({area}).")
    try:
        t = int(float(r["_threat"])) if pd.notna(r["_threat"]) else None
        if t:
            desc = {1: "Minimal", 2: "Low", 3: "Medium", 4: "High — watch closely", 5: "Critical — top priority"}
            ins.append(f"🎯 Threat level {t}/5: {desc.get(t, '')}")
    except:
        pass
    if v(r, "Top_Threat_Flag") not in ("Normal", "—"):
        ins.append(f"⚑ Flagged: {v(r, 'Top_Threat_Flag')}")
    if v(r, "Weekend_Advantage") not in ("No", "—"):
        ins.append(f"📅 Weekend Advantage: {v(r, 'Weekend_Advantage')}")
    nearest = v(r, "Nearest_PT_of_The_City")
    dist    = v(r, "Distance_to_Nearest_PTotC_miles")
    if nearest != "—":
        ins.append(f"🏥 Nearest PT of the City: {nearest} ({dist} mi away).")
    return ins


def apply_filters(df_in, search_q, f_area, f_threat, f_ins, show_us, sort_by):
    fdf = df_in.copy()
    if search_q:
        fdf = fdf[
            fdf["Clinic Name"].str.contains(search_q, case=False, na=False)
            | fdf["Neighborhood / Area"].str.contains(search_q, case=False, na=False)
        ]
    if f_area != "All Areas":
        fdf = fdf[fdf["Neighborhood / Area"] == f_area]
    if f_threat != "All Threats":
        try:
            fdf = fdf[fdf["_threat"] == float(f_threat[0])]
        except:
            pass
    if f_ins != "All Insurances":
        fdf = fdf[fdf["_insurance"].str.contains(f_ins, case=False, na=False, regex=False)]
    if show_us:
        fdf = fdf[fdf["_is_us"]]
    if sort_by == "Sort: Threat ↓":
        fdf = fdf.sort_values("_threat", ascending=False, na_position="last")
    elif sort_by == "Sort: Rating ↓":
        fdf = fdf.sort_values("_rating", ascending=False, na_position="last")
    elif sort_by == "Sort: Reviews ↓":
        fdf = fdf.sort_values("_reviews", ascending=False, na_position="last")
    elif sort_by == "Sort: Score ↓":
        fdf = fdf.sort_values("_google_score", ascending=False, na_position="last")
    else:
        fdf = fdf.sort_values("Clinic Name", ascending=True, na_position="last")
    return fdf


def render_filter_widgets(key_prefix):
    st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([2, 1.3, 1.3, 1.5, 0.8, 1.1])
    with fc1:
        search_q = st.text_input(
            "", placeholder="🔍  Search clinic name or area…",
            label_visibility="collapsed", key=f"{key_prefix}_search",
        )
    with fc2:
        f_area = st.selectbox("", AREA_OPTIONS, label_visibility="collapsed", key=f"{key_prefix}_area")
    with fc3:
        f_threat = st.selectbox(
            "", ["All Threats", "5 — Critical", "4 — High", "3 — Medium", "2 — Low", "1 — Minimal"],
            label_visibility="collapsed", key=f"{key_prefix}_threat",
        )
    with fc4:
        f_ins = st.selectbox(
            "", ["All Insurances"] + INSURANCE_OPTIONS,
            label_visibility="collapsed", key=f"{key_prefix}_ins",
        )
    with fc5:
        show_us = st.checkbox("Ours only", key=f"{key_prefix}_us")
    with fc6:
        sort_by = st.selectbox(
            "", ["Sort: Threat ↓", "Sort: Rating ↓", "Sort: Reviews ↓", "Sort: Score ↓", "Sort: A–Z"],
            label_visibility="collapsed", key=f"{key_prefix}_sort",
        )
    st.markdown('</div>', unsafe_allow_html=True)
    return search_q, f_area, f_threat, f_ins, show_us, sort_by


# ─────────────────────────────────────────────────────────────────────────────
#  CHARTS
# ─────────────────────────────────────────────────────────────────────────────
def chart_threat_donut(df_in):
    tm = {5: "Critical", 4: "High", 3: "Medium", 2: "Low", 1: "Minimal"}
    counts = {}
    for _, row in df_in.iterrows():
        if row["_is_us"]:
            continue
        t = row["_threat"]
        key = tm.get(int(t), "Unknown") if pd.notna(t) and t is not None else "Unknown"
        counts[key] = counts.get(key, 0) + 1
    order  = ["Critical", "High", "Medium", "Low", "Minimal", "Unknown"]
    colors = ["#DC2626", "#F59E0B", "#EAB308", "#60A5FA", "#10B981", "#CBD5E1"]
    labs   = [l for l in order if l in counts]
    vals   = [counts[l] for l in labs]
    cols   = [colors[order.index(l)] for l in labs]
    fig = go.Figure(go.Pie(
        labels=labs, values=vals, hole=0.6,
        marker=dict(colors=cols, line=dict(color="#fff", width=2)),
        textinfo="label+percent", textfont_size=11,
        hovertemplate="<b>%{label}</b><br>%{value} clinics (%{percent})<extra></extra>",
    ))
    fig.add_annotation(text=f"<b>{sum(vals)}</b>", showarrow=False,
                       font=dict(size=22, color="#0F1E3D", family="Inter"), x=0.5, y=0.55)
    fig.add_annotation(text="Competitors", showarrow=False,
                       font=dict(size=10, color="#94A3B8", family="Inter"), x=0.5, y=0.42)
    fig.update_layout(**PL, showlegend=False, height=260)
    return fig


def chart_borough_breakdown(df_in):
    BM = {
        "brooklyn": "Brooklyn", "park slope": "Brooklyn", "williamsburg": "Brooklyn",
        "bushwick": "Brooklyn", "bed-stuy": "Brooklyn", "bedford": "Brooklyn",
        "greenpoint": "Brooklyn", "crown heights": "Brooklyn", "flatbush": "Brooklyn",
        "cobble hill": "Brooklyn", "boerum hill": "Brooklyn", "fort greene": "Brooklyn",
        "bay ridge": "Brooklyn", "sunset park": "Brooklyn", "prospect": "Brooklyn",
        "downtown brooklyn": "Brooklyn", "sheepshead": "Brooklyn", "brighton": "Brooklyn",
        "coney island": "Brooklyn", "canarsie": "Brooklyn", "borough park": "Brooklyn",
        "ditmas": "Brooklyn", "marine park": "Brooklyn", "midwood": "Brooklyn",
        "manhattan": "Manhattan", "midtown": "Manhattan", "chelsea": "Manhattan",
        "soho": "Manhattan", "tribeca": "Manhattan", "lower east": "Manhattan",
        "east village": "Manhattan", "west village": "Manhattan", "gramercy": "Manhattan",
        "flatiron": "Manhattan", "murray hill": "Manhattan", "kips bay": "Manhattan",
        "hell's kitchen": "Manhattan", "hells kitchen": "Manhattan",
        "upper east": "Upper Manhattan", "upper west": "Upper Manhattan",
        "harlem": "Upper Manhattan", "morningside": "Upper Manhattan",
        "washington heights": "Upper Manhattan", "inwood": "Upper Manhattan",
        "queens": "Queens", "astoria": "Queens", "long island city": "Queens",
        "flushing": "Queens", "jackson heights": "Queens", "forest hills": "Queens",
        "corona": "Queens", "elmhurst": "Queens", "woodside": "Queens",
        "sunnyside": "Queens", "rego park": "Queens", "jamaica": "Queens",
        "ridgewood": "Queens", "maspeth": "Queens", "bayside": "Queens",
        "bronx": "Bronx", "riverdale": "Bronx", "fordham": "Bronx", "pelham": "Bronx",
        "staten island": "Staten Island",
    }

    def to_boro(a):
        al = str(a).lower().strip()
        for k, b in BM.items():
            if k in al:
                return b
        return "Other"

    df2 = df_in.copy()
    df2["_boro"] = df2["Neighborhood / Area"].apply(to_boro)
    boros = ["Brooklyn", "Manhattan", "Upper Manhattan", "Queens", "Bronx", "Staten Island", "Other"]
    labs, us_c, co_c = [], [], []
    for b in boros:
        sub = df2[df2["_boro"] == b]
        if sub.empty:
            continue
        labs.append(b)
        us_c.append(int(sub["_is_us"].sum()))
        co_c.append(int((~sub["_is_us"]).sum()))
    if not labs:
        return None
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="PT of the City", x=labs, y=us_c, marker_color="#2563EB", marker_opacity=0.92,
        text=us_c, textposition="outside", textfont=dict(size=11, color="#2563EB"),
        hovertemplate="<b>%{x}</b><br>PT of the City: <b>%{y}</b><extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Competitors", x=labs, y=co_c,
        marker_color="#E2E8F0", marker_line_color="#94A3B8", marker_line_width=1,
        text=co_c, textposition="outside", textfont=dict(size=11, color="#64748B"),
        hovertemplate="<b>%{x}</b><br>Competitors: <b>%{y}</b><extra></extra>",
    ))
    fig.update_layout(
        **PL, barmode="group", height=260, bargap=0.22, bargroupgap=0.06,
        xaxis=dict(tickfont_size=11, showgrid=False),
        yaxis=dict(tickfont_size=10, gridcolor="#F1F5F9", zeroline=False),
        legend=dict(orientation="h", y=-0.25, font_size=11, bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def chart_top20_reviews(df_in):
    comp = df_in[~df_in["_is_us"] & df_in["_reviews"].notna()].nlargest(20, "_reviews")
    threat_colors = {5: "#DC2626", 4: "#F59E0B", 3: "#EAB308", 2: "#60A5FA", 1: "#10B981"}
    colors = [
        threat_colors.get(int(r["_threat"]), "#CBD5E1") if pd.notna(r["_threat"]) else "#CBD5E1"
        for _, r in comp.iterrows()
    ]
    fig = go.Figure(go.Bar(
        x=comp["_reviews"].tolist(), y=comp["Clinic Name"].tolist(), orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.4)", width=0.5)),
        text=[f"{int(r):,}" for r in comp["_reviews"].tolist()],
        textposition="outside", textfont=dict(size=10, color="#374151"),
        hovertemplate="<b>%{y}</b><br>Reviews: <b>%{x:,}</b><extra></extra>",
    ))
    fig.update_layout(
        **PL, height=480,
        xaxis=dict(tickfont_size=10, gridcolor="#F1F5F9", zeroline=False),
        yaxis=dict(tickfont_size=10, autorange="reversed"),
        bargap=0.28, showlegend=False,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(name):
    rows = df[df["Clinic Name"] == name]
    if rows.empty:
        return
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
            <div class="sb-name">{v(r,'Clinic Name')}</div>
            <div class="sb-area">🏙️ {v(r,'Neighborhood / Area')}</div>
            <div class="sb-addr">📍 {v(r,'Address')}</div>
            <div class="sb-addr">📞 {v(r,'Phone')}</div>
            <div class="sb-badges">{threat_badge(t_val,is_us)}{flag_badge(r)}</div>
        </div>
        """, unsafe_allow_html=True)

        yelp = v(r, "Yelp_Rating")
        yr   = v(r, "Yelp_Reviews")
        try:
            ti = int(float(t_val))
            tc = {5: "#DC2626", 4: "#F59E0B", 3: "#EAB308", 2: "#60A5FA", 1: "#10B981"}.get(ti, "#CBD5E1")
        except:
            tc = "#CBD5E1"; ti = None

        gs_display = fmt_gscore(gs_val)

        st.markdown(f"""
        <div class="sb-stats">
            <div class="sb-stat"><div class="sb-stat-val">⭐ {v(r,'Google Rating')}</div><div class="sb-stat-lbl">Google Rating</div></div>
            <div class="sb-stat"><div class="sb-stat-val">{v(r,'# Reviews')}</div><div class="sb-stat-lbl">Reviews</div></div>
            <div class="sb-stat gscore"><div class="sb-stat-val">📊 {gs_display}</div><div class="sb-stat-lbl">Google Score</div></div>
            <div class="sb-stat"><div class="sb-stat-val" style="color:{tc};">{(str(ti)+'/5') if ti else '—'}</div><div class="sb-stat-lbl">Threat</div></div>
            <div class="sb-stat"><div class="sb-stat-val">{v(r,'Distance from PTotC (mi)')} mi</div><div class="sb-stat-lbl">Distance</div></div>
            <div class="sb-stat"><div class="sb-stat-val">{v(r,'Estimated_Daily_Volume')}</div><div class="sb-stat-lbl">Daily Volume</div></div>
        </div>
        """, unsafe_allow_html=True)

        if yelp != "—":
            st.markdown(f"""
            <div class="sb-stats" style="margin-top:-6px;">
                <div class="sb-stat"><div class="sb-stat-val">⭐ {yelp}</div><div class="sb-stat-lbl">Yelp ({yr} rev.)</div></div>
            </div>
            """, unsafe_allow_html=True)

        website = v(r, "Website"); gmaps = v(r, "Google Maps Link"); social = v(r, "Social_Media")
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

        # Nearest PT of the City
        nearest = v(r, "Nearest_PT_of_The_City")
        dist_near = v(r, "Distance_to_Nearest_PTotC_miles")
        if nearest != "—":
            st.markdown(f"""
            <div class="sb-sec"><div class="sb-sec-title">🏥 Nearest PT of the City</div>
            <div class="sb-f-val" style="color:#7DC4FF;">{nearest}</div>
            <div class="sb-area" style="margin-top:2px;">{dist_near} mi away</div></div>
            """, unsafe_allow_html=True)

        insights = generate_insights(r)
        if insights:
            st.markdown('<div class="sb-sec"><div class="sb-sec-title">🔍 Intelligence</div>', unsafe_allow_html=True)
            for ins in insights:
                st.markdown(f'<div class="sb-insight"><div class="sb-insight-txt">{ins}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        usp   = v(r, "Unique_Selling_Proposition_USP")
        notes = v(r, "Competitor Notes")
        rag   = v(r, "RAG_Summary")
        deep  = v(r, "Deep_Search_Extra_Notes")

        intel_parts = ""
        if usp   != "—": intel_parts += f"<div class='sb-f' style='margin-bottom:8px;'><div class='sb-f-lbl'>USP</div><div class='sb-text'>{usp}</div></div>"
        if notes != "—": intel_parts += f"<div class='sb-f' style='margin-bottom:8px;'><div class='sb-f-lbl'>Notes</div><div class='sb-text'>{notes}</div></div>"
        if rag   != "—": intel_parts += f"<div class='sb-f' style='margin-bottom:8px;'><div class='sb-f-lbl'>RAG Summary</div><div class='sb-text'>{rag}</div></div>"
        if deep  != "—": intel_parts += f"<div class='sb-f'><div class='sb-f-lbl'>Deep Search</div><div class='sb-text'>{deep}</div></div>"
        if intel_parts:
            st.markdown(f'<div class="sb-sec"><div class="sb-sec-title">🎯 Competitive Intel</div>{intel_parts}</div>', unsafe_allow_html=True)

        spec  = v(r, "Specializations")
        equip = v(r, "Key_Equipment")
        langs = v(r, "Languages_Spoken")
        spec_html  = f"<div class='sb-f' style='margin-top:6px;'><div class='sb-f-lbl'>Specializations</div><div class='sb-tags'>{tags_html(spec,sb=True)}</div></div>"  if spec  != "—" else ""
        equip_html = f"<div class='sb-f' style='margin-top:6px;'><div class='sb-f-lbl'>Equipment</div><div class='sb-tags'>{tags_html(equip,sb=True)}</div></div>"         if equip != "—" else ""
        langs_html = f"<div class='sb-f' style='margin-top:6px;'><div class='sb-f-lbl'>Languages</div><div class='sb-tags'>{tags_html(langs,sb=True)}</div></div>"         if langs != "—" else ""
        st.markdown(f"""
        <div class="sb-sec"><div class="sb-sec-title">⚕️ Services</div>
        <div class="sb-row">
            <div class="sb-f"><div class="sb-f-lbl">Telehealth</div><div class="sb-f-val">{v(r,'Telehealth')}</div></div>
            <div class="sb-f"><div class="sb-f-lbl">Home Care</div><div class="sb-f-val">{v(r,'Home_Care')}</div></div>
        </div>
        {spec_html}{equip_html}{langs_html}
        </div>
        """, unsafe_allow_html=True)

        # Insurance — use the combined _insurance column
        ins_text = v(r, "_insurance")
        # Also show the raw Insurances_Accepted_Clean and Insurance_Verification_Notes
        ins_note = v(r, "Insurance_Verification_Notes")
        st.markdown(
            f'<div class="sb-sec"><div class="sb-sec-title">🛡️ Insurance</div>'
            f'<div class="sb-tags">{tags_html(ins_text,sb=True)}</div>'
            + (f'<div class="sb-text" style="margin-top:6px;font-size:10px;color:#60A5FA;">{ins_note}</div>' if ins_note != "—" else "")
            + '</div>',
            unsafe_allow_html=True,
        )

        days = [("Mon","Mon"), ("Tue","Tue"), ("Wed","Wed"), ("Thu","Thu"),
                ("Fri","Fri"), ("Sat","Sat"), ("Sun","Sun")]
        boxes = ""
        for dn, dk in days:
            dv = day_hours(r, dk)
            closed = dv in ("—", "Closed", "")
            bg = "rgba(239,68,68,.08)" if closed else "rgba(16,185,129,.06)"
            bc = "rgba(239,68,68,.15)" if closed else "rgba(16,185,129,.15)"
            disp = "Closed" if closed else dv.replace(" – ", "\n").replace(" AM", "a").replace(" PM", "p")
            boxes += (
                f'<div class="sb-day" style="background:{bg};border-color:{bc};">'
                f'<div class="sb-day-n">{dn}</div>'
                f'<div class="sb-day-v" style="white-space:pre-wrap;">{disp}</div></div>'
            )
        st.markdown(f"""
        <div class="sb-sec"><div class="sb-sec-title">🕐 Schedule</div>
        <div class="sb-row" style="margin-bottom:8px;">
            <div class="sb-f"><div class="sb-f-lbl">Total Hrs/Wk</div><div class="sb-f-val">{v(r,'Total Hrs/Wk')}</div></div>
            <div class="sb-f"><div class="sb-f-lbl">Wkday / Wkend</div><div class="sb-f-val">{v(r,'Weekday Hrs/Wk')} / {v(r,'Weekend Hrs/Wk')}</div></div>
        </div>
        <div class="sb-sch">{boxes}</div></div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
        if st.button("📋  Open Full Profile →", key="sb_full", use_container_width=True):
            open_clinic(name)


# ─────────────────────────────────────────────────────────────────────────────
#  TOP NAV
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "dashboard":
    page_label = "Market Intelligence"
elif st.session_state.page == "map":
    page_label = "Live Map"
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


# ═════════════════════════════════════════════════════════════════════════════
#  PROFILE PAGE
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "profile" and st.session_state.clinic:
    rows = df[df["Clinic Name"] == st.session_state.clinic]
    if rows.empty:
        st.warning("Clinic not found.")
        st.stop()
    r     = rows.iloc[0]
    is_us = r["_is_us"]
    t_val = r["_threat"]
    gs_val = r["_google_score"]

    st.markdown('<div class="profile-wrap">', unsafe_allow_html=True)
    bc, _ = st.columns([1, 4])
    with bc:
        if st.button("← Back to Dashboard"):
            go_dash()

    website = v(r, "Website"); gmaps = v(r, "Google Maps Link"); social = v(r, "Social_Media")
    wb  = f'<a href="{("https://"+website) if not website.startswith("http") else website}" target="_blank"><button class="btn-p">🌐 Website</button></a>' if website != "—" and "Not found" not in website else ""
    mb  = f'<a href="{gmaps}" target="_blank"><button class="btn-o">📍 Maps</button></a>' if gmaps.startswith("http") else ""
    sb2 = f'<a href="{social}" target="_blank"><button class="btn-o">📱 Social</button></a>' if social.startswith("http") else ""

    st.markdown(f"""
    <div class="profile-hdr">
        <div>
            <div style="margin-bottom:10px;">{threat_badge(t_val,is_us)} {flag_badge(r)}</div>
            <div class="profile-title">{v(r,'Clinic Name')}</div>
            <div class="profile-meta">
                <div class="profile-meta-item">📍 {v(r,'Address')}</div>
                <div class="profile-meta-item">🏙️ {v(r,'Neighborhood / Area')}</div>
                <div class="profile-meta-item">📞 {v(r,'Phone')}</div>
                <div class="profile-meta-item">📮 {v(r,'Zip_Code')}</div>
            </div>
        </div>
        <div class="profile-actions">{wb}{mb}{sb2}</div>
    </div>
    """, unsafe_allow_html=True)

    yelp = v(r, "Yelp_Rating")
    yd   = f"⭐ {yelp}" if yelp != "—" else "—"
    gs_display = fmt_gscore(gs_val)

    def ps(lbl, val, highlight=False):
        style = ' style="color:#15803D;"' if highlight else ''
        return f'<div class="pstat"><div class="pstat-val"{style}>{val}</div><div class="pstat-lbl">{lbl}</div></div>'

    st.markdown(f"""
    <div class="pstats">
        {ps("Google Rating", f"⭐ {v(r,'Google Rating')}")}
        {ps("Reviews", v(r,'# Reviews'))}
        {ps("Google Score", f"📊 {gs_display}", highlight=True)}
        {ps("Yelp", yd)}
        {ps("Threat", v(r,'Competitive_Threat_1to5')+"/5")}
        {ps("Daily Volume", v(r,'Estimated_Daily_Volume'))}
        {ps("Distance", v(r,'Distance from PTotC (mi)')+" mi")}
    </div>
    """, unsafe_allow_html=True)

    ins2 = generate_insights(r)
    if ins2:
        html = "".join(f'<div class="insight-item">{i}</div>' for i in ins2)
        st.markdown(f'<div class="insight-box"><div class="insight-box-title">🔍 Quick Intelligence</div>{html}</div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5, t6 = st.tabs(["Intelligence", "Competitive View", "Services", "Insurance", "Schedule", "About"])

    with t1:
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="info-card"><div class="info-card-title">Unique Selling Proposition</div><div class="info-card-body">{v(r,"Unique_Selling_Proposition_USP")}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="info-card"><div class="info-card-title">Competitor Notes</div><div class="info-card-body">{v(r,"Competitor Notes")}</div></div>', unsafe_allow_html=True)
        st.write("")
        c3, c4 = st.columns(2)
        with c3:
            st.markdown(f'<div class="info-card"><div class="info-card-title">RAG Summary</div><div class="info-card-body">{v(r,"RAG_Summary")}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="info-card"><div class="info-card-title">Deep Search Notes</div><div class="info-card-body">{v(r,"Deep_Search_Extra_Notes")}</div></div>', unsafe_allow_html=True)

        # Nearest PT of the City card
        st.write("")
        nearest = v(r, "Nearest_PT_of_The_City")
        dist_near = v(r, "Distance_to_Nearest_PTotC_miles")
        if nearest != "—":
            st.markdown(f"""
            <div class="info-card" style="background:linear-gradient(135deg,#EFF6FF,#F0FDF4);">
                <div class="info-card-title">🏥 Nearest PT of the City Location</div>
                <div class="info-card-body"><b>{nearest}</b> &nbsp;·&nbsp; {dist_near} miles away</div>
            </div>
            """, unsafe_allow_html=True)

        if pd.notna(r["Latitude"]) and pd.notna(r["Longitude"]):
            st.write("")
            if is_us:
                cc = "#2563EB"
            elif t_val and t_val >= 4:
                cc = "#DC2626"
            elif t_val == 3:
                cc = "#F59E0B"
            else:
                cc = "#60A5FA"
            mm = folium.Map(location=[r["Latitude"], r["Longitude"]], zoom_start=15, tiles="CartoDB Positron")
            folium.CircleMarker(
                location=[r["Latitude"], r["Longitude"]], radius=14,
                color=cc, fill=True, fill_color=cc, fill_opacity=0.85,
                tooltip=v(r, "Clinic Name"),
            ).add_to(mm)
            for _, nr in df.iterrows():
                if nr["Clinic Name"] == r["Clinic Name"] or pd.isna(nr["Latitude"]) or pd.isna(nr["Longitude"]):
                    continue
                nc = "#2563EB" if nr["_is_us"] else "#94A3B8"
                folium.CircleMarker(
                    location=[nr["Latitude"], nr["Longitude"]], radius=5,
                    color=nc, fill=True, fill_color=nc, fill_opacity=0.5,
                    tooltip=nr["Clinic Name"],
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
            rb  = adf["_rating"].tolist()
            iu  = adf["_is_us"].tolist()
            bc2 = ["#2563EB" if u else "#E2E8F0" for u in iu]
            bb2 = ["#2563EB" if u else "#94A3B8" for u in iu]
            fig_rb = go.Figure(go.Bar(
                x=rb, y=cn, orientation="h",
                marker=dict(color=bc2, line=dict(color=bb2, width=1)),
                hovertemplate="<b>%{y}</b>: %{x:.1f}⭐<extra></extra>",
            ))
            fig_rb.update_layout(
                **PL, height=max(220, len(cn) * 34),
                xaxis=dict(range=[0, 5.5], dtick=1, tickfont_size=10, gridcolor="#F1F5F9"),
                yaxis=dict(tickfont_size=10), bargap=0.35, showlegend=False,
            )
            st.plotly_chart(fig_rb, use_container_width=True, config={"displayModeBar": False}, theme=None)
            st.markdown("</div></div>", unsafe_allow_html=True)
        with cr:
            sa = adf.sort_values("_rating", ascending=False).reset_index(drop=True)
            try:
                rank = sa[sa["Clinic Name"] == r["Clinic Name"]].index[0] + 1
            except:
                rank = "—"
            st.markdown(f'<div class="rank-card"><div class="rank-num">#{rank}</div><div class="rank-lbl">Rank by Rating</div><div class="rank-ctx">out of {len(adf)} clinics in {area}</div></div>', unsafe_allow_html=True)
            st.write("")
            st.markdown(f'<div class="info-card"><div class="info-card-title">Rating Breakdown</div>{star_bar(v(r,"Google Rating"))}<div style="margin-top:12px;font-size:12px;color:#64748B;"><b style="color:#0F1E3D;">{v(r,"# Reviews")}</b> reviews · Yelp: <b style="color:#0F1E3D;">{yd}</b> · Google Score: <b style="color:#15803D;">{gs_display}</b></div></div>', unsafe_allow_html=True)

    with t3:
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="info-card"><div class="info-card-title">Specializations</div><div class="tags">{tags_html(v(r,"Specializations"))}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="info-card"><div class="info-card-title">Key Equipment</div><div class="tags">{tags_html(v(r,"Key_Equipment"))}</div></div>', unsafe_allow_html=True)
        st.write("")
        c3, c4 = st.columns(2)
        with c3:
            st.markdown(f'<div class="info-card"><div class="info-card-title">Languages</div><div class="tags">{tags_html(v(r,"Languages_Spoken"))}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="info-card"><div class="info-card-title">Additional Services</div><div class="dg"><div class="di"><div class="di-lbl">Telehealth</div><div class="di-val">{v(r,"Telehealth")}</div></div><div class="di"><div class="di-lbl">Home Care</div><div class="di-val">{v(r,"Home_Care")}</div></div></div></div>', unsafe_allow_html=True)

    with t4:
        st.write("")
        ins_text = v(r, "_insurance")
        ins_raw  = v(r, "Insurances_Accepted_Clean") if INS_COL == "Insurances_Accepted_Clean" else "—"
        ins_note = v(r, "Insurance_Verification_Notes")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="info-card"><div class="info-card-title">Insurances Accepted</div><div class="tags">{tags_html(ins_text)}</div></div>', unsafe_allow_html=True)
        with c2:
            note_html = f'<div style="margin-top:12px;font-size:11px;color:#64748B;border-top:1px solid #F1F5F9;padding-top:10px;"><b>Verification Notes:</b> {ins_note}</div>' if ins_note != "—" else ""
            st.markdown(f'<div class="info-card"><div class="info-card-title">Insurance Details</div><div class="info-card-body" style="font-size:12px;">{ins_raw}{note_html}</div></div>', unsafe_allow_html=True)

    with t5:
        st.write("")
        day_cols = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        chips = "".join(
            f'<div class="di"><div class="di-lbl">{d}</div><div class="di-val" style="font-size:12px;">{day_hours(r, d)}</div></div>'
            for d in day_cols
        )
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-title">Weekly Hours</div>
            <div class="dg" style="margin-bottom:16px;">
                <div class="di"><div class="di-lbl">Total Hrs/Wk</div><div class="di-val">{v(r,"Total Hrs/Wk")}</div></div>
                <div class="di"><div class="di-lbl">Weekend Hrs</div><div class="di-val">{v(r,"Weekend Hrs/Wk")}</div></div>
                <div class="di"><div class="di-lbl">Weekend Advantage</div><div class="di-val">{v(r,"Weekend_Advantage")}</div></div>
            </div>
            <div class="dg">{chips}</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.code(v(r, "Full Weekly Schedule", "Not available"), language=None)

    with t6:
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="info-card"><div class="info-card-title">Organization</div>
            <div class="dg">
                <div class="di"><div class="di-lbl">Parent Org</div><div class="di-val">{v(r,'Parent Organization')}</div></div>
                <div class="di"><div class="di-lbl">Owner/Founder</div><div class="di-val">{v(r,'Owner_Founder')}</div></div>
                <div class="di"><div class="di-lbl">Established</div><div class="di-val">{v(r,'Founded / Est.')}</div></div>
                <div class="di"><div class="di-lbl">Chain Size</div><div class="di-val">{v(r,'Chain_Size')}</div></div>
                <div class="di"><div class="di-lbl">Zip Code</div><div class="di-val">{v(r,'Zip_Code')}</div></div>
            </div></div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="info-card"><div class="info-card-title">Information Sources</div><div class="info-card-body" style="word-break:break-all;font-size:12px;">{v(r,"Information_Sources (URLs)")}</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
#  MAP PAGE
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "map":
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    bc, _ = st.columns([1, 4])
    with bc:
        if st.button("← Back to Dashboard", key="map_back_btn"):
            go_dash()

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
    fdf_map = apply_filters(df, search_q, f_area, f_threat, f_ins, show_us, sort_by)

    m = folium.Map(location=[40.75, -73.99], zoom_start=11, tiles="CartoDB Positron")
    for _, row in fdf_map.iterrows():
        if pd.isna(row["Latitude"]) or pd.isna(row["Longitude"]):
            continue
        if row["_is_us"]:
            c, sz = "#2563EB", 12
        else:
            t = row["_threat"]
            if pd.isna(t) or t is None:   c, sz = "#CBD5E1", 6
            elif t >= 5:                    c, sz = "#DC2626", 10
            elif t >= 4:                    c, sz = "#F59E0B", 9
            elif t == 3:                    c, sz = "#EAB308", 7
            else:                           c, sz = "#60A5FA", 6
        try:
            ti = int(float(row["_threat"]))
            tl = {5: "🔴 Critical", 4: "🟠 High", 3: "🟡 Medium", 2: "🔵 Low", 1: "🟢 Minimal"}.get(ti, "Unknown")
        except:
            tl = "Unknown"

        gs_tip  = fmt_gscore(row.get("_google_score"))
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

    map_data = st_folium(m, width="100%", height=560, key="main_map",
                         returned_objects=["last_object_clicked_tooltip", "last_object_clicked_popup"])

    clicked = None
    if map_data:
        pv = map_data.get("last_object_clicked_popup")
        if pv and isinstance(pv, dict):
            clicked = pv.get("__html", "").replace("<div>", "").replace("</div>", "").strip()
        elif pv and isinstance(pv, str):
            clicked = pv.strip()

    if clicked and clicked in df["Clinic Name"].values:
        if st.session_state.selected_clinic != clicked:
            st.session_state.selected_clinic = clicked
            st.rerun()

    if st.session_state.selected_clinic:
        render_sidebar(st.session_state.selected_clinic)

    st.markdown(f'<div class="sec-pill" style="display:inline-block;margin-top:4px;">{len(fdf_map)} clinics shown</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ── KPIs ─────────────────────────────────────────────────────────────────────
avg_us   = round(us_df["_rating"].mean(),   2) if not us_df["_rating"].isna().all()   else "—"
avg_comp = round(comp_df["_rating"].mean(), 2) if not comp_df["_rating"].isna().all() else "—"
high_t   = len(comp_df[comp_df["_threat"] >= 4])
cov      = df["Neighborhood / Area"].nunique()

try:
    dr = round(float(avg_us) - float(avg_comp), 2) if avg_us != "—" and avg_comp != "—" else None
    dhtml = f'<div class="stat-delta {"delta-up" if dr>=0 else "delta-dn"}">{"▲" if dr>=0 else "▼"} {abs(dr):.2f} vs competitors</div>' if dr is not None else ""
except:
    dhtml = ""

st.markdown(f"""
<div class="stat-row">
    <div class="stat-card c1"><div class="stat-icon">🏥</div>
        <div class="stat-lbl">Total Clinics</div><div class="stat-val">{len(df)}</div>
        <div class="stat-sub">{len(us_df)} ours · {len(comp_df)} competitors</div></div>
    <div class="stat-card c2"><div class="stat-icon">⚠️</div>
        <div class="stat-lbl">Critical / High Threat</div><div class="stat-val">{high_t}</div>
        <div class="stat-sub">Threat level 4–5 — priority monitoring</div></div>
    <div class="stat-card c3"><div class="stat-icon">⭐</div>
        <div class="stat-lbl">Our Avg Rating</div><div class="stat-val">{avg_us}</div>{dhtml}</div>
    <div class="stat-card c4"><div class="stat-icon">📍</div>
        <div class="stat-lbl">Neighborhoods</div><div class="stat-val">{cov}</div>
        <div class="stat-sub">Distinct areas tracked</div></div>
    <div class="stat-card c5"><div class="stat-icon">🏆</div>
        <div class="stat-lbl">Comp Avg Rating</div><div class="stat-val">{avg_comp}</div>
        <div class="stat-sub">All {len(comp_df)} competitors</div></div>
</div>
""", unsafe_allow_html=True)

# ── BIG CTA → MAP PAGE ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="map-cta-banner">
    <div class="map-cta-icon">🗺️</div>
    <div class="map-cta-text">
        <div class="map-cta-title">Explore the Interactive Market Map</div>
        <div class="map-cta-sub">Plot all {len(df)} clinics across NYC, filter by area / threat / insurance, and click any pin to pull up full competitive intelligence in a side panel.</div>
    </div>
</div>
""", unsafe_allow_html=True)
if st.button("🗺️  OPEN LIVE MARKET MAP  →", type="primary", use_container_width=True, key="goto_map_btn"):
    go_map()

st.write("")

# ── Charts Row ────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-hdr"><div class="sec-title">Market Analytics</div><div class="sec-pill">NYC Physical Therapy Landscape</div></div>', unsafe_allow_html=True)

ch1, ch2, ch3 = st.columns([1, 1.35, 1.35])
with ch1:
    st.markdown('<div class="chart-card"><div class="chart-hdr"><span class="chart-hdr-title">Threat Distribution</span><span class="chart-hdr-sub">all competitors</span></div><div class="chart-body">', unsafe_allow_html=True)
    st.plotly_chart(chart_threat_donut(df), use_container_width=True, config={"displayModeBar": False}, theme=None)
    st.markdown("</div></div>", unsafe_allow_html=True)

with ch2:
    st.markdown('<div class="chart-card"><div class="chart-hdr"><span class="chart-hdr-title">Clinics by Borough</span><span class="chart-hdr-sub">PT of the City vs competitors</span></div><div class="chart-body">', unsafe_allow_html=True)
    fb = chart_borough_breakdown(df)
    if fb:
        st.plotly_chart(fb, use_container_width=True, config={"displayModeBar": False}, theme=None)
    else:
        st.markdown('<div style="padding:20px;color:#94A3B8;text-align:center;">No data</div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

with ch3:
    st.markdown('<div class="chart-card"><div class="chart-hdr"><span class="chart-hdr-title">Top 20 Competitors</span><span class="chart-hdr-sub">by review count · color = threat level</span></div><div class="chart-body">', unsafe_allow_html=True)
    ft = chart_top20_reviews(df)
    if ft:
        st.plotly_chart(ft, use_container_width=True, config={"displayModeBar": False}, theme=None)
    else:
        st.markdown('<div style="padding:20px;color:#94A3B8;text-align:center;">No data</div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

st.write("")

# ── TOP 7 TABLE ───────────────────────────────────────────────────────────────
st.markdown('<div class="sec-hdr"><div class="sec-title">🏆 Top 7 Competitor Clinics in NYC</div><div class="sec-pill">Strength &amp; Weakness Analysis</div></div>', unsafe_allow_html=True)

rank_cls = {1: "r1", 2: "r2", 3: "r3"}
threat_colors = {5: "#DC2626", 4: "#F59E0B", 3: "#EAB308", 2: "#60A5FA", 1: "#10B981"}
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

for cl in TOP7_DATA:
    rk = cl["rank"]
    ti = cl["threat"]
    tc = threat_colors.get(ti, "#CBD5E1")
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

# ── Filters + Clinic Table ────────────────────────────────────────────────────
st.markdown('<div class="sec-hdr"><div class="sec-title">All Clinics</div><div class="sec-pill">Filter and browse the full roster</div></div>', unsafe_allow_html=True)

search_q, f_area, f_threat, f_ins, show_us, sort_by = render_filter_widgets("dash")
fdf = apply_filters(df, search_q, f_area, f_threat, f_ins, show_us, sort_by)

st.markdown(f'<div class="sec-hdr" style="margin-top:-4px;"><div></div><div class="sec-pill">{len(fdf)} results</div></div>', unsafe_allow_html=True)
st.markdown('<div class="tbl-wrap"><div class="tbl-head"><span>Clinic Name</span><span>Neighborhood</span><span>Rating</span><span>Reviews</span><span>G. Score</span><span>Threat</span><span></span></div>', unsafe_allow_html=True)

for i, (_, row) in enumerate(fdf.iterrows()):
    name   = row["Clinic Name"]
    iu     = row["_is_us"]
    t      = row["_threat"]
    area   = row["Neighborhood / Area"] or "—"
    rating = f"⭐ {row['_rating']}" if pd.notna(row["_rating"]) else "—"
    revs   = f"{int(row['_reviews']):,}" if pd.notna(row["_reviews"]) else "—"
    gscore = fmt_gscore(row.get("_google_score"))
    bdg    = threat_badge(t, iu)
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
        if st.button("View →", key=f"v_{name}_{i}", use_container_width=True):
            open_clinic(name)
    if i < len(fdf) - 1:
        st.markdown('<div class="div-row"></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.write("")
st.markdown('</div>', unsafe_allow_html=True)