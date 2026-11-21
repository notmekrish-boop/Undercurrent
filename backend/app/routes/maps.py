from fastapi import APIRouter, HTTPException
from ..services.data_service import data_service

router = APIRouter(prefix="/map", tags=["Geospatial Map Layers"])

@router.get("/layers", summary="List all available geospatial layers for map visualisation")
def get_map_layers():
    return {
        "basin": "Teesta River Basin, Sikkim",
        "center": [27.55, 88.50],
        "default_zoom": 10,
        "layers": [
            {
                "id": "layer_lake_boundaries",
                "name": "Glacial Lake Extents (Multi-date)",
                "type": "vector_polygon",
                "endpoint": "/api/map/geojson/south_lhonak",
                "color": "#0284c7",
                "category": "Glacial Lake",
                "visible_default": True
            },
            {
                "id": "layer_reservoirs",
                "name": "Reservoir Water Spread Boundaries",
                "type": "vector_polygon",
                "endpoint": "/api/map/geojson/chungthang",
                "color": "#38bdf8",
                "category": "Reservoir",
                "visible_default": True
            },
            {
                "id": "layer_drainage",
                "name": "River Drainage Flowpath",
                "type": "vector_linestring",
                "endpoint": "/api/map/geojson/drainage",
                "color": "#2563eb",
                "category": "Hydrology",
                "visible_default": True
            },
            {
                "id": "layer_exposure_high",
                "name": "Downstream Exposure Corridor (High & Moderate)",
                "type": "vector_polygon",
                "endpoint": "/api/map/geojson/exposure",
                "color": "#ef4444",
                "category": "Risk Screening",
                "visible_default": True
            },
            {
                "id": "layer_assets",
                "name": "Settlements & Critical Infrastructure",
                "type": "vector_point",
                "endpoint": "/api/map/geojson/assets",
                "color": "#f59e0b",
                "category": "Exposure Overlay",
                "visible_default": True
            }
        ]
    }

@router.get("/geojson/{layer_name}", summary="Fetch raw GeoJSON for a specified layer")
def get_layer_geojson(layer_name: str):
    data = data_service.get_geojson(layer_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Layer GeoJSON '{layer_name}' not found.")
    return data
