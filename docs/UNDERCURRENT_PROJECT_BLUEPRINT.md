# UNDERCURRENT
## Himalayan Water Intelligence & Glacial Risk Monitoring System
### Complete Project Blueprint
**Ideation • Domains • Scientific Method • Software Architecture • Team Roles • Execution Plan • Evaluation Strategy**

**ASTRA 2026 | Space Hackathon Project Concept**  
**Team Composition:** 3 Computer Science members + 1 Aerospace member  

---

### Project Positioning
A satellite-data-driven geospatial platform connecting upstream glacial-lake change monitoring, downstream exposure screening, and reservoir water-spread monitoring in one basin-oriented decision-support interface.

> [!IMPORTANT]
> **Important:** **Undercurrent** is a prototype for monitoring and preliminary exposure screening. It is **not** an operational GLOF early-warning system, a validated flood forecast, or a substitute for official hydrological and disaster-management authorities.

---

## 1. Executive Summary and Project Identity
* **Project Name:** Undercurrent – Himalayan Water Intelligence & Glacial Risk Monitoring System.
* **Project Type:** Software-first satellite-data and geospatial intelligence prototype.
* **Core Idea:** Integrate satellite observations of glacial lakes and reservoirs with terrain and geographic data to identify water-body changes and screen downstream areas for potential exposure to glacial-lake outburst flood (GLOF) pathways.

### Proposed Problem Statement
Develop an integrated geospatial intelligence platform that utilises satellite imagery, terrain elevation models, and environmental observations to monitor changes in Himalayan glacial lakes and downstream reservoirs, identify unusual water-spread variations, assess potential glacial lake outburst flood (GLOF) exposure, and visualise potentially vulnerable downstream regions to support disaster preparedness and sustainable water-resource management.

### One-Sentence Pitch
**Undercurrent** turns satellite observations into a connected picture of changing Himalayan water bodies and downstream exposure, helping users inspect where conditions may warrant further investigation.

### Core Outputs
* Glacial-lake boundaries and surface-area trends across selected observation dates.
* Reservoir water-spread boundaries and historical surface-area variations.
* DEM-derived elevation, slope, and drainage context.
* Preliminary downstream exposure maps with settlements and infrastructure overlays.
* A web dashboard with source metadata, charts, maps, and transparent limitations.

---

## 2. Ideation: Problem, Users, and Value Proposition

### 2.1 The Problem
Himalayan regions contain glacial lakes, river valleys, settlements, transport links, hydropower infrastructure, and reservoirs. Changes in glacial-lake extent can be relevant to hazard screening, while reservoir water-spread changes can inform water-resource monitoring. These are related aspects of mountain water systems, but they are not interchangeable measurements and must be analysed with appropriate methods.

### 2.2 The Gap Undercurrent Addresses
* Monitoring information can be fragmented across separate satellite images, maps, terrain layers, and water-resource records.
* Users need to compare observations from multiple dates to understand whether a lake or reservoir surface area has changed.
* An observed lake-area change alone does not establish imminent failure; it needs additional context such as terrain, lake setting, dam characteristics, and other evidence.
* Downstream settlements and infrastructure should be spatially considered when screening potential hazard corridors.
* Reservoir water-spread area varies seasonally and is not the same as storage volume.

### 2.3 Target Users and Decisions Supported
| User Group | Potential Decision Supported |
| :--- | :--- |
| **Disaster-Management Planners** | Which downstream settlements or infrastructure intersect a preliminary exposure corridor and may merit closer study? |
| **Water-Resource Departments** | How has a selected reservoir's observed surface area varied across comparable dates or seasons? |
| **Researchers and Students** | How do glacial-lake boundaries and water-spread observations change over time? |
| **Local Authorities and Planners** | Which geographic layers and observations should be reviewed together for a selected basin? |

### 2.4 Value Proposition
Undercurrent provides one place to inspect multi-date water-body observations, view terrain and drainage context, and examine potentially exposed downstream assets. It supports screening and situational understanding; final decisions remain with qualified agencies using validated field and hydrological information.

