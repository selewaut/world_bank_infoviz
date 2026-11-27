# Historia periodística — Energía, desarrollo y datacenters

> Plan de análisis del Paso 2. Complementa [`01-tp-final-plan.md`](01-tp-final-plan.md).
> Indicadores validados con el MCP Data360 el **2026-11-27**.
> El enunciado pide **hasta 3 visualizaciones**. Este documento arma un arco de **5** (3 núcleo + 2 de apoyo).

## Metadata

| Campo | Valor |
|---|---|
| Ángulo | Dónde se instala la nube, qué tan intensa en energía es la economía, con qué matriz se genera, y quién exporta el petróleo/gas |
| Formato | Nota / artículo de datos (lede → mapa → cruce → matriz → cierre) |
| Herramienta | Python + Altair (Vega-Lite), notebook de análisis |
| MCP | `data360` (`search_indicators`, `get_disaggregation`, `get_data`, `rank_countries`, `compare_countries`, `get_metadata`) |
| Estado | Plan de historia; datos de viz todavía no extraídos en lote |

---

## 1. Historia global

### Lede

La infraestructura digital no flota en la nube: se enchufa a una red eléctrica. En 2023, PeeringDB registró **1.377 datacenters conectados en Estados Unidos**, más que los cuatro países siguientes juntos. El ranking no es solo un mapa de riqueza: Brasil (347), India (235) e Indonesia (198) aparecen entre los diez primeros. Lo que sí comparte el club es otra cosa: una red capaz de entregar electricidad a escala.

### Nut graf

Este artículo cruza cuatro capas de Data360:

1. **Dónde está la infraestructura digital** — datacenters conectados (`PEERING_DB`, 2023).
2. **Desarrollo y demografía** — PIB per cápita PPA, población y crecimiento poblacional (`WB_WDI`).
3. **Electricidad e intensidad energética** — kWh/persona y MJ por dólar de PIB, series tipo IEA/SDG 7.3.1 (`WB_WDI`).
4. **Hidrocarburos** — matriz eléctrica (carbón/gas/petróleo/nuclear/hidro) y dependencia exportadora de combustibles (`TX_VAL_FUEL_ZS_UN`, rentas de petróleo/gas).

La pregunta para el lector: **¿la próxima ola de cómputo aterriza en economías eficientes y redes limpias, o en los mismos países que venden (o queman) petróleo y gas?**

### Mensaje en una frase

Los datacenters siguen al ingreso y a la electricidad; la intensidad energética y el mix fósil son ejes aparte — y los grandes exportadores de fuel no son, en general, los grandes hubs de interconexión.

### Por qué es relevante ahora

El boom de IA reabrió el debate sobre demanda eléctrica de datacenters. Data360 no mide el consumo de cada sala, pero sí permite ubicar **dónde está el hardware de interconexión** y **sobre qué mix eléctrico se apoya el país**. Eso alcanza para una nota: geografía del cómputo vs. geografía de la energía.

---

## 2. Recorte

| Dimensión | Decisión |
|---|---|
| Geografía | Global a nivel país (ISO3). Color por **región WB** (`EAS`, `ECS`, `LCN`, `NAC`, `SAS`, `MEA`, `SSF`). Argentina siempre anotada como ancla local. |
| Tiempo | **Corte 2023** para PeeringDB, PIB, población, kWh y matriz. Intensidad energética: **2022** (último año WDI). Rentas petróleo/gas: **2021**. |
| Unidad de análisis | País. Filtrar agregados regionales (`AFE`, `WLD`, `EUU`, …) de `REF_AREA`. |
| Incluye | Datacenters, PIB PPA, población y crecimiento, kWh/persona, intensidad energética, % generación por fuente, fuel exports % y rentas oil/gas. |
| Excluye | Ookla, IXPs como viz principal, RISE, acceso a electricidad, Brent/WTI (no están en Data360), producción cruda IFS (solo 13 países). |

### IEA vs EIA (importante)

Data360 **no tiene un dataset IEA propio**. Lo “IEA” usable es WDI:

- Matriz eléctrica `EG_ELC_*_ZS` — metodología IEA.
- Intensidad energética `EG_EGY_PRIM_PP_KD` — oferta primaria / PIB PPA (SDG 7.3.1, IEA/UNSD).
- kWh per cápita `EG_USE_ELEC_KH_PC` — generación neta / población.

