# Paso 1 — Exploración de la API Data360 (hallazgos)

> Documento de resultados del relevamiento. Complementa `01-tp-final-plan.md`.
> Datos generados con los scripts de `scripts/` y persistidos en `data/`.
> Fecha de referencia: **2026-11-20**.

## 0. Resumen ejecutivo

- **174 bases de datos** con documentos en el índice de metadatos; **9.859 indicadores** y 12.601 documentos totales.
- La temática se organiza en **3 niveles**: `L0` (WB Practice Groups: Prosperity, People, Planet, Infrastructure, Digital), `L1` (26 temas) y `L2` (129 subtemas).
- **95% de los indicadores son anuales**. Solo **36 indicadores son subanuales** (33 mensuales, 3 trimestrales) y **no hay series semanales ni diarias**.
- Cobertura mediana: **141 economías** por indicador; 88 bases tienen mediana ≥150.
- **Frescura**: 44% de las bases con datos de sonda llegan a 2024 o después; 20% a 2025-2026.
- Para el foco **datacenter/connectivity/energy/infrastructure** hay fuentes sólidas, pero el conteo de datacenters (`PEERING_DB`) es un **snapshot único de 2023**.

## 1. Cómo se exploró (reproducible)

### 1.1 Endpoints usados

| Método | Endpoint | Uso |
|---|---|---|
| POST | `/data360/metadata` | Metadatos masivos tipo OData (`$filter`, `$select`, `$top`, `$skip`, `$orderby`) |
| GET | `/data360/indicators?datasetId=…` | IDs de indicadores de una base |
| GET | `/data360/disaggregation?datasetId=…&indicatorId=…` | Dimensiones y períodos disponibles |
| GET | `/data360/data?DATABASE_ID=…&INDICATOR=…` | Observaciones (con `REF_AREA`, `timePeriodFrom/To`, `skip`) |
| POST | `/data360/searchv2` | Búsqueda vectorial |
| GET | `/data360/portal/v1/hierarchy?type=country` | Jerarquía país → región / ingreso |

Especificación OpenAPI: `https://raw.githubusercontent.com/worldbank/open-api-specs/refs/heads/main/Data360%20Open_API.json`
Base: `https://data360api.worldbank.org`

> El MCP (`data360-mcp`) se usó para descubrir el catálogo y validar indicadores; la extracción masiva se hizo contra la API REST porque el MCP está pensado para consultas interactivas. Esto cubre el **bonus track MCP**.

### 1.2 Scripts y salidas

| Script | Qué hace | Salidas |
|---|---|---|
| `scripts/explore_api.py` | Baja metadatos de los 9.859 indicadores paginando de a 1000 | `data/raw/data360_indicators.jsonl.gz`, `database_summary.csv`, `indicators.csv`, `topic_summary.csv`, `database_topics.csv`, `freshness_summary.csv`, `region_summary.csv` |
| `scripts/check_freshness.py` | Verifica la **última observación real** (no nominal) de series granulares y de hasta 2 indicadores por base | `granular_freshness.csv`, `database_actual_freshness.csv` |
| `scripts/region_coverage.py` | Calcula cobertura por región desde `ref_country` | `database_region_coverage.csv`, `region_overall.csv` |
| *(inline)* | Conteo de documentos por base y tipo | `database_doc_counts.csv` |

Todas las tablas quedan en `data/derived/`. Los scripts usan `requests` (declarado en `pyproject.toml`).

## 2. Bases de datos: panorama

### 2.1 Volumen por tipo de documento

| Tipo | Documentos |
|---|---:|
| indicator | 9.859 |
| analytics | 2.151 |
| document | 198 |
| dataset | 174 |
| insights-resources | 89 |
| country factsheets | 85 |
| global report | 45 |
| **Total** | **12.601** |

### 2.2 Categorías de alto nivel (L0)

