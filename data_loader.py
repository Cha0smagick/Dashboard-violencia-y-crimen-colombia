"""
Módulo de carga y preprocesamiento de datos
Dashboard Científico - Criminalidad y Violencia en Colombia
Maestría en Analítica de Datos - Politécnico Grancolombiano
Autor: Alejandro Quintero Ruiz
"""

import pandas as pd
import numpy as np
from pathlib import Path
import kagglehub
from kagglehub import KaggleDatasetAdapter
import os

# Streamlit debe importarse antes de usar @st.cache_data
import streamlit as st


# Rutas de archivos cacheados
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DELITOS_PATH = DATA_DIR / "delitos_colombia.pkl"
DOMESTIC_PATH = DATA_DIR / "domestic_violence_colombia.pkl"


def _configure_kaggle_credentials() -> bool:
    """Configura credenciales Kaggle desde st.secrets o variables de entorno.
    Retorna True si están disponibles, False si faltan."""
    # Prioridad: st.secrets > env vars > ~/.kaggle/kaggle.json
    username = st.secrets.get("KAGGLE_USERNAME", os.environ.get("KAGGLE_USERNAME", ""))
    key = st.secrets.get("KAGGLE_KEY", os.environ.get("KAGGLE_KEY", ""))
    
    if username and key:
        os.environ["KAGGLE_USERNAME"] = username
        os.environ["KAGGLE_KEY"] = key
        return True
    
    # Verificar si existe ~/.kaggle/kaggle.json
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_json.exists():
        return True
    
    return False


def _show_kaggle_error(dataset_name: str) -> None:
    """Muestra error amigable cuando faltan credenciales Kaggle."""
    st.error(f"""
    ❌ **Credenciales de Kaggle requeridas** para descargar `{dataset_name}`
    
    **En Streamlit Cloud:** Ve a **Manage app → Settings → Secrets** y agrega:
    ```toml
    KAGGLE_USERNAME = "cha0smagick"
    KAGGLE_KEY = "KGAT_0eadfea8127585d36cd300b2d9cb65e0"
    ```
    
    **En local:** Crea `~/.kaggle/kaggle.json` con:
    ```json
    {{"username": "cha0smagick", "key": "KGAT_0eadfea8127585d36cd300b2d9cb65e0"}}
    ```
    
    Obtén tu token en: https://www.kaggle.com/settings/account
    """)
    st.stop()


def normalize_text(series: pd.Series) -> pd.Series:
    """Normaliza texto para joins: minúsculas, sin acentos, sin espacios extra."""
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('ascii')
    )


@st.cache_data(show_spinner="Cargando dataset de delitos (2.38M registros)...")
def load_delitos() -> pd.DataFrame:
    """Carga y preprocesa el dataset general de delitos."""
    if not _configure_kaggle_credentials():
        _show_kaggle_error("leonardoariasalemn/delitos-colombia")
    
    if DELITOS_PATH.exists():
        df = pd.read_pickle(DELITOS_PATH)
    else:
        try:
            df = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                "leonardoariasalemn/delitos-colombia",
                "v_delitos.csv"
            )
            df.to_pickle(DELITOS_PATH)
        except Exception as e:
            st.error(f"Error descargando dataset: {e}")
            _show_kaggle_error("leonardoariasalemn/delitos-colombia")
    
    # Preprocesamiento
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df['año'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month
    df['trimestre'] = df['fecha'].dt.quarter
    df['departamento_norm'] = normalize_text(df['departamento'])
    df['municipio_norm'] = normalize_text(df['municipio'])
    df['es_violencia_intrafamiliar'] = df['tipo'] == 'Violencia intrafamiliar'
    
    # Categoría de edad ordenada
    edad_order = ['MENORES', 'ADOLESCENTES', 'ADULTOS', 'NO REPORTADO']
    df['rango_edad'] = pd.Categorical(df['rango_edad'], categories=edad_order, ordered=True)
    
    # Género ordenado
    genero_order = ['FEMENINO', 'MASCULINO', 'NO REPORTADO']
    df['genero'] = pd.Categorical(df['genero'], categories=genero_order, ordered=True)
    
    return df


@st.cache_data(show_spinner="Cargando dataset de violencia intrafamiliar (575K registros)...")
def load_domestic_violence() -> pd.DataFrame:
    """Carga y preprocesa el dataset específico de violencia intrafamiliar."""
    if not _configure_kaggle_credentials():
        _show_kaggle_error("estiven0507/domestic-violence-in-colombia")
    
    if DOMESTIC_PATH.exists():
        df = pd.read_pickle(DOMESTIC_PATH)
    else:
        try:
            df = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                "estiven0507/domestic-violence-in-colombia",
                "raw_data.csv"
            )
            df.to_pickle(DOMESTIC_PATH)
        except Exception as e:
            st.error(f"Error descargando dataset: {e}")
            _show_kaggle_error("estiven0507/domestic-violence-in-colombia")
    
    # Preprocesamiento
    df['fecha_hecho'] = pd.to_datetime(df['fecha_hecho'], dayfirst=True, format='mixed', errors='coerce')
    df['año'] = df['fecha_hecho'].dt.year
    df['mes'] = df['fecha_hecho'].dt.month
    df['trimestre'] = df['fecha_hecho'].dt.quarter
    df['departamento_norm'] = normalize_text(df['departamento'])
    df['municipio_norm'] = normalize_text(df['municipio'])
    df['codigo_dane_num'] = pd.to_numeric(df['codigo_dane'], errors='coerce').astype('Int64')
    
    # Categoría de edad ordenada
    edad_order = ['MENORES', 'ADOLESCENTES', 'ADULTOS', 'NO REPORTADO', 'NO REPORTA']
    df['grupo_etario'] = pd.Categorical(df['grupo_etario'], categories=edad_order, ordered=True)
    
    # Género ordenado
    genero_order = ['FEMENINO', 'MASCULINO', 'NO REPORTADO', 'NO REPORTA', 'INTERSEXUAL']
    df['genero'] = pd.Categorical(df['genero'], categories=genero_order, ordered=True)
    
    return df