### 2.5 Innovation Statement
Undercurrent integrates three connected analytical views—glacial-lake change, reservoir water-spread change, and downstream terrain-based exposure—within a single basin-oriented geospatial workflow. Its innovation lies in connected interpretation and traceable data lineage, not simply displaying satellite imagery.

### 2.6 Study-Area Rule
* **Chosen Study Area:** Teesta River Basin, Sikkim Himalaya, India.
* **Glacial Lake:** South Lhonak Glacial Lake (~5,200 m ASL).
* **Reservoirs in Basin:** Teesta-III Chungthang Dam Reservoir (~1,560 m ASL) & Teesta-V Dam (Dikchu, ~650 m ASL).
* **Hydraulic Connection:** Both reservoirs lie directly downstream in the same basin along the Teesta River drainage corridor.

---

## 3. ASTRA Domain Alignment and Boundaries

Undercurrent is designed to remain within the three domains selected from the six domains supplied for ASTRA:

| ASTRA Domain | Undercurrent Contribution | Evidence in Prototype |
| :--- | :--- | :--- |
| **01 \| Indian Space Missions & Space Data** | Use satellite observations and space-derived datasets to inspect glacial lakes and reservoirs. | ISRO Bhuvan CartoDEM for terrain/slope, Bhoonidhi RISAT-1A SAR coherence verification, source metadata, and data-source acknowledgement. |
| **02 \| Earth Observation & Satellite Applications** | Extract water-body boundaries, compare surface areas, and analyse terrain/environmental patterns. | NDWI/MNDWI outputs, lake/reservoir boundaries, DEM/slope layers, and time-series charts. |
| **03 \| Space-Based Disaster Management** | Screen downstream river corridors and overlay settlements/infrastructure that may be exposed. | Terrain/drainage map, 112km exposure corridor overlay, clearly labelled preliminary screening results. |

### Domain Boundary Rules
* Do not add a separate communications, navigation, or connectivity product feature; it is not needed for this project.
* Keep all functionality tied to satellite data, Earth observation, water-resource monitoring, or space-based disaster-management support.
* Use Indian space datasets or portals where appropriate and accessible (Bhuvan, Bhoonidhi, MOSDAC, VEDAS).
* Do not claim an Indian dataset was used unless it was actually used and documented. Sentinel and Landsat are valid Earth-observation sources, but they are not Indian missions.
* Do not describe the dashboard as a real-time satellite system unless the data feed and refresh frequency genuinely support that claim.

---

## 4. Objectives, Use Cases, and Functional Scope

### 4.1 Main Objectives
* Monitor selected glacial-lake boundaries across multiple satellite observation dates.
* Calculate and visualise lake surface-area changes using a consistent method.
* Monitor selected reservoir water-spread boundaries and historical variation.
* Prepare terrain and drainage context from a DEM.
* Overlay downstream settlements, roads, and infrastructure for preliminary exposure screening.
* Present source data, observation dates, methods, limitations, and outputs in an accessible dashboard.

### 4.2 Core User Journeys
* **Journey A – Glacial Lake Review:** User selects South Lhonak Lake &rarr; chooses observation dates &rarr; views satellite imagery &rarr; compares extracted boundaries &rarr; reviews area and percentage change &rarr; inspects the source and quality notes.
* **Journey B – Reservoir Review:** User selects Chungthang Reservoir &rarr; chooses dates/seasons &rarr; views water boundaries &rarr; compares surface area &rarr; reviews trend chart and contextual notes (explicitly noting surface area vs volume).
* **Journey C – Downstream Exposure Screening:** User selects Teesta Basin &rarr; views DEM, slope, and drainage layers &rarr; overlays settlements/infrastructure &rarr; inspects preliminary exposure corridor and methodology notes.

### 4.3 Must-Have MVP vs Optional Scope
* **Must-Have MVP:**
  * One selected glacial lake (South Lhonak) with multiple valid observation dates (2013, 2019, 2021, Sept 2023, Oct 2023).
  * One reservoir case (Chungthang Dam) with comparable seasonal observations.
  * Water boundary and area calculation.
  * Basic historical comparison and trend chart.
  * DEM-based terrain/drainage visualisation.
  * Settlement and infrastructure overlay and exposure screening.
