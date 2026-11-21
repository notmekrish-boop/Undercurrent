from fastapi import APIRouter, HTTPException
from typing import List
from ..services.data_service import data_service

router = APIRouter(prefix="/reservoirs", tags=["Reservoir Water-Spread Monitoring"])

@router.get("", summary="List monitored downstream reservoirs")
def get_reservoirs():
    return data_service.get_reservoirs()

@router.get("/{reservoir_id}", summary="Get details for a specific reservoir")
def get_reservoir_by_id(reservoir_id: str):
    res_list = data_service.get_reservoirs()
    for res in res_list:
        if res["id"] == reservoir_id or reservoir_id.lower() in res["name"].lower():
            return res
    raise HTTPException(status_code=404, detail=f"Reservoir '{reservoir_id}' not found.")

@router.get("/{reservoir_id}/history", summary="Get multi-date water-spread observations for a reservoir")
def get_reservoir_history(reservoir_id: str):
    history = data_service.get_reservoir_history(reservoir_id)
    if not history:
        raise HTTPException(status_code=404, detail=f"No history found for reservoir '{reservoir_id}'.")
    return {
        "reservoir_id": reservoir_id,
        "observations_count": len(history),
        "history": history,
        "scientific_disclaimer": "Crucial distinction: Reservoir surface area is an optical water-spread indicator, not a direct measurement of storage volume. Storage estimation requires bathymetry or calibrated elevation-area-capacity relationships."
    }
