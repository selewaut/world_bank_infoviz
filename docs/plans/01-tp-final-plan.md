# TP Final — Plan de trabajo

> Plantilla de planificación. Completar los `TODO` y ajustar según el avance.

## Metadata

| Campo | Valor |
|---|---|
| Materia | InfoVis — ECD.2026.B |
| Trabajo | TP Final — Visualización de Datos con World Bank Data360 |
| Integrantes | TODO (3) |
| Entrega | 2026-11-30 00:00 |
| Estado | Paso 1 completado — tema y visualizaciones a definir |
| Herramienta | Python + Altair en Colab (recomendado); Observable para publicar |
| Repo | `world_bank_infoviz` |

## 1. Resumen del enunciado

- **Paso 1:** explorar la API de Data360 → qué bases de datos existen, qué indicadores hay, cómo se estructuran (país, tiempo, temática).
- **Paso 2:** hasta **3 visualizaciones** (preferentemente interactivas), aptas para una nota/artículo periodístico.
- **Bonus:** usar el protocolo MCP para acceder a la API. *(Ya configurado en `opencode.json` → `data360-mcp`.)*
- Enunciado completo: [`InfoVis _ ECD.2026.B _ TP Final.md`](../../InfoVis%20_%20ECD.2026.B%20_%20TP%20Final.md)

## 2. Objetivo y pregunta de investigación

- **Tema tentativo:** TODO — datacenters / internet / conectividad / energía / infraestructura.
- **Pregunta central:** TODO
- **Mensaje en una frase (para el lector periodístico):** TODO
- **Por qué es relevante:** TODO

## 3. Alcance del tema

- **Incluye:** TODO
- **Excluye:** TODO
- **Recorte geográfico:** TODO (global / regiones / países seleccionados)
- **Recorte temporal:** TODO (último año / serie histórica / comparación de períodos)

## 4. Paso 1 — Exploración de la API

> Resultados completos y tablas: [`02-api-exploration-findings.md`](02-api-exploration-findings.md).
> Datos crudos y derivados en `data/`; scripts en `scripts/`.

### 4.0 Pipeline reproducible

| Script | Qué hace | Salidas principales |
|---|---|---|
| `scripts/explore_api.py` | Baja metadatos de los 9.859 indicadores (paginado 1000) | `data/raw/data360_indicators.jsonl.gz`, `database_summary.csv`, `indicators.csv`, `topic_summary.csv`, `freshness_summary.csv` |
| `scripts/check_freshness.py` | Verifica último dato **real** (no nominal) | `granular_freshness.csv`, `database_actual_freshness.csv` |
| `scripts/region_coverage.py` | Cobertura por región desde `ref_country` | `database_region_coverage.csv`, `region_overall.csv` |

**Definiciones**
- **Completitud:** cobertura nominal de metadatos (`ref_country` / `economies_count`), no densidad real de observaciones.
- **Frescura nominal:** `time_periods.end` (puede incluir proyecciones).
- **Frescura real:** máximo `TIME_PERIOD` observado en `/data360/data` para una sonda representativa.

### 4.1 Bases de datos

Panorama verificado: **174 bases**, **9.859 indicadores**, 12.601 documentos.
Categorías L0: Prosperity (4.551 ind), People (832), Planet (291), Infrastructure (291), Digital (141).
Temas L1 y subtemas L2 en el documento de hallazgos.

Shortlist de foco (datacenter / conectividad / energía / infraestructura):

| ID | Nombre | Ind. | Span nominal | Último real | Rol |
|---|---|---:|---|---:|---|
| `PEERING_DB` | Connected Data Centers | 1 | 2023 | 2023 | Datacenters (snapshot) |
| `PCH_IXP` | Internet Exchange Directory | 2 | 2024 | 2024 | IXPs |
| `OOKLA_ST` | Speed Test | 2 | 2019–2024 | 2024 | Velocidad |
| `ITU_DH` | ITU DataHub | 39 | 2000–2025 | 2022* | Conectividad |
| `WB_WDI` | World Development Indicators | 1.545 | 1960–2025 | 2024 | Internet/energía |
| `WB_SE4ALL` | Sustainable Energy for All | 8 | 1990–2022 | 2021 | Energía |
| `WB_RISE` | Regulatory Indicators Sustainable Energy | 27 | 2010–2023 | 2023 | Energía (política) |
| `WB_PPI` | Private Participation in Infrastructure | 5 | 1990–2024 | 2024 | Inversión infra |

\* Sonda de menor cobertura; la base declara datos hasta 2025.

### 4.2 Indicadores

