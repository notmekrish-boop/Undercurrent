from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..services.data_service import data_service
from ..services.geospatial import compute_percentage_change

router = APIRouter(prefix="/lakes", tags=["Glacial Lake Monitoring"])

@router.get("", summary="List monitored glacial lakes")
def get_glacial_lakes():
    return data_service.get_glacial_lakes()

@router.get("/{lake_id}", summary="Get details for a specific glacial lake")
def get_lake_by_id(lake_id: str):
    lakes = data_service.get_glacial_lakes()
    for lake in lakes:
        if lake["id"] == lake_id or lake_id.lower() in lake["name"].lower():
            return lake
    raise HTTPException(status_code=404, detail=f"Glacial lake '{lake_id}' not found.")

@router.get("/{lake_id}/history", summary="Get multi-date observation records for a glacial lake")
def get_lake_history(lake_id: str):
    history = data_service.get_lake_history(lake_id)
    if not history:
        raise HTTPException(status_code=404, detail=f"No history records found for lake '{lake_id}'.")
    return {
        "lake_id": lake_id,
        "name": "South Lhonak Glacial Lake",
        "observations_count": len(history),
        "history": history
    }

@router.get("/{lake_id}/compare", summary="Compare two observation dates for a glacial lake")
def compare_lake_dates(
    lake_id: str,
    date1: str = Query(..., description="Earlier observation date (YYYY-MM-DD), e.g., 2023-09-17"),
    date2: str = Query(..., description="Later observation date (YYYY-MM-DD), e.g., 2023-10-04")
):
    history = data_service.get_lake_history(lake_id)
    obs_dict = {o.get("date"): o for o in history}

    if date1 not in obs_dict:
        raise HTTPException(status_code=400, detail=f"Date '{date1}' not available in observations. Available: {list(obs_dict.keys())}")
    if date2 not in obs_dict:
        raise HTTPException(status_code=400, detail=f"Date '{date2}' not available in observations. Available: {list(obs_dict.keys())}")

    obs1 = obs_dict[date1]
    obs2 = obs_dict[date2]

    # Ensure chronological order
    if obs1["date"] > obs2["date"]:
        obs1, obs2 = obs2, obs1

    area1 = obs1.get("area_km2", 0.0)
    area2 = obs2.get("area_km2", 0.0)
    change = compute_percentage_change(area1, area2)

    if change["pct_change"] <= -20.0:
        interpretation = f"Significant lake area shrinkage ({change['pct_change']}%). Observed post-event reduction consistent with moraine breach / drainage event."
    elif change["pct_change"] >= 15.0:
        interpretation = f"Rapid surface area expansion observed ({change['pct_change']}%). Indicates accelerated glacial meltwater accumulation or moraine impoundment."
    else:
        interpretation = f"Moderate change ({change['pct_change']}%). Within standard seasonal fluctuation and sensor resolution margin."

    return {
        "lake_id": lake_id,
        "name": "South Lhonak Glacial Lake",
        "date_earlier": obs1["date"],
        "date_later": obs2["date"],
        "area_earlier_km2": area1,
        "area_later_km2": area2,
        "absolute_change_km2": change["delta_km2"],
        "percentage_change": change["pct_change"],
        "change_direction": change["direction"],
        "sensor_earlier": obs1.get("sensor", "Unknown"),
        "sensor_later": obs2.get("sensor", "Unknown"),
        "quality_notes": {
            "earlier": obs1.get("quality_flag"),
            "later": obs2.get("quality_flag")
        },
        "interpretation": interpretation,
        "scientific_disclaimer": "An observed lake-area change does not, by itself, prove an imminent GLOF or hazard trigger. Verification with local moraine stability and field sensors is required."
    }
