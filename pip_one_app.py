import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import uuid
import os

st.set_page_config(page_title="PIP ONE", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════════════════
# ESTILOS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;900&family=Barlow:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Barlow',sans-serif;background:#0d0d0d;color:#f0f0f0;}
.stApp{background:#0d0d0d;}
section[data-testid="stSidebar"]{background-color:#111!important;border-right:1px solid #1e1e1e;}
.pip-header{background:linear-gradient(135deg,#111,#0d0d0d);border-bottom:3px solid #e63946;padding:14px 24px;margin:-1rem -1rem 1.5rem -1rem;}
.pip-logo{font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:2rem;color:#e63946;letter-spacing:4px;display:inline;}
.pip-subtitle{font-family:'Barlow Condensed',sans-serif;font-weight:600;font-size:0.9rem;color:#555;letter-spacing:3px;text-transform:uppercase;margin-left:16px;}
.card{background:#161616;border:1px solid #222;border-radius:8px;padding:16px;margin-bottom:12px;}
.card-red{background:#160508;border:1px solid #e63946;border-radius:8px;padding:16px;margin-bottom:12px;}
.badge{display:inline-block;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:0.7rem;letter-spacing:2px;padding:3px 10px;border-radius:4px;text-transform:uppercase;}
.badge-red{background:#e63946;color:#fff;}
.badge-gray{background:#1e1e1e;color:#777;}
.rating-xl{font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:3.8rem;color:#e63946;line-height:1;}
.rating-lg{font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:2.2rem;color:#e63946;line-height:1;}
.rating-label{font-size:0.65rem;color:#555;letter-spacing:2px;text-transform:uppercase;}
.sbar-wrap{display:flex;align-items:center;gap:8px;margin-bottom:5px;}
.sbar-label{font-size:0.76rem;color:#888;width:74px;text-align:right;}
.sbar-bg{flex:1;background:#1e1e1e;border-radius:3px;height:7px;overflow:hidden;}
.sbar-fill{height:7px;border-radius:3px;background:linear-gradient(90deg,#e63946,#ff6b6b);}
.sbar-val{font-family:'Barlow Condensed',sans-serif;font-weight:700;color:#e63946;font-size:0.9rem;width:30px;}
.stitle{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:0.65rem;letter-spacing:3px;color:#444;text-transform:uppercase;margin-bottom:8px;padding-bottom:4px;border-bottom:1px solid #1e1e1e;}
.elog{display:flex;align-items:center;gap:7px;padding:4px 8px;border-radius:4px;background:#111;margin-bottom:3px;font-size:0.8rem;}
.stat-pill{display:inline-flex;flex-direction:column;align-items:center;background:#161616;border:1px solid #222;border-radius:8px;padding:8px 14px;margin:4px;min-width:70px;}
.stat-pill-val{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:1.3rem;color:#e63946;line-height:1;}
.stat-pill-label{font-size:0.65rem;color:#555;text-align:center;margin-top:2px;}
.ficha-header{background:linear-gradient(135deg,#1a0507,#110203);border:1px solid #3a1015;border-radius:10px;padding:20px;margin-bottom:16px;}
.ficha-nombre{font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:2rem;color:#fff;line-height:1.1;}
.ficha-equipo{font-size:0.85rem;color:#888;margin-top:4px;}
[data-testid="metric-container"]{background:#161616!important;border:1px solid #222!important;border-radius:8px!important;padding:12px!important;}
[data-testid="metric-container"] label{color:#666!important;font-size:0.72rem!important;letter-spacing:1px!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#e63946!important;font-family:'Barlow Condensed',sans-serif!important;font-size:1.5rem!important;font-weight:700!important;}
[data-testid="stTabs"] [role="tab"]{font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;letter-spacing:2px!important;font-size:0.85rem!important;color:#444!important;text-transform:uppercase!important;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{color:#e63946!important;border-bottom:2px solid #e63946!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════
SESSION_TYPES  = {1:"Technical",2:"Decision",3:"Offensive",4:"Defensive",5:"Physical",6:"Game"}
SESSION_COLORS = {"Technical":"#3498db","Decision":"#9b59b6","Offensive":"#e63946","Defensive":"#27ae60","Physical":"#f39c12","Game":"#1abc9c"}
SESSION_WEIGHTS = {
    "Technical": {"technical":0.50,"decision":0.20,"offensive":0.15,"defensive":0.15},
    "Decision":  {"technical":0.20,"decision":0.50,"offensive":0.15,"defensive":0.15},
    "Offensive": {"technical":0.15,"decision":0.20,"offensive":0.50,"defensive":0.15},
    "Defensive": {"technical":0.15,"decision":0.20,"offensive":0.15,"defensive":0.50},
    "Physical":  {"technical":0.20,"decision":0.20,"offensive":0.30,"defensive":0.30},
    "Game":      {"technical":0.20,"decision":0.25,"offensive":0.30,"defensive":0.25},
}
CAT_LABELS = {"technical":"Técnica","decision":"Decisión","offensive":"Ataque","defensive":"Defensa"}
RADAR_CATS = ["Técnica","Decisión","Ataque","Defensa","Participación"]
EVENTS = {
    "pass_success":     {"label":"Pase ✓",      "color":"#27ae60","cat":"technical"},
    "pass_fail":        {"label":"Pase ✗",      "color":"#e74c3c","cat":"technical"},
    "control_success":  {"label":"Control ✓",   "color":"#2980b9","cat":"technical"},
    "control_fail":     {"label":"Control ✗",   "color":"#c0392b","cat":"technical"},
    "decision_correct": {"label":"Decisión ✓",  "color":"#1abc9c","cat":"decision"},
    "decision_wrong":   {"label":"Decisión ✗",  "color":"#e74c3c","cat":"decision"},
    "shot":             {"label":"Tiro",         "color":"#f39c12","cat":"offensive"},
    "shot_on_target":   {"label":"Tiro Puerta", "color":"#e67e22","cat":"offensive"},
    "goal":             {"label":"Gol ⚽",       "color":"#f1c40f","cat":"offensive"},
    "dribble_success":  {"label":"Regate ✓",    "color":"#27ae60","cat":"offensive"},
    "dribble_fail":     {"label":"Regate ✗",    "color":"#e74c3c","cat":"offensive"},
    "recovery":         {"label":"Recuperación","color":"#8e44ad","cat":"defensive"},
    "interception":     {"label":"Intercepción","color":"#9b59b6","cat":"defensive"},
    "duel_won":         {"label":"Duelo ✓",     "color":"#27ae60","cat":"defensive"},
    "duel_lost":        {"label":"Duelo ✗",     "color":"#e74c3c","cat":"defensive"},
    "error":            {"label":"Error",        "color":"#c0392b","cat":"general"},
}
EVENT_LAYOUT = [
    ("pass_success","pass_fail"),("control_success","control_fail"),
    ("decision_correct","decision_wrong"),("shot","shot_on_target"),
    ("goal","dribble_success"),("dribble_fail","recovery"),
    ("interception","duel_won"),("duel_lost","error"),
]
POS_LABELS = {"G":"Portero","D":"Defensa","M":"Centrocampista","F":"Delantero"}

# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════
def fix_dec(val):
    return val.replace(",",".") if isinstance(val,str) else val

@st.cache_data
def load_data():
    base = "/mnt/user-data/uploads/"
    def load_csv(f):
        p = base+f
        if not os.path.exists(p): return pd.DataFrame()
        df = pd.read_csv(p,sep=";",skiprows=1,encoding="utf-8-sig",low_memory=False)
        for col in df.columns:
            df[col] = df[col].apply(fix_dec)
        return df

    dp = load_csv("1rfef_partidos_2526.csv")
    dj = load_csv("1rfef_jugadores_2526.csv")
    num_p = ['goles','tiros_totales','tiros_a_puerta','xG','xA','pases_totales','pases_precisos',
             'pases_campo_rival','pases_largos_totales','pases_largos_precisos',
             'entradas_totales','entradas_ganadas','intercepciones','despejes',
             'duelos_ganados','duelos_perdidos','duelos_aereos_ganados','duelos_aereos_perdidos',
             'regates_intentados','regates_exitosos','toques_fallidos','faltas_recibidas',
             'faltas_cometidas','recuperaciones','perdidas','asistencias','paradas_totales',
             'bloqueos_def','centros_totales','centros_precisos','minutos_jugados','rating_sofascore']
    for c in num_p:
        if c in dp.columns: dp[c] = pd.to_numeric(dp[c],errors='coerce')
    return dp, dj

df_partidos, df_jugadores = load_data()

@st.cache_data
def build_profiles():
    if df_partidos.empty: return pd.DataFrame()
    df = df_partidos.copy()
    valid = {c:'sum' for c in ['goles','tiros_totales','tiros_a_puerta','xG','xA','pases_totales',
             'pases_precisos','pases_campo_rival','entradas_totales','entradas_ganadas','intercepciones',
             'despejes','duelos_ganados','duelos_perdidos','regates_intentados','regates_exitosos',
             'toques_fallidos','faltas_recibidas','recuperaciones','perdidas','asistencias',
             'paradas_totales','bloqueos_def','minutos_jugados'] if c in df.columns}
    valid['rating_sofascore'] = 'mean'
    meta = df.groupby('jugador').agg({'equipo':'last','posicion':'last'}).reset_index()
    stats = df.groupby('jugador').agg(valid).reset_index()
    stats['partidos'] = df.groupby('jugador').size().values
    prof = meta.merge(stats, on='jugador')
    prof = prof[prof['minutos_jugados'] >= 90].copy()
    mins = prof['minutos_jugados'].replace(0,np.nan)

    def s(c): return prof[c] if c in prof.columns else pd.Series(0,index=prof.index)

    prof['pass_acc']   = np.where(s('pases_totales')>0, s('pases_precisos')/s('pases_totales'), 0)
    prof['entry_acc']  = np.where(s('entradas_totales')>0, s('entradas_ganadas')/s('entradas_totales'), 0)
    prof['duel_acc']   = np.where(s('duelos_ganados')+s('duelos_perdidos')>0,
                                   s('duelos_ganados')/(s('duelos_ganados')+s('duelos_perdidos')), 0)
    prof['drb_acc']    = np.where(s('regates_intentados')>0, s('regates_exitosos')/s('regates_intentados'), 0)
    prof['ctrl_err90'] = s('toques_fallidos') / (mins/90)
    prof['shots_90']   = s('tiros_totales')  / (mins/90)
    prof['sot_90']     = s('tiros_a_puerta') / (mins/90)
    prof['goals_90']   = s('goles')          / (mins/90)
    prof['xg_90']      = s('xG')             / (mins/90)
    prof['xa_90']      = s('xA')             / (mins/90)
    prof['rec_90']     = s('recuperaciones') / (mins/90)
    prof['int_90']     = s('intercepciones') / (mins/90)
    prof['dsp_90']     = s('despejes')       / (mins/90)
    prof['pass_rv90']  = s('pases_campo_rival')/(mins/90)
    prof['assist_90']  = s('asistencias')    / (mins/90)

    ctrl_s = np.clip(1 - prof['ctrl_err90']/4, 0, 1)
    prof['score_technical'] = (prof['pass_acc']*0.6 + ctrl_s*0.4)*10
    prof['score_decision']  = (prof['duel_acc']*0.4 + prof['entry_acc']*0.3 + prof['pass_acc']*0.3)*10
    sn = np.clip(prof['shots_90']/4,0,1)
    sr = np.where(prof['shots_90']>0, prof['sot_90']/prof['shots_90'], 0)
    gn = np.clip(prof['goals_90']/0.5,0,1)
    prof['score_offensive'] = (sn*0.3 + sr*0.25 + gn*0.25 + prof['drb_acc']*0.2)*10
    rn = np.clip(prof['rec_90']/8,0,1)
    in_ = np.clip(prof['int_90']/4,0,1)
    dn = np.clip(prof['dsp_90']/5,0,1)
    prof['score_defensive'] = (rn*0.35 + in_*0.30 + prof['duel_acc']*0.25 + dn*0.10)*10
    prof['participation_rate'] = np.clip(prof['minutos_jugados']/2700*100,0,100)
    w = SESSION_WEIGHTS["Game"]
    prof['pip_rating'] = (prof['score_technical']*w['technical'] + prof['score_decision']*w['decision'] +
                          prof['score_offensive']*w['offensive'] + prof['score_defensive']*w['defensive']).round(1)
    for c in ['score_technical','score_decision','score_offensive','score_defensive','pass_acc','duel_acc']:
        prof[c] = prof[c].round(2)
    prof['rating_sofascore'] = pd.to_numeric(prof['rating_sofascore'].apply(fix_dec), errors='coerce')
    return prof.reset_index(drop=True)

rfef_profiles = build_profiles()

# ══════════════════════════════════════════════════════════════════════════════
# MÉTRICAS PIP (desde eventos)
# ══════════════════════════════════════════════════════════════════════════════
def compute_pip_metrics(evs, snum=None):
    if not evs: return None
    def cnt(k): return sum(1 for e in evs if e["event_type"]==k)
    ps,pf=cnt("pass_success"),cnt("pass_fail")
    cs,cf=cnt("control_success"),cnt("control_fail")
    dc,dw=cnt("decision_correct"),cnt("decision_wrong")
    sh,sot=cnt("shot"),cnt("shot_on_target")
    gl=cnt("goal"); drs,drf=cnt("dribble_success"),cnt("dribble_fail")
    rec,icp=cnt("recovery"),cnt("interception")
    duw,dul=cnt("duel_won"),cnt("duel_lost"); err=cnt("error"); total=len(evs)
    pa=ps/(ps+pf) if (ps+pf)>0 else 0.0
    ca=cs/(cs+cf) if (cs+cf)>0 else 0.0
    da=dc/(dc+dw) if (dc+dw)>0 else 0.0
    dra=drs/(drs+drf) if (drs+drf)>0 else 0.0
    dua=duw/(duw+dul) if (duw+dul)>0 else 0.0
    part=min(total/20.0,1.0); ep=min(err*0.05,0.25)
    tech=max(0,(pa*0.5+ca*0.5)-ep); dec=max(0,da-ep*0.5)
    off=min((sh+sot+gl+drs)/5.0,1.0)*0.5+(sot/max(sh,1))*0.3+(gl>0)*0.2
    defe=min((rec+icp+duw)/5.0,1.0)*0.6+dua*0.4
    sn=SESSION_TYPES.get(snum or 6,"Game"); w=SESSION_WEIGHTS[sn]
    g=min(tech*w["technical"]+dec*w["decision"]+off*w["offensive"]+defe*w["defensive"]+part*0.5,1.0)
    return {"total_events":total,"pass_accuracy":round(pa*100,1),"control_accuracy":round(ca*100,1),
            "decision_score":round(da*100,1),"dribble_accuracy":round(dra*100,1),"duel_accuracy":round(dua*100,1),
            "total_shots":sh+sot,"shots_on_target":sot,"goals":gl,"offensive_actions":sh+sot+gl+drs,
            "defensive_actions":rec+icp+duw,"recoveries":rec,"interceptions":icp,"errors":err,
            "participation_rate":round(part*100,1),"score_technical":round(tech*10,1),
            "score_decision":round(dec*10,1),"score_offensive":round(off*10,1),
            "score_defensive":round(defe*10,1),"rating":round(g*10,1)}

# ══════════════════════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════════════════════
def make_radar(vals, title="", color="#e63946"):
    r=vals+[vals[0]]; cats=RADAR_CATS+[RADAR_CATS[0]]
    fig=go.Figure()
    fig.add_trace(go.Scatterpolar(r=r,theta=cats,fill='toself',
        fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.18)',
        line=dict(color=color,width=2.5),name=title))
    fig.update_layout(
        polar=dict(bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True,range=[0,1],tickvals=[.25,.5,.75,1.0],
                ticktext=["2.5","5","7.5","10"],tickfont=dict(color='#444',size=8),
                gridcolor='#1e1e1e',linecolor='#1e1e1e'),
            angularaxis=dict(tickfont=dict(color='#aaa',size=11,family='Barlow Condensed'),
                gridcolor='#1e1e1e',linecolor='#2a2a2a')),
        paper_bgcolor='rgba(0,0,0,0)',margin=dict(l=30,r=30,t=30,b=30),height=250,showlegend=False)
    return fig

def make_multi_radar(players_data):
    colors=["#e63946","#3498db","#2ecc71","#f39c12","#9b59b6"]
    fig=go.Figure()
    for i,(name,vals) in enumerate(players_data):
        c=colors[i%len(colors)]; r=vals+[vals[0]]; cats=RADAR_CATS+[RADAR_CATS[0]]
        fig.add_trace(go.Scatterpolar(r=r,theta=cats,fill='toself',name=name,
            fillcolor=f'rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.12)',
            line=dict(color=c,width=2)))
    fig.update_layout(
        polar=dict(bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True,range=[0,1],tickvals=[.25,.5,.75,1],
                tickfont=dict(color='#444',size=8),gridcolor='#1e1e1e',linecolor='#1e1e1e'),
            angularaxis=dict(tickfont=dict(color='#aaa',size=11,family='Barlow Condensed'),
                gridcolor='#1e1e1e',linecolor='#2a2a2a')),
        paper_bgcolor='rgba(0,0,0,0)',margin=dict(l=30,r=30,t=30,b=50),height=300,
        legend=dict(font=dict(color='#ccc',family='Barlow',size=11),bgcolor='rgba(0,0,0,0)',
            orientation='h',yanchor='bottom',y=-0.30))
    return fig

def sbar(label, value, max_val=10.0):
    pct=(value/max_val)*100
    return (f'<div class="sbar-wrap"><div class="sbar-label">{label}</div>'
            f'<div class="sbar-bg"><div class="sbar-fill" style="width:{pct:.0f}%"></div></div>'
            f'<div class="sbar-val">{value:.1f}</div></div>')

def stat_pills(d):
    pills="".join(f'<div class="stat-pill"><div class="stat-pill-val">{v}</div>'
                  f'<div class="stat-pill-label">{k}</div></div>' for k,v in d.items())
    return f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:8px;">{pills}</div>'

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def init():
    defs={"players":[],"events":[],"active_player":None,"current_session":1,
          "group_name":"Grupo A","completed_sessions":[],"sel_hist_id":None}
    for k,v in defs.items():
        if k not in st.session_state: st.session_state[k]=v
init()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="pip-logo">PIP ONE</div>', unsafe_allow_html=True)
    st.divider()
    st.session_state.group_name = st.text_input("Grupo", value=st.session_state.group_name)
    si = st.selectbox("Sesión",range(6),format_func=lambda i:f"S{i+1} · {SESSION_TYPES[i+1]}",
                      index=st.session_state.current_session-1,label_visibility="collapsed")
    st.session_state.current_session = si+1
    sname = SESSION_TYPES[st.session_state.current_session]
    st.markdown(f'<span class="badge badge-red">{sname}</span>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="stitle">Jugadores</div>', unsafe_allow_html=True)
    new_p = st.text_input("Añadir jugador",placeholder="Nombre…",label_visibility="collapsed")
    ca_,cb_ = st.columns(2)
    with ca_:
        if st.button("➕ Añadir",use_container_width=True):
            n=new_p.strip()
            if n and n not in st.session_state.players:
                st.session_state.players.append(n)
                if not st.session_state.active_player: st.session_state.active_player=n
                st.rerun()
    with cb_:
        if st.button("🗑 Reset",use_container_width=True):
            st.session_state.players=[]; st.session_state.events=[]
            st.session_state.active_player=None; st.rerun()
    for p in st.session_state.players:
        ne=sum(1 for e in st.session_state.events if e["player"]==p)
        ia=p==st.session_state.active_player
        if st.button(f"{'▶ ' if ia else ''}{p}  ({ne})",key=f"sp_{p}",use_container_width=True):
            st.session_state.active_player=p; st.rerun()
    st.divider()
    st.metric("Eventos",len(st.session_state.events))
    st.metric("Sesiones guardadas",len(st.session_state.completed_sessions))
    if st.session_state.events:
        st.divider()
        if st.button("💾 Finalizar y guardar",use_container_width=True,type="primary"):
            pms=[]
            for p in st.session_state.players:
                m=compute_pip_metrics([e for e in st.session_state.events if e["player"]==p])
                if m: m["player"]=p; pms.append(m)
            st.session_state.completed_sessions.append({
                "id":str(uuid.uuid4())[:8],"date":datetime.now().strftime("%Y-%m-%d"),
                "time":datetime.now().strftime("%H:%M"),"session_number":st.session_state.current_session,
                "session_type":sname,"group_name":st.session_state.group_name,
                "players_metrics":pms,"n_events":len(st.session_state.events),
                "events":st.session_state.events.copy(),
            })
            st.success("✓ Guardado")
        df_exp=pd.DataFrame(st.session_state.events)
        st.download_button("📥 Exportar CSV",data=df_exp.to_csv(index=False,sep=";").encode(),
            file_name=f"pip_{sname.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
sname=SESSION_TYPES[st.session_state.current_session]
st.markdown(f"""<div class="pip-header">
    <span class="pip-logo">⚽ PIP ONE</span>
    <span class="pip-subtitle">{st.session_state.group_name} · S{st.session_state.current_session}: {sname}</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1,tab2,tab3 = st.tabs(["⚡ CAPTURA Y ANÁLISIS","📅 HISTORIAL","🃏 FICHAS DE JUGADORES"])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1: CAPTURA Y ANÁLISIS
# ────────────────────────────────────────────────────────────────────────────
with tab1:
    if not st.session_state.players:
        st.markdown('<div style="text-align:center;padding:80px 20px;color:#1a1a1a;">'
                    '<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:5rem;font-weight:900;">PIP ONE</div>'
                    '<div style="font-size:1rem;color:#2a2a2a;margin-top:8px;">Añade jugadores en el sidebar para iniciar.</div>'
                    '</div>', unsafe_allow_html=True)
    else:
        cl,cc,cr = st.columns([1.1,1.4,1.5],gap="medium")

        # LEFT
        with cl:
            st.markdown('<div class="stitle">Jugadores</div>', unsafe_allow_html=True)
            for p in st.session_state.players:
                ia=p==st.session_state.active_player
                ne=sum(1 for e in st.session_state.events if e["player"]==p)
                m=compute_pip_metrics([e for e in st.session_state.events if e["player"]==p])
                rtg=f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;color:#e63946;font-size:1.1rem;">{m["rating"]}</span>' if m else '<span style="color:#2a2a2a">—</span>'
                bg="#1a0507" if ia else "#111"; bl="3px solid #e63946" if ia else "1px solid #1e1e1e"
                st.markdown(f'<div style="background:{bg};border-left:{bl};border-radius:6px;padding:8px 12px;margin-bottom:4px;'
                            f'display:flex;align-items:center;justify-content:space-between;">'
                            f'<div style="display:flex;align-items:center;gap:8px;">'
                            f'<div style="width:26px;height:26px;border-radius:50%;background:{"#e63946" if ia else "#1e1e1e"};'
                            f'display:flex;align-items:center;justify-content:center;font-family:\'Barlow Condensed\',sans-serif;'
                            f'font-weight:700;font-size:0.8rem;">{p[0].upper()}</div>'
                            f'<div><div style="font-size:0.88rem;font-weight:{"600" if ia else "400"};color:{"#fff" if ia else "#bbb"};">{p}</div>'
                            f'<div style="font-size:0.7rem;color:#333;">{ne} eventos</div></div></div>{rtg}</div>',
                            unsafe_allow_html=True)
            st.divider()
            st.markdown('<div class="stitle">Últimos eventos</div>', unsafe_allow_html=True)
            for e in list(reversed(st.session_state.events))[:14]:
                ei=EVENTS[e["event_type"]]
                st.markdown(f'<div class="elog">'
                            f'<div style="width:7px;height:7px;border-radius:50%;background:{ei["color"]};flex-shrink:0;"></div>'
                            f'<div style="color:#444;font-size:0.7rem;width:36px;">{e.get("timestamp","")}</div>'
                            f'<div style="color:#bbb;flex:1;font-size:0.82rem;">{e["player"]}</div>'
                            f'<div style="color:{ei["color"]};font-size:0.78rem;">{ei["label"]}</div></div>',
                            unsafe_allow_html=True)
            if not st.session_state.events:
                st.markdown('<div style="color:#222;font-size:0.82rem;padding:8px;">Sin eventos aún.</div>', unsafe_allow_html=True)
            if st.session_state.events:
                if st.button("↩ Deshacer último",use_container_width=True):
                    st.session_state.events.pop(); st.rerun()

        # CENTER
        with cc:
            active=st.session_state.active_player
            sn_=SESSION_TYPES[st.session_state.current_session]; sc_=SESSION_COLORS[sn_]
            ne_=sum(1 for e in st.session_state.events if e["player"]==active)
            st.markdown(f'<div class="card-red" style="text-align:center;margin-bottom:14px;">'
                        f'<div style="font-size:0.65rem;color:#555;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">JUGADOR ACTIVO</div>'
                        f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-weight:900;font-size:1.9rem;color:#fff;">{active}</div>'
                        f'<div style="margin-top:5px;"><span class="badge" style="background:{sc_};color:#fff;">S{st.session_state.current_session} · {sn_}</span>'
                        f'<span style="font-size:0.75rem;color:#444;margin-left:8px;">{ne_} eventos</span></div></div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="stitle">Panel de acciones</div>', unsafe_allow_html=True)
            for ev_a,ev_b in EVENT_LAYOUT:
                c1,c2=st.columns(2); kb=len(st.session_state.events)
                with c1:
                    ea=EVENTS[ev_a]
                    if st.button(ea["label"],key=f"ea_{ev_a}_{kb}",use_container_width=True):
                        st.session_state.events.append({"player":active,"session":st.session_state.current_session,
                            "session_type":sn_,"event_type":ev_a,
                            "timestamp":datetime.now().strftime("%M:%S"),
                            "date":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}); st.rerun()
                with c2:
                    if ev_b:
                        eb=EVENTS[ev_b]
                        if st.button(eb["label"],key=f"eb_{ev_b}_{kb}",use_container_width=True):
                            st.session_state.events.append({"player":active,"session":st.session_state.current_session,
                                "session_type":sn_,"event_type":ev_b,
                                "timestamp":datetime.now().strftime("%M:%S"),
                                "date":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}); st.rerun()
            evs_sn=[e for e in st.session_state.events if e["player"]==active and e["session"]==st.session_state.current_session]
            if evs_sn:
                st.divider()
                st.markdown('<div class="stitle">Resumen sesión</div>', unsafe_allow_html=True)
                cc2={}
                for e in evs_sn: cc2[EVENTS[e["event_type"]]["cat"]]=cc2.get(EVENTS[e["event_type"]]["cat"],0)+1
                mcols=st.columns(4)
                for col_,(cat,lbl) in zip(mcols,[("technical","Técnica"),("decision","Decisión"),("offensive","Ataque"),("defensive","Defensa")]):
                    with col_: st.metric(lbl,cc2.get(cat,0))

        # RIGHT
        with cr:
            st.markdown('<div class="stitle">Dashboard</div>', unsafe_allow_html=True)
            td1,td2=st.tabs(["Individual","Comparar"])
            with td1:
                rp=st.selectbox("Jugador",st.session_state.players,
                    index=st.session_state.players.index(active) if active in st.session_state.players else 0,
                    label_visibility="collapsed")
                m=compute_pip_metrics([e for e in st.session_state.events if e["player"]==rp])
                if m:
                    st.markdown(f'<div style="display:flex;align-items:flex-end;gap:14px;margin-bottom:10px;">'
                                f'<div><div class="rating-xl">{m["rating"]}</div><div class="rating-label">Rating</div></div>'
                                f'<div style="flex:1;padding-bottom:4px;"><div style="font-size:0.72rem;color:#333;margin-bottom:6px;">'
                                f'{m["total_events"]} eventos · {m["participation_rate"]}% participación</div>'
                                f'{"".join(sbar(CAT_LABELS[k],m[f"score_{k}"]) for k in ["technical","decision","offensive","defensive"])}'
                                f'</div></div>', unsafe_allow_html=True)
                    vals=[m["score_technical"]/10,m["score_decision"]/10,m["score_offensive"]/10,m["score_defensive"]/10,m["participation_rate"]/100]
                    st.plotly_chart(
                        make_radar(vals, rp),
                        use_container_width=True,
                        config={"displayModeBar": False},
                        key=f"radar_{rp}"
                    )
                    mc1,mc2=st.columns(2)
                    with mc1: st.metric("Pase %",f'{m["pass_accuracy"]:.0f}%'); st.metric("Decisión %",f'{m["decision_score"]:.0f}%'); st.metric("Acc. ofensivas",m["offensive_actions"])
                    with mc2: st.metric("Control %",f'{m["control_accuracy"]:.0f}%'); st.metric("Acc. defensivas",m["defensive_actions"]); st.metric("Goles",m["goals"])
                else:
                    st.markdown('<div style="color:#222;padding:30px;text-align:center;">Sin eventos.</div>', unsafe_allow_html=True)
            with td2:
                rows=[{**compute_pip_metrics([e for e in st.session_state.events if e["player"]==p]),"player":p}
                      for p in st.session_state.players if compute_pip_metrics([e for e in st.session_state.events if e["player"]==p])]
                if len(rows)>=2:
                    df_cmp=pd.DataFrame(rows)
                    sel=st.multiselect("Jugadores",df_cmp["player"].tolist(),default=df_cmp["player"].tolist()[:3],max_selections=5)
                    if len(sel)>=2:
                        pdata=[(r["player"],[r["score_technical"]/10,r["score_decision"]/10,r["score_offensive"]/10,r["score_defensive"]/10,r["participation_rate"]/100])
                               for _,r in df_cmp[df_cmp["player"].isin(sel)].iterrows()]
                        st.plotly_chart(
                            make_multi_radar(pdata),
                            use_container_width=True,
                            config={"displayModeBar": False},
                            key=f"multi_radar_tab1_{hash(tuple(p[0] for p in pdata))}"
                        )
                        disp=df_cmp[df_cmp["player"].isin(sel)][["player","rating","pass_accuracy","decision_score","offensive_actions","defensive_actions"]].sort_values("rating",ascending=False).reset_index(drop=True)
                        disp.columns=["Jugador","Rating","Pase%","Decisión%","Ataque","Defensa"]; disp.index+=1
                        st.dataframe(disp.style.background_gradient(subset=["Rating"],cmap="RdYlGn"),use_container_width=True)
                else: st.info("Captura eventos de al menos 2 jugadores.")

# ────────────────────────────────────────────────────────────────────────────
# TAB 2: HISTORIAL
# ────────────────────────────────────────────────────────────────────────────
with tab2:
    cs_list=st.session_state.completed_sessions
    if not cs_list:
        st.markdown('<div style="text-align:center;padding:80px 20px;">'
                    '<div style="font-size:3rem;">📅</div>'
                    '<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.5rem;color:#1e1e1e;font-weight:700;margin-top:10px;">Sin sesiones guardadas</div>'
                    '<div style="font-size:0.85rem;color:#2a2a2a;margin-top:8px;">Captura eventos y pulsa \'Finalizar y guardar\' en el sidebar.</div>'
                    '</div>', unsafe_allow_html=True)
    else:
        hl,hr=st.columns([1,2.2],gap="medium")
        with hl:
            st.markdown('<div class="stitle">Sesiones registradas</div>', unsafe_allow_html=True)
            for cs in reversed(cs_list):
                sc_s=SESSION_COLORS.get(cs["session_type"],"#e63946")
                sel=(st.session_state.sel_hist_id==cs["id"])
                if st.button(f"S{cs['session_number']} · {cs['session_type']}  —  {cs['date']} {cs['time']}",
                             key=f"h_{cs['id']}",use_container_width=True):
                    st.session_state.sel_hist_id=cs["id"]; st.rerun()
                bg="#1a0507" if sel else "#111"; bl="2px solid #e63946" if sel else "1px solid #1e1e1e"
                st.markdown(f'<div style="background:{bg};border-left:{bl};border-radius:6px;padding:7px 12px;'
                            f'margin-top:-12px;margin-bottom:8px;">'
                            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                            f'<span class="badge" style="background:{sc_s};color:#fff;font-size:0.65rem;">{cs["session_type"]}</span>'
                            f'<span style="color:#333;font-size:0.72rem;">{cs["n_events"]} eventos</span></div>'
                            f'<div style="font-size:0.75rem;color:#444;margin-top:3px;">{cs["group_name"]} · {len(cs["players_metrics"])} jugadores</div>'
                            f'</div>', unsafe_allow_html=True)

            # Evolución
            all_ph=set(pm["player"] for cs in cs_list for pm in cs["players_metrics"])
            if len(cs_list)>1 and all_ph:
                st.divider()
                st.markdown('<div class="stitle">Evolución rating</div>', unsafe_allow_html=True)
                ep=st.selectbox("Jugador",sorted(all_ph),key="evo_p",label_visibility="collapsed")
                evo=[{"Sesión":f"S{cs['session_number']}\n{cs['date']}","Rating":pm["rating"]}
                     for cs in cs_list for pm in cs["players_metrics"] if pm["player"]==ep]
                if len(evo)>=2:
                    df_evo=pd.DataFrame(evo)
                    fig_evo=go.Figure()
                    fig_evo.add_trace(go.Scatter(x=df_evo["Sesión"],y=df_evo["Rating"],mode="lines+markers",
                        line=dict(color="#e63946",width=2),marker=dict(size=8,color="#e63946"),
                        fill="tozeroy",fillcolor="rgba(230,57,70,0.08)"))
                    fig_evo.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=0,r=0,t=10,b=0),height=160,
                        yaxis=dict(range=[0,10],gridcolor="#1e1e1e",color="#444",tickfont=dict(size=9)),
                        xaxis=dict(gridcolor="#1e1e1e",color="#444",tickfont=dict(size=9)))
                    st.plotly_chart(fig_evo,use_container_width=True,config={"displayModeBar":False})

        with hr:
            sid=st.session_state.sel_hist_id
            sel_cs=next((c for c in cs_list if c["id"]==sid),cs_list[-1])
            sc_s=SESSION_COLORS.get(sel_cs["session_type"],"#e63946")
            st.markdown(f'<div class="ficha-header">'
                        f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
                        f'<span class="badge" style="background:{sc_s};">S{sel_cs["session_number"]} · {sel_cs["session_type"]}</span>'
                        f'<span style="color:#555;font-size:0.8rem;">📅 {sel_cs["date"]} {sel_cs["time"]}</span>'
                        f'<span style="color:#555;font-size:0.8rem;">👥 {sel_cs["group_name"]}</span>'
                        f'<span style="color:#555;font-size:0.8rem;">⚡ {sel_cs["n_events"]} eventos</span>'
                        f'</div></div>', unsafe_allow_html=True)
            pms=sel_cs["players_metrics"]
            if pms:
                st.markdown('<div class="stitle">Ranking</div>', unsafe_allow_html=True)
                df_rank=pd.DataFrame(pms).sort_values("rating",ascending=False).reset_index(drop=True)
                df_rank.index+=1
                for i,row in df_rank.iterrows():
                    medal={1:"🥇",2:"🥈",3:"🥉"}.get(i,"")
                    st.markdown(f'<div class="card" style="padding:12px 16px;margin-bottom:6px;">'
                                f'<div style="display:flex;align-items:center;justify-content:space-between;">'
                                f'<div style="display:flex;align-items:center;gap:10px;">'
                                f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-weight:900;font-size:1.2rem;color:#2a2a2a;width:20px;">{i}</div>'
                                f'<div style="font-size:1.4rem;">{medal}</div>'
                                f'<div><div style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;font-size:1rem;color:#fff;">{row["player"]}</div>'
                                f'<div style="font-size:0.7rem;color:#444;">{row["total_events"]} eventos</div></div></div>'
                                f'<div class="rating-lg">{row["rating"]}</div></div>'
                                f'<div style="margin-top:8px;">{"".join(sbar(CAT_LABELS[k],row[f"score_{k}"]) for k in ["technical","decision","offensive","defensive"])}</div>'
                                f'</div>', unsafe_allow_html=True)
                if len(pms)>=2:
                    st.divider()
                    st.markdown('<div class="stitle">Radar comparativa</div>', unsafe_allow_html=True)
                    pdata=[(r["player"],[r["score_technical"]/10,r["score_decision"]/10,r["score_offensive"]/10,r["score_defensive"]/10,r["participation_rate"]/100]) for r in pms]
                    st.plotly_chart(
                        make_multi_radar(pdata),
                        use_container_width=True,
                        config={"displayModeBar": False},
                        key=f"multi_radar_hist_{sel_cs['id']}"
                    )
                st.divider()
                disp=df_rank[["player","rating","pass_accuracy","control_accuracy","decision_score",
                              "dribble_accuracy","offensive_actions","defensive_actions","goals","errors","total_events"]].copy()
                disp.columns=["Jugador","Rating","Pase%","Control%","Decisión%","Regate%","Ataque","Defensa","Goles","Errores","Eventos"]
                st.dataframe(disp.style.background_gradient(subset=["Rating"],cmap="RdYlGn"),use_container_width=True,hide_index=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 3: FICHAS DE JUGADORES
# ────────────────────────────────────────────────────────────────────────────
with tab3:
    fc_src,fc_main=st.columns([1,3],gap="medium")

    with fc_src:
        st.markdown('<div class="stitle">Fuente</div>', unsafe_allow_html=True)
        source=st.radio("Fuente",["🏟 1ª RFEF 2025/26","⚡ Sesiones PIP ONE"],label_visibility="collapsed")
        use_rfef="RFEF" in source
        if use_rfef and not rfef_profiles.empty:
            st.divider()
            pos_opts=["Todos"]+sorted(rfef_profiles["posicion"].dropna().unique().tolist())
            pos_f=st.selectbox("Posición",pos_opts,label_visibility="collapsed")
            min_m=st.slider("Minutos mín.",90,1800,270,step=90)
            team_opts=["Todos"]+sorted(rfef_profiles["equipo"].dropna().unique().tolist())
            team_f=st.selectbox("Equipo",team_opts,label_visibility="collapsed")
            st.divider()
            st.markdown('<div class="stitle">Ordenar por</div>', unsafe_allow_html=True)
            sort_c=st.selectbox("Ordenar",["pip_rating","score_technical","score_decision","score_offensive","score_defensive"],
                label_visibility="collapsed",
                format_func=lambda x:{"pip_rating":"Rating PIP","score_technical":"Técnica",
                    "score_decision":"Decisión","score_offensive":"Ataque","score_defensive":"Defensa"}[x])

    with fc_main:
        if use_rfef:
            if rfef_profiles.empty:
                st.warning("No hay datos RFEF cargados.")
            else:
                df_show=rfef_profiles.copy()
                if pos_f!="Todos": df_show=df_show[df_show["posicion"]==pos_f]
                if team_f!="Todos": df_show=df_show[df_show["equipo"]==team_f]
                df_show=df_show[df_show["minutos_jugados"]>=min_m].sort_values(sort_c,ascending=False)
                if df_show.empty: st.warning("Sin jugadores con estos filtros.")
                else:
                    player_names=df_show["jugador"].tolist()
                    search=st.selectbox("Buscar jugador",player_names,label_visibility="collapsed")
                    r=df_show[df_show["jugador"]==search].iloc[0]
                    pos_full=POS_LABELS.get(str(r.get("posicion","")),"—")
                    mins=int(r.get("minutos_jugados",0))
                    partidos=int(r.get("partidos",0))
                    equipo=r.get("equipo","—")
                    rank_pos=list(df_show["jugador"]).index(search)+1

                    fc1,fc2=st.columns([1.8,1.2],gap="medium")
                    with fc1:
                        st.markdown(f'<div class="ficha-header">'
                                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                                    f'<div><div class="ficha-nombre">{r["jugador"]}</div>'
                                    f'<div class="ficha-equipo">{equipo} · {pos_full}</div>'
                                    f'<div style="margin-top:10px;display:flex;gap:5px;flex-wrap:wrap;">'
                                    f'<span class="badge badge-red">{pos_full}</span>'
                                    f'<span class="badge badge-gray">{mins} min</span>'
                                    f'<span class="badge badge-gray">{partidos} PJ</span>'
                                    f'<span class="badge badge-gray">#{rank_pos}/{len(df_show)}</span>'
                                    f'</div></div>'
                                    f'<div style="text-align:center;">'
                                    f'<div class="rating-xl">{r["pip_rating"]:.1f}</div>'
                                    f'<div class="rating-label">PIP Rating</div></div></div>'
                                    f'<div style="margin-top:14px;">'
                                    f'{"".join(sbar(CAT_LABELS[k],r[f"score_{k}"]) for k in ["technical","decision","offensive","defensive"])}'
                                    f'</div></div>', unsafe_allow_html=True)

                        goles=int(r.get("goles",0) or 0); asis=int(r.get("asistencias",0) or 0)
                        tiros=int(r.get("tiros_totales",0) or 0); sot_v=int(r.get("tiros_a_puerta",0) or 0)
                        rec_v=int(r.get("recuperaciones",0) or 0); icp_v=int(r.get("intercepciones",0) or 0)
                        rgt_v=int(r.get("regates_exitosos",0) or 0); dsp_v=int(r.get("despejes",0) or 0)
                        pa_p=f'{r.get("pass_acc",0)*100:.0f}%'; da_p=f'{r.get("duel_acc",0)*100:.0f}%'
                        st.markdown(stat_pills({"Goles":goles,"Asist.":asis,"Tiros":tiros,"A puerta":sot_v,
                                                "Pase %":pa_p,"Duelo %":da_p,"Recup.":rec_v,
                                                "Interc.":icp_v,"Despejes":dsp_v,"Regates":rgt_v}), unsafe_allow_html=True)

                        scores_r={"Técnica":r["score_technical"],"Decisión":r["score_decision"],
                                  "Ataque":r["score_offensive"],"Defensa":r["score_defensive"]}
                        ss=sorted(scores_r.items(),key=lambda x:x[1],reverse=True)
                        st.divider()
                        sw1,sw2=st.columns(2)
                        with sw1:
                            st.markdown('<div class="stitle">💪 Fortalezas</div>', unsafe_allow_html=True)
                            for cat,val in ss[:2]:
                                st.markdown(f'<div style="color:#27ae60;font-size:0.85rem;padding:2px 0;">▸ {cat} <span style="color:#333;font-size:0.75rem;">({val:.1f})</span></div>', unsafe_allow_html=True)
                        with sw2:
                            st.markdown('<div class="stitle">📈 A mejorar</div>', unsafe_allow_html=True)
                            for cat,val in ss[2:]:
                                st.markdown(f'<div style="color:#e63946;font-size:0.85rem;padding:2px 0;">▸ {cat} <span style="color:#333;font-size:0.75rem;">({val:.1f})</span></div>', unsafe_allow_html=True)

                        # PIP ONE data cross-linked
                        pip_evs=[e for e in st.session_state.events if e["player"].lower()==r["jugador"].lower()]
                        hist_pms=[pm for cs in st.session_state.completed_sessions for pm in cs["players_metrics"] if pm["player"].lower()==r["jugador"].lower()]
                        if pip_evs or hist_pms:
                            st.divider()
                            st.markdown('<div class="stitle">⚡ Datos PIP ONE cruzados</div>', unsafe_allow_html=True)
                            if hist_pms:
                                for pm in hist_pms[-3:]:
                                    st.markdown(f'<div style="background:#111;border:1px solid #1e1e1e;border-radius:6px;padding:8px 12px;margin-bottom:5px;display:flex;justify-content:space-between;align-items:center;">'
                                                f'<span style="font-size:0.8rem;color:#666;">Sesión PIP ONE</span>'
                                                f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;color:#e63946;font-size:1.1rem;">{pm["rating"]}</span>'
                                                f'</div>', unsafe_allow_html=True)
                            if pip_evs:
                                m_pip=compute_pip_metrics(pip_evs)
                                if m_pip:
                                    st.markdown(f'<div style="background:#111;border:1px solid #e63946;border-radius:6px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;">'
                                                f'<span style="font-size:0.8rem;color:#888;">Sesión activa</span>'
                                                f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;color:#e63946;font-size:1.1rem;">{m_pip["rating"]}</span>'
                                                f'</div>', unsafe_allow_html=True)

                    with fc2:
                        vals_r=[r["score_technical"]/10,r["score_decision"]/10,
                                r["score_offensive"]/10,r["score_defensive"]/10,
                                r["participation_rate"]/100]
                        st.plotly_chart(make_radar(vals_r,r["jugador"]),use_container_width=True,config={"displayModeBar":False})
                        st.markdown('<div class="stitle">Métricas / 90 min</div>', unsafe_allow_html=True)
                        m90={"Tiros/90":f'{r.get("shots_90",0):.2f}',"T.Puerta/90":f'{r.get("sot_90",0):.2f}',
                             "Goles/90":f'{r.get("goals_90",0):.2f}',"xG/90":f'{r.get("xg_90",0):.2f}',
                             "Recup./90":f'{r.get("rec_90",0):.2f}',"Interc./90":f'{r.get("int_90",0):.2f}'}
                        for lbl,val in m90.items():
                            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1e1e1e;">'
                                        f'<span style="font-size:0.8rem;color:#555;">{lbl}</span>'
                                        f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;color:#e63946;font-size:0.9rem;">{val}</span>'
                                        f'</div>', unsafe_allow_html=True)
                        rs=r.get("rating_sofascore",np.nan)
                        if pd.notna(rs) and float(rs)>0:
                            st.markdown(f'<div style="text-align:center;background:#111;border:1px solid #1e1e1e;border-radius:8px;padding:12px;margin-top:12px;">'
                                        f'<div style="font-size:0.65rem;color:#444;letter-spacing:2px;text-transform:uppercase;">Sofascore Avg</div>'
                                        f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-weight:900;font-size:2.2rem;color:#f39c12;">{float(rs):.1f}</div>'
                                        f'</div>', unsafe_allow_html=True)

                    # Top 10 misma posición
                    st.divider()
                    st.markdown(f'<div class="stitle">Top 10 {pos_full}s · Rating PIP</div>', unsafe_allow_html=True)
                    df_pos=rfef_profiles[rfef_profiles["posicion"]==r["posicion"]].copy()
                    df_pos=df_pos[df_pos["minutos_jugados"]>=min_m].sort_values("pip_rating",ascending=False).head(10)
                    df_pos=df_pos[["jugador","equipo","pip_rating","score_technical","score_decision","score_offensive","score_defensive","minutos_jugados","partidos"]].reset_index(drop=True)
                    df_pos.index+=1; df_pos.columns=["Jugador","Equipo","Rating","Téc","Dec","Ata","Def","Min","PJ"]
                    st.dataframe(df_pos.style.background_gradient(subset=["Rating"],cmap="RdYlGn"),use_container_width=True)

        else:
            # PIP ONE fichas
            all_pip=set(p for p in st.session_state.players)
            for cs in st.session_state.completed_sessions:
                for pm in cs["players_metrics"]: all_pip.add(pm["player"])
            if not all_pip:
                st.markdown('<div style="text-align:center;padding:60px 20px;">'
                            '<div style="font-size:2.5rem;">⚡</div>'
                            '<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.3rem;color:#1e1e1e;font-weight:700;margin-top:8px;">Sin jugadores PIP ONE</div>'
                            '<div style="font-size:0.82rem;color:#2a2a2a;margin-top:6px;">Captura eventos en la pestaña Captura y Análisis.</div>'
                            '</div>', unsafe_allow_html=True)
            else:
                pip_sel=st.selectbox("Jugador PIP ONE",sorted(all_pip),label_visibility="collapsed")
                all_e=[e for e in st.session_state.events if e["player"]==pip_sel]
                m_pip=compute_pip_metrics(all_e)
                hist_data=[{**pm,"session_type":cs["session_type"],"session_number":cs["session_number"],"date":cs["date"],"time":cs["time"]}
                           for cs in st.session_state.completed_sessions for pm in cs["players_metrics"] if pm["player"]==pip_sel]
                use_m = m_pip or (hist_data[-1] if hist_data else None)
                if use_m:
                    pc1,pc2=st.columns([1.8,1.2],gap="medium")
                    with pc1:
                        st.markdown(f'<div class="ficha-header">'
                                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                                    f'<div><div class="ficha-nombre">{pip_sel}</div>'
                                    f'<div class="ficha-equipo">Sesiones PIP ONE · {len(hist_data)} guardadas</div></div>'
                                    f'<div style="text-align:center;"><div class="rating-xl">{use_m["rating"]}</div>'
                                    f'<div class="rating-label">Rating</div></div></div>'
                                    f'<div style="margin-top:12px;">{"".join(sbar(CAT_LABELS[k],use_m[f"score_{k}"]) for k in ["technical","decision","offensive","defensive"])}</div>'
                                    f'</div>', unsafe_allow_html=True)
                        kc1,kc2=st.columns(2)
                        with kc1:
                            st.metric("Pase %",f'{use_m["pass_accuracy"]:.0f}%')
                            st.metric("Decisión %",f'{use_m["decision_score"]:.0f}%')
                            st.metric("Goles",use_m["goals"])
                        with kc2:
                            st.metric("Control %",f'{use_m["control_accuracy"]:.0f}%')
                            st.metric("Acc. ofensivas",use_m["offensive_actions"])
                            st.metric("Acc. defensivas",use_m["defensive_actions"])
                    with pc2:
                        vals=[use_m["score_technical"]/10,use_m["score_decision"]/10,use_m["score_offensive"]/10,use_m["score_defensive"]/10,use_m["participation_rate"]/100]
                        st.plotly_chart(make_radar(vals,pip_sel),use_container_width=True,config={"displayModeBar":False})
                    if hist_data:
                        st.divider()
                        st.markdown('<div class="stitle">Historial de sesiones</div>', unsafe_allow_html=True)
                        df_h=pd.DataFrame(hist_data)[["date","time","session_number","session_type","rating","score_technical","score_decision","score_offensive","score_defensive"]]
                        df_h.columns=["Fecha","Hora","Sesión","Tipo","Rating","Téc","Dec","Ata","Def"]
                        st.dataframe(df_h.style.background_gradient(subset=["Rating"],cmap="RdYlGn"),use_container_width=True,hide_index=True)
