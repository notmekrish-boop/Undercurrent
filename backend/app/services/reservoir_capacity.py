"""
Reservoir GLOF Holding Capacity & Controlled Drawdown Calculation Service.
Project Undercurrent: Decision-support screening for downstream reservoir retention buffer,
drawdown requirements, and emergency spillway discharge during glacial lake outbursts.
"""

from typing import Dict, Any
from ..schemas.models import ReservoirCapacityCheckRequest, ReservoirCapacityCheckResult

RESERVOIR_PRESETS: Dict[str, Dict[str, Any]] = {
    "RES-TK-01": {
        "id": "RES-TK-01",
        "name": "Teesta-III Chungthang Dam",
        "river": "Teesta River (Lachen Chu - Lachung Chu confluence)",
        "dam_type": "Concrete Face Rockfill Dam (CFRD)",
        "distance_from_lake_km": 68.5,
        "elevation_masl": 1560.0,
        "max_capacity_mcm": 6.30,  # Gross Storage at FRL (1560m)
        "dead_storage_mcm": 1.22,  # MDDL storage (1530m)
        "current_storage_mcm": 5.08, # ~81% Full / Pre-event live storage
        "spillway_capacity_cumecs": 7000.0,
        "default_lead_time_hours": 3.5,
        "default_surge_mcm": 45.0, # Estimated South Lhonak Oct 2023 Outburst
        "historical_note": (
            "During the 4 Oct 2023 disaster, South Lhonak lake released an estimated 40-50 MCM of water and debris. "
            "Chungthang Dam had a total gross capacity of only 6.30 MCM. The incoming outburst was >7x the dam's total "
            "storage capacity, causing rapid crest overtopping and failure."
        )
    },
    "RES-TK-02": {
        "id": "RES-TK-02",
        "name": "Teesta-V NHPC Dam (Dikchu)",
        "river": "Teesta River (Dikchu, East Sikkim)",
        "dam_type": "Concrete Gravity Dam",
        "distance_from_lake_km": 86.0,
        "elevation_masl": 650.0,
        "max_capacity_mcm": 13.25, # Gross storage at FRL (579m)
        "dead_storage_mcm": 8.15,  # MDDL storage (568m)
        "current_storage_mcm": 11.20, # ~85% Full
        "spillway_capacity_cumecs": 9500.0,
        "default_lead_time_hours": 5.5,
        "default_surge_mcm": 20.0, # Attenuated downstream surge
        "historical_note": (
            "Dikchu Dam (Teesta-V) is situated ~18 km downstream of Chungthang. "
            "It experienced high siltation and inundation during the 2023 flood wave."
        )
    }
}


