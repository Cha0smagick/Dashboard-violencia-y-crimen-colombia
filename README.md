# 📊 Dashboard Científico: Criminalidad y Violencia en Colombia

> **Maestría en Analítica de Datos** — Politécnico Grancolombiano  
> **Autor:** Alejandro Quintero Ruiz  
> **Curso:** Visualización de Datos — Corte 3  

Dashboard interactivo de nivel científico para el análisis exploratorio y comparativo de criminalidad general y violencia intrafamiliar en Colombia, integrando dos datasets de Kaggle con validación cruzada, visualizaciones avanzadas y filtros dinámicos.

---

## 🎯 Características Principales

| Componente | Descripción |
|------------|-------------|
| **🔧 Input Interactivo** | Filtros dinámicos: rango temporal (slider), departamentos (multiselect), tipos de delito, género, grupo etario, armas/medios |
| **📝 Output de Texto** | Resumen estadístico automático: métricas agregadas, estadísticas descriptivas, validación cruzada entre datasets |
| **📈 Gráficos Plotly** | Series temporales, heatmaps calendario, treemaps, sunbursts, scatter con regresión, barras comparativas, pie charts |
| **📋 Tablas Filtradas** | Top registros, resúmenes por categoría, tabla de validación departamental con ratio de consistencia |
| **🔗 Validación Cruzada** | Correlación departamental entre dataset general y específico (Pearson r, p-value) |
| **📱 Responsivo** | Diseño adaptable mobile/desktop con CSS custom y tema oscuro profesional |

---

## 📊 Fuentes de Datos

| Dataset | Registros | Período | Descripción |
|---------|-----------|---------|-------------|
| [`leonardoariasalemn/delitos-colombia`](https://www.kaggle.com/datasets/leonardoariasalemn/delitos-colombia) | 2.38M | 2020-2026 | Delitos generales (18 tipos, 54 artículos, 32 depts, 1029 munic.) |
| [`estiven0507/domestic-violence-in-colombia`](https://www.kaggle.com/datasets/estiven0507/domestic-violence-in-colombia) | 575K | 2010-2023 | Violencia intrafamiliar específica (11 armas/medios, 33 depts) |

**Período de solapamiento:** 2020-2023 (4 años) — permite validación cruzada directa.

---

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Python 3.10+
- Cuenta Kaggle (para descarga inicial de datasets)

### Pasos

```bash
# 1. Clonar repositorio
git clone https://github.com/alejandro-quintero/dashboard-criminalidad-colombia.git
cd dashboard-criminalidad-colombia

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar credenciales Kaggle (una sola vez)
# Obtener token en: https://www.kaggle.com/settings/account
mkdir -p ~/.kaggle
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# 5. Ejecutar dashboard
streamlit run app.py
```

El dashboard se abrirá en `http://localhost:8501`

---

## 🎨 Capturas de Pantalla

### Vista Principal - KPIs y Resumen Estadístico
![Dashboard Principal](docs/screenshots/main.png)

### Evolución Temporal con Heatmap
![Temporal](docs/screenshots/temporal.png)

### Análisis Geográfico - Treemap
![Geográfico](docs/screenshots/geographic.png)

### Validación Cruzada - Correlación Departamental
![Correlación](docs/screenshots/correlation.png)

---

## 🏗️ Arquitectura del Proyecto

```
dashboard-criminalidad-colombia/
├── app.py                 # Aplicación principal Streamlit
├── data_loader.py         # Carga y preprocesamiento de datos (cached)
├── requirements.txt       # Dependencias Python
├── .streamlit/
│   └── config.toml       # Configuración Streamlit
├── data/                 # Datasets cacheados (generados automáticamente)
│   ├── delitos_colombia.pkl
│   └── domestic_violence_colombia.pkl
├── docs/
│   └── screenshots/      # Capturas para README
└── README.md
```

### Módulos Clave

| Archivo | Responsabilidad |
|---------|-----------------|
| `app.py` | UI, layout, visualizaciones, lógica de presentación |
| `data_loader.py` | ETL, caché, normalización de texto, filtros, joins |

---

## 🔬 Metodología Científica

### 1. Normalización para Integración
```python
# Homologación de claves geográficas
normalize_text(series) → minúsculas + sin acentos + trim
# Permite join departamentales pese a encoding distinto
```

### 2. Validación Cruzada (Período 2020-2023)
- **Dataset General:** `Violencia intrafamiliar` = 211,373 casos
- **Dataset Específico:** Violencia intrafamiliar = 223,791 casos  
- **Ratio:** 1.06 → **Alta consistencia** entre fuentes independientes

### 3. Correlación Departamental (Pearson)
- Cálculo a nivel departamental (n=32)
- Scatter con línea de regresión OLS
- Ratio Específico/General por departamento
- Test de significancia estadística (p-value)

### 4. Visualizaciones Nivel Q4 (Científico)
- **Ejes con etiquetas de valor** y unidades
- **Leyendas informativas** y tooltips enriquecidos
- **Líneas de tendencia** con regresión lineal
- **Heatmaps calendario** para estacionalidad
- **Treemaps/Sunbursts** para composición jerárquica
- **Paleta accesible** (viridis, plasma) + colores semánticos

---

## 🎛️ Controles Disponibles

| Control | Tipo | Afecta |
|---------|------|--------|
| Rango de años | Slider (dual) | Ambos datasets |
| Departamentos | Multiselect | Ambos datasets |
| Tipos de delito | Multiselect | Solo dataset general |
| Género víctima | Multiselect | Ambos datasets |
| Grupo etario | Multiselect | Ambos datasets |
| Solo VI (general) | Checkbox | Dataset general |
| Armas/medios | Multiselect | Solo dataset específico |

---

## 📦 Dependencias Principales

```txt
streamlit>=1.28.0      # Framework web
plotly>=5.17.0         # Visualizaciones interactivas
pandas>=2.1.0          # Manipulación de datos
numpy>=1.24.0          # Computación numérica
kagglehub>=0.3.0       # Descarga datasets Kaggle
```

Ver `requirements.txt` para versiones completas.

---

## 📄 Licencia

Este proyecto es parte del trabajo académico para la **Maestría en Analítica de Datos** del **Politécnico Grancolombiano**.

**Uso educativo y de investigación.** Para uso comercial, contactar al autor.

---

## 👨‍💻 Autor

**Alejandro Quintero Ruiz**  
Estudiante de Maestría en Analítica de Datos  
Politécnico Grancolombiano — Bogotá, Colombia  

- GitHub: [@alejandro-quintero](https://github.com/alejandro-quintero)
- LinkedIn: [linkedin.com/in/alejandro-quintero-ruiz](https://linkedin.com/in/alejandro-quintero-ruiz)

---

## 🙏 Agradecimientos

- A los autores de los datasets en Kaggle por hacerlos públicos
- Al Politécnico Grancolombiano por la formación en analítica de datos
- A la comunidad de Streamlit y Plotly por herramientas excepcionales

---

> *"Los datos no mienten, pero requieren preguntas correctas para revelar la verdad."*  
> — Dashboard construido con rigor científico, estética profesional y cero *AI slop*.