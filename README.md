# 📊 Dashboard Científico: Criminalidad y Violencia en Colombia

> **Maestría en Analítica de Datos** — Politécnico Grancolombiano  
> **Autor:** Alejandro Quintero Ruiz  
> **Curso:** Visualización de Datos — Corte 3  

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)](#-licencia)
[![Status](https://img.shields.io/badge/Status-Production-green.svg)]()

Dashboard interactivo de **nivel científico** para el análisis exploratorio y comparativo de criminalidad general y violencia intrafamiliar en Colombia, integrando dos datasets de Kaggle con validación cruzada, visualizaciones avanzadas y filtros dinámicos.

---

## 🌐 Demo Live

**Dashboard desplegado y funcionando:**  
🔗 **https://dashboard-violencia-y-crimen-colombia.streamlit.app/**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dashboard-violencia-y-crimen-colombia.streamlit.app/)

> **Nota:** La primera carga tarda ~30-60s mientras descarga los datasets de Kaggle (2.38M + 575K registros). Luego queda en caché.

---

## 🎯 Características Principales

| Componente | Descripción |
|------------|-------------|
| **🔧 Input Interactivo** | Filtros dinámicos: rango temporal (slider 2010-2026), 32 departamentos (multiselect), 18 tipos de delito, género, grupo etario, 11 armas/medios |
| **📝 Output de Texto** | Resumen estadístico automático: métricas agregadas, estadísticas descriptivas, validación cruzada entre datasets (ratio 1.06) |
| **📈 Gráficos Plotly** | Series temporales con tendencia OLS, heatmaps calendario, treemaps, sunbursts, scatter con regresión, barras comparativas, pie charts |
| **📋 Tablas Filtradas** | Top 50 registros, resúmenes por categoría, tabla validación departamental con ratio y correlación Pearson (r, p-value) |
| **🔗 Validación Cruzada** | Correlación departamental entre dataset general y específico (n=32, test significancia) |
| **📱 100% Responsivo** | CSS Grid/Flexbox, media queries ≤768px, tema oscuro profesional (navy/amber/cyan) |

---

## 📊 Fuentes de Datos

| Dataset | Registros | Período | Descripción |
|---------|-----------|---------|-------------|
| [`leonardoariasalemn/delitos-colombia`](https://www.kaggle.com/datasets/leonardoariasalemn/delitos-colombia) | **2.38M** | 2020-2026 | Delitos generales: 18 tipos, 54 artículos, 32 depts, 1,029 munic. |
| [`estiven0507/domestic-violence-in-colombia`](https://www.kaggle.com/datasets/estiven0507/domestic-violence-in-colombia) | **575K** | 2010-2023 | Violencia intrafamiliar: 11 armas/medios, 33 depts |

**Período de solapamiento:** 2020-2023 (4 años) — permite validación cruzada directa.

---

## 🚀 Instalación Local

### Prerrequisitos
- Python 3.10+
- Cuenta Kaggle (para descarga inicial automática de datasets)

### Pasos

```bash
# 1. Clonar repositorio
git clone https://github.com/Cha0smagick/Dashboard-violencia-y-crimen-colombia.git
cd Dashboard-violencia-y-crimen-colombia

# 2. Crear entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar credenciales Kaggle (una sola vez)
# Obtener token en: https://www.kaggle.com/settings/account
mkdir -p ~/.kaggle
# Coloca tu kaggle.json en ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json

# 5. Ejecutar dashboard
streamlit run app.py
```

> 📍 Se abre en `http://localhost:8501`  
> 📥 **Los datasets se descargan automáticamente de Kaggle** la primera vez (cache local en `data/`)

---

## ☁️ Deploy en Streamlit Community Cloud (Gratis, 2 min)

1. Ve a **[share.streamlit.io](https://share.streamlit.io)** → Login con GitHub
2. **New app** → Repository: `Cha0smagick/Dashboard-violencia-y-crimen-colombia` → Branch: `main` → File: `app.py`
3. **Advanced settings** → Secrets (opcional, para Kaggle):
   ```toml
   KAGGLE_USERNAME = "tu_usuario"
   KAGGLE_KEY = "tu_api_key"
   ```
4. **Deploy** → ¡Listo en 2-3 min!

> ⚡ **Ventaja:** No subas los datasets (pesan 160MB). La app los descarga de Kaggle al iniciar.

---

## 🏗️ Arquitectura

```
Dashboard-violencia-y-crimen-colombia/
├── app.py                 # Dashboard principal Streamlit (5 tabs, 1500+ líneas)
├── data_loader.py         # ETL, caché @st.cache_data, normalización, filtros
├── requirements.txt       # Dependencias: streamlit, plotly, pandas, numpy, kagglehub
├── .streamlit/
│   └── config.toml       # Tema oscuro, puerto 8501, CORS
├── .gitignore            # Ignora *.pkl, venv, credenciales, caché
├── data/                 # Se crea auto al descargar de Kaggle (no en git)
│   ├── delitos_colombia.pkl
│   └── domestic_violence_colombia.pkl
└── README.md
```

---

## 🔬 Metodología Científica

### 1. Normalización para Integración
```python
# Homologación de claves geográficas (encoding distinto entre datasets)
normalize_text(series) → minúsculas + sin acentos (NFKD) + trim
# Permite join departamentales pese a encoding distinto
```

### 2. Validación Cruzada (Período 2020-2023)
- **Dataset General:** `Violencia intrafamiliar` = 211,373 casos
- **Dataset Específico:** Violencia intrafamiliar = 223,791 casos  
- **Ratio:** 1.06 → **Alta consistencia** entre fuentes independientes

### 3. Correlación Departamental (Pearson)
- Cálculo a nivel departamental (n=32)
- Scatter con línea de regresión OLS + trust interval
- Ratio Específico/General por departamento (heatmap)
- Test significancia estadística (p-value)

### 4. Visualizaciones Nivel Q4 (Estándar Académico)
- Ejes con etiquetas de valor y unidades SI
- Leyendas informativas + tooltips enriquecidos (hover)
- Líneas de tendencia con regresión lineal (scipy.stats.linregress)
- Heatmaps calendario para estacionalidad mensual/anual
- Treemaps/Sunbursts para composición jerárquica (depto × tipo × arma)
- Paletas accesibles (viridis, plasma) + colores semánticos (cyan/amber/purple)

---

## 🎛️ Controles Disponibles (Sidebar)

| Control | Tipo | Dataset Afectado |
|---------|------|------------------|
| Rango de años | Slider dual (2010-2026) | Ambos |
| Departamentos | Multiselect (32) | Ambos |
| Tipos de delito | Multiselect (18) | Solo General |
| Género víctima | Multiselect (5) | Ambos |
| Grupo etario | Multiselect (5) | Ambos |
| Solo VI (general) | Checkbox | Solo General |
| Armas/Medios | Multiselect (11) | Solo Específico |

---

## 📦 Dependencias

```txt
streamlit>=1.28.0      # Framework web reactivo
plotly>=5.17.0         # Visualizaciones interactivas WebGL
pandas>=2.1.0          # Manipulación datos (PyArrow backend)
numpy>=1.24.0          # Computación numérica vectorizada
kagglehub>=0.3.0       # Descarga datasets Kaggle API
```

Ver `requirements.txt` para versiones completas pinned.

---

## 📄 Licencia

Este proyecto es trabajo académico para la **Maestría en Analítica de Datos** del **Politécnico Grancolombiano**.

**Uso educativo y de investigación.** Para uso comercial, contactar al autor.

---

## 👨‍💻 Autor

**Alejandro Quintero Ruiz**  
Estudiante de Maestría en Analítica de Datos  
Politécnico Grancolombiano — Bogotá, Colombia  

- GitHub: [@Cha0smagick](https://github.com/Cha0smagick)
- Repo: [Dashboard-violencia-y-crimen-colombia](https://github.com/Cha0smagick/Dashboard-violencia-y-crimen-colombia)

---

## 🙏 Agradecimientos

- A los autores de los datasets en Kaggle por hacerlos públicos
- Al Politécnico Grancolombiano por la formación en analítica de datos
- A la comunidad de Streamlit y Plotly por herramientas excepcionales

---

> *"Los datos no mienten, pero requieren preguntas correctas para revelar la verdad."*  
> — Dashboard construido con rigor científico, estética profesional y **cero AI slop**.