def evaluate_reservoir_holding_capacity(req: ReservoirCapacityCheckRequest) -> ReservoirCapacityCheckResult:
    """
    Evaluates whether a downstream reservoir has sufficient holding capacity for an incoming
    GLOF surge volume, and computes the exact pre-release drawdown volume and discharge rate needed.
    """
    v_max = round(float(req.max_capacity_mcm), 3)
    v_dead = round(float(req.dead_storage_mcm), 3)
    v_curr = round(float(req.current_storage_mcm), 3)
    v_surge = round(float(req.estimated_glof_volume_mcm), 3)
    t_lead = max(0.1, round(float(req.lead_time_hours), 2))
    q_spill_max = round(float(req.spillway_capacity_cumecs), 1)

    # Sanity bounds
    v_curr = min(v_max, max(0.0, v_curr))
    v_dead = min(v_curr, max(0.0, v_dead))

    # Available freeboard retention storage in current state
    current_buffer = round(max(0.0, v_max - v_curr), 3)

    # Maximum possible buffer if drawn down completely to MDDL (Dead Storage Level)
    max_possible_buffer = round(max(0.0, v_max - v_dead), 3)

    # Deficit under current conditions
    holding_deficit = round(max(0.0, v_surge - current_buffer), 3)

    # Case 1: Current buffer is sufficient
    if current_buffer >= v_surge:
        has_sufficient_capacity = True
        capacity_status = "SUFFICIENT_BUFFER"
        water_release_required = 0.0
        can_fully_contain = True
        uncontainable_excess = 0.0
        target_storage = v_curr
        req_discharge_cumecs = 0.0
        is_discharge_feasible = True

        op_rec = (
            f"SUFFICIENT RETENTION BUFFER AVAILABLE: The reservoir currently has {current_buffer:.2f} Million m³ (MCM) "
            f"of free retention buffer, which is sufficient to absorb the estimated {v_surge:.2f} MCM GLOF surge without "
            f"exceeding Full Reservoir Level (FRL). No pre-emptive emergency water release is required."
        )
        risk_narrative = (
            f"The reservoir can safely attenuate and hold the incoming flood surge within its existing freeboard margin. "
            f"Monitor upstream river stage hydrographs and maintain spillway gates on standby."
        )

    # Case 2: Insufficient buffer currently, but can be fully contained if drawn down before arrival
    elif v_surge <= max_possible_buffer:
        has_sufficient_capacity = False
        capacity_status = "DRAWDOWN_REQUIRED"
        water_release_required = round(v_surge - current_buffer, 3)
        can_fully_contain = True
        uncontainable_excess = 0.0
        target_storage = round(max(v_dead, v_max - v_surge), 3)

        # Pre-release discharge calculation: ΔV (m³) / Δt (seconds)
        volume_m3 = water_release_required * 1_000_000.0
        seconds_available = t_lead * 3600.0
        req_discharge_cumecs = round(volume_m3 / seconds_available, 1)
        is_discharge_feasible = req_discharge_cumecs <= q_spill_max

        feasibility_text = (
            f"Achievable within design spillway capacity ({q_spill_max:.0f} m³/s)."
            if is_discharge_feasible else
            f"WARNING: Exceeds design spillway capacity of {q_spill_max:.0f} m³/s! Drawdown cannot be completed in {t_lead} hours."
        )

        op_rec = (
            f"CONTROLLED DRAWDOWN REQUIRED: The reservoir has an immediate holding deficit of {holding_deficit:.2f} MCM. "
            f"Pre-emptively release {water_release_required:.2f} MCM of stored water over the {t_lead:.1f} hour lead time "
            f"at an average spillway discharge of {req_discharge_cumecs:.1f} m³/s (cumecs) to draw down storage to "
            f"{target_storage:.2f} MCM ({round(target_storage / v_max * 100, 1)}% FRL). "
            f"This creates sufficient retention buffer to contain the {v_surge:.2f} MCM GLOF wave. {feasibility_text}"
        )
        risk_narrative = (
            f"Controlled pre-release creates the necessary {v_surge:.2f} MCM flood retention pocket. "
            f"Downstream settlements between dam and next cascade should be alerted to pre-release discharge rate of "
            f"{req_discharge_cumecs:.1f} m³/s."
        )

    # Case 3: GLOF surge exceeds TOTAL active storage capacity of the reservoir
    else:
        has_sufficient_capacity = False
        capacity_status = "CAPACITY_EXCEEDED"
        can_fully_contain = False
        uncontainable_excess = round(v_surge - max_possible_buffer, 3)
        # Maximum drawdown release possible is draining all water above MDDL
        water_release_required = round(max(0.0, v_curr - v_dead), 3)
        target_storage = v_dead

        # Pre-release discharge rate to reach MDDL
        volume_m3 = water_release_required * 1_000_000.0
        seconds_available = t_lead * 3600.0
        req_discharge_cumecs = round(volume_m3 / seconds_available, 1) if seconds_available > 0 else 0.0
        is_discharge_feasible = req_discharge_cumecs <= q_spill_max

        op_rec = (
            f"SURGE EXCEEDS TOTAL RESERVOIR RETENTION CAPACITY: The incoming GLOF volume ({v_surge:.2f} MCM) "
            f"exceeds the reservoir's entire active retention volume ({max_possible_buffer:.2f} MCM) by "
            f"{uncontainable_excess:.2f} MCM. Even if drawn down completely to empty / MDDL ({v_dead:.2f} MCM), "
            f"the reservoir CANNOT contain this flood. "
            f"MANDATORY OPERATIONAL PROTOCOL: Pre-release {water_release_required:.2f} MCM immediately at "
            f"{req_discharge_cumecs:.1f} m³/s to maximize flood attenuation storage, AND configure spillways "
            f"for MAXIMUM CONTROLLED PASS-THROUGH DISCHARGE (up to {q_spill_max:.0f} m³/s) to prevent dam crest overtopping."
        )
        risk_narrative = (
            f"Physical Analogy: In the 4 October 2023 disaster, Teesta-III Chungthang Dam (gross capacity 6.3 MCM, "
            f"live storage 5.08 MCM) was struck by an estimated 40-50 MCM outburst surge from South Lhonak. "
            f"Because the surge was ~8x greater than the reservoir's total containment volume, the reservoir was "
            f"overwhelmed and overtopped within minutes, causing structural breach. Run-of-the-river dams cannot store "
            f"catastrophic glacial outbursts; early warning must trigger maximum emergency spillway opening."
        )

    res_name = req.reservoir_name or req.reservoir_id
    if req.reservoir_id in RESERVOIR_PRESETS:
        res_name = RESERVOIR_PRESETS[req.reservoir_id]["name"]

    return ReservoirCapacityCheckResult(
        reservoir_id=req.reservoir_id,
        reservoir_name=res_name,
        max_capacity_mcm=v_max,
        dead_storage_mcm=v_dead,
        current_storage_mcm=v_curr,
        current_buffer_mcm=current_buffer,
        max_possible_buffer_mcm=max_possible_buffer,
        estimated_glof_volume_mcm=v_surge,
        lead_time_hours=t_lead,
        has_sufficient_holding_capacity=has_sufficient_capacity,
        capacity_status=capacity_status,
        holding_deficit_mcm=holding_deficit,
        water_release_required_mcm=water_release_required,
        can_fully_contain_if_drawn_down=can_fully_contain,
        uncontainable_excess_volume_mcm=uncontainable_excess,
        target_storage_mcm=target_storage,
        required_discharge_rate_cumecs=req_discharge_cumecs,
        spillway_capacity_cumecs=q_spill_max,
        is_discharge_rate_feasible=is_discharge_feasible,
        operational_recommendation=op_rec,
        risk_narrative=risk_narrative,
        scientific_safeguards=(
            "Decision-Support Safeguards: Project Undercurrent provides indicative hydrodynamic and storage screening. "
            "Reservoir storage capacity, spillway gate dispatch, and controlled drawdown operations are strictly governed "
            "by Central Water Commission (CWC), dam safety authorities, and SDMA under the Dam Safety Act 2021. "
            "Optical 2D water-spread is not equivalent to 3D storage volume without surveyed elevation-area-capacity curves."
        )
    )