| Categoría (WB Practice Group) | Indicadores | Bases |
|---|---:|---:|
| Prosperity | 4.551 | 70 |
| People | 832 | 17 |
| Planet | 291 | 33 |
| Infrastructure | 291 | 44 |
| Digital | 141 | 17 |

> El índice tiene además una fila duplicada de `Digital` con 1 indicador por inconsistencia de vocabulario.

### 2.3 Temas (L1) — los 26

| Tema L1 | Indicadores | Bases |
|---|---:|---:|
| Economic Policy | 2.201 | 22 |
| Trade, Investment and Competitiveness | 1.015 | 22 |
| Finance | 948 | 14 |
| Institutions | 774 | 21 |
| Gender | 400 | 11 |
| Education | 211 | 6 |
| Health, Nutrition & Population | 209 | 9 |
| Urban, Resilience and Land | 120 | 27 |
| Water | 103 | 4 |
| Energy & Extractives | 83 | 15 |
| Agriculture and Food | 83 | 16 |
| Poverty | 77 | 6 |
| Climate Change | 76 | 6 |
| Transport | 70 | 13 |
| **Connectivity** | **57** | **5** |
| **Digital Services** | **33** | **6** |
| **Cybersecurity** | **26** | **1** |
| Social Protection | 26 | 3 |
| Environment | 23 | 9 |
| **Global Infrastructure Finance** | **23** | **8** |
| **Digital Industry and Jobs** | **20** | **5** |
| Growth and Jobs | 20 | 4 |
| AgriConnect | 6 | 2 |
| Artificial Intelligence | 5 | 3 |
| Financial Sector Development | 4 | 1 |
| **Data Infrastructure** | **3** | **2** |

### 2.4 Subtemas (L2) — 129 en total, top 15

| Subtema L2 | Indicadores | Bases |
|---|---:|---:|
| Macro-financial Policies | 1.559 | 13 |
| Investment and Business Climate | 629 | 10 |
| Financial Stability and Integrity | 617 | 3 |
| Fiscal Policy | 462 | 11 |
| Economic and Sociopolitical Governance | 337 | 15 |
| Public Institutions | 332 | 16 |
| Financial Inclusion, Infrastructure and Access | 309 | 4 |
| Markets, Competition, and Technology | 272 | 10 |
| Growth and Jobs | 175 | 11 |
| Public Finance Management | 107 | 10 |
| Schooling | 101 | 1 |
| Assets | 95 | 3 |
| Housing | 66 | 19 |
| Education | 60 | 4 |
| Inequality and Shared Prosperity | 59 | 3 |

> Catálogo completo por base: `data/derived/database_summary.csv` y `database_topics.csv`.

### 2.5 Bases más grandes (por cantidad de indicadores)

| Base | Ind. | Cobertura mediana | Span nominal | Temas L1 principales |
|---|---:|---:|---|---|
| WB_WDI | 1.545 | 183 | 1960–2025 | Education, Economic Policy, Gender |
| IMF_BOP | 1.146 | 50 | 1948–2024 | Economic Policy |
| WB_EDSTATS | 1.072 | 96 | 1970–2023 | Education, Gender |
| WB_ES | 584 | 180 | 2006–2025 | Trade/Investment, Transport, Digital Services |
| IMF_IFS | 495 | 23 | 1940–2024 | Finance, Economic Policy |
| WB_GS | 363 | 217 | 1960–2023 | Gender |
| WB_FINDEX | 280 | 90 | 2011–2024 | Finance, Digital Services |
| IMF_GFS_SOO | 218 | 151 | 2017–2025 | Economic Policy |
| BS_SGI | 193 | 41 | 2014–2024 | Institutions |
| WB_HNP | 192 | 217 | 1960–2023 | Health, Nutrition & Population |

## 3. Indicadores: panorama

### 3.1 Periodicidad

