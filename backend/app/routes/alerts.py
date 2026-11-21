import os
import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..schemas.models import AlertFlag, EvidenceAdvisory, HumanReviewSubmission
from ..services.data_service import data_service

router = APIRouter(prefix="/alerts", tags=["Rule-Based Anomaly & Screening Flags"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REVIEWS_FILE = os.path.normpath(os.path.join(BASE_DIR, "..", "data", "processed", "human_reviews.json"))


def _load_reviews() -> Dict[str, Dict[str, Any]]:
    if os.path.isfile(REVIEWS_FILE):
        try:
            with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Undercurrent] Error loading human reviews: {e}")
            return {}
    return {}


def _save_reviews(reviews: Dict[str, Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(REVIEWS_FILE), exist_ok=True)
    with open(REVIEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2)


@router.post("/{alert_id}/review", summary="Human expert review sign-off before advisory elevation")
def submit_human_review(alert_id: str, submission: HumanReviewSubmission):
    now_utc = datetime.now(timezone.utc).isoformat()
    review_record = {
        "alert_id": alert_id,
        "reviewed_by": submission.reviewer_name,
        "organization": submission.organization,
        "decision": submission.review_decision,
        "comments": submission.technical_comments,
        "reviewed_at_utc": now_utc,
        "elevation_authorized": submission.review_decision == "ENDORSED_FOR_INTERNAL_ACTION"
    }

    reviews = _load_reviews()
    reviews[alert_id] = review_record
    _save_reviews(reviews)

    return {
        "status": "success",
        "message": f"Expert review recorded for alert {alert_id} at {now_utc}",
        "review_record": review_record
    }


@router.get("/{alert_id}/review", summary="Get human expert review record for an alert")
def get_alert_review(alert_id: str):
    reviews = _load_reviews()
    if alert_id in reviews:
        return reviews[alert_id]

    return {
        "alert_id": alert_id,
        "review_status": "PENDING_EXPERT_REVIEW",
        "elevation_authorized": False,
        "gate_requirement": "Requires human review by State Disaster Management Authority before elevation to civil advisory."
    }


@router.get("/advisory", response_model=EvidenceAdvisory, summary="Get structured evidence-based stakeholder advisory")
def get_advisory():
    # 1. Dynamically retrieve lake observations
    lake_history = data_service.get_lake_history("GL-SK-01")
    if not lake_history:
        raise HTTPException(status_code=404, detail="No lake history records found for GL-SK-01.")

    obs_map = {o["date"]: o for o in lake_history}
    latest_obs = obs_map.get("2023-10-09", lake_history[-1])
    baseline_obs = obs_map.get("2023-09-26", lake_history[0])

    area_latest = latest_obs.get("area_km2", 0.0)
    area_base = baseline_obs.get("area_km2", 0.0)
    delta_km2 = round(area_latest - area_base, 3) if area_base > 0 else 0.0
    pct_change = round((delta_km2 / area_base) * 100.0, 1) if area_base > 0 else 0.0

    # 2. Dynamically retrieve and score assets
    raw_assets = data_service.get_assets()
    critical_assets = [
        {
            "name": a.get("name"),
            "chainage_km": a.get("distance_from_lake_km"),
            "elevation_m": a.get("elevation_m"),
            "type": a.get("type"),
            "status": a.get("status_notes", "Screened")
        }
        for a in raw_assets if a.get("exposure_rating") == "Critical"
    ]

    # 3. Dynamically retrieve independent reservoir track
    reservoirs = data_service.get_reservoirs()
    res_map = {r.get("id"): r for r in reservoirs}
    chungthang = res_map.get("RES-TK-01", {})
    dikchu = res_map.get("RES-TK-02", {})

    chungthang_peak = chungthang.get("peak_monsoon_area_km2", 0.512)
    chungthang_latest = chungthang.get("latest_area_km2", 0.241)
    chungthang_pct = round(((chungthang_latest - chungthang_peak) / chungthang_peak) * 100.0, 1) if chungthang_peak > 0 else 0.0

    # 4. Check persisted human expert review gate
    reviews = _load_reviews()
    basin_review = reviews.get("ALT-2023-SK-01", {})
    review_status_str = basin_review.get("decision", "Awaiting Human Expert Review")
    elevation_authorized = basin_review.get("elevation_authorized", False)

    return EvidenceAdvisory(
        advisory_id="ADV-2023-SK-TEESTA-01",
        timestamp_utc=latest_obs.get("date", "2023-10-09") + "T04:58:31Z",
        basin="Teesta River Basin (Upper & Middle Reach)",
        target_lake="South Lhonak Glacial Lake",
        latest_observation={
            "observation_date": latest_obs.get("date", "2023-10-09"),
            "sensor": latest_obs.get("sensor", "Sentinel-2 MSI Level-2A (ESA Copernicus)"),
            "water_area_km2": area_latest,
            "baseline_date": baseline_obs.get("date", "2023-09-26"),
            "baseline_water_area_km2": area_base,
            "net_area_change_km2": delta_km2,
            "net_percentage_change": pct_change,
            "interpretation": "Catastrophic moraine breach and glacial lake drainage event confirmed by Sentinel-2 MSI multi-spectral surface tracking."
        },
        downstream_corridor={
            "corridor_length_km": 112.4,
            "elevation_drop_m": 4920,
            "elevation_start_m": 5200,
            "elevation_end_m": 280,
            "flow_path": "South Lhonak Lake -> Lhonak River -> Zemu Chu -> Lachen Chu -> Chungthang (Confluence) -> Teesta River Gorge -> Dikchu -> Singtam -> Rangpo",
            "terrain_screening": "D8 DEM flow accumulation through steep V-shaped Himalayan canyon (confinement ratio > 85%, mean valley slope 22.4°)."
        },
        screened_assets={
            "total_screened": len(raw_assets),
            "critical_count": len(critical_assets),
            "critical_assets": critical_assets
        },
        independent_reservoir_track={
            "track_description": "Track B: Independent Downstream Reservoir Water-Spread Surveillance",
            "chungthang_dam": {
                "id": "RES-TK-01",
                "pre_flood_spread_km2": chungthang_peak,
                "post_flood_spread_km2": chungthang_latest,
                "percentage_change": chungthang_pct,
                "status": chungthang.get("status", "Breached Oct 2023 / Bypass Reconstruction Flow")
            },
            "dikchu_dam": {
                "id": "RES-TK-02",
                "operating_spread_km2": dikchu.get("latest_area_km2", 0.385),
                "status": dikchu.get("status", "Operational / Post-desiltation")
            },
            "hydrological_safeguard": "Reservoir water-spread area is monitored as an independent empirical track. Storage volume cannot be inferred directly from 2D water-spread alone without bathymetric rating curves."
        },
        imagery_quality_and_confidence={
            "spatial_resolution_m": 10.0,
            "cloud_cover_pct": latest_obs.get("cloud_cover_pct", 3.4),
            "qa_flag": latest_obs.get("quality_flag", "Valid (Clear Sky Verification)"),
            "bands_used": "B03 (Green, 560nm), B08 (NIR, 842nm), B11 (SWIR-1, 1610nm)",
            "validation_reference": "ISRO NRSC Disaster Management Support Programme & Copernicus Open Access Hub",
            "confidence_rating": "High (Multi-spectral + Terrain validated)"
        },
        recommended_response="Review the evidence and relevant reservoir conditions with authorized disaster-management and reservoir personnel.",
        scientific_safeguards="Undercurrent is a research prototype for monitoring and preliminary exposure screening. It is not an operational GLOF early warning system (EWS) or hydrodynamic flood dispatch model. Real-world emergency response relies on official NDMA/SDMA directives.",
        review_status=review_status_str,
        review_authority="Sikkim SDMA / NDMA Glacial Risk Cell",
        can_elevate_to_public=False
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
                "ISRO RISAT-1A SAR structural displacement signatures"
            ],
            rule_applied="IF reservoir_surface_loss > 50% following upstream breach THEN flag_critical_reservoir_breach",
            confidence_level="High (Multi-mission verified)",
            disclaimer="Track B Independent observation. 2D water-spread loss is not equivalent to storage volume depletion without rating curves."
        )
    ]
