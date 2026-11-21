"""
Unit test suite for Project Undercurrent routes and services.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.routes import health, lakes, reservoirs, exposure, maps, alerts, analysis, pipeline
from backend.app.schemas.models import NDWICalculationRequest, HumanReviewSubmission

def test_undercurrent():
    print("Testing /api/health...")
    h = health.health_check()
    assert h["status"] == "online"
    assert h["project"] == "Undercurrent"

    print("Testing /api/lakes...")
    lk = lakes.get_glacial_lakes()
    assert len(lk) >= 1
    assert lk[0]["name"] == "South Lhonak Glacial Lake"

    print("Testing /api/lakes/GL-SK-01/history...")
    hist = lakes.get_lake_history("GL-SK-01")
    assert hist["observations_count"] >= 3

    print("Testing /api/lakes/GL-SK-01/compare...")
    comp = lakes.compare_lake_dates("GL-SK-01", "2023-09-17", "2023-10-04")
    assert comp["percentage_change"] < -30.0

    print("Testing /api/reservoirs...")
    res = reservoirs.get_reservoirs()
    assert len(res) >= 2

    print("Testing /api/reservoirs/RES-TK-01/history...")
    res_hist = reservoirs.get_reservoir_history("RES-TK-01")
    assert res_hist["observations_count"] >= 2

    print("Testing /api/exposure/SA-TEESTA-01...")
    exp = exposure.get_exposure_summary("SA-TEESTA-01")
    assert exp["total_corridor_length_km"] > 100

    print("Testing /api/exposure/SA-TEESTA-01/profile...")
    prof = exposure.get_corridor_profile("SA-TEESTA-01")
    assert prof["profile_points_count"] >= 5

    print("Testing /api/exposure/SA-TEESTA-01/assets (Location-specific DEM slopes)...")
    asts = exposure.get_corridor_assets("SA-TEESTA-01")
    assert asts["total_assets"] >= 5
    # Verify location-specific slope varies along corridor (not static 25.0)
    slopes = [a["location_slope_deg"] for a in asts["assets"]]
    assert len(set(slopes)) > 1, "Expected location-specific slopes derived from DEM elevation profile"
    assert asts["assets"][0]["location_slope_deg"] != asts["assets"][-1]["location_slope_deg"]

    print("Testing /api/map/layers...")
    layers = maps.get_map_layers()
    assert len(layers["layers"]) >= 4

    print("Testing /api/map/geojson/south_lhonak...")
    gj = maps.get_layer_geojson("south_lhonak")
    assert gj["type"] == "FeatureCollection"

    print("Testing /api/alerts...")
    al = alerts.get_alert_flags()
    assert len(al) >= 2

    print("Testing /api/alerts/advisory...")
    adv = alerts.get_advisory()
    assert adv.advisory_id == "ADV-2023-SK-TEESTA-01"
    assert adv.latest_observation["water_area_km2"] == 1.003
    assert adv.downstream_corridor["elevation_drop_m"] == 4920
    assert adv.screened_assets["critical_count"] == 3

    print("Testing /api/analysis/ndwi (Interactive Simulator)...")
    ndwi_req = NDWICalculationRequest(lake_id="south-lhonak-post", threshold=0.14, grid_size=24)
    ndwi_res = analysis.calculate_ndwi(ndwi_req)
    assert ndwi_res.water_pixel_count > 0
    assert ndwi_res.calculated_area_km2 > 0

    print("Testing /api/analysis/raster/south-lhonak (Physical 10m Sentinel-2 Rasters)...")
    raster_pre = analysis.get_physical_raster_analysis(date="2023-09-26")
    assert raster_pre["processing_status"] == "PROCESSED_SATELLITE_MEASUREMENT"
    assert raster_pre["lake_isolated_water_pixels"] > 16000
    assert abs(raster_pre["physical_area_km2"] - 1.666) < 0.05
    assert raster_pre["crs"] == "EPSG:32645"
    assert raster_pre["qa_evidence"]["valid_data_fraction_pct"] > 95.0

    raster_post = analysis.get_physical_raster_analysis(date="2023-10-09")
    assert raster_post["processing_status"] == "PROCESSED_SATELLITE_MEASUREMENT"
    assert raster_post["lake_isolated_water_pixels"] > 9000
    assert abs(raster_post["physical_area_km2"] - 1.0) < 0.08
    assert raster_post["qa_evidence"]["valid_data_fraction_pct"] > 95.0

    print("Testing /api/exposure/SA-TEESTA-01/sensitivity (Weight sensitivity testing)...")
    sens = exposure.get_exposure_sensitivity("SA-TEESTA-01")
    assert sens["assets_evaluated"] >= 5
    assert len(sens["scenarios_tested"]) == 4
    assert "ranks_across_scenarios" in sens["results"][0]
    assert "slope_source" in sens["results"][0]
    assert "Dynamic rank evaluation" in sens["sensitivity_conclusion"]

    print("Testing /api/alerts/ALT-2023-SK-01/review (Human Expert Review gate)...")
    sub = HumanReviewSubmission(
        reviewer_name="Dr. P. Sharma",
        organization="Sikkim State Disaster Management Authority",
        review_decision="ENDORSED_FOR_INTERNAL_ACTION",
        technical_comments="Validated against Sentinel-2 MSI 10m Ground Sampling Distance. Drainage footprint confirmed."
    )
    rev_res = alerts.submit_human_review("ALT-2023-SK-01", sub)
    assert rev_res["status"] == "success"
    assert rev_res["review_record"]["elevation_authorized"] is True
    assert "T" in rev_res["review_record"]["reviewed_at_utc"]

    # Verify review persistence across lookup
    stored_rev = alerts.get_alert_review("ALT-2023-SK-01")
    assert stored_rev["reviewed_by"] == "Dr. P. Sharma"
    assert stored_rev["elevation_authorized"] is True

    print("Testing /api/analysis/validation (Phase 1 Scientific Validation Record)...")
    val_rec = analysis.get_scientific_validation()
    assert val_rec["pre_outburst_baseline"]["isolated_lake_pixels"] in (16660, 16661)
    assert val_rec["post_outburst_state"]["isolated_lake_pixels"] in (9762, 10023)
    assert val_rec["pre_outburst_baseline"]["classification_accuracy_vs_reference"]["iou_jaccard_index"] > 0.95
    assert "regional_benchmark_alignment_and_date_documentation" in val_rec

    print("Testing /api/map/download/south_lhonak (Downloadable GeoJSON)...")
    dl = maps.download_layer_geojson("south_lhonak")
    assert dl.headers["Content-Disposition"] == 'attachment; filename="undercurrent_south_lhonak.geojson"'

    print("Testing /api/pipeline/end-to-end (Phase 3 Unified Workflow MVP)...")
    pipe = pipeline.get_end_to_end_pipeline()
    assert pipe["pipeline_version"].startswith("1.0.0")
    assert pipe["pipeline_status"] == "SUCCESS"
    assert pipe["is_measured"] is True
    assert pipe["is_fallback"] is False
    assert "step_1_lake_only_change" in pipe["workflow_steps"]
    assert "step_2_drainage_corridor" in pipe["workflow_steps"]
    assert "step_3_screened_asset_overlays" in pipe["workflow_steps"]
    assert "step_4_independent_reservoir_track" in pipe["workflow_steps"]
    assert "step_5_evidence_advisory" in pipe["workflow_steps"]

    print("Testing /api/lakes/assess-risk (Multi-Date Glacial Outburst Risk Engine)...")
    from backend.app.schemas.models import GlacierLakeRiskAssessmentRequest, GlacierLakeObservationInput

    # Scenario 1: Critical moraine breach drainage
    req_breach = GlacierLakeRiskAssessmentRequest(
        lake_name="South Lhonak Lake",
        basin="Teesta River Basin",
        elevation_masl=5200.0,
        downstream_distance_km=68.0,
        channel_slope_deg=22.0,
        dam_type="Moraine-dammed",
        observations=[
            GlacierLakeObservationInput(date="2023-09-26", area_km2=1.6664),
            GlacierLakeObservationInput(date="2023-10-09", area_km2=0.9764)
        ]
    )
    res_b = lakes.assess_glacier_lake_risk(req_breach)
    assert res_b.hazard_classification["risk_tier"] == "CRITICAL"
    assert res_b.temporal_metrics["percentage_change"] < -40.0
    assert res_b.hazard_classification["hazard_score_0_to_100"] > 80.0

    # Scenario 2: Accelerated expansion hazard
    req_exp = GlacierLakeRiskAssessmentRequest(
        lake_name="Imja Tsho",
        basin="Dudh Koshi",
        elevation_masl=5010.0,
        downstream_distance_km=45.0,
        channel_slope_deg=18.0,
        dam_type="Ice-cored moraine",
        observations=[
            GlacierLakeObservationInput(date="2018-10-01", area_km2=0.95),
            GlacierLakeObservationInput(date="2023-10-01", area_km2=1.35)
        ]
    )
    res_e = lakes.assess_glacier_lake_risk(req_exp)
    assert res_e.hazard_classification["risk_tier"] == "HIGH"
    assert res_e.temporal_metrics["percentage_change"] > 35.0

    # Scenario 3: Stable baseline lake
    req_stable = GlacierLakeRiskAssessmentRequest(
        lake_name="Stable Alpine Tarn",
        observations=[
            GlacierLakeObservationInput(date="2021-10-01", area_km2=1.00),
            GlacierLakeObservationInput(date="2023-10-01", area_km2=1.02)
        ]
    )
    res_s = lakes.assess_glacier_lake_risk(req_stable)
    assert res_s.hazard_classification["risk_tier"] == "LOW"

    # Scenario 4: Ingestion endpoint
    ing_res = lakes.ingest_lake_observation(
        lake_id="GL-CUSTOM-01",
        obs=GlacierLakeObservationInput(date="2024-10-15", area_km2=1.01)
    )
    assert ing_res["status"] == "success"

    print("Testing input validation and error handling...")
    from fastapi import HTTPException
    from pydantic import ValidationError

    # Invalid compare date
    try:
        lakes.compare_lake_dates("GL-SK-01", "1990-01-01", "2023-10-04")
        assert False, "Should raise HTTPException for unknown earlier date"
    except HTTPException as e:
        assert e.status_code == 400

    # Invalid NDWI threshold (> 1.0)
    try:
        NDWICalculationRequest(lake_id="GL-SK-01", threshold=2.5)
        assert False, "Should raise ValidationError for threshold > 1.0"
    except ValidationError:
        pass

    # Invalid risk assessment (< 2 observations)
    try:
        req_bad = GlacierLakeRiskAssessmentRequest(
            lake_name="Bad Lake",
            observations=[GlacierLakeObservationInput(date="2023-01-01", area_km2=1.0)]
        )
        assert False, "Should raise ValidationError for < 2 observations"
    except ValidationError:
        pass

    print("ALL API & VALIDATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_undercurrent()
