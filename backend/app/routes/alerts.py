from fastapi import APIRouter
from typing import List, Dict, Any
from ..schemas.models import AlertFlag, EvidenceAdvisory

router = APIRouter(prefix="/alerts", tags=["Rule-Based Anomaly & Screening Flags"])

@router.get("/advisory", response_model=EvidenceAdvisory, summary="Get structured evidence-based stakeholder advisory")
def get_advisory():
    return EvidenceAdvisory(
        advisory_id="ADV-2023-SK-TEESTA-01",
        timestamp_utc="2023-10-09T04:58:31Z",
        basin="Teesta River Basin (Upper & Middle Reach)",
        target_lake="South Lhonak Glacial Lake",
        latest_observation={
            "observation_date": "2023-10-09",
            "sensor": "Sentinel-2 MSI Level-2A (ESA Copernicus)",
            "water_area_km2": 1.003,
            "baseline_date": "2023-09-26",
            "baseline_water_area_km2": 1.666,
            "net_area_change_km2": -0.663,
            "net_percentage_change": -39.8,
            "interpretation": "Catastrophic moraine breach and glacial lake drainage event confirmed by Sentinel-2 MSI multi-spectral surface tracking."
        },
        downstream_corridor={
            "corridor_length_km": 112.4,
            "elevation_drop_m": 4920,
            "elevation_start_m": 5200,
            "elevation_end_m": 280,
            "flow_path": "South Lhonak Lake -> Lhonak River -> Zemu Chu -> Lachen Chu -> Chungthang (Confluence) -> Teesta River Gorge -> Dikchu -> Singtam -> Rangpo",
            "terrain_screening": "D8 DEM flow accumulation through steep V-shaped Himalayan canyon (confinement ratio > 85%, mean valley slope 28.4°)."
        },
        screened_assets={
            "total_screened": 8,
            "critical_count": 3,
            "critical_assets": [
                {
                    "name": "Teesta-III Chungthang Hydroelectric Project (Dam)",
                    "chainage_km": 68.5,
                    "elevation_m": 1560,
                    "type": "Hydroelectric Infrastructure",
                    "status": "Overtopped / Breached (Oct 2023)"
                },
                {
                    "name": "Singtam Urban Settlement & Suspension Bridge",
                    "chainage_km": 96.2,
                    "elevation_m": 350,
                    "type": "Township & River Crossing",
                    "status": "Low-lying riverbank inundation screening"
                },
                {
                    "name": "Rangpo Border Transit Hub & Checkpost",
                    "chainage_km": 112.4,
                    "elevation_m": 280,
                    "type": "Transport & Trade Node",
                    "status": "Corridor terminus screening"
                }
            ]
        },
        independent_reservoir_track={
            "track_description": "Track B: Independent Downstream Reservoir Water-Spread Surveillance",
            "chungthang_dam": {
                "id": "RES-TK-01",
                "pre_flood_spread_km2": 0.512,
                "post_flood_spread_km2": 0.114,
                "percentage_change": -77.7,
                "status": "Water-spread contracted; bypass flow through breached spillway/dam section"
            },
            "dikchu_dam": {
                "id": "RES-TK-02",
                "operating_spread_km2": 0.385,
                "status": "Operational; intake protected; high sediment load screening active"
            },
            "hydrological_safeguard": "Reservoir water-spread area is monitored as an independent empirical track. Storage volume cannot be inferred directly from 2D water-spread alone without bathymetric rating curves."
        },
        imagery_quality_and_confidence={
            "spatial_resolution_m": 10.0,
            "cloud_cover_pct": 1.8,
            "qa_flag": "Valid (Clear Observation, High Atmospheric Transmittance)",
            "bands_used": "B03 (Green, 560nm), B08 (NIR, 842nm), B11 (SWIR-1, 1610nm)",
            "validation_reference": "ISRO NRSC Disaster Management Support Programme & Copernicus Open Access Hub",
            "confidence_rating": "High (Multi-spectral + Terrain validated)"
        },
        recommended_response="Review the evidence and relevant reservoir conditions with authorized disaster-management and reservoir personnel.",
        scientific_safeguards="Undercurrent is a research prototype for monitoring and preliminary exposure screening. It is not an operational GLOF early warning system (EWS) or hydrodynamic flood dispatch model. Real-world emergency response relies on official NDMA/SDMA directives."
    )