* **Out of Scope for Hackathon Prototype:**
  * Operational GLOF prediction or public emergency alerting.
  * Validated flood depth, velocity, arrival time, or inundation boundary without hydrodynamic modeling and calibration data.
  * Estimating reservoir storage volume from surface area alone.
  * Claiming continuous real-time monitoring when observations are historical or periodically updated.
  * Replacing official warning systems, field inspections, or expert decisions.

---

## 5. System Architecture and End-to-End Workflow

### 5.1 Logical Architecture
* **Data Sources:** Sentinel-2 MSI, Landsat 8/9, ISRO CartoDEM (Bhuvan), RISAT-1A SAR (Bhoonidhi), OpenStreetMap vectors.
* **Preprocessing:** Cloud/quality filtering, date selection, reprojection (UTM Zone 45N / EPSG:32645), clipping, and metadata capture.
* **Module 1 (Glacial Lake):** NDWI calculation, boundary extraction, area calculation, multi-date comparison.
* **Module 2 (Reservoir):** Water-boundary extraction, seasonal water-spread comparison.
* **Module 3 (Exposure):** Terrain slope, flow/drainage context, downstream asset overlay, multi-factor indicator.
* **Analytics/API:** FastAPI REST service exposing JSON summaries, map layers, alerts, and provenance.
* **Frontend:** Interactive Leaflet GIS map, Chart.js telemetry charts, NDWI threshold slider, dark aerospace UI.

### 5.2 End-to-End Workflow
$$\text{Satellite/Space Data} \longrightarrow \text{Preprocessing/Quality} \longrightarrow \text{Lake \& Reservoir Analyses} \longrightarrow \text{DEM/Drainage} \longrightarrow \text{Exposure Screening} \longrightarrow \text{API} \longrightarrow \text{Dashboard}$$

### 5.3 Data Lineage Requirements
Every displayed result retains:
1. Source name & provider (Copernicus / ISRO / USGS)
2. Product/sensor identifier
3. Acquisition timestamp
4. Spatial resolution
5. Coordinate reference system (EPSG:32645)
6. Cloud/quality assessment
7. Analysis method & threshold parameter
8. Area units ($km^2$) and scientific limitations

---

## 6. Data Strategy and Sources

| Dataset | Source Portal | Role in Undercurrent | Cautions & Mitigations |
| :--- | :--- | :--- | :--- |
| **Sentinel-2 MSI** | Copernicus Data Space | 10m water boundary extraction & NDWI tracking | Cloud, snow, terrain shadow; screened via QA band. |
| **CartoDEM (30m)** | ISRO Bhuvan Portal | Elevation, slope, and drainage flow path derivation | Interpolation artifacts in high relief; cross-checked with SRTM. |
| **RISAT-1A SAR** | ISRO Bhoonidhi Portal | Cloud-penetrating radar coherence for Oct 2023 breach | Radar layover/foreshortening in mountain terrain. |
| **Landsat 8/9 OLI** | USGS EarthExplorer | Decadal historical baseline (2013-2023) | 30m coarser spatial resolution; documented in metadata. |
| **Vector Assets** | OpenStreetMap / SDMA | Downstream settlements, bridges, dams, NH-10 highway | Citing source; labeled as screening perimeter. |

---

## 7. Scientific and Geospatial Methodology

### 7.1 Glacial Lake & Reservoir Water Detection
Normalized Difference Water Index (NDWI) using green and near-infrared bands:
$$\text{NDWI} = \frac{\text{Green} - \text{NIR}}{\text{Green} + \text{NIR}}$$
For Sentinel-2: Band 3 (560 nm) and Band 8 (842 nm). A threshold (typically $0.10 \le \theta \le 0.20$) classifies water pixels while separating moraine debris and shadows.

