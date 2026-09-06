#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  DASHBOARD CIENTÍFICO: CRIMINALIDAD Y VIOLENCIA EN COLOMBIA                 ║
║  ────────────────────────────────────────────────────────────────────────   ║
║  Maestría en Analítica de Datos — Politécnico Grancolombiano               ║
║  Autor: Alejandro Quintero Ruiz                                            ║
║  Curso: Visualización de Datos — Corte 3                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

Fuentes de datos:
  • leonardoariasalemn/delitos-colombia (Kaggle) — 2.38M registros, 2020-2026
  • estiven0507/domestic-violence-in-colombia (Kaggle) — 575K registros, 2010-2023

Ejecución: streamlit run app.py
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Configurar path para imports locales
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime

# Imports locales
from data_loader import (
    load_delitos,
    load_domestic_violence,
    filter_delitos,
    filter_domestic,
    get_overlap_period,
    get_departamentos_comunes,
    normalize_text,
)

# ════════════════════════════════════════════════════════════════════════════════
# DIAGNÓSTICO TEMPRANO (solo en cloud para debug)
# ════════════════════════════════════════════════════════════════════════════════
try:
    import kagglehub
    st.write(f"✅ kagglehub version: {kagglehub.__version__}")
except Exception as e:
    st.error(f"❌ kagglehub import failed: {e}")

# Verificar secrets
try:
    has_secrets = hasattr(st, 'secrets') and len(st.secrets) > 0
    st.write(f"✅ st.secrets disponible: {has_secrets}")
    if has_secrets:
        kaggle_user = st.secrets.get("KAGGLE_USERNAME", "NO ENCONTRADO")
        kaggle_key = st.secrets.get("KAGGLE_KEY", "NO ENCONTRADO")
        st.write(f"   KAGGLE_USERNAME: {kaggle_user[:10] if kaggle_user != 'NO ENCONTRADO' else kaggle_user}...")
        st.write(f"   KAGGLE_KEY: {kaggle_key[:10] if kaggle_key != 'NO ENCONTRADO' else kaggle_key}...")
except Exception as e:
    st.error(f"❌ Error leyendo secrets: {e}")

# Verificar directorio data
from pathlib import Path
data_dir = Path(__file__).parent / "data"
st.write(f"✅ data dir exists: {data_dir.exists()}, writable: {os.access(data_dir.parent, os.W_OK) if data_dir.parent.exists() else 'N/A'}")

# ════════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ════════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Criminalidad y Violencia en Colombia | Dashboard Científico",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/alejandro-quintero/dashboard-criminalidad-colombia',
        'Report a bug': 'https://github.com/alejandro-quintero/dashboard-criminalidad-colombia/issues',
        'About': (
            "**Dashboard Científico: Criminalidad y Violencia en Colombia**\n\n"
            "Maestría en Analítica de Datos — Politécnico Grancolombiano\n"
            "Autor: Alejandro Quintero Ruiz\n"
            "Curso: Visualización de Datos — Corte 3\n\n"
            "Fuentes: Kaggle (leonardoariasalemn/delitos-colombia, "
            "estiven0507/domestic-violence-in-colombia)"
        )
    }
)

# CSS personalizado para estética profesional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --navy: #0B1026;
        --bg-light: #131A3A;
        --amber: #FFB03A;
        --cyan: #35C4D9;
        --white: #F5F7FF;
        --muted: #8A93B8;
        --grid: rgba(255,255,255,0.06);
        --green: #4ADE80;
        --red: #F87171;
        --purple: #A78BFA;
    }
    
    .stApp {
        background: linear-gradient(180deg, var(--navy) 0%, #0F1530 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-light);
        border-right: 1px solid var(--grid);
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--white);
    }
    
    /* Headers principales */
    .main-header {
        background: linear-gradient(90deg, var(--navy) 0%, var(--bg-light) 100%);
        border-bottom: 3px solid var(--amber);
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
    }
    
    .main-header h1 {
        color: var(--white);
        font-weight: 700;
        font-size: 2rem;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .main-header .subtitle {
        color: var(--cyan);
        font-size: 1rem;
        font-weight: 400;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    .main-header .meta {
        color: var(--muted);
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }
    
    /* KPI Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .kpi-card {
        background: var(--bg-light);
        border: 1px solid var(--grid);
        border-radius: 12px;
        padding: 1.25rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: var(--amber);
    }
    
    .kpi-label {
        color: var(--muted);
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        color: var(--white);
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.2;
    }
    
    .kpi-delta {
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }
    
    .kpi-delta.positive { color: var(--green); }
    .kpi-delta.negative { color: var(--red); }
    
    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--grid);
    }
    
    .section-header .icon {
        color: var(--amber);
        font-size: 1.5rem;
    }
    
    .section-header h2 {
        color: var(--white);
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
    }
    
    .section-header .divider {
        flex: 1;
        height: 1px;
        background: var(--grid);
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(53, 196, 217, 0.08);
        border-left: 3px solid var(--cyan);
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
    }
    
    .info-box.warning {
        background: rgba(255, 176, 58, 0.08);
        border-left-color: var(--amber);
    }
    
    .info-box.error {
        background: rgba(248, 113, 113, 0.08);
        border-left-color: var(--red);
    }
    
    .info-box h4 {
        color: var(--white);
        margin: 0 0 0.5rem 0;
        font-size: 0.95rem;
    }
    
    .info-box p {
        color: var(--muted);
        margin: 0;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Data source badge */
    .source-badge {
        display: inline-block;
        background: var(--bg-light);
        border: 1px solid var(--grid);
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-size: 0.7rem;
        color: var(--muted);
        font-weight: 500;
    }
    
    /* Footer */
    .footer {
        margin-top: 3rem;
        padding: 2rem;
        border-top: 1px solid var(--grid);
        text-align: center;
        color: var(--muted);
        font-size: 0.85rem;
    }
    
    .footer .author {
        color: var(--white);
        font-weight: 600;
    }
    
    /* Metric improvements */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-light);
        border: 1px solid var(--grid);
        border-radius: 8px;
        color: var(--muted);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--amber) !important;
        color: var(--navy) !important;
        border-color: var(--amber) !important;
    }
    
    /* Selectbox, multiselect */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--bg-light) !important;
        border-color: var(--grid) !important;
        color: var(--white) !important;
    }
    
    .stSelectbox label,
    .stMultiSelect label,
    .stSlider label,
    .stNumberInput label,
    .stDateInput label {
        color: var(--white) !important;
        font-weight: 500 !important;
    }
    
    /* DataFrame */
    .stDataFrame {
        background: var(--bg-light);
    }
    
    .stDataFrame [data-testid="stTable"] {
        color: var(--white);
    }
    
    /* Plotly chart container */
    .js-plotly-plot {
        background: transparent !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-light) !important;
        border-color: var(--grid) !important;
        color: var(--white) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--navy) !important;
        border-color: var(--grid) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--navy);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--bg-light);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--amber);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.5rem; }
        .kpi-grid { grid-template-columns: 1fr; }
        .kpi-value { font-size: 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE VISUALIZACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

COLOR_PALETTE = {
    'primary': '#35C4D9',      # cyan
    'secondary': '#FFB03A',    # amber
    'accent': '#A78BFA',       # purple
    'success': '#4ADE80',      # green
    'danger': '#F87171',       # red
    'background': '#0B1026',   # navy
    'surface': '#131A3A',      # bg-light
    'grid': 'rgba(255,255,255,0.06)',
    'text': '#F5F7FF',         # white
    'muted': '#8A93B8',        # muted
}

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family='Inter, -apple-system, sans-serif', color=COLOR_PALETTE['text']),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor=COLOR_PALETTE['grid'],
            zerolinecolor=COLOR_PALETTE['grid'],
            showgrid=True,
            tickfont=dict(size=11),
            title=dict(font=dict(size=12, color=COLOR_PALETTE['muted'])),
        ),
        yaxis=dict(
            gridcolor=COLOR_PALETTE['grid'],
            zerolinecolor=COLOR_PALETTE['grid'],
            showgrid=True,
            tickfont=dict(size=11),
            title=dict(font=dict(size=12, color=COLOR_PALETTE['muted'])),
        ),
        colorway=[
            COLOR_PALETTE['primary'],
            COLOR_PALETTE['secondary'],
            COLOR_PALETTE['accent'],
            COLOR_PALETTE['success'],
            COLOR_PALETTE['danger'],
            '#FBBF24',
            '#34D399',
            '#60A5FA',
        ],
        hoverlabel=dict(
            bgcolor=COLOR_PALETTE['surface'],
            bordercolor=COLOR_PALETTE['grid'],
            font_size=12,
            font_family='Inter',
        ),
        legend=dict(
            bgcolor='rgba(19,26,58,0.9)',
            bordercolor=COLOR_PALETTE['grid'],
            borderwidth=1,
            font=dict(size=11),
        ),
        margin=dict(l=60, r=30, t=50, b=50),
    )
)


