# UNDERCURRENT | ASTRA 2026 Presentation & Live Demo Script

**Total Duration:** 7–8 Minutes (Fits 5–10 minute hackathon format)  
**Team Composition:** 1 Aerospace Lead + 3 Computer Science Engineers  
**Project:** Undercurrent – Himalayan Water Intelligence & Glacial Risk Monitoring System  

---

## 1. Presentation Timeline & Speaking Split

```
0:00 - 0:45 | Problem & Project Identity      -> CS 3 (Frontend / Pitch Lead)
0:45 - 1:45 | Domains & Indian Space Data      -> Aerospace Member (Science Lead)
1:45 - 2:45 | System Architecture & Data Flow -> CS 2 (Backend / Data Engineer)
2:45 - 3:45 | Geospatial Science & Pipeline   -> CS 1 (Geospatial / AI Engineer)
3:45 - 6:30 | Live Interactive Prototype Demo -> CS 3 + Aerospace
6:30 - 7:30 | Impact, Limitations & Roadmap   -> Aerospace + CS 2
7:30 - End  | Judge Q&A Defense               -> Full Team
```

---

## 2. Minute-by-Minute Rehearsal Script

### [0:00 – 0:45] Problem & Project Identity (Speaker: CS 3)
* **Screen:** Show Dashboard Overview with Teesta River Basin header.
* **Script:**
  > "Respected judges, the Himalayas are called the Third Pole, housing thousands of glacial lakes perched high above populated river valleys. In October 2023, the sudden outburst of South Lhonak Lake in Sikkim overtopped the Chungthang Dam and devastated downstream infrastructure across 100 kilometers of the Teesta Valley. 
  > Current monitoring is often fragmented: satellite images sit in one portal, terrain models in another, and reservoir records elsewhere. 
  > Introducing **Undercurrent**—an integrated geospatial intelligence platform connecting upstream glacial-lake change monitoring, downstream exposure screening, and reservoir water-spread tracking into a single basin-oriented decision-support dashboard."

### [0:45 – 1:45] Domains & Indian Space Missions Alignment (Speaker: Aerospace Lead)
* **Screen:** Switch to *Methodology & Provenance* tab showing ASTRA domain alignment and Bhuvan/Copernicus data sources.
* **Script:**
  > "Undercurrent addresses three key ASTRA domains:
  > First, **Indian Space Missions & Data**: We integrate ISRO CartoDEM from Bhuvan at 30-meter resolution to derive true topographic slope and hydrological stream routing down the Teesta gorge. During monsoon cloud cover, optical satellites are blinded; we utilize ISRO Bhoonidhi's RISAT-1A C-band radar data for cloud-penetrating change detection.
  > Second, **Earth Observation**: We track multi-date surface-area variations using Sentinel-2 MSI and decadal Landsat-8 observations.
  > Third, **Space-Based Disaster Management**: We project the preliminary exposure corridor along 112 kilometers of valley floor to screen vulnerable downstream assets."

### [1:45 – 2:45] System Architecture & Data Lineage (Speaker: CS 2)
* **Screen:** Show FastAPI Swagger docs (`/api/docs`) or Architecture block.
* **Script:**
  > "Our architecture is intentionally lean, modular, and fast. Built with Python and FastAPI, our backend handles geospatial calculations using projected UTM Zone 45N coordinates.
  > We designed 8 dedicated REST endpoints covering lake histories, reservoir water-spread variations, elevation profiles, and rule-based anomaly flags.
  > Every data point returned by the API carries rigorous provenance: sensor type, spatial resolution, acquisition date, cloud quality score, and coordinate reference system. This ensures transparency before judges and stakeholders."

### [2:45 – 3:45] Scientific Method & Water Detection (Speaker: CS 1)
* **Screen:** Switch to *Glacial Lake Monitor* showing the NDWI formula and dynamic threshold slider.
* **Script:**
  > "To extract water bodies consistently across dates, we apply the Normalized Difference Water Index: Green minus Near-Infrared divided by Green plus Near-Infrared. Water absorbs NIR strongly while reflecting green light.
  > Rather than hardcoding an arbitrary threshold, Undercurrent features an adaptive threshold engine. Look at this interactive simulation of South Lhonak Lake: as we adjust the cutoff between 0.05 and 0.25, the system visualizes the boundary between turbid glacial meltwater and barren lateral moraine.
  > Between September 17 and October 4, 2023, the lake's mapped surface area plunged from 1.68 km² down to 1.03 km²—a catastrophic drainage of -38.7% corresponding to moraine failure."

