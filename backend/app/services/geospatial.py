"""
Geospatial calculation engine for Project Undercurrent.
Performs accurate distance measurements, percentage change calculations,
and multi-factor exposure scoring without opaque black boxes.
"""

import math
from typing import Dict, Any, List

def calculate_haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Haversine formula to compute great-circle distance between two points on Earth."""
    R = 6371.0 # Earth mean radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 3)

def compute_percentage_change(area_earlier: float, area_later: float) -> Dict[str, Any]:
    """
    Percentage area change formula per Section 7.2 of Undercurrent Blueprint:
    Percentage area change = ((A_later - A_earlier) / A_earlier) * 100
    """
    if area_earlier <= 0:
        return {"delta_km2": 0.0, "pct_change": 0.0, "direction": "Neutral"}
    delta = area_later - area_earlier
    pct = (delta / area_earlier) * 100.0
    direction = "Expansion" if delta > 0.001 else ("Reduction" if delta < -0.001 else "Stable")
    return {
        "delta_km2": round(delta, 4),
        "pct_change": round(pct, 2),
        "direction": direction
    }

def evaluate_exposure_score(
    distance_km: float,
    elevation_drop_m: float,
    slope_deg: float,
    asset_type: str,
    population: int
) -> Dict[str, Any]:
    """
    Transparent Multi-Factor Exposure Indicator (Section 7.7 compliance).
    Zero black-box 'AI risk score'. Every weight and contributing component is explicitly returned.
    
    Components:
    1. Proximity factor (closer to source lake along gorge => higher exposure) [Weight 0.35]
    2. Relief gradient factor (steep narrow slopes upstream accelerate flow) [Weight 0.25]
    3. Asset critical vulnerability (settlements / dams / highways) [Weight 0.25]
    4. Population / infrastructure exposure footprint [Weight 0.15]
    """
    # Proximity: 1.0 at 0km down to 0.1 at 120km
    prox_score = max(0.1, min(1.0, 1.0 - (distance_km / 120.0)))
    
    # Relief gradient: high slope (> 25 deg) gives maximum confinement factor
    slope_factor = min(1.0, max(0.2, slope_deg / 40.0))
    
    # Criticality
    if asset_type == "Infrastructure":
        crit_score = 0.95
    elif population > 3000:
        crit_score = 0.85
    else:
        crit_score = 0.60

    # Pop scale
    pop_score = min(1.0, max(0.1, math.log10(max(10, population)) / 4.5))

    composite = (prox_score * 0.35) + (slope_factor * 0.25) + (crit_score * 0.25) + (pop_score * 0.15)
    
    rating = "Critical" if composite >= 0.75 else ("High" if composite >= 0.55 else "Moderate")
    
    return {
        "composite_exposure_index": round(composite * 100.0, 1),
        "rating": rating,
        "weights": {
            "proximity_to_hazard_source": 0.35,
            "valley_gradient_confinement": 0.25,
            "asset_criticality": 0.25,
            "population_footprint": 0.15
        },
        "breakdown": {
            "proximity_score": round(prox_score * 100, 1),
            "slope_confinement_score": round(slope_factor * 100, 1),
            "criticality_score": round(crit_score * 100, 1),
            "population_factor_score": round(pop_score * 100, 1)
        },
        "disclaimer": "Preliminary geometric/topographic screening indicator only. Does not compute hydrodynamic velocity or inundation wave height."
    }