| Periodicidad | Indicadores |
|---|---:|
| Annual | 9.396 |
| Triennial | 296 |
| Unknown | 99 |
| Monthly | 33 |
| Five-Year Interval | 12 |
| Biennial | 10 |
| Every two years | 5 |
| Ad hoc | 4 |
| Quarterly | 3 |
| Other | 1 |

### 3.2 Cobertura (economías por indicador, vía `ref_country`)

- n = 9.859 · mínimo 0 · **mediana 141** · máximo 253.
- 12 indicadores con 0 economías en metadatos.
- 88 bases con mediana ≥150 economías.

### 3.3 Estructura de una observación

Campos núcleo del endpoint de datos:

| Campo | Ejemplo | Uso |
|---|---|---|
| `REF_AREA` | `BRA`, `USA`, `SAS` | País **o agregado regional** |
| `TIME_PERIOD` | `2023`, `2025-Q2`, `2026-03` | Período |
| `OBS_VALUE` | `84.15` | Valor |
| `UNIT_MEASURE` | `PT_POP`, `DC`, `KBPS` | Unidad |
| `OBS_STATUS` | `A` | Estado (no distingue proyección) |
| `LATEST_DATA` | `true/false` | Marca el último dato de la serie |
| `SEX` / `AGE` / `URBANISATION` | `_T`, `Y15T24`, `URB` | Desagregaciones opcionales |

Metadatos (`series_description`): `topics`, `periodicity`, `time_periods`, `ref_country`, `measurement_unit`, `methodology`, `limitation`, `sources_note`, etc.

## 4. Completitud

### 4.1 Cobertura por región (promedio entre bases)

Calculada mapeando `ref_country` a la jerarquía país→región del Banco Mundial.

| Región | Países | Bases | Cobertura media | Bases >50% |
|---|---:|---:|---:|---:|
| South Asia (SAS) | 6 | 171 | 0,692 | 128 |
| Western & Central Africa (AFW) | 22 | 171 | 0,671 | 126 |
| Sub-Saharan Africa (SSF) | 48 | 171 | 0,670 | 123 |
| Eastern & Southern Africa (AFE) | 26 | 171 | 0,670 | 124 |
| Europe & Central Asia (ECS) | 58 | 171 | 0,639 | 129 |
| Middle East, N. Africa, Afghanistan & Pakistan (MEA) | 23 | 171 | 0,634 | 113 |
| North America (NAC) | 3 | 171 | 0,557 | 115 |
| East Asia & Pacific (EAS) | 38 | 171 | 0,530 | 94 |
| Latin America & Caribbean (LCN) | 44 | 171 | 0,528 | 100 |

> `AFE` + `AFW` se solapan con `SSF`; la jerarquía del portal las trata como subregiones.

### 4.2 Advertencia

`ref_country` es **cobertura nominal declarada**, no densidad real de observaciones. Para completitud efectiva hay que consultar el endpoint de datos por indicador. Para el TP alcanza con declararlo como "cobertura de metadatos".

## 5. Frescura / actualidad

### 5.1 El problema: nominal ≠ real

`series_description.time_periods.end` es **nominal e incluye proyecciones**:

- `IMF_WEO` declara series hasta **2031** (proyecciones).
- `UNCTAD_DE` declara fin 2023, pero **tiene datos reales hasta 2025**.
- `date_last_update` está **vacío en los 9.859 indicadores**.

Por eso se hizo una verificación empírica contra `/data360/data`.

### 5.2 Fin nominal declarado (todos los indicadores)

| Año fin nominal | Indicadores |
|---|---:|
| 2026 | 1.010 |
| 2025 | 1.209 |
| 2024 | 3.203 |
| 2023 | 1.767 |
| 2022 | 583 |
| 2021 | 220 |
| 2020 | 349 |
| 2019 | 644 |
| 2018 | 193 |
| 2017 | 241 |
| > 2026 (proyección) | 159 |

### 5.3 Último dato real por base (sonda representativa)

Se consultó 1–2 indicadores por base (mayor cobertura) y un país con datos. **158 bases** respondieron.

| Último año real | Bases |
|---|---:|
| 2026 | 10 |
| 2025 | 22 |
| 2024 | 37 |
| 2023 | 29 |
| 2022 | 12 |
| 2021 | 16 |
| 2020 | 9 |
| 2019 | 5 |
| 2018 | 6 |
| 2017 | 2 |
| 2016 | 3 |
| 2014 | 5 |
| 2013 | 2 |

Lectura: **44% de las bases llega a 2024+**, **20% a 2025-2026**, **62% a 2023+**.
Es una **cota inferior**: la sonda usa un solo indicador/país, no el máximo global.

### 5.4 Series subanuales (último mes / trimestre real)

Solo **36 indicadores** en 6 bases. No hay series semanales ni diarias.

| Base | Periodicidad | Ind. | Fin nominal | Último real |
|---|---|---:|---|---|
| FAO_CP | Monthly | 3 | 2026-03 | **2026-03** |
| IPC_IPC | Monthly | 2 | 2025-11 | **2025-08** |
| OECD_AHD | Quarterly | 1 | 2025-Q2 | **2025-Q1** |
| UNCTAD_LSC | Quarterly | 1 | 2024-Q1 | **2024-Q1** |
| IMF_GHW | Quarterly | 1 | 2021-Q4¹ | **2021-Q4** |
| WB_BPS | Monthly | 28 | 2021-12 | **2021-06** |

¹ El metadato venía corrupto (`20214`); se normalizó a 2021-Q4.

Detalle: `data/derived/granular_freshness.csv`.

## 6. Foco temático: digital, conectividad, energía, infraestructura

### 6.1 Bases candidatas

| Base | Ind. | Cob. mediana | Span nominal | Último real | Temas |
|---|---:|---:|---|---:|---|
| ITU_DH | 39 | 189 | 2000–2025 | 2022* | Trade/Investment, **Connectivity** |
| ITU_GCI | 26 | 194 | 2020–2024 | 2024 | **Cybersecurity** |
| UNCTAD_DE | 14 | 60 | 2010–2023 | 2025 | **Connectivity**, Digital Industry |
| WB_GTMI | 64 | 198 | 2022–2025 | 2022 | Institutions, Digital Services, AI |
| ITU_ICT | 10 | 194 | 2007–2023 | 2022 | **Connectivity** |
| PCH_IXP | 2 | 156 | 2024 | 2024 | Data Infrastructure |
| PEERING_DB | 1 | 158 | 2023 | 2023 | Data Infrastructure, AI |
| OOKLA_ST | 2 | 242 | 2019–2024 | 2024 | Velocidad de internet |
| WB_WDI | 1.545 | 183 | 1960–2025 | 2024 | Internet, energía, infraestructura |
| WB_ES | 584 | 180 | 2006–2025 | — | Digital Services, Transport |
| OWID_CB | 76 | 207 | 1750–2023 | 2023 | **Energy & Extractives**, Climate |
| WB_RISE | 27 | 140 | 2010–2023 | 2023 | **Energy & Extractives** |
| WB_SE4ALL | 8 | 220 | 1990–2022 | 2021 | **Energy & Extractives** |
| WB_PPI | 5 | 112 | 1990–2024 | 2024 | **Global Infrastructure Finance** |
| WB_BID | 4 | 140 | 2025 | 2025 | **Global Infrastructure Finance** |

\* La sonda de ITU_DH tomó un indicador de menor cobertura; la base declara series hasta 2025.

### 6.2 Triage específico de datacenters

