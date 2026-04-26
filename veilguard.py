import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import subprocess
import shutil
import sys

from groq_helper import (
    generate_alert_explanation,
    generate_attack_simulation
)

# =========================================================
# VEILGuard — Enterprise Insider Risk Platform
# Vigilant Enterprise Insider Leakage Guard
# AI-Powered Insider Risk Detection & Proactive Threat Simulation
# =========================================================

st.set_page_config(
    page_title="VEILGuard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ╔══════════════════════════════════════════════════════════════╗
# ║   🎨  GLOBAL THEME CONFIGURATION — EDIT HERE ONLY          ║
# ║   All colors, fonts, sizes, and spacing are controlled      ║
# ║   from this single block. Changes apply site-wide.          ║
# ╚══════════════════════════════════════════════════════════════╝

THEME = {
    # ── Backgrounds ──────────────────────────────────────────────
    "bg_base":          "#04080f",       # Deepest background
    "bg_surface":       "#080e1c",       # Surface / sidebar
    "bg_card":          "#0c1424",       # Cards
    "bg_card_hover":    "#101a2e",       # Card hover state
    "bg_input":         "#0a1220",       # Form inputs

    # ── Brand / Accent Colours ───────────────────────────────────
    "cyan":             "#38bdf8",       # Primary brand colour
    "cyan_glow":        "rgba(56,189,248,0.07)",
    "cyan_dim":         "rgba(56,189,248,0.14)",
    "violet":           "#a78bfa",       # Secondary accent
    "red":              "#f87171",       # Critical / danger
    "amber":            "#fbbf24",       # Warning / high
    "green":            "#34d399",       # Safe / low risk
    "pink":             "#ec4899",       # Defense evasion

    # ── Borders ──────────────────────────────────────────────────
    "border":           "rgba(56,189,248,0.08)",
    "border_accent":    "rgba(56,189,248,0.22)",
    "border_strong":    "rgba(56,189,248,0.42)",

    # ── Text ─────────────────────────────────────────────────────
    "text_primary":     "#f0f4ff",       # Headings / high-emphasis
    "text_secondary":   "#a8b8d4",       # Body text — NOT grey
    "text_muted":       "#5a6e8a",       # Labels / metadata

    # ── Typography ───────────────────────────────────────────────
    "font_display":     "'Orbitron', 'Syne', sans-serif",   # Headers / logo
    "font_body":        "'DM Sans', 'Inter', sans-serif",   # Body text
    "font_mono":        "'JetBrains Mono', 'IBM Plex Mono', monospace",

    # ── Font Sizes (min 14px everywhere) ─────────────────────────
    "fs_xs":            "13px",          # Only for tiny labels
    "fs_sm":            "14px",          # Minimum body size
    "fs_base":          "15px",          # Standard body
    "fs_md":            "16px",          # Slightly larger body
    "fs_lg":            "18px",          # Sub-headings
    "fs_xl":            "22px",          # Section headings
    "fs_2xl":           "28px",          # Page headings
    "fs_3xl":           "38px",          # Hero numbers
    "fs_display":       "52px",          # Display / logo

    # ── Spacing & Radius ─────────────────────────────────────────
    "radius_sm":        "8px",
    "radius_md":        "14px",
    "radius_lg":        "20px",
    "radius_xl":        "28px",

    # ── Button Style ─────────────────────────────────────────────
    "btn_gradient":     "linear-gradient(135deg, #0ea5e9 0%, #2563eb 60%, #4f46e5 100%)",
    "btn_shadow":       "0 4px 20px rgba(14,165,233,0.35), 0 1px 3px rgba(0,0,0,0.4)",
    "btn_hover_shadow": "0 8px 32px rgba(14,165,233,0.55), 0 2px 8px rgba(0,0,0,0.5)",

    # ── Sidebar width ─────────────────────────────────────────────
    "sidebar_width":    "260px",
}

# Convenience shorthand references (used in CSS f-string below)
T = THEME

# ─────────────────────────────────────────────────────────────────
# INJECT GOOGLE FONTS + GLOBAL CSS
# ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500;600;700&family=Syne:wght@400;600;700;800&display=swap');

/* ═══════════════════════════════════════════════════════
   CSS CUSTOM PROPERTIES  — driven by THEME dict above
   ═══════════════════════════════════════════════════════ */
:root {{
    --bg-base:          {T['bg_base']};
    --bg-surface:       {T['bg_surface']};
    --bg-card:          {T['bg_card']};
    --bg-card-hover:    {T['bg_card_hover']};
    --bg-input:         {T['bg_input']};

    --cyan:             {T['cyan']};
    --cyan-glow:        {T['cyan_glow']};
    --cyan-dim:         {T['cyan_dim']};
    --violet:           {T['violet']};
    --red:              {T['red']};
    --amber:            {T['amber']};
    --green:            {T['green']};
    --pink:             {T['pink']};

    --border:           {T['border']};
    --border-accent:    {T['border_accent']};
    --border-strong:    {T['border_strong']};

    --text-primary:     {T['text_primary']};
    --text-secondary:   {T['text_secondary']};
    --text-muted:       {T['text_muted']};

    --font-display:     {T['font_display']};
    --font-body:        {T['font_body']};
    --font-mono:        {T['font_mono']};

    --fs-xs:            {T['fs_xs']};
    --fs-sm:            {T['fs_sm']};
    --fs-base:          {T['fs_base']};
    --fs-md:            {T['fs_md']};
    --fs-lg:            {T['fs_lg']};
    --fs-xl:            {T['fs_xl']};
    --fs-2xl:           {T['fs_2xl']};
    --fs-3xl:           {T['fs_3xl']};

    --radius-sm:        {T['radius_sm']};
    --radius-md:        {T['radius_md']};
    --radius-lg:        {T['radius_lg']};
    --radius-xl:        {T['radius_xl']};

    --btn-gradient:     {T['btn_gradient']};
    --btn-shadow:       {T['btn_shadow']};
    --btn-hover-shadow: {T['btn_hover_shadow']};
}}

/* ═══════════════════════════════════════════════════════
   GLOBAL RESET & BASE
   ═══════════════════════════════════════════════════════ */
*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [class*="css"] {{
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: var(--fs-base) !important;
}}

/* Premium animated mesh background on main area */
.main .block-container::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse 80% 60% at 10% 0%, rgba(56,189,248,0.055) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 100%, rgba(167,139,250,0.045) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(14,165,233,0.025) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}}

#MainMenu, footer {{ visibility: hidden; }}

.block-container {{
    padding: 5rem 2.4rem 4rem !important;
    max-width: 1760px;
    position: relative;
    z-index: 1;
}}

/* ═══════════════════════════════════════════════════════
   SIDEBAR — LUXURY DARK PANEL
   ═══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #060c1a 0%, {T['bg_base']} 100%) !important;
    border-right: 1px solid var(--border-accent) !important;
    box-shadow: 4px 0 40px rgba(0,0,0,0.5) !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding-top: 0 !important;
    overflow: hidden;
}}

/* Sidebar nav radio — reimagined as icon button list */
[data-testid="stSidebar"] .stRadio > label {{ display: none; }}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
    gap: 3px !important;
    display: flex;
    flex-direction: column;
    padding: 0 10px;
}}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {{
    background: transparent !important;
    border: 1px solid transparent !important;
    padding: 12px 16px !important;
    border-radius: var(--radius-sm) !important;
    cursor: pointer !important;
    transition: all 0.2s cubic-bezier(0.4,0,0.2,1) !important;
    font-family: var(--font-body) !important;
    font-size: var(--fs-sm) !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    letter-spacing: 0.01em;
    position: relative;
}}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] p {{
    font-size: var(--fs-sm) !important;
    color: inherit !important;
}}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {{
    background: rgba(56,189,248,0.07) !important;
    border-color: var(--border) !important;
    color: var(--cyan) !important;
    transform: translateX(3px) !important;
}}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"][aria-checked="true"] {{
    background: linear-gradient(135deg, rgba(56,189,248,0.15), rgba(56,189,248,0.06)) !important;
    border-color: rgba(56,189,248,0.30) !important;
    color: var(--cyan) !important;
    box-shadow: inset 3px 0 0 var(--cyan), 0 0 20px var(--cyan-glow) !important;
    font-weight: 600 !important;
}}
/* Hide the radio circle dot */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:first-child {{
    display: none !important;
}}

/* ═══════════════════════════════════════════════════════
   TYPOGRAPHY
   ═══════════════════════════════════════════════════════ */
h1, h2, h3, h4 {{
    font-family: var(--font-display) !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}}
p, li, span, div {{
    font-size: var(--fs-base);
    line-height: 1.75;
    color: var(--text-secondary);
}}
/* Ensure no text drops below 14px globally */
* {{ min-font-size: 14px; }}
small, .small {{ font-size: var(--fs-sm) !important; }}

/* ═══════════════════════════════════════════════════════
   METRIC CARDS — HOLOGRAPHIC STYLE
   ═══════════════════════════════════════════════════════ */
[data-testid="metric-container"] {{
    background: linear-gradient(135deg, var(--bg-card) 0%, rgba(56,189,248,0.04) 100%) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.4rem 1.6rem !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    position: relative;
    overflow: hidden;
}}
[data-testid="metric-container"]::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    opacity: 0.6;
}}
[data-testid="metric-container"]:hover {{
    border-color: var(--border-strong) !important;
    box-shadow: 0 0 40px var(--cyan-glow), 0 8px 32px rgba(0,0,0,0.4) !important;
    transform: translateY(-3px) !important;
}}
[data-testid="stMetricLabel"] p {{
    font-family: var(--font-mono) !important;
    font-size: var(--fs-xs) !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
}}
[data-testid="stMetricValue"] {{
    font-family: var(--font-display) !important;
    font-size: var(--fs-3xl) !important;
    font-weight: 900 !important;
    color: var(--text-primary) !important;
    line-height: 1.1 !important;
    letter-spacing: -0.03em !important;
}}
[data-testid="stMetricDelta"] {{
    font-family: var(--font-mono) !important;
    font-size: var(--fs-sm) !important;
}}

/* ═══════════════════════════════════════════════════════
   BUTTONS — WORLD CLASS CTA STYLE
   ═══════════════════════════════════════════════════════ */
.stButton > button {{
    background: var(--btn-gradient) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: var(--fs-sm) !important;
    letter-spacing: 0.04em !important;
    padding: 0.72rem 1.8rem !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: var(--btn-shadow) !important;
    position: relative !important;
    overflow: hidden !important;
    cursor: pointer !important;
    text-transform: none !important;
    min-height: 44px !important;
}}
.stButton > button::before {{
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
    transition: left 0.5s ease;
}}
.stButton > button:hover {{
    box-shadow: var(--btn-hover-shadow) !important;
    transform: translateY(-2px) scale(1.02) !important;
    filter: brightness(1.08) !important;
}}
.stButton > button:hover::before {{
    left: 100%;
}}
.stButton > button:active {{
    transform: translateY(0px) scale(0.99) !important;
    box-shadow: 0 2px 8px rgba(14,165,233,0.3) !important;
}}
/* Download button variant */
[data-testid="stDownloadButton"] > button {{
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    box-shadow: 0 4px 20px rgba(5,150,105,0.35) !important;
    border-radius: 10px !important;
    font-family: var(--font-body) !important;
    font-size: var(--fs-sm) !important;
    font-weight: 600 !important;
    padding: 0.72rem 1.8rem !important;
    color: #fff !important;
    transition: all 0.25s ease !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(5,150,105,0.5) !important;
}}

/* ═══════════════════════════════════════════════════════
   EXPANDERS — SLEEK ACCORDION
   ═══════════════════════════════════════════════════════ */
[data-testid="stExpander"] {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    margin-bottom: 10px !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    overflow: hidden;
}}
[data-testid="stExpander"]:hover {{
    border-color: var(--border-accent) !important;
    box-shadow: 0 4px 32px var(--cyan-glow), 0 0 0 1px rgba(56,189,248,0.1) !important;
}}
details summary {{
    font-family: var(--font-body) !important;
    font-size: var(--fs-sm) !important;
    color: var(--text-secondary) !important;
    padding: 16px 22px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
}}
details summary:hover {{ color: var(--text-primary) !important; }}
details[open] summary {{ color: var(--cyan) !important; font-weight: 600 !important; }}
details[open] {{ border-color: var(--border-accent) !important; }}

/* ═══════════════════════════════════════════════════════
   SELECT BOXES & INPUTS
   ═══════════════════════════════════════════════════════ */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {{
    background: var(--bg-input) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: var(--fs-sm) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stMultiSelect"] > div > div:focus-within {{
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-glow) !important;
}}
[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] input {{
    background: var(--bg-input) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: var(--fs-sm) !important;
    padding: 10px 14px !important;
}}
[data-testid="stTextInput"] > div > div > input:focus {{
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-glow) !important;
    outline: none !important;
}}

/* ═══════════════════════════════════════════════════════
   SLIDERS
   ═══════════════════════════════════════════════════════ */
[data-testid="stSlider"] > div > div > div > div {{
    background: var(--cyan) !important;
}}
[data-testid="stSlider"] .st-emotion-cache-1inwz65 {{
    background: rgba(56,189,248,0.2) !important;
}}