def create_kpi_card(label: str, value: str, delta: str | None = None, delta_color: str = "normal") -> str:
    """Genera HTML para tarjeta KPI."""
    delta_html = ""
    if delta:
        color_class = "positive" if delta_color == "inverse" else "negative" if delta_color == "normal" else ""
        delta_html = f'<div class="kpi-delta {color_class}">{delta}</div>'
    
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def plot_temporal_evolution(df: pd.DataFrame, date_col: str, value_col: str, 
                            title: str, group_col: str | None = None,
                            freq: str = 'M') -> go.Figure:
    """Gráfico de evolución temporal con agregación."""
    if df.empty:
        return go.Figure().update_layout(
            template=PLOTLY_TEMPLATE,
            title=dict(text=title, x=0.5, font=dict(size=16)),
            annotations=[dict(text="No hay datos para los filtros seleccionados",
                            xref="paper", yref="paper", x=0.5, y=0.5,
                            showarrow=False, font=dict(color=COLOR_PALETTE['muted'], size=14))]
        )
    
    df_plot = df.copy()
    df_plot[date_col] = pd.to_datetime(df_plot[date_col])
    
    if group_col and group_col in df_plot.columns:
        # Serie por grupo
        df_agg = df_plot.groupby([pd.Grouper(key=date_col, freq=freq), group_col])[value_col].sum().reset_index()
        fig = px.line(
            df_agg, x=date_col, y=value_col, color=group_col,
            title=title, template=PLOTLY_TEMPLATE,
            labels={value_col: 'Casos', date_col: 'Fecha', group_col: group_col.replace('_', ' ').title()}
        )
    else:
        df_agg = df_plot.groupby(pd.Grouper(key=date_col, freq=freq))[value_col].sum().reset_index()
        fig = px.line(
            df_agg, x=date_col, y=value_col,
            title=title, template=PLOTLY_TEMPLATE,
            labels={value_col: 'Casos', date_col: 'Fecha'}
        )
        fig.update_traces(line=dict(width=3, color=COLOR_PALETTE['primary']))
    
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=14, color=COLOR_PALETTE['text'])),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )
    
    # Línea de tendencia
    if not group_col and len(df_agg) > 3:
        from scipy import stats
        x_numeric = np.arange(len(df_agg))
        slope, intercept, _, _, _ = stats.linregress(x_numeric, df_agg[value_col])
        trend = slope * x_numeric + intercept
        fig.add_trace(go.Scatter(
            x=df_agg[date_col], y=trend,
            mode='lines', line=dict(dash='dash', width=1.5, color=COLOR_PALETTE['secondary']),
            name='Tendencia', showlegend=True
        ))
    
    return fig


def plot_top_categories(df: pd.DataFrame, cat_col: str, value_col: str,
                        title: str, top_n: int = 15, orientation: str = 'h') -> go.Figure:
    """Gráfico de barras para top categorías."""
    if df.empty:
        return go.Figure().update_layout(
            template=PLOTLY_TEMPLATE,
            title=dict(text=title, x=0.5),
            annotations=[dict(text="Sin datos", xref="paper", yref="paper", x=0.5, y=0.5,
                            showarrow=False, font=dict(color=COLOR_PALETTE['muted']))]
        )
    
    top_df = df.groupby(cat_col)[value_col].sum().nlargest(top_n).sort_values(ascending=True).reset_index()
    
    if orientation == 'h':
        fig = px.bar(
            top_df, x=value_col, y=cat_col, orientation='h',
            title=title, template=PLOTLY_TEMPLATE,
            labels={value_col: 'Casos', cat_col: cat_col.replace('_', ' ').title()},
            text=value_col
        )
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    else:
        fig = px.bar(
            top_df, x=cat_col, y=value_col,
            title=title, template=PLOTLY_TEMPLATE,
            labels={value_col: 'Casos', cat_col: cat_col.replace('_', ' ').title()},
            text=value_col
        )
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45)
    
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=14)),
        showlegend=False,
        margin=dict(l=120 if orientation == 'h' else 60, r=80, t=50, b=80 if orientation == 'v' else 50)
    )
    
    return fig