- 95% anuales; solo **36 subanuales** (33 mensuales, 3 trimestrales); **0 semanales/diarias**.
- Cobertura mediana 141 economías; 88 bases con mediana ≥150.
- Estructura de observación: `REF_AREA`, `TIME_PERIOD`, `OBS_VALUE`, `UNIT_MEASURE`, `OBS_STATUS`, `LATEST_DATA` + desagregaciones opcionales.
- Shortlist de indicadores por tema: ver §6 de los hallazgos.

### 4.3 Estructura de los datos

- **Modelo:** base de datos → indicador (`series_description`) → observaciones.
- **Dimensiones:**
  - `REF_AREA` — país ISO3 **o agregado regional** (`EAS`, `SAS`, …).
  - `TIME_PERIOD` — año, trimestre (`2025-Q2`) o mes (`2026-03`).
  - `UNIT_MEASURE` — `PT_POP`, `DC`, `KBPS`, etc.
  - `REGION` — agrupación regional; excluir de los países.
  - `SEX` / `AGE` / `URBANISATION` — desagregaciones opcionales.
- **Ejemplo:** `REF_AREA=BRA`, `TIME_PERIOD=2023`, `OBS_VALUE=84.15`, `UNIT_MEASURE=PT_POP`.

### 4.4 Advertencias / calidad de datos

- [x] Filtrar agregados regionales (`REGION`) de los países reales.
- [x] Verificar cobertura y años disponibles por indicador.
- [x] Registrar fuente y metodología de cada indicador.
- [x] `date_last_update` vacío en los 9.859 indicadores.
- [x] `time_periods.end` incluye proyecciones (WEO 2031) y a veces subestima (UNCTAD 2023 vs real 2025).
- [x] `OBS_STATUS=A` no distingue valores proyectados.
- [x] `$top` máximo 1000; paginar con `$skip`; no usar `$count=true` (HTTP 417).
- [x] `$skip` sin `$orderby` duplica/omite documentos: ordenar por `database_id,idno` y deduplicar.
- [x] `tags` es campo de primer nivel; `topics`/`time_periods`/`ref_country` están en `series_description`.

### 4.5 Visualizaciones de exploración (opcionales)

> **No** son las 3 visualizaciones obligatorias del enunciado: son candidatas para mostrar el Paso 1 (anexo / notebook de exploración). Elegir 0–3 más adelante.

| # | Visualización | Codificación | Fuente | ¿La hacemos? |
|---|---|---|---|---|
| 1 | Treemap jerárquico L0 → L1 → L2 | área = indicadores | `topic_summary.csv` | No — mezcla 19 vocabularios y ~40 % de indicadores sin L1/L2; jerarquía no limpia |
| 2 | Barras top-N bases por indicadores, color = tema L1 | x = indicadores, y = base | `database_summary.csv` | **Sí** |
| 3 | Heatmap base × región | color = cobertura media | `database_region_coverage.csv` | No — 171 bases × 9 regiones es demasiado denso para un anexo |
| 4 | Dumbbell fin nominal vs último dato real | par de puntos por base | `database_actual_freshness.csv` | **Sí** |
| 5 | Barras apiladas de periodicidad | conteo por periodicidad | `indicators.csv` | No — 95 % anual; se resuelve con una frase, no con un gráfico |
| 6 | Scatter indicadores vs cobertura mediana | x = ind., y = cobertura | `database_summary.csv` | **Sí** |

Detalle de cada una: `02-api-exploration-findings.md` §8.

**Decisión (3/6):** se construyen **#2, #4 y #6**, porque cubren tres ángulos distintos del catálogo:
- **#2** — panorama: qué bases concentran más indicadores (líderes del catálogo).
- **#4** — calidad: 44 de 158 bases tienen fin nominal ≠ último dato real (39 desactualizadas, 5 con proyecciones), evidencia directa de la advertencia de frescura.
- **#6** — selección: amplitud vs profundidad, resaltando las 8 bases del shortlist temático; justifica el recorte del Paso 2.

#1, #3 y #5 quedan descartadas por las razones de la tabla; si se necesita contexto regional o de periodicidad, va como nota al pie del anexo.

## 5. Paso 2 — Visualizaciones (3 obligatorias)

### Visualización 1

- **Pregunta:** TODO
- **Indicador(es):** TODO
- **Tipo de gráfico:** TODO
- **Herramienta:** TODO
- **Interactividad:** TODO (filtro, tooltip, slider, etc.)
- **Nota de fuente:** TODO

### Visualización 2

- **Pregunta:** TODO
- **Indicador(es):** TODO
- **Tipo de gráfico:** TODO
- **Herramienta:** TODO
- **Interactividad:** TODO
- **Nota de fuente:** TODO

### Visualización 3

- **Pregunta:** TODO
- **Indicador(es):** TODO
- **Tipo de gráfico:** TODO
- **Herramienta:** TODO
- **Interactividad:** TODO
- **Nota de fuente:** TODO

