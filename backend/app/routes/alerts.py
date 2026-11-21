from fastapi import APIRouter
from typing import List
from ..schemas.models import AlertFlag

router = APIRouter(prefix="/alerts", tags=["Rule-Based Anomaly & Screening Flags"])

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