/* ═══════════════════════════════════════════════════════
   DATAFRAME — ENTERPRISE TABLE
   ═══════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {{
    border: 1px solid var(--border-accent) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
}}
.dvn-scroller {{ background: var(--bg-surface) !important; }}
[data-testid="stDataFrame"] th {{
    background: #070d1c !important;
    color: var(--text-muted) !important;
    font-family: var(--font-mono) !important;
    font-size: var(--fs-xs) !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-accent) !important;
    padding: 10px 14px !important;
}}
[data-testid="stDataFrame"] td {{
    font-family: var(--font-body) !important;
    font-size: var(--fs-sm) !important;
    color: var(--text-secondary) !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 9px 14px !important;
}}

/* ═══════════════════════════════════════════════════════
   ALERTS & NOTIFICATIONS
   ═══════════════════════════════════════════════════════ */
[data-testid="stAlert"] {{
    border-radius: var(--radius-md) !important;
    font-family: var(--font-body) !important;
    font-size: var(--fs-sm) !important;
    border: none !important;
    padding: 14px 18px !important;
}}
.stSuccess {{ background: rgba(52,211,153,0.1) !important; border-left: 3px solid #34d399 !important; }}
.stError   {{ background: rgba(248,113,113,0.1) !important; border-left: 3px solid #f87171 !important; }}
.stWarning {{ background: rgba(251,191,36,0.1)  !important; border-left: 3px solid #fbbf24 !important; }}
.stInfo    {{ background: rgba(56,189,248,0.1)  !important; border-left: 3px solid #38bdf8 !important; }}

/* ═══════════════════════════════════════════════════════
   CODE BLOCKS
   ═══════════════════════════════════════════════════════ */
.stCode, code, pre {{
    font-family: var(--font-mono) !important;
    background: #040810 !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--cyan) !important;
    font-size: var(--fs-sm) !important;
}}

/* ═══════════════════════════════════════════════════════
   FILE UPLOADER
   ═══════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {{
    background: var(--bg-card) !important;
    border: 2px dashed var(--border-accent) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem !important;
    transition: border-color 0.3s ease, background 0.3s ease !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: var(--cyan) !important;
    background: rgba(56,189,248,0.04) !important;
}}
[data-testid="stFileUploaderDropzone"] p {{
    font-size: var(--fs-sm) !important;
    color: var(--text-secondary) !important;
}}

/* ═══════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════ */
.stProgress > div > div {{
    background: linear-gradient(90deg, var(--cyan), var(--violet)) !important;
    border-radius: 10px !important;
}}
.stProgress > div {{
    background: rgba(56,189,248,0.1) !important;
    border-radius: 10px !important;
}}

/* ═══════════════════════════════════════════════════════
   SPINNER
   ═══════════════════════════════════════════════════════ */
[data-testid="stSpinner"] {{ color: var(--cyan) !important; }}
[data-testid="stSpinner"] > div {{
    border-top-color: var(--cyan) !important;
    border-right-color: transparent !important;
}}

/* ═══════════════════════════════════════════════════════
   SCROLLBAR — PREMIUM THIN TRACK
   ═══════════════════════════════════════════════════════ */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: var(--bg-base); }}
::-webkit-scrollbar-thumb {{
    background: linear-gradient(180deg, rgba(56,189,248,0.3), rgba(56,189,248,0.1));
    border-radius: 10px;
}}
::-webkit-scrollbar-thumb:hover {{ background: rgba(56,189,248,0.5); }}

/* ═══════════════════════════════════════════════════════
   CHECKBOX & RADIO
   ═══════════════════════════════════════════════════════ */
[data-testid="stCheckbox"] label p,
[data-testid="stRadio"] label p {{
    font-size: var(--fs-sm) !important;
    color: var(--text-secondary) !important;
}}

/* ═══════════════════════════════════════════════════════
   DIVIDER
   ═══════════════════════════════════════════════════════ */
hr {{
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}}

/* ═══════════════════════════════════════════════════════
   PLOTLY MODEBAR
   ═══════════════════════════════════════════════════════ */
.js-plotly-plot .plotly .gtitle {{ display: none !important; }}
.modebar {{ background: transparent !important; }}
.modebar-btn path {{ fill: rgba(56,189,248,0.3) !important; }}
.modebar-btn:hover path {{ fill: var(--cyan) !important; }}

/* ═══════════════════════════════════════════════════════
   KEYFRAME ANIMATIONS
   ═══════════════════════════════════════════════════════ */
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeInLeft {{
    from {{ opacity: 0; transform: translateX(-20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes fadeInRight {{
    from {{ opacity: 0; transform: translateX(20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}
@keyframes pulseDot {{
    0%,100% {{ transform: scale(1);   opacity: 1;   box-shadow: 0 0 6px currentColor; }}
    50%      {{ transform: scale(1.6); opacity: 0.7; box-shadow: 0 0 18px currentColor; }}
}}
@keyframes shimmer {{
    0%   {{ background-position: -200% center; }}
    100% {{ background-position:  200% center; }}
}}
@keyframes scanPulse {{
    0%,100% {{ box-shadow: 0 0 10px rgba(56,189,248,0.15), inset 0 0 10px rgba(56,189,248,0.05); }}
    50%      {{ box-shadow: 0 0 36px rgba(56,189,248,0.45), inset 0 0 20px rgba(56,189,248,0.12); }}
}}
@keyframes glowBorder {{
    0%,100% {{ border-color: rgba(248,113,113,0.25); box-shadow: 0 0 0px rgba(248,113,113,0); }}
    50%      {{ border-color: rgba(248,113,113,0.60); box-shadow: 0 0 20px rgba(248,113,113,0.2); }}
}}
@keyframes floatUp {{
    0%,100% {{ transform: translateY(0);   }}
    50%      {{ transform: translateY(-6px); }}
}}
@keyframes radarPing {{
    0%   {{ transform: scale(0.8); opacity: 1; }}
    100% {{ transform: scale(2.8); opacity: 0; }}
}}
@keyframes rotateRing {{
    from {{ transform: rotate(0deg); }}
    to   {{ transform: rotate(360deg); }}
}}
@keyframes scanLine {{
    0%   {{ transform: translateY(-100%); }}
    100% {{ transform: translateY(200vh); }}
}}
@keyframes neonFlicker {{
    0%,100% {{ opacity: 1; }}
    92%      {{ opacity: 1; }}
    93%      {{ opacity: 0.4; }}
    94%      {{ opacity: 1; }}
    96%      {{ opacity: 0.6; }}
    97%      {{ opacity: 1; }}
}}
@keyframes gradientShift {{
    0%,100% {{ background-position: 0% 50%; }}
    50%      {{ background-position: 100% 50%; }}
}}
@keyframes countUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes borderGlow {{
    0%,100% {{ border-color: var(--border-accent); }}
    50%      {{ border-color: var(--border-strong); box-shadow: 0 0 24px var(--cyan-glow); }}
}}

/* ═══════════════════════════════════════════════════════
   REUSABLE COMPONENT CLASSES
   ═══════════════════════════════════════════════════════ */

/* Glass card base */
.vg-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.5rem 1.8rem;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    animation: fadeInUp 0.4s ease;
    position: relative;
    overflow: hidden;
}}
.vg-card::after {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: linear-gradient(135deg, rgba(56,189,248,0.02), transparent 60%);
    pointer-events: none;
}}
.vg-card:hover {{
    border-color: var(--border-accent);
    box-shadow: 0 0 40px var(--cyan-glow), 0 8px 32px rgba(0,0,0,0.3);
    transform: translateY(-2px);
}}

/* Elevated card */
.vg-card-elevated {{
    background: var(--bg-card);
    border: 1px solid var(--border-accent);
    border-radius: var(--radius-lg);
    padding: 2rem 2.2rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(56,189,248,0.06);
    animation: fadeInUp 0.5s ease;
}}

/* Stat badge */
.stat-badge {{
    animation: fadeInUp 0.5s ease;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    cursor: default;
}}
.stat-badge:hover {{
    transform: translateY(-6px) scale(1.03) !important;
    box-shadow: 0 20px 48px rgba(0,0,0,0.55) !important;
}}

/* Kill chain pills */
.kc-pill {{
    display: inline-flex;
    align-items: center;
    padding: 5px 14px;
    border-radius: 20px;
    font-family: var(--font-mono);
    font-size: var(--fs-xs);
    font-weight: 600;
    letter-spacing: 0.05em;
    white-space: nowrap;
    transition: all 0.2s ease;
}}
.kc-pill:hover {{ transform: translateY(-2px); }}

/* Stack rows */
.stack-row {{
    transition: all 0.2s ease !important;
    border-radius: var(--radius-sm) !important;
}}
.stack-row:hover {{
    background: rgba(56,189,248,0.07) !important;
    transform: translateX(5px) !important;
    border-left-width: 3px !important;
}}

/* Capability list items */
.cap-item {{
    transition: all 0.2s ease !important;
    border-radius: 6px;
}}
.cap-item:hover {{
    background: rgba(56,189,248,0.07) !important;
    transform: translateX(5px) !important;
}}

/* About cards */
.about-cap-card   {{ animation: fadeInLeft  0.6s ease; }}
.about-stack-card {{ animation: fadeInRight 0.6s ease; }}

/* Section divider line */
.vg-divider {{
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, var(--border-strong), rgba(56,189,248,0.04), transparent);
    margin-bottom: 2rem;
}}

/* Live indicator badge */
.live-badge {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(52,211,153,0.1);
    border: 1px solid rgba(52,211,153,0.25);
    border-radius: 20px;
    padding: 5px 14px;
    font-family: var(--font-mono);
    font-size: 12px;
    color: #34d399;
    letter-spacing: 0.1em;
    font-weight: 600;
    animation: fadeIn 0.5s ease;
}}

/* Hero number */
.hero-number {{
    font-family: var(--font-display) !important;
    font-weight: 900 !important;
    letter-spacing: -0.04em !important;
    line-height: 1 !important;
    animation: countUp 0.6s ease !important;
}}

/* Threat level indicator line */
.threat-bar-track {{
    width: 100%;
    height: 6px;
    background: rgba(56,189,248,0.1);
    border-radius: 6px;
    overflow: hidden;
}}
.threat-bar-fill {{
    height: 6px;
    border-radius: 6px;
    transition: width 1s cubic-bezier(0.4,0,0.2,1);
}}

/* Top banner ticker */
.vg-ticker-wrap {{
    overflow: hidden;
    white-space: nowrap;
}}
@keyframes ticker {{
    from {{ transform: translateX(0); }}
    to   {{ transform: translateX(-50%); }}
}}
.vg-ticker-inner {{
    display: inline-block;
    animation: ticker 30s linear infinite;
}}

/* Card with shimmer top-border accent */
.vg-shimmer-card {{
    position: relative;
    overflow: hidden;
}}
.vg-shimmer-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--violet), var(--cyan));
    background-size: 200%;
    animation: shimmer 3s linear infinite;
}}

/* Floating action button style */
.vg-fab {{
    display: inline-flex;
    align-items: center;
    gap: 9px;
    background: var(--btn-gradient);
    color: #fff;
    padding: 11px 22px;
    border-radius: 12px;
    font-family: var(--font-body);
    font-size: var(--fs-sm);
    font-weight: 600;
    letter-spacing: 0.03em;
    cursor: pointer;
    box-shadow: var(--btn-shadow);
    transition: all 0.25s ease;
    text-decoration: none;
    border: none;
}}
.vg-fab:hover {{
    box-shadow: var(--btn-hover-shadow);
    transform: translateY(-2px) scale(1.02);
}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTS
# =========================================================

ALERTS_FILE = "data/detected_alerts.csv"
LOGS_FILE   = "data/synthetic_logs.csv"

import os

# Force fresh session on every app restart
for file in [
    "data/detected_alerts.csv",
    "data/synthetic_logs.csv"
]:
    if os.path.exists(file):
        os.remove(file)
        
SEVERITY_COLORS = {
    "Critical": "#f87171",
    "High":     "#fbbf24",
    "Medium":   "#a78bfa",
    "Low":      "#34d399",
}
SEVERITY_DIM = {
    "Critical": "rgba(248,113,113,0.15)",
    "High":     "rgba(251,191,36,0.15)",
    "Medium":   "rgba(167,139,250,0.15)",
    "Low":      "rgba(52,211,153,0.15)",
}

def make_plotly_theme():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, JetBrains Mono, monospace", color="#a8b8d4", size=13),
        xaxis=dict(
            gridcolor="#0d1628",
            zerolinecolor="#0d1628",
            tickfont=dict(color="#a8b8d4", size=12),
            title_font=dict(color="#a8b8d4", size=13),
            showline=False,
        ),
        yaxis=dict(
            gridcolor="#0d1628",
            zerolinecolor="#0d1628",
            tickfont=dict(color="#a8b8d4", size=12),
            title_font=dict(color="#a8b8d4", size=13),
            showline=False,
        ),
        title=dict(text="", font=dict(family="Orbitron, Syne", color="#f0f4ff", size=1)),
        colorway=["#38bdf8", "#a78bfa", "#fbbf24", "#f87171", "#34d399", "#ec4899", "#fb923c"],
        margin=dict(l=40, r=20, t=24, b=40),
        legend=dict(
            font=dict(color="#a8b8d4", size=12),
            bgcolor="rgba(0,0,0,0)",
        )
    )

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def apply_theme(fig):
    fig.update_layout(**make_plotly_theme())
    return fig


def severity_badge(level: str) -> str:
    color = SEVERITY_COLORS.get(level, "#8b9ab5")
    bg    = SEVERITY_DIM.get(level, "rgba(139,154,181,0.12)")
    icons = {"Critical": "●", "High": "●", "Medium": "●", "Low": "●"}
    icon  = icons.get(level, "●")
    return (
        f'<span style="background:{bg};color:{color};border:1px solid {color}44;'
        f'padding:4px 14px 4px 10px;border-radius:20px;font-size:13px;'
        f'font-family:\'JetBrains Mono\',monospace;font-weight:600;letter-spacing:0.06em;'
        f'display:inline-flex;align-items:center;gap:6px;animation:pulseDot 3s infinite;">'
        f'<span style="color:{color};animation:pulseDot 2s infinite;font-size:10px;">{icon}</span>'
        f' {level.upper()}</span>'
    )


def risk_bar(score: float, max_score: float = 100) -> str:
    pct = min(int(score / max_score * 100), 100)
    if score >= 80:   color = "#f87171"
    elif score >= 60: color = "#fbbf24"
    elif score >= 40: color = "#a78bfa"
    else:             color = "#34d399"
    return (
        f'<div style="display:flex;align-items:center;gap:12px;">'
        f'<div style="flex:1;background:rgba(56,189,248,0.08);border-radius:6px;height:8px;overflow:hidden;">'
        f'<div style="width:{pct}%;background:linear-gradient(90deg,{color}88,{color});'
        f'height:8px;border-radius:6px;box-shadow:0 0 12px {color}66;'
        f'transition:width 0.8s cubic-bezier(0.4,0,0.2,1);"></div></div>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:14px;color:{color};'
        f'font-weight:700;min-width:36px;">{int(score)}</span></div>'
    )


def page_header(icon: str, title: str, subtitle: str = ""):
    subtitle_html = (
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:12px;'
        f'color:var(--text-muted);margin-top:5px;letter-spacing:0.14em;">{subtitle}</div>'
        if subtitle else ""
    )
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:18px;margin-bottom:1rem;animation:fadeInLeft 0.5s ease;">
        <div style="width:54px;height:54px;
                    background:linear-gradient(135deg,rgba(56,189,248,0.20),rgba(56,189,248,0.05));
                    border:1px solid var(--border-accent);border-radius:14px;
                    display:flex;align-items:center;justify-content:center;font-size:1.6rem;
                    box-shadow:0 0 28px var(--cyan-glow);animation:scanPulse 4s ease infinite;
                    flex-shrink:0;">{icon}</div>
        <div>
            <div style="font-family:'Orbitron','Syne',sans-serif;font-size:{T['fs_2xl']};font-weight:800;
                        color:var(--text-primary);letter-spacing:-0.01em;line-height:1.1;">{title}</div>
            {subtitle_html}
        </div>
    </div>
    <div class="vg-divider"></div>
    """, unsafe_allow_html=True)


def glass_card(content_html: str, accent: str = "var(--cyan-glow)", border_color: str = "var(--border)"):
    st.markdown(f"""
    <div style="background:var(--bg-card);border:1px solid {border_color};border-radius:var(--radius-md);
                padding:1.6rem 2rem;box-shadow:0 0 40px {accent};animation:fadeInUp 0.4s ease;">
        {content_html}
    </div>
    """, unsafe_allow_html=True)


def section_label(text: str, color: str = "var(--text-muted)"):
    st.markdown(f"""
    <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:{color};
                letter-spacing:0.18em;text-transform:uppercase;margin-bottom:14px;
                display:flex;align-items:center;gap:8px;">
        <span style="display:inline-block;width:14px;height:1px;background:{color};opacity:0.7;"></span>
        {text}
        <span style="display:inline-block;flex:1;height:1px;background:linear-gradient(90deg,{color}40,transparent);opacity:0.4;"></span>
    </div>""", unsafe_allow_html=True)


def no_data_state(message: str = "No Data Available", hint: str = ""):
    hint_html = (
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:14px;'
        f'color:var(--text-muted);margin-top:10px;">{hint}</div>'
        if hint else ""
    )
    glass_card(f"""
    <div style="text-align:center;padding:4rem 0;">
        <div style="font-size:3.6rem;margin-bottom:20px;filter:opacity(0.35);animation:floatUp 3s ease infinite;">📡</div>
        <div style="font-family:'Orbitron','Syne',sans-serif;font-weight:700;font-size:18px;
                    color:var(--text-primary);">{message}</div>
        {hint_html}
    </div>""")


def map_kill_chain_stage(row) -> tuple:
    action    = str(row.get("action", "")).lower()
    file_path = str(row.get("file_path", "")).lower()
    stages = [
        (["scan","browse","enumerate"],                          "Reconnaissance",        "#38bdf8"),
        (["login_fail","vpn_login","new_login"],                 "Initial Access",         "#fbbf24"),
        (["admin_access","privilege_change","role_change"],      "Privilege Escalation",  "#f87171"),
        (["remote_access","server_access","lateral_move"],       "Lateral Movement",      "#fb923c"),
        (["create_account","backup_admin","persistence"],        "Persistence",            "#a78bfa"),
        (["download","bulk_export","usb_copy"],                  "Data Exfiltration",     "#f87171"),
        (["delete_logs","clear_history","disable_monitoring"],   "Defense Evasion",       "#ec4899"),
    ]
    for keywords, label, color in stages:
        if any(k in action for k in keywords):
            return label, color
    if any(k in file_path for k in ["confidential","finance","salary","payroll","admin"]):
        return "Sensitive Data Targeting", "#fbbf24"
    return "Behavioral Anomaly", "#a78bfa"


def explain_detection_and_recommendation(row):
    reasons = []
    actions = []
    try:
        hour = pd.to_datetime(row["timestamp"]).hour
        if hour < 6 or hour > 22:
            reasons.append("Unusual login time detected (outside normal working hours)")
            actions.append("Enforce after-hours MFA verification")
    except Exception:
        pass

    sensitive_keywords = ["salary","finance","confidential","admin","payroll","customer","backup"]
    file_path = str(row.get("file_path", "")).lower()
    if any(k in file_path for k in sensitive_keywords):
        reasons.append("Sensitive or privileged file access observed")
        actions.append("Trigger manager approval for sensitive file access")

    suspicious_locations = ["remote","unknown","outside","vpn"]
    location = str(row.get("location", "")).lower()
    if any(loc in location for loc in suspicious_locations):
        reasons.append("Login from unusual or suspicious access location")
        actions.append("Temporarily restrict VPN / remote access")

    action = str(row.get("action", "")).lower()
    if "privilege" in action:
        reasons.append("Privilege escalation attempt detected")
        actions.append("Require admin approval for privilege elevation")
    elif "admin" in action:
        reasons.append("Unauthorized privileged administrative access detected")
        actions.append("Suspend privileged account and trigger SOC escalation")
    elif "bulk_export" in action:
        reasons.append("Mass sensitive data export behavior observed")
        actions.append("Block export action and initiate DLP review")
    elif "delete" in action:
        reasons.append("Potential defense evasion activity detected")
        actions.append("Preserve forensic logs and restrict deletion privileges")
    elif "logout" in action:
        reasons.append("Suspicious logout behavior following sensitive activity")
        actions.append("Trigger post-session behavioral investigation")

    if row.get("severity", "") == "Critical":
        reasons.append("Critical severity threshold exceeded")
        actions.append("Temporarily suspend privileged account access")

    if not reasons:
        reasons.append("Behavior deviates from established UEBA baseline")
        actions.append("Continue monitoring and initiate manager verification")

    return list(dict.fromkeys(reasons)), list(dict.fromkeys(actions))


def generate_pdf_report(row, reasons, actions, explanation):
    try:
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer
        )
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4

        user_id       = row.get("user_id", "UNKNOWN")
        severity      = row.get("severity", "Unknown")
        risk_score    = row.get("risk_score", 0)
        action        = row.get("action", "Unknown")
        location      = row.get("location", "Unknown")
        device        = row.get("device", "Unknown")
        file_accessed = row.get("file_path", "N/A")

        os.makedirs("reports", exist_ok=True)
        file_path = f"reports/VEILGuard_Executive_Report_{user_id}.pdf"
        styles    = getSampleStyleSheet()
        doc       = SimpleDocTemplate(file_path, pagesize=A4)
        content   = []

        content.append(Paragraph("VEILGuard Executive SOC Investigation Report", styles["Title"]))
        content.append(Spacer(1, 14))
        content.append(Paragraph("AI-Powered Insider Risk Detection & Threat Analysis", styles["Heading3"]))
        content.append(Spacer(1, 18))
        summary_text = (
            f"<b>Executive Summary</b><br/><br/>"
            f"This report identifies suspicious insider activity associated with user <b>{user_id}</b>. "
            f"The detected behavior indicates potential enterprise security risk requiring administrative review. "
            f"Based on anomaly detection, behavioral analysis, and AI-assisted investigation, this event has been "
            f"classified as <b>{severity}</b> severity with a calculated risk score of <b>{risk_score}</b>."
        )
        content.append(Paragraph(summary_text, styles["BodyText"]))
        content.append(Spacer(1, 16))
        incident_details = (
            f"<b>Incident Details</b><br/><br/>"
            f"<b>User ID:</b> {user_id}<br/>"
            f"<b>Severity:</b> {severity}<br/>"
            f"<b>Risk Score:</b> {risk_score}<br/>"
            f"<b>Suspicious Action:</b> {action}<br/>"
            f"<b>Location:</b> {location}<br/>"
            f"<b>Device:</b> {device}<br/>"
            f"<b>File Accessed:</b> {file_accessed}<br/>"
        )
        content.append(Paragraph(incident_details, styles["BodyText"]))
        content.append(Spacer(1, 16))
        content.append(Paragraph("<b>Why This Alert Was Flagged</b>", styles["Heading3"]))
        content.append(Spacer(1, 6))
        for r in reasons:
            content.append(Paragraph(f"• {r}", styles["BodyText"]))
        content.append(Spacer(1, 14))
        content.append(Paragraph("<b>Administrative Recommended Actions</b>", styles["Heading3"]))
        content.append(Spacer(1, 6))
        for a in actions:
            content.append(Paragraph(f"• {a}", styles["BodyText"]))
        content.append(Spacer(1, 14))
        content.append(Paragraph("<b>AI SOC Analyst Investigation</b>", styles["Heading3"]))
        content.append(Spacer(1, 6))
        safe_explanation = str(explanation).replace("\n", "<br/>")
        content.append(Paragraph(safe_explanation, styles["BodyText"]))
        content.append(Spacer(1, 20))
        footer = Paragraph(
            "<i>Generated by VEILGuard — Enterprise Insider Threat Detection Platform<br/>"
            "This report is AI-assisted and intended for security review, not final disciplinary action without human validation.</i>",
            styles["BodyText"]
        )
        content.append(footer)
        doc.build(content)
        return file_path, None
    except Exception as e:
        return None, str(e)


def run_detection_engine():
    try:
        os.makedirs("data", exist_ok=True)
        if not os.path.exists("data/synthetic_logs.csv"):
            return False, "No input log file found at data/synthetic_logs.csv"
        result = subprocess.run(
            [sys.executable, "detector.py"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode == 0:
            return True, result.stdout
        return False, result.stderr if result.stderr else result.stdout
    except Exception as e:
        return False, str(e)


# =========================================================
# DATA LOADERS
# =========================================================

# @st.cache_data
def load_alerts():
    if os.path.exists(ALERTS_FILE):
        try:
            df = pd.read_csv(ALERTS_FILE)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            return df
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


# @st.cache_data
def load_logs():
    if os.path.exists(LOGS_FILE):
        try:
            df = pd.read_csv(LOGS_FILE)
            column_map = {
                "employee_name": "user_id", "username": "user_id", "user": "user_id",
                "event_time": "timestamp", "time": "timestamp",
                "event_type": "action", "event": "action",
                "login_city": "location", "city": "location",
                "endpoint_name": "device", "host": "device",
                "file_name": "file_path", "file": "file_path",
            }
            df.columns = [str(c).strip().lower() for c in df.columns]
            for old, new in column_map.items():
                if old in df.columns and new not in df.columns:
                    df.rename(columns={old: new}, inplace=True)
            if "timestamp" not in df.columns:
                df["timestamp"] = pd.Timestamp.now()
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            return df
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


alerts_df = load_alerts()
logs_df   = load_logs()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    # ── Logo & Brand ──────────────────────────────────────
    st.markdown("""
    <div style="padding:2rem 1.2rem 1.6rem;border-bottom:1px solid rgba(56,189,248,0.12);
                margin-bottom:1.4rem;position:relative;overflow:hidden;">
        <!-- Glow orb behind logo -->
        <div style="position:absolute;top:-20px;right:-20px;width:120px;height:120px;
                    background:radial-gradient(circle,rgba(56,189,248,0.12),transparent 70%);
                    pointer-events:none;"></div>
        <div style="display:flex;align-items:center;gap:14px;position:relative;">
            <div style="position:relative;flex-shrink:0;">
                <!-- Radar ping ring -->
                <div style="position:absolute;top:50%;left:50%;
                            transform:translate(-50%,-50%);
                            width:56px;height:56px;border-radius:50%;
                            border:2px solid rgba(56,189,248,0.3);
                            animation:radarPing 2.5s ease-out infinite;"></div>
                <div style="width:46px;height:46px;
                            background:linear-gradient(135deg,#0ea5e9,#2563eb,#4f46e5);
                            border-radius:14px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.4rem;
                            box-shadow:0 4px 24px rgba(14,165,233,0.5),inset 0 1px 0 rgba(255,255,255,0.15);
                            animation:scanPulse 3s ease infinite;
                            position:relative;z-index:1;">🛡️</div>
            </div>
            <div>
                <div style="font-family:'Orbitron','Syne',sans-serif;font-weight:900;font-size:1.25rem;
                            color:#f0f4ff;letter-spacing:0.04em;animation:neonFlicker 8s ease infinite;">
                    VEIL<span style="color:#38bdf8;text-shadow:0 0 14px rgba(56,189,248,0.6);">Guard</span>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#5a6e8a;
                            letter-spacing:0.18em;margin-top:3px;text-transform:uppercase;">
                    Insider Risk Platform
                </div>
            </div>
        </div>
        <!-- Version tag -->
        <div style="margin-top:14px;display:inline-flex;align-items:center;gap:7px;
                    background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.18);
                    border-radius:20px;padding:4px 12px;">
            <span style="width:6px;height:6px;border-radius:50%;background:#34d399;
                         box-shadow:0 0 8px #34d399;animation:pulseDot 2s infinite;
                         display:inline-block;"></span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#a8b8d4;
                         letter-spacing:0.1em;">v2.0 · ENTERPRISE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Nav label ─────────────────────────────────────────
    st.markdown(
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#5a6e8a;'
        'letter-spacing:0.2em;padding:0 14px;margin-bottom:6px;text-transform:uppercase;">Navigation</div>',
        unsafe_allow_html=True
    )

    selected = st.radio(
        "Navigation",
        [
            "🏠  Dashboard Overview",
            "🚨  Live Monitor & Alerts",
            "👤  User Behavior Profiles",
            "⚡  What-If Simulator",
            "🧪  Synthetic Data Generator",
            "ℹ️  About VEILGuard"
        ],
        label_visibility="collapsed"
    )

    # ── System Status ─────────────────────────────────────
    st.markdown("""
    <div style="margin-top:2rem;padding:0 0.5rem;">
        <div style="background:linear-gradient(135deg,rgba(8,14,28,0.98),rgba(12,20,36,0.98));
                    border:1px solid rgba(56,189,248,0.12);
                    border-radius:14px;padding:1.2rem 1.3rem;
                    box-shadow:0 4px 24px rgba(0,0,0,0.3),inset 0 1px 0 rgba(56,189,248,0.05);">
            <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#5a6e8a;
                        letter-spacing:0.18em;margin-bottom:14px;text-transform:uppercase;
                        display:flex;align-items:center;gap:8px;">
                <span style="width:12px;height:1px;background:#5a6e8a;display:inline-block;"></span>
                System Status
            </div>
            <div style="display:flex;flex-direction:column;gap:10px;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="width:8px;height:8px;background:#34d399;border-radius:50%;
                                    box-shadow:0 0 10px #34d399;animation:pulseDot 2s infinite;"></div>
                        <span style="font-family:'DM Sans',sans-serif;font-size:14px;color:#a8b8d4;font-weight:500;">Detection Engine</span>
                    </div>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                 color:#34d399;background:rgba(52,211,153,0.1);
                                 border-radius:10px;padding:2px 8px;">ONLINE</span>
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="width:8px;height:8px;background:#34d399;border-radius:50%;
                                    box-shadow:0 0 10px #34d399;animation:pulseDot 2s infinite 0.4s;"></div>
                        <span style="font-family:'DM Sans',sans-serif;font-size:14px;color:#a8b8d4;font-weight:500;">Groq AI Engine</span>
                    </div>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                 color:#34d399;background:rgba(52,211,153,0.1);
                                 border-radius:10px;padding:2px 8px;">ONLINE</span>
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="width:8px;height:8px;background:#fbbf24;border-radius:50%;
                                    box-shadow:0 0 10px #fbbf24;animation:pulseDot 2s infinite 0.8s;"></div>
                        <span style="font-family:'DM Sans',sans-serif;font-size:14px;color:#a8b8d4;font-weight:500;">UEBA Monitor</span>
                    </div>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                 color:#fbbf24;background:rgba(251,191,36,0.1);
                                 border-radius:10px;padding:2px 8px;">STANDBY</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Critical alert banner in sidebar ──────────────────
    if not alerts_df.empty:
        critical_count = len(alerts_df[alerts_df["severity"] == "Critical"]) if "severity" in alerts_df.columns else 0
        if critical_count > 0:
            st.markdown(f"""
            <div style="margin-top:1.4rem;padding:0 0.5rem;">
                <div style="background:linear-gradient(135deg,rgba(248,113,113,0.12),rgba(248,113,113,0.06));
                            border:1px solid rgba(248,113,113,0.35);
                            border-radius:14px;padding:1.1rem 1.3rem;
                            animation:glowBorder 2s ease infinite;
                            position:relative;overflow:hidden;">
                    <div style="position:absolute;top:0;left:0;right:0;height:2px;
                                background:linear-gradient(90deg,#f87171,#fbbf24,#f87171);
                                background-size:200%;animation:shimmer 2s linear infinite;"></div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#f87171;
                                letter-spacing:0.16em;margin-bottom:8px;text-transform:uppercase;">⚠ Critical Alerts</div>
                    <div style="font-family:'Orbitron','Syne',sans-serif;font-size:2rem;font-weight:900;
                                color:#f87171;text-shadow:0 0 20px rgba(248,113,113,0.4);
                                line-height:1;">{critical_count}</div>
                    <div style="font-family:'DM Sans',sans-serif;font-size:14px;color:rgba(248,113,113,0.7);
                                margin-top:4px;">Require immediate review</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Sidebar footer ─────────────────────────────────────
    st.markdown("""
    <div style="margin-top:2.5rem;padding:0 0.5rem;">
        <div style="border-top:1px solid rgba(56,189,248,0.08);padding-top:1.2rem;
                    font-family:'JetBrains Mono',monospace;font-size:11px;color:#5a6e8a;
                    text-align:center;letter-spacing:0.08em;line-height:1.9;">
            <div style="margin-bottom:4px;">MITRE ATT&CK™ Aligned</div>
            <div>ISO 27001 · SOC 2 Ready</div>
            <div style="margin-top:8px;color:#38bdf8;opacity:0.5;">VEILGuard © 2025</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PAGE ROUTING
# =========================================================

_page = selected.split("  ", 1)[-1].strip() if "  " in selected else selected.strip()

# =========================================================
# DASHBOARD OVERVIEW
# =========================================================

if _page == "Dashboard Overview":

    page_header("🏠", "Dashboard Overview", "REAL-TIME THREAT INTELLIGENCE  ·  SOC COMMAND CENTER  ·  UEBA ANALYTICS")

    # ── Live status ticker ───────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:2rem;
                padding:13px 20px;
                background:linear-gradient(135deg,rgba(12,20,36,0.95),rgba(8,14,28,0.95));
                border:1px solid rgba(56,189,248,0.14);
                border-radius:12px;overflow:hidden;position:relative;">
        <div style="position:absolute;top:0;left:0;right:0;height:1px;
                    background:linear-gradient(90deg,transparent,rgba(56,189,248,0.4),transparent);"></div>
        <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;
                    background:rgba(52,211,153,0.12);border:1px solid rgba(52,211,153,0.25);
                    border-radius:20px;padding:5px 14px;">
            <span style="width:7px;height:7px;border-radius:50%;background:#34d399;
                         box-shadow:0 0 10px #34d399;animation:pulseDot 2s infinite;
                         display:inline-block;"></span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:12px;
                         color:#34d399;font-weight:600;letter-spacing:0.1em;">LIVE</span>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#a8b8d4;
                    display:flex;gap:20px;flex-wrap:wrap;">
            <span>MONITORING ACTIVE</span>
            <span style="color:rgba(56,189,248,0.3);">|</span>
            <span>IAM SECURITY</span>
            <span style="color:rgba(56,189,248,0.3);">|</span>
            <span>UEBA ENGINE</span>
            <span style="color:rgba(56,189,248,0.3);">|</span>
            <span>INSIDER RISK PLATFORM</span>
            <span style="color:rgba(56,189,248,0.3);">|</span>
            <span>MITRE ATT&CK™ ALIGNED</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    total_users    = logs_df["user_id"].nunique()   if not logs_df.empty   else 0
    total_alerts   = len(alerts_df)
    critical_count = 0
    high_count     = 0
    avg_risk_score = 0.0

    if not alerts_df.empty and "severity" in alerts_df.columns:
        critical_count = len(alerts_df[alerts_df["severity"] == "Critical"])
        high_count     = len(alerts_df[alerts_df["severity"] == "High"])
        if "risk_score" in alerts_df.columns:
            avg_risk_score = round(alerts_df["risk_score"].mean(), 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("MONITORED USERS", f"{total_users:,}", help="Active users in UEBA baseline")
    with c2:
        st.metric("TOTAL ALERTS", f"{total_alerts:,}", help="All flagged anomalous events")
    with c3:
        st.metric("⬤ CRITICAL", f"{critical_count:,}", help="Users with Critical severity flags")
    with c4:
        st.metric("🟠 HIGH", f"{high_count:,}", help="High-severity behavioral deviations")
    with c5:
        st.metric("AVG RISK SCORE", f"{avg_risk_score}", help="Mean risk across flagged users")

    st.markdown("<br>", unsafe_allow_html=True)

    if alerts_df.empty:
        no_data_state("No Alert Data Found", "Run detector.py to populate the detection pipeline")
    else:
        col_bar, col_pie, col_action = st.columns([1.4, 1, 1], gap="medium")

        with col_bar:
            section_label("Alert Severity Distribution")
            sev_order  = ["Critical", "High", "Medium", "Low"]
            sev_counts = (
                alerts_df["severity"].value_counts()
                .reindex(sev_order).fillna(0).reset_index()
            )
            sev_counts.columns = ["severity", "count"]

            fig_sev = go.Figure()
            for _, r in sev_counts.iterrows():
                col = SEVERITY_COLORS.get(r["severity"], "#8b9ab5")
                fig_sev.add_trace(go.Bar(
                    x=[r["severity"]], y=[r["count"]],
                    marker_color=col,
                    marker_line_width=0,
                    name=r["severity"],
                    hovertemplate=f"<b>{r['severity']}</b><br>Alerts: {int(r['count'])}<extra></extra>"
                ))
            apply_theme(fig_sev)
            fig_sev.update_layout(
                showlegend=False, barmode="stack",
                height=280, xaxis_title="", yaxis_title="Alert Count",
            )
            st.plotly_chart(fig_sev, use_container_width=True)

        with col_pie:
            section_label("Severity Breakdown")
            fig_pie = px.pie(
                sev_counts, names="severity", values="count", hole=0.68,
                color="severity", color_discrete_map=SEVERITY_COLORS,
            )
            apply_theme(fig_pie)
            fig_pie.update_traces(
                textposition="outside", textinfo="percent+label",
                textfont=dict(color="#a8b8d4", size=12),
                hovertemplate="<b>%{label}</b><br>%{value} alerts<br>%{percent}<extra></extra>",
                marker=dict(line=dict(color="#04080f", width=3))
            )
            fig_pie.update_layout(
                showlegend=False, height=280,
                annotations=[dict(
                    text="ALERTS", x=0.5, y=0.5,
                    font=dict(family="JetBrains Mono", size=11, color="#5a6e8a"),
                    showarrow=False
                )]
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_action:
            section_label("Top Actions Flagged")
            if "action" in alerts_df.columns:
                top_actions = alerts_df["action"].value_counts().head(6).reset_index()
                top_actions.columns = ["action", "count"]
                fig_act = px.bar(
                    top_actions, x="count", y="action", orientation="h",
                    color_discrete_sequence=["#38bdf8"]
                )
                apply_theme(fig_act)
                fig_act.update_traces(
                    marker_line_width=0,
                    hovertemplate="<b>%{y}</b><br>%{x} events<extra></extra>"
                )
                fig_act.update_layout(
                    showlegend=False, height=280,
                    xaxis_title="Events", yaxis_title="",
                    yaxis=dict(categoryorder="total ascending")
                )
                st.plotly_chart(fig_act, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        section_label("Alert Activity Timeline")
        if "timestamp" in alerts_df.columns:
            ts_df = alerts_df.dropna(subset=["timestamp"])
            if not ts_df.empty:
                timeline_df = (
                    ts_df.set_index("timestamp")
                    .resample("1h").size().reset_index(name="alerts")
                )
                fig_time = go.Figure()
                fig_time.add_trace(go.Scatter(
                    x=timeline_df["timestamp"], y=timeline_df["alerts"],
                    mode="lines", fill="tozeroy",
                    line=dict(color="#38bdf8", width=2.5),
                    fillcolor="rgba(56,189,248,0.07)",
                    hovertemplate="<b>%{x}</b><br>Alerts: %{y}<extra></extra>"
                ))
                apply_theme(fig_time)
                fig_time.update_layout(
                    showlegend=False, height=220,
                    xaxis_title="", yaxis_title="Alerts / Hour",
                )
                st.plotly_chart(fig_time, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_dist, col_top = st.columns([1, 1.3], gap="medium")

        with col_dist:
            section_label("Risk Score Distribution")
            if "risk_score" in alerts_df.columns:
                fig_hist = px.histogram(
                    alerts_df, x="risk_score", nbins=20,
                    color_discrete_sequence=["#a78bfa"]
                )
                apply_theme(fig_hist)
                fig_hist.update_traces(
                    marker_line_width=0,
                    hovertemplate="Risk %{x}<br>Count: %{y}<extra></extra>"
                )
                fig_hist.update_layout(
                    showlegend=False, height=320,
                    xaxis_title="Risk Score", yaxis_title="Frequency",
                )
                st.plotly_chart(fig_hist, use_container_width=True)

        with col_top:
            section_label("🔴 Top 10 High-Risk Actors")
            if "user_id" in alerts_df.columns and "risk_score" in alerts_df.columns:
                top_users = (
                    alerts_df.groupby("user_id")["risk_score"]
                    .mean().sort_values(ascending=False).head(10).reset_index()
                )
                top_users["risk_score"] = top_users["risk_score"].round(1)

                rows_html = ""
                for i, row in top_users.iterrows():
                    rank_color = "#f87171" if i < 3 else ("#fbbf24" if i < 6 else "#a8b8d4")
                    medal = ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"
                    rows_html += f"""
                    <tr style="border-bottom:1px solid rgba(56,189,248,0.06);
                               transition:background 0.2s ease;"
                        onmouseover="this.style.background='rgba(56,189,248,0.04)'"
                        onmouseout="this.style.background='transparent'">
                        <td style="padding:11px 16px;font-family:'JetBrains Mono',monospace;font-size:14px;
                                   color:{rank_color};font-weight:700;">{medal}</td>
                        <td style="padding:11px 16px;font-family:'JetBrains Mono',monospace;font-size:14px;
                                   color:#f0f4ff;font-weight:500;">{row['user_id']}</td>
                        <td style="padding:11px 16px;min-width:200px;">{risk_bar(row['risk_score'])}</td>
                    </tr>"""

                st.markdown(f"""
                <div style="background:var(--bg-card);border:1px solid var(--border-accent);
                            border-radius:var(--radius-md);overflow:hidden;
                            box-shadow:0 4px 24px rgba(0,0,0,0.3);">
                    <table style="width:100%;border-collapse:collapse;">
                        <thead>
                            <tr style="background:#060c1a;border-bottom:1px solid var(--border-accent);">
                                <th style="padding:11px 16px;text-align:left;font-family:'JetBrains Mono',monospace;
                                           font-size:11px;color:var(--text-muted);letter-spacing:0.16em;">RANK</th>
                                <th style="padding:11px 16px;text-align:left;font-family:'JetBrains Mono',monospace;
                                           font-size:11px;color:var(--text-muted);letter-spacing:0.16em;">USER ID</th>
                                <th style="padding:11px 16px;text-align:left;font-family:'JetBrains Mono',monospace;
                                           font-size:11px;color:var(--text-muted);letter-spacing:0.16em;">RISK SCORE</th>
                            </tr>
                        </thead>
                        <tbody>{rows_html}</tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_dept, col_loc = st.columns(2, gap="medium")
        with col_dept:
            section_label("User Activity by Location")
            if "location" in alerts_df.columns:
                loc_counts = alerts_df["location"].value_counts().head(10).reset_index()
                loc_counts.columns = ["location", "count"]
                fig_loc = px.bar(
                    loc_counts, x="location", y="count",
                    color="count", color_continuous_scale=["#0e1a30","#0ea5e9","#f87171"]
                )
                apply_theme(fig_loc)
                fig_loc.update_layout(showlegend=False, height=280, coloraxis_showscale=False,
                                       xaxis_title="", yaxis_title="Alerts")
                st.plotly_chart(fig_loc, use_container_width=True)

        with col_loc:
            section_label("Device Risk Analysis")
            if "device" in alerts_df.columns and "risk_score" in alerts_df.columns:
                device_risk = (
                    alerts_df.groupby("device")["risk_score"]
                    .mean().sort_values(ascending=False).head(8).reset_index()
                )
                fig_dev = px.bar(
                    device_risk, x="risk_score", y="device", orientation="h",
                    color="risk_score", color_continuous_scale=["#34d399","#fbbf24","#f87171"]
                )
                apply_theme(fig_dev)
                fig_dev.update_layout(showlegend=False, height=280, coloraxis_showscale=False,
                                       xaxis_title="Avg Risk Score", yaxis_title="")
                st.plotly_chart(fig_dev, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section_label("Threat Activity Heatmap — Hour × Action Type")
        if "timestamp" in alerts_df.columns and "action" in alerts_df.columns:
            heat_df = alerts_df.dropna(subset=["timestamp"]).copy()
            heat_df["hour"] = heat_df["timestamp"].dt.hour
            heat_pivot = heat_df.groupby(["action", "hour"]).size().unstack(fill_value=0)
            if not heat_pivot.empty:
                top_actions = heat_df["action"].value_counts().head(8).index.tolist()
                heat_pivot  = heat_pivot.loc[heat_pivot.index.isin(top_actions)]
                fig_heat = go.Figure(go.Heatmap(
                    z=heat_pivot.values,
                    x=[f"{h:02d}:00" for h in heat_pivot.columns],
                    y=heat_pivot.index.tolist(),
                    colorscale=[
                        [0, "#04080f"],
                        [0.3, "rgba(14,165,233,0.38)"],
                        [0.7, "rgba(167,139,250,0.50)"],
                        [1, "#f87171"]
                    ],
                    hovertemplate="<b>%{y}</b><br>Hour: %{x}<br>Events: %{z}<extra></extra>",
                    showscale=False,
                ))
                apply_theme(fig_heat)
                fig_heat.update_layout(height=280, xaxis_title="Hour of Day", yaxis_title="")
                st.plotly_chart(fig_heat, use_container_width=True)

# =========================================================
# LIVE MONITOR & ALERTS
# =========================================================

elif _page == "Live Monitor & Alerts":

    page_header("🚨", "Live Monitor & Alerts", "REAL-TIME ALERT FEED  ·  KILL CHAIN MAPPING  ·  AI SOC INVESTIGATION")

    if alerts_df.empty:
        no_data_state("No Alert Data Found", "Run detector.py to populate the detection pipeline")
    else:
        sev_counts_map = alerts_df["severity"].value_counts().to_dict() if "severity" in alerts_df.columns else {}
        col_a, col_b, col_c, col_d = st.columns(4)
        for col, label, icon, gradient in [
            (col_a, "Critical", "🔴", "linear-gradient(135deg,rgba(248,113,113,0.18),rgba(248,113,113,0.06))"),
            (col_b, "High",     "🟠", "linear-gradient(135deg,rgba(251,191,36,0.18),rgba(251,191,36,0.06))"),
            (col_c, "Medium",   "🟡", "linear-gradient(135deg,rgba(167,139,250,0.18),rgba(167,139,250,0.06))"),
            (col_d, "Low",      "🟢", "linear-gradient(135deg,rgba(52,211,153,0.18),rgba(52,211,153,0.06))"),
        ]:
            with col:
                count = sev_counts_map.get(label, 0)
                color = SEVERITY_COLORS.get(label, "#8b9ab5")
                idx   = ["Critical","High","Medium","Low"].index(label)
                st.markdown(f"""
                <div class="stat-badge" style="background:{gradient};
                            border:1px solid {color}33;
                            border-radius:var(--radius-md);padding:1.5rem 1.6rem;
                            text-align:center;animation-delay:{idx*0.08:.2f}s;
                            position:relative;overflow:hidden;">
                    <div style="position:absolute;top:0;left:0;right:0;height:2px;
                                background:{color};opacity:0.5;"></div>
                    <div style="font-family:'Orbitron','Syne',sans-serif;font-size:2.8rem;font-weight:900;
                                color:{color};line-height:1;text-shadow:0 0 24px {color}66;
                                animation:neonFlicker {8+idx}s ease infinite;">{count}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:{color};
                                letter-spacing:0.14em;margin-top:8px;opacity:0.85;">{icon} {label.upper()}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Filters row ───────────────────────────────────

        col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1, 1.2, 1.4])

        with col_f1:
            section_label("Filter by Severity")
            severity_filter = st.selectbox(
                "Severity",
                ["All", "Critical", "High", "Medium", "Low"],
                label_visibility="collapsed"
            )

        with col_f2:
            section_label("Display Count")
            display_option = st.selectbox(
                "Count",
                ["20", "50", "100", "All"],
                label_visibility="collapsed"
            )

        with col_f3:
            section_label("Select Date")
            selected_date = st.date_input(
                "Date",
                value=None,
                label_visibility="collapsed"
            )

        with col_f4:
            section_label("Time Range")
            time_range = st.selectbox(
                "Time Range",
                [
                    "All Day",
                    "00:00 - 06:00",
                    "06:00 - 12:00",
                    "12:00 - 18:00",
                    "18:00 - 23:59"
                ],
                label_visibility="collapsed"
            )


        # ── Filtering Logic ───────────────────────────────────

        filtered_df = alerts_df.copy()

        # Severity Filter
        if severity_filter != "All":
            filtered_df = filtered_df[
                filtered_df["severity"] == severity_filter
            ]

        # Timestamp conversion (required for date/time filtering)
        if "timestamp" in filtered_df.columns:
            filtered_df["timestamp"] = pd.to_datetime(
                filtered_df["timestamp"],
                errors="coerce"
            )

        # Date Filter
        if selected_date and "timestamp" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["timestamp"].dt.date == selected_date
            ]

        # Time Range Filter
        if time_range != "All Day" and "timestamp" in filtered_df.columns:
            time_map = {
                "00:00 - 06:00": (0, 6),
                "06:00 - 12:00": (6, 12),
                "12:00 - 18:00": (12, 18),
                "18:00 - 23:59": (18, 24),
            }

            start_hour, end_hour = time_map[time_range]

            filtered_df = filtered_df[
                filtered_df["timestamp"].dt.hour.between(
                    start_hour,
                    end_hour - 1
                )
            ]

        # Display Count Filter
        display_df = (
            filtered_df
            if display_option == "All"
            else filtered_df.head(int(display_option))
        )

        # ── Feed header ───────────────────────────────────
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    margin-bottom:16px;flex-wrap:wrap;gap:10px;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--text-muted);
                        letter-spacing:0.1em;">
                SHOWING <span style="color:var(--text-primary);font-weight:700;">{len(display_df)}</span>
                OF <span style="color:var(--text-secondary);">{len(filtered_df)}</span> ALERTS
            </div>
            <div style="display:flex;align-items:center;gap:8px;
                        background:rgba(52,211,153,0.1);border:1px solid rgba(52,211,153,0.25);
                        border-radius:20px;padding:5px 14px;">
                <span style="width:7px;height:7px;border-radius:50%;background:#34d399;
                             box-shadow:0 0 10px #34d399;animation:pulseDot 2s infinite;
                             display:inline-block;"></span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:12px;
                             color:#34d399;font-weight:600;letter-spacing:0.1em;">LIVE FEED</span>
            </div>
        </div>""", unsafe_allow_html=True)

        KILL_CHAIN_STAGES = [
            ("Reconnaissance",         "#38bdf8"),
            ("Initial Access",         "#fbbf24"),
            ("Privilege Escalation",   "#f87171"),
            ("Lateral Movement",       "#fb923c"),
            ("Persistence",            "#a78bfa"),
            ("Data Exfiltration",      "#f87171"),
            ("Defense Evasion",        "#ec4899"),
        ]
        stage_names = [s[0] for s in KILL_CHAIN_STAGES]

        for idx, row in display_df.iterrows():
            sev         = row.get("severity", "Low")
            sev_color   = SEVERITY_COLORS.get(sev, "#8b9ab5")
            kill_stage, kill_color = map_kill_chain_stage(row)
            risk_val    = row.get("risk_score", 0)
            user_id     = row.get("user_id", "UNKNOWN")
            action      = row.get("action", "Unknown")

            with st.expander(
                f"[{sev.upper()}]  {user_id}  ·  {action}  ·  Risk Score: {risk_val}",
            ):
                current_idx = stage_names.index(kill_stage) if kill_stage in stage_names else -1
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;flex-wrap:wrap;">
                    {severity_badge(sev)}
                    <span style="background:{kill_color}18;color:{kill_color};border:1px solid {kill_color}40;
                                 padding:5px 15px;border-radius:20px;font-size:13px;
                                 font-family:'JetBrains Mono',monospace;font-weight:600;letter-spacing:0.06em;">
                        ⛓ {kill_stage.upper()}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                d_col1, d_col2, d_col3 = st.columns(3, gap="medium")
                with d_col1:
                    st.markdown(f"""
                    <div style="background:rgba(56,189,248,0.04);border:1px solid rgba(56,189,248,0.14);
                                border-radius:var(--radius-sm);padding:1.2rem 1.4rem;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                    color:var(--text-muted);letter-spacing:0.16em;margin-bottom:12px;
                                    text-transform:uppercase;">Entity Details</div>
                        <div style="display:grid;gap:8px;">
                            <div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text-muted);margin-bottom:2px;">USER</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#f0f4ff;font-weight:600;">{row.get('user_id','—')}</div>
                            </div>
                            <div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text-muted);margin-bottom:2px;">TIMESTAMP</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#a8b8d4;">{row.get('timestamp','—')}</div>
                            </div>
                            <div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text-muted);margin-bottom:2px;">ACTION</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#fbbf24;font-weight:600;">{row.get('action','—')}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with d_col2:
                    st.markdown(f"""
                    <div style="background:rgba(56,189,248,0.04);border:1px solid rgba(56,189,248,0.14);
                                border-radius:var(--radius-sm);padding:1.2rem 1.4rem;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                    color:var(--text-muted);letter-spacing:0.16em;margin-bottom:12px;
                                    text-transform:uppercase;">Access Context</div>
                        <div style="display:grid;gap:8px;">
                            <div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text-muted);margin-bottom:2px;">LOCATION</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#f0f4ff;">{row.get('location','—')}</div>
                            </div>
                            <div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text-muted);margin-bottom:2px;">DEVICE</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#a8b8d4;">{row.get('device','Unknown')}</div>
                            </div>
                            <div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text-muted);margin-bottom:2px;">FILE PATH</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#a78bfa;">{str(row.get('file_path','N/A'))[:30]}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with d_col3:
                    st.markdown(f"""
                    <div style="background:rgba(56,189,248,0.04);border:1px solid rgba(56,189,248,0.14);
                                border-radius:var(--radius-sm);padding:1.2rem 1.4rem;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                    color:var(--text-muted);letter-spacing:0.16em;margin-bottom:14px;
                                    text-transform:uppercase;">Risk Assessment</div>
                        <div style="margin-bottom:14px;">{risk_bar(risk_val)}</div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                    color:var(--text-muted);margin-bottom:6px;">SEVERITY LEVEL</div>
                        <div>{severity_badge(sev)}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # ── Kill chain visualization ───────────────
                st.markdown(
                    '<div style="font-family:\'JetBrains Mono\',monospace;font-size:12px;'
                    'color:var(--text-muted);letter-spacing:0.16em;margin-bottom:12px;'
                    'text-transform:uppercase;">⛓ Cyber Kill Chain Progression</div>',
                    unsafe_allow_html=True
                )

                kc_cols = st.columns(len(KILL_CHAIN_STAGES))
                for ki, (kc_col, (stage_name, stage_color)) in enumerate(zip(kc_cols, KILL_CHAIN_STAGES)):
                    with kc_col:
                        is_active = (ki == current_idx)
                        is_past   = (ki < current_idx)
                        if is_active:
                            bg_style  = f"background:{stage_color};color:#fff;"
                            border_s  = f"border:1px solid {stage_color};"
                            shadow_s  = f"box-shadow:0 0 18px {stage_color}88;"
                            weight    = "font-weight:700;"
                        elif is_past:
                            bg_style  = f"background:{stage_color}22;color:{stage_color};"
                            border_s  = f"border:1px solid {stage_color}55;"
                            shadow_s  = ""
                            weight    = "font-weight:500;"
                        else:
                            bg_style  = "background:#070d1c;color:#3a4f6a;"
                            border_s  = "border:1px solid rgba(56,189,248,0.08);"
                            shadow_s  = ""
                            weight    = ""

                        st.markdown(f"""
                        <div style="{bg_style}{border_s}{shadow_s}{weight}
                                    border-radius:6px;padding:7px 4px;
                                    font-family:'JetBrains Mono',monospace;font-size:11px;
                                    letter-spacing:0.03em;text-align:center;line-height:1.4;
                                    transition:all 0.2s ease;">
                            {stage_name}
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                reasons, actions_list = explain_detection_and_recommendation(row)
                x_col1, x_col2 = st.columns(2, gap="medium")

                with x_col1:
                    reasons_items = "".join(
                        f'<div style="display:flex;gap:12px;margin-bottom:10px;align-items:flex-start;">'
                        f'<span style="color:#f87171;flex-shrink:0;margin-top:3px;font-size:12px;">▸</span>'
                        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:14px;'
                        f'color:#c8d8f0;line-height:1.6;">{r}</span></div>'
                        for r in reasons
                    )
                    st.markdown(f"""
                    <div style="background:rgba(248,113,113,0.05);border:1px solid rgba(248,113,113,0.22);
                                border-radius:var(--radius-sm);padding:1.2rem 1.4rem;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#f87171;
                                    letter-spacing:0.14em;margin-bottom:14px;font-weight:600;
                                    text-transform:uppercase;">◈ Why Flagged</div>
                        {reasons_items}
                    </div>""", unsafe_allow_html=True)

                with x_col2:
                    actions_items = "".join(
                        f'<div style="display:flex;gap:12px;margin-bottom:10px;align-items:flex-start;">'
                        f'<span style="color:#34d399;flex-shrink:0;margin-top:3px;font-size:12px;">▸</span>'
                        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:14px;'
                        f'color:#c8d8f0;line-height:1.6;">{a}</span></div>'
                        for a in actions_list
                    )
                    st.markdown(f"""
                    <div style="background:rgba(52,211,153,0.05);border:1px solid rgba(52,211,153,0.22);
                                border-radius:var(--radius-sm);padding:1.2rem 1.4rem;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#34d399;
                                    letter-spacing:0.14em;margin-bottom:14px;font-weight:600;
                                    text-transform:uppercase;">◈ Recommended Actions</div>
                        {actions_items}
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button(f"🤖 Generate AI SOC Analyst Report", key=f"explain_{idx}"):
                    with st.spinner("Dispatching Groq AI — building SOC analyst report..."):
                        alert_data = {
                            "user_id":    row.get("user_id", "Unknown"),
                            "risk_score": row.get("risk_score", 0),
                            "severity":   row.get("severity", "Unknown"),
                            "action":     row.get("action", "Unknown"),
                            "location":   row.get("location", "Unknown"),
                            "device":     row.get("device", "Unknown"),
                            "file_path":  row.get("file_path", "N/A"),
                        }
                        try:
                            explanation = generate_alert_explanation(alert_data)
                        except Exception as e:
                            explanation = f"AI explanation unavailable: {e}"

                    st.markdown(f"""
                    <div style="background:rgba(56,189,248,0.04);border:1px solid var(--border-accent);
                                border-radius:var(--radius-md);padding:1.8rem 2rem;margin-top:12px;
                                animation:fadeInUp 0.4s ease;position:relative;overflow:hidden;">
                        <div style="position:absolute;top:0;left:0;right:0;height:2px;
                                    background:linear-gradient(90deg,#38bdf8,#a78bfa,#34d399,#38bdf8);
                                    background-size:300%;animation:shimmer 4s linear infinite;"></div>
                        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                            <div style="width:10px;height:10px;background:var(--cyan);border-radius:50%;
                                        box-shadow:0 0 14px var(--cyan);animation:pulseDot 2s infinite;"></div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--cyan);
                                        letter-spacing:0.14em;font-weight:600;text-transform:uppercase;">
                                ◈ AI SOC Analyst Report — Groq Engine</div>
                        </div>
                        <div style="font-family:'DM Sans',sans-serif;font-size:15px;color:#c8d8f0;
                                    line-height:1.9;white-space:pre-wrap;">{explanation}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    pdf_path, pdf_err = generate_pdf_report(row, reasons, actions_list, explanation)
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label="⬇ Download Executive PDF Report",
                                data=pdf_file,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf",
                                key=f"pdf_{idx}"
                            )
                    elif pdf_err:
                        st.warning(f"PDF generation failed: {pdf_err}")


# =========================================================
# USER BEHAVIOR PROFILES
# =========================================================

elif _page == "User Behavior Profiles":

    page_header("👤", "User Behavior Profiles", "ENTITY BEHAVIOR ANALYTICS  ·  UEBA DEEP DIVE  ·  IAM PROFILING")

    if logs_df.empty:
        no_data_state("No User Log Data Found", "Upload a log file or generate synthetic data first")
    else:
        col_sel, col_sp = st.columns([1, 3])
        with col_sel:
            section_label("Select Entity")
            users = sorted(logs_df["user_id"].unique()) if "user_id" in logs_df.columns else []
            selected_user = st.selectbox("User", users, label_visibility="collapsed")

        user_data   = logs_df[logs_df["user_id"] == selected_user] if "user_id" in logs_df.columns else pd.DataFrame()
        user_alerts = alerts_df[alerts_df["user_id"] == selected_user] if (not alerts_df.empty and "user_id" in alerts_df.columns) else pd.DataFrame()

        # ── User risk header card ────────────────────────
        user_risk    = user_alerts["risk_score"].mean() if (not user_alerts.empty and "risk_score" in user_alerts.columns) else 0
        user_sev     = user_alerts["severity"].mode()[0] if (not user_alerts.empty and "severity" in user_alerts.columns) else "None"
        risk_color   = "#f87171" if user_risk >= 80 else ("#fbbf24" if user_risk >= 60 else ("#a78bfa" if user_risk >= 40 else "#34d399"))
        total_events = len(user_data)
        total_flags  = len(user_alerts)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(12,20,36,0.98),rgba(8,14,28,0.98));
                    border:1px solid var(--border-accent);border-radius:var(--radius-lg);
                    padding:1.8rem 2.2rem;margin-bottom:1.6rem;
                    position:relative;overflow:hidden;animation:fadeInUp 0.4s ease;">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                        background:linear-gradient(90deg,{risk_color},{risk_color}80,transparent);"></div>
            <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
                <!-- Avatar -->
                <div style="width:64px;height:64px;
                            background:linear-gradient(135deg,{risk_color}22,{risk_color}08);
                            border:2px solid {risk_color}44;border-radius:16px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.8rem;flex-shrink:0;
                            box-shadow:0 0 28px {risk_color}22;">👤</div>
                <div style="flex:1;min-width:160px;">
                    <div style="font-family:'Orbitron','Syne',sans-serif;font-size:22px;font-weight:800;
                                color:#f0f4ff;margin-bottom:4px;">{selected_user}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
                                color:var(--text-muted);letter-spacing:0.12em;">
                        UEBA ENTITY PROFILE  ·  {total_events} EVENTS  ·  {total_flags} FLAGS
                    </div>
                </div>
                <!-- Risk score gauge -->
                <div style="text-align:center;flex-shrink:0;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                color:var(--text-muted);letter-spacing:0.16em;margin-bottom:6px;
                                text-transform:uppercase;">Risk Score</div>
                    <div style="font-family:'Orbitron','Syne',sans-serif;font-size:38px;font-weight:900;
                                color:{risk_color};text-shadow:0 0 24px {risk_color}66;
                                line-height:1;">{int(user_risk) if user_risk else '—'}</div>
                </div>
                <!-- Severity -->
                <div style="text-align:center;flex-shrink:0;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                                color:var(--text-muted);letter-spacing:0.16em;margin-bottom:8px;
                                text-transform:uppercase;">Peak Severity</div>
                    {severity_badge(user_sev) if user_sev != "None" else
                     '<span style="font-family:\'JetBrains Mono\',monospace;font-size:13px;color:#5a6e8a;">No Alerts</span>'}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        chart_col, hour_col = st.columns(2, gap="medium")

        with chart_col:
            section_label("Action Distribution")
            if "action" in user_data.columns:
                action_counts = user_data["action"].value_counts().reset_index()
                action_counts.columns = ["action", "count"]
                fig_act = px.bar(
                    action_counts, x="count", y="action", orientation="h",
                    color="count", color_continuous_scale=["#0e1a30","#38bdf8"]
                )
                apply_theme(fig_act)
                fig_act.update_traces(marker_line_width=0,
                    hovertemplate="<b>%{y}</b><br>Events: %{x}<extra></extra>")
                fig_act.update_layout(
                    showlegend=False, height=320, coloraxis_showscale=False,
                    xaxis_title="Event Count", yaxis_title="",
                    yaxis=dict(categoryorder="total ascending")
                )
                st.plotly_chart(fig_act, use_container_width=True)

        with hour_col:
            section_label("Login Hour Heatmap")
            if "timestamp" in user_data.columns:
                ts_clean = user_data.dropna(subset=["timestamp"]).copy()
                if not ts_clean.empty:
                    ts_clean["hour"] = ts_clean["timestamp"].dt.hour
                    hour_counts = ts_clean["hour"].value_counts().sort_index().reset_index()
                    hour_counts.columns = ["hour", "count"]
                    all_hours = pd.DataFrame({"hour": range(24)})
                    hour_counts = all_hours.merge(hour_counts, on="hour", how="left").fillna(0)
                    fig_hour = go.Figure(go.Bar(
                        x=hour_counts["hour"], y=hour_counts["count"],
                        marker_color=["#f87171" if h < 6 or h > 22 else "#38bdf8"
                                      for h in hour_counts["hour"]],
                        hovertemplate="Hour %{x}:00<br>Events: %{y}<extra></extra>"
                    ))
                    apply_theme(fig_hour)
                    fig_hour.update_layout(
                        showlegend=False, height=320,
                        xaxis_title="Hour of Day", yaxis_title="Events",
                        shapes=[dict(
                            type="rect", x0=-0.5, x1=5.5, y0=0, y1=1,
                            yref="paper", fillcolor="rgba(248,113,113,0.07)",
                            line=dict(width=0)
                        )]
                    )
                    st.plotly_chart(fig_hour, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        trend_col, log_col = st.columns([1.3, 1], gap="medium")

        with trend_col:
            section_label("Risk Score Progression Over Time")
            if not user_alerts.empty and "timestamp" in user_alerts.columns and "risk_score" in user_alerts.columns:
                ua = user_alerts.copy()
                ua["timestamp"] = pd.to_datetime(ua["timestamp"])
                ua = ua.sort_values("timestamp")
                risk_trend = ua.set_index("timestamp").resample("1D")["risk_score"].mean().ffill().reset_index()
                fig_risk = go.Figure()
                fig_risk.add_trace(go.Scatter(
                    x=risk_trend["timestamp"], y=risk_trend["risk_score"],
                    mode="lines+markers", fill="tozeroy",
                    line=dict(color="#a78bfa", width=2.5),
                    fillcolor="rgba(167,139,250,0.07)",
                    marker=dict(size=8, color="#a78bfa",
                                line=dict(color="#04080f", width=2)),
                    hovertemplate="<b>%{x|%b %d}</b><br>Risk: %{y:.1f}<extra></extra>"
                ))
                fig_risk.add_hline(y=80, line_color="#f87171", line_dash="dash", line_width=1,
                                   annotation_text="CRITICAL", annotation_position="top right",
                                   annotation_font=dict(color="#f87171", size=11))
                fig_risk.add_hline(y=60, line_color="#fbbf24", line_dash="dash", line_width=1,
                                   annotation_text="HIGH", annotation_position="top right",
                                   annotation_font=dict(color="#fbbf24", size=11))
                apply_theme(fig_risk)
                fig_risk.update_layout(
                    showlegend=False, height=320,
                    xaxis_title="", yaxis_title="Risk Score",
                    yaxis=dict(range=[0, 105])
                )
                st.plotly_chart(fig_risk, use_container_width=True)
            else:
                no_data_state("No Alert History for This User")

        with log_col:
            section_label("Recent Activity Log")
            display_cols = [c for c in ["timestamp", "action", "location", "device"] if c in user_data.columns]
            st.dataframe(
                user_data[display_cols].head(20),
                use_container_width=True, hide_index=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if "location" in user_data.columns:
            section_label("Access Location Pattern")
            loc_counts = user_data["location"].value_counts().reset_index()
            loc_counts.columns = ["location", "count"]
            fig_loc = px.treemap(
                loc_counts, path=["location"], values="count",
                color="count", color_continuous_scale=["#0b1120","#38bdf8"]
            )
            apply_theme(fig_loc)
            fig_loc.update_layout(height=240, coloraxis_showscale=False)
            st.plotly_chart(fig_loc, use_container_width=True)


# =========================================================
# WHAT-IF SIMULATOR
# =========================================================

elif _page == "What-If Simulator":

    page_header("⚡", "What-If Simulator", "PROACTIVE THREAT SIMULATION  ·  ATTACK CHAIN MODELING  ·  DEFENSE PLANNING")

    if logs_df.empty:
        no_data_state("No User Data Available for Simulation", "Upload a log file first")
    else:
        # ── Warning banner ────────────────────────────────
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(248,113,113,0.08),rgba(248,113,113,0.03));
                    border:1px solid rgba(248,113,113,0.28);
                    border-radius:var(--radius-md);padding:1.2rem 1.6rem;margin-bottom:2rem;
                    display:flex;align-items:flex-start;gap:16px;animation:fadeInUp 0.4s ease;
                    position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;
                        background:linear-gradient(90deg,transparent,rgba(248,113,113,0.5),transparent);"></div>
            <div style="font-size:1.4rem;flex-shrink:0;margin-top:2px;animation:floatUp 3s ease infinite;">⚠️</div>
            <div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#f87171;
                            font-weight:600;letter-spacing:0.1em;margin-bottom:6px;text-transform:uppercase;">
                    Simulation Mode Active</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:15px;color:#a8b8d4;line-height:1.7;">
                    Attack chains generated by Groq AI are hypothetical scenarios for proactive defense planning only.
                    No real actions are executed. All simulations are for SOC training and threat modeling.
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        sim_col1, sim_col2 = st.columns(2, gap="medium")
        with sim_col1:
            section_label("Target Entity")
            selected_user = st.selectbox(
                "User", sorted(logs_df["user_id"].unique()),
                label_visibility="collapsed"
            )
        with sim_col2:
            section_label("Threat Scenario")
            scenario = st.selectbox(
                "Scenario",
                ["Disgruntled Employee", "Privilege Escalation",
                 "Sensitive Data Exfiltration", "Shadow Admin Behavior"],
                label_visibility="collapsed"
            )

        scenario_meta = {
            "Disgruntled Employee":        ("🔴", "#f87171", "Lateral movement, data staging, and exfiltration patterns consistent with a motivated internal actor."),
            "Privilege Escalation":        ("🟠", "#fbbf24", "Unauthorized elevation of access rights to gain control over sensitive systems and critical infrastructure."),
            "Sensitive Data Exfiltration": ("🟡", "#fbbf24", "Systematic access and transfer of classified or confidential organizational assets to external endpoints."),
            "Shadow Admin Behavior":       ("🟣", "#a78bfa", "Unauthorized creation of admin accounts or backdoors to maintain persistent privileged access."),
        }
        icon, s_color, desc = scenario_meta.get(scenario, ("⚪", "#8b9ab5", ""))

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{s_color}0a,{s_color}04);
                    border:1px solid {s_color}30;border-radius:var(--radius-md);
                    padding:1.4rem 1.8rem;margin:1.2rem 0 2rem 0;animation:fadeInUp 0.3s ease;
                    position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;bottom:0;width:3px;background:{s_color};opacity:0.7;"></div>
            <div style="display:flex;gap:18px;align-items:flex-start;padding-left:8px;">
                <div style="font-size:1.8rem;flex-shrink:0;animation:floatUp 3s ease infinite;">{icon}</div>
                <div>
                    <div style="font-family:'Orbitron','Syne',sans-serif;font-size:18px;font-weight:700;
                                color:{s_color};margin-bottom:8px;">{scenario}</div>
                    <div style="font-family:'DM Sans',sans-serif;font-size:15px;color:#a8b8d4;
                                line-height:1.7;">{desc}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        chain_steps = {
            "Disgruntled Employee": [
                ("Reconnaissance",  "Enumerating sensitive directories",    "#38bdf8"),
                ("Data Staging",    "Bulk-copying confidential files",       "#fbbf24"),
                ("Exfiltration",    "Transferring to external endpoint",     "#f87171"),
                ("Cover Tracks",    "Deleting access logs",                  "#ec4899"),
            ],
            "Privilege Escalation": [
                ("Initial Probe",   "Scanning permission boundaries",        "#38bdf8"),
                ("Exploit Attempt", "Triggering privilege_change",           "#fbbf24"),
                ("Admin Access",    "Gaining elevated control",              "#f87171"),
                ("Persistence",     "Creating backdoor admin",               "#a78bfa"),
            ],
            "Sensitive Data Exfiltration": [
                ("Target ID",       "Locating payroll & finance dirs",       "#38bdf8"),
                ("Bulk Export",     "Mass downloading sensitive files",      "#fbbf24"),
                ("Compression",     "Archiving datasets",                    "#fb923c"),
                ("Exfiltration",    "Uploading to external storage",         "#f87171"),
            ],
            "Shadow Admin Behavior": [
                ("Cred Theft",      "Capturing privileged credentials",      "#38bdf8"),
                ("Acct Creation",   "Creating hidden admin account",         "#a78bfa"),
                ("Backdoor",        "Embedding persistent access",           "#fbbf24"),
                ("Silent Ops",      "Operating below detection threshold",   "#34d399"),
            ],
        }
        steps = chain_steps.get(scenario, [])

        if steps:
            section_label("Attack Chain Preview")
            step_cols = st.columns(len(steps))
            for si, (sc, (step_title, step_desc, step_color)) in enumerate(zip(step_cols, steps)):
                with sc:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,{step_color}0e,{step_color}04);
                                border:1px solid {step_color}35;
                                border-radius:var(--radius-sm);padding:16px 14px;
                                animation:fadeInUp 0.5s ease {si*0.1:.1f}s both;
                                position:relative;overflow:hidden;text-align:center;">
                        <div style="position:absolute;top:0;left:0;right:0;height:2px;background:{step_color};opacity:0.6;"></div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{step_color};
                                    letter-spacing:0.14em;margin-bottom:8px;text-transform:uppercase;">Step {si+1}</div>
                        <div style="font-family:'Orbitron','Syne',sans-serif;font-size:15px;font-weight:700;
                                    color:#f0f4ff;margin-bottom:6px;">{step_title}</div>
                        <div style="font-family:'DM Sans',sans-serif;font-size:13px;
                                    color:#5a6e8a;line-height:1.5;">{step_desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⚡ Launch Attack Chain Simulation"):
            with st.spinner("Groq AI modeling attack progression..."):
                try:
                    simulation = generate_attack_simulation(selected_user, scenario)
                except Exception as e:
                    simulation = f"Simulation unavailable: {e}"

            st.markdown(f"""
            <div style="background:rgba(248,113,113,0.04);border:1px solid rgba(248,113,113,0.28);
                        border-radius:var(--radius-md);padding:2rem 2.2rem;margin-top:1rem;
                        animation:fadeInUp 0.4s ease;position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;
                            background:linear-gradient(90deg,#f87171,#a78bfa,#38bdf8,#34d399,#f87171);
                            background-size:300%;animation:shimmer 4s linear infinite;"></div>
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:18px;">
                    <div style="width:10px;height:10px;background:#f87171;border-radius:50%;
                                box-shadow:0 0 16px #f87171;animation:pulseDot 2s infinite;"></div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#f87171;
                                letter-spacing:0.14em;font-weight:600;text-transform:uppercase;">
                        ◈ AI Attack Chain — {selected_user} · {scenario.upper()}</div>
                </div>
                <div style="font-family:'DM Sans',sans-serif;font-size:15px;color:#c8d8f0;
                            line-height:1.9;white-space:pre-wrap;">{simulation}</div>
            </div>""", unsafe_allow_html=True)

            mitigation_map = {
                "Disgruntled Employee":        ["Revoke remote access immediately", "Enable DLP monitoring", "Preserve forensic artifacts", "Alert HR and legal"],
                "Privilege Escalation":        ["Lock privileged accounts", "Audit IAM role assignments", "Enable JIT access controls", "Trigger admin approval gates"],
                "Sensitive Data Exfiltration": ["Block bulk export capabilities", "Enable egress DLP rules", "Quarantine user device", "Notify data owners"],
                "Shadow Admin Behavior":       ["Audit all admin accounts", "Remove unauthorized accounts", "Review backdoor signatures", "Reset all privileged credentials"],
            }
            mitigations = mitigation_map.get(scenario, ["Investigate immediately", "Escalate to SOC manager"])
            mit_items = "".join(
                f'<div style="display:flex;gap:12px;margin-bottom:10px;align-items:flex-start;">'
                f'<span style="color:#34d399;flex-shrink:0;margin-top:3px;font-size:14px;">▸</span>'
                f'<span style="font-family:\'DM Sans\',sans-serif;font-size:15px;color:#c8d8f0;line-height:1.6;">{m}</span></div>'
                for m in mitigations
            )
            st.markdown(f"""
            <div style="margin-top:16px;background:rgba(52,211,153,0.05);border:1px solid rgba(52,211,153,0.22);
                        border-radius:var(--radius-md);padding:1.6rem 1.8rem;animation:fadeInUp 0.5s ease 0.2s both;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#34d399;
                            letter-spacing:0.14em;margin-bottom:16px;font-weight:600;text-transform:uppercase;">
                    ◈ Recommended Mitigations</div>
                {mit_items}
            </div>""", unsafe_allow_html=True)


# =========================================================
# SYNTHETIC DATA GENERATOR
# =========================================================

elif _page == "Synthetic Data Generator":

    page_header("🧪", "Synthetic Data Generator", "ENTERPRISE LOG SYNTHESIS  ·  TEST ENVIRONMENT  ·  DEMO PIPELINE")

    # ── Hero card ─────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(56,189,248,0.08),rgba(167,139,250,0.05),rgba(52,211,153,0.04));
                border:1px solid rgba(56,189,248,0.20);border-radius:var(--radius-lg);
                padding:2rem 2.4rem;margin-bottom:2rem;position:relative;overflow:hidden;
                animation:fadeInUp 0.5s ease;">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;
                    background:linear-gradient(90deg,#38bdf8,#a78bfa,#34d399,#38bdf8);
                    background-size:300%;animation:shimmer 4s linear infinite;"></div>
        <div style="display:flex;align-items:center;gap:20px;">
            <div style="font-size:2.8rem;animation:floatUp 3s ease infinite;flex-shrink:0;">⚗️</div>
            <div>
                <div style="font-family:'Orbitron','Syne',sans-serif;font-size:20px;font-weight:800;
                            color:#f0f4ff;margin-bottom:8px;">Enterprise Log Synthesizer</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:15px;color:#a8b8d4;line-height:1.75;max-width:600px;">
                    Ingest real enterprise logs or generate realistic synthetic behavioral datasets to populate
                    the VEILGuard detection pipeline. Supports CSV, LOG, and TXT formats.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    section_label("Upload Enterprise Log File")
    uploaded_file = st.file_uploader(
        "Upload CSV / LOG File",
        type=["csv", "log", "txt"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        try:
            os.makedirs("data", exist_ok=True)
            save_path = "data/synthetic_logs.csv"
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Log file **{uploaded_file.name}** ingested into VEILGuard pipeline.")
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Upload failed: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    section_label("Detection Engine")
    if st.button("🚨 Run Detection Engine"):
        if not os.path.exists("data/synthetic_logs.csv"):
            st.error("❌ No log file found. Please upload a file first.")
        else:
            with st.spinner("Running VEILGuard Detection Engine..."):
                success, message = run_detection_engine()
            if success:
                st.success("✅ Detection Engine completed successfully.")
                if message.strip():
                    st.code(message, language="bash")
                st.cache_data.clear()
                st.info("📊 New alerts generated. Navigate to **Live Monitor & Alerts** to review.")
            else:
                st.error("❌ Detection Engine encountered an error.")
                if message.strip():
                    st.code(message, language="bash")

    st.markdown("<br>", unsafe_allow_html=True)

    section_label("Or Generate Synthetic Data (Advanced)")
    st.code("python synthetic_generator.py", language="bash")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")
    for col, title, desc, icon, color, delay in [
        (col1, "UEBA Logs",     "Simulates normal & anomalous user entity behavior patterns across departments", "📋", "#38bdf8", "0s"),
        (col2, "File Access",   "Generates sensitive file access sequences with metadata, DLP triggers, and paths", "🗂️", "#a78bfa", "0.1s"),
        (col3, "Travel Events", "Creates impossible travel & geolocation anomaly records with Haversine scoring", "🌐", "#fbbf24", "0.2s"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-badge" style="background:linear-gradient(135deg,{color}0d,{color}04);
                        border:1px solid {color}28;border-radius:var(--radius-md);
                        padding:2rem;text-align:center;
                        animation:fadeInUp 0.5s ease {delay} both;
                        position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;
                            background:{color};opacity:0.5;"></div>
                <div style="font-size:2.6rem;margin-bottom:14px;animation:floatUp 3s ease infinite;">{icon}</div>
                <div style="font-family:'Orbitron','Syne',sans-serif;font-size:15px;font-weight:700;
                            color:{color};letter-spacing:0.06em;margin-bottom:12px;">{title}</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:14px;color:#a8b8d4;
                            line-height:1.65;">{desc}</div>
            </div>""", unsafe_allow_html=True)


# =========================================================
# ABOUT VEILGUARD
# =========================================================

elif _page == "About VEILGuard":

    page_header("ℹ️", "About VEILGuard", "PLATFORM DOCUMENTATION  ·  ARCHITECTURE OVERVIEW  ·  INSIDER RISK")

    # ── Hero banner ───────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(56,189,248,0.10),rgba(167,139,250,0.08),rgba(56,189,248,0.04));
                border:1px solid rgba(56,189,248,0.26);border-radius:var(--radius-xl);
                padding:2.4rem 2.8rem;margin-bottom:2rem;position:relative;overflow:hidden;
                animation:fadeInUp 0.5s ease;">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;
                    background:linear-gradient(90deg,#38bdf8,#a78bfa,#34d399,#38bdf8);
                    background-size:200%;animation:shimmer 4s linear infinite;"></div>
        <!-- Decorative orbs -->
        <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
                    background:radial-gradient(circle,rgba(56,189,248,0.10),transparent 70%);
                    pointer-events:none;"></div>
        <div style="position:absolute;bottom:-40px;left:30%;width:180px;height:180px;
                    background:radial-gradient(circle,rgba(167,139,250,0.08),transparent 70%);
                    pointer-events:none;"></div>
        <div style="position:relative;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#38bdf8;
                        letter-spacing:0.2em;margin-bottom:16px;text-transform:uppercase;">◈ VEILGuard Platform</div>
            <div style="font-family:'Orbitron','Syne',sans-serif;font-size:28px;font-weight:900;
                        color:#f0f4ff;margin-bottom:14px;letter-spacing:-0.01em;line-height:1.2;">
                Vigilant Enterprise Insider Leakage Guard</div>
            <div style="font-family:'DM Sans',sans-serif;font-size:16px;color:#a8b8d4;
                        line-height:1.85;max-width:700px;">
                An enterprise-grade insider threat detection and proactive risk simulation platform.
                VEILGuard combines behavioral anomaly detection, IAM governance, and AI-powered investigation
                to identify and neutralize malicious insider activity before damage occurs.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;gap:14px;margin-bottom:2rem;flex-wrap:wrap;">
        <div class="stat-badge" style="flex:1;min-width:130px;
             background:linear-gradient(135deg,rgba(56,189,248,0.12),rgba(56,189,248,0.04));
             border:1px solid rgba(56,189,248,0.28);border-radius:var(--radius-md);
             padding:1.4rem;text-align:center;animation-delay:0s;position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                        background:#38bdf8;opacity:0.5;"></div>
            <div style="font-family:'Orbitron','Syne',sans-serif;font-size:2.4rem;font-weight:900;
                        color:#38bdf8;text-shadow:0 0 20px rgba(56,189,248,0.5);">9</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#5a6e8a;
                        letter-spacing:0.16em;margin-top:6px;text-transform:uppercase;">Capabilities</div>
        </div>
        <div class="stat-badge" style="flex:1;min-width:130px;
             background:linear-gradient(135deg,rgba(167,139,250,0.12),rgba(167,139,250,0.04));
             border:1px solid rgba(167,139,250,0.28);border-radius:var(--radius-md);
             padding:1.4rem;text-align:center;animation-delay:0.1s;position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                        background:#a78bfa;opacity:0.5;"></div>
            <div style="font-family:'Orbitron','Syne',sans-serif;font-size:2.4rem;font-weight:900;
                        color:#a78bfa;text-shadow:0 0 20px rgba(167,139,250,0.5);">7</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#5a6e8a;
                        letter-spacing:0.16em;margin-top:6px;text-transform:uppercase;">Tech Stack</div>
        </div>
        <div class="stat-badge" style="flex:1;min-width:130px;
             background:linear-gradient(135deg,rgba(251,191,36,0.12),rgba(251,191,36,0.04));
             border:1px solid rgba(251,191,36,0.28);border-radius:var(--radius-md);
             padding:1.4rem;text-align:center;animation-delay:0.2s;position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                        background:#fbbf24;opacity:0.5;"></div>
            <div style="font-family:'Orbitron','Syne',sans-serif;font-size:2.4rem;font-weight:900;
                        color:#fbbf24;text-shadow:0 0 20px rgba(251,191,36,0.5);">AI</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#5a6e8a;
                        letter-spacing:0.16em;margin-top:6px;text-transform:uppercase;">Powered</div>
        </div>
        <div class="stat-badge" style="flex:1;min-width:130px;
             background:linear-gradient(135deg,rgba(52,211,153,0.12),rgba(52,211,153,0.04));
             border:1px solid rgba(52,211,153,0.28);border-radius:var(--radius-md);
             padding:1.4rem;text-align:center;animation-delay:0.3s;position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                        background:#34d399;opacity:0.5;"></div>
            <div style="font-family:'Orbitron','Syne',sans-serif;font-size:2.4rem;font-weight:900;
                        color:#34d399;text-shadow:0 0 20px rgba(52,211,153,0.5);">RT</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#5a6e8a;
                        letter-spacing:0.16em;margin-top:6px;text-transform:uppercase;">Real-Time</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_caps, col_stack = st.columns(2, gap="medium")

    with col_caps:
        capabilities = [
            ("🔍", "User & Entity Behavior Analytics (UEBA)"),
            ("🌲", "Isolation Forest Anomaly Detection"),
            ("📏", "Rule-Based Insider Threat Detection"),
            ("✈️",  "Impossible Travel Detection (Haversine)"),
            ("🗂️", "Sensitive File Access Monitoring"),
            ("🔑", "Privilege Misuse Detection"),
            ("📊", "Risk Scoring Engine"),
            ("🤖", "Groq AI SOC Analyst Explanations"),
            ("⚡", "Insider Threat What-If Simulation"),
        ]
        rows = "".join(f"""
        <div class="cap-item" style="display:flex;align-items:center;gap:14px;padding:10px 10px;
                     margin-bottom:2px;border-radius:8px;animation:fadeInLeft 0.4s ease {0.05*i:.2f}s both;">
            <span style="font-size:1rem;min-width:26px;text-align:center;">{ic}</span>
            <span style="font-family:'DM Sans',sans-serif;font-size:14px;color:#a8b8d4;font-weight:500;">{label}</span>
        </div>""" for i, (ic, label) in enumerate(capabilities))

        st.markdown(f"""
        <div class="about-cap-card" style="background:var(--bg-card);border:1px solid rgba(56,189,248,0.16);
             border-radius:var(--radius-md);padding:1.8rem;position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                        background:linear-gradient(90deg,#38bdf8,transparent);opacity:0.5;"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#38bdf8;
                        letter-spacing:0.16em;margin-bottom:18px;display:flex;align-items:center;gap:10px;
                        text-transform:uppercase;">
                <span style="display:inline-block;width:9px;height:9px;background:#38bdf8;border-radius:50%;
                             box-shadow:0 0 10px #38bdf8;animation:pulseDot 2s infinite;"></span>
                Core Capabilities
            </div>
            {rows}
        </div>""", unsafe_allow_html=True)

    with col_stack:
        tech_items = [
            ("Python",      "Core Runtime",      "#38bdf8"),
            ("Streamlit",   "Dashboard UI",      "#a78bfa"),
            ("Scikit-learn","Isolation Forest",  "#fbbf24"),
            ("Plotly",      "Visualization",     "#34d399"),
            ("Groq LLM",    "AI Explanations",   "#f87171"),
            ("Haversine",   "Travel Detection",  "#38bdf8"),
            ("Pandas",      "Data Engineering",  "#a78bfa"),
        ]
        rows2 = "".join(f"""
        <div class="stack-row" style="display:flex;justify-content:space-between;align-items:center;
                     padding:11px 14px;background:rgba(4,8,15,0.7);border-radius:var(--radius-sm);
                     margin-bottom:7px;animation:fadeInRight 0.4s ease {0.05*i:.2f}s both;
                     border-left:2px solid {color}55;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#f0f4ff;
                         font-weight:500;">{name}</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:12px;color:{color};
                         background:{color}18;padding:4px 12px;border-radius:12px;
                         letter-spacing:0.05em;">{role}</span>
        </div>""" for i, (name, role, color) in enumerate(tech_items))

        st.markdown(f"""
        <div class="about-stack-card" style="background:var(--bg-card);border:1px solid rgba(167,139,250,0.16);
             border-radius:var(--radius-md);padding:1.8rem;position:relative;overflow:hidden;">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                        background:linear-gradient(90deg,#a78bfa,transparent);opacity:0.5;"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#a78bfa;
                        letter-spacing:0.16em;margin-bottom:18px;display:flex;align-items:center;gap:10px;
                        text-transform:uppercase;">
                <span style="display:inline-block;width:9px;height:9px;background:#a78bfa;border-radius:50%;
                             box-shadow:0 0 10px #a78bfa;animation:pulseDot 2s infinite 0.5s;"></span>
                Technology Stack
            </div>
            {rows2}
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Resume impact statement ───────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(56,189,248,0.08),rgba(167,139,250,0.06),rgba(56,189,248,0.04));
                border:1px solid rgba(56,189,248,0.28);border-radius:var(--radius-lg);
                padding:2.2rem 2.6rem;position:relative;overflow:hidden;animation:fadeInUp 0.7s ease 0.3s both;">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;
                    background:linear-gradient(90deg,#38bdf8,#a78bfa,#34d399,#38bdf8);
                    background-size:200%;animation:shimmer 3s linear infinite;"></div>
        <div style="display:flex;align-items:flex-start;gap:22px;">
            <div style="font-size:2.4rem;flex-shrink:0;margin-top:2px;animation:floatUp 3s ease infinite;">📄</div>
            <div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#38bdf8;
                            letter-spacing:0.18em;margin-bottom:16px;text-transform:uppercase;">◈ Resume Impact Statement</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:16px;color:#f0f4ff;
                            line-height:1.9;font-style:italic;">
                    "Built <strong style="color:#38bdf8;font-style:normal;">VEILGuard</strong> — an advanced
                    enterprise cybersecurity platform leveraging Streamlit, Isolation Forest anomaly detection,
                    UEBA pipelines, and Groq LLMs to detect insider threats in real time, generate AI-powered
                    SOC analyst reports, simulate malicious insider attack chains, and recommend proactive
                    defensive controls aligned with MITRE ATT&CK."
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detection pipeline ────────────────────────────────
    section_label("Detection Pipeline Architecture")
    pipeline_steps = [
        ("📥", "Log Ingestion",       "#38bdf8"),
        ("🔧", "Feature Engineering", "#a78bfa"),
        ("🌲", "Isolation Forest",    "#fbbf24"),
        ("📏", "Rule Engine",         "#f87171"),
        ("📊", "Risk Scoring",        "#34d399"),
        ("🤖", "Groq AI Report",      "#38bdf8"),
    ]
    pipe_cols = st.columns(len(pipeline_steps))
    for pi, (pc, (p_icon, p_label, p_color)) in enumerate(zip(pipe_cols, pipeline_steps)):
        with pc:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{p_color}0e,{p_color}04);
                        border:1px solid {p_color}32;border-radius:var(--radius-sm);
                        padding:14px 10px;font-family:'JetBrains Mono',monospace;font-size:12px;
                        color:{p_color};text-align:center;
                        animation:fadeInLeft 0.4s ease {pi*0.08:.2f}s both;
                        position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;
                            background:{p_color};opacity:0.4;"></div>
                <div style="font-size:1.3rem;margin-bottom:7px;">{p_icon}</div>
                {p_label}
            </div>
            """, unsafe_allow_html=True)
            if pi < len(pipeline_steps) - 1:
                st.markdown(
                    f'<div style="color:#5a6e8a;text-align:center;font-size:1.2rem;'
                    f'margin-top:-28px;position:relative;z-index:10;">→</div>',
                    unsafe_allow_html=True
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Why insider risk matters ──────────────────────────
    section_label("Why Insider Risk Matters")
    r1c1, r1c2, r1c3, r1c4 = st.columns(4, gap="medium")
    risk_cards = [
        (r1c1, "#f87171", "🔑", "Privilege Abuse",   "Over-privileged accounts are the #1 attack vector. VEILGuard detects anomalous privilege usage in real time."),
        (r1c2, "#fbbf24", "👥", "Shadow Admins",     "Unauthorized admin accounts invisible to standard IAM tools are surfaced by VEILGuard immediately."),
        (r1c3, "#a78bfa", "📤", "Data Exfiltration", "Bulk transfers, unauthorized downloads, and sensitive file copying trigger immediate pipeline alerts."),
        (r1c4, "#38bdf8", "🌐", "Impossible Travel", "Geolocation anomalies — logins from multiple continents in minutes — caught by Haversine scoring."),
    ]
    for rc, color, icon, title, desc in risk_cards:
        with rc:
            st.markdown(f"""
            <div class="stat-badge" style="background:linear-gradient(135deg,{color}0e,{color}04);
                        border:1px solid {color}22;border-radius:var(--radius-md);
                        padding:1.6rem;animation:fadeInUp 0.5s ease;height:100%;
                        position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;
                            background:{color};opacity:0.4;"></div>
                <div style="font-size:1.8rem;margin-bottom:12px;">{icon}</div>
                <div style="font-family:'Orbitron','Syne',sans-serif;font-size:15px;font-weight:700;
                            color:{color};margin-bottom:10px;">{title}</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:14px;color:#a8b8d4;
                            line-height:1.7;">{desc}</div>
            </div>""", unsafe_allow_html=True)