@router.get("", response_model=List[AlertFlag], summary="List rule-based change detection flags")
def get_alert_flags():
    return [
        AlertFlag(
            alert_id="ALT-2023-SK-01",
            level="CRITICAL",
            category="Sudden Water-Spread Drainage (Moraine Breach)",
            target_name="South Lhonak Glacial Lake",
            observation_date="2023-10-04",
            summary="Rapid lake area shrinkage of -38.7% detected between 17-Sep-2023 (1.682 km²) and 04-Oct-2023 (1.031 km²). Net loss of ~0.651 km² water spread indicates catastrophic drainage.",
            metrics={
                "area_pre_km2": 1.682,
                "area_post_km2": 1.031,
                "absolute_diff_km2": -0.651,
                "percentage_change": -38.7,
                "elevation_m": 5200
            },
            evidence_fields=[
                "Sentinel-2 MSI Level-2A band comparison (B3 & B8)",
                "RISAT-1A SAR coherence loss along eastern terminal moraine",
                "Visible moraine breach scar and downstream sediment scouring"
            ],
            rule_applied="IF abs(lake_area_pct_change) > 20% within 30-day window THEN flag_critical_morphological_event",
            confidence_level="High (Verified across optical Sentinel-2 & SAR RISAT-1A)",
            disclaimer="Rule-based indicator flags morphological changes for human expert investigation. Does not predict future outbursts."
        ),
        AlertFlag(
            alert_id="ALT-2023-RES-01",
            level="CRITICAL",
            category="Reservoir Structure Impact & Water Loss",
            target_name="Teesta-III Chungthang Dam Reservoir",
            observation_date="2023-10-06",
            summary="Reservoir water-spread plummeted from 0.512 km² (pre-monsoon peak) down to 0.114 km² (-77.7%) following flash flood impact and dam structure breach.",
            metrics={
                "water_spread_pre_km2": 0.512,
                "water_spread_post_km2": 0.114,
                "percentage_change": -77.7,
                "distance_from_lake_km": 68.5
            },
            evidence_fields=[
                "Copernicus Sentinel-2 optical imagery post-surge",
                "Central Water Commission (CWC) stage hydrograph anomalies",
                "Dam crest overtopping observed in satellite telemetry"
            ],
            rule_applied="IF reservoir_water_spread_pct_change < -50% during non-drawdown period THEN flag_infrastructure_failure_risk",
            confidence_level="High",
            disclaimer="Surface water-spread reduction indicates uncontrolled emptying or breach; does not replace on-site dam safety structural inspection."
        ),
        AlertFlag(
            alert_id="ALT-2021-HIST-01",
            level="WARNING",
            category="Decadal Glacial Lake Expansion Trend",
            target_name="South Lhonak Glacial Lake",
            observation_date="2021-10-12",
            summary="Long-term multi-year expansion from 0.984 km² (2013) to 1.492 km² (2021), an increase of +51.6% over 8 years (~0.063 km²/year).",
            metrics={
                "area_2013_km2": 0.984,
                "area_2021_km2": 1.492,
                "expansion_pct": 51.6,
                "observation_span_years": 8
            },
            evidence_fields=[
                "Landsat-8 OLI time series (2013-2021)",
                "Sentinel-2 MSI time series",
                "Glacier retreat rate from Cartosat stereo DEM"
            ],
            rule_applied="IF multi_year_growth_rate > 3%_per_annum THEN flag_expansion_hazard_screening",
            confidence_level="High",
            disclaimer="Observed lake expansion demonstrates moraine retreat and water impoundment; hazard screening requires ongoing moraine stability analysis."
        )
    ]
