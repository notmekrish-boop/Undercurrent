import os
import json
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from ..schemas.models import NDWICalculationRequest, NDWICalculationResult
from ..services.ndwi_engine import (
    generate_lake_ndwi_matrix,
    classify_water_pixels,
    process_real_satellite_raster
)

router = APIRouter(prefix="/analysis", tags=["Scientific Geospatial Analysis"])

@router.get("/raster/south-lhonak", summary="Process physical Sentinel-2 MSI Level-2A GeoTIFFs with exact pixel ground area")
def get_physical_raster_analysis(
    date: str = Query("2023-10-09", description="Observation date (2023-09-26 or 2023-10-09)"),
    threshold: Optional[float] = Query(None, description="Optional custom NDWI threshold (default: 0.0 pre-flood, 0.265 post-flood)")
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