### 7.2 Area Calculation
Pixels classified as water are converted into an area using the projected coordinate system (UTM Zone 45N):
$$\text{Percentage Area Change} = \left(\frac{A_{\text{later}} - A_{\text{earlier}}}{A_{\text{earlier}}}\right) \times 100$$
Where $A_{\text{earlier}}$ and $A_{\text{later}}$ are observed surface areas in $km^2$.

### 7.3 Reservoir Interpretation
Reservoir surface area is a **water-spread indicator**, not storage volume. Storage estimation requires validated elevation-area-capacity curves or bathymetry. Undercurrent reports surface area and explicitly avoids presenting it as volume.

### 7.4 Exposure Screening vs Flood Modelling
Terrain-based screening identifies assets along downstream drainage paths. It does not calculate flood waves, water depth, velocity, or arrival time. MVP results are labeled as **"potential exposure screening"**.

### 7.5 Transparent Indicator Design
Zero black-box "AI risk scores". Multi-factor indicators disclose all component weights:
* Proximity to hazard source: 35%
* Valley slope & confinement: 25%
* Asset structural criticality: 25%
* Population footprint: 15%

---

## 8. Software Architecture & Technology Stack
* **Frontend:** Responsive Web Interface (HTML5, Tailwind CSS, Leaflet JS, Chart.js, Lucide Icons) + React Vite repository.
* **Backend:** Python 3 + FastAPI, Uvicorn, Pydantic, NumPy.
* **Geospatial Processing:** Pure Python + NumPy geodesic formulas, CartoDEM D8 flow routing, GeoJSON standard vectors.
* **API Endpoints:**
  * `GET /api/health`
  * `GET /api/lakes` & `GET /api/lakes/{id}/history`
  * `GET /api/lakes/{id}/compare`
  * `GET /api/reservoirs` & `GET /api/reservoirs/{id}/history`
  * `GET /api/exposure/{id}` & `GET /api/exposure/{id}/profile` & `GET /api/exposure/{id}/assets`
  * `GET /api/map/layers` & `GET /api/map/geojson/{layer_name}`
  * `GET /api/alerts`
  * `POST /api/analysis/ndwi`

---

## 9. Team Structure & Role Allocations
1. **Aerospace Member (Remote Sensing & Scientific Analysis Lead):**
   * Satellite image selection (Bhuvan, Copernicus).
   * QGIS validation, CRS alignment, GLOF physical mechanisms.
   * Scientific disclaimer governance and judge defense on remote sensing.
2. **CS Member 1 (Geospatial Processing & AI Engineer):**
   * Automated NDWI processing pipeline, raster matrix thresholding, area calculation.
3. **CS Member 2 (Backend & Data Engineer):**
   * FastAPI endpoints, schemas, metadata catalogue, REST services, CORS.
4. **CS Member 3 (Frontend & Product Engineer):**
   * UI/UX dashboard, Leaflet GIS map controls, Chart.js graphs, live presentation demo flow.

---

## 10. ASTRA 100-Point Scoring Strategy
* **Technical Implementation (25 Marks):** Real satellite inputs, clean FastAPI backend, modular code, documented REST API.
* **Working Prototype & Demo (20 Marks):** Seamless end-to-end user journeys working in a live browser without mock errors.
* **Presentation & Demo (15 Marks):** Disciplined speaking split, real science defense, honest technical answers.
* **Innovation & Creativity (10 Marks):** Basin-oriented integration of glacial lakes and reservoirs into one workflow.
* **Problem Relevance (10 Marks):** Focus on real Himalayan vulnerable geography (Teesta River / South Lhonak disaster).
* **UI/UX & User Experience (10 Marks):** Professional dark aerospace interface, interactive maps, intuitive sliders.
* **Scalability & Feasibility (10 Marks):** Modular configuration allows easily adding more Himalayan basins (e.g. Satluj, Bhagirathi).

---

## 11. Final Principle
**Build a small, scientifically defensible, fully working system. Show the real data, show the method, show the output, and explain its limitations. Undercurrent's strongest story is the integration of satellite-observed water-body change with downstream geographical context—not an unsupported claim that it can predict disasters.**
