import os
import json
from fastapi import APIRouter
from ..schemas.models import NDWICalculationRequest, NDWICalculationResult
from ..services.ndwi_engine import generate_lake_ndwi_matrix, classify_water_pixels

router = APIRouter(prefix="/analysis", tags=["Scientific Geospatial Analysis"])

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
