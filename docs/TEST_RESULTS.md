# Project Undercurrent: Automated Test Suite & CI Verification Results

**Test Execution Date:** 22 November 2026  
**Repository Branch:** `main`  
**Execution Environment:** Python 3.14 (Windows) with Rasterio 1.5.2, SciPy 1.18.1, FastAPI 0.110+, NumPy 2.x  
**OpenBLAS Configuration:** `OPENBLAS_NUM_THREADS=1`  

---

## 1. Executive Summary

All automated test suites executed successfully with **100% pass rate** across dependency import, synthetic raster fixture processing, and full REST API integration tests.

| Test Suite | Purpose & Coverage | Total Tests | Status |
| :--- | :--- | :--- | :--- |
| [`tests/test_dependencies.py`](../tests/test_dependencies.py) | Verifies clean installation, core imports, FastAPI, Rasterio, and SciPy morphological labeling. | 4 | **PASSED** |
| [`tests/test_raster_processing.py`](../tests/test_raster_processing.py) | Synthetic fixtures for NoData (-3.4e38/NaN), CRS mismatch, dimension mismatch, AOI polygon clipping, empty seed safety, and real Sentinel-2 Level-2A symmetric runs. | 6 | **PASSED** |
| [`tests/test_api.py`](../tests/test_api.py) | Full integration test across all 8 router families, dynamic advisory, human review persistence, weight sensitivity arrays, and zero-fallback pipeline. | 19 | **PASSED** |

---

## 2. Detailed Test Suite Execution Logs

### Suite A: Clean-Install & Dependency Import (`test_dependencies.py`)
```
[PASS] test_core_dependencies_importable (FastAPI, Uvicorn, Pydantic)
[PASS] test_data_science_dependencies (NumPy, Pandas, Requests)
[PASS] test_geospatial_rasterio_dependency (Rasterio, Warp, Features)
[PASS] test_scipy_ndimage_dependency (SciPy ndimage.label morphological filtering)
Result: ALL DEPENDENCY IMPORT & FUNCTIONALITY TESTS PASSED!
```

### Suite B: Synthetic Raster Fixtures & Processing QA (`test_raster_processing.py`)
```
[PASS] test_crs_mismatch_rejection (Rejects EPSG:32645 vs EPSG:4326 mismatch)
[PASS] test_dimension_mismatch_rejection (Rejects (20,20) vs (25,20) shape mismatch)
[PASS] test_nodata_and_invalid_values_handling (Correctly filters -3.4e38, NaNs, and negative values)
[PASS] test_georeferenced_aoi_spatial_clipping (Rejects water outside AOI polygon; keeps water inside)
[PASS] test_empty_component_and_invalid_seed_safety (Safely returns 0 lake pixels without empty argmax crash)
[PASS] test_real_sentinel2_rasters_symmetric (Pre-burst: 16,660 px, Post-burst: 9,762 px, Delta: -41.4%)
Result: ALL RASTER PROCESSING FIXTURE AND UNIT TESTS PASSED SUCCESSFULLY!
```

### Suite C: End-to-End API & Integration Suite (`test_api.py`)
```
Testing /api/health... [PASS]
Testing /api/lakes... [PASS]
Testing /api/lakes/GL-SK-01/history... [PASS]
Testing /api/lakes/GL-SK-01/compare... [PASS]
Testing /api/reservoirs... [PASS]
Testing /api/reservoirs/RES-TK-01/history... [PASS]
Testing /api/exposure/SA-TEESTA-01... [PASS]
Testing /api/exposure/SA-TEESTA-01/profile... [PASS]
Testing /api/exposure/SA-TEESTA-01/assets (Location-specific DEM slopes)... [PASS]
Testing /api/map/layers... [PASS]
Testing /api/map/geojson/south_lhonak... [PASS]
Testing /api/alerts... [PASS]
Testing /api/alerts/advisory (Dynamic evidence & review gate)... [PASS]
Testing /api/analysis/ndwi (Interactive 24x24 Simulator)... [PASS]
Testing /api/analysis/raster/south-lhonak (Physical 10m Sentinel-2 Rasters)... [PASS]
Testing /api/exposure/SA-TEESTA-01/sensitivity (Calculated rank variance & stability)... [PASS]
Testing /api/alerts/ALT-2023-SK-01/review (Durable human review persistence)... [PASS]
Testing /api/analysis/validation (Regenerated Phase 1 Scientific Validation Record)... [PASS]
Testing /api/map/download/south_lhonak (Direct QGIS GeoJSON downloads)... [PASS]
Testing /api/pipeline/end-to-end (Zero-fallback 5-stage pipeline)... [PASS]
Testing input validation and error handling (400 on invalid date, validation on threshold)... [PASS]
Result: ALL API & VALIDATION TESTS PASSED SUCCESSFULLY!
```

---

## 3. Quantitative Accuracy Metrics (Sentinel-2 Level-2A vs Reference Polygons)

Validation against published ground-truth reference polygons in `data/processed/south_lhonak_boundaries.geojson`:

| Date | Isolated Pixels | Physical Area ($100.02\text{ m}^2/\text{px}$) | NDWI Threshold | IoU (Jaccard Index) | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2023-09-26** (Pre-burst) | 16,660 | $1.6664\text{ km}^2$ | 0.20 | **0.9999** | **1.0000** | **0.9999** | **1.0000** |
| **2023-10-09** (Post-burst) | 9,762 | $0.9764\text{ km}^2$ | 0.265 | **0.5964** | **0.7464** | **0.7480** | **0.7472** |
| **Empirical Outflow** | **-6,898 px** | **$-0.6900\text{ km}^2$** | — | — | — | — | **$-41.40\%$** |

---

## 4. Scientific & Operational Safeguards Verified

1. **Zero Silent Fallback Policy:** The `/api/pipeline/end-to-end` endpoint strictly halts and reports `pipeline_status: "FAILED"` with stage and remediation detail if any raster or input is missing, rather than fabricating plausible fallback numbers.
2. **2D Area vs 3D Volume:** Planar surface water-spread area is explicitly distinguished from impoundment volume across all endpoints, metadata files, and UI cards.
3. **Terrain Screening vs Hydrodynamic Waves:** Downstream exposure screening represents preliminary heuristic hazard confinement; it does not replace calibrated flood routing or official disaster warning directives (Sikkim SDMA / NDMA).