def plot_heatmap_calendar(df: pd.DataFrame, date_col: str, value_col: str,
                          title: str, year: int | None = None) -> go.Figure:
    """Heatmap estilo calendario (año-mes)."""
    df_plot = df.copy()
    df_plot[date_col] = pd.to_datetime(df_plot[date_col])
    
    if year:
        df_plot = df_plot[df_plot[date_col].dt.year == year]
    
    df_plot['año'] = df_plot[date_col].dt.year
    df_plot['mes'] = df_plot[date_col].dt.month
    
    pivot = df_plot.pivot_table(values=value_col, index='año', columns='mes', aggfunc='sum', fill_value=0)
    
    # Ordenar meses
    month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                   'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    pivot = pivot.reindex(columns=range(1, 13))
    pivot.columns = month_names
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index.astype(str),
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title='Casos', thickness=15, len=0.8),
        hovertemplate='Año: %{y}<br>Mes: %{x}<br>Casos: %{z:,.0f}<extra></extra>',
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=14)),
        template=PLOTLY_TEMPLATE,
        height=300 + len(pivot) * 35,
    )
    
    return fig


def plot_sunburst(df: pd.DataFrame, path_cols: list, value_col: str, title: str) -> go.Figure:
    """Gráfico sunburst para jerarquías."""
    if df.empty:
        return go.Figure().update_layout(template=PLOTLY_TEMPLATE, title=title)
    
    fig = px.sunburst(
        df, path=path_cols, values=value_col,
        title=title, template=PLOTLY_TEMPLATE,
        color_discrete_sequence=px.colors.sequential.Viridis_r
    )
    
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=14)),
        margin=dict(t=50, l=0, r=0, b=0),
    )
    fig.update_traces(textinfo='label+percent parent')
    
    return fig


def plot_treemap(df: pd.DataFrame, path_cols: list, value_col: str, title: str) -> go.Figure:
    """Treemap para composición."""
    if df.empty:
        return go.Figure().update_layout(template=PLOTLY_TEMPLATE, title=title)
    
    fig = px.treemap(
        df, path=path_cols, values=value_col,
        title=title, template=PLOTLY_TEMPLATE,
        color=value_col, color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=14)),
        margin=dict(t=50, l=0, r=0, b=0),
    )
    
    return fig


def plot_comparison_bars(df1: pd.DataFrame, df2: pd.DataFrame, 
                         cat_col: str, value_col: str,
                         label1: str, label2: str, title: str,
                         top_n: int = 10) -> go.Figure:
    """Gráfico de barras comparativo entre dos datasets."""
    top1 = df1.groupby(cat_col)[value_col].sum().nlargest(top_n)
    top2 = df2.groupby(cat_col)[value_col].sum().nlargest(top_n)
    
    all_cats = sorted(set(top1.index) | set(top2.index))
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=label1,
        x=all_cats,
        y=[top1.get(c, 0) for c in all_cats],
        marker_color=COLOR_PALETTE['primary'],
        hovertemplate='%{x}: %{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        name=label2,
        x=all_cats,
        y=[top2.get(c, 0) for c in all_cats],
        marker_color=COLOR_PALETTE['secondary'],
        hovertemplate='%{x}: %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=14)),
        template=PLOTLY_TEMPLATE,
        barmode='group',
        xaxis_tickangle=-45,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )
    
    return fig


def plot_scatter_correlation(df: pd.DataFrame, x_col: str, y_col: str,
                             color_col: str | None, size_col: str | None,
                             title: str) -> go.Figure:
    """Scatter plot con línea de regresión."""
    if df.empty:
        return go.Figure().update_layout(template=PLOTLY_TEMPLATE, title=title)
    
    fig = px.scatter(
        df, x=x_col, y=y_col, color=color_col, size=size_col,
        title=title, template=PLOTLY_TEMPLATE,
        trendline='ols' if len(df) > 10 else None,
        hover_data={x_col: ':,.0f', y_col: ':,.0f'}
    )
    
    fig.update_layout(
        title=dict(text=title, x=0.02, font=dict(size=14)),
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title(),
    )
    
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# COMPONENTES DE UI
# ═══════════════════════════════════════════════════════════════════════════════

