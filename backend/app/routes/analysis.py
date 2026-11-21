import os
import base64
import json
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from ..schemas.models import NDWICalculationRequest, NDWICalculationResult, LakePhotoAnalysisRequest, LakePhotoAnalysisResult
from ..services.image_analysis import analyze_uploaded_lake_photo
from ..services.ndwi_engine import (
    generate_lake_ndwi_matrix,
    classify_water_pixels,
    process_real_satellite_raster
)

router = APIRouter(prefix="/analysis", tags=["Scientific Geospatial Analysis"])

@router.get("/validation", summary="Get scientific validation record conforming to Phase 1 of development roadmap")
def get_scientific_validation():
    val_file = os.path.normpath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "..", "data", "metadata", "scientific_validation.json"
    ))
    if os.path.exists(val_file):
        with open(val_file, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Scientific validation record not found.")

@router.get("/raster/south-lhonak", summary="Process physical Sentinel-2 MSI Level-2A GeoTIFFs with exact pixel ground area")
def get_physical_raster_analysis(
    date: str = Query("2023-10-09", description="Observation date (2023-09-26 or 2023-10-09)"),
    threshold: Optional[float] = Query(None, description="Optional custom NDWI threshold (default: 0.20 pre-flood, 0.265 post-flood)")
):
    try:
        th = float(threshold) if (threshold is not None and isinstance(threshold, (int, float))) else None
        d_str = str(date) if isinstance(date, str) else "2023-10-09"
        return process_real_satellite_raster(date=d_str, threshold=th)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Raster processing error: {e}")

@router.get("/ndwi/grids", summary="Get real Sentinel-2 MSI level-2A NDWI grids for pre and post outburst")
def get_real_ndwi_grids():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    grid_path = os.path.normpath(os.path.join(base_dir, "..", "data", "processed", "sentinel2_real_ndwi_grids.json"))
    if os.path.exists(grid_path):
        with open(grid_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.post("/ndwi", response_model=NDWICalculationResult, summary="Perform NDWI threshold water extraction calculation")
def calculate_ndwi(req: NDWICalculationRequest):
    is_post = "post" in req.lake_id.lower() or "breach" in req.lake_id.lower()
    matrix = generate_lake_ndwi_matrix(grid_size=req.grid_size, post_outburst=is_post)
    res = classify_water_pixels(matrix, threshold=req.threshold)
    
    return NDWICalculationResult(
        lake_id=req.lake_id,
        threshold_used=req.threshold,
        water_pixel_count=res["water_pixel_count"],
        total_pixel_count=res["total_pixel_count"],
        water_area_ratio=res["water_area_ratio"],
        calculated_area_km2=res["calculated_area_km2"],
        sensor=req.sensor,
        formula="NDWI = (Green - NIR) / (Green + NIR)",
        matrix_grid=res["matrix_grid"],
        classification_grid=res["classification_grid"]
    )

@router.post("/upload-photo", response_model=LakePhotoAnalysisResult, summary="Upload a photo or satellite image to calculate lake water area and pixel segmentation")
def upload_and_calculate_photo_area(req: LakePhotoAnalysisRequest):
    try:
        return analyze_uploaded_lake_photo(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image processing error: {e}")



@router.get("/sample-photo", summary="Get a pre-loaded sample photo or satellite band for demonstration")
def get_sample_photo(preset: str = Query("oct09_b11", description="Preset key: oct09_b11, sep26_truecolor, oct09_truecolor, sep26_b03")):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sat_dir = os.path.normpath(os.path.join(base_dir, "..", "data", "raw", "satellite"))

    presets = {
        "oct09_b11": ("2023-10-09_B11.tiff.tiff", "2023-10-09", "South Lhonak Glacial Lake (Post-Breach SWIR Band 11)"),
        "sep26_truecolor": ("2023-09-26_TrueColor.tiff.tiff", "2023-09-26", "South Lhonak Glacial Lake (Pre-Breach TrueColor)"),
        "oct09_truecolor": ("2023-10-09_TrueColor.tiff.tiff", "2023-10-09", "South Lhonak Glacial Lake (Post-Breach TrueColor)"),
        "sep26_b03": ("2023-09-26_B03.tiff.tiff", "2023-09-26", "South Lhonak Glacial Lake (Pre-Breach Green Band 3)")
    }

    if preset not in presets:
        raise HTTPException(status_code=400, detail=f"Unknown preset '{preset}'. Available: {list(presets.keys())}")

    filename, obs_date, desc = presets[preset]
    file_path = os.path.join(sat_dir, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"Sample file {filename} not found.")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    b64_data = base64.b64encode(file_bytes).decode("utf-8")
    data_uri = f"data:image/tiff;base64,{b64_data}"

    return {
        "preset": preset,
        "file_name": filename,
        "observation_date": obs_date,
        "lake_name": "South Lhonak Glacial Lake",
        "description": desc,
        "photo_base64": data_uri,
        "pixel_resolution_m": 10.0,
        "file_size_kb": round(len(file_bytes) / 1024, 1)
    }