## 6. Setup técnico

- [x] Servidor MCP `data360-mcp` configurado (`opencode.json`).
- [x] Entorno Python (`uv`) con `requests` instalado.
- [x] Dependencias de visualización: `pandas`, `altair`, `jupyterlab` (gestionadas con `uv`).
- [x] Estructura de carpetas: `scripts/`, `notebooks/`, `data/raw/`, `data/derived/`, `docs/plans/`.
- [x] Estrategia de obtención de datos: API REST para extracción masiva + MCP para consultas interactivas.

## 7. Hitos

- [x] **Hito 1** — Bases de datos e indicadores relevados (Paso 1).
- [x] **Hito 2** — Estructura, completitud, frescura y advertencias documentadas.
- [ ] **Hito 3** — Datos descargados y validados **para el tema elegido**.
- [ ] **Hito 4** — Visualización 1.
- [ ] **Hito 5** — Visualización 2.
- [ ] **Hito 6** — Visualización 3.
- [ ] **Hito 7** — Redacción / notas de fuente / entrega.

## 8. Preguntas abiertas y decisiones

| # | Pregunta | Decisión | Fecha |
|---|---|---|---|
| 1 | ¿Qué viz de exploración construir? | #2 (top-N bases), #4 (dumbbell frescura) y #6 (scatter amplitud/profundidad) | 2026-11-20 |
| 2 | Herramienta de las viz | Altair / Vega-Lite leyendo los CSV de `data/derived/` | 2026-11-20 |

## Apéndice A — Acceso a la API

**MCP (interactivo)**
1. `search_datasets` → identificar bases de datos.
2. `search_indicators` → identificar indicadores.
3. `get_disaggregation` → años, unidades y desagregaciones disponibles.
4. `get_data` / `compare_countries` / `rank_countries` → obtener valores.
5. `get_viz_spec` → borrador de gráfico Vega-Lite.

**REST (extracción masiva, usada por los scripts)**

| Método | Endpoint |
|---|---|
| POST | `https://data360api.worldbank.org/data360/metadata` |
| GET | `/data360/indicators?datasetId=…` |
| GET | `/data360/disaggregation?datasetId=…&indicatorId=…` |
| GET | `/data360/data?DATABASE_ID=…&INDICATOR=…&REF_AREA=…` |
| POST | `/data360/searchv2` |
| GET | `/data360/portal/v1/hierarchy?type=country` |

OpenAPI: `https://raw.githubusercontent.com/worldbank/open-api-specs/refs/heads/main/Data360%20Open_API.json`

## Apéndice B — Catálogo de referencia (verificado)

> Punto de partida ya consultado contra la API. Mover a §4.1–4.2 lo que se use.

**Datacenters / interconexión**
- `PEERING_DB` — Interconnection / Connected Data Centers · 162 econ · **solo 2023**.
  - `PEERING_DB_CONN_DATA_CENT` — Number of connected data centers.
- `PCH_IXP` — Internet Exchange Directory · 158 econ · 1993–2023.
  - `PCH_IXP_NUM`, `PCH_IXP_PARTICIPANTS`.

**Conectividad / acceso**
- `ITU_DH` — ITU DataHub · 236 econ · 2000–2025.
  - `IT_NET_BBND`, `IT_CEL_SETS`.
- `OOKLA_ST` — Speed Test · 244 econ · 2019–2024.
  - `OOKLA_ST_MOB_PER`, `OOKLA_ST_FIX_PER`.
- `WB_WDI` — World Development Indicators · 1990–2025.
  - `WB_WDI_IT_NET_USER_ZS`, `WB_WDI_IT_NET_BBND`, `WB_WDI_IT_CEL_SETS`.
- `OECD_BROADBAND`, `UNCTAD_DE`, `PI_NRI`, `ITU_GCI`, `ITU_ICT`.

**Energía**
- `WB_SE4ALL` — 234 econ · 1990–2022.
- `WB_RISE` — 140 econ · 2010–2023.
- `EIA_EIAOD` — 220 econ · 1980–2022.
- Indicadores: `WB_WDI_EG_ELC_ACCS_ZS`, `WB_WDI_EG_FEC_RNEW_ZS`, `WB_WDI_EG_EGY_PRIM_PP_KD`, `WB_RISE_EA_ALL`, `WB_RISE_RE_ELEC`.

**Infraestructura**
- `WB_PPI` — Private Participation in Infrastructure · 133 econ · 1990–2024.
  - `PSD_PPI_ICT_INV`, `PSD_PPI_ENR_INV`, `PSD_PPI_TOT_INV`.

**Advertencia clave:** `PEERING_DB` es un snapshot de 2023 → no permite serie temporal de datacenters; usar comparación entre países o cruce con conectividad/energía.
