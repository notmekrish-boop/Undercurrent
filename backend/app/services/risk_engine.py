"""
Glacial Lake Multi-Date Risk Assessment Engine for Project Undercurrent.

Implements scientific multi-temporal analysis and hazard scoring per ICIMOD, CWC,
and Reynolds/GAPHAZ glacial hazard frameworks:
1. Multi-date area velocity analysis (expansion vs catastrophic drainage).
2. Moraine breach / piping detection (>20% loss within rapid window).
3. Downstream terrain exposure routing (channel slope, proximity attenuation, dam type).
4. Actionable decision-support recommendations with strict scientific safeguards.
"""

import math
from datetime import datetime
from typing import Dict, Any, List
from ..schemas.models import (
    GlacierLakeRiskAssessmentRequest,
    GlacierLakeRiskAssessmentResult
)


def calculate_glacier_lake_risk(req: GlacierLakeRiskAssessmentRequest) -> GlacierLakeRiskAssessmentResult:
    # 1. Sort observations chronologically
    sorted_obs = sorted(req.observations, key=lambda o: o.date)
    obs_earliest = sorted_obs[0]
    obs_latest = sorted_obs[-1]

    d_earliest = datetime.strptime(obs_earliest.date, "%Y-%m-%d")
    d_latest = datetime.strptime(obs_latest.date, "%Y-%m-%d")
    elapsed_days = max(1, (d_latest - d_earliest).days)

    area_base = obs_earliest.area_km2
    area_latest = obs_latest.area_km2
    delta_area_km2 = round(area_latest - area_base, 4)
    pct_change = round((delta_area_km2 / area_base) * 100.0, 2) if area_base > 0 else 0.0

    # Annualized expansion or shrinkage rate
    annualized_rate_pct = round((pct_change / elapsed_days) * 365.25, 2)
    daily_change_m2 = round((delta_area_km2 * 1_000_000.0) / elapsed_days, 1)

    # 2. Scientific Hazard Classification Logic
    # Case A: Rapid Sudden Drainage (Moraine Breach / Subsurface Piping Outburst)
    if pct_change <= -20.0 and elapsed_days <= 90:
        risk_tier = "CRITICAL"
        hazard_label = "CRITICAL MORAINE BREACH OUTFLOW"
        primary_trigger = (
            f"Catastrophic rapid drainage detected: {abs(pct_change):.1f}% surface water loss "
            f"({abs(delta_area_km2):.3f} km²) within {elapsed_days} days, indicating structural moraine dam failure."
        )
        base_hazard_score = min(100.0, 85.0 + (abs(pct_change) - 20.0) * 0.75)
        recommended_action = (
            "EMERGENCY PROTOCOL: Immediately verify breach scar with SAR/optical imagery; "
            "alert downstream hydropower authorities (dam spillway gates) and civil defense (NDMA/SDMA) for valley corridor inspection."
        )

    # Case B: Significant drainage over longer time or moderate drainage
    elif pct_change <= -10.0:
        risk_tier = "HIGH"
        hazard_label = "SIGNIFICANT DRAINAGE / BREACH WARNING"
        primary_trigger = (
            f"Substantial lake contraction: {abs(pct_change):.1f}% loss over {elapsed_days} days. "
            "Requires immediate investigation for subsurface seepage or moraine piping."
        )
        base_hazard_score = min(84.0, 70.0 + (abs(pct_change) - 10.0) * 1.4)
        recommended_action = (
            "HIGH PRIORITY: Dispatch ground/aerial reconnaissance to inspect terminal moraine stability and monitor river stage gauges downstream."
        )

    # Case C: Accelerated Glacial Melt Expansion
    elif pct_change > 0:
        if (annualized_rate_pct >= 15.0 or pct_change >= 25.0) and area_latest >= 0.5:
            risk_tier = "HIGH"
            hazard_label = "ACCELERATED MELTWATER EXPANSION HAZARD"
            primary_trigger = (
                f"Rapid glacial lake growth: {pct_change:.1f}% expansion ({annualized_rate_pct:.1f}%/yr) "
                f"impounding {area_latest:.2f} km² behind high-altitude moraine."
            )
            base_hazard_score = min(85.0, 70.0 + min(15.0, annualized_rate_pct * 0.5))
            recommended_action = (
                "ACTIONABLE SURVEILLANCE: Place lake on high-priority Sentinel-2/Landsat monitoring cadence; "
                "conduct bathymetric depth survey and assess moraine freeboard margin."
            )
        elif annualized_rate_pct >= 5.0 or pct_change >= 10.0:
            risk_tier = "MODERATE"
            hazard_label = "STEADY EXPANSION SCREENING"
            primary_trigger = (
                f"Steady post-monsoon meltwater growth: {pct_change:.1f}% over {elapsed_days} days "
                f"({annualized_rate_pct:.1f}%/yr). Standard glacial retreat expansion."
            )
            base_hazard_score = min(69.0, 45.0 + min(24.0, annualized_rate_pct * 1.5))
            recommended_action = (
                "ROUTINE MONITORING: Re-assess lake perimeter post-monsoon and maintain seasonal satellite tracking records."
            )
        else:
            risk_tier = "LOW"
            hazard_label = "STABLE GLACIAL BASELINE"
            primary_trigger = (
                f"Minimal area variance (+{pct_change:.1f}%): Lake surface extent is within normal seasonal equilibrium."
            )
            base_hazard_score = max(10.0, 20.0 + annualized_rate_pct * 2.0)
            recommended_action = "Standard baseline surveillance; no immediate intervention required."

    # Case D: Slight fluctuation (-10% to 0%)
    else:
        risk_tier = "LOW"
        hazard_label = "STABLE / SEASONAL RETREAT BASELINE"
        primary_trigger = (
            f"Minor surface contraction ({pct_change:.1f}%): Attributable to seasonal evaporation, winter freezing, or sediment settling."
        )
        base_hazard_score = max(10.0, 25.0 + abs(pct_change))
        recommended_action = "Maintain regular satellite catalogue records."

    # 3. Downstream Terrain & Confinement Exposure Calculation
    slope_val = req.channel_slope_deg or 20.0
    dist_val = req.downstream_distance_km or 50.0
    dam_type_str = req.dam_type or "Moraine-dammed"

    slope_factor = min(1.0, max(0.2, slope_val / 35.0))
    dist_factor = min(1.0, max(0.1, 1.0 - (dist_val / 120.0)))
    dam_multiplier = 1.0 if "moraine" in dam_type_str.lower() else (0.85 if "ice" in dam_type_str.lower() else 0.6)

    terrain_confinement = "High Gorge Confinement (Steep V-shaped canyon, rapid surge propagation)" if slope_val >= 15.0 else "Moderate Valley Confinement"
    
    # Composite vulnerability score (0 - 100)
    composite_score = round(
        min(100.0, (base_hazard_score * 0.65) + (slope_factor * 18.0 * dam_multiplier) + (dist_factor * 17.0 * dam_multiplier)),
        1
    )

    temporal_metrics = {
        "baseline_observation": {
            "date": obs_earliest.date,
            "area_km2": area_base,
            "sensor": obs_earliest.sensor,
            "source": obs_earliest.source
        },
        "latest_observation": {
            "date": obs_latest.date,
            "area_km2": area_latest,
            "sensor": obs_latest.sensor,
            "source": obs_latest.source
        },
        "total_observations_evaluated": len(sorted_obs),
        "elapsed_days": elapsed_days,
        "delta_area_km2": delta_area_km2,
        "percentage_change": pct_change,
        "annualized_rate_pct_per_year": annualized_rate_pct,
        "daily_area_change_rate_m2_per_day": daily_change_m2
    }

    hazard_classification = {
        "risk_tier": risk_tier,
        "hazard_score_0_to_100": composite_score,
        "base_hazard_score": round(base_hazard_score, 1),
        "hazard_label": hazard_label,
        "primary_trigger": primary_trigger,
        "governing_rule": (
            "IF abs(lake_area_pct_change) > 20% in <= 90 days THEN CRITICAL_BREACH_OUTFLOW; "
            "ELSE IF annual_growth > 15% and area > 0.5 km² THEN HIGH_EXPANSION_GLOF; "
            "ELSE IF annual_growth >= 5% THEN MODERATE_SCREENING; ELSE LOW_BASELINE."
        )
    }

    downstream_screening = {
        "elevation_masl": req.elevation_masl,
        "downstream_distance_km": dist_val,
        "channel_slope_deg": slope_val,
        "dam_type": dam_type_str,
        "terrain_confinement": terrain_confinement,
        "proximity_attenuation_factor": round(dist_factor, 2),
        "slope_acceleration_factor": round(slope_factor, 2),
        "dam_vulnerability_multiplier": dam_multiplier
    }

    return GlacierLakeRiskAssessmentResult(
        lake_id=req.lake_id or "GL-CUSTOM-01",
        lake_name=req.lake_name,
        basin=req.basin or "Himalayan Basin",
        elevation_masl=req.elevation_masl or 5200.0,
        dam_type=dam_type_str,
        temporal_metrics=temporal_metrics,
        hazard_classification=hazard_classification,
        downstream_screening=downstream_screening,
        recommended_response=recommended_action,
        scientific_safeguards=(
            "Undercurrent is a decision-support prototype for remote sensing screening and multi-temporal lake tracking. "
            "Planar 2D area delta is not equivalent to 3D water volume without bathymetry. "
            "Heuristic exposure scoring does not replace 2D hydrodynamic inundation routing (HEC-RAS/BASEMENT) "
            "or official emergency evacuation directives by national disaster management authorities (NDMA/SDMA)."
        )
    )