### [3:45 – 6:30] Live Interactive Demonstration (Speakers: CS 3 + Aerospace)
* **Action 1 (Lake Review):** Select date `2023-10-04`. Point out the -0.651 km² delta and the decadal trend chart showing growth since 2013.
* **Action 2 (Reservoir Review):** Switch to *Reservoir Water Spread*.
  > **Aerospace Lead:** "Notice this crucial scientific distinction: we report reservoir **water-spread area**, not storage volume. Satellite optical imagery cannot measure underwater bathymetry. Between September and October 2023, the Chungthang Dam's surface spread dropped by 77.7%, visually capturing the physical destruction and bypass drainage of the dam structure."
* **Action 3 (Exposure Screening):** Switch to *Downstream Exposure*.
  > **CS 3:** "Here is our 112-kilometer DEM elevation profile: descending 4,920 vertical meters from 5,200m down to Rangpo at 280m. We overlay 8 critical downstream assets. Notice our transparent multi-factor exposure scoring—no black-box AI scores. We weight proximity by 35%, slope confinement by 25%, structural criticality by 25%, and population footprint by 15%."
* **Action 4 (Interactive GIS Map):** Switch to *Interactive GIS Map*.
  > **CS 3:** "On the live Leaflet map, judges can inspect the lake boundary, toggle the high-exposure 500-meter gorge buffer, trace the Teesta River flowpath, and inspect individual settlement pins like Chungthang Town, Indreni Bridge, and NH-10 Highway."

### [6:30 – 7:30] Responsible Claims, Impact & Future Scope (Speaker: Aerospace Lead)
* **Screen:** Return to *Overview* or *Methodology*.
* **Script:**
  > "We hold ourselves to strict ethical and scientific boundaries. Undercurrent does not claim to predict GLOFs or issue real-time public emergency warnings—that requires complex 2D hydrodynamic calibration and on-site geotechnical sensors.
  > What Undercurrent provides is rapid, defensible, satellite-driven situational awareness for planners. Because our data models are fully decoupled from hardcoded geometries, adding new Himalayan river basins like Satluj, Chamoli, or Bhagirathi requires only new configuration and imagery.
  > Thank you, and we welcome your questions!"

---

## 3. Judge Defense Q&A Cheat Sheet

| Question | Who Answers | Model Answer to Deliver |
| :--- | :--- | :--- |
| **Why not claim this as an AI GLOF prediction system?** | Aerospace Lead | "Predicting a GLOF requires knowing the internal ice core degradation, hydrostatic pressure, moraine shear strength, and geotechnical triggers like seismic activity or rock avalanches—none of which optical satellite imagery alone can measure. Labeling it 'preliminary exposure screening' is the only scientifically honest approach." |
| **How did you handle cloud cover during the October 2023 Sikkim disaster?** | Aerospace Lead | "During the intense pre-disaster rain event, optical sensors like Sentinel-2 were cloud-obscured. We reviewed ISRO Bhoonidhi's RISAT-1A Synthetic Aperture Radar (SAR) imagery, which penetrates clouds using active microwave C-band pulses to detect moraine breach changes." |
| **Why not calculate water volume from satellite area?** | CS 1 | "Lake and reservoir beds have non-uniform bathymetric profiles (U-shaped vs V-shaped). Without calibrated elevation-capacity curves or sonar bathymetry, multiplying area by an assumed depth produces misleading volumetric estimates." |
| **How is the system architected for scalability?** | CS 2 | "The backend uses a modular schema with StudyArea, WaterBody, Observation, and ExposureLayer entities. To onboard a new basin, an analyst simply adds GeoJSON boundaries and satellite observation records into the repository without modifying any core processing logic." |
| **How did you prevent calculation errors from raw coordinates?** | CS 1 | "Degrees of latitude and longitude distort distance and area as you move away from the equator. We reproject coordinates into the standard projected coordinate reference system UTM Zone 45N (EPSG:32645), computing true geodesic metrics in square kilometers." |
