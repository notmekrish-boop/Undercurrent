"""
Data models and schemas for Project Undercurrent.
Conforms strictly to Section 8.5 and Section 12 of the Undercurrent Blueprint.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class StudyArea(BaseModel):
    id: str
    name: str
    basin: str
    region: str
    bbox: List[float]
    projected_crs: str
    elevation_range_m: List[int]
    description: str

class Observation(BaseModel):
    observation_id: str
    water_body_id: str
    name: str
    date: str
    period: Optional[str] = None
    season: Optional[str] = None
    sensor: str
    source: str
    spatial_res_m: Optional[float] = None
    cloud_cover_pct: Optional[float] = None
    method: str
    area_km2: float
    area_change_km2: Optional[float] = None
    area_change_pct: Optional[float] = None
    quality_flag: str
    label_note: Optional[str] = None
    color: Optional[str] = None

class WaterBody(BaseModel):
    id: str
    name: str
    type: str # 'glacial_lake' or 'reservoir'
    study_area_id: str
    latitude: float
    longitude: float
    elevation_m: int
    latest_area_km2: float
    status: str
    observations_count: int
    data_sources: List[str]

class LakeCompareResult(BaseModel):
    lake_id: str
    name: str
    date_earlier: str
    date_later: str
    area_earlier_km2: float
    area_later_km2: float
    absolute_change_km2: float
    percentage_change: float
    sensor_earlier: str
    sensor_later: str
    interpretation: str
    scientific_disclaimer: str

class ReservoirObservation(BaseModel):
    observation_id: str
    reservoir_id: str
    name: str
    date: str
    season: str
    sensor: str
    source: str
    water_spread_area_km2: float
    water_spread_change_pct: Optional[float] = None
    label_note: str = "Observed water-spread area only; not storage volume."
    quality_flag: str
    color: Optional[str] = None

class Asset(BaseModel):
    id: str
    name: str
    type: str # 'Settlement' or 'Infrastructure'
    category: str
    lon: float
    lat: float
    elevation_m: int
    distance_from_lake_km: float
    exposure_rating: str # 'Critical', 'High', 'Moderate'
    population_approx: int
    key_vulnerability: str
    status_notes: str

class ExposureProfilePoint(BaseModel):
    distance_km: float
    elevation_m: int
    slope_deg: float
    landmark: str
    zone: str

class ExposureSummary(BaseModel):
    corridor_id: str
    basin: str
    origin_lake: str
    total_corridor_length_km: float
    elevation_drop_m: int
    high_exposure_assets_count: int
    total_assets_screened: int
    terrain_slope_mean_deg: float
    methodology: str
    scientific_disclaimer: str

class AlertFlag(BaseModel):
    alert_id: str
    level: str # 'CRITICAL', 'WARNING', 'INFO'
    category: str
    target_name: str
    observation_date: str
    summary: str
    metrics: Dict[str, Any]
    evidence_fields: List[str]
    rule_applied: str
    confidence_level: str
    disclaimer: str

class EvidenceAdvisory(BaseModel):
    advisory_id: str
    timestamp_utc: str
    basin: str
    target_lake: str
    latest_observation: Dict[str, Any]
    downstream_corridor: Dict[str, Any]
    screened_assets: Dict[str, Any]
    independent_reservoir_track: Dict[str, Any]
    imagery_quality_and_confidence: Dict[str, Any]
    recommended_response: str
    scientific_safeguards: str

class NDWICalculationRequest(BaseModel):
    lake_id: str
    threshold: float = Field(0.14, ge=-1.0, le=1.0)
    grid_size: int = Field(24, ge=10, le=60)
    sensor: str = "Sentinel-2 MSI"

class NDWICalculationResult(BaseModel):
    lake_id: str
    threshold_used: float
    water_pixel_count: int
    total_pixel_count: int
    water_area_ratio: float
    calculated_area_km2: float
    sensor: str
    formula: str = "NDWI = (Green - NIR) / (Green + NIR)"
    matrix_grid: List[List[float]]
    classification_grid: List[List[int]]
