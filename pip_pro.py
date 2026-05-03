"""
PIP PRO — Integrated Platform v1.0
Splash · Login · Dashboard · Sesiones · Jugadores · Análisis Técnico (PIP ONE) · Reportes · ...
"""

import streamlit as st
import io, uuid, re, time as _match_time
from datetime import datetime
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

DB_PATH = "pip_one.db"


# ══════════════════════════════════════════════════════════════════════════════
# SUPABASE
# ══════════════════════════════════════════════════════════════════════════════
SUPABASE_URL = "https://qknilpypekeytixvgobd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrbmlscHlwZWtleXRpeHZnb2JkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4MzM2NDYsImV4cCI6MjA5MzQwOTY0Nn0.q0bCAMbtdDM1_p-5afkE4MIR2-FnTpA_KfWJoWl96Vw"

@st.cache_resource
def get_sb():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def _q(table, filters=None, order=None, desc_order=False, limit=None, columns="*"):
    q = get_sb().table(table).select(columns)
    if filters:
        for k, v in filters.items():
            q = q.eq(k, v)
    if order:
        q = q.order(order, desc=desc_order)
    if limit:
        q = q.limit(limit)
    try:
        return q.execute().data or []
    except:
        return []

def _one(table, filters=None, order=None, desc_order=False):
    rows = _q(table, filters, order, desc_order, limit=1)
    return rows[0] if rows else None

def _ins(table, data):
    try:
        get_sb().table(table).insert(data).execute()
    except Exception as e:
        st.error(f"Error BD: {e}")

def _upd(table, data, filters):
    q = get_sb().table(table).update(data)
    for k, v in filters.items():
        q = q.eq(k, v)
    try:
        q.execute()
    except Exception as e:
        st.error(f"Error BD: {e}")

def _del(table, filters):
    q = get_sb().table(table).delete()
    for k, v in filters.items():
        q = q.eq(k, v)
    try:
        q.execute()
    except Exception as e:
        st.error(f"Error BD: {e}")

def _cnt(table, filters=None):
    return len(_q(table, filters, columns="id"))

def auth_login(email, password):
    try:
        res = get_sb().auth.sign_in_with_password({"email": email, "password": password})
        return res.user, None
    except Exception as e:
        return None, str(e)

def auth_signup(email, password):
    try:
        res = get_sb().auth.sign_up({"email": email, "password": password})
        return res.user, None
    except Exception as e:
        return None, str(e)

st.set_page_config(
    page_title="PIP PRO",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS — PIP PRO Design System
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f !important;
    color: #e8e8f0 !important;
}
.stApp { background-color: #0a0a0f !important; }
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 13px !important; padding: 0.55rem 1rem !important;
    width: 100% !important; cursor: pointer !important; transition: all 0.18s ease !important;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.45) !important;
}
.stButton > button:disabled {
    background: rgba(255,255,255,0.05) !important; color: #374151 !important;
    transform: none !important; box-shadow: none !important;
}

