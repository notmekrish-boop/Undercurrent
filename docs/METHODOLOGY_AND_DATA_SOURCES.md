# Project Undercurrent: Scientific Methodology & Data Sources

This document details the scientific principles, sensor specifications, indices, and geospatial algorithms implemented across Project Undercurrent.

---

## 1. Data Sources & Space Missions

Undercurrent aligns with the **ASTRA 2026 Space Hackathon** requirements by combining Indian space data with open-access international Earth observation missions.

### 1.1 Indian Space Missions & Portals
* **ISRO Bhuvan (NRSC):** 
  * Source of **CartoDEM (30-meter spatial resolution)** derived from Cartosat-1 stereo pairs. 
  * Used to calculate the elevation profile, terrain slope gradients, and hydrological stream flow vectors from 5,200 m down to 280 m ASL.
* **ISRO Bhoonidhi:**
  * Source of **RISAT-1A (EOS-04) C-band Synthetic Aperture Radar (SAR)**.
  * Essential for cloud-penetrating verification of moraine geometry during heavy Himalayan monsoon storms when optical sensors suffer >80% cloud occlusion.
* **MOSDAC & VEDAS (ISRO/SAC):**
  * Meteorological parameters and regional hydrological mapping baselines for the Teesta basin.

### 1.2 Earth Observation Constellations
* **Copernicus Sentinel-2 MSI (Level-2A Bottom-Of-Atmosphere):**
  * 10m spatial resolution in visible (Band 2 Blue, Band 3 Green, Band 4 Red) and Near-Infrared (Band 8).
  * 5-day revisit rate under two-satellite constellation.
  * Primary optical imagery source for NDWI water extraction.
* **USGS / NASA Landsat-8 & Landsat-9 OLI:**
  * 30m multispectral resolution.
  * Serves as the decadal historical baseline (2013–2023) tracking long-term lake expansion.

---

## 2. Water Boundary Extraction: Normalized Difference Water Index (NDWI)

### 2.1 Index Formulation
The platform implements McFeeters' Normalized Difference Water Index:
$$\text{NDWI} = \frac{\rho_{\text{Green}} - \rho_{\text{NIR}}}{\rho_{\text{Green}} + \rho_{\text{NIR}}}$$
For Sentinel-2 MSI:
* $\rho_{\text{Green}}$ = Band 3 ($560 \text{ nm}$)
* $\rho_{\text{NIR}}$ = Band 8 ($842 \text{ nm}$)

### 2.2 Physical Basis
Clear and turbid water bodies absorb almost all incident radiation in the near-infrared wavelengths while exhibiting moderate reflectance in the green band. In contrast, surrounding snow, moraine debris, bare rock, and sparse mountain vegetation reflect higher proportions of NIR radiation, yielding negative or near-zero NDWI values.

### 2.3 Threshold Sensitivity
Rather than relying on a static $0.0$ threshold, Undercurrent incorporates an adaptive thresholding mechanism ($0.05 \le \theta \le 0.25$):
* **Lower thresholds ($\sim 0.08 - 0.12$):** Capture shallow, sediment-heavy glacial lake margins.
* **Nominal threshold ($0.14$):** Calibrated against South Lhonak ground truth, isolating deep glacial water while rejecting mountain shadows.
* **Higher thresholds ($\sim 0.20$):** High confidence core water mask, minimizing edge false positives from melting snow patches.

---

## 3. Surface Area Calculation & Projected Coordinate Systems

### 3.1 CRS Projection
Calculating area directly from geographic coordinates (degrees of latitude and longitude) introduces severe latitude-dependent distortions in high-latitude mountain terrain. 
* All vector polygon geometries are projected into **WGS 84 / UTM Zone 45N (EPSG:32645)**.
* Area in square meters is computed via the Shoelace polygon formula and converted to square kilometers ($km^2$):
$$\text{Area } (km^2) = \frac{1}{2 \times 10^6} \left| \sum_{i=0}^{N-1} (x_i y_{i+1} - x_{i+1} y_i) \right|$$

### 3.2 Change Detection Formulation
Relative surface area variation between chronological dates $t_1$ and $t_2$:
$$\Delta A = A_{t_2} - A_{t_1}$$
$$\% \Delta A = \left(\frac{A_{t_2} - A_{t_1}}{A_{t_1}}\right) \times 100$$
* A positive value represents glacial melt accumulation or seasonal reservoir filling.
* A sudden severe negative value ($<-20\%$) flags a potential moraine breach or dam failure.

---

## 4. Downstream Exposure Corridor & Asset Screening

### 4.1 Hydrological Drainage Extraction
Using the 30m CartoDEM, sink-filling and D8 single-flow-direction algorithms delineate the primary hydraulic flowpath from South Lhonak Lake through Lhonak Chu, Zemu Chu, Lachen Chu, and into the Teesta River mainstem.

### 4.2 Valley Confinement & Exposure Buffering
In steep Himalayan V-shaped gorges, flood surges remain hydraulically confined to narrow valley floors:
* **High Exposure Zone:** 500-meter corridor centered on the thalweg centerline. Encompasses immediate valley floor, riverbed terraces, low-clearance bridges, and riverbank highway alignments.
* **Moderate Exposure Zone:** 1,500-meter corridor encompassing secondary alluvial fans, tributary confluences, and valley flanks susceptible to debris damming.

### 4.3 Multi-Factor Asset Scoring
To remain scientifically defensible and avoid deceptive "AI prediction scores", exposure ratings are calculated through explicit multi-factor weighting:
$$\text{Exposure Score} = 0.35 \cdot S_{\text{prox}} + 0.25 \cdot S_{\text{slope}} + 0.25 \cdot S_{\text{crit}} + 0.15 \cdot S_{\text{pop}}$$
* **$S_{\text{prox}}$ (Proximity):** Normalised inverse distance along the 112 km river reach.
* **$S_{\text{slope}}$ (Slope Confinement):** Mean slope gradient of surrounding valley walls ($>25^\circ$ creates higher confinement).
* **$S_{\text{crit}}$ (Asset Criticality):** High for strategic hydropower dams (Teesta-III, Teesta-V) and lifeline highway bridges (NH-10).
* **$S_{\text{pop}}$ (Population Footprint):** Log-scaled settlement census estimation.

---

## 5. Summary of South Lhonak Historical Observations

| Date | Sensor | Area ($km^2$) | $\% \Delta A$ (vs baseline) | Status / Context |
| :--- | :--- | :--- | :--- | :--- |
| **2013-10-18** | Landsat-8 OLI | 0.984 | Reference | Historical baseline |
| **2019-10-05** | Sentinel-2 MSI | 1.348 | +37.0% | Steady decadal expansion |
| **2021-10-12** | Sentinel-2 MSI | 1.492 | +51.6% | Significant glacial retreat |
| **2023-09-17** | Sentinel-2 MSI | 1.682 | +70.9% | Pre-disaster maximum extent |
| **2023-10-04** | Sentinel-2 / RISAT-1A | 1.031 | -38.7% (vs Sep 2023) | Moraine breach & sudden drainage |
| **2024-05-20** | Sentinel-2 MSI | 1.082 | +4.9% (vs Oct 2023) | Stabilized remnant lake |
