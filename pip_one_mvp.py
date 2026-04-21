"""
PIP ONE — MVP v3
Partido vs Entrenamiento · Eventos GK separados · Posición × Ejercicio · SQLite · PDF
"""

import streamlit as st
import sqlite3, os, io, uuid, re
from datetime import datetime
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                  TableStyle, HRFlowable, Image as RLImage)

DB_PATH = "pip_one.db"

st.set_page_config(page_title="PIP ONE", page_icon="⚽", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;900&family=Barlow:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Barlow',sans-serif;background:#080808;color:#f0f0f0;}
.stApp{background:#080808;}
section[data-testid="stSidebar"]{background:#080808!important;border-right:1px solid #181818;}
.pip-hdr{background:#080808;border-bottom:3px solid #e63946;padding:14px 28px;margin:-1rem -1rem 1.5rem -1rem;display:flex;align-items:baseline;gap:14px;}
.pip-logo{font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:2.2rem;color:#e63946;letter-spacing:5px;}
.pip-sub{font-family:'Barlow Condensed',sans-serif;font-weight:600;font-size:0.85rem;color:#333;letter-spacing:3px;text-transform:uppercase;}
.card{background:#101010;border:1px solid #1c1c1c;border-radius:10px;padding:16px;margin-bottom:12px;}
.card-red{background:#0e0203;border:1px solid #3a0810;border-radius:10px;padding:16px;margin-bottom:12px;}
.card-amber{background:#0e0b02;border:1px solid #3a2e08;border-radius:10px;padding:16px;margin-bottom:12px;}
.stitle{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:0.62rem;letter-spacing:3px;color:#333;text-transform:uppercase;margin-bottom:8px;padding-bottom:4px;border-bottom:1px solid #181818;}
.badge{display:inline-block;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:0.68rem;letter-spacing:2px;padding:3px 10px;border-radius:3px;text-transform:uppercase;}
.badge-red{background:#e63946;color:#fff;}
.badge-amber{background:#f39c12;color:#080808;}
.badge-green{background:#27ae60;color:#fff;}
.badge-gray{background:#1e1e1e;color:#555;}
.badge-blue{background:#2980b9;color:#fff;}
.badge-purple{background:#8e44ad;color:#fff;}
.rating-hero{font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:5rem;color:#e63946;line-height:1;}
.rating-lg{font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:2.2rem;color:#e63946;line-height:1;}
.sbar-wrap{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
.sbar-label{font-size:0.76rem;color:#666;width:80px;text-align:right;flex-shrink:0;}
.sbar-bg{flex:1;background:#181818;border-radius:3px;height:7px;overflow:hidden;}
.sbar-fill{height:7px;border-radius:3px;}
.sbar-val{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:0.9rem;width:32px;}
.elog{display:flex;align-items:center;gap:7px;padding:5px 9px;border-radius:4px;background:#0a0a0a;border:1px solid #181818;margin-bottom:3px;font-size:0.78rem;}
.pos-gk{color:#f39c12;}
.pos-def{color:#27ae60;}
.pos-med{color:#8e44ad;}
.pos-del{color:#e63946;}
.analysis-block{background:#0a0a0a;border-left:3px solid #e63946;padding:12px 16px;border-radius:0 8px 8px 0;margin:8px 0;font-size:0.86rem;line-height:1.65;color:#bbb;}
[data-testid="metric-container"]{background:#101010!important;border:1px solid #1c1c1c!important;border-radius:8px!important;padding:12px!important;}
[data-testid="metric-container"] label{color:#444!important;font-size:0.7rem!important;letter-spacing:1px!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#e63946!important;font-family:'Barlow Condensed',sans-serif!important;font-size:1.5rem!important;font-weight:700!important;}
[data-testid="stTabs"] [role="tab"]{font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;letter-spacing:2px!important;font-size:0.8rem!important;color:#333!important;text-transform:uppercase!important;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{color:#e63946!important;border-bottom:2px solid #e63946!important;}
div.stButton>button{font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;letter-spacing:1px!important;}
div.stButton>button[kind="primary"]{background:#e63946!important;border:none!important;color:#fff!important;}
.toggle-big{display:flex;gap:0;border:1px solid #2a2a2a;border-radius:8px;overflow:hidden;margin-bottom:16px;}
.toggle-opt{flex:1;padding:14px;text-align:center;cursor:pointer;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:1rem;letter-spacing:2px;text-transform:uppercase;transition:background .15s;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BASE DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

def get_conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = get_conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS sessions (
        id            TEXT PRIMARY KEY,
        name          TEXT NOT NULL,
        group_name    TEXT,
        category      TEXT NOT NULL,
        exercise_type TEXT,
        status        TEXT DEFAULT 'open',
        created_at    TEXT,
        closed_at     TEXT
    );
    CREATE TABLE IF NOT EXISTS players (
        id         TEXT PRIMARY KEY,
        name       TEXT NOT NULL UNIQUE,
        position   TEXT DEFAULT 'MED',
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS session_players (
        session_id TEXT, player_id TEXT,
        PRIMARY KEY(session_id, player_id)
    );
    CREATE TABLE IF NOT EXISTS events (
        id         TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        player_id  TEXT NOT NULL,
        event_type TEXT NOT NULL,
        event_cat  TEXT NOT NULL,
        ts         TEXT,
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS player_metrics (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL, player_id TEXT NOT NULL,
        position TEXT, exercise_type TEXT,
        w_technical REAL, w_decision REAL, w_offensive REAL, w_defensive REAL,
        total_events INTEGER DEFAULT 0,
        save_rate REAL DEFAULT 0, exit_rate REAL DEFAULT 0,
        short_pass_acc REAL DEFAULT 0, long_pass_acc REAL DEFAULT 0,
        total_saves INTEGER DEFAULT 0, great_saves INTEGER DEFAULT 0,
        pass_accuracy REAL DEFAULT 0, control_accuracy REAL DEFAULT 0,
        decision_score REAL DEFAULT 0, dribble_accuracy REAL DEFAULT 0,
        duel_accuracy REAL DEFAULT 0, total_shots INTEGER DEFAULT 0,
        shots_on_target INTEGER DEFAULT 0, goals INTEGER DEFAULT 0,
        offensive_actions INTEGER DEFAULT 0, defensive_actions INTEGER DEFAULT 0,
        recoveries INTEGER DEFAULT 0, interceptions INTEGER DEFAULT 0, errors INTEGER DEFAULT 0,
        participation_rate REAL DEFAULT 0,
        score_technical REAL DEFAULT 0, score_decision REAL DEFAULT 0,
        score_offensive REAL DEFAULT 0, score_defensive REAL DEFAULT 0,
        rating REAL DEFAULT 0, calculated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS scout_observations (
        id TEXT PRIMARY KEY, session_id TEXT NOT NULL, player_id TEXT NOT NULL,
        observation TEXT DEFAULT '', updated_at TEXT
    );
    """)
    c.commit(); c.close()

init_db()

def migrate_db():
    """Añade columnas que puedan faltar en bases de datos creadas con versiones anteriores."""
    c = get_conn()
    migrations = [
        ("sessions",       "category",       "TEXT DEFAULT 'Partido'"),
        ("sessions",       "exercise_type",  "TEXT DEFAULT 'Partido'"),
        ("players",        "position",       "TEXT DEFAULT 'MED'"),
        ("player_metrics", "position",       "TEXT DEFAULT 'MED'"),
        ("player_metrics", "exercise_type",  "TEXT DEFAULT 'Partido'"),
        ("player_metrics", "w_technical",    "REAL DEFAULT 0.25"),
        ("player_metrics", "w_decision",     "REAL DEFAULT 0.25"),
        ("player_metrics", "w_offensive",    "REAL DEFAULT 0.25"),
        ("player_metrics", "w_defensive",    "REAL DEFAULT 0.25"),
        ("player_metrics", "save_rate",      "REAL DEFAULT 0"),
        ("player_metrics", "exit_rate",      "REAL DEFAULT 0"),
        ("player_metrics", "short_pass_acc", "REAL DEFAULT 0"),
        ("player_metrics", "long_pass_acc",  "REAL DEFAULT 0"),
        ("player_metrics", "total_saves",    "INTEGER DEFAULT 0"),
        ("player_metrics", "great_saves",    "INTEGER DEFAULT 0"),
    ]
    for table, col, col_def in migrations:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
        except Exception:
            pass
    c.commit(); c.close()

migrate_db()

# ── helpers ──────────────────────────────────────────────────────────────────
def q(sql, *args, one=False, write=False):
    c = get_conn()
    cur = c.execute(sql, args)
    if write: c.commit(); c.close(); return
    rows = cur.fetchone() if one else cur.fetchall()
    c.close()
    return (dict(rows) if rows else None) if one else [dict(r) for r in rows]

def insert(sql, *args):
    c = get_conn(); c.execute(sql, args); c.commit(); c.close()

def normalise_session(s):
    """Garantiza valores por defecto en sesiones con columnas NULL (bases de datos antiguas)."""
    if not s: return s
    s = dict(s)
    s.setdefault("category",      "Partido")
    s.setdefault("exercise_type", "Partido")
    if not s.get("category"):      s["category"]      = "Partido"
    if not s.get("exercise_type"): s["exercise_type"] = "Partido"
    return s

def normalise_player(p):
    if not p: return p
    p = dict(p)
    if not p.get("position"): p["position"] = "MED"
    return p

def fmt_dt(iso):
    try: return datetime.fromisoformat(iso).strftime("%d/%m/%Y %H:%M")
    except: return iso or "—"

def pos_badge(pos):
    m = {"GK":"badge-amber","DEF":"badge-green","MED":"badge-purple","DEL":"badge-red"}
    return f'<span class="badge {m.get(pos,"badge-gray")}">{pos}</span>'

def pos_color(pos):
    return {"GK":"#f39c12","DEF":"#27ae60","MED":"#8e44ad","DEL":"#e63946"}.get(pos,"#888")

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

POSITIONS = ["GK","DEF","MED","DEL"]
POS_NAMES = {"GK":"Portero","DEF":"Defensa","MED":"Centrocampista","DEL":"Delantero"}

CATEGORIES = ["Partido","Entrenamiento"]

EXERCISES = ["Rondo / Posesión","Ataque organizado","Defensa organizada",
             "1v1 / Duelos","Pressing","Finalización"]

EX_DESC = {
    "Rondo / Posesión":   "Técnica y decisión bajo presión",
    "Ataque organizado":  "Combinaciones, movilidad, remate",
    "Defensa organizada": "Bloque, duelos, recuperación",
    "1v1 / Duelos":       "Situaciones individuales",
    "Pressing":           "Intensidad, recuperación alta",
    "Finalización":       "Tiro, remate, definición",
}

EX_COLOR = {
    "Rondo / Posesión":"#3498db","Ataque organizado":"#e63946",
    "Defensa organizada":"#27ae60","1v1 / Duelos":"#f39c12",
    "Pressing":"#e67e22","Finalización":"#e63946","Partido":"#1abc9c",
}

# Pesos: (exercise_or_partido, position) → {technical, decision, offensive, defensive}
WEIGHTS = {
    ("Partido","GK") : {"technical":.15,"decision":.20,"offensive":.10,"defensive":.55},
    ("Partido","DEF"): {"technical":.20,"decision":.25,"offensive":.20,"defensive":.35},
    ("Partido","MED"): {"technical":.25,"decision":.28,"offensive":.25,"defensive":.22},
    ("Partido","DEL"): {"technical":.18,"decision":.22,"offensive":.45,"defensive":.15},

    ("Rondo / Posesión","GK") : {"technical":.40,"decision":.35,"offensive":.00,"defensive":.25},
    ("Rondo / Posesión","DEF"): {"technical":.35,"decision":.30,"offensive":.10,"defensive":.25},
    ("Rondo / Posesión","MED"): {"technical":.40,"decision":.35,"offensive":.10,"defensive":.15},
    ("Rondo / Posesión","DEL"): {"technical":.35,"decision":.35,"offensive":.20,"defensive":.10},

    ("Ataque organizado","GK") : {"technical":.20,"decision":.35,"offensive":.00,"defensive":.45},
    ("Ataque organizado","DEF"): {"technical":.25,"decision":.30,"offensive":.15,"defensive":.30},
    ("Ataque organizado","MED"): {"technical":.25,"decision":.30,"offensive":.30,"defensive":.15},
    ("Ataque organizado","DEL"): {"technical":.15,"decision":.20,"offensive":.50,"defensive":.15},

    ("Defensa organizada","GK") : {"technical":.15,"decision":.25,"offensive":.00,"defensive":.60},
    ("Defensa organizada","DEF"): {"technical":.20,"decision":.25,"offensive":.10,"defensive":.45},
    ("Defensa organizada","MED"): {"technical":.20,"decision":.30,"offensive":.15,"defensive":.35},
    ("Defensa organizada","DEL"): {"technical":.20,"decision":.30,"offensive":.25,"defensive":.25},

    ("1v1 / Duelos","GK") : {"technical":.10,"decision":.40,"offensive":.00,"defensive":.50},
    ("1v1 / Duelos","DEF"): {"technical":.15,"decision":.30,"offensive":.15,"defensive":.40},
    ("1v1 / Duelos","MED"): {"technical":.20,"decision":.30,"offensive":.25,"defensive":.25},
    ("1v1 / Duelos","DEL"): {"technical":.15,"decision":.30,"offensive":.40,"defensive":.15},

    ("Pressing","GK") : {"technical":.15,"decision":.35,"offensive":.00,"defensive":.50},
    ("Pressing","DEF"): {"technical":.20,"decision":.25,"offensive":.15,"defensive":.40},
    ("Pressing","MED"): {"technical":.20,"decision":.30,"offensive":.20,"defensive":.30},
    ("Pressing","DEL"): {"technical":.20,"decision":.30,"offensive":.30,"defensive":.20},

    ("Finalización","GK") : {"technical":.15,"decision":.30,"offensive":.00,"defensive":.55},
    ("Finalización","DEF"): {"technical":.25,"decision":.25,"offensive":.20,"defensive":.30},
    ("Finalización","MED"): {"technical":.25,"decision":.25,"offensive":.30,"defensive":.20},
    ("Finalización","DEL"): {"technical":.20,"decision":.20,"offensive":.50,"defensive":.10},
}

# Fallback
DEFAULT_W = {"technical":.25,"decision":.25,"offensive":.25,"defensive":.25}

def get_weights(exercise_or_partido, position):
    return WEIGHTS.get((exercise_or_partido, position), DEFAULT_W)

# ── EVENTOS ──────────────────────────────────────────────────────────────────

GK_EVENTS = {
    "save":            {"label":"Parada",          "color":"#27ae60","cat":"defensive"},
    "great_save":      {"label":"Parada difícil",  "color":"#1abc9c","cat":"defensive"},
    "clearance":       {"label":"Despeje",          "color":"#2980b9","cat":"defensive"},
    "good_exit":       {"label":"Salida ✓",        "color":"#27ae60","cat":"defensive"},
    "bad_exit":        {"label":"Salida ✗",        "color":"#e74c3c","cat":"defensive"},
    "short_pass_ok":   {"label":"Pase corto ✓",    "color":"#3498db","cat":"technical"},
    "short_pass_fail": {"label":"Pase corto ✗",    "color":"#c0392b","cat":"technical"},
    "long_pass_ok":    {"label":"Pase largo ✓",    "color":"#2980b9","cat":"technical"},
    "long_pass_fail":  {"label":"Pase largo ✗",    "color":"#c0392b","cat":"technical"},
    "gk_error":        {"label":"Error",            "color":"#c0392b","cat":"general"},
}

GK_LAYOUT = [
    ("save","great_save"),
    ("clearance","good_exit"),
    ("bad_exit","short_pass_ok"),
    ("short_pass_fail","long_pass_ok"),
    ("long_pass_fail","gk_error"),
]

FIELD_EVENTS = {
    "pass_success":     {"label":"Pase ✓",       "color":"#27ae60","cat":"technical"},
    "pass_fail":        {"label":"Pase ✗",       "color":"#e74c3c","cat":"technical"},
    "control_success":  {"label":"Control ✓",    "color":"#3498db","cat":"technical"},
    "control_fail":     {"label":"Control ✗",    "color":"#c0392b","cat":"technical"},
    "decision_correct": {"label":"Decisión ✓",   "color":"#1abc9c","cat":"decision"},
    "decision_wrong":   {"label":"Decisión ✗",   "color":"#e74c3c","cat":"decision"},
    "shot":             {"label":"Tiro",          "color":"#f39c12","cat":"offensive"},
    "shot_on_target":   {"label":"Tiro puerta",  "color":"#e67e22","cat":"offensive"},
    "goal":             {"label":"Gol",           "color":"#f1c40f","cat":"offensive"},
    "dribble_success":  {"label":"Regate ✓",     "color":"#27ae60","cat":"offensive"},
    "dribble_fail":     {"label":"Regate ✗",     "color":"#e74c3c","cat":"offensive"},
    "recovery":         {"label":"Recuperación", "color":"#8e44ad","cat":"defensive"},
    "interception":     {"label":"Intercepción", "color":"#9b59b6","cat":"defensive"},
    "duel_won":         {"label":"Duelo ✓",      "color":"#27ae60","cat":"defensive"},
    "duel_lost":        {"label":"Duelo ✗",      "color":"#e74c3c","cat":"defensive"},
    "error":            {"label":"Error",         "color":"#c0392b","cat":"general"},
}

FIELD_LAYOUT = [
    ("pass_success","pass_fail"),
    ("control_success","control_fail"),
    ("decision_correct","decision_wrong"),
    ("shot","shot_on_target"),
    ("goal","dribble_success"),
    ("dribble_fail","recovery"),
    ("interception","duel_won"),
    ("duel_lost","error"),
]

ALL_EVENTS = {**GK_EVENTS, **FIELD_EVENTS}

CAT_LABELS = {"technical":"Técnica","decision":"Decisión","offensive":"Ataque","defensive":"Defensa"}

# ══════════════════════════════════════════════════════════════════════════════
# MOTOR DE MÉTRICAS
# ══════════════════════════════════════════════════════════════════════════════

def compute_metrics(events_list, position, exercise_key):
    if not events_list: return None
    def cnt(k): return sum(1 for e in events_list if e["event_type"]==k)
    total = len(events_list)
    w = get_weights(exercise_key, position)

    if position == "GK":
        saves      = cnt("save") + cnt("great_save")
        great      = cnt("great_save")
        clr        = cnt("clearance")
        good_ex    = cnt("good_exit")
        bad_ex     = cnt("bad_exit")
        sp_ok      = cnt("short_pass_ok")
        sp_fail    = cnt("short_pass_fail")
        lp_ok      = cnt("long_pass_ok")
        lp_fail    = cnt("long_pass_fail")
        gk_err     = cnt("gk_error")

        save_rate  = saves / max(saves + gk_err, 1)
        exit_rate  = good_ex / max(good_ex + bad_ex, 1)
        sp_acc     = sp_ok  / max(sp_ok  + sp_fail, 1)
        lp_acc     = lp_ok  / max(lp_ok  + lp_fail, 1)
        part       = min(total / 15.0, 1.0)
        err_pen    = min(gk_err * 0.08, 0.30)

        tech  = max(0, (sp_acc * 0.5 + lp_acc * 0.5) - err_pen * 0.5)
        dec   = max(0, exit_rate - err_pen * 0.3)
        off   = 0.0
        defe  = max(0, save_rate * 0.7 + (clr / max(clr+1,1)) * 0.3 - err_pen * 0.5)
        defe  = min(defe, 1.0)

        g = tech*w["technical"] + dec*w["decision"] + off*w["offensive"] + defe*w["defensive"]
        g = min(g + part*0.4, 1.0)

        return {
            "is_gk": True, "total_events": total, "position": position,
            "exercise_type": exercise_key,
            "w_technical": w["technical"], "w_decision": w["decision"],
            "w_offensive": w["offensive"], "w_defensive": w["defensive"],
            "save_rate": round(save_rate*100,1), "exit_rate": round(exit_rate*100,1),
            "short_pass_acc": round(sp_acc*100,1), "long_pass_acc": round(lp_acc*100,1),
            "total_saves": saves, "great_saves": great,
            "errors": gk_err,
            "participation_rate": round(part*100,1),
            "score_technical":  round(tech*10,1),
            "score_decision":   round(dec*10,1),
            "score_offensive":  0.0,
            "score_defensive":  round(defe*10,1),
            "rating": round(g*10,1),
            # unused field-only cols (stored as 0 for DB)
            "pass_accuracy":0,"control_accuracy":0,"decision_score":0,
            "dribble_accuracy":0,"duel_accuracy":0,"total_shots":0,
            "shots_on_target":0,"goals":0,"offensive_actions":0,
            "defensive_actions": saves+clr+good_ex,
            "recoveries":0,"interceptions":0,
        }
    else:
        ps,pf   = cnt("pass_success"),cnt("pass_fail")
        cs,cf   = cnt("control_success"),cnt("control_fail")
        dc,dw   = cnt("decision_correct"),cnt("decision_wrong")
        sh,sot  = cnt("shot"),cnt("shot_on_target")
        gl      = cnt("goal")
        drs,drf = cnt("dribble_success"),cnt("dribble_fail")
        rec,icp = cnt("recovery"),cnt("interception")
        duw,dul = cnt("duel_won"),cnt("duel_lost")
        err     = cnt("error")

        pa   = ps/(ps+pf)    if (ps+pf)>0   else 0.0
        ca   = cs/(cs+cf)    if (cs+cf)>0   else 0.0
        da   = dc/(dc+dw)    if (dc+dw)>0   else 0.0
        dra  = drs/(drs+drf) if (drs+drf)>0 else 0.0
        dua  = duw/(duw+dul) if (duw+dul)>0 else 0.0
        part = min(total/20.0, 1.0)
        ep   = min(err*0.05, 0.25)

        tech = max(0, (pa*0.5 + ca*0.5) - ep)
        dec  = max(0, da - ep*0.5)
        off  = min((sh+sot+gl+drs)/5.0,1.0)*0.5 + (sot/max(sh,1))*0.3 + min(gl,1)*0.2
        defe = min((rec+icp+duw)/5.0,1.0)*0.6 + dua*0.4

        g = tech*w["technical"]+dec*w["decision"]+off*w["offensive"]+defe*w["defensive"]
        g = min(g + part*0.4, 1.0)

        return {
            "is_gk": False, "total_events": total, "position": position,
            "exercise_type": exercise_key,
            "w_technical": w["technical"], "w_decision": w["decision"],
            "w_offensive": w["offensive"], "w_defensive": w["defensive"],
            "save_rate":0,"exit_rate":0,"short_pass_acc":0,"long_pass_acc":0,
            "total_saves":0,"great_saves":0,
            "pass_accuracy": round(pa*100,1), "control_accuracy": round(ca*100,1),
            "decision_score": round(da*100,1), "dribble_accuracy": round(dra*100,1),
            "duel_accuracy":  round(dua*100,1),
            "total_shots": sh+sot, "shots_on_target": sot, "goals": gl,
            "offensive_actions": sh+sot+gl+drs,
            "defensive_actions": rec+icp+duw,
            "recoveries": rec, "interceptions": icp, "errors": err,
            "participation_rate": round(part*100,1),
            "score_technical":  round(tech*10,1),
            "score_decision":   round(dec*10,1),
            "score_offensive":  round(off*10,1),
            "score_defensive":  round(defe*10,1),
            "rating": round(g*10,1),
        }

def close_and_compute(session_id, exercise_key):
    for p in q("SELECT p.* FROM players p JOIN session_players sp ON sp.player_id=p.id WHERE sp.session_id=?", session_id):
        evs = q("SELECT * FROM events WHERE session_id=? AND player_id=?", session_id, p["id"])
        m = compute_metrics(evs, p["position"], exercise_key)
        if not m: continue
        c = get_conn()
        c.execute("DELETE FROM player_metrics WHERE session_id=? AND player_id=?", (session_id, p["id"]))
        c.execute("""INSERT INTO player_metrics VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (str(uuid.uuid4())[:12], session_id, p["id"],
             p["position"], exercise_key,
             m["w_technical"], m["w_decision"], m["w_offensive"], m["w_defensive"],
             m["total_events"], m["save_rate"], m["exit_rate"],
             m["short_pass_acc"], m["long_pass_acc"],
             m["total_saves"], m["great_saves"],
             m["pass_accuracy"], m["control_accuracy"],
             m["decision_score"], m["dribble_accuracy"], m["duel_accuracy"],
             m["total_shots"], m["shots_on_target"], m["goals"],
             m["offensive_actions"], m["defensive_actions"],
             m["recoveries"], m["interceptions"], m["errors"],
             m["participation_rate"],
             m["score_technical"], m["score_decision"],
             m["score_offensive"], m["score_defensive"],
             m["rating"], datetime.now().isoformat()))
        c.commit(); c.close()
    q("UPDATE sessions SET status='closed', closed_at=? WHERE id=?",
      datetime.now().isoformat(), session_id, write=True)

# ══════════════════════════════════════════════════════════════════════════════
# TEXTO DE ANÁLISIS
# ══════════════════════════════════════════════════════════════════════════════

def analysis_text(player_name, m, exercise_key):
    r = m["rating"]; pos = m["position"]
    nivel = "excepcional" if r>=8 else ("muy bueno" if r>=6.5 else ("correcto" if r>=5 else "mejorable"))
    cats = {"Técnica":m["score_technical"],"Decisión":m["score_decision"],
            "Ataque":m["score_offensive"],"Defensa":m["score_defensive"]}
    best  = max(cats, key=cats.get)
    worst = min(cats, key=cats.get)
    ex_label = f"**{exercise_key}**" if exercise_key != "Partido" else "el **partido**"

    txt = (f"{player_name} ({POS_NAMES.get(pos,pos)}) ha completado {ex_label} "
           f"con un rendimiento **{nivel}** — rating **{r}/10**. "
           f"Registró **{m['total_events']} acciones** con una participación del {m['participation_rate']:.0f}%.")

    if pos == "GK":
        if m["total_saves"] > 0:
            txt += (f" Realizó **{m['total_saves']} paradas** ({m.get('great_saves',0)} difíciles) "
                    f"con una efectividad del {m['save_rate']:.0f}%.")
        if m["exit_rate"] > 0:
            txt += f" En las salidas, su tasa de acierto fue del **{m['exit_rate']:.0f}%**."
        pa = m.get("short_pass_acc",0)
        if pa > 0:
            txt += f" Su pase corto tiene una precisión del {pa:.0f}%."
    else:
        if m["pass_accuracy"] > 0:
            txt += f" Su precisión de pase es del **{m['pass_accuracy']:.0f}%**."
        if m["offensive_actions"] > 0:
            txt += (f" Generó **{m['offensive_actions']} acciones ofensivas**"
                    + (f", incluyendo **{m['goals']} gol{'es' if m['goals']!=1 else ''}**" if m["goals"]>0 else "") + ".")
        if m["defensive_actions"] > 0:
            txt += (f" En defensa sumó **{m['defensive_actions']} acciones** "
                    f"({m['recoveries']} recuperaciones, {m['interceptions']} intercepciones).")

    txt += (f" Su **mayor fortaleza** en este contexto es la **{best}** ({cats[best]:.1f}/10)"
            f" y el área con mayor margen de mejora es la **{worst}** ({cats[worst]:.1f}/10).")
    return txt

# ══════════════════════════════════════════════════════════════════════════════
# GRÁFICAS
# ══════════════════════════════════════════════════════════════════════════════

def radar_img(m, name, size=(3.2,3.2)):
    cats  = ["Técnica","Decisión","Ataque","Defensa","Particip."]
    vals  = [m["score_technical"]/10, m["score_decision"]/10,
             m["score_offensive"]/10, m["score_defensive"]/10,
             m["participation_rate"]/100]
    N = len(cats); angles = [n/N*2*np.pi for n in range(N)]; angles += angles[:1]
    v = vals+[vals[0]]
    fig, ax = plt.subplots(figsize=size, subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#080808"); ax.set_facecolor("#080808")
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(cats, size=8, color="#777")
    ax.set_ylim(0,1); ax.set_yticks([.25,.5,.75,1]); ax.set_yticklabels(["2.5","5","7.5","10"],size=6,color="#2a2a2a")
    ax.grid(color="#1a1a1a",linewidth=0.8); ax.spines['polar'].set_edgecolor("#2a2a2a")
    pc = pos_color(m["position"])
    ax.plot(angles, v, color=pc, linewidth=2.5)
    ax.fill(angles, v, color=pc, alpha=0.18)
    for a,vv in zip(angles,v[:-1]): ax.plot(a,vv,"o",color=pc,markersize=5)
    plt.tight_layout(pad=0.5)
    buf = io.BytesIO()
    plt.savefig(buf,format="png",dpi=150,bbox_inches="tight",facecolor="#080808")
    plt.close(fig); buf.seek(0); return buf

def bar_img(m, size=(4.0,1.8)):
    cats = ["Técnica","Decisión","Ataque","Defensa"]
    vals = [m["score_technical"],m["score_decision"],m["score_offensive"],m["score_defensive"]]
    clrs = ["#3498db","#9b59b6","#e63946","#27ae60"]
    fig, ax = plt.subplots(figsize=size)
    fig.patch.set_facecolor("#080808"); ax.set_facecolor("#080808")
    bars = ax.barh(cats, vals, color=clrs, height=0.5)
    for bar, v in zip(bars,vals):
        ax.text(v+0.12, bar.get_y()+bar.get_height()/2, f"{v:.1f}",
                va="center",ha="left",color="#e63946",fontsize=9,fontweight="bold")
    ax.set_xlim(0,11.5)
    ax.tick_params(colors="#555",labelsize=9)
    for s in ax.spines.values(): s.set_edgecolor("#181818")
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    plt.tight_layout(pad=0.4)
    buf = io.BytesIO()
    plt.savefig(buf,format="png",dpi=150,bbox_inches="tight",facecolor="#080808")
    plt.close(fig); buf.seek(0); return buf

# ══════════════════════════════════════════════════════════════════════════════
# PDF
# ══════════════════════════════════════════════════════════════════════════════

def make_pdf(player_name, sess, m, analysis, observation):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm,rightMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    RED   = colors.HexColor("#e63946")
    DARK  = colors.HexColor("#080808")
    MID   = colors.HexColor("#161616")
    LIGHT = colors.HexColor("#222222")
    GRAY  = colors.HexColor("#888888")
    pc    = colors.HexColor(pos_color(m["position"]))

    s_title = ParagraphStyle("T",parent=styles["Title"],fontSize=22,textColor=RED,spaceAfter=2,fontName="Helvetica-Bold")
    s_sub   = ParagraphStyle("S",parent=styles["Normal"],fontSize=9,textColor=GRAY,spaceAfter=6,alignment=TA_CENTER)
    s_h2    = ParagraphStyle("H2",parent=styles["Normal"],fontSize=11,textColor=RED,spaceBefore=12,spaceAfter=4,fontName="Helvetica-Bold")
    s_body  = ParagraphStyle("B",parent=styles["Normal"],fontSize=9,textColor=colors.HexColor("#cccccc"),leading=14,spaceAfter=8)
    s_obs   = ParagraphStyle("O",parent=styles["Normal"],fontSize=9,textColor=colors.HexColor("#aaaaaa"),leading=14,leftIndent=10)
    s_small = ParagraphStyle("SM",parent=styles["Normal"],fontSize=7,textColor=GRAY,alignment=TA_CENTER,spaceBefore=4)

    def enc(t):
        t = re.sub(r'\*\*(.*?)\*\*',r'\1',str(t))
        return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

    story = []

    # Header
    ht = Table([[
        Paragraph("PIP ONE",ParagraphStyle("HL",parent=styles["Normal"],fontSize=18,textColor=RED,fontName="Helvetica-Bold",alignment=TA_LEFT)),
        Paragraph("INFORME DE JUGADOR",ParagraphStyle("HR",parent=styles["Normal"],fontSize=8,textColor=GRAY,fontName="Helvetica-Bold",alignment=4,letterSpacing=3)),
    ]],colWidths=[9*cm,8*cm])
    ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK),("LINEBELOW",(0,0),(-1,-1),2,RED),
                             ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
    story.append(ht); story.append(Spacer(1,10))

    story.append(Paragraph(enc(player_name), s_title))
    ex_label = sess.get("exercise_type") or "Partido"
    pos_label = POS_NAMES.get(m["position"], m["position"])
    story.append(Paragraph(enc(f"{pos_label} · {ex_label} · {sess['name']} · {sess['created_at'][:10]}"), s_sub))
    story.append(HRFlowable(width="100%",thickness=1,color=LIGHT,spaceAfter=10))

    # Rating block
    rating_p = Paragraph(
        f'<font color="#e63946" size="36"><b>{m["rating"]}</b></font><br/>'
        f'<font color="#888" size="8">RATING /10</font>',
        ParagraphStyle("RT",parent=styles["Normal"],alignment=TA_CENTER))

    pos_p = Paragraph(
        f'<font size="9" color="#888">POSICIÓN</font><br/>'
        f'<font size="13" color="{pos_color(m["position"])}"><b>{pos_label}</b></font><br/>'
        f'<font size="8" color="#555">{m["total_events"]} acciones · {m["participation_rate"]:.0f}% part.</font>',
        ParagraphStyle("PP",parent=styles["Normal"],alignment=TA_CENTER))

    w_p = Paragraph(
        f'<font size="8" color="#555">PESOS APLICADOS</font><br/>'
        f'<font size="8" color="#3498db">Téc {m["w_technical"]*100:.0f}%</font>  '
        f'<font size="8" color="#9b59b6">Dec {m["w_decision"]*100:.0f}%</font><br/>'
        f'<font size="8" color="#e63946">Ata {m["w_offensive"]*100:.0f}%</font>  '
        f'<font size="8" color="#27ae60">Def {m["w_defensive"]*100:.0f}%</font>',
        ParagraphStyle("WP",parent=styles["Normal"],alignment=TA_CENTER))

    top = Table([[rating_p, pos_p, w_p]],colWidths=[4.5*cm,5.5*cm,7*cm])
    top.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),MID),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                              ("ALIGN",(0,0),(-1,-1),"CENTER"),("BOX",(0,0),(-1,-1),0.5,LIGHT),
                              ("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14)]))
    story.append(top); story.append(Spacer(1,10))

    # Scores
    scores_data = [["CATEGORÍA","SCORE","PESO"]]
    for cat,score,weight,color_hex in [
        ("Técnica",  m["score_technical"], m["w_technical"], "#3498db"),
        ("Decisión", m["score_decision"],  m["w_decision"],  "#9b59b6"),
        ("Ataque",   m["score_offensive"], m["w_offensive"], "#e63946"),
        ("Defensa",  m["score_defensive"], m["w_defensive"], "#27ae60"),
    ]:
        scores_data.append([
            Paragraph(f'<font color="#888" size="8">{cat}</font>',styles["Normal"]),
            Paragraph(f'<font color="{color_hex}" size="14"><b>{score:.1f}</b></font>',styles["Normal"]),
            Paragraph(f'<font color="#555" size="8">{weight*100:.0f}%</font>',styles["Normal"]),
        ])
    st_ = Table(scores_data, colWidths=[4*cm,3*cm,3*cm])
    st_.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),MID),("GRID",(0,0),(-1,-1),0.3,LIGHT),
                              ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
                              ("LEFTPADDING",(0,0),(-1,-1),8),
                              ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0a0a0a")),
                              ("TEXTCOLOR",(0,0),(-1,0),GRAY),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                              ("FONTSIZE",(0,0),(-1,0),7)]))

    # Bar chart
    b_buf = bar_img(m)
    b_img = RLImage(b_buf,width=9*cm,height=4*cm)

    mid_block = Table([[st_, b_img]],colWidths=[10*cm,7*cm])
    mid_block.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                    ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    story.append(mid_block); story.append(Spacer(1,8))

    # Key metrics
    story.append(Paragraph("MÉTRICAS CLAVE", s_h2))
    if m["position"] == "GK":
        mkeys = [("Paradas",m["total_saves"]),("Paradas difíciles",m.get("great_saves",0)),
                 ("Efectividad %",f'{m["save_rate"]:.0f}%'),("Salidas %",f'{m["exit_rate"]:.0f}%'),
                 ("Pase corto %",f'{m["short_pass_acc"]:.0f}%'),("Pase largo %",f'{m["long_pass_acc"]:.0f}%'),
                 ("Errores",m["errors"]),("Participación %",f'{m["participation_rate"]:.0f}%')]
    else:
        mkeys = [("Pase %",f'{m["pass_accuracy"]:.0f}%'),("Control %",f'{m["control_accuracy"]:.0f}%'),
                 ("Decisión %",f'{m["decision_score"]:.0f}%'),("Regate %",f'{m["dribble_accuracy"]:.0f}%'),
                 ("Duelo %",f'{m["duel_accuracy"]:.0f}%'),("Tiros puerta",m["shots_on_target"]),
                 ("Goles",m["goals"]),("Recuperaciones",m["recoveries"]),
                 ("Intercepciones",m["interceptions"]),("Errores",m["errors"]),
                 ("Acc. ofensivas",m["offensive_actions"]),("Acc. defensivas",m["defensive_actions"])]
    rows = []
    for i in range(0,len(mkeys),3):
        chunk = mkeys[i:i+3]; row = []
        for lbl,val in chunk:
            row += [Paragraph(f'<font color="#555" size="7">{enc(lbl)}</font>',styles["Normal"]),
                    Paragraph(f'<font color="#e63946" size="11"><b>{enc(str(val))}</b></font>',styles["Normal"])]
        while len(row)<6: row += [Paragraph("",styles["Normal"]),Paragraph("",styles["Normal"])]
        rows.append(row)
    mt = Table(rows,colWidths=[4*cm,1.5*cm,4*cm,1.5*cm,4*cm,1.5*cm])
    mt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),MID),("GRID",(0,0),(-1,-1),0.3,LIGHT),
                             ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                             ("LEFTPADDING",(0,0),(-1,-1),8),
                             ("ROWBACKGROUNDS",(0,0),(-1,-1),[MID,colors.HexColor("#131313")])]))
    story.append(mt); story.append(Spacer(1,8))

    # Radar
    r_buf = radar_img(m, player_name)
    r_img = RLImage(r_buf, width=7*cm, height=7*cm)
    analysis_p = Paragraph(enc(re.sub(r'\*\*(.*?)\*\*',r'\1',analysis)), s_body)
    ra_block = Table([[r_img, analysis_p]],colWidths=[7.5*cm,9.5*cm])
    ra_block.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                   ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    story.append(HRFlowable(width="100%",thickness=0.5,color=LIGHT,spaceAfter=6))
    story.append(Paragraph("ANÁLISIS AUTOMÁTICO", s_h2))
    story.append(ra_block); story.append(Spacer(1,6))

    # Observations
    story.append(HRFlowable(width="100%",thickness=0.5,color=LIGHT,spaceAfter=6))
    story.append(Paragraph("OBSERVACIONES DEL SCOUT", s_h2))
    obs = observation.strip() if observation else "Sin observaciones registradas."
    story.append(Paragraph(enc(obs), s_obs))

    # Footer
    story.append(Spacer(1,16))
    story.append(HRFlowable(width="100%",thickness=1,color=RED,spaceAfter=4))
    story.append(Paragraph(f"PIP ONE · {datetime.now().strftime('%d/%m/%Y %H:%M')} · {enc(sess['name'])} · {enc(ex_label)}", s_small))

    doc.build(story); buf.seek(0); return buf.read()

# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def sbar(label, value, color="#e63946", max_val=10.0):
    pct = (value/max_val)*100
    return (f'<div class="sbar-wrap"><div class="sbar-label">{label}</div>'
            f'<div class="sbar-bg"><div class="sbar-fill" style="width:{pct:.0f}%;background:{color};"></div></div>'
            f'<div class="sbar-val" style="color:{color};">{value:.1f}</div></div>')

def sbars_for(m):
    cats = [("Técnica","score_technical","#3498db"),
            ("Decisión","score_decision","#9b59b6"),
            ("Ataque","score_offensive","#e63946"),
            ("Defensa","score_defensive","#27ae60")]
    return "".join(sbar(l,m[k],c) for l,k,c in cats)

def ev_count(sid, pid=None):
    if pid: return q("SELECT COUNT(*) c FROM events WHERE session_id=? AND player_id=?",sid,pid,one=True)["c"]
    return q("SELECT COUNT(*) c FROM events WHERE session_id=?",sid,one=True)["c"]

def session_players(sid):
    return [normalise_player(p) for p in q("""SELECT p.* FROM players p
                JOIN session_players sp ON sp.player_id=p.id
                WHERE sp.session_id=? ORDER BY p.name""", sid)]

# ══════════════════════════════════════════════════════════════════════════════
# STATE
# ══════════════════════════════════════════════════════════════════════════════

def init_state():
    for k,v in {"page":"home","active_session":None,"active_player":None,
                "report_session":None,"report_player":None}.items():
        if k not in st.session_state: st.session_state[k] = v
init_state()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

crumb = {"home":"Inicio","session":"Sesión activa","report":"Reporte"}.get(st.session_state.page,"")
if st.session_state.active_session and st.session_state.page=="session":
    crumb += f" · {st.session_state.active_session['name']}"
st.markdown(f'<div class="pip-hdr"><span class="pip-logo">PIP ONE</span><span class="pip-sub">{crumb}</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<div style="font-family:\'Barlow Condensed\',sans-serif;font-weight:900;font-size:1.4rem;color:#e63946;letter-spacing:4px;">PIP ONE</div>', unsafe_allow_html=True)
    st.divider()
    if st.button("Inicio", use_container_width=True):
        st.session_state.page="home"; st.rerun()
    open_sess = [normalise_session(s) for s in q("SELECT * FROM sessions WHERE status='open' ORDER BY created_at DESC")]
    if open_sess:
        st.divider()
        st.markdown('<div class="stitle">Sesiones abiertas</div>', unsafe_allow_html=True)
        for s in open_sess[:5]:
            if st.button(f"▶ {s['name']}", key=f"sb_{s['id']}", use_container_width=True):
                st.session_state.active_session=s; st.session_state.active_player=None
                st.session_state.page="session"; st.rerun()
    closed_sess = [normalise_session(s) for s in q("SELECT * FROM sessions WHERE status='closed' ORDER BY closed_at DESC")]
    if closed_sess:
        st.divider()
        st.markdown('<div class="stitle">Reportes</div>', unsafe_allow_html=True)
        for s in closed_sess[:8]:
            if st.button(f"📋 {s['name']}", key=f"sc_{s['id']}", use_container_width=True):
                pls = session_players(s["id"])
                st.session_state.report_session=s
                st.session_state.report_player=pls[0] if pls else None
                st.session_state.page="report"; st.rerun()
    st.divider()
    n_ev = ev_count(st.session_state.active_session["id"]) if st.session_state.active_session else 0
    st.metric("Eventos sesión", n_ev)
    st.metric("Sesiones totales", len(q("SELECT id FROM sessions")))

# ══════════════════════════════════════════════════════════════════════════════
# ██ PÁGINA: HOME
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.page == "home":
    left, right = st.columns([1.1,1], gap="large")

    with left:
        st.markdown('<div class="stitle">Nueva sesión</div>', unsafe_allow_html=True)

        # TOGGLE PARTIDO / ENTRENAMIENTO
        if "new_cat" not in st.session_state: st.session_state.new_cat = "Partido"
        c1,c2 = st.columns(2)
        with c1:
            partido_bg = "#e63946" if st.session_state.new_cat=="Partido" else "#1a1a1a"
            partido_col = "#fff" if st.session_state.new_cat=="Partido" else "#444"
            if st.button("PARTIDO", use_container_width=True, key="tog_partido"):
                st.session_state.new_cat="Partido"; st.rerun()
        with c2:
            entr_bg = "#2980b9" if st.session_state.new_cat=="Entrenamiento" else "#1a1a1a"
            if st.button("ENTRENAMIENTO", use_container_width=True, key="tog_entr"):
                st.session_state.new_cat="Entrenamiento"; st.rerun()

        cat = st.session_state.new_cat
        if cat == "Partido":
            st.markdown('<div style="background:#0e0203;border:1px solid #3a0810;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:0.82rem;color:#888;">Pesos automáticos por posición. Un GK se valora por paradas, un DEL por goles.</div>', unsafe_allow_html=True)
            exercise_type = "Partido"
        else:
            st.markdown('<div class="stitle" style="margin-top:8px;">Tipo de ejercicio</div>', unsafe_allow_html=True)
            if "new_ex" not in st.session_state: st.session_state.new_ex = EXERCISES[0]
            for ex in EXERCISES:
                ec = EX_COLOR.get(ex,"#888")
                sel = st.session_state.new_ex == ex
                bg = f"background:{ec}18;border:1px solid {ec}55;" if sel else "background:#101010;border:1px solid #1c1c1c;"
                if st.button(f"{'▶ ' if sel else ''}{ex}", key=f"ex_{ex}", use_container_width=True):
                    st.session_state.new_ex=ex; st.rerun()
            exercise_type = st.session_state.new_ex
            desc = EX_DESC.get(exercise_type,"")
            ec = EX_COLOR.get(exercise_type,"#888")
            st.markdown(f'<div style="background:{ec}12;border-left:3px solid {ec};padding:8px 12px;border-radius:0 6px 6px 0;font-size:0.8rem;color:#888;margin-bottom:8px;">{desc}</div>', unsafe_allow_html=True)

        st.divider()
        sess_name  = st.text_input("Nombre de la sesión *", placeholder="Ej: Martes tarde – Grupo A")
        group_name = st.text_input("Grupo / equipo (opcional)", placeholder="Ej: Sub-18 Grupo A")

        if st.button("Crear sesión", type="primary", use_container_width=True):
            if not sess_name.strip():
                st.error("El nombre es obligatorio.")
            else:
                sid = str(uuid.uuid4())[:12]
                insert("INSERT INTO sessions VALUES (?,?,?,?,?,?,?,?)",
                       sid, sess_name.strip(), group_name.strip(),
                       cat, exercise_type, "open",
                       datetime.now().isoformat(), None)
                new_s = normalise_session(q("SELECT * FROM sessions WHERE id=?", sid, one=True))
                st.session_state.active_session=new_s; st.session_state.active_player=None
                st.session_state.page="session"; st.rerun()

    with right:
        st.markdown('<div class="stitle">Sesiones recientes</div>', unsafe_allow_html=True)
        all_sess = [normalise_session(s) for s in q("SELECT * FROM sessions ORDER BY created_at DESC LIMIT 10")]
        if not all_sess:
            st.markdown('<div style="color:#222;font-size:0.88rem;padding:16px;">Sin sesiones todavía.</div>', unsafe_allow_html=True)
        for s in all_sess:
            ex_type      = s.get("exercise_type") or "Partido"
            categoria    = s.get("category") or "Partido"
            ec           = EX_COLOR.get(ex_type, "#e63946")
            cat_color    = "#e63946" if categoria == "Partido" else "#2980b9"
            status_badge = "ABIERTA" if s["status"] == "open" else "CERRADA"
            status_cls   = "badge-green" if s["status"] == "open" else "badge-gray"
            n_ev         = ev_count(s["id"])
            pls          = session_players(s["id"])
            n_pls        = len(pls)
            ex_badge     = (f'<span class="badge" style="background:{ec}22;color:{ec};'
                            f'border:1px solid {ec}44;">{ex_type}</span>')  if categoria == "Entrenamiento" else ""
            html = (
                f'<div class="card">' 
                f'<div style="display:flex;justify-content:space-between;align-items:center;">' 
                f'<div>' 
                f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:700;font-size:1rem;color:#fff;">{s["name"]}</div>' 
                f'<div style="margin-top:4px;display:flex;gap:5px;align-items:center;flex-wrap:wrap;">' 
                f'<span class="badge" style="background:{cat_color};color:#fff;">{categoria}</span>' 
                f'{ex_badge}' 
                f'<span class="badge {status_cls}">{status_badge}</span>' 
                f'<span style="color:#2a2a2a;font-size:0.72rem;">{fmt_dt(s["created_at"])}</span>' 
                f'</div></div>' 
                f'<div style="text-align:right;">' 
                f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:700;font-size:1.4rem;color:#2a2a2a;">{n_ev}</div>' 
                f'<div style="font-size:0.65rem;color:#1a1a1a;letter-spacing:1px;">EVENTOS</div>' 
                f'</div></div>' 
                f'<div style="margin-top:5px;font-size:0.72rem;color:#2a2a2a;">{n_pls} jugadores</div>' 
                f'</div>'
            )
            st.markdown(html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ██ PÁGINA: SESSION
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "session":
    sess = normalise_session(q("SELECT * FROM sessions WHERE id=?", st.session_state.active_session["id"], one=True))
    if not sess: st.error("Sesión no encontrada."); st.stop()
    st.session_state.active_session = sess

    if sess["status"] == "closed":
        st.warning("Esta sesión ya está cerrada.")
        if st.button("Ver reporte"):
            pls = session_players(sess["id"])
            st.session_state.report_session=sess
            st.session_state.report_player=pls[0] if pls else None
            st.session_state.page="report"; st.rerun()
        st.stop()

    ex_key = sess.get("exercise_type") or "Partido"
    ec = EX_COLOR.get(ex_key,"#e63946")
    cat_color = "#e63946" if sess["category"]=="Partido" else "#2980b9"

    # Session header
    ex_badge_sess = (f'<span class="badge" style="background:{ec}22;color:{ec};border:1px solid {ec}44;">{ex_key}</span>') if sess["category"] == "Entrenamiento" else ""
    grp_badge     = f'<span class="badge badge-gray">{sess["group_name"]}</span>' if sess.get("group_name") else ""
    st.markdown(
        f'<div class="card-red" style="margin-bottom:16px;">' 
        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">' 
        f'<div>' 
        f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:900;font-size:1.6rem;color:#fff;">{sess["name"]}</div>' 
        f'<div style="margin-top:5px;display:flex;gap:5px;flex-wrap:wrap;align-items:center;">' 
        f'<span class="badge" style="background:{cat_color};color:#fff;">{sess["category"]}</span>' 
        f'{ex_badge_sess}{grp_badge}' 
        f'<span class="badge badge-green">ABIERTA</span>' 
        f'</div></div>' 
        f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:900;font-size:2rem;color:#2a2a2a;">' 
        f'{ev_count(sess["id"])} <span style="font-size:0.7rem;color:#1a1a1a;letter-spacing:2px;">EVENTOS</span>' 
        f'</div></div></div>',
        unsafe_allow_html=True)

    col_pl, col_cap, col_dash = st.columns([1, 1.3, 1.5], gap="medium")

    # ── PLAYERS ──────────────────────────────────────────────────────────────
    with col_pl:
        st.markdown('<div class="stitle">Jugadores</div>', unsafe_allow_html=True)
        with st.expander("Añadir jugador"):
            new_pname = st.text_input("Nombre", key="new_pn", label_visibility="collapsed", placeholder="Nombre del jugador")
            new_ppos  = st.radio("Posición", POSITIONS,
                                  format_func=lambda p: f"{p} · {POS_NAMES[p]}",
                                  horizontal=True, key="new_pp", label_visibility="collapsed")
            if st.button("Añadir a sesión", use_container_width=True, key="btn_addp"):
                name = new_pname.strip()
                if name:
                    existing = q("SELECT id FROM players WHERE name=?", name, one=True)
                    if existing:
                        pid = existing["id"]
                        q("UPDATE players SET position=? WHERE id=?", new_ppos, pid, write=True)
                    else:
                        pid = str(uuid.uuid4())[:12]
                        insert("INSERT INTO players VALUES (?,?,?,?)", pid, name, new_ppos, datetime.now().isoformat())
                    insert("INSERT OR IGNORE INTO session_players VALUES (?,?)", sess["id"], pid)
                    pls = session_players(sess["id"])
                    if not st.session_state.active_player: st.session_state.active_player = pls[0]
                    st.rerun()

        pls = session_players(sess["id"])
        if not pls:
            st.markdown('<div style="color:#222;font-size:0.82rem;padding:10px;">Añade jugadores para empezar.</div>', unsafe_allow_html=True)
        else:
            for p in pls:
                ia = st.session_state.active_player and st.session_state.active_player["id"]==p["id"]
                ne = ev_count(sess["id"], p["id"])
                bg = "#0e0203" if ia else "#080808"
                bl = "2px solid #e63946" if ia else "1px solid #181818"
                pc = pos_color(p["position"])
                if st.button(f"{'▶ ' if ia else ''}{p['name']}  [{p['position']}]  ({ne})",
                             key=f"selp_{p['id']}", use_container_width=True):
                    st.session_state.active_player=p; st.rerun()
                st.markdown(f'<div style="background:{bg};border-left:{bl};border-radius:0 0 5px 5px;height:3px;margin-top:-12px;margin-bottom:5px;"></div>', unsafe_allow_html=True)

        # Event log
        st.divider()
        st.markdown('<div class="stitle">Últimos eventos</div>', unsafe_allow_html=True)
        all_evs = q("SELECT * FROM events WHERE session_id=? ORDER BY created_at DESC LIMIT 12", sess["id"])
        p_map = {p["id"]:p for p in pls}
        if all_evs:
            for e in all_evs:
                ei = ALL_EVENTS.get(e["event_type"],{"label":e["event_type"],"color":"#888"})
                pn = p_map.get(e["player_id"],{}).get("name","?")
                pp = p_map.get(e["player_id"],{}).get("position","")
                pc_ = pos_color(pp)
                ts = e.get("ts","") or ""
                st.markdown(f'<div class="elog">'
                            f'<div style="width:6px;height:6px;border-radius:50%;background:{ei["color"]};flex-shrink:0;"></div>'
                            f'<div style="color:#2a2a2a;font-size:0.68rem;width:38px;">{ts}</div>'
                            f'<div style="color:{pc_};font-size:0.78rem;width:22px;">{pp}</div>'
                            f'<div style="color:#aaa;flex:1;font-size:0.8rem;">{pn}</div>'
                            f'<div style="color:{ei["color"]};font-size:0.75rem;">{ei["label"]}</div>'
                            f'</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#1a1a1a;font-size:0.8rem;padding:6px;">Sin eventos.</div>', unsafe_allow_html=True)

        ap = st.session_state.active_player
        if ap and all_evs:
            if st.button("↩ Deshacer último", use_container_width=True):
                r = q("SELECT id FROM events WHERE session_id=? AND player_id=? ORDER BY created_at DESC LIMIT 1",
                       sess["id"], ap["id"], one=True)
                if r: q("DELETE FROM events WHERE id=?", r["id"], write=True)
                st.rerun()

        # Close
        st.divider()
        st.markdown('<div class="stitle" style="color:#e63946;">Cerrar sesión</div>', unsafe_allow_html=True)
        n_total = ev_count(sess["id"])
        st.markdown(f'<div style="font-size:0.8rem;color:#444;margin-bottom:8px;">{n_total} eventos · {len(pls)} jugadores</div>', unsafe_allow_html=True)
        if st.button("CERRAR Y CALCULAR MÉTRICAS", type="primary", use_container_width=True):
            if n_total == 0: st.error("Sin eventos registrados.")
            else:
                close_and_compute(sess["id"], ex_key)
                closed = normalise_session(q("SELECT * FROM sessions WHERE id=?", sess["id"], one=True))
                pls2 = session_players(sess["id"])
                st.session_state.report_session=closed
                st.session_state.report_player=pls2[0] if pls2 else None
                st.session_state.active_session=None
                st.session_state.page="report"; st.rerun()

    # ── EVENT CAPTURE ─────────────────────────────────────────────────────────
    with col_cap:
        ap = st.session_state.active_player
        if not ap:
            st.markdown('<div style="color:#1a1a1a;padding:40px;text-align:center;font-family:\'Barlow Condensed\',sans-serif;font-size:1.1rem;">Selecciona o añade un jugador</div>', unsafe_allow_html=True)
        else:
            is_gk = ap["position"] == "GK"
            pc = pos_color(ap["position"])
            ne_ap = ev_count(sess["id"], ap["id"])
            pos_badge_html = f'<span class="badge" style="background:{pc}22;color:{pc};border:1px solid {pc}44;">{ap["position"]} · {POS_NAMES[ap["position"]]}</span>'

            st.markdown(f'<div class="card-red" style="text-align:center;margin-bottom:14px;">'
                        f'<div style="font-size:0.6rem;color:#444;letter-spacing:2px;text-transform:uppercase;">JUGADOR ACTIVO</div>'
                        f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-weight:900;font-size:2rem;color:#fff;margin-top:2px;">{ap["name"]}</div>'
                        f'<div style="margin-top:5px;">{pos_badge_html}'
                        f'<span style="font-size:0.72rem;color:#333;margin-left:8px;">{ne_ap} eventos</span></div></div>',
                        unsafe_allow_html=True)

            if is_gk:
                st.markdown('<div class="stitle" style="color:#f39c12;">Panel portero</div>', unsafe_allow_html=True)
                layout = GK_LAYOUT
                ev_dict = GK_EVENTS
            else:
                st.markdown('<div class="stitle">Panel de acciones</div>', unsafe_allow_html=True)
                layout = FIELD_LAYOUT
                ev_dict = FIELD_EVENTS

            kb = ev_count(sess["id"])
            for ev_a, ev_b in layout:
                c1, c2 = st.columns(2)
                with c1:
                    ea = ev_dict[ev_a]
                    if st.button(ea["label"], key=f"ea_{ev_a}_{kb}", use_container_width=True):
                        insert("INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                               str(uuid.uuid4())[:16], sess["id"], ap["id"],
                               ev_a, ea["cat"], datetime.now().strftime("%H:%M:%S"),
                               datetime.now().isoformat())
                        st.rerun()
                with c2:
                    if ev_b:
                        eb = ev_dict[ev_b]
                        if st.button(eb["label"], key=f"eb_{ev_b}_{kb}", use_container_width=True):
                            insert("INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                                   str(uuid.uuid4())[:16], sess["id"], ap["id"],
                                   ev_b, eb["cat"], datetime.now().strftime("%H:%M:%S"),
                                   datetime.now().isoformat())
                            st.rerun()

            evs_ap = q("SELECT * FROM events WHERE session_id=? AND player_id=?", sess["id"], ap["id"])
            if evs_ap:
                st.divider()
                cat_c = {}
                for e in evs_ap: cat_c[e["event_cat"]] = cat_c.get(e["event_cat"],0)+1
                mcols = st.columns(4)
                for col_,(cat,lbl) in zip(mcols,[("technical","Téc"),("decision","Dec"),("offensive","Ata"),("defensive","Def")]):
                    with col_: st.metric(lbl, cat_c.get(cat,0))

    # ── LIVE DASHBOARD ────────────────────────────────────────────────────────
    with col_dash:
        ap = st.session_state.active_player
        st.markdown('<div class="stitle">Métricas en vivo</div>', unsafe_allow_html=True)
        if ap:
            evs_ap = q("SELECT * FROM events WHERE session_id=? AND player_id=?", sess["id"], ap["id"])
            m = compute_metrics(evs_ap, ap["position"], ex_key)
            if m:
                pc = pos_color(ap["position"])
                st.markdown(f'<div style="display:flex;align-items:flex-end;gap:12px;margin-bottom:12px;">'
                            f'<div><div style="font-family:\'Barlow Condensed\',sans-serif;font-weight:900;font-size:5rem;color:{pc};line-height:1;">{m["rating"]}</div>'
                            f'<div style="font-size:0.6rem;color:#333;letter-spacing:2px;">RATING LIVE</div></div>'
                            f'<div style="flex:1;padding-bottom:4px;">'
                            f'<div style="font-size:0.7rem;color:#2a2a2a;margin-bottom:6px;">{m["total_events"]} eventos · {m["participation_rate"]:.0f}% part.</div>'
                            f'{"".join(sbar(CAT_LABELS[k],m[f"score_{k}"],{"technical":"#3498db","decision":"#9b59b6","offensive":"#e63946","defensive":"#27ae60"}[k]) for k in ["technical","decision","offensive","defensive"])}'
                            f'</div></div>', unsafe_allow_html=True)
                r_buf = radar_img(m, ap["name"])
                st.image(r_buf, use_container_width=True)

                if ap["position"] == "GK":
                    mc1,mc2 = st.columns(2)
                    with mc1:
                        st.metric("Paradas",    m["total_saves"])
                        st.metric("Efectividad %", f'{m["save_rate"]:.0f}%')
                    with mc2:
                        st.metric("Salidas %",  f'{m["exit_rate"]:.0f}%')
                        st.metric("Pase corto %", f'{m["short_pass_acc"]:.0f}%')
                else:
                    mc1,mc2 = st.columns(2)
                    with mc1:
                        st.metric("Pase %",    f'{m["pass_accuracy"]:.0f}%')
                        st.metric("Decisión %",f'{m["decision_score"]:.0f}%')
                        st.metric("Ataque",    m["offensive_actions"])
                    with mc2:
                        st.metric("Control %", f'{m["control_accuracy"]:.0f}%')
                        st.metric("Defensa",   m["defensive_actions"])
                        st.metric("Goles",     m["goals"])
            else:
                st.markdown('<div style="color:#1a1a1a;padding:20px;text-align:center;">Captura eventos para ver métricas.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ██ PÁGINA: REPORT
# ══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "report":
    rsess = normalise_session(q("SELECT * FROM sessions WHERE id=?", st.session_state.report_session["id"], one=True))
    pls = session_players(rsess["id"])
    if not pls: st.warning("Sin jugadores."); st.stop()

    rp = st.session_state.report_player
    ex_key = rsess.get("exercise_type") or "Partido"
    ec = EX_COLOR.get(ex_key,"#e63946")
    cat_color = "#e63946" if rsess["category"]=="Partido" else "#2980b9"

    # Session header
    ex_badge_rep = (f'<span class="badge" style="background:{ec}22;color:{ec};border:1px solid {ec}44;">{ex_key}</span>') if rsess["category"] == "Entrenamiento" else ""
    st.markdown(
        f'<div class="card-red" style="margin-bottom:16px;">' 
        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">' 
        f'<div>' 
        f'<div style="font-family:Barlow Condensed,sans-serif;font-weight:900;font-size:1.5rem;color:#fff;">{rsess["name"]}</div>' 
        f'<div style="margin-top:4px;display:flex;gap:5px;flex-wrap:wrap;align-items:center;">' 
        f'<span class="badge" style="background:{cat_color};color:#fff;">{rsess["category"]}</span>' 
        f'{ex_badge_rep}' 
        f'<span class="badge badge-gray">{fmt_dt(rsess["created_at"])}</span>' 
        f'<span class="badge badge-gray">{len(pls)} jugadores</span>' 
        f'</div></div>' 
        f'<span class="badge badge-gray">{fmt_dt(rsess.get("closed_at",""))}</span>' 
        f'</div></div>',
        unsafe_allow_html=True)

    # Player selector
    pl_names = [p["name"] for p in pls]
    sel_name = st.selectbox("Jugador", pl_names,
        index=pl_names.index(rp["name"]) if rp and rp["name"] in pl_names else 0,
        label_visibility="collapsed")
    rp = next(p for p in pls if p["name"]==sel_name)
    st.session_state.report_player = rp

    m = q("SELECT * FROM player_metrics WHERE session_id=? AND player_id=?",
          rsess["id"], rp["id"], one=True)

    if not m:
        st.warning(f"Sin métricas para {rp['name']}.")
        if st.button("Calcular ahora"):
            evs = q("SELECT * FROM events WHERE session_id=? AND player_id=?", rsess["id"], rp["id"])
            mx = compute_metrics(evs, rp["position"], ex_key)
            if mx:
                c = get_conn()
                c.execute("DELETE FROM player_metrics WHERE session_id=? AND player_id=?", (rsess["id"],rp["id"]))
                c.execute("""INSERT INTO player_metrics VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (str(uuid.uuid4())[:12], rsess["id"], rp["id"],
                     rp["position"], ex_key,
                     mx["w_technical"],mx["w_decision"],mx["w_offensive"],mx["w_defensive"],
                     mx["total_events"],mx["save_rate"],mx["exit_rate"],
                     mx["short_pass_acc"],mx["long_pass_acc"],
                     mx["total_saves"],mx["great_saves"],
                     mx["pass_accuracy"],mx["control_accuracy"],
                     mx["decision_score"],mx["dribble_accuracy"],mx["duel_accuracy"],
                     mx["total_shots"],mx["shots_on_target"],mx["goals"],
                     mx["offensive_actions"],mx["defensive_actions"],
                     mx["recoveries"],mx["interceptions"],mx["errors"],
                     mx["participation_rate"],
                     mx["score_technical"],mx["score_decision"],
                     mx["score_offensive"],mx["score_defensive"],
                     mx["rating"],datetime.now().isoformat()))
                c.commit(); c.close(); st.rerun()
        st.stop()

    m = dict(m)
    pc = pos_color(m["position"])
    atxt = analysis_text(rp["name"], m, ex_key)

    rc1, rc2 = st.columns([1.6, 1], gap="large")

    with rc1:
        # Player card
        pos_label = POS_NAMES.get(m["position"], m["position"])
        w_info = (f'Téc {m["w_technical"]*100:.0f}% · Dec {m["w_decision"]*100:.0f}% · '
                  f'Ata {m["w_offensive"]*100:.0f}% · Def {m["w_defensive"]*100:.0f}%')
        st.markdown(f"""
        <div class="card-red">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <div style="font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:2.4rem;color:#fff;line-height:1;">{rp['name']}</div>
              <div style="margin-top:6px;">
                <span class="badge" style="background:{pc}22;color:{pc};border:1px solid {pc}44;">{m['position']} · {pos_label}</span>
              </div>
              <div style="font-size:0.7rem;color:#2a2a2a;margin-top:6px;">Pesos: {w_info}</div>
            </div>
            <div style="text-align:center;margin-left:16px;">
              <div style="font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:5rem;color:{pc};line-height:1;">{m['rating']}</div>
              <div style="font-size:0.6rem;color:#333;letter-spacing:2px;">RATING</div>
            </div>
          </div>
          <div style="margin-top:14px;">
            {"".join(sbar(CAT_LABELS[k],m[f"score_{k}"],{"technical":"#3498db","decision":"#9b59b6","offensive":"#e63946","defensive":"#27ae60"}[k]) for k in ["technical","decision","offensive","defensive"])}
          </div>
        </div>""", unsafe_allow_html=True)

        # Metrics grid
        st.markdown('<div class="stitle">Métricas detalladas</div>', unsafe_allow_html=True)
        if m["position"] == "GK":
            mg = st.columns(4)
            for col_, (lbl,val) in zip(mg,[("Paradas",m["total_saves"]),("P. difíciles",m["great_saves"]),
                                          ("Efectividad",f'{m["save_rate"]:.0f}%'),("Salidas",f'{m["exit_rate"]:.0f}%')]):
                with col_: st.metric(lbl,val)
            mg2 = st.columns(4)
            for col_,(lbl,val) in zip(mg2,[("Pase corto",f'{m["short_pass_acc"]:.0f}%'),
                                           ("Pase largo",f'{m["long_pass_acc"]:.0f}%'),
                                           ("Errores",m["errors"]),("Participación",f'{m["participation_rate"]:.0f}%')]):
                with col_: st.metric(lbl,val)
        else:
            mg = st.columns(4)
            for col_,(lbl,val) in zip(mg,[("Pase %",f'{m["pass_accuracy"]:.0f}%'),("Control %",f'{m["control_accuracy"]:.0f}%'),
                                         ("Decisión %",f'{m["decision_score"]:.0f}%'),("Regate %",f'{m["dribble_accuracy"]:.0f}%')]):
                with col_: st.metric(lbl,val)
            mg2 = st.columns(4)
            for col_,(lbl,val) in zip(mg2,[("Duelo %",f'{m["duel_accuracy"]:.0f}%'),("Goles",m["goals"]),
                                          ("Recuper.",m["recoveries"]),("Errores",m["errors"])]):
                with col_: st.metric(lbl,val)

        # Analysis
        st.divider()
        st.markdown('<div class="stitle">Análisis automático</div>', unsafe_allow_html=True)
        formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#e63946;">\1</strong>', atxt)
        st.markdown(f'<div class="analysis-block">{formatted}</div>', unsafe_allow_html=True)

        # Fortalezas
        st.divider()
        cats_sc = {"Técnica":m["score_technical"],"Decisión":m["score_decision"],
                   "Ataque":m["score_offensive"],"Defensa":m["score_defensive"]}
        sorted_cats = sorted(cats_sc.items(), key=lambda x:x[1], reverse=True)
        sw1,sw2 = st.columns(2)
        cat_colors = {"Técnica":"#3498db","Decisión":"#9b59b6","Ataque":"#e63946","Defensa":"#27ae60"}
        with sw1:
            st.markdown('<div class="stitle">Fortalezas</div>', unsafe_allow_html=True)
            for cat,val in sorted_cats[:2]:
                cc = cat_colors[cat]
                st.markdown(f'<div style="display:flex;justify-content:space-between;padding:6px 10px;background:#0a0a0a;border:1px solid #181818;border-left:3px solid {cc};border-radius:0 5px 5px 0;margin-bottom:4px;">'
                            f'<span style="color:#ccc;font-size:0.85rem;">{cat}</span>'
                            f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;color:{cc};">{val:.1f}</span>'
                            f'</div>', unsafe_allow_html=True)
        with sw2:
            st.markdown('<div class="stitle">A mejorar</div>', unsafe_allow_html=True)
            for cat,val in sorted_cats[2:]:
                cc = cat_colors[cat]
                st.markdown(f'<div style="display:flex;justify-content:space-between;padding:6px 10px;background:#0a0a0a;border:1px solid #181818;border-left:3px solid {cc}44;border-radius:0 5px 5px 0;margin-bottom:4px;">'
                            f'<span style="color:#666;font-size:0.85rem;">{cat}</span>'
                            f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;color:{cc}88;">{val:.1f}</span>'
                            f'</div>', unsafe_allow_html=True)

        # Scout observations
        st.divider()
        st.markdown('<div class="stitle">Observaciones del scout</div>', unsafe_allow_html=True)
        obs_row = q("SELECT * FROM scout_observations WHERE session_id=? AND player_id=?",
                    rsess["id"], rp["id"], one=True)
        obs_current = obs_row["observation"] if obs_row else ""
        obs_input = st.text_area("", value=obs_current, height=110,
            placeholder="Observaciones, contexto, áreas de trabajo...",
            label_visibility="collapsed", key=f"obs_{rsess['id']}_{rp['id']}")
        if st.button("Guardar observaciones", use_container_width=True):
            if obs_row:
                q("UPDATE scout_observations SET observation=?, updated_at=? WHERE session_id=? AND player_id=?",
                  obs_input, datetime.now().isoformat(), rsess["id"], rp["id"], write=True)
            else:
                insert("INSERT INTO scout_observations VALUES (?,?,?,?,?)",
                       str(uuid.uuid4())[:12], rsess["id"], rp["id"],
                       obs_input, datetime.now().isoformat())
            st.success("Guardado ✓")

    with rc2:
        # Radar
        st.markdown('<div class="stitle">Perfil de rendimiento</div>', unsafe_allow_html=True)
        st.image(radar_img(m, rp["name"]), use_container_width=True)

        # Bar chart
        st.markdown('<div class="stitle">Categorías</div>', unsafe_allow_html=True)
        st.image(bar_img(m), use_container_width=True)

        # Quick stats
        st.divider()
        st.markdown('<div class="stitle">Resumen rápido</div>', unsafe_allow_html=True)
        if m["position"] == "GK":
            quick = [("Total eventos",m["total_events"]),("Paradas",m["total_saves"]),
                     ("P. difíciles",m["great_saves"]),("Acc. defensivas",m["defensive_actions"])]
        else:
            quick = [("Total eventos",m["total_events"]),("Acc. ofensivas",m["offensive_actions"]),
                     ("Acc. defensivas",m["defensive_actions"]),("Tiros puerta",m["shots_on_target"]),
                     ("Recuperaciones",m["recoveries"])]
        for lbl,val in quick:
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #181818;">'
                        f'<span style="font-size:0.8rem;color:#333;">{lbl}</span>'
                        f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;color:{pc};">{val}</span>'
                        f'</div>', unsafe_allow_html=True)

        # Ranking
        if len(pls) > 1:
            st.divider()
            st.markdown('<div class="stitle">Ranking sesión</div>', unsafe_allow_html=True)
            medals = {1:"🥇",2:"🥈",3:"🥉"}
            ratings = []
            for p in pls:
                pm = q("SELECT rating, position FROM player_metrics WHERE session_id=? AND player_id=?",
                       rsess["id"], p["id"], one=True)
                if pm: ratings.append((p["name"], pm["rating"], pm["position"]))
            ratings.sort(key=lambda x:x[1], reverse=True)
            for i,(pname,prat,ppos) in enumerate(ratings,1):
                is_sel = pname==rp["name"]
                bg = "#0e0203" if is_sel else "#080808"
                bl = "1px solid #e63946" if is_sel else "1px solid #181818"
                ppc = pos_color(ppos)
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;background:{bg};border:{bl};border-radius:6px;padding:6px 10px;margin-bottom:4px;">'
                            f'<div style="display:flex;align-items:center;gap:6px;">'
                            f'<span style="font-size:1rem;">{medals.get(i,"")}</span>'
                            f'<span style="font-size:0.82rem;color:{"#fff" if is_sel else "#888"};">{pname}</span>'
                            f'<span style="font-size:0.68rem;color:{ppc};">[{ppos}]</span>'
                            f'</div>'
                            f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;color:{ppc};font-size:1.1rem;">{prat}</span>'
                            f'</div>', unsafe_allow_html=True)

        # PDF
        st.divider()
        obs_saved = q("SELECT * FROM scout_observations WHERE session_id=? AND player_id=?",
                      rsess["id"], rp["id"], one=True)
        obs_text = obs_saved["observation"] if obs_saved else ""
        try:
            pdf_bytes = make_pdf(rp["name"], rsess, m, atxt, obs_text)
            st.download_button(
                label="DESCARGAR PDF",
                data=pdf_bytes,
                file_name=f"pip_{rp['name'].replace(' ','_')}_{rsess['id']}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
        except Exception as e:
            st.error(f"Error PDF: {e}")

        # Navigate other players
        if len(pls) > 1:
            st.divider()
            st.markdown('<div class="stitle">Otros jugadores</div>', unsafe_allow_html=True)
            for p in pls:
                if p["id"] != rp["id"]:
                    pm = q("SELECT rating FROM player_metrics WHERE session_id=? AND player_id=?",
                           rsess["id"], p["id"], one=True)
                    r_label = f"{pm['rating']}" if pm else "—"
                    ppc = pos_color(p["position"])
                    if st.button(f"{p['name']}  [{p['position']}]  {r_label}",
                                 key=f"nav_{p['id']}", use_container_width=True):
                        st.session_state.report_player=p; st.rerun()