/* ── Nav buttons — maxima especificitat ── */
div.nav-btn button,
div.nav-btn [data-testid="stButton"] button,
div.nav-btn [data-testid="baseButton-secondary"],
div.nav-btn > div > button {
    background: transparent !important;
    background-image: none !important;
    color: #6b7280 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 9px 12px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    box-shadow: none !important;
    border: none !important;
    letter-spacing: 0 !important;
    transform: none !important;
    min-height: 36px !important;
}
div.nav-btn button:hover,
div.nav-btn [data-testid="stButton"] button:hover,
div.nav-btn > div > button:hover {
    background: rgba(255,255,255,0.06) !important;
    background-image: none !important;
    color: #d1d5db !important;
    transform: none !important;
    box-shadow: none !important;
}
div.nav-btn-active button,
div.nav-btn-active [data-testid="stButton"] button,
div.nav-btn-active [data-testid="baseButton-secondary"],
div.nav-btn-active > div > button {
    background: rgba(124,58,237,0.18) !important;
    background-image: none !important;
    color: #a78bfa !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    border: none !important;
    transform: none !important;
}
div.nav-btn-active button:hover,
div.nav-btn-active > div > button:hover {
    background: rgba(124,58,237,0.25) !important;
    transform: none !important;
}
/* Multiselect pills */
[data-baseweb="tag"] {
    background: rgba(124,58,237,0.25) !important;
    border: 1px solid rgba(124,58,237,0.5) !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span { color: #c4b5fd !important; }
[data-baseweb="tag"] button { color: #a78bfa !important; background: transparent !important; width:auto !important; }

/* ── Força tema fosc global ── */
html, body, .stApp, .main, .block-container,
[data-testid="stAppViewContainer"],
[data-baseweb="base-input"], [data-baseweb="input-container"] {
    background-color: #0a0a0f !important;
    color: #e8e8f0 !important;
}

/* ── Inputs: màxima especificitat ── */
input, textarea,
.stTextInput input,
.stTextInput > div > div > input,
[data-baseweb="base-input"] input,
[data-testid="stTextInputRootElement"] input,
div[class*="Input"] input {
    background: #13131f !important;
    background-color: #13131f !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    -webkit-text-fill-color: #e8e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.6rem 1rem !important;
    caret-color: #a78bfa !important;
}
input:focus, .stTextInput > div > div > input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.25) !important;
    outline: none !important;
}
input::placeholder, .stTextInput input::placeholder {
    color: #4b5563 !important;
    -webkit-text-fill-color: #4b5563 !important;
    opacity: 1 !important;
}
/* Botó de l'ull (password) */
[data-testid="stTextInputRootElement"] button {
    background: transparent !important; color: #6b7280 !important;
    border: none !important; box-shadow: none !important;
    width: auto !important; padding: 0 8px !important; transform: none !important;
}
.stTextInput > label, .stTextInput label {
    color: #6b7280 !important; font-size: 11px !important;
    letter-spacing:.08em !important; text-transform: uppercase !important;
}
/* Selectbox */
.stSelectbox > div > div,
[data-baseweb="select"] > div {
    background: #13131f !important; border: 1px solid rgba(255,255,255,0.15) !important;
    color: #e8e8f0 !important; border-radius: 8px !important;
}
[data-baseweb="select"] span { color: #e8e8f0 !important; }
[data-baseweb="popover"] ul, [data-baseweb="menu"] {
    background: #13131f !important; border: 1px solid rgba(255,255,255,0.12) !important;
}
[data-baseweb="menu"] li { color: #e8e8f0 !important; }
[data-baseweb="menu"] li:hover { background: rgba(124,58,237,0.15) !important; }
.stRadio > label { color: #6b7280 !important; font-size: 12px !important; letter-spacing:.06em !important; text-transform: uppercase !important; }
div[data-testid="stCheckbox"] label { color: #9ca3af !important; font-size: 13px !important; }
[data-testid="stTabs"] [role="tab"] { font-family:'DM Sans',sans-serif !important; font-weight:600 !important; letter-spacing:1px !important; font-size:0.75rem !important; color:#6b7280 !important; text-transform:uppercase !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color:#a78bfa !important; border-bottom:2px solid #7c3aed !important; }
[data-testid="metric-container"] { background:rgba(255,255,255,0.04) !important; border:1px solid rgba(255,255,255,0.09) !important; border-radius:10px !important; padding:12px !important; }
[data-testid="metric-container"] label { color:#6b7280 !important; font-size:0.68rem !important; letter-spacing:1px !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color:#a78bfa !important; font-family:'DM Sans',sans-serif !important; font-size:1.4rem !important; font-weight:700 !important; }
hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── Logo ── */
.pip-logo { font-family:'Orbitron',monospace; font-weight:900; letter-spacing:.05em; }
.pip-logo .pip { color:#e8e8f0; }
.pip-logo .pro { color:#7c3aed; }

/* ── Glow orb ── */
.glow-orb {
    width:200px; height:200px; border-radius:50%; margin:0 auto 2rem;
    position:relative; display:flex; align-items:center; justify-content:center;
}
.glow-orb::before {
    content:''; position:absolute; inset:0; border-radius:50%;
    background: radial-gradient(circle at 35% 35%, rgba(139,92,246,0.3), transparent 60%),
                radial-gradient(circle at 65% 65%, rgba(79,70,229,0.2), transparent 60%);
    border:1.5px solid rgba(139,92,246,0.5);
    box-shadow:0 0 60px rgba(124,58,237,0.4), inset 0 0 40px rgba(124,58,237,0.1);
    animation:pulse 3s ease-in-out infinite;
}
.glow-orb::after { content:''; position:absolute; inset:15px; border-radius:50%; border:1px solid rgba(139,92,246,0.25); }
@keyframes pulse {
    0%,100% { box-shadow:0 0 60px rgba(124,58,237,0.4), inset 0 0 40px rgba(124,58,237,0.1); }
    50% { box-shadow:0 0 90px rgba(124,58,237,0.6), inset 0 0 60px rgba(124,58,237,0.2); }
}
@keyframes loadbar { 0%{width:0%} 100%{width:100%} }
.loading-bar-wrap { width:180px; height:2px; background:rgba(255,255,255,0.1); border-radius:2px; margin:2rem auto 0; overflow:hidden; }
.loading-bar-inner { height:100%; background:linear-gradient(90deg,#7c3aed,#a78bfa); border-radius:2px; animation:loadbar 2.2s ease-in-out forwards; }

/* ── Cards ── */
.pip-card { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09); border-radius:14px; padding:1.5rem; }
.pip-card-sm { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09); border-radius:10px; padding:1rem 1.25rem; }
.pip-card-accent { background:rgba(124,58,237,0.08); border:1px solid rgba(124,58,237,0.25); border-radius:10px; padding:1rem 1.25rem; }
.pip-card-warn { background:rgba(239,68,68,0.07); border:1px solid rgba(239,68,68,0.2); border-radius:10px; padding:1rem 1.25rem; }
.pip-card-open { background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.2); border-radius:10px; padding:1rem 1.25rem; }

/* ── Sidebar nav ── */
.nav-sidebar { background:#0d0d17; border-right:1px solid rgba(255,255,255,0.07); min-height:100vh; padding:1.4rem 0.8rem; }

/* ── Table ── */
.pip-table { width:100%; border-collapse:collapse; font-size:13px; }
.pip-table th { color:#6b7280; font-weight:500; font-size:10px; letter-spacing:.1em; text-transform:uppercase; padding:10px 12px; border-bottom:1px solid rgba(255,255,255,0.07); text-align:left; }
.pip-table td { padding:10px 12px; border-bottom:1px solid rgba(255,255,255,0.04); color:#c9cad4; }
.pip-table tr:hover td { background:rgba(255,255,255,0.03); }

/* ── Badges ── */
.badge { display:inline-block; font-size:10px; font-weight:600; padding:2px 9px; border-radius:20px; letter-spacing:.04em; }
.badge-green  { background:rgba(16,185,129,0.15); color:#34d399; }
.badge-yellow { background:rgba(251,191,36,0.15); color:#fbbf24; }
.badge-purple { background:rgba(124,58,237,0.2); color:#a78bfa; }
.badge-red    { background:rgba(239,68,68,0.15); color:#f87171; }
.badge-gray   { background:rgba(255,255,255,0.07); color:#6b7280; }
.badge-blue   { background:rgba(59,130,246,0.15); color:#60a5fa; }

/* ── Info bar ── */
.info-bar { display:flex; gap:1.2rem; align-items:center; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:.7rem 1.2rem; margin-bottom:1.2rem; font-size:12.5px; color:#9ca3af; flex-wrap:wrap; }
.info-bar span { display:flex; align-items:center; gap:5px; }
.info-bar strong { color:#d1d5db; }

/* ── Avatar ── */
.avatar-chip { display:flex; align-items:center; gap:10px; background:rgba(255,255,255,0.05); border-radius:10px; padding:8px 12px; }
.avatar { width:32px; height:32px; border-radius:50%; background:linear-gradient(135deg,#7c3aed,#4f46e5); display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:white; flex-shrink:0; }

/* ── Section titles ── */
.stitle { font-family:'DM Sans',sans-serif; font-weight:600; font-size:9.5px; letter-spacing:.14em; color:#374151; text-transform:uppercase; margin-bottom:10px; padding-bottom:5px; border-bottom:1px solid rgba(255,255,255,0.06); }

/* ── Event log ── */
.elog { display:flex; align-items:center; gap:7px; padding:5px 9px; border-radius:6px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); margin-bottom:3px; font-size:.76rem; }

/* ── Metric bars ── */
.sbar-wrap { display:flex; align-items:center; gap:8px; margin-bottom:5px; }
.sbar-label { font-size:.7rem; color:#6b7280; width:68px; text-align:right; flex-shrink:0; }
.sbar-bg { flex:1; background:rgba(255,255,255,0.08); border-radius:3px; height:5px; overflow:hidden; }
.sbar-fill { height:5px; border-radius:3px; }
.sbar-val { font-family:'DM Sans',sans-serif; font-weight:700; font-size:.82rem; width:28px; }

/* ── Analysis block ── */
.analysis-block { background:rgba(124,58,237,0.08); border-left:3px solid #7c3aed; padding:12px 16px; border-radius:0 8px 8px 0; margin:8px 0; font-size:.83rem; line-height:1.65; color:#9ca3af; }

/* ── Empty state ── */
.empty-state { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:4rem 2rem; text-align:center; }
.empty-icon { font-size:2.8rem; margin-bottom:1rem; opacity:.25; }
.empty-title { font-size:15px; font-weight:600; color:#374151; margin-bottom:.4rem; }
.empty-sub { font-size:12.5px; color:#1f2937; }

/* ── Page header ── */
.page-header { padding:1.5rem 2rem 0; margin-bottom:1rem; }
.page-title { font-size:20px; font-weight:700; color:#f3f4f6; margin:0 0 .2rem; }
.page-sub { font-size:13px; color:#6b7280; margin:0; }
</style>
""", unsafe_allow_html=True)

def normalise_session(s):
    if not s: return s
    s = dict(s); s.setdefault("category","Partido"); s.setdefault("exercise_type","Partido")
    if not s.get("category"): s["category"] = "Partido"
    if not s.get("exercise_type"): s["exercise_type"] = "Partido"
    return s

def normalise_player(p):
    if not p: return p
    p = dict(p)
    if not p.get("position"): p["position"] = "MED"
    return p

def fmt_dt(iso):
    if not iso: return "—"
    try:
        s = str(iso).replace("Z", "+00:00")
        return datetime.fromisoformat(s).strftime("%d/%m/%Y %H:%M")
    except:
        return str(iso)[:16]

def pos_color(pos):
    return {"GK":"#f59e0b","DEF":"#10b981","MED":"#8b5cf6","DEL":"#ef4444"}.get(pos,"#6b7280")

def pos_badge_html(pos):
    c = pos_color(pos)
    return f'<span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;background:{c}22;color:{c};border:1px solid {c}44;">{pos}</span>'

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES & EVENTOS
# ══════════════════════════════════════════════════════════════════════════════
POSITIONS = ["GK","DEF","MED","DEL"]
POS_NAMES = {"GK":"Portero","DEF":"Defensa","MED":"Centrocampista","DEL":"Delantero"}
CATEGORIES = ["Partido","Entrenamiento"]
EXERCISES = ["Rondo / Posesión","Ataque organizado","Defensa organizada","1v1 / Duelos","Pressing","Finalización"]
EX_DESC = {
    "Rondo / Posesión":"Técnica y decisión bajo presión","Ataque organizado":"Combinaciones, movilidad, remate",
    "Defensa organizada":"Bloque, duelos, recuperación","1v1 / Duelos":"Situaciones individuales",
    "Pressing":"Intensidad, recuperación alta","Finalización":"Tiro, remate, definición",
}
EX_COLOR = {
    "Rondo / Posesión":"#3498db","Ataque organizado":"#ef4444","Defensa organizada":"#10b981",
    "1v1 / Duelos":"#f59e0b","Pressing":"#f97316","Finalización":"#ef4444","Partido":"#7c3aed",
}
WEIGHTS = {
    ("Partido","GK"):{"technical":.15,"decision":.20,"offensive":.10,"defensive":.55},
    ("Partido","DEF"):{"technical":.20,"decision":.25,"offensive":.20,"defensive":.35},
    ("Partido","MED"):{"technical":.25,"decision":.28,"offensive":.25,"defensive":.22},
    ("Partido","DEL"):{"technical":.18,"decision":.22,"offensive":.45,"defensive":.15},
    ("Rondo / Posesión","GK"):{"technical":.40,"decision":.35,"offensive":.00,"defensive":.25},
    ("Rondo / Posesión","DEF"):{"technical":.35,"decision":.30,"offensive":.10,"defensive":.25},
    ("Rondo / Posesión","MED"):{"technical":.40,"decision":.35,"offensive":.10,"defensive":.15},
    ("Rondo / Posesión","DEL"):{"technical":.35,"decision":.35,"offensive":.20,"defensive":.10},
    ("Ataque organizado","GK"):{"technical":.20,"decision":.35,"offensive":.00,"defensive":.45},
    ("Ataque organizado","DEF"):{"technical":.25,"decision":.30,"offensive":.15,"defensive":.30},
    ("Ataque organizado","MED"):{"technical":.25,"decision":.30,"offensive":.30,"defensive":.15},
    ("Ataque organizado","DEL"):{"technical":.15,"decision":.20,"offensive":.50,"defensive":.15},
    ("Defensa organizada","GK"):{"technical":.15,"decision":.25,"offensive":.00,"defensive":.60},
    ("Defensa organizada","DEF"):{"technical":.20,"decision":.25,"offensive":.10,"defensive":.45},
    ("Defensa organizada","MED"):{"technical":.20,"decision":.30,"offensive":.15,"defensive":.35},
    ("Defensa organizada","DEL"):{"technical":.20,"decision":.30,"offensive":.25,"defensive":.25},
    ("1v1 / Duelos","GK"):{"technical":.10,"decision":.40,"offensive":.00,"defensive":.50},
    ("1v1 / Duelos","DEF"):{"technical":.15,"decision":.30,"offensive":.15,"defensive":.40},
    ("1v1 / Duelos","MED"):{"technical":.20,"decision":.30,"offensive":.25,"defensive":.25},
    ("1v1 / Duelos","DEL"):{"technical":.15,"decision":.30,"offensive":.40,"defensive":.15},
    ("Pressing","GK"):{"technical":.15,"decision":.35,"offensive":.00,"defensive":.50},
    ("Pressing","DEF"):{"technical":.20,"decision":.25,"offensive":.15,"defensive":.40},
    ("Pressing","MED"):{"technical":.20,"decision":.30,"offensive":.20,"defensive":.30},
    ("Pressing","DEL"):{"technical":.20,"decision":.30,"offensive":.30,"defensive":.20},
    ("Finalización","GK"):{"technical":.15,"decision":.30,"offensive":.00,"defensive":.55},
    ("Finalización","DEF"):{"technical":.25,"decision":.25,"offensive":.20,"defensive":.30},
    ("Finalización","MED"):{"technical":.25,"decision":.25,"offensive":.30,"defensive":.20},
    ("Finalización","DEL"):{"technical":.20,"decision":.20,"offensive":.50,"defensive":.10},
}
DEFAULT_W = {"technical":.25,"decision":.25,"offensive":.25,"defensive":.25}
def get_weights(ex, pos): return WEIGHTS.get((ex, pos), DEFAULT_W)

GK_EVENTS = {
    "save":{"label":"Parada","color":"#10b981","cat":"defensive"},
    "great_save":{"label":"Parada difícil","color":"#34d399","cat":"defensive"},
    "penalty_saved":{"label":"Penalti parado","color":"#fbbf24","cat":"defensive"},
    "one_v_one_won":{"label":"1v1 ganado","color":"#10b981","cat":"defensive"},
    "one_v_one_lost":{"label":"1v1 perdido","color":"#ef4444","cat":"defensive"},
    "clearance":{"label":"Despeje","color":"#60a5fa","cat":"defensive"},
    "cross_caught":{"label":"Centro atrapado","color":"#3b82f6","cat":"defensive"},
    "good_exit":{"label":"Salida ✓","color":"#10b981","cat":"defensive"},
    "bad_exit":{"label":"Salida ✗","color":"#ef4444","cat":"defensive"},
    "short_pass_ok":{"label":"Pase corto ✓","color":"#3b82f6","cat":"technical"},
    "short_pass_fail":{"label":"Pase corto ✗","color":"#dc2626","cat":"technical"},
    "long_pass_ok":{"label":"Pase largo ✓","color":"#2563eb","cat":"technical"},
    "long_pass_fail":{"label":"Pase largo ✗","color":"#dc2626","cat":"technical"},
    "gk_error":{"label":"Error","color":"#dc2626","cat":"general"},
}
GK_LAYOUT = [
    ("save","great_save"),("penalty_saved","one_v_one_won"),("one_v_one_lost","clearance"),
    ("cross_caught","good_exit"),("bad_exit","short_pass_ok"),
    ("short_pass_fail","long_pass_ok"),("long_pass_fail","gk_error"),
]
FIELD_EVENTS = {
    "pass_success":{"label":"Pase ✓","color":"#10b981","cat":"technical"},
    "pass_fail":{"label":"Pase ✗","color":"#ef4444","cat":"technical"},
    "control_success":{"label":"Control ✓","color":"#3b82f6","cat":"technical"},
    "control_fail":{"label":"Control ✗","color":"#dc2626","cat":"technical"},
    "header_success":{"label":"Cabezazo ✓","color":"#34d399","cat":"technical"},
    "header_fail":{"label":"Cabezazo ✗","color":"#ef4444","cat":"technical"},
    "decision_correct":{"label":"Decisión ✓","color":"#06b6d4","cat":"decision"},
    "decision_wrong":{"label":"Decisión ✗","color":"#ef4444","cat":"decision"},
    "shot":{"label":"Tiro ✗","color":"#ef4444","cat":"offensive"},
    "shot_on_target":{"label":"Tiro a gol ✓","color":"#f59e0b","cat":"offensive"},
    "goal":{"label":"Gol ⚽","color":"#fbbf24","cat":"offensive"},
    "assist":{"label":"Asistencia","color":"#f59e0b","cat":"offensive"},
    "dribble_success":{"label":"Regate ✓","color":"#10b981","cat":"offensive"},
    "dribble_fail":{"label":"Regate ✗","color":"#ef4444","cat":"offensive"},
    "corner_won":{"label":"Córner ganado","color":"#f97316","cat":"offensive"},
    "recovery":{"label":"Recuperación","color":"#8b5cf6","cat":"defensive"},
    "interception":{"label":"Intercepción","color":"#7c3aed","cat":"defensive"},
    "duel_off_won":{"label":"Duelo ofensivo ✓","color":"#10b981","cat":"offensive"},
    "duel_off_lost":{"label":"Duelo ofensivo ✗","color":"#ef4444","cat":"offensive"},
    "duel_def_won":{"label":"Duelo defensivo ✓","color":"#10b981","cat":"defensive"},
    "duel_def_lost":{"label":"Duelo defensivo ✗","color":"#ef4444","cat":"defensive"},
    "aerial_off_won":{"label":"Aéreo ofensivo ✓","color":"#34d399","cat":"offensive"},
    "aerial_off_lost":{"label":"Aéreo ofensivo ✗","color":"#dc2626","cat":"offensive"},
    "aerial_def_won":{"label":"Aéreo defensivo ✓","color":"#3b82f6","cat":"defensive"},
    "aerial_def_lost":{"label":"Aéreo defensivo ✗","color":"#ef4444","cat":"defensive"},
    "pressing_success":{"label":"Pressing ✓","color":"#10b981","cat":"defensive"},
    "pressing_fail":{"label":"Pressing ✗","color":"#ef4444","cat":"defensive"},
    "foul_received":{"label":"Falta recibida","color":"#3b82f6","cat":"general"},
    "foul_committed":{"label":"Falta cometida","color":"#f97316","cat":"general"},
    "offside":{"label":"Fuera de juego","color":"#ef4444","cat":"general"},
    "ball_loss":{"label":"Pérdida de balón","color":"#dc2626","cat":"general"},
    "error":{"label":"Error","color":"#dc2626","cat":"general"},
}
FIELD_LAYOUT = [
    ("pass_success","pass_fail"),("control_success","control_fail"),("header_success","header_fail"),
    ("decision_correct","decision_wrong"),("shot","shot_on_target"),("goal","assist"),
    ("dribble_success","dribble_fail"),("corner_won",None),
    ("duel_off_won","duel_off_lost"),
    ("duel_def_won","duel_def_lost"),
    ("aerial_off_won","aerial_off_lost"),
    ("aerial_def_won","aerial_def_lost"),
    ("foul_received","foul_committed"),("offside","ball_loss"),("error",None),
]
ALL_EVENTS = {**GK_EVENTS, **FIELD_EVENTS}
CAT_LABELS = {"technical":"Técnica","decision":"Decisión","offensive":"Ataque","defensive":"Defensa"}

# ══════════════════════════════════════════════════════════════════════════════
# MOTOR DE MÉTRICAS
# ══════════════════════════════════════════════════════════════════════════════
def compute_metrics(events_list, position, exercise_key):
    if not events_list: return None
    def cnt(k): return sum(1 for e in events_list if e["event_type"]==k)
    total = len(events_list); w = get_weights(exercise_key, position)

    if position == "GK":
        saves = cnt("save") + cnt("great_save"); great = cnt("great_save")
        clr = cnt("clearance"); cross_ok = cnt("cross_caught")
        good_ex = cnt("good_exit"); bad_ex = cnt("bad_exit")
        sp_ok = cnt("short_pass_ok"); sp_fail = cnt("short_pass_fail")
        lp_ok = cnt("long_pass_ok"); lp_fail = cnt("long_pass_fail")
        gk_err = cnt("gk_error")
        save_rate = saves / max(saves + gk_err, 1)
        exit_rate = good_ex / max(good_ex + bad_ex, 1)
        sp_acc = sp_ok / max(sp_ok + sp_fail, 1); lp_acc = lp_ok / max(lp_ok + lp_fail, 1)
        part = min(total / 15.0, 1.0); err_pen = min(gk_err * 0.08, 0.30)
        tech = max(0, (sp_acc * 0.5 + lp_acc * 0.5) - err_pen * 0.5)
        dec = max(0, exit_rate - err_pen * 0.3); off = 0.0
        defe = max(0, min(save_rate * 0.7 + (clr / max(clr+1,1)) * 0.3 - err_pen * 0.5, 1.0))
        g = min(tech*w["technical"]+dec*w["decision"]+off*w["offensive"]+defe*w["defensive"]+part*0.4, 1.0)
        return {
            "is_gk":True,"total_events":total,"position":position,"exercise_type":exercise_key,
            "w_technical":w["technical"],"w_decision":w["decision"],"w_offensive":w["offensive"],"w_defensive":w["defensive"],
            "save_rate":round(save_rate*100,1),"exit_rate":round(exit_rate*100,1),
            "short_pass_acc":round(sp_acc*100,1),"long_pass_acc":round(lp_acc*100,1),
            "total_saves":saves,"great_saves":great,"errors":gk_err,
            "participation_rate":round(part*100,1),
            "score_technical":round(tech*10,1),"score_decision":round(dec*10,1),
            "score_offensive":0.0,"score_defensive":round(defe*10,1),"rating":round(g*10,1),
            "pass_accuracy":0,"control_accuracy":0,"decision_score":0,"dribble_accuracy":0,
            "duel_accuracy":0,"total_shots":0,"shots_on_target":0,"goals":0,
            "offensive_actions":0,"defensive_actions":saves+clr+cross_ok+good_ex,
            "recoveries":0,"interceptions":0,"assists":0,"corners_won":0,
            "header_accuracy":0,"pressing_accuracy":0,"fouls_received":0,"fouls_committed":0,
            "offsides":0,"ball_losses":0,
        }
    else:
        ps,pf = cnt("pass_success"),cnt("pass_fail")
        cs,cf = cnt("control_success"),cnt("control_fail")
        hs,hf = cnt("header_success"),cnt("header_fail")
        dc,dw = cnt("decision_correct"),cnt("decision_wrong")
        sh,sot = cnt("shot"),cnt("shot_on_target"); gl = cnt("goal"); ast = cnt("assist")
        drs,drf = cnt("dribble_success"),cnt("dribble_fail"); crn = cnt("corner_won")
        rec,icp = cnt("recovery"),cnt("interception")
        duw_off=cnt("duel_off_won"); dul_off=cnt("duel_off_lost")
        duw_def=cnt("duel_def_won"); dul_def=cnt("duel_def_lost")
        aer_ow=cnt("aerial_off_won"); aer_ol=cnt("aerial_off_lost")
        aer_dw=cnt("aerial_def_won"); aer_dl=cnt("aerial_def_lost")
        duw=duw_off+duw_def+aer_ow+aer_dw; dul=dul_off+dul_def+aer_ol+aer_dl
        prs,prf = cnt("pressing_success"),cnt("pressing_fail")
        f_recv,f_comm = cnt("foul_received"),cnt("foul_committed")
        offsides,bl,err = cnt("offside"),cnt("ball_loss"),cnt("error")
        pa = ps/(ps+pf) if (ps+pf)>0 else 0.0
        ca = cs/(cs+cf) if (cs+cf)>0 else 0.0
        ha = hs/(hs+hf) if (hs+hf)>0 else 0.5
        da = dc/(dc+dw) if (dc+dw)>0 else 0.0
        dra = drs/(drs+drf) if (drs+drf)>0 else 0.0
        dua = duw/(duw+dul) if (duw+dul)>0 else 0.0
        pra = prs/(prs+prf) if (prs+prf)>0 else 0.5
        part = min(total/25.0, 1.0)
        neg_pen = min((err*0.06+f_comm*0.03+offsides*0.03+bl*0.04), 0.30)
        tech = max(0, (pa*0.45+ca*0.35+ha*0.20) - neg_pen*0.6)
        dec = max(0, da - neg_pen*0.4)
        drb_score = dra if (drs+drf)>0 else 0.5
        off_total = sh+sot+gl+drs+ast+crn+duw_off+aer_ow
        off = (min(off_total/7.0,1.0)*0.35+(sot/max(sh+0.01,1))*0.25+min(gl,1)*0.15+min(ast/2,1)*0.10+drb_score*0.10+min(f_recv*0.02,0.05))
        def_total = rec+icp+duw_def+aer_dw+prs
        defe = (min(def_total/6.0,1.0)*0.45+dua*0.30+pra*0.25)
        g = tech*w["technical"]+dec*w["decision"]+off*w["offensive"]+defe*w["defensive"]
        g = min(g+part*0.4, 1.0)
        return {
            "is_gk":False,"total_events":total,"position":position,"exercise_type":exercise_key,
            "w_technical":w["technical"],"w_decision":w["decision"],"w_offensive":w["offensive"],"w_defensive":w["defensive"],
            "save_rate":0,"exit_rate":0,"short_pass_acc":0,"long_pass_acc":0,"total_saves":0,"great_saves":0,
            "pass_accuracy":round(pa*100,1),"control_accuracy":round(ca*100,1),
            "decision_score":round(da*100,1),"dribble_accuracy":round(dra*100,1),"duel_accuracy":round(dua*100,1),
            "total_shots":sh+sot,"shots_on_target":sot,"goals":gl,"offensive_actions":off_total,"defensive_actions":def_total,
            "recoveries":rec,"interceptions":icp,"errors":err,"assists":ast,"corners_won":crn,
            "header_accuracy":round(ha*100,1),"pressing_accuracy":round(pra*100,1),
            "fouls_received":f_recv,"fouls_committed":f_comm,"offsides":offsides,"ball_losses":bl,
            "participation_rate":round(part*100,1),
            "score_technical":round(tech*10,1),"score_decision":round(dec*10,1),
            "score_offensive":round(off*10,1),"score_defensive":round(defe*10,1),"rating":round(g*10,1),
        }

def close_and_compute(session_id, exercise_key):
    sess_info = _one("sessions", {"id": session_id}) or {}
    is_partido = (sess_info.get("category") or "Partido") == "Partido"
    for p in session_players(session_id):
        evs = _q("events", {"session_id": session_id, "player_id": p["id"]})
        m = compute_metrics(evs, p["position"], exercise_key)
        if not m: continue
        # Override participation with minutes if partido
        mins = player_minutes(p, is_partido)
        if mins is not None:
            m["participation_rate"] = round(min(mins / 90.0, 1.0) * 100, 1)
        m["is_starter"]    = p.get("is_starter", True)
        m["entry_minute"]  = p.get("entry_minute") or 0
        m["exit_minute"]   = p.get("exit_minute")
        _del("player_metrics", {"session_id": session_id, "player_id": p["id"]})
        _ins("player_metrics", {
            "id": str(uuid.uuid4())[:12], "session_id": session_id, "player_id": p["id"],
            "position": p["position"], "exercise_type": exercise_key,
            "w_technical": m["w_technical"], "w_decision": m["w_decision"],
            "w_offensive": m["w_offensive"], "w_defensive": m["w_defensive"],
            "total_events": m["total_events"], "save_rate": m["save_rate"],
            "exit_rate": m["exit_rate"], "short_pass_acc": m["short_pass_acc"],
            "long_pass_acc": m["long_pass_acc"], "total_saves": m["total_saves"],
            "great_saves": m["great_saves"], "pass_accuracy": m["pass_accuracy"],
            "control_accuracy": m["control_accuracy"], "decision_score": m["decision_score"],
            "dribble_accuracy": m["dribble_accuracy"], "duel_accuracy": m["duel_accuracy"],
            "total_shots": m["total_shots"], "shots_on_target": m["shots_on_target"],
            "goals": m["goals"], "offensive_actions": m["offensive_actions"],
            "defensive_actions": m["defensive_actions"], "recoveries": m["recoveries"],
            "interceptions": m["interceptions"], "errors": m["errors"],
            "participation_rate": m["participation_rate"], "score_technical": m["score_technical"],
            "score_decision": m["score_decision"], "score_offensive": m["score_offensive"],
            "score_defensive": m["score_defensive"], "rating": m["rating"],
            "calculated_at": datetime.now().isoformat()
        })
    _upd("sessions", {"status": "closed", "closed_at": datetime.now().isoformat()}, {"id": session_id})
def analysis_text(player_name, m, exercise_key):
    r = m["rating"]; pos = m["position"]
    nivel = "excepcional" if r>=8 else ("muy bueno" if r>=6.5 else ("correcto" if r>=5 else "mejorable"))
    cats = {"Técnica":m["score_technical"],"Decisión":m["score_decision"],"Ataque":m["score_offensive"],"Defensa":m["score_defensive"]}
    best = max(cats, key=cats.get); worst = min(cats, key=cats.get)
    ex_label = f"**{exercise_key}**" if exercise_key != "Partido" else "el **partido**"
    txt = (f"{player_name} ({POS_NAMES.get(pos,pos)}) ha completado {ex_label} con un rendimiento **{nivel}** — rating **{r}/10**. "
           f"Registró **{m['total_events']} acciones** con una participación del {m['participation_rate']:.0f}%.")
    if pos=="GK":
        if m["total_saves"]>0: txt += f" Realizó **{m['total_saves']} paradas** ({m.get('great_saves',0)} difíciles) con una efectividad del {m['save_rate']:.0f}%."
        if m["exit_rate"]>0: txt += f" En las salidas, su tasa de acierto fue del **{m['exit_rate']:.0f}%**."
    else:
        if m["pass_accuracy"]>0: txt += f" Su precisión de pase es del **{m['pass_accuracy']:.0f}%**."
        if m["offensive_actions"]>0:
            txt += (f" Generó **{m['offensive_actions']} acciones ofensivas**"
                    + (f", incluyendo **{m['goals']} gol{'es' if m['goals']!=1 else ''}**" if m["goals"]>0 else "") + ".")
        if m["defensive_actions"]>0:
            txt += f" En defensa sumó **{m['defensive_actions']} acciones** ({m['recoveries']} recuperaciones, {m['interceptions']} intercepciones)."
    txt += f" Su **mayor fortaleza** es la **{best}** ({cats[best]:.1f}/10) y el área con mayor margen de mejora es la **{worst}** ({cats[worst]:.1f}/10)."
    return txt

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICAS
# ══════════════════════════════════════════════════════════════════════════════
def radar_img(m, name, size=(3.0,3.0)):
    cats = ["Técnica","Decisión","Ataque","Defensa","Particip."]
    vals = [m["score_technical"]/10,m["score_decision"]/10,m["score_offensive"]/10,m["score_defensive"]/10,m["participation_rate"]/100]
    N = len(cats); angles = [n/N*2*np.pi for n in range(N)]; angles += angles[:1]; v = vals+[vals[0]]
    fig, ax = plt.subplots(figsize=size, subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0d0d17"); ax.set_facecolor("#0d0d17")
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(cats, size=8, color="#6b7280")
    ax.set_ylim(0,1); ax.set_yticks([.25,.5,.75,1]); ax.set_yticklabels(["2.5","5","7.5","10"],size=6,color="#1f2937")
    ax.grid(color="#1a1a2e",linewidth=0.8); ax.spines['polar'].set_edgecolor("#1a1a2e")
    pc = pos_color(m["position"])
    ax.plot(angles, v, color=pc, linewidth=2.5); ax.fill(angles, v, color=pc, alpha=0.18)
    for a,vv in zip(angles,v[:-1]): ax.plot(a,vv,"o",color=pc,markersize=5)
    plt.tight_layout(pad=0.5)
    buf = io.BytesIO()
    plt.savefig(buf,format="png",dpi=150,bbox_inches="tight",facecolor="#0d0d17")
    plt.close(fig); buf.seek(0); return buf

def bar_img(m, size=(4.0,1.6)):
    cats = ["Técnica","Decisión","Ataque","Defensa"]
    vals = [m["score_technical"],m["score_decision"],m["score_offensive"],m["score_defensive"]]
    clrs = ["#3b82f6","#8b5cf6","#ef4444","#10b981"]
    fig, ax = plt.subplots(figsize=size)
    fig.patch.set_facecolor("#0d0d17"); ax.set_facecolor("#0d0d17")
    bars = ax.barh(cats, vals, color=clrs, height=0.5)
    for bar, v in zip(bars,vals):
        ax.text(v+0.12, bar.get_y()+bar.get_height()/2, f"{v:.1f}", va="center",ha="left",color="#a78bfa",fontsize=9,fontweight="bold")
    ax.set_xlim(0,11.5); ax.tick_params(colors="#4b5563",labelsize=9)
    for s in ax.spines.values(): s.set_edgecolor("#1a1a2e")
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    plt.tight_layout(pad=0.4)
    buf = io.BytesIO()
    plt.savefig(buf,format="png",dpi=150,bbox_inches="tight",facecolor="#0d0d17")
    plt.close(fig); buf.seek(0); return buf

# ══════════════════════════════════════════════════════════════════════════════
# INFORME HTML
# ══════════════════════════════════════════════════════════════════════════════
def _radar_svg(m):
    import math
    cats = ["TÉCNICA","DEC.","ATAQUE","PART.","DEF."]
    scores = [m["score_technical"],m["score_decision"],m["score_offensive"],m["participation_rate"]/10,m["score_defensive"]]
    cx,cy,R = 100,100,80; n = len(cats)
    angles = [math.radians(90+i*360/n) for i in range(n)]
    axes = [(cx+R*math.cos(a),cy-R*math.sin(a)) for a in angles]
    pts = [(cx+(s/10)*R*math.cos(a),cy-(s/10)*R*math.sin(a)) for s,a in zip(scores,angles)]
    poly_pts = " ".join(f"{x:.1f},{y:.1f}" for x,y in pts)
    pc = {"GK":"#f59e0b","DEF":"#10b981","MED":"#8b5cf6","DEL":"#ef4444"}.get(m["position"],"#7c3aed")
    lines = "".join(f'<line x1="{cx}" y1="{cy}" x2="{ax:.1f}" y2="{ay:.1f}" stroke="#252830" stroke-width="1"/>' for ax,ay in axes)
    circles = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#252830" stroke-width="1"/>' for r in [20,40,60,80])
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{pc}"/>' for x,y in pts)
    label_r = R+14
    labels_svg = "".join(f'<text x="{cx+label_r*math.cos(a):.1f}" y="{cy-label_r*math.sin(a):.1f}" text-anchor="middle" dominant-baseline="central" fill="#9ca3af" font-size="9" font-weight="600">{cat}</text>' for cat,a in zip(cats,angles))
    return f'<svg width="200" height="200" viewBox="0 0 200 200">{circles}{lines}<polygon points="{poly_pts}" fill="{pc}26" stroke="{pc}" stroke-width="2" stroke-linejoin="round"/>{dots}{labels_svg}</svg>'

def make_report_html(player_name, sess, m, analysis, observation):
    import re as _re
    ex_label = sess.get("exercise_type") or "Partido"
    pos_label = {"GK":"Portero","DEF":"Defensa","MED":"Centrocampista","DEL":"Delantero"}.get(m["position"],m["position"])
    date_str = fmt_dt(sess.get("created_at",""))[:10]
    part_str = f'{m["total_events"]} ({m["participation_rate"]:.0f}% part.)'
    pc = {"GK":"#f59e0b","DEF":"#10b981","MED":"#8b5cf6","DEL":"#ef4444"}.get(m["position"],"#7c3aed")
    r = m["rating"]
    nivel = ("Rendimiento Excepcional" if r>=8.5 else "Rendimiento Muy Bueno" if r>=7.0 else "Rendimiento Correcto" if r>=5.0 else "Rendimiento Mejorable")
    cat_info = [("Técnica","score_technical",m["w_technical"],"#6366f1"),("Decisión","score_decision",m["w_decision"],"#a78bfa"),("Ataque","score_offensive",m["w_offensive"],"#ef4444"),("Defensa","score_defensive",m["w_defensive"],"#10b981")]
    score_cards = ""
    for cat,key,weight,color in cat_info:
        val=m[key]; pct=val*10
        best=val==max(m["score_technical"],m["score_decision"],m["score_offensive"],m["score_defensive"])
        worst=val==min(m["score_technical"],m["score_decision"],m["score_offensive"],m["score_defensive"])
        cls="highlight" if best else ("low" if worst else "")
        score_cards += f'<div class="score-card {cls}"><div class="score-cat">{cat}</div><div class="score-val">{val:.1f}</div><div class="score-weight">Peso {weight*100:.0f}%</div><div class="score-bar"><div class="score-bar-fill" style="width:{pct:.0f}%;background:{color};"></div></div></div>'
    cats_sc = {"Técnica":m["score_technical"],"Decisión":m["score_decision"],"Ataque":m["score_offensive"],"Defensa":m["score_defensive"]}
    best_cat = max(cats_sc,key=cats_sc.get); worst_cat = min(cats_sc,key=cats_sc.get)
    obs_text = observation.strip() if observation and observation.strip() else "Sin observaciones registradas."
    clean_analysis = _re.sub(r'\*\*(.*?)\*\*',r'\1',analysis)
    radar_svg = _radar_svg(m)
    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Informe – {player_name}</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>:root{{--black:#0a0a0a;--dark:#111318;--card:#16191f;--border:#252830;--accent:{pc};--text:#f0f2f5;--muted:#6b7280;--good:#4ade80;--bad:#f87171;}}
*{{margin:0;padding:0;box-sizing:border-box;}}body{{background:#0d0f13;font-family:'DM Sans',sans-serif;color:var(--text);min-height:100vh;display:flex;justify-content:center;padding:40px 20px;}}
.page{{width:794px;background:var(--dark);border-radius:16px;overflow:hidden;box-shadow:0 40px 120px rgba(0,0,0,0.8);border:1px solid var(--border);}}
.header{{background:var(--black);padding:36px 44px 30px;border-bottom:3px solid var(--accent);display:flex;justify-content:space-between;align-items:flex-end;}}
.brand{{font-family:'Bebas Neue',cursive;font-size:13px;letter-spacing:4px;color:var(--accent);margin-bottom:10px;}}
.player-name{{font-family:'Bebas Neue',cursive;font-size:54px;line-height:1;color:var(--text);letter-spacing:2px;}}
.player-meta{{margin-top:10px;display:flex;gap:20px;flex-wrap:wrap;}}
.meta-tag{{font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;gap:6px;}}
.meta-tag span{{color:var(--text);font-weight:500;}}
.header-right{{text-align:right;flex-shrink:0;}}
.rating-label{{font-size:11px;letter-spacing:2px;color:var(--muted);text-transform:uppercase;font-weight:600;}}
.rating-value{{font-family:'Bebas Neue',cursive;font-size:86px;line-height:1;color:var(--accent);}}
.rating-badge{{font-size:12px;font-weight:700;letter-spacing:1px;color:var(--accent);background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.15);border-radius:4px;padding:4px 12px;text-transform:uppercase;display:inline-block;margin-top:4px;}}
.body{{padding:36px 44px;}}.section-title{{font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:16px;display:flex;align-items:center;gap:10px;}}
.section-title::after{{content:'';flex:1;height:1px;background:var(--border);}}
.scores-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:32px;}}
.score-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px 16px;text-align:center;}}
.score-card.highlight{{border-color:var(--accent);}}.score-card.low{{border-color:#f87171;}}
.score-cat{{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:10px;}}
.score-val{{font-family:'Bebas Neue',cursive;font-size:44px;line-height:1;color:var(--text);}}
.score-card.highlight .score-val{{color:var(--accent);}}.score-card.low .score-val{{color:#f87171;}}
.score-weight{{margin-top:8px;font-size:10px;font-weight:600;color:var(--muted);background:rgba(255,255,255,0.04);border-radius:20px;padding:3px 10px;display:inline-block;}}
.score-bar{{margin-top:12px;height:3px;background:var(--border);border-radius:2px;overflow:hidden;}}
.score-bar-fill{{height:100%;border-radius:2px;}}
.mid-section{{display:grid;grid-template-columns:220px 1fr;gap:24px;margin-bottom:32px;}}
.radar-wrap{{background:var(--card);border:1px solid var(--border);border-radius:12px;display:flex;align-items:center;justify-content:center;padding:20px;}}
.insight-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:28px;}}
.insight-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;display:flex;gap:16px;align-items:flex-start;}}
.insight-card.strength{{border-color:rgba(74,222,128,0.3);}}.insight-card.area{{border-color:rgba(248,113,113,0.3);}}
.insight-icon{{font-size:24px;flex-shrink:0;}}
.insight-heading{{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:4px;}}
.insight-val{{font-family:'Bebas Neue',cursive;font-size:22px;color:var(--text);margin-bottom:2px;}}
.analysis-section{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:8px;}}
.analysis-box,.scout-box{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:22px;}}
.analysis-box p{{font-size:13px;line-height:1.7;color:#9ca3af;}}
.scout-box blockquote{{font-size:14px;line-height:1.65;color:#cbd5e1;font-style:italic;border-left:3px solid var(--accent);padding-left:14px;margin-top:8px;}}
.footer{{background:var(--black);border-top:1px solid var(--border);padding:18px 44px;display:flex;justify-content:space-between;align-items:center;}}
.footer-brand{{font-family:'Bebas Neue',cursive;font-size:18px;letter-spacing:3px;color:var(--accent);}}
.footer-info{{font-size:11px;color:var(--muted);text-align:right;line-height:1.6;}}
.metric-item{{padding:10px 12px;border-bottom:1px solid var(--border);}}
.metrics-wrap{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:24px;}}
.metrics-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:0;}}
.metric-label{{font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--muted);margin-bottom:4px;}}
.metric-val{{font-family:'Bebas Neue',cursive;font-size:22px;color:var(--text);}}
.metric-val.good{{color:var(--good);}}.metric-val.bad{{color:var(--bad);}}
</style></head><body><div class="page">
<div class="header"><div class="header-left"><div class="brand">PIP PRO · Informe de Jugador</div>
<div class="player-name">{player_name}</div>
<div class="player-meta">
<div class="meta-tag">Posición <span>{pos_label}</span></div>
<div class="meta-tag">Sesión <span>{sess["name"]}</span></div>
<div class="meta-tag">Tipo <span>{ex_label}</span></div>
<div class="meta-tag">Fecha <span>{date_str}</span></div>
<div class="meta-tag">Acciones <span>{part_str}</span></div>
</div></div>
<div class="header-right"><div class="rating-label">Rating General</div>
<div class="rating-value">{r:.1f}</div><div class="rating-badge">{nivel}</div></div></div>
<div class="body">
<div class="section-title">Categorías evaluadas</div>
<div class="scores-grid">{score_cards}</div>
<div class="mid-section"><div class="radar-wrap">{radar_svg}</div>
<div class="metrics-wrap"><div class="section-title" style="margin-bottom:12px;">Métricas clave</div>
<div class="metrics-grid">
{''.join(f'<div class="metric-item"><div class="metric-label">{lbl}</div><div class="metric-val {"good" if m.get(k,0)>0 else ""}">{"—" if m.get(k,0)==0 else m.get(k,0)}</div></div>' for lbl,k in [("Rating",None),("Todal eventos","total_events"),("Participación %","participation_rate")])}
</div></div></div>
<div class="section-title">Fortalezas y áreas de mejora</div>
<div class="insight-grid">
<div class="insight-card strength"><div class="insight-icon">⚡</div>
<div><div class="insight-heading">Mayor fortaleza</div>
<div class="insight-val">{best_cat} — {cats_sc[best_cat]:.1f}/10</div>
<div style="font-size:12px;color:var(--muted);">Categoría dominante</div></div></div>
<div class="insight-card area"><div class="insight-icon">🎯</div>
<div><div class="insight-heading">Área de mejora</div>
<div class="insight-val">{worst_cat} — {cats_sc[worst_cat]:.1f}/10</div>
<div style="font-size:12px;color:var(--muted);">Prioritaria de trabajo</div></div></div>
</div>
<div class="section-title">Análisis</div>
<div class="analysis-section">
<div class="analysis-box"><div class="section-title" style="font-size:9px;margin-bottom:12px;">Análisis automático</div><p>{clean_analysis}</p></div>
<div class="scout-box"><div class="section-title" style="font-size:9px;margin-bottom:14px;">Observaciones del scout</div><blockquote>{obs_text}</blockquote></div>
</div></div>
<div class="footer"><div class="footer-brand">PIP PRO</div>
<div class="footer-info"><strong>{sess["name"].upper()}</strong> · {ex_label} · {date_str}<br>Informe generado automáticamente · Confidencial</div>
</div></div></body></html>"""
    return html.encode("utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def sbar(label, value, color="#7c3aed", max_val=10.0):
    pct = (value/max_val)*100
    return (f'<div class="sbar-wrap"><div class="sbar-label">{label}</div>'
            f'<div class="sbar-bg"><div class="sbar-fill" style="width:{pct:.0f}%;background:{color};"></div></div>'
            f'<div class="sbar-val" style="color:{color};">{value:.1f}</div></div>')

def ev_count(sid, pid=None):
    if pid: return _cnt("events", {"session_id": sid, "player_id": pid})
    return _cnt("events", {"session_id": sid})

def session_players(sid):
    sp_rows = _q("session_players", {"session_id": sid})
    if not sp_rows: return []
    sp_map = {r["player_id"]: r for r in sp_rows}
    all_p = _q("players", order="name")
    result = []
    for p in all_p:
        if p["id"] in sp_map:
            np = normalise_player(p)
            sd = sp_map[p["id"]]
            np["is_starter"]   = sd.get("is_starter", True)
            np["entry_minute"] = sd.get("entry_minute") or 0
            np["exit_minute"]  = sd.get("exit_minute")
            result.append(np)
    return result

def player_minutes(p, is_partido=True, total_min=90):
    """Minutos jugados según titular/suplente."""
    if not is_partido: return None
    entry = p.get("entry_minute") or 0
    exit_m = p.get("exit_minute")
    if exit_m is not None:
        return max(0, exit_m - entry)
    return max(0, total_min - entry)

# ══════════════════════════════════════════════════════════════════════════════
# STATE
# ══════════════════════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "screen":"splash","nav":"Dashboard",
        "active_session":None,"active_player":None,
        "report_session":None,"report_player":None,
        "new_cat":"Partido","new_ex":EXERCISES[0],
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

init_state()

def go_screen(s): st.session_state.screen = s; st.rerun()
def go_nav(n): st.session_state.nav = n; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# NAVEGACIÓ — SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
NAV_ITEMS = [
    ("⊞","Dashboard"),("☰","Sesiones"),("👤","Jugadores"),
    ("📊","Análisis Técnico"),("📈","Análisis Físico"),
    ("📋","Reportes"),("⇄","Comparaciones"),("📅","Calendario"),("⚙","Configuración"),
]
NAV_BADGES = {
    "Análisis Técnico": '<span style="font-size:9px;background:#f59e0b;color:#000;border-radius:3px;padding:1px 5px;font-weight:700;margin-left:4px;">PIP ONE</span>',
    "Análisis Físico":  '<span style="font-size:9px;background:#7c3aed;color:#fff;border-radius:3px;padding:1px 5px;font-weight:700;margin-left:4px;">PIP PRO</span>',
}

def render_sidebar(sidebar_col):
    with sidebar_col:
        st.markdown('''
        <style>
        /* Elimina espai extra entre botons del sidebar */
        div.nav-btn, div.nav-btn-active {
            margin-bottom: 1px !important;
        }
        div.nav-btn [data-testid="stButton"],
        div.nav-btn-active [data-testid="stButton"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        div.nav-btn [data-testid="stButton"] > button,
        div.nav-btn-active [data-testid="stButton"] > button {
            margin: 0 !important;
        }
        </style>
        ''', unsafe_allow_html=True)
        st.markdown('<div class="nav-sidebar">', unsafe_allow_html=True)
        st.markdown('<div class="pip-logo" style="font-size:19px;margin-bottom:1.2rem;padding-left:.3rem;">'
                    '<span class="pip">PIP</span><span class="pro">PRO</span></div>', unsafe_allow_html=True)
        for icon, label in NAV_ITEMS:
            cls = "nav-btn-active" if st.session_state.nav == label else "nav-btn"
            badge = NAV_BADGES.get(label,"")
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state.nav = label; st.rerun()
            if badge:
                st.markdown(f'<div style="margin-top:-8px;padding:0 4px 3px 36px;">{badge}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Active session indicator
        if st.session_state.active_session:
            s = st.session_state.active_session
            n_ev = ev_count(s["id"])
            st.markdown(f'<div style="margin-top:1rem;background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:8px;padding:8px 10px;">'
                        f'<div style="font-size:9px;color:#34d399;letter-spacing:.1em;font-weight:600;text-transform:uppercase;margin-bottom:3px;">Sesión activa</div>'
                        f'<div style="font-size:12px;color:#d1fae5;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{s["name"]}</div>'
                        f'<div style="font-size:10px;color:#6b7280;margin-top:2px;">{n_ev} eventos</div>'
                        f'</div>', unsafe_allow_html=True)

        # User footer
        _uname = st.session_state.get("logged_user", "Usuario")
        _parts = _uname.split()
        _initials = (_parts[0][0] + _parts[1][0]).upper() if len(_parts) >= 2 else _uname[:2].upper()
        st.markdown(f"""
        <div style="margin-top:2rem;">
            <div class="avatar-chip">
                <div class="avatar">{_initials}</div>
                <div><p style="margin:0;font-size:12px;font-weight:500;color:#d1d5db;">{_uname}</p>
                     <p style="margin:0;font-size:10px;color:#6b7280;">Scout</p></div>
            </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIONS
# ══════════════════════════════════════════════════════════════════════════════

def render_dashboard():
    st.markdown('<div class="page-header"><div class="page-title">Dashboard</div>'
                '<div class="page-sub">Resumen general de actividad</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='padding:0 2rem;'>", unsafe_allow_html=True)

    total_sess = _cnt("sessions")
    open_sess  = _cnt("sessions", {"status": "open"})
    total_pl   = _cnt("players")
    total_ev   = _cnt("events")
    closed_s   = _q("sessions", {"status": "closed"}, columns="id")
    _all_r = _q("player_metrics", columns="rating")
    avg_rating = round(sum(r["rating"] for r in _all_r)/len(_all_r),1) if _all_r else 0.0



    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Sesiones totales", total_sess)
    with c2: st.metric("Sesiones abiertas", open_sess)
    with c3: st.metric("Jugadores registrados", total_pl)
    with c4: st.metric("Eventos totales", total_ev)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    d1, d2 = st.columns([1.6, 1])

    with d1:
        st.markdown('<div class="stitle">Últimas sesiones</div>', unsafe_allow_html=True)
        recent = [normalise_session(s) for s in _q("sessions", order="created_at", desc_order=True, limit=6)]
        if recent:
            rows = ""
            for s in recent:
                badge_cls = "badge-yellow" if s["status"]=="open" else "badge-green"
                badge_lbl = "Abierta" if s["status"]=="open" else "Cerrada"
                n_ev_s = ev_count(s["id"])
                rows += f'<tr><td style="font-weight:500;color:#e5e7eb;">{s["name"]}</td><td>{s["category"]}</td><td>{fmt_dt(s["created_at"])[:10]}</td><td style="text-align:center;">{n_ev_s}</td><td><span class="badge {badge_cls}">{badge_lbl}</span></td></tr>'
            st.markdown(f'<div class="pip-card" style="padding:0;overflow:hidden;"><table class="pip-table"><thead><tr><th>Sesión</th><th>Tipo</th><th>Fecha</th><th style="text-align:center;">Eventos</th><th>Estado</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="pip-card"><div class="empty-state"><div class="empty-icon">📋</div><div class="empty-title">Sin sesiones todavía</div><div class="empty-sub">Crea una sesión para empezar</div></div></div>', unsafe_allow_html=True)

    with d2:
        st.markdown('<div class="stitle">Acciones rápidas</div>', unsafe_allow_html=True)
        st.markdown('<div class="pip-card-accent" style="margin-bottom:10px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px;font-weight:600;color:#a78bfa;margin-bottom:8px;">Nueva sesión</div>', unsafe_allow_html=True)
        if st.button("＋ Crear sesión", key="dash_new_sess"):
            go_nav("Sesiones")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.active_session:
            st.markdown('<div class="pip-card-open">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:13px;font-weight:600;color:#34d399;margin-bottom:8px;">Sesión en curso</div>'
                        f'<div style="font-size:12px;color:#9ca3af;margin-bottom:8px;">{st.session_state.active_session["name"]}</div>', unsafe_allow_html=True)
            if st.button("▶ Continuar captura", key="dash_cont"):
                go_nav("Análisis Técnico")
            st.markdown('</div>', unsafe_allow_html=True)
        if avg_rating > 0:
            st.markdown(f'<div class="pip-card" style="margin-top:10px;text-align:center;">'
                        f'<div style="font-size:10px;color:#6b7280;letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px;">Rating medio global</div>'
                        f'<div style="font-family:\'DM Sans\',sans-serif;font-weight:900;font-size:3rem;color:#a78bfa;line-height:1;">{avg_rating:.1f}</div>'
                        f'<div style="font-size:10px;color:#374151;">sobre 10</div>'
                        f'</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_sesiones():
    st.markdown('<div class="page-header"><div class="page-title">Sesiones</div>'
                '<div class="page-sub">Gestiona y crea sesiones de partido o entrenamiento</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='padding:0 2rem;'>", unsafe_allow_html=True)

    with st.expander("＋  Nueva sesión", expanded=False):
        c1,c2 = st.columns(2)
        with c1:
            if st.button("PARTIDO", use_container_width=True, key="sess_tog_p"):
                st.session_state.new_cat="Partido"; st.rerun()
        with c2:
            if st.button("ENTRENAMIENTO", use_container_width=True, key="sess_tog_e"):
                st.session_state.new_cat="Entrenamiento"; st.rerun()
        cat_sel = st.session_state.new_cat
        st.markdown(f'<div style="font-size:11px;color:#6b7280;padding:4px 0 8px;letter-spacing:.06em;">Modo seleccionado: <strong style="color:#a78bfa;">{cat_sel}</strong></div>', unsafe_allow_html=True)

        if cat_sel == "Entrenamiento":
            st.markdown('<div class="stitle" style="margin-top:4px;">Tipo de ejercicio</div>', unsafe_allow_html=True)
            ex_cols = st.columns(3)
            for i, ex in enumerate(EXERCISES):
                with ex_cols[i%3]:
                    sel = st.session_state.new_ex == ex
                    if st.button(f"{'▶ ' if sel else ''}{ex}", key=f"sess_ex_{ex}", use_container_width=True):
                        st.session_state.new_ex=ex; st.rerun()
            exercise_type = st.session_state.new_ex
        else:
            exercise_type = "Partido"

        sess_name  = st.text_input("Nombre de la sesión *", placeholder="Ej: Partido vs FC León", key="sess_name_inp")
        group_name = st.text_input("Grupo / equipo", placeholder="Ej: Sub-18 Grupo A", key="sess_group_inp")

        if st.button("Crear sesión →", type="primary", use_container_width=True, key="sess_create_btn"):
            if not sess_name.strip():
                st.error("El nombre es obligatorio.")
            else:
                sid = str(uuid.uuid4())[:12]
                _ins("sessions", {"id": sid, "name": sess_name.strip(), "group_name": group_name.strip(), "category": cat_sel, "exercise_type": exercise_type, "status": "open", "created_at": datetime.now().isoformat(), "closed_at": None})


                new_s = normalise_session(_one("sessions", {"id": sid}))
                st.session_state.active_session = new_s; st.session_state.active_player = None
                go_nav("Análisis Técnico")

    st.divider()
    all_sessions = [normalise_session(s) for s in _q("sessions", order="created_at", desc_order=True)]
    if not all_sessions:
        st.markdown('<div class="pip-card"><div class="empty-state"><div class="empty-icon">☰</div><div class="empty-title">Sin sesiones</div><div class="empty-sub">Crea tu primera sesión arriba</div></div></div>', unsafe_allow_html=True)
    else:
        open_s   = [s for s in all_sessions if s["status"]=="open"]
        closed_s = [s for s in all_sessions if s["status"]=="closed"]
        if open_s:
            st.markdown('<div class="stitle">Sesiones abiertas</div>', unsafe_allow_html=True)
            for s in open_s:
                n_ev = ev_count(s["id"]); n_pl = len(session_players(s["id"]))
                is_active = st.session_state.active_session and st.session_state.active_session["id"]==s["id"]
                card_cls = "pip-card-open" if is_active else "pip-card-sm"
                sc1,sc2,sc3 = st.columns([3,1,1])
                with sc1:
                    st.markdown(f'<div class="{card_cls}">'
                                f'<div style="font-weight:600;color:#e5e7eb;font-size:14px;">{s["name"]}</div>'
                                f'<div style="font-size:11px;color:#6b7280;margin-top:3px;">'
                                f'<span class="badge badge-yellow">Abierta</span>&nbsp;'
                                f'<span style="margin-left:4px;">{s["category"]} · {n_pl} jugadores · {n_ev} eventos · {fmt_dt(s["created_at"])[:10]}</span>'
                                f'</div></div>', unsafe_allow_html=True)
                with sc2:
                    if st.button("▶ Abrir", key=f"open_{s['id']}", use_container_width=True):
                        st.session_state.active_session = s; st.session_state.active_player = None
                        go_nav("Análisis Técnico")
                with sc3:
                    if n_ev > 0:
                        if st.button("⏹ Cerrar", key=f"close_{s['id']}", use_container_width=True):
                            close_and_compute(s["id"], s.get("exercise_type","Partido"))
                            closed = normalise_session(_one("sessions", {"id": s["id"]}))
                            pls2 = session_players(s["id"])
                            st.session_state.report_session = closed
                            st.session_state.report_player = pls2[0] if pls2 else None
                            st.session_state.active_session = None
                            go_nav("Reportes")

        if closed_s:
            st.divider()
            st.markdown('<div class="stitle">Sesiones cerradas</div>', unsafe_allow_html=True)
            rows = ""
            for s in closed_s[:12]:
                n_pl = len(session_players(s["id"])); n_ev = ev_count(s["id"])
                rows += f'<tr><td style="font-weight:500;color:#e5e7eb;">{s["name"]}</td><td>{s["category"]}</td><td>{fmt_dt(s["created_at"])[:10]}</td><td style="text-align:center;">{n_pl}</td><td style="text-align:center;">{n_ev}</td><td><span class="badge badge-green">Cerrada</span></td></tr>'
            st.markdown(f'<div class="pip-card" style="padding:0;overflow:hidden;"><table class="pip-table"><thead><tr><th>Sesión</th><th>Tipo</th><th>Fecha</th><th style="text-align:center;">Jugadores</th><th style="text-align:center;">Eventos</th><th>Estado</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:11px;color:#374151;margin-top:.5rem;padding-left:4px;">Selecciona una sesión desde Reportes para ver los datos.</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_jugadores():
    st.markdown('<div class="page-header"><div class="page-title">Jugadores</div>'
                '<div class="page-sub">Plantilla registrada en el sistema</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='padding:0 2rem;'>", unsafe_allow_html=True)

    with st.expander("＋  Añadir jugador"):
        p1,p2 = st.columns([2,1])
        with p1: new_pname = st.text_input("Nombre *", key="jug_name", placeholder="Nombre del jugador")
        with p2: new_ppos = st.selectbox("Posición", POSITIONS, format_func=lambda p: f"{p} · {POS_NAMES[p]}", key="jug_pos")
        if st.button("Añadir jugador →", use_container_width=True, key="jug_add"):
            name = new_pname.strip()
            if name:
                existing = _one("players", {"name": name})

                if existing: pid=existing["id"]; _upd("players",{"position":new_ppos},{"id":pid}); st.success("Posición actualizada.")

                else:
                    pid = str(uuid.uuid4())[:12]
                    _ins("players", {"id": pid, "name": name, "position": new_ppos, "created_at": datetime.now().isoformat()})
                    st.success(f"Jugador {name} añadido.")
                st.rerun()

    players = [normalise_player(p) for p in _q("players", order="name")]
    if not players:
        st.markdown('<div class="pip-card" style="margin-top:1rem;"><div class="empty-state"><div class="empty-icon">👤</div><div class="empty-title">Sin jugadores registrados</div><div class="empty-sub">Añade jugadores desde el panel superior o al crear una sesión</div></div></div>', unsafe_allow_html=True)
    else:
        rows = ""
        for p in players:
            pc = pos_color(p["position"]); n_sess = _cnt("session_players", {"player_id": p["id"]})
            last_m = _one("player_metrics", {"player_id": p["id"]}, order="calculated_at", desc_order=True)
            rating_str = f'{last_m["rating"]:.1f}' if last_m else "—"
            rows += f'<tr><td style="font-weight:500;color:#e5e7eb;">{p["name"]}</td><td><span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;background:{pc}22;color:{pc};border:1px solid {pc}44;">{p["position"]}</span></td><td>{POS_NAMES[p["position"]]}</td><td style="text-align:center;">{n_sess}</td><td style="text-align:center;font-weight:700;color:#a78bfa;">{rating_str}</td></tr>'
        st.markdown(f'<div class="pip-card" style="padding:0;overflow:hidden;margin-top:1rem;"><table class="pip-table"><thead><tr><th>Jugador</th><th>Pos.</th><th>Posición</th><th style="text-align:center;">Sesiones</th><th style="text-align:center;">Último rating</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_analisis_tecnico():
    st.markdown('<div class="page-header"><div class="page-title">Análisis Técnico</div>'
                '<div class="page-sub">Captura de eventos en tiempo real — <span style="color:#f59e0b;font-size:11px;font-weight:700;">PIP ONE</span></div></div>', unsafe_allow_html=True)
    st.markdown("<div style='padding:0 2rem;'>", unsafe_allow_html=True)

    sess_obj = st.session_state.active_session
    if not sess_obj:
        st.markdown('<div class="pip-card" style="margin-top:1rem;"><div class="empty-state"><div class="empty-icon">📊</div><div class="empty-title">Sin sesión activa</div><div class="empty-sub">Ve a Sesiones para abrir o crear una sesión</div></div></div>', unsafe_allow_html=True)
        if st.button("Ir a Sesiones →", key="at_go_sess"): go_nav("Sesiones")
        st.markdown("</div>", unsafe_allow_html=True); return

    sess = normalise_session(_one("sessions", {"id": sess_obj["id"]}))
    if not sess: st.error("Sesión no encontrada."); st.markdown("</div>",unsafe_allow_html=True); return
    st.session_state.active_session = sess

    if sess["status"] == "closed":
        st.warning("Esta sesión ya está cerrada.")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Ver reporte", key="at_ver_rep"):
                pls2 = session_players(sess["id"])
                st.session_state.report_session = sess
                st.session_state.report_player = pls2[0] if pls2 else None
                go_nav("Reportes")
        with col_btn2:
            if st.button("Nueva sesión", key="at_new"):
                st.session_state.active_session = None; go_nav("Sesiones")
        st.markdown("</div>",unsafe_allow_html=True); return

    ex_key = sess.get("exercise_type") or "Partido"
    ec = EX_COLOR.get(ex_key,"#7c3aed")
    cat_color = "#7c3aed" if sess["category"]=="Partido" else "#3b82f6"

    # Session header
    st.markdown(
        f'<div class="pip-card-sm" style="margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
        f'<div><div style="font-weight:700;font-size:15px;color:#f3f4f6;">{sess["name"]}</div>'
        f'<div style="margin-top:4px;display:flex;gap:5px;flex-wrap:wrap;align-items:center;">'
        f'<span class="badge" style="background:{cat_color}22;color:{cat_color};border:1px solid {cat_color}44;">{sess["category"]}</span>'
        f'{"<span class=\"badge\" style=\"background:"+ec+"22;color:"+ec+";border:1px solid "+ec+"44;\">"+ex_key+"</span>" if sess["category"]=="Entrenamiento" else ""}'
        f'<span class="badge badge-green">ABIERTA</span>'
        f'</div></div>'
        f'<div style="font-size:1.6rem;font-weight:900;color:#374151;">{ev_count(sess["id"])} <span style="font-size:0.65rem;color:#1f2937;letter-spacing:2px;">EVENTOS</span></div>'
        f'</div>', unsafe_allow_html=True)

    col_pl, col_cap, col_dash = st.columns([1, 1.2, 1.4], gap="medium")

    # ── JUGADORS ──
    with col_pl:
        st.markdown('<div class="stitle">Jugadores</div>', unsafe_allow_html=True)
        with st.expander("Añadir jugador"):
            new_pname = st.text_input("Nombre", key="at_pname", label_visibility="collapsed", placeholder="Nombre del jugador")
            new_ppos  = st.radio("Pos", POSITIONS, format_func=lambda p: f"{p}", horizontal=True, key="at_ppos", label_visibility="collapsed")
            _rol = st.radio("Rol", ["Titular","Suplente"], horizontal=True, key="at_rol")
            _entry_min = 0
            if _rol == "Suplente":
                _auto_min = st.session_state.get("current_match_min", 46)
            _entry_min = st.number_input("Minuto de entrada", min_value=0, max_value=120, value=int(_auto_min), step=1, key="at_entry_min")
            if st.button("Añadir a sesión", use_container_width=True, key="at_addp"):
                name = new_pname.strip()
                if name:
                    existing = _one("players", {"name": name})
                    if existing: pid = existing["id"]; _upd("players", {"position": new_ppos}, {"id": pid})
                    else: pid = str(uuid.uuid4())[:12]; _ins("players", {"id": pid, "name": name, "position": new_ppos, "created_at": datetime.now().isoformat()})
                    if not _one("session_players", {"session_id": sess["id"], "player_id": pid}):
                        _ins("session_players", {"session_id": sess["id"], "player_id": pid, "is_starter": (_rol=="Titular"), "entry_minute": int(_entry_min), "exit_minute": None})
                    pls = session_players(sess["id"])
                    if not st.session_state.active_player: st.session_state.active_player = pls[0]
                    st.rerun()
        pls = session_players(sess["id"])
        if not pls:
            st.markdown('<div style="color:#1f2937;font-size:.82rem;padding:10px;">Añade jugadores para empezar.</div>', unsafe_allow_html=True)
        else:
            for p in pls:
                ia = st.session_state.active_player and st.session_state.active_player["id"]==p["id"]
                ne = ev_count(sess["id"], p["id"])
                is_sub = not p.get("is_starter", True)
                entry_m = p.get("entry_minute") or 0
                exit_m  = p.get("exit_minute")
                rol_tag = f"[S {entry_m}']" if is_sub else (f"[T→{exit_m}']" if exit_m else "[T]")
                subbed_out = exit_m is not None
                label = f"{'▶ ' if ia else ''}{'⏹ ' if subbed_out else ''}{p['name']} [{p['position']}] {rol_tag} ({ne} ev)"
                if st.button(label, key=f"at_selp_{p['id']}", use_container_width=True, disabled=subbed_out):
                    st.session_state.active_player = p; st.rerun()
            # Sustituir jugador activo
            ap_act = st.session_state.active_player
            if ap_act:
                # Refresh from DB to get current exit_minute
                _sp_fresh = [x for x in session_players(sess["id"]) if x["id"]==ap_act["id"]]
                if _sp_fresh and _sp_fresh[0].get("exit_minute") is None:
                    with st.expander("🔄 Sustituir jugador activo"):
                        st.markdown(f'<div style="font-size:11px;color:#9ca3af;margin-bottom:6px;">Jugador: <strong>{ap_act["name"]}</strong></div>', unsafe_allow_html=True)
                        _auto_sub = st.session_state.get("current_match_min", 46)
                        _sub_min = st.number_input("Minuto de sustitución", min_value=1, max_value=120, value=max(1,int(_auto_sub)), step=1, key="sub_min_input")
                        if st.button("Confirmar sustitución", use_container_width=True, key="sub_confirm", type="primary"):
                            _upd("session_players", {"exit_minute": int(_sub_min)}, {"session_id": sess["id"], "player_id": ap_act["id"]})
                            st.session_state.active_player = None; st.rerun()

        
        st.divider()
        st.markdown('<div class="stitle">Últimos eventos</div>', unsafe_allow_html=True)
        all_evs = _q("events", {"session_id": sess["id"]}, order="created_at", desc_order=True, limit=10)
        p_map = {p["id"]:p for p in pls}
        if all_evs:
            for e in all_evs:
                ei = ALL_EVENTS.get(e["event_type"],{"label":e["event_type"],"color":"#6b7280"})
                pn = p_map.get(e["player_id"],{}).get("name","?")
                pp = p_map.get(e["player_id"],{}).get("position","")
                pc_ = pos_color(pp); ts = e.get("ts","") or ""
                st.markdown(f'<div class="elog"><div style="width:5px;height:5px;border-radius:50%;background:{ei["color"]};flex-shrink:0;"></div>'
                            f'<div style="color:#374151;font-size:.65rem;width:34px;">{ts}</div>'
                            f'<div style="color:{pc_};font-size:.75rem;width:22px;">{pp}</div>'
                            f'<div style="color:#9ca3af;flex:1;font-size:.77rem;">{pn}</div>'
                            f'<div style="color:{ei["color"]};font-size:.72rem;">{ei["label"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#1f2937;font-size:.78rem;padding:6px;">Sin eventos.</div>', unsafe_allow_html=True)

        ap = st.session_state.active_player
        if ap and all_evs:
            if st.button("↩ Deshacer último", use_container_width=True, key="at_undo"):
                r = _one("events", {"session_id": sess["id"], "player_id": ap["id"]}, order="created_at", desc_order=True)
                if r: _del("events", {"id": r["id"]})
                st.rerun()
        # ── Corregir evento ───────────────────────────────────
        if all_evs:
            with st.expander("✏️ Corregir un evento"):
                _pls_edit = session_players(sess["id"])
                _pmap_edit = {p["id"]: p for p in _pls_edit}
                ev_labels = [f"{e.get('ts','--')} · {_pmap_edit.get(e['player_id'],{}).get('name','?')} · {ALL_EVENTS.get(e['event_type'],{}).get('label',e['event_type'])}" for e in all_evs]
                sel_idx_edit = st.selectbox("Evento a corregir", range(len(ev_labels)), format_func=lambda i: ev_labels[i], key="edit_ev_sel")
                sel_ev = all_evs[sel_idx_edit]
                _ev_pos = _pmap_edit.get(sel_ev["player_id"], {}).get("position", "MED")
                ev_dict_edit = GK_EVENTS if _ev_pos=="GK" else FIELD_EVENTS
                _cur_idx = list(ev_dict_edit.keys()).index(sel_ev["event_type"]) if sel_ev["event_type"] in ev_dict_edit else 0
                new_ev_type = st.selectbox("Cambiarlo a", list(ev_dict_edit.keys()), index=_cur_idx, format_func=lambda k: ev_dict_edit[k]["label"], key="edit_ev_new")
                if st.button("✓ Aplicar corrección", use_container_width=True, key="edit_ev_save", type="primary"):
                    _upd("events", {"event_type": new_ev_type, "event_cat": ev_dict_edit[new_ev_type]["cat"]}, {"id": sel_ev["id"]})
                    st.success(f"✓ Corregido: {ev_dict_edit[new_ev_type]['label']}")
                    st.rerun()

        st.divider()
        st.markdown('<div class="stitle" style="color:#ef4444;">Cerrar sesión</div>', unsafe_allow_html=True)
        n_total = ev_count(sess["id"])
        st.markdown(f'<div style="font-size:.78rem;color:#374151;margin-bottom:8px;">{n_total} eventos · {len(pls)} jugadores</div>', unsafe_allow_html=True)
        if st.button("CERRAR Y CALCULAR MÉTRICAS", type="primary", use_container_width=True, key="at_close"):
            if n_total == 0: st.error("Sin eventos registrados.")
            else:
                close_and_compute(sess["id"], ex_key)
                closed = normalise_session(_one("sessions", {"id": sess["id"]}))
                pls2 = session_players(sess["id"])
                st.session_state.report_session = closed
                st.session_state.report_player = pls2[0] if pls2 else None
                st.session_state.active_session = None
                go_nav("Reportes")

    # ── EVENT CAPTURE ──
    with col_cap:
        # Match clock
        _phase_k = f"mph_{sess['id']}"; _start_k = f"mst_{sess['id']}"; _halft_k = f"mht_{sess['id']}"
        if _phase_k not in st.session_state: st.session_state[_phase_k] = "not_started"
        _phase = st.session_state[_phase_k]; _now = _match_time.time()

        if _phase == "first_half":
            _curr_min = min(int((_now - st.session_state.get(_start_k,_now))/60), 45); match_ts = f"{_curr_min}'"
        elif _phase == "second_half":
            _curr_min = 45 + int((_now - st.session_state.get(_halft_k,_now))/60); match_ts = f"{_curr_min}'"
        elif _phase == "finished":
            _curr_min = 90; match_ts = "90'"
        else:
            _curr_min = 0; match_ts = "--'"
        # Expose current match minute globally for other widgets
        st.session_state["current_match_min"] = _curr_min

        if sess["category"] == "Partido":
            _phase_meta = {
                "not_started":("⚫","SIN INICIAR","#374151","rgba(255,255,255,0.04)"),
                "first_half":("🟢","1ª PARTE","#10b981","rgba(16,185,129,0.08)"),
                "half_time":("🟡","DESCANSO","#f59e0b","rgba(245,158,11,0.08)"),
                "second_half":("🟢","2ª PARTE","#10b981","rgba(16,185,129,0.08)"),
                "finished":("🔴","FINALIZADO","#ef4444","rgba(239,68,68,0.08)"),
            }
            _icon,_plabel,_pcolor,_pbg = _phase_meta.get(_phase,("⚫","—","#374151","rgba(255,255,255,0.04)"))
            st.markdown(f'<div style="background:{_pbg};border:1px solid {_pcolor}44;border-radius:8px;padding:10px 14px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">'
                        f'<span style="font-size:.7rem;font-weight:700;letter-spacing:.1em;color:{_pcolor};">{_icon} {_plabel}</span>'
                        f'<span style="font-family:\'DM Sans\',sans-serif;font-weight:900;font-size:2rem;color:{_pcolor};line-height:1;">{match_ts}</span>'
                        f'</div>', unsafe_allow_html=True)
            _bp1, _bp2 = st.columns(2)
            if _phase == "not_started":
                with _bp1:
                    if st.button("▶ INICIO PARTIDO", use_container_width=True, type="primary", key=f"mph_s_{sess['id']}"):
                        st.session_state[_phase_k]="first_half"; st.session_state[_start_k]=_match_time.time(); st.rerun()
            elif _phase == "first_half":
                with _bp1:
                    if st.button("⏸ FIN 1ª PARTE", use_container_width=True, key=f"mph_h_{sess['id']}"):
                        st.session_state[_phase_k]="half_time"; st.rerun()
            elif _phase == "half_time":
                with _bp1:
                    if st.button("▶ INICIO 2ª PARTE", use_container_width=True, type="primary", key=f"mph_2_{sess['id']}"):
                        st.session_state[_phase_k]="second_half"; st.session_state[_halft_k]=_match_time.time(); st.rerun()
            elif _phase == "second_half":
                with _bp1:
                    if st.button("⏹ FIN 2ª PARTE", use_container_width=True, key=f"mph_e_{sess['id']}"):
                        st.session_state[_phase_k]="finished"; st.rerun()
            if _phase in ("not_started","half_time","finished"):
                st.markdown(f'<div style="font-size:.72rem;color:#374151;text-align:center;padding:2px 0 6px;letter-spacing:.05em;">{"Inicia el partido para capturar" if _phase=="not_started" else ("Descanso · Inicia 2ª parte" if _phase=="half_time" else "Partido finalizado")}</div>', unsafe_allow_html=True)
            st.divider()
        else:
            match_ts = datetime.now().strftime("%H:%M:%S")

        ap = st.session_state.active_player
        if not ap:
            st.markdown('<div style="color:#1f2937;padding:40px;text-align:center;font-size:1rem;">Selecciona un jugador</div>', unsafe_allow_html=True)
        else:
            is_gk = ap["position"] == "GK"; pc = pos_color(ap["position"]); ne_ap = ev_count(sess["id"], ap["id"])
            st.markdown(f'<div class="pip-card-accent" style="text-align:center;margin-bottom:12px;padding:10px;">'
                        f'<div style="font-size:.58rem;color:#6b7280;letter-spacing:.12em;text-transform:uppercase;">JUGADOR ACTIVO</div>'
                        f'<div style="font-weight:900;font-size:1.6rem;color:#f3f4f6;margin-top:2px;">{ap["name"]}</div>'
                        f'<div style="margin-top:4px;">{pos_badge_html(ap["position"])}'
                        f'<span style="font-size:.68rem;color:#374151;margin-left:8px;">{ne_ap} eventos</span></div></div>', unsafe_allow_html=True)

            if is_gk:
                st.markdown('<div class="stitle" style="color:#f59e0b;">Panel portero</div>', unsafe_allow_html=True)
                layout = GK_LAYOUT; ev_dict = GK_EVENTS
            else:
                st.markdown('<div class="stitle">Panel de acciones</div>', unsafe_allow_html=True)
                layout = FIELD_LAYOUT; ev_dict = FIELD_EVENTS

            kb = ev_count(sess["id"])
            _blocked = (sess["category"]=="Partido" and st.session_state.get(_phase_k,"not_started") in ("not_started","half_time","finished"))
            for ev_a, ev_b in layout:
                c1, c2 = st.columns(2)
                with c1:
                    ea = ev_dict[ev_a]
                    if st.button(ea["label"], key=f"ea_{ev_a}_{kb}", use_container_width=True, disabled=_blocked):
                        _ins("events", {"id": str(uuid.uuid4())[:16], "session_id": sess["id"], "player_id": ap["id"], "event_type": ev_a, "event_cat": ea["cat"], "ts": match_ts, "created_at": datetime.now().isoformat()})
                with c2:
                    if ev_b:
                        eb = ev_dict[ev_b]
                        if st.button(eb["label"], key=f"eb_{ev_b}_{kb}", use_container_width=True, disabled=_blocked):
                            _ins("events", {"id": str(uuid.uuid4())[:16], "session_id": sess["id"], "player_id": ap["id"], "event_type": ev_b, "event_cat": eb["cat"], "ts": match_ts, "created_at": datetime.now().isoformat()})

            evs_ap = _q("events", {"session_id": sess["id"], "player_id": ap["id"]})
            if evs_ap:
                st.divider()
                cat_c = {}
                for e in evs_ap: cat_c[e["event_cat"]] = cat_c.get(e["event_cat"],0)+1
                mc = st.columns(4)
                for col_,(cat,lbl) in zip(mc,[("technical","Téc"),("decision","Dec"),("offensive","Ata"),("defensive","Def")]):
                    with col_: st.metric(lbl, cat_c.get(cat,0))

    # ── LIVE DASHBOARD ──
    with col_dash:
        ap = st.session_state.active_player
        st.markdown('<div class="stitle">Métricas en vivo</div>', unsafe_allow_html=True)
        if ap:
            evs_ap = _q("events", {"session_id": sess["id"], "player_id": ap["id"]})
            m = compute_metrics(evs_ap, ap["position"], ex_key)
            if m:
                pc = pos_color(ap["position"])
                st.markdown(f'<div style="display:flex;align-items:flex-end;gap:12px;margin-bottom:10px;">'
                            f'<div><div style="font-family:\'DM Sans\',sans-serif;font-weight:900;font-size:4.5rem;color:{pc};line-height:1;">{m["rating"]}</div>'
                            f'<div style="font-size:.58rem;color:#374151;letter-spacing:.15em;">RATING LIVE</div></div>'
                            f'<div style="flex:1;padding-bottom:4px;">'
                            f'<div style="font-size:.68rem;color:#1f2937;margin-bottom:5px;">{m["total_events"]} eventos · {m["participation_rate"]:.0f}% part.</div>'
                            f'{"".join(sbar(CAT_LABELS[k],m[f"score_{k}"],{"technical":"#3b82f6","decision":"#8b5cf6","offensive":"#ef4444","defensive":"#10b981"}[k]) for k in ["technical","decision","offensive","defensive"])}'
                            f'</div></div>', unsafe_allow_html=True)
                st.image(radar_img(m, ap["name"]), use_container_width=True)
                if ap["position"]=="GK":
                    mc1,mc2 = st.columns(2)
                    with mc1: st.metric("Paradas",m["total_saves"]); st.metric("Efectividad %",f'{m["save_rate"]:.0f}%')
                    with mc2: st.metric("Salidas %",f'{m["exit_rate"]:.0f}%'); st.metric("Pase corto %",f'{m["short_pass_acc"]:.0f}%')
                else:
                    mc1,mc2 = st.columns(2)
                    with mc1: st.metric("Pase %",f'{m["pass_accuracy"]:.0f}%'); st.metric("Decisión %",f'{m["decision_score"]:.0f}%'); st.metric("Acciones of.",m["offensive_actions"])
                    with mc2: st.metric("Control %",f'{m["control_accuracy"]:.0f}%'); st.metric("Defensa",m["defensive_actions"]); st.metric("Goles",m["goals"])
            else:
                st.markdown('<div style="color:#1f2937;padding:20px;text-align:center;font-size:.85rem;">Captura eventos para ver métricas.</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_reportes():
    st.markdown('<div class="page-header"><div class="page-title">Reportes</div>'
                '<div class="page-sub">Análisis de rendimiento por sesión y jugador</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='padding:0 2rem;'>", unsafe_allow_html=True)

    closed_sess = [normalise_session(s) for s in _q("sessions", {"status": "closed"}, order="closed_at", desc_order=True)]
    if not closed_sess:
        st.markdown('<div class="pip-card" style="margin-top:1rem;"><div class="empty-state"><div class="empty-icon">📋</div><div class="empty-title">Sin reportes disponibles</div><div class="empty-sub">Los reportes se generan al cerrar una sesión con eventos registrados</div></div></div>', unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True); return

    # Session selector
    sess_names = [s["name"] for s in closed_sess]
    cur_sess = st.session_state.report_session
    cur_idx = next((i for i,s in enumerate(closed_sess) if cur_sess and s["id"]==cur_sess["id"]), 0)
    sel_name = st.selectbox("Sesión", sess_names, index=cur_idx, key="rep_sess_sel")
    rsess = next(s for s in closed_sess if s["name"]==sel_name)
    st.session_state.report_session = rsess

    pls = session_players(rsess["id"])
    if not pls: st.warning("Sin jugadores en esta sesión."); st.markdown("</div>",unsafe_allow_html=True); return

    rp = st.session_state.report_player
    pl_names = [p["name"] for p in pls]
    cur_pl_idx = next((i for i,p in enumerate(pls) if rp and p["id"]==rp["id"]), 0)
    sel_pl = st.selectbox("Jugador", pl_names, index=cur_pl_idx, key="rep_pl_sel", label_visibility="collapsed")
    rp = next(p for p in pls if p["name"]==sel_pl); st.session_state.report_player = rp

    ex_key = rsess.get("exercise_type") or "Partido"
    m = _one("player_metrics", {"session_id": rsess["id"], "player_id": rp["id"]})
    if not m:
        st.warning("Sin métricas calculadas para este jugador."); st.markdown("</div>",unsafe_allow_html=True); return
    m = dict(m); atxt = analysis_text(rp["name"], m, ex_key); pc = pos_color(rp["position"])

    # Player card header
    st.markdown(f'<div class="pip-card-sm" style="margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;">'
                f'<div><div style="font-weight:700;font-size:18px;color:#f3f4f6;">{rp["name"]}</div>'
                f'<div style="margin-top:4px;">{pos_badge_html(rp["position"])}'
                f'<span style="font-size:.78rem;color:#6b7280;margin-left:8px;">{rsess["name"]} · {fmt_dt(rses.get("closed_at",""))[:10]}</span></div></div>'
                f'<div style="text-align:right;"><div style="font-size:.6rem;color:#6b7280;letter-spacing:.1em;text-transform:uppercase;">Rating</div>'
                f'<div style="font-family:\'DM Sans\',sans-serif;font-weight:900;font-size:3rem;color:{pc};line-height:1;">{m["rating"]}</div></div>'
                f'</div>', unsafe_allow_html=True)

    rc1, rc2 = st.columns([1.6, 1])
    with rc1:
        # Score bars
        st.markdown('<div class="stitle">Categorías</div>', unsafe_allow_html=True)
        cats_info = [("Técnica","score_technical","#3b82f6"),("Decisión","score_decision","#8b5cf6"),("Ataque","score_offensive","#ef4444"),("Defensa","score_defensive","#10b981")]
        for lbl,key,col in cats_info:
            st.markdown(sbar(lbl, m[key], col), unsafe_allow_html=True)

        st.divider()
        # Métriques clau
        st.markdown('<div class="stitle">Métricas clave</div>', unsafe_allow_html=True)
        if m["position"]=="GK":
            mg1,mg2 = st.columns(2)
            with mg1:
                st.metric("Paradas",m.get("total_saves",0)); st.metric("P. difíciles",m.get("great_saves",0))
                st.metric("Efectividad %",f'{m.get("save_rate",0):.0f}%')
            with mg2:
                st.metric("Salidas %",f'{m.get("exit_rate",0):.0f}%')
                st.metric("Pase corto %",f'{m.get("short_pass_acc",0):.0f}%')
                st.metric("Pase largo %",f'{m.get("long_pass_acc",0):.0f}%')
        else:
            mg1,mg2,mg3 = st.columns(3)
            with mg1: st.metric("Pase %",f'{m["pass_accuracy"]:.0f}%'); st.metric("Control %",f'{m["control_accuracy"]:.0f}%'); st.metric("Decisión %",f'{m["decision_score"]:.0f}%')
            with mg2: st.metric("Tiros puerta",m["shots_on_target"]); st.metric("Goles",m["goals"]); st.metric("Asistencias",m.get("assists",0))
            with mg3: st.metric("Recuperaciones",m["recoveries"]); st.metric("Intercepciones",m["interceptions"]); st.metric("Errores",m["errors"])

        st.divider()
        st.markdown('<div class="stitle">Análisis automático</div>', unsafe_allow_html=True)
        formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#a78bfa;">\1</strong>', atxt)
        st.markdown(f'<div class="analysis-block">{formatted}</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="stitle">Observaciones del scout</div>', unsafe_allow_html=True)
        obs_row = _one("scout_observations", {"session_id": rsess["id"], "player_id": rp["id"]})
        obs_current = obs_row["observation"] if obs_row else ""
        obs_input = st.text_area("", value=obs_current, height=100, placeholder="Observaciones, contexto, áreas de trabajo...", label_visibility="collapsed", key=f"obs_{rsess['id']}_{rp['id']}")
        if st.button("Guardar observaciones", use_container_width=True, key="rep_save_obs"):
            if obs_row: _upd("scout_observations",{"observation":obs_input,"updated_at":datetime.now().isoformat()},{"session_id":rsess["id"],"player_id":rp["id"]})
            else: _ins("scout_observations", {"id": str(uuid.uuid4())[:12], "session_id": rsess["id"], "player_id": rp["id"], "observation": obs_input, "updated_at": datetime.now().isoformat()})


            st.success("Guardado ✓")

    with rc2:
        st.markdown('<div class="stitle">Perfil de rendimiento</div>', unsafe_allow_html=True)
        st.image(radar_img(m, rp["name"]), use_container_width=True)
        st.image(bar_img(m), use_container_width=True)

        # Ranking sessió
        if len(pls) > 1:
            st.divider()
            st.markdown('<div class="stitle">Ranking sesión</div>', unsafe_allow_html=True)
            medals = {1:"🥇",2:"🥈",3:"🥉"}
            ratings = []
            for p in pls:
                pm = _one("player_metrics", {"session_id": rsess["id"], "player_id": p["id"]})
                if pm: ratings.append((p["name"],pm["rating"],pm["position"]))
            ratings.sort(key=lambda x:x[1], reverse=True)
            for i,(pname,prat,ppos) in enumerate(ratings,1):
                is_sel = pname==rp["name"]; ppc = pos_color(ppos)
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;background:{"rgba(124,58,237,0.1)" if is_sel else "rgba(255,255,255,0.02)"};border:{"1px solid rgba(124,58,237,0.3)" if is_sel else "1px solid rgba(255,255,255,0.06)"};border-radius:6px;padding:6px 10px;margin-bottom:3px;">'
                            f'<div style="display:flex;align-items:center;gap:6px;"><span>{medals.get(i,"")}</span>'
                            f'<span style="font-size:.82rem;color:{"#e5e7eb" if is_sel else "#9ca3af"};">{pname}</span>'
                            f'<span style="font-size:.65rem;color:{ppc};">[{ppos}]</span></div>'
                            f'<span style="font-weight:700;color:{ppc};font-size:1.05rem;">{prat}</span></div>', unsafe_allow_html=True)

        st.divider()
        obs_saved = _one("scout_observations", {"session_id": rsess["id"], "player_id": rp["id"]})
        obs_text_dl = obs_saved["observation"] if obs_saved else ""
        try:
            html_bytes = make_report_html(rp["name"], rsess, m, atxt, obs_text_dl)
            st.download_button("DESCARGAR INFORME HTML", data=html_bytes,
                file_name=f"pip_pro_{rp['name'].replace(' ','_')}_{rsess['id']}.html",
                mime="text/html", use_container_width=True, type="primary", key="rep_dl")
        except Exception as e:
            st.error(f"Error generando informe: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


def render_comparaciones():
    st.markdown('<div class="page-header"><div class="page-title">Comparaciones</div>'
                '<div class="page-sub">Comparativa de rendimiento entre jugadores</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='padding:0 2rem;'>", unsafe_allow_html=True)

    # Obtenir totes les sessions tancades amb mètriques
    closed_sess = [normalise_session(s) for s in _q("sessions", {"status": "closed"}, order="closed_at", desc_order=True)]
    all_players  = [normalise_player(p) for p in _q("players", order="name")]

    if not closed_sess or not all_players:
        st.markdown('<div class="pip-card" style="margin-top:1rem;"><div class="empty-state">'
                    '<div class="empty-icon">⇄</div>'
                    '<div class="empty-title">Sin datos para comparar</div>'
                    '<div class="empty-sub">Necesitas al menos una sesión cerrada con eventos registrados.</div>'
                    '</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True); return

    # Selectors
    sel_col1, sel_col2 = st.columns(2)
    with sel_col1:
        sess_options = ["Todas las sesiones"] + [s["name"] for s in closed_sess]
        sel_sess = st.selectbox("Sesión", sess_options, key="comp_sess")
    with sel_col2:
        player_names = [p["name"] for p in all_players]
        sel_players  = st.multiselect("Jugadores a comparar (máx 4)", player_names, default=player_names[:min(2,len(player_names))], key="comp_players")

    if not sel_players:
        st.info("Selecciona al menos un jugador."); st.markdown("</div>",unsafe_allow_html=True); return

    # Recollir mètriques per cada jugador seleccionat
    comp_data = []
    for pname in sel_players[:4]:
        p = next((x for x in all_players if x["name"]==pname), None)
        if not p: continue
        if sel_sess == "Todas las sesiones": metrics_rows = _q("player_metrics", {"player_id": p["id"]}, order="calculated_at", desc_order=True)
        else:
            sess_obj = next((s for s in closed_sess if s["name"]==sel_sess), None)
            metrics_rows = _q("player_metrics", {"player_id": p["id"], "session_id": sess_obj["id"]}) if sess_obj else []





        if not metrics_rows: continue
        # Calcular promig si hi ha múltiples sessions
        def avg_field(field):
            vals = [r[field] for r in metrics_rows if r.get(field) is not None]
            return round(sum(vals)/len(vals), 1) if vals else 0.0
        m = {
            "name": pname, "position": p["position"],
            "rating":            avg_field("rating"),
            "score_technical":   avg_field("score_technical"),
            "score_decision":    avg_field("score_decision"),
            "score_offensive":   avg_field("score_offensive"),
            "score_defensive":   avg_field("score_defensive"),
            "participation_rate":avg_field("participation_rate"),
            "total_events":      int(avg_field("total_events")),
            "goals":             int(avg_field("goals")),
            "pass_accuracy":     avg_field("pass_accuracy"),
            "recoveries":        int(avg_field("recoveries")),
            "n_sessions":        len(metrics_rows),
        }
        comp_data.append(m)

    if not comp_data:
        st.warning("Ninguno de los jugadores seleccionats té métricas en la sesión escollida.")
        st.markdown("</div>",unsafe_allow_html=True); return

    st.divider()

    # ── Taula resum de ratings ──
    st.markdown('<div class="stitle">Resumen de ratings</div>', unsafe_allow_html=True)
    cols_header = st.columns(len(comp_data))
    for i, m in enumerate(comp_data):
        pc = pos_color(m["position"])
        with cols_header[i]:
            sess_label = f'{m["n_sessions"]} ses.' if m["n_sessions"]>1 else "1 ses."
            st.markdown(
                f'<div class="pip-card-sm" style="text-align:center;border-color:{pc}44;">'
                f'<div style="font-size:10px;color:#6b7280;letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px;">{m["position"]} · {sess_label}</div>'
                f'<div style="font-weight:700;font-size:15px;color:#f3f4f6;margin-bottom:6px;">{m["name"]}</div>'
                f'<div style="font-family:\'DM Sans\',sans-serif;font-weight:900;font-size:3rem;color:{pc};line-height:1;">{m["rating"]}</div>'
                f'<div style="font-size:10px;color:#374151;margin-top:2px;">rating mig</div>'
                f'</div>', unsafe_allow_html=True)

    st.divider()

    # ── Comparativa de categories ──
    st.markdown('<div class="stitle">Categorías</div>', unsafe_allow_html=True)
    cat_keys = [("Técnica","score_technical","#3b82f6"),
                ("Decisión","score_decision","#8b5cf6"),
                ("Ataque","score_offensive","#ef4444"),
                ("Defensa","score_defensive","#10b981")]

    for cat_lbl, cat_key, cat_col in cat_keys:
        bar_cols = st.columns([1] + [3]*len(comp_data))
        with bar_cols[0]:
            st.markdown(f'<div style="font-size:11px;color:#6b7280;padding-top:8px;text-align:right;">{cat_lbl}</div>', unsafe_allow_html=True)
        for i, m in enumerate(comp_data):
            val = m[cat_key]; pct = val * 10
            pc  = pos_color(m["position"])
            with bar_cols[i+1]:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;">'
                    f'<div style="flex:1;background:rgba(255,255,255,0.07);border-radius:4px;height:8px;overflow:hidden;">'
                    f'<div style="width:{pct:.0f}%;height:8px;background:{cat_col};border-radius:4px;"></div></div>'
                    f'<div style="font-weight:700;font-size:12px;color:{cat_col};width:28px;">{val:.1f}</div>'
                    f'</div>', unsafe_allow_html=True)

    st.divider()

    # ── Radars en columnes ──
    st.markdown('<div class="stitle">Perfiles de rendimiento</div>', unsafe_allow_html=True)
    radar_cols = st.columns(len(comp_data))
    for i, m in enumerate(comp_data):
        with radar_cols[i]:
            st.markdown(f'<div style="font-size:11px;color:#9ca3af;text-align:center;margin-bottom:4px;">{m["name"]}</div>', unsafe_allow_html=True)
            st.image(radar_img(m, m["name"]), use_container_width=True)

    st.divider()

    # ── Taula detallada ──
    st.markdown('<div class="stitle">Mètriques detallades</div>', unsafe_allow_html=True)
    metric_rows_def = [
        ("Rating",         "rating"),
        ("Participació %", "participation_rate"),
        ("Todal events",   "total_events"),
        ("Pase %",         "pass_accuracy"),
        ("Gols",           "goals"),
        ("Recuperacions",  "recoveries"),
    ]
    header_cells = "<th>Mètrica</th>" + "".join(f'<th style="text-align:center;">{m["name"]}</th>' for m in comp_data)
    body_rows = ""
    for row_lbl, row_key in metric_rows_def:
        vals = [m[row_key] for m in comp_data]
        max_val = max(vals) if vals else 0
        cells = "".join(
            f'<td style="text-align:center;font-weight:700;color:{"#a78bfa" if v==max_val and max_val>0 else "#9ca3af"};">{v}</td>'
            for v, m in zip(vals, comp_data)
        )
        body_rows += f'<tr><td style="color:#6b7280;">{row_lbl}</td>{cells}</tr>'
    st.markdown(f'<div class="pip-card" style="padding:0;overflow:hidden;">'
                f'<table class="pip-table"><thead><tr>{header_cells}</tr></thead>'
                f'<tbody>{body_rows}</tbody></table></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_calendario():
    import calendar as _cal
    from datetime import date as _date

    st.markdown('<div class="page-header"><div class="page-title">Calendario</div>'
                '<div class="page-sub">Historial de sessions per data</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='padding:0 2rem;'>", unsafe_allow_html=True)

    # Estat de navegació del mes
    today = _date.today()
    if "cal_year"  not in st.session_state: st.session_state.cal_year  = today.year
    if "cal_month" not in st.session_state: st.session_state.cal_month = today.month

    y = st.session_state.cal_year
    m = st.session_state.cal_month

    # Carregar totes les sessions i indexar per data
    all_sessions = [normalise_session(s) for s in _q("sessions", order="created_at")]
    sessions_by_date = {}
    for s in all_sessions:
        try:
            d = datetime.fromisoformat(s["created_at"]).date()
            sessions_by_date.setdefault(d, []).append(s)
        except: pass

    # Navegació de mes
    nav1, nav2, nav3 = st.columns([1, 3, 1])
    with nav1:
        if st.button("◀ Mes anterior", use_container_width=True, key="cal_prev"):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12; st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with nav2:
        month_names = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
                       "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        st.markdown(f'<div style="text-align:center;font-family:\'DM Sans\',sans-serif;font-weight:700;font-size:18px;color:#f3f4f6;padding:.4rem 0;">'
                    f'{month_names[m]} {y}</div>', unsafe_allow_html=True)
    with nav3:
        if st.button("Mes siguiente ▶", use_container_width=True, key="cal_next"):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1; st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    # Construir la graella del calendari en HTML
    cal = _cal.monthcalendar(y, m)
    day_headers = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]

    header_html = "".join(
        f'<th style="padding:8px 0;text-align:center;font-size:10px;font-weight:600;'
        f'letter-spacing:.1em;color:#4b5563;text-transform:uppercase;">{d}</th>'
        for d in day_headers
    )

    rows_html = ""
    for week in cal:
        rows_html += "<tr>"
        for day in week:
            if day == 0:
                rows_html += '<td style="padding:4px;"></td>'
            else:
                cell_date = _date(y, m, day)
                is_today  = cell_date == today
                day_sess  = sessions_by_date.get(cell_date, [])
                n_sess    = len(day_sess)

                # Estil del dia
                if is_today:
                    day_bg     = "rgba(124,58,237,0.25)"
                    day_border = "1px solid #7c3aed"
                    day_color  = "#c4b5fd"
                    num_color  = "#a78bfa"
                elif n_sess > 0:
                    day_bg     = "rgba(16,185,129,0.08)"
                    day_border = "1px solid rgba(16,185,129,0.3)"
                    day_color  = "#d1fae5"
                    num_color  = "#f3f4f6"
                else:
                    day_bg     = "rgba(255,255,255,0.02)"
                    day_border = "1px solid rgba(255,255,255,0.05)"
                    day_color  = "#374151"
                    num_color  = "#6b7280"

                # Punts de sessió (màx 3)
                dots = ""
                for s in day_sess[:3]:
                    dot_col = "#7c3aed" if s["category"]=="Partido" else "#10b981"
                    dots += f'<div style="width:5px;height:5px;border-radius:50%;background:{dot_col};flex-shrink:0;"></div>'
                dots_html = f'<div style="display:flex;justify-content:center;gap:3px;margin-top:4px;">{dots}</div>' if dots else ""

                rows_html += (
                    f'<td style="padding:4px;width:14.28%;">'
                    f'<div style="background:{day_bg};border:{day_border};border-radius:8px;'
                    f'padding:6px 4px;text-align:center;min-height:52px;">'
                    f'<div style="font-size:13px;font-weight:{"700" if is_today or n_sess>0 else "400"};color:{num_color};">{day}</div>'
                    f'{dots_html}'
                    f'</div></td>'
                )
        rows_html += "</tr>"

    st.markdown(f"""
    <div class="pip-card" style="padding:1rem;margin-top:.5rem;">
        <table style="width:100%;border-collapse:collapse;">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        <div style="display:flex;gap:1.5rem;margin-top:1rem;padding-top:.8rem;
                    border-top:1px solid rgba(255,255,255,0.06);flex-wrap:wrap;">
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#6b7280;">
                <div style="width:8px;height:8px;border-radius:50%;background:#7c3aed;"></div> Partido
            </div>
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#6b7280;">
                <div style="width:8px;height:8px;border-radius:50%;background:#10b981;"></div> Entrenamiento
            </div>
            <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#6b7280;">
                <div style="width:10px;height:10px;border-radius:3px;background:rgba(124,58,237,0.25);border:1px solid #7c3aed;"></div> Hoy
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Llistat de sessions del mes actual
    month_sessions = [
        (d, s) for d, sl in sessions_by_date.items()
        for s in sl if d.year == y and d.month == m
    ]
    month_sessions.sort(key=lambda x: x[0])

    if month_sessions:
        st.divider()
        st.markdown('<div class="stitle">Sessions d\'aquest mes</div>', unsafe_allow_html=True)
        for d, s in month_sessions:
            status_badge = '<span class="badge badge-yellow">Abierta</span>' if s["status"]=="open" else '<span class="badge badge-green">Cerrada</span>'
            cat_col = "#7c3aed" if s["category"]=="Partido" else "#10b981"
            n_ev = ev_count(s["id"])
            sc1, sc2 = st.columns([4, 1])
            with sc1:
                st.markdown(
                    f'<div class="pip-card-sm" style="border-left:3px solid {cat_col};">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">'
                    f'<div>'
                    f'<div style="font-weight:600;color:#e5e7eb;font-size:13px;">{s["name"]}</div>'
                    f'<div style="font-size:11px;color:#6b7280;margin-top:2px;">'
                    f'<span style="color:{cat_col};">{s["category"]}</span>'
                    f' · {d.strftime("%d %b %Y")} · {n_ev} eventos'
                    f'</div></div>'
                    f'{status_badge}'
                    f'</div></div>', unsafe_allow_html=True)
            with sc2:
                if s["status"] == "open":
                    if st.button("▶ Abrir", key=f"cal_open_{s['id']}", use_container_width=True):
                        st.session_state.active_session = s
                        st.session_state.active_player  = None
                        go_nav("Análisis Técnico")
                else:
                    if st.button("📋 Informe", key=f"cal_rep_{s['id']}", use_container_width=True):
                        pls2 = session_players(s["id"])
                        st.session_state.report_session = s
                        st.session_state.report_player  = pls2[0] if pls2 else None
                        go_nav("Reportes")
    else:
        st.markdown(f'<div style="text-align:center;color:#374151;font-size:13px;padding:1rem 0;">'
                    f'Cap sessió registrada al {month_names[m]} {y}.</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_placeholder(title, icon, desc, note=""):
    st.markdown(f'<div class="page-header"><div class="page-title">{title}</div>'
                f'<div class="page-sub">{desc}</div></div>', unsafe_allow_html=True)
    st.markdown(f"<div style='padding:0 2rem;'>", unsafe_allow_html=True)
    st.markdown(f'<div class="pip-card" style="margin-top:1rem;">'
                f'<div class="empty-state"><div class="empty-icon">{icon}</div>'
                f'<div class="empty-title">{title} · Próximamente</div>'
                f'<div class="empty-sub">{note if note else "Esta sección estará disponible en futuras versiones de PIP PRO."}</div>'
                f'</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ██ SCREEN: SPLASH
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.screen == "splash":
    st.markdown("""
    <div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:2rem;">
        <div class="glow-orb" style="margin-bottom:2rem;"></div>
        <div class="pip-logo" style="font-size:38px;margin-bottom:.5rem;">
            <span class="pip">PIP</span><span class="pro">PRO</span>
        </div>
        <p style="color:#6b7280;font-size:12px;letter-spacing:.18em;text-transform:uppercase;margin-bottom:2.5rem;">
            Performance Integral Platform
        </p>
        <div class="loading-bar-wrap"><div class="loading-bar-inner"></div></div>
        <p style="color:#374151;font-size:11px;margin-top:1rem;letter-spacing:.12em;text-transform:uppercase;">Cargando...</p>
    </div>
    <script>
        setTimeout(function() {
            var btns = window.parent.document.querySelectorAll('button');
            btns.forEach(function(b){ if(b.innerText==='__pip_auto__') b.click(); });
        }, 2400);
    </script>
    """, unsafe_allow_html=True)
    if st.button("__pip_auto__", key="pip_auto"): go_screen("login")

# ══════════════════════════════════════════════════════════════════════════════
# ██ SCREEN: LOGIN
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen=="login":
    st.markdown("""
    <style>
    .login-page { padding-top:7vh; }
    .login-logo-block { text-align:center; margin-bottom:2rem; }
    .login-logo-text { font-family:'Orbitron',monospace; font-weight:900; font-size:32px; letter-spacing:.05em; margin-bottom:.4rem; }
    .login-logo-text .pip { color:#e8e8f0; }
    .login-logo-text .pro { color:#7c3aed; }
    </style>
    """, unsafe_allow_html=True)
    _,center,_=st.columns([1,1.05,1])
    with center:
        st.markdown('<div class="login-page">',unsafe_allow_html=True)
        st.markdown('<div class="login-logo-block"><div class="login-logo-text"><span class="pip">PIP</span><span class="pro">PRO</span></div><p style="color:#4b5563;font-size:10px;letter-spacing:.18em;text-transform:uppercase;margin:0;">Performance Integral Platform</p></div>',unsafe_allow_html=True)
        mode=st.session_state.get("login_mode","login")
        t1,t2=st.columns(2)
        with t1:
            if st.button("Iniciar sesión",use_container_width=True,key="tab_login",
                         type="primary" if mode=="login" else "secondary"):
                st.session_state.login_mode="login"; st.rerun()
        with t2:
            if st.button("Crear cuenta",use_container_width=True,key="tab_reg",
                         type="primary" if mode=="register" else "secondary"):
                st.session_state.login_mode="register"; st.rerun()
        st.markdown('<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:1.6rem 1.4rem 1rem;margin-top:0.5rem;">',unsafe_allow_html=True)
        if mode=="login":
            st.markdown('<h2 style="font-size:18px;font-weight:700;margin:0 0 .2rem;color:#f3f4f6;">Bienvenido de vuelta</h2><p style="color:#6b7280;font-size:13px;margin:0 0 1rem;">Inicia sesión para continuar</p>',unsafe_allow_html=True)
        else:
            st.markdown('<h2 style="font-size:18px;font-weight:700;margin:0 0 .2rem;color:#f3f4f6;">Crear cuenta</h2><p style="color:#6b7280;font-size:13px;margin:0 0 1rem;">Regístrate para acceder a PIP PRO</p>',unsafe_allow_html=True)
        email=st.text_input("EMAIL",placeholder="tu@email.com",key="login_email")
        password=st.text_input("CONTRASEÑA",placeholder="Contraseña",type="password",key="login_pass")
        if mode=="login":
            if st.button("Iniciar sesión →",type="primary",use_container_width=True,key="login_btn"):
                if email and password:
                    with st.spinner("Verificando..."):
                        user,err=auth_login(email,password)
                    if user:
                        display=email.split("@")[0].replace("."," ").replace("_"," ").title()
                        st.session_state.logged_user=display; st.session_state.supabase_user=user
                        go_screen("app")
                    else:
                        st.error("Credenciales incorrectas.")
                else:
                    st.error("Introduce email y contraseña.")
        else:
            if st.button("Crear cuenta →",type="primary",use_container_width=True,key="reg_btn"):
                if email and password:
                    if len(password)<6: st.error("Mínimo 6 caracteres.")
                    else:
                        with st.spinner("Creando cuenta..."):
                            user,err=auth_signup(email,password)
                        if user:
                            st.success("✓ ¡Cuenta creada! Revisa tu correo para confirmarla e inicia sesión.")
                            st.session_state.login_mode="login"; st.rerun()
                        else: st.error(f"Error: {err}")
                else: st.error("Introduce email y contraseña.")
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#1f2937;font-size:10px;margin-top:.8rem;">© 2024 PIP PRO · Confidencial</p>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ██ SCREEN: APP
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "app":
    sidebar_col, main_col = st.columns([1, 5.5])
    render_sidebar(sidebar_col)

    with main_col:
        nav = st.session_state.nav
        if   nav == "Dashboard":        render_dashboard()
        elif nav == "Sesiones":         render_sesiones()
        elif nav == "Jugadores":        render_jugadores()
        elif nav == "Análisis Técnico": render_analisis_tecnico()
        elif nav == "Análisis Físico":  render_placeholder("Análisis Físico","📈","Módulo de métricas físicas y carga de trabajo","Disponible próximamente. Integrará datos de GPS, frecuencia cardíaca y métricas de carga física por jugador.")
        elif nav == "Reportes":         render_reportes()
        elif nav == "Comparaciones":    render_comparaciones()
        elif nav == "Calendario":       render_calendario()
        elif nav == "Configuración":    render_placeholder("Configuración","⚙","Preferencias y gestión del sistema","Configuración de credenciales, preferencias de visualización, exportación de datos y gestión de usuarios.")