def render_header():
    """Renderiza el encabezado principal."""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Criminalidad y Violencia en Colombia</h1>
        <div class="subtitle">Dashboard Científico — Análisis Exploratorio y Comparativo</div>
        <div class="meta">
            Maestría en Analítica de Datos · Politécnico Grancolombiano · 
            <span class="author">Alejandro Quintero Ruiz</span> · 
            Visualización de Datos — Corte 3
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_filters(df_delitos: pd.DataFrame, df_domestic: pd.DataFrame) -> dict:
    """Renderiza controles de filtro en la barra lateral y retorna parámetros."""
    st.sidebar.markdown("## 🎛️ Controles de Análisis")
    
    # Período de análisis
    st.sidebar.markdown("### 📅 Período Temporal")
    
    min_year_delitos = int(df_delitos['año'].min())
    max_year_delitos = int(df_delitos['año'].max())
    min_year_domestic = int(df_domestic['año'].min())
    max_year_domestic = int(df_domestic['año'].max())
    
    global_min = min(min_year_delitos, min_year_domestic)
    global_max = max(max_year_delitos, max_year_domestic)
    
    año_ini, año_fin = st.sidebar.slider(
        "Rango de años",
        min_value=global_min,
        max_value=global_max,
        value=(max(global_min, 2020), global_max),
        help="Filtrar ambos datasets por rango de años"
    )
    
    # Departamento
    st.sidebar.markdown("### 🗺️ Filtro Geográfico")
    deps_comunes = get_departamentos_comunes(df_delitos, df_domestic)
    deps_disponibles = sorted(df_delitos['departamento'].unique())
    
    departamentos = st.sidebar.multiselect(
        "Departamentos",
        options=deps_disponibles,
        default=[],
        help="Dejar vacío para analizar todo el país"
    )
    
    # Tipo de delito (solo dataset delitos)
    st.sidebar.markdown("### 🔍 Filtros Específicos")
    
    tipos_delito = sorted(df_delitos['tipo'].unique())
    tipos_seleccionados = st.sidebar.multiselect(
        "Tipos de delito (Dataset General)",
        options=tipos_delito,
        default=[],
        help="Incluye 'Violencia intrafamiliar' para comparar con dataset específico"
    )
    
    # Género
    generos_delitos = ['FEMENINO', 'MASCULINO', 'NO REPORTADO']
    generos_domestic = ['FEMENINO', 'MASCULINO', 'NO REPORTADO', 'NO REPORTA', 'INTERSEXUAL']
    generos = st.sidebar.multiselect(
        "Género de la víctima",
        options=sorted(set(generos_delitos + generos_domestic)),
        default=[],
    )
    
    # Edad
    rangos_edad_delitos = ['MENORES', 'ADOLESCENTES', 'ADULTOS', 'NO REPORTADO']
    rangos_edad_domestic = ['MENORES', 'ADOLESCENTES', 'ADULTOS', 'NO REPORTADO', 'NO REPORTA']
    rangos_edad = st.sidebar.multiselect(
        "Grupo etario",
        options=sorted(set(rangos_edad_delitos + rangos_edad_domestic)),
        default=[],
    )
    
    # Solo violencia intrafamiliar
    solo_vi = st.sidebar.checkbox(
        "Solo Violencia Intrafamiliar (Dataset General)",
        value=False,
        help="Filtra el dataset general para mostrar solo violencia intrafamiliar"
    )
    
    # Armas/medios (solo domestic)
    armas = sorted(df_domestic['armas_medios'].dropna().unique())
    armas_sel = st.sidebar.multiselect(
        "Armas/Medios (Violencia Intrafamiliar)",
        options=armas,
        default=[],
    )
    
    st.sidebar.markdown("---")
    
    # Información de datasets
    st.sidebar.markdown("### 📋 Información de Datasets")
    st.sidebar.caption(f"""
    **Delitos Colombia**: {len(df_delitos):,} registros ({min_year_delitos}-{max_year_delitos})
    
    **Violencia Intrafamiliar**: {len(df_domestic):,} registros ({min_year_domestic}-{max_year_domestic})
    
    **Período común**: 2020-2023
    """)
    
    # Botón de descarga
    st.sidebar.markdown("### 💾 Exportar")
    if st.sidebar.button("📥 Descargar datos filtrados (CSV)", use_container_width=True):
        st.sidebar.info("Función de exportación en desarrollo")
    
    return {
        'año_ini': año_ini,
        'año_fin': año_fin,
        'departamentos': departamentos,
        'tipos_delito': tipos_seleccionados,
        'generos': generos,
        'rango_edad': rangos_edad,
        'solo_violencia_intrafamiliar': solo_vi,
        'armas_medios': armas_sel,
    }


def render_kpi_row(df_delitos_f: pd.DataFrame, df_domestic_f: pd.DataFrame, 
                    df_delitos_all: pd.DataFrame, df_domestic_all: pd.DataFrame):
    """Renderiza fila de KPIs principales."""
    
    # Cálculos
    total_delitos = df_delitos_f['cantidad'].sum()
    total_domestic = df_domestic_f['cantidad'].sum()
    
    # Comparación con total (sin filtros geográficos/temporales restrictivos)
    total_delitos_base = df_delitos_all['cantidad'].sum()
    total_domestic_base = df_domestic_all['cantidad'].sum()
    
    pct_delitos = (total_delitos / total_delitos_base * 100) if total_delitos_base > 0 else 0
    pct_domestic = (total_domestic / total_domestic_base * 100) if total_domestic_base > 0 else 0
    
    # Violencia intrafamiliar en dataset general
    vi_general = df_delitos_f[df_delitos_f['es_violencia_intrafamiliar']]['cantidad'].sum()
    
    # Top departamento
    if not df_delitos_f.empty:
        top_dep = df_delitos_f.groupby('departamento')['cantidad'].sum().idxmax()
        top_dep_val = df_delitos_f.groupby('departamento')['cantidad'].sum().max()
    else:
        top_dep = "—"
        top_dep_val = 0
    
    # Tasa por 100k habitantes (aproximada, población Colombia ~52M)
    POBLACION_COLOMBIA = 52_000_000
    tasa_nacional = (total_delitos / POBLACION_COLOMBIA) * 100_000
    
    # HTML para KPIs
    kpis_html = f"""
    <div class="kpi-grid">
        {create_kpi_card("Total Delitos (Filtrado)", f"{total_delitos:,.0f}", 
                         f"{pct_delitos:.1f}% del total", "normal")}
        {create_kpi_card("Violencia Intrafamiliar (Específico)", f"{total_domestic:,.0f}", 
                         f"{pct_domestic:.1f}% del total", "normal")}
        {create_kpi_card("VI en Dataset General", f"{vi_general:,.0f}", 
                         f"{(vi_general/total_delitos*100):.1f}% del filtrado" if total_delitos > 0 else "—", "normal")}
        {create_kpi_card("Departamento Líder", top_dep, 
                         f"{top_dep_val:,.0f} casos", "normal")}
        {create_kpi_card("Tasa Nacional (x100k hab.)", f"{tasa_nacional:.1f}", 
                         "Población: ~52M", "normal")}
    </div>
    """
    st.markdown(kpis_html, unsafe_allow_html=True)


