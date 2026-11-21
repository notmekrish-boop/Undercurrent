from fastapi import APIRouter, HTTPException
from typing import List
from ..services.data_service import data_service
from ..services.geospatial import evaluate_exposure_score

router = APIRouter(prefix="/exposure", tags=["Downstream Exposure Screening"])

@router.get("/{study_area_id}", summary="Get exposure screening summary for the basin corridor")
def get_exposure_summary(study_area_id: str):
    assets = data_service.get_assets()
    profile = data_service.get_elevation_profile()

    high_exposure = [a for a in assets if a.get("exposure_rating") == "Critical"]
    total_screened = len(assets)

    avg_slope = 0.0
    if profile:
        avg_slope = round(sum(p["slope_deg"] for p in profile) / len(profile), 1)

    return {
        "corridor_id": "EXP-TEESTA-MAIN",
        "study_area_id": study_area_id,
        "basin": "Teesta River Basin, Sikkim Himalaya",
        "origin_lake": "South Lhonak Glacial Lake (Elev: 5,200m)",
        "terminal_checkpoint": "Rangpo Border (Elev: 280m)",
        "total_corridor_length_km": 112.4,
        "elevation_drop_m": 4920,
        "high_exposure_assets_count": len(high_exposure),
        "total_assets_screened": total_screened,
        "terrain_slope_mean_deg": avg_slope,
        "screening_zones": [
            {
                "zone_name": "High Exposure Valley Floor",
                "width_buffer_m": 500,
                "description": "Steep V-shaped gorge corridor with high stream confinement."
            },
            {
                "zone_name": "Secondary Flank Screening",
                "width_buffer_m": 1500,
                "description": "Tributary junctions, terrace terraces, and alluvial fan backwater areas."
            }
        ],
        "methodology": "SRTM/CartoDEM D8 flow routing + buffer geometric intersections.",
        "scientific_disclaimer": "This is a preliminary downstream exposure screening corridor. It identifies areas along the drainage pathway that may merit closer investigation; it does NOT compute hydrodynamic flood waves, water depths, or arrival velocities."
    }

@router.get("/{study_area_id}/profile", summary="Get DEM elevation and slope profile along the river corridor")
def get_corridor_profile(study_area_id: str):
    profile = data_service.get_elevation_profile()
    return {
        "study_area_id": study_area_id,
        "basin": "Teesta River Basin",
        "profile_points_count": len(profile),
        "profile": profile
    }

def interpolate_corridor_slope(distance_km: float, profile: List[Dict[str, Any]]) -> float:
    """Derive location-specific valley slope from DEM elevation profile."""
    if not profile:
        return 22.0
    if distance_km <= profile[0]["distance_km"]:
        return profile[0]["slope_deg"]
    if distance_km >= profile[-1]["distance_km"]:
        return profile[-1]["slope_deg"]
    for i in range(len(profile) - 1):
        d0, d1 = profile[i]["distance_km"], profile[i+1]["distance_km"]
        if d0 <= distance_km <= d1:
            ratio = (distance_km - d0) / (d1 - d0) if d1 > d0 else 0
            s0, s1 = profile[i]["slope_deg"], profile[i+1]["slope_deg"]
            return round(s0 + ratio * (s1 - s0), 1)
    return profile[-1]["slope_deg"]

@router.get("/{study_area_id}/assets", summary="Get list of downstream assets with transparent exposure breakdown")
def get_corridor_assets(study_area_id: str):
    raw_assets = data_service.get_assets()
    profile = data_service.get_elevation_profile()
    scored_assets = []
    for a in raw_assets:
        dist = a.get("distance_from_lake_km", 50.0)
        elev = a.get("elevation_m", 1000)
        elev_drop = 5200 - elev
        local_slope = interpolate_corridor_slope(dist, profile)

        score_data = evaluate_exposure_score(
            distance_km=dist,
            elevation_drop_m=elev_drop,
            slope_deg=local_slope,
            asset_type=a.get("type", "Settlement"),
            population=a.get("population_approx", 1000)
        )
        score_data["location_slope_deg"] = local_slope
        score_data["elevation_drop_m"] = elev_drop
        score_data["slope_source"] = "DEM-derived corridor elevation profile"

        item = dict(a)
        item["location_slope_deg"] = local_slope
        item["elevation_drop_m"] = elev_drop
        item["scoring_breakdown"] = score_data
        scored_assets.append(item)
    return {
        "study_area_id": study_area_id,
        "total_assets": len(scored_assets),
        "assets": scored_assets,
        "methodology": "Weighted multi-factor heuristic screening index using location-specific DEM slope. Not a calibrated hydraulic flood probability."
    }