| Indicador | ID | Cobertura | Años | Limitación |
|---|---|---|---:|---|
| Nº de datacenters conectados | `PEERING_DB_CONN_DATA_CENT` | 158 | **solo 2023** | Sin serie temporal |
| Nº de IXPs | `PCH_IXP_NUM` | 156 | 2024 | Un año |
| Participantes medianos por IXP | `PCH_IXP_PARTICIPANTS` | 156 | 2024 | Un año |
| Velocidad móvil | `OOKLA_ST_MOB_PER` | 240 | 2019–2024 | kbps |
| Velocidad fija | `OOKLA_ST_FIX_PER` | 244 | 2019–2024 | kbps |

**Consecuencia para el TP:** no se puede hacer una serie temporal de datacenters con Data360. El ángulo viable es **comparación entre países (2023) + cruce con conectividad/energía** que sí tienen serie.

## 7. Gotchas de la API

1. **Paginación inestable sin `$orderby`**: `$skip` sobre el índice de búsqueda puede duplicar/omitir documentos (en una prueba se obtuvieron 230 duplicados y 169 bases en vez de 171). Usar `$orderby=series_description/database_id asc,series_description/idno asc` y deduplicar por `(database_id, idno)`.
2. `$top` máximo 1000 por request; **no usar `$count=true`** (devuelve HTTP 417). El total viene en `@odata.count`.
3. `tags` es campo de primer nivel; `topics`, `time_periods`, `ref_country` están dentro de `series_description`.
4. `REGION`/agregados aparecen mezclados con países en `REF_AREA`: filtrar a ISO3 reales.
5. `date_last_update` vacío en todos los indicadores.
6. `time_periods.end` incluye proyecciones (WEO 2031) y a veces subestima (UNCTAD 2023 vs real 2025).
7. `OBS_STATUS = A` no distingue valores proyectados.
8. Cobertura y periodicidad varían mucho entre bases: validar antes de prometer un gráfico.
9. Algunos metadatos vienen corruptos (`20214` en IMF_GHW).

## 8. Visualizaciones sugeridas para la exploración de la API

Estas visualizaciones son **sobre el catálogo** (meta-visualización), no sobre el tema periodístico. Sirven como dashboard de exploración / anexo.

| # | Visualización | Codificación | Fuente | Para qué |
|---|---|---|---|---|
| 1 | **Treemap jerárquico** L0 → L1 → L2 | área = indicadores | `topic_summary.csv` | Mostrar la estructura temática completa de un vistazo |
| 2 | **Barras horizontales top-N** bases por indicadores, color = tema dominante | x = indicadores, y = base, color = L1 | `database_summary.csv` | Identificar las bases más ricas |
| 3 | **Heatmap base × región** | color = cobertura media | `database_region_coverage.csv` | Detectar vacíos regionales por base |
| 4 | **Dumbbell / lollipop** fin nominal vs último real | par de puntos por base | `database_actual_freshness.csv` | Evidenciar proyecciones y desactualización |
| 5 | **Barras apiladas** periodicidad por base (o overall) | conteo por periodicidad | `indicators.csv` | Mostrar que casi todo es anual |
| 6 | **Scatter** indicadores vs cobertura mediana | x = ind., y = cobertura, tamaño = bases | `database_summary.csv` | Amplitud vs profundidad |

## 9. Herramienta recomendada

**Python + Altair en Colab**, con este esquema:

- La extracción está en Python (`scripts/`), usando `requests`.
- El notebook lee los CSV de `data/derived/` (no vuelve a golpear la API).
- Altair genera Vega-Lite interactivo (tooltips, filtros, selección cruzada) y exporta HTML/spec.
- Si luego se quiere publicar, los specs Vega-Lite se reutilizan en Observable sin reescribir los datos.

**Observable puro** exigiría reimplementar la descarga/paginación en JS; no conviene para esta etapa.

## 10. Próximos pasos

1. Elegir el recorte definitivo (países, años, tema).
2. Pasar de la meta-exploración a las **3 visualizaciones periodísticas**.
3. Validar los indicadores elegidos con `get_disaggregation` + `get_data` (datos reales, no metadata).
4. Fijar la narrativa y las notas de fuente.