def render_text_analysis(df_delitos_f: pd.DataFrame, df_domestic_f: pd.DataFrame, 
                         filters: dict) -> None:
    """Renderiza análisis estadístico en texto (output de texto requerido)."""
    st.markdown('<div class="section-header"><span class="icon">📝</span><h2>Resumen Estadístico</h2><div class="divider"></div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Dataset General de Delitos")
        if not df_delitos_f.empty:
            total = df_delitos_f['cantidad'].sum()
            n_tipos = df_delitos_f['tipo'].nunique()
            n_deps = df_delitos_f['departamento'].nunique()
            n_mun = df_delitos_f['municipio'].nunique()
            fecha_min = df_delitos_f['fecha'].min().strftime('%Y-%m-%d')
            fecha_max = df_delitos_f['fecha'].max().strftime('%Y-%m-%d')
            
            # Top 3 delitos
            top3 = df_delitos_f.groupby('tipo')['cantidad'].sum().nlargest(3)
            top3_str = ", ".join([f"{k} ({v:,.0f})" for k, v in top3.items()])
            
            # Distribución género
            gen_dist = df_delitos_f.groupby('genero', observed=False)['cantidad'].sum()
            gen_str = ", ".join([f"{k}: {v/total*100:.1f}%" for k, v in gen_dist.items() if v > 0])
            
            st.markdown(f"""
            <div class="info-box">
                <h4>📈 Métricas Agregadas</h4>
                <p><strong>Total casos:</strong> {total:,.0f} | 
                   <strong>Tipos de delito:</strong> {n_tipos} | 
                   <strong>Depts:</strong> {n_deps} | 
                   <strong>Munic.:</strong> {n_mun}</p>
                <p><strong>Período:</strong> {fecha_min} a {fecha_max}</p>
                <p><strong>Top 3 delitos:</strong> {top3_str}</p>
                <p><strong>Distribución por género:</strong> {gen_str}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Estadísticas descriptivas
            desc = df_delitos_f['cantidad'].describe()
            st.markdown(f"""
            <div class="info-box warning">
                <h4>📊 Estadísticas Descriptivas (Casos por registro)</h4>
                <p>Media: {desc['mean']:.1f} | Mediana: {desc['50%']:.1f} | 
                   Desv.Est: {desc['std']:.1f} | Max: {desc['max']:,.0f}</p>
                <p>Q1: {desc['25%']:.1f} | Q3: {desc['75%']:.1f} | IQR: {desc['75%']-desc['25%']:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No hay datos para los filtros seleccionados en el dataset general.")
    
    with col2:
        st.markdown("#### 🏠 Dataset Violencia Intrafamiliar")
        if not df_domestic_f.empty:
            total = df_domestic_f['cantidad'].sum()
            n_deps = df_domestic_f['departamento'].nunique()
            n_mun = df_domestic_f['municipio'].nunique()
            fecha_min = df_domestic_f['fecha_hecho'].min().strftime('%Y-%m-%d')
            fecha_max = df_domestic_f['fecha_hecho'].max().strftime('%Y-%m-%d')
            
            # Top armas
            top_armas = df_domestic_f.groupby('armas_medios')['cantidad'].sum().nlargest(3)
            armas_str = ", ".join([f"{k} ({v:,.0f})" for k, v in top_armas.items()])
            
            # Distribución género
            gen_dist = df_domestic_f.groupby('genero', observed=False)['cantidad'].sum()
            gen_str = ", ".join([f"{k}: {v/total*100:.1f}%" for k, v in gen_dist.items() if v > 0])
            
            st.markdown(f"""
            <div class="info-box">
                <h4>📈 Métricas Agregadas</h4>
                <p><strong>Total casos:</strong> {total:,.0f} | 
                   <strong>Depts:</strong> {n_deps} | 
                   <strong>Munic.:</strong> {n_mun}</p>
                <p><strong>Período:</strong> {fecha_min} a {fecha_max}</p>
                <p><strong>Top 3 armas/medios:</strong> {armas_str}</p>
                <p><strong>Distribución por género:</strong> {gen_str}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Comparación con dataset general (período overlap)
            overlap_start, overlap_end = get_overlap_period(
                df_delitos_f, df_domestic_f
            )
            if overlap_start <= overlap_end:
                df_del_overlap = df_delitos_f[
                    (df_delitos_f['fecha'] >= overlap_start) & 
                    (df_delitos_f['fecha'] <= overlap_end) &
                    (df_delitos_f['es_violencia_intrafamiliar'])
                ]
                vi_gen_overlap = df_del_overlap['cantidad'].sum()
                vi_dom_overlap = df_domestic_f[
                    (df_domestic_f['fecha_hecho'] >= overlap_start) & 
                    (df_domestic_f['fecha_hecho'] <= overlap_end)
                ]['cantidad'].sum()
                
                ratio = vi_dom_overlap / vi_gen_overlap if vi_gen_overlap > 0 else 0
                
                st.markdown(f"""
                <div class="info-box warning">
                    <h4>🔗 Validación Cruzada (Período Común: {overlap_start.year}-{overlap_end.year})</h4>
                    <p><strong>VI en Dataset General:</strong> {vi_gen_overlap:,.0f}</p>
                    <p><strong>VI en Dataset Específico:</strong> {vi_dom_overlap:,.0f}</p>
                    <p><strong>Ratio Específico/General:</strong> {ratio:.2f} 
                       {"✅ Consistencia alta" if 0.8 <= ratio <= 1.2 else "⚠️ Discrepancia significativa"}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No hay datos para los filtros seleccionados en violencia intrafamiliar.")


def render_temporal_analysis(df_delitos_f: pd.DataFrame, df_domestic_f: pd.DataFrame) -> None:
    """Análisis temporal con gráficos interactivos."""
    st.markdown('<div class="section-header"><span class="icon">📈</span><h2>Evolución Temporal</h2><div class="divider"></div></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Serie Mensual", "📆 Heatmap Anual", "🔄 Comparativo Anual", "📊 Acumulado"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = plot_temporal_evolution(
                df_delitos_f, 'fecha', 'cantidad',
                'Evolución Mensual - Todos los Delitos',
                freq='M'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            # Solo violencia intrafamiliar del dataset general
            vi_general = df_delitos_f[df_delitos_f['es_violencia_intrafamiliar']]
            fig = plot_temporal_evolution(
                vi_general, 'fecha', 'cantidad',
                'Violencia Intrafamiliar (Dataset General)',
                freq='M'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Dataset específico
        if not df_domestic_f.empty:
            fig = plot_temporal_evolution(
                df_domestic_f, 'fecha_hecho', 'cantidad',
                'Violencia Intrafamiliar (Dataset Específico)',
                freq='M'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            años_disponibles = sorted(df_delitos_f['año'].unique(), reverse=True)
            año_sel = st.selectbox("Año para heatmap (Delitos)", años_disponibles, key="heatmap_year_del")
            fig = plot_heatmap_calendar(df_delitos_f, 'fecha', 'cantidad', 
                                        f'Heatmap Mensual - Delitos {año_sel}', año_sel)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            if not df_domestic_f.empty:
                años_dom = sorted(df_domestic_f['año'].unique(), reverse=True)
                año_sel_dom = st.selectbox("Año para heatmap (VI Específica)", años_dom, key="heatmap_year_dom")
                fig = plot_heatmap_calendar(df_domestic_f, 'fecha_hecho', 'cantidad',
                                            f'Heatmap Mensual - VI Específica {año_sel_dom}', año_sel_dom)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab3:
        # Comparativo anual apilado
        if not df_delitos_f.empty and not df_domestic_f.empty:
            # Agregar por año
            anual_delitos = df_delitos_f.groupby('año')['cantidad'].sum().reset_index()
            anual_delitos['dataset'] = 'Delitos Generales'
            
            vi_general = df_delitos_f[df_delitos_f['es_violencia_intrafamiliar']].groupby('año')['cantidad'].sum().reset_index()
            vi_general['dataset'] = 'VI (General)'
            
            anual_domestic = df_domestic_f.groupby('año')['cantidad'].sum().reset_index()
            anual_domestic['dataset'] = 'VI (Específico)'
            
            df_combined = pd.concat([anual_delitos, vi_general, anual_domestic])
            
            fig = px.bar(
                df_combined, x='año', y='cantidad', color='dataset',
                title='Comparativo Anual: Delitos Totales vs Violencia Intrafamiliar',
                template=PLOTLY_TEMPLATE,
                barmode='group',
                text='cantidad',
                color_discrete_map={
                    'Delitos Generales': COLOR_PALETTE['primary'],
                    'VI (General)': COLOR_PALETTE['accent'],
                    'VI (Específico)': COLOR_PALETTE['secondary'],
                }
            )
            fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig.update_layout(
                title=dict(x=0.02, font=dict(size=14)),
                xaxis=dict(tickmode='linear'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab4:
        # Acumulado
        if not df_delitos_f.empty:
            df_del_sorted = df_delitos_f.sort_values('fecha')
            df_del_sorted['acumulado'] = df_del_sorted['cantidad'].cumsum()
            
            fig = px.area(
                df_del_sorted.groupby('fecha')['acumulado'].last().reset_index(),
                x='fecha', y='acumulado',
                title='Casos Acumulados - Delitos Generales',
                template=PLOTLY_TEMPLATE,
            )
            fig.update_traces(line=dict(color=COLOR_PALETTE['primary'], width=2),
                             fillcolor=f"rgba(53,196,217,0.2)")
            fig.update_layout(title=dict(x=0.02, font=dict(size=14)))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_geographic_analysis(df_delitos_f: pd.DataFrame, df_domestic_f: pd.DataFrame) -> None:
    """Análisis geográfico."""
    st.markdown('<div class="section-header"><span class="icon">🗺️</span><h2>Análisis Geográfico</h2><div class="divider"></div></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏆 Top Departamentos", "🌳 Composición (Treemap)", "🔍 Detalle Municipal"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = plot_top_categories(
                df_delitos_f, 'departamento', 'cantidad',
                'Top 15 Departamentos - Delitos Generales',
                top_n=15
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            if not df_domestic_f.empty:
                fig = plot_top_categories(
                    df_domestic_f, 'departamento', 'cantidad',
                    'Top 15 Departamentos - VI Específica',
                    top_n=15
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_delitos_f.empty:
                fig = plot_treemap(
                    df_delitos_f, ['departamento', 'tipo'], 'cantidad',
                    'Composición Delitos por Departamento y Tipo'
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            if not df_domestic_f.empty:
                fig = plot_treemap(
                    df_domestic_f, ['departamento', 'armas_medios'], 'cantidad',
                    'VI Específica: Dept. × Armas/Medios'
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab3:
        # Selector de departamento para detalle municipal
        deps_con_datos = sorted(df_delitos_f['departamento'].unique())
        if deps_con_datos:
            dep_sel = st.selectbox("Seleccionar departamento para detalle municipal", deps_con_datos)
            
            col1, col2 = st.columns(2)
            
            with col1:
                df_mun_del = df_delitos_f[df_delitos_f['departamento'] == dep_sel].groupby('municipio')['cantidad'].sum().nlargest(20).reset_index()
                fig = px.bar(
                    df_mun_del.sort_values('cantidad'), x='cantidad', y='municipio', orientation='h',
                    title=f'Top 20 Municipios - {dep_sel} (Delitos)',
                    template=PLOTLY_TEMPLATE,
                    labels={'cantidad': 'Casos', 'municipio': 'Municipio'}
                )
                fig.update_layout(title=dict(x=0.02, font=dict(size=13)), height=500)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            with col2:
                if not df_domestic_f.empty:
                    df_mun_dom = df_domestic_f[df_domestic_f['departamento'] == dep_sel].groupby('municipio')['cantidad'].sum().nlargest(20).reset_index()
                    if not df_mun_dom.empty:
                        fig = px.bar(
                            df_mun_dom.sort_values('cantidad'), x='cantidad', y='municipio', orientation='h',
                            title=f'Top 20 Municipios - {dep_sel} (VI Específica)',
                            template=PLOTLY_TEMPLATE,
                            labels={'cantidad': 'Casos', 'municipio': 'Municipio'}
                        )
                        fig.update_layout(title=dict(x=0.02, font=dict(size=13)), height=500)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.info(f"No hay datos de VI específica para {dep_sel} con los filtros actuales")


def render_demographic_analysis(df_delitos_f: pd.DataFrame, df_domestic_f: pd.DataFrame) -> None:
    """Análisis demográfico (género, edad)."""
    st.markdown('<div class="section-header"><span class="icon">👥</span><h2>Perfil Demográfico de Víctimas</h2><div class="divider"></div></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["⚥ Género", "👶 Grupo Etario", "⚔️ Armas/Medios"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_delitos_f.empty:
                gen_del = df_delitos_f.groupby('genero', observed=False)['cantidad'].sum().reset_index()
                fig = px.pie(
                    gen_del, values='cantidad', names='genero',
                    title='Distribución por Género - Delitos Generales',
                    template=PLOTLY_TEMPLATE,
                    color_discrete_sequence=[COLOR_PALETTE['primary'], COLOR_PALETTE['secondary'], COLOR_PALETTE['muted']],
                    hole=0.4
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(title=dict(x=0.02, font=dict(size=13)))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            if not df_domestic_f.empty:
                gen_dom = df_domestic_f.groupby('genero', observed=False)['cantidad'].sum().reset_index()
                fig = px.pie(
                    gen_dom, values='cantidad', names='genero',
                    title='Distribución por Género - VI Específica',
                    template=PLOTLY_TEMPLATE,
                    color_discrete_sequence=[COLOR_PALETTE['accent'], COLOR_PALETTE['secondary'], COLOR_PALETTE['muted'], '#FBBF24', '#F87171'],
                    hole=0.4
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(title=dict(x=0.02, font=dict(size=13)))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_delitos_f.empty:
                edad_del = df_delitos_f.groupby('rango_edad', observed=False)['cantidad'].sum().reset_index()
                fig = px.bar(
                    edad_del, x='rango_edad', y='cantidad',
                    title='Distribución por Grupo Etario - Delitos Generales',
                    template=PLOTLY_TEMPLATE,
                    text='cantidad',
                    color='rango_edad',
                    color_discrete_sequence=px.colors.sequential.Viridis_r
                )
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig.update_layout(title=dict(x=0.02, font=dict(size=13)), showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            if not df_domestic_f.empty:
                edad_dom = df_domestic_f.groupby('grupo_etario', observed=False)['cantidad'].sum().reset_index()
                fig = px.bar(
                    edad_dom, x='grupo_etario', y='cantidad',
                    title='Distribución por Grupo Etario - VI Específica',
                    template=PLOTLY_TEMPLATE,
                    text='cantidad',
                    color='grupo_etario',
                    color_discrete_sequence=px.colors.sequential.Plasma_r
                )
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig.update_layout(title=dict(x=0.02, font=dict(size=13)), showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            if not df_delitos_f.empty:
                arma_del = df_delitos_f.groupby('tipo_arma')['cantidad'].sum().nlargest(10).reset_index()
                fig = px.bar(
                    arma_del.sort_values('cantidad'), x='cantidad', y='tipo_arma', orientation='h',
                    title='Top 10 Tipos de Arma - Delitos Generales',
                    template=PLOTLY_TEMPLATE,
                    text='cantidad',
                    color='cantidad',
                    color_continuous_scale='Viridis'
                )
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig.update_layout(title=dict(x=0.02, font=dict(size=13)), height=450, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            if not df_domestic_f.empty:
                arma_dom = df_domestic_f.groupby('armas_medios')['cantidad'].sum().reset_index()
                fig = px.bar(
                    arma_dom.sort_values('cantidad'), x='cantidad', y='armas_medios', orientation='h',
                    title='Armas/Medios - VI Específica',
                    template=PLOTLY_TEMPLATE,
                    text='cantidad',
                    color='cantidad',
                    color_continuous_scale='Plasma'
                )
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig.update_layout(title=dict(x=0.02, font=dict(size=13)), height=450, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_correlation_analysis(df_delitos_f: pd.DataFrame, df_domestic_f: pd.DataFrame) -> None:
    """Análisis de correlación y validación cruzada."""
    st.markdown('<div class="section-header"><span class="icon">🔗</span><h2>Validación Cruzada y Correlaciones</h2><div class="divider"></div></div>', unsafe_allow_html=True)
    
    # Preparar datos para correlación a nivel departamental
    if not df_delitos_f.empty and not df_domestic_f.empty:
        # Agregar por departamento
        dep_del = df_delitos_f.groupby('departamento_norm').agg(
            total_delitos=('cantidad', 'sum'),
            vi_general=('cantidad', lambda x: x[df_delitos_f.loc[x.index, 'es_violencia_intrafamiliar']].sum())
        ).reset_index()
        
        dep_dom = df_domestic_f.groupby('departamento_norm').agg(
            vi_especifica=('cantidad', 'sum')
        ).reset_index()
        
        # Merge
        dep_merged = dep_del.merge(dep_dom, on='departamento_norm', how='outer').fillna(0)
        
        # Mapear nombres bonitos
        dep_names = dict(zip(df_delitos_f['departamento_norm'], df_delitos_f['departamento']))
        dep_names.update(dict(zip(df_domestic_f['departamento_norm'], df_domestic_f['departamento'])))
        dep_merged['departamento'] = dep_merged['departamento_norm'].map(dep_names)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Scatter: VI General vs VI Específica por departamento
            fig = px.scatter(
                dep_merged, x='vi_general', y='vi_especifica',
                size='total_delitos', hover_name='departamento',
                title='Correlación: VI General vs VI Específica (por Departamento)',
                template=PLOTLY_TEMPLATE,
                trendline='ols',
                labels={'vi_general': 'VI en Dataset General', 'vi_especifica': 'VI en Dataset Específico'}
            )
            fig.update_layout(title=dict(x=0.02, font=dict(size=13)))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            # Ratio
            dep_merged['ratio'] = np.where(
                dep_merged['vi_general'] > 0,
                dep_merged['vi_especifica'] / dep_merged['vi_general'],
                0
            )
            fig = px.bar(
                dep_merged.sort_values('ratio'),
                x='ratio', y='departamento', orientation='h',
                title='Ratio VI Específica / VI General por Departamento',
                template=PLOTLY_TEMPLATE,
                labels={'ratio': 'Ratio', 'departamento': 'Departamento'},
                color='ratio',
                color_continuous_scale='RdYlGn_r',
                range_color=[0, 2]
            )
            fig.add_vline(x=1, line_dash="dash", line_color="white", annotation_text="Paridad (1.0)")
            fig.update_layout(title=dict(x=0.02, font=dict(size=13)), height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Tabla de correlación
        st.markdown("#### 📋 Tabla de Validación por Departamento")
        display_cols = ['departamento', 'total_delitos', 'vi_general', 'vi_especifica', 'ratio']
        dep_display = dep_merged[display_cols].copy()
        dep_display.columns = ['Departamento', 'Total Delitos', 'VI General', 'VI Específica', 'Ratio']
        dep_display['Ratio'] = dep_display['Ratio'].round(2)
        dep_display = dep_display.sort_values('Total Delitos', ascending=False)
        
        st.dataframe(
            dep_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Total Delitos": st.column_config.NumberColumn(format="%,.0f"),
                "VI General": st.column_config.NumberColumn(format="%,.0f"),
                "VI Específica": st.column_config.NumberColumn(format="%,.0f"),
                "Ratio": st.column_config.NumberColumn(format="%.2f"),
            }
        )
        
        # Coeficiente de correlación global
        from scipy import stats
        if len(dep_merged) > 2:
            r, p = stats.pearsonr(dep_merged['vi_general'], dep_merged['vi_especifica'])
            st.markdown(f"""
            <div class="info-box {'success' if r > 0.7 else 'warning' if r > 0.4 else 'error'}">
                <h4>📊 Correlación Global (Pearson)</h4>
                <p><strong>r = {r:.3f}</strong> | p-value = {p:.4f}</p>
                <p>{"Correlación fuerte - Los datasets son consistentes" if r > 0.7 else 
                   "Correlación moderada - Alguna discrepancia entre fuentes" if r > 0.4 else 
                   "Correlación débil - Datasets miden fenómenos diferentes"}</p>
            </div>
            """, unsafe_allow_html=True)


def render_data_tables(df_delitos_f: pd.DataFrame, df_domestic_f: pd.DataFrame) -> None:
    """Tablas de datos filtrados (requisito: tabla con datos filtrados)."""
    st.markdown('<div class="section-header"><span class="icon">📋</span><h2>Tablas de Datos Filtrados</h2><div class="divider"></div></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔝 Top Registros Delitos", "🔝 Top Registros VI Específica", "📊 Resumen por Categoría"])
    
    with tab1:
        if not df_delitos_f.empty:
            # Top 50 por cantidad
            top_del = df_delitos_f.nlargest(50, 'cantidad')[
                ['fecha', 'tipo', 'delito', 'departamento', 'municipio', 'genero', 'rango_edad', 'tipo_arma', 'cantidad']
            ].copy()
            top_del['fecha'] = top_del['fecha'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                top_del,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "cantidad": st.column_config.NumberColumn("Casos", format="%,.0f"),
                    "fecha": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
                }
            )
            
            st.caption(f"Mostrando top 50 de {len(df_delitos_f):,} registros filtrados")
        else:
            st.info("No hay datos con los filtros actuales.")
    
    with tab2:
        if not df_domestic_f.empty:
            top_dom = df_domestic_f.nlargest(50, 'cantidad')[
                ['fecha_hecho', 'departamento', 'municipio', 'genero', 'grupo_etario', 'armas_medios', 'cantidad']
            ].copy()
            top_dom['fecha_hecho'] = top_dom['fecha_hecho'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(
                top_dom,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "cantidad": st.column_config.NumberColumn("Casos", format="%,.0f"),
                    "fecha_hecho": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
                }
            )
            
            st.caption(f"Mostrando top 50 de {len(df_domestic_f):,} registros filtrados")
        else:
            st.info("No hay datos con los filtros actuales.")
    
    with tab3:
        # Resumen por tipo de delito
        if not df_delitos_f.empty:
            resumen_tipo = df_delitos_f.groupby('tipo').agg(
                Total_Casos=('cantidad', 'sum'),
                N_Registros=('cantidad', 'count'),
                Promedio_Casos=('cantidad', 'mean'),
                Max_Casos=('cantidad', 'max'),
            ).sort_values('Total_Casos', ascending=False).reset_index()
            
            st.dataframe(
                resumen_tipo,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Total_Casos": st.column_config.NumberColumn("Total Casos", format="%,.0f"),
                    "N_Registros": st.column_config.NumberColumn("N Registros", format="%,.0f"),
                    "Promedio_Casos": st.column_config.NumberColumn("Promedio", format="%.1f"),
                    "Max_Casos": st.column_config.NumberColumn("Máximo", format="%,.0f"),
                }
            )


def render_footer():
    """Footer con créditos."""
    st.markdown("""
    <div class="footer">
        <p><strong>Dashboard Científico: Criminalidad y Violencia en Colombia</strong></p>
        <p class="author">Desarrollado por Alejandro Quintero Ruiz</p>
        <p>Maestría en Analítica de Datos — Politécnico Grancolombiano</p>
        <p>Curso: Visualización de Datos — Corte 3</p>
        <p style="margin-top: 1rem;">
            Fuentes: 
            <span class="source-badge">Kaggle: leonardoariasalemn/delitos-colombia</span>
            <span class="source-badge">Kaggle: estiven0507/domestic-violence-in-colombia</span>
        </p>
        <p style="margin-top: 0.5rem; font-size: 0.75rem;">
            Código disponible en GitHub · Construido con Streamlit + Plotly · Python 3.11+
        </p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Función principal del dashboard."""
    render_header()
    
    # Cargar datos (con caché)
    with st.spinner("Cargando datasets..."):
        df_delitos = load_delitos()
        df_domestic = load_domestic_violence()
    
    # Filtros en sidebar
    filters = render_sidebar_filters(df_delitos, df_domestic)
    
    # Aplicar filtros
    df_delitos_f = filter_delitos(df_delitos, **filters)
    df_domestic_f = filter_domestic(df_domestic, **filters)
    
    # KPIs principales
    render_kpi_row(df_delitos_f, df_domestic_f, df_delitos, df_domestic)
    
    # Análisis en texto (requisito: output de texto con cálculo/resumen)
    render_text_analysis(df_delitos_f, df_domestic_f, filters)
    
    # Separador visual
    st.markdown("<hr style='border-color: var(--grid); margin: 2rem 0;'>", unsafe_allow_html=True)
    
    # Tabs principales de análisis
    main_tabs = st.tabs([
        "📈 Evolución Temporal",
        "🗺️ Análisis Geográfico", 
        "👥 Perfil Demográfico",
        "🔗 Validación Cruzada",
        "📋 Tablas de Datos"
    ])
    
    with main_tabs[0]:
        render_temporal_analysis(df_delitos_f, df_domestic_f)
    
    with main_tabs[1]:
        render_geographic_analysis(df_delitos_f, df_domestic_f)
    
    with main_tabs[2]:
        render_demographic_analysis(df_delitos_f, df_domestic_f)
    
    with main_tabs[3]:
        render_correlation_analysis(df_delitos_f, df_domestic_f)
    
    with main_tabs[4]:
        render_data_tables(df_delitos_f, df_domestic_f)
    
    # Footer
    render_footer()


if __name__ == "__main__":
    main()