@st.cache_data
def get_overlap_period(df_delitos: pd.DataFrame, df_domestic: pd.DataFrame) -> tuple:
    """Calcula el período de solapamiento entre ambos datasets."""
    min_delitos = df_delitos['fecha'].min()
    max_delitos = df_delitos['fecha'].max()
    min_domestic = df_domestic['fecha_hecho'].min()
    max_domestic = df_domestic['fecha_hecho'].max()
    
    overlap_start = max(min_delitos, min_domestic)
    overlap_end = min(max_delitos, max_domestic)
    
    return overlap_start, overlap_end


@st.cache_data
def get_departamentos_comunes(df_delitos: pd.DataFrame, df_domestic: pd.DataFrame) -> list:
    """Obtiene lista de departamentos presentes en ambos datasets."""
    deps_delitos = set(df_delitos['departamento_norm'].unique())
    deps_domestic = set(df_domestic['departamento_norm'].unique())
    comunes = sorted(deps_delitos & deps_domestic)
    # Mapear de vuelta a nombres originales bonitos
    mapping = dict(zip(df_delitos['departamento_norm'], df_delitos['departamento']))
    return [mapping.get(d, d) for d in comunes]


@st.cache_data
def filter_delitos(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Filtra el dataset de delitos según parámetros."""
    mask = pd.Series(True, index=df.index)
    
    if 'año_ini' in kwargs and kwargs['año_ini']:
        mask &= df['año'] >= kwargs['año_ini']
    if 'año_fin' in kwargs and kwargs['año_fin']:
        mask &= df['año'] <= kwargs['año_fin']
    if 'departamentos' in kwargs and kwargs['departamentos']:
        mask &= df['departamento_norm'].isin([normalize_text(d) for d in kwargs['departamentos']])
    if 'tipos_delito' in kwargs and kwargs['tipos_delito']:
        mask &= df['tipo'].isin(kwargs['tipos_delito'])
    if 'generos' in kwargs and kwargs['generos']:
        mask &= df['genero'].isin(kwargs['generos'])
    if 'rango_edad' in kwargs and kwargs['rango_edad']:
        mask &= df['rango_edad'].isin(kwargs['rango_edad'])
    if 'solo_violencia_intrafamiliar' in kwargs and kwargs['solo_violencia_intrafamiliar']:
        mask &= df['es_violencia_intrafamiliar']
    
    return df[mask].copy()


@st.cache_data
def filter_domestic(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Filtra el dataset de violencia intrafamiliar según parámetros."""
    mask = pd.Series(True, index=df.index)
    
    if 'año_ini' in kwargs and kwargs['año_ini']:
        mask &= df['año'] >= kwargs['año_ini']
    if 'año_fin' in kwargs and kwargs['año_fin']:
        mask &= df['año'] <= kwargs['año_fin']
    if 'departamentos' in kwargs and kwargs['departamentos']:
        mask &= df['departamento_norm'].isin([normalize_text(d) for d in kwargs['departamentos']])
    if 'generos' in kwargs and kwargs['generos']:
        mask &= df['genero'].isin(kwargs['generos'])
    if 'grupo_etario' in kwargs and kwargs['grupo_etario']:
        mask &= df['grupo_etario'].isin(kwargs['grupo_etario'])
    if 'armas_medios' in kwargs and kwargs['armas_medios']:
        mask &= df['armas_medios'].isin(kwargs['armas_medios'])
    
    return df[mask].copy()