`EIA_EIAOD` es la **EIA de EE.UU.**, no IEA: GWh de hidro, gas, petróleo, geotérmica y biomasa (1980–2022), **sin carbón ni nuclear ni solar/eólica**. No alcanza para una matriz.

**Precios de petróleo/gas:** no hay Brent ni Henry Hub. El proxy de país es `IMF_PCTOT` (índice de precios de commodities de exportación, mensual hasta 2024-06). El proxy de surtidor es `WEF_TTDI_FUELPRICE` (US$/litro, ~119 economías). Ninguno es el precio spot mundial; no merecen una viz núcleo.

---

## 3. Indicadores ancla (verificados MCP)

| Rol | Base | Indicador | Unidad | Años reales | Cobertura |
|---|---|---|---|---|---|
| Datacenters | `PEERING_DB` | `PEERING_DB_CONN_DATA_CENT` | DC | **solo 2023** | 158 economías |
| PIB | `WB_WDI` | `WB_WDI_NY_GDP_PCAP_PP_KD` | PPA 2021 int$ | 1990–2024 | ~199 |
| Población | `WB_WDI` | `WB_WDI_SP_POP_TOTL` | personas | 1960–2025 | amplia |
| Electricidad | `WB_WDI` | `WB_WDI_EG_USE_ELEC_KH_PC` | kWh/persona | 1990–2024 | ~150 |
| Carbón % | `WB_WDI` | `WB_WDI_EG_ELC_COAL_ZS` | % generación | 1990–2024 | ~209 |
| Gas % | `WB_WDI` | `WB_WDI_EG_ELC_NGAS_ZS` | % | 1990–2024 | ~209 |
| Petróleo % | `WB_WDI` | `WB_WDI_EG_ELC_PETR_ZS` | % | 1990–2024 | ~209 |
| Nuclear % | `WB_WDI` | `WB_WDI_EG_ELC_NUCL_ZS` | % | 1990–2024 | ~209 |
| Hidro % | `WB_WDI` | `WB_WDI_EG_ELC_HYRO_ZS` | % | 1990–2024 | ~209 |
| Renovables excl. hidro | `WB_WDI` | `WB_WDI_EG_ELC_RNWX_ZS` | % | 1990–**2021** | ~209 |
| Renovables consumo | `WB_WDI` | `WB_WDI_EG_FEC_RNEW_ZS` | % TFEC | 1990–2022 | ~212 |
| Intensidad energética | `WB_WDI` | `WB_WDI_EG_EGY_PRIM_PP_KD` | MJ / $2021 PPA PIB | 2000–**2022** | ~201 |
| Crecimiento poblacional | `WB_WDI` | `WB_WDI_SP_POP_GROW` | % anual | 1961–2025 | amplia |
| Bandwidth internacional (uso) | `ITU_DH` | `INT_CONN_BAND` | Mbit/s | 2000–2024 | ~224 |
| Bandwidth lit/equipped | `ITU_DH` | `INT_CONN_BAND_PS` | Mbit/s | 2006–2024 | ~165 |
| Usuarios de internet | `ITU_DH` / `WB_WDI` | `IT_NET_USER` / `IT_NET_USER_ZS` | % población | 2000–2025 | amplia |
| Fuel exports | `WB_WDI` | `WB_WDI_TX_VAL_FUEL_ZS_UN` | % exportaciones mercadería | 1962–2024 | ~197 |
| Fuel imports | `WB_WDI` | `WB_WDI_TM_VAL_FUEL_ZS_UN` | % importaciones | 1962–2024 | ~197 |
| Rentas petróleo | `WB_WDI` | `WB_WDI_NY_GDP_PETR_RT_ZS` | % PIB | 1970–**2021** | ~200 |
| Rentas gas | `WB_WDI` | `WB_WDI_NY_GDP_NGAS_RT_ZS` | % PIB | 1970–**2021** | ~201 |
| Precio commodities (proxy) | `IMF_PCTOT` | `IMF_PCTOT_X` | índice | 1962–2024-06 | 180; mensual |
| Capacidad renovable | `WB_SE4ALL` | `WB_SE4ALL_EG_EGEN_RNEW` | W/persona | 2000–2022 | 226; solar/eólica/hidro/bio/geo |

**No usar como viz principal**

| Tema pedido | Qué hay | Por qué no entra al núcleo |
|---|---|---|
| Precio Brent/gas spot | No existe en Data360 | PCTOT es país-específico (canasta de exportación), no el crudo mundial |
| Producción de crudo (barriles) | `IMF_IFS_AOMPC` | Solo **13** `REF_AREA`; insuficiente para mapa |
| Producción EIA de petróleo | `EIA_EIAOD_GOGWH` | Es **generación eléctrica** a partir de petróleo (GWh), no producción de crudo |

**Derivados a calcular en el notebook**

- `dc_per_million` = datacenters / (población / 1e6)
- `other_elc_pct` = 100 − (carbón + gas + petróleo + nuclear + hidro), año 2023 (el residual cubre eólica/solar/biomasa cuando `RNWX` no llega a 2023)
- `hydrocarbon_rents_gdp` = oil rents + gas rents (2021)
- Join país → región WB con la jerarquía ya usada en `scripts/region_coverage.py`

### Hechos que ya sostienen el lede (MCP, 2023)

**Datacenters conectados:** USA 1.377 · BRA 347 · DEU 330 · GBR 246 · IND 235 · FRA 221 · IDN 198 · CAN/NLD 162 · AUS 161. Argentina 69, Chile 52, China **41** (sesgo PeeringDB; ver caveats).

**kWh/persona:** CAN 14.508 · USA 12.711 · FRA 6.396 · NLD 6.206 · DEU 6.079 · GBR 4.229 · BRA 2.916 · ARG 2.822 · IDN 1.481 · IND 1.160.

**PIB PPA/persona:** USA 74.352 · NLD 70.199 · DEU 63.140 · … · ARG 27.230 · BRA 19.080 · IDN 13.890 · IND 8.871.

**Matriz 2023 (puntos de giro):**

| País | Carbón | Gas | Hidro | Nuclear |
|---|---:|---:|---:|---:|
| India | 74% | 3% | 7% | 2% |
| Indonesia | 70% | 13% | 6% | — |
| Alemania | 26% | 16% | 5% | 1% |
| EE.UU. | 17% | 42% | 6% | 18% |
| Argentina | 1% | 46% | 27% | 6% |
| Brasil | 2% | 5% | **60%** | 2% |
| Canadá | 4% | 16% | **57%** | 14% |
| Francia | 0,5% | 6% | 11% | **64%** |

**Intensidad energética (MJ / $ PPA PIB):** CAN 6,4 (2022) · NGA 6,6 (2021) · CHN 6,3 (2021) · SAU 5,8 (2021) · USA 4,2 · IND 4,2 (2021) · BRA 3,9 · ARG 3,3 · FRA 2,8 · DEU 2,5. Alemania produce más con menos energía por dólar; Canadá y Nigeria son intensivos.

**Fuel exports % de mercadería (2023):** NGA 92 · QAT 87 · SAU 81 · NOR 68 · CAN 25 · IDN 23 · USA 19 · ARG 9 · DEU 2. Los petroestados casi no aparecen en el top de PeeringDB (Noruega 49 DC; Nigeria 18; Arabia no está en el top 15).

**Crecimiento poblacional 2023 (%):** CAN 2,8 · NGA 2,1 · IND 0,9 · USA 0,8 · ARG 0,3 · DEU 0,1 · JPN −0,5. Entra en tooltips y en el texto (densidad digital vs demografía), no como viz propia.

---

## 3b. Mapa de temas pedidos → lugar en la nota

| Tema | Rol | Dónde vive |
|---|---|---|
| Energy / matriz IEA | Núcleo | V3 barras apiladas |
| Data center connections | Núcleo | V1 coropleta |
| GDP per capita | Núcleo | V2 eje x |
| Energy intensity | Núcleo de apoyo | **V4** coropleta (o color en V2 si hay que recortar) |
| Oil/gas exports | Núcleo de apoyo | **V5** coropleta fuel exports; rentas oil+gas en tooltip |
| Population / growth | Contexto | Denominador de V2 (`dc_per_million`); `SP_POP_GROW` en tooltip, no chart |
| Electricity intensive (kWh/persona) | Contexto | Tamaño en V2; V4 si se prefiere kWh en vez de intensidad |
| Oil/gas prices | Fuera del núcleo | Pie de nota + anexo PCTOT si hace falta un gráfico de términos de intercambio |
| Conectividad ITU (`ITU_DH`) | **Fijo en V1/V2** | V1: toggle fill DC vs `INT_CONN_BAND`. V2: tooltip `% internet` + bandwidth |
| IA (`OECD_AI`, `IMF_AI`) | Fuera del arco | Una cifra en el lede/cierre si hace falta; no chart |

### Presupuesto de dimensiones (no entra un 6.º mapa)

El TP admite **3** viz; el arco de la nota ya tiene **5**. Un sexto choropleta de `ITU_DH` pelea con V1 (misma geografía) y diluye energía.

| Chart | Codificaciones ya usadas | Qué se puede sumar | Qué no |
|---|---|---|---|
| V1 mapa | color = DC **o** ITU bandwidth (toggle) | Tooltip: n DC, DC/millón, `INT_CONN_BAND` | Segundo mapa ITU; toggle extra DC vs /millón (eso ya es el eje y de V2) |
| V2 scatter | x PIB, y DC/millón, size kWh, color región | Tooltip: `% internet` ITU/WDI + bandwidth | Un 5.º canal visual (forma, opacidad, facet) |
| V3 barras | país × fuente % | Nada | — |
| V4 mapa | color = intensidad | Tooltip DC | — |
| V5 mapa | color = fuel exports | Tooltip DC | Reemplazar V5 por bandwidth **solo si** se prefiere digital a hidrocarburos |

`ITU_DH` entra porque es el **caño** (Mbit/s internacionales) del mismo objeto que PeeringDB cuenta como **sala**. Eso es un toggle, no una historia nueva.

No entran como viz: Ookla (velocidad al usuario final), `OECD_AI` papers, `IMF_AI` índice, `EPC_AI` (34 países), `PCH_IXP` (redundante con PeeringDB).

---

## 4. Arco de visualizaciones

Orden de lectura = orden de la nota. Interactividad mínima en todas: tooltip de país, valor y fuente.

### V1 — Mapa: salas vs caños (núcleo, TP)

- **Pregunta:** ¿Dónde están los datacenters conectados, y coinciden con el bandwidth internacional?
- **Tipo:** Una coropleta, **dos fills** (radio / dropdown).
  - Default: `PEERING_DB_CONN_DATA_CENT` 2023 (escala **log**).
  - Toggle: `ITU_DH` `INT_CONN_BAND` 2023 (Mbit/s, también log).
- **Año:** 2023 (inner join; gris = missing de esa capa, no cero).
- **Codificación:** `iso3` → geometría. Misma proyección al cambiar el fill.
- **Tooltip (siempre):** país, región, n DC, DC por millón, bandwidth Mbit/s, fuente de la capa activa.
- **No** segundo toggle “DC vs DC/millón”: esa densidad es el eje y de V2.
- **Texto al pie:** “Estados Unidos concentra más salas listadas que Brasil, Alemania, Reino Unido e India juntos. PeeringDB cuenta **facilities**; ITU cuenta **uso de bandwidth internacional** (Mbit/s). Más caño no implica más salas en el registro.”
- **Por qué esta viz:** geografía de la nube + la capa ITU sin un mapa extra.

### V2 — Scatter: ingreso, electricidad y densidad digital (núcleo, TP)

- **Pregunta:** ¿Los datacenters siguen al desarrollo económico y a la electricidad per cápita?
- **Tipo:** Scatter.
  - **x** = PIB per cápita PPA (`NY_GDP_PCAP_PP_KD`)
  - **y** = datacenters **por millón de habitantes** (no el conteo crudo: si no, India/Indonesia ganan por tamaño)
  - **tamaño** = kWh per cápita
  - **color** = región WB
- **Año:** 2023 (inner join PeeringDB + WDI + ITU; si falta ITU, el punto se dibuja igual y el tooltip dice “s/d”).
- **Interactividad:** tooltip **fijo** con PIB, DC, DC/millón, kWh, crecimiento poblacional, **`IT_NET_USER` / `IT_NET_USER_ZS` (% internet)**, **`INT_CONN_BAND` (Mbit/s)**, región. Brush por región; labels en USA, NLD, SGP, BRA, IND, ARG, IRL.
- **ITU no es canal visual** (ni tamaño ni color): V2 ya tiene cuatro. Conectividad va al hover.
- **Hipótesis visual:** nube de países ricos y electrificados arriba-derecha; India/Indonesia abajo (mucho conteo absoluto, poca densidad); Países Bajos / Irlanda / Singapur como outliers de densidad.
- **Texto al pie:** “Un país puede tener muchas salas porque es grande (India) o porque es un hub (Países Bajos). El eje vertical es densidad. El hover muestra usuarios de internet y bandwidth ITU: el caño y el uso, no solo el rack.”

### V3 — Matriz eléctrica de los hubs (núcleo, TP)

- **Pregunta:** ¿Sobre qué mix se apoyan los países con más datacenters?
- **Tipo:** Barras apiladas horizontales (100%), un país por fila.
- **Universo:** top 10 de V1 + **Argentina** + **Francia** (contraste nuclear) + **China** (con nota de cobertura).
- **Series 2023 (WDI/IEA):** carbón, gas, petróleo, nuclear, hidro, residual (eólica/solar/otras).
- **Orden de filas:** el mismo ranking de datacenters, para que el lector cruce V1 y V3 sin reordenar.
- **Paleta:** fósiles en tierra/gris, nuclear en violeta, hidro en azul, residual renovable en verde. **Nunca** arcoíris.
- **Interactividad:** hover del tramo; opcional highlight de una fuente.
- **Texto al pie:** “Brasil y Canadá enchufan la nube a redes hidroeléctricas. India e Indonesia, a carbón (~70%). EE.UU. es gas + nuclear. Francia es el extremo nuclear. La ubicación digital no elige sola la matriz limpia.”

### V4 — Mapa: intensidad energética (apoyo, entra al arco de 5)

- **Pregunta:** ¿Las economías que hospedan datacenters son eficientes en energía por dólar de PIB, o intensivas?
- **Tipo:** Coropleta, misma proyección que V1.
- **Indicador:** `WB_WDI_EG_EGY_PRIM_PP_KD` (MJ por $2021 PPA de PIB), **2022** (2021 si falta el país). Más alto = más energía por unidad de producto (peor eficiencia agregada).
- **Escala:** continua, invertir lectura en el pie (“más oscuro = más intensivo”).
- **Función narrativa:** el kWh/persona de V2 mide *cuánta* electricidad hay por habitante; esto mide *cuánta energía pide cada dólar de PIB*. Canadá y EE.UU. son a la vez hubs digitales e intensivos; Alemania es hub y eficiente; Nigeria es intensiva y casi sin salas PeeringDB.
- **Si hay que recortar a 3 viz:** recodificar V2: color = intensidad (en vez de región) y dejar región para el tooltip.

### V5 — Mapa: quién exporta el fuel (apoyo, entra al arco de 5)

- **Pregunta:** ¿Los países que venden petróleo y gas son los mismos que hospedan la nube?
- **Tipo:** Coropleta de `WB_WDI_TX_VAL_FUEL_ZS_UN` (2023), misma proyección que V1. Tooltip: fuel exports %, oil rents, gas rents, n° de DC.
- **Contraste visual:** el mapa de V1 (salas) vs este mapa (petroestados). Nigeria/Qatar/Arabia ~80–90% fuel exports y casi no figuran en PeeringDB; Alemania 2% fuel exports y 330 salas.
- **No es producción en barriles.** Data360 no tiene un censo global de crude output usable (IFS = 13 países). Rentas `% PIB` (2021) y fuel exports `%` son el proxy correcto de “economía de hidrocarburos”.
- **Precios:** no chart. Una frase en el pie: los precios spot no están en Data360; el shock de 2022 se lee, si se quiere, en `IMF_PCTOT_X` para exportadores (NOR, SAU, NGA, ARG) como anexo.
- **Si hay que recortar a 3 viz:** V5 es la última en caer; el contraste petroestado vs hub se puede decir en texto bajo V3.
- **Swap (no extra):** si se prefiere conectividad a hidrocarburos, V5 pasa a ser el choropleta de `INT_CONN_BAND` y fuel exports queda en el pie. No las dos.

---

## 5. Qué entregar en el TP (3 de 5)

El enunciado limita a **3**. Núcleo:

| Entrega | Viz | Rol en la nota |
|---|---|---|
| 1 | V1 coropleta datacenters | Dónde |
| 2 | V2 scatter ingreso × densidad digital | Por qué ahí (desarrollo + energía) |
| 3 | V3 barras apiladas de matriz | Con qué electricidad |

V4 (intensidad) y V5 (fuel exports) son el arco completo de 5. Si el TP se queda en 3, viven en el notebook como anexo. Preferir **V4 sobre V5** si solo entra una más: cierra el hilo IEA (intensidad + matriz + kWh).

---

## 6. Conclusión que la nota puede afirmar (y la que no)

### Afirmar (soportado por los datos)

- La infraestructura de interconexión está **muy concentrada**: un país (USA) y un puñado de hubs europeos y emergentes.
- El conteo absoluto y la **densidad por habitante** cuentan historias distintas. Brasil e India son grandes mercados (y siguen creciendo); Países Bajos y Nordics/Singapur son densos.
- Los hubs no comparten matriz: **hidro (BRA, CAN)**, **gas (USA, ARG)**, **carbón (IND, IDN)**, **nuclear (FRA)**.
- **Intensidad energética** no copia el mapa digital: Alemania es eficiente y hub; Canadá es intensivo y hub; Nigeria es intensiva y casi no tiene salas listadas.
- **Exportar fuel no es hospedar cómputo.** Nigeria, Qatar y Arabia dependen de combustibles en el 80–90% de sus exportaciones y no están en el club PeeringDB; Alemania exporta 2% fuel y tiene 330 salas.
- América Latina llega con ventaja de matriz (hidro) y desventaja de kWh per cápita frente a Norteamérica. Argentina: gas en la matriz (~46%), fuel exports modestos (~9%), 69 DC.
- PeeringDB **subcuenta a China** (41 salas vs. 1.377 en USA): el mapa es el del registro de peering, no el censo de MW.

### No afirmar

- Que los datacenters **causan** el mix o las exportaciones de fuel.
- El consumo en TWh de datacenters: **Data360 no lo publica**.
- Tendencias 2015–2025 de datacenters: un solo año.
- Un precio mundial de petróleo o gas a partir de Data360.
- Que “más renovables ⇒ más datacenters” o “petroestado ⇒ más (o menos) DC” como ley. V5 muestra un contraste, no una causalidad.

### Cierre propuesto (párrafo)

> La nube se instala donde hay mercado, red y capital — no donde se extrae el crudo. El Atlántico Norte y unos emergentes (Brasil, India, Indonesia) concentran las salas; los petroestados concentran las exportaciones de fuel. El costo energético de esa geografía tampoco es uniforme: un servidor en São Paulo nace más hidroeléctrico que uno en Mumbai, y un dólar de PIB alemán pide menos megajoules que uno canadiense. Si la IA fuerza nueva generación, el mapa de PeeringDB es un mapa de **presión sobre redes y balances comerciales distintos**. La pregunta no es si habrá más datacenters, sino **en qué mix se enchufan y cuánta energía pide cada dólar de la economía anfitriona**.

---

## 7. Caveats de datos (llevar al pie de cada viz)

1. **PeeringDB 2023 only.** Comparación entre países, nunca serie. Definición: “active data centers” recuperados en diciembre.
2. **Sesgo de registro.** PeeringDB es voluntario y sesgado a operadores que anuncian peering. China, y en parte otros no-OCDE, quedan chicos. Irlanda (26) queda chica frente a la fama de Dublin: el indicador cuenta **sitios listados**, no MW de hiperescala.
3. **Join 2023.** kWh y matriz WDI cubren ~150–209 países; el scatter usa inner join (se caen islas y algunos LIC). Declararlo.
4. **Residual de la matriz.** `EG_ELC_RNWX_ZS` corta en 2021. En 2023 el tramo “otras” es 100 − suma de carbón/gas/petróleo/nuclear/hidro. Puede incluir solar/eólica **y** desajustes estadísticos.
5. **Agregados regionales.** `REF_AREA` mezcla `EAS`, `SSF`, `WLD`. Filtrar a ISO3 de `ref_country` / jerarquía portal.
6. **IEA revisa series.** Quiebres por cambios políticos/metodológicos (nota de `limitation` en WDI).
7. **Población 2023** para `dc_per_million`; chequear que `SP_POP_TOTL` no use proyección 2025 sin marcar.
8. **Años desfasados.** Intensidad 2022 (a veces 2021); rentas oil/gas 2021; PeeringDB 2023. Declarar el año en cada capa del join.
9. **Fuel exports** es SITC 3 (combustibles minerales), no “solo crudo”. Incluye carbón, gas, derivados.
10. **`IMF_IFS_AOMPC`** no sirve para el mapa: 13 economías.

---

## 8. Implementación

### Extracción

MCP para sondas y metadatos (ya hecho). REST para el lote:

```
GET /data360/data?DATABASE_ID=PEERING_DB&INDICATOR=PEERING_DB_CONN_DATA_CENT
GET /data360/data?DATABASE_ID=WB_WDI&INDICATOR=WB_WDI_NY_GDP_PCAP_PP_KD&timePeriodFrom=2023&timePeriodTo=2023
… igual para SP_POP_TOTL, EG_USE_ELEC_KH_PC, EG_ELC_{COAL,NGAS,PETR,NUCL,HYRO}_ZS
```

Persistir en `data/derived/story/`:

- `datacenters_2023.csv`
- `wdi_cross_2023.csv` (PIB, pop, kWh, mix)
- `se4all_renewable_capacity.csv` (si se hace V5A)
- `country_region.csv` (reusar pipeline de `region_coverage.py`)

### Visual

- Altair + `vega_datasets` world-110m, o GeoJSON Natural Earth, `lookup` por ISO3.
- Proyección: equalEarth o naturalEarth1.
- Export HTML + spec Vega-Lite para posible paso a Observable.
- Una paleta fija en un `theme.py` / dict compartido (regiones WB + fuentes de energía).

### Notebook

`notebooks/03-historia-energia-datacenters.ipynb`

1. Carga y join.
2. Chequeos: n países, missingness, China, top 15.
3. V1–V3 (y V4–V5 si hay tiempo).
4. Bloque de texto de la nota debajo de cada chart (lede, pie, fuente).

---

## 9. Notas de fuente (pie de artículo)

> Datacenters conectados: PeeringDB vía World Bank Data360 (`PEERING_DB_CONN_DATA_CENT`), 2023.  
> PIB per cápita PPA, población, crecimiento, kWh/persona, intensidad energética (SDG 7.3.1) y matriz de generación: World Development Indicators. Matriz e intensidad se apoyan en balances **IEA**.  
> Fuel exports y rentas de petróleo/gas: WDI (UN Comtrade / WB rents).  
> No se usa un precio spot de crudo: Data360 no publica Brent/WTI.  
> Regiones: clasificación del Banco Mundial. Consulta vía API Data360 y MCP `data360`.

---

## 10. Próximos pasos

1. Extraer el lote 2023 a `data/derived/story/` y calcular `dc_per_million` + residual de matriz.
2. Prototipar V1–V3 en el notebook; decidir umbrales de color de la coropleta con los datos reales (no con USA lineal).
3. Redactar pies y el párrafo de cierre con los números del join (no los de esta sonda de 8–15 países).
4. Si el layout da, añadir V4 o V5A.
5. Congelar fuentes y fecha de descarga en el notebook.

---

## Apéndice — Por qué no otras viz tentadoras

| Idea | Por qué no entra al núcleo |
|---|---|
| Serie temporal de datacenters | Un solo año en Data360 |
| Heatmap país × año de kWh | Compite con V2/V4; poco “nota” |
| RISE scores de política | Otro objeto (regulación), diluye energía física |
| Ookla / IXPs | Vuelven al TP a “conectividad”; el cruce pedido es energía × desarrollo × DC |
| EIA GWh apilados | Recorte incompleto (sin carbón/nuclear/solar); WDI % es más limpio |
| Choropleta de % renovable global | El residual 2023 es frágil; mejor V3 en el club de hubs |
| Precio del petróleo (línea mundial) | No hay Brent/WTI; PCTOT es otro objeto (canasta país) |
| Producción de crudo IFS | 13 países |
| Crecimiento poblacional como chart | Ya está en el denominador y el tooltip de V2; un sexto mapa no suma |
