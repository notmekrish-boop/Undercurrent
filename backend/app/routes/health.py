from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "online",
        "project": "Undercurrent",
        "description": "Himalayan Water Intelligence & Glacial Risk Monitoring System",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "basin_monitored": "Teesta River Basin (Sikkim)",
        "modules_active": {
            "glacial_lake_monitor": True,
            "reservoir_water_spread": True,
            "downstream_exposure_screening": True,
            "ndwi_analysis_engine": True
        }
    }
