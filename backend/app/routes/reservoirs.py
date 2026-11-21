from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from ..services.data_service import data_service
from ..schemas.models import ReservoirCapacityCheckRequest, ReservoirCapacityCheckResult
from ..services.reservoir_capacity import RESERVOIR_PRESETS, evaluate_reservoir_holding_capacity

router = APIRouter(prefix="/reservoirs", tags=["Reservoir Water-Spread & GLOF Holding Capacity"])

@router.get("", summary="List monitored downstream reservoirs")
def get_reservoirs():
    return data_service.get_reservoirs()

@router.get("/presets", summary="Get standard engineering and capacity presets for cascade reservoirs")
def get_reservoir_presets():
    return {
        "presets": RESERVOIR_PRESETS,
        "scientific_disclaimer": "Presets derived from CWC/NHPC dam design reports and published Teesta-III/V hydrological records."
    }

@router.post("/capacity-check", response_model=ReservoirCapacityCheckResult, summary="Assess reservoir holding capacity and calculate required pre-release drawdown for incoming GLOF")
def check_reservoir_capacity(req: ReservoirCapacityCheckRequest):
    return evaluate_reservoir_holding_capacity(req)

@router.post("/{reservoir_id}/capacity-check", response_model=ReservoirCapacityCheckResult, summary="Assess reservoir holding capacity for a specific reservoir ID")
def check_reservoir_capacity_by_id(reservoir_id: str, req: ReservoirCapacityCheckRequest):
    req_dict = req.model_dump()
    req_dict["reservoir_id"] = reservoir_id
    if reservoir_id in RESERVOIR_PRESETS:
        preset = RESERVOIR_PRESETS[reservoir_id]
        if not req.reservoir_name or req.reservoir_name == "Teesta-III Chungthang Dam":
            req_dict["reservoir_name"] = preset["name"]
    updated_req = ReservoirCapacityCheckRequest(**req_dict)
    return evaluate_reservoir_holding_capacity(updated_req)

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
