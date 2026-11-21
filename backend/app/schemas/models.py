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
    review_status: str = "Awaiting Human Expert Review"
    review_authority: str = "Sikkim SDMA / NDMA Glacial Risk Cell"
    can_elevate_to_public: bool = False

class HumanReviewSubmission(BaseModel):
    reviewer_name: str
    organization: str
    review_decision: str # "ENDORSED_FOR_INTERNAL_ACTION", "REQUEST_GROUND_CONFIRMATION", "REJECTED_FALSE_ALARM"
    technical_comments: str

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

class GlacierLakeObservationInput(BaseModel):
    date: str
    area_km2: float = Field(..., gt=0.0, description="Measured or extracted lake surface area in km²")
    sensor: Optional[str] = "Sentinel-2 MSI Level-2A"
    source: Optional[str] = "Satellite Observation Feed"
    water_pixel_count: Optional[int] = None
    spatial_res_m: Optional[float] = 10.0

class GlacierLakeRiskAssessmentRequest(BaseModel):
    lake_id: Optional[str] = "GL-CUSTOM-01"
    lake_name: str = Field(..., description="Name of the glacial lake")
    basin: Optional[str] = "Himalayan Basin"
    elevation_masl: Optional[float] = Field(5200.0, ge=1000.0, le=8000.0, description="Lake elevation in meters ASL")
    observations: List[GlacierLakeObservationInput] = Field(..., min_length=2, description="At least two dated observations for multi-temporal analysis")
    downstream_distance_km: Optional[float] = Field(50.0, ge=1.0, le=300.0, description="Distance along river corridor to nearest critical infrastructure")
    channel_slope_deg: Optional[float] = Field(20.0, ge=0.5, le=60.0, description="Average downstream channel gradient in degrees")
    dam_type: Optional[str] = Field("Moraine-dammed", description="Dam type: Moraine-dammed, Ice-dammed, or Bedrock")

class GlacierLakeRiskAssessmentResult(BaseModel):
    lake_id: str
    lake_name: str
    basin: str
    elevation_masl: float
    dam_type: str
    temporal_metrics: Dict[str, Any]
    hazard_classification: Dict[str, Any]
    downstream_screening: Dict[str, Any]
    recommended_response: str
    scientific_safeguards: str

class ReservoirCapacityCheckRequest(BaseModel):
    reservoir_id: str = Field("RES-TK-01", description="Reservoir identifier or preset")
    reservoir_name: Optional[str] = Field("Teesta-III Chungthang Dam", description="Name of dam or reservoir")
    max_capacity_mcm: float = Field(6.30, gt=0.0, description="Gross storage capacity at Full Reservoir Level (FRL) in Million m³ (MCM)")
    dead_storage_mcm: float = Field(1.22, ge=0.0, description="Dead storage capacity at Minimum Drawdown Level (MDDL) in Million m³ (MCM)")
    current_storage_mcm: float = Field(5.08, ge=0.0, description="Current impounded water storage in Million m³ (MCM)")
    spillway_capacity_cumecs: float = Field(7000.0, gt=0.0, description="Design spillway discharge capacity in m³/s (cumecs)")
    estimated_glof_volume_mcm: float = Field(45.0, gt=0.0, description="Estimated incoming GLOF outburst surge volume in Million m³ (MCM)")
    lead_time_hours: float = Field(3.5, gt=0.05, le=72.0, description="Flood wave travel time from lake breach to reservoir arrival in hours")

class ReservoirCapacityCheckResult(BaseModel):
    reservoir_id: str
    reservoir_name: str
    max_capacity_mcm: float
    dead_storage_mcm: float
    current_storage_mcm: float
    current_buffer_mcm: float
    max_possible_buffer_mcm: float
    estimated_glof_volume_mcm: float
    lead_time_hours: float
    has_sufficient_holding_capacity: bool
    capacity_status: str
    holding_deficit_mcm: float
    water_release_required_mcm: float
    can_fully_contain_if_drawn_down: bool
    uncontainable_excess_volume_mcm: float
    target_storage_mcm: float
    required_discharge_rate_cumecs: float
    spillway_capacity_cumecs: float
    is_discharge_rate_feasible: bool
    operational_recommendation: str
    risk_narrative: str
    scientific_safeguards: str
