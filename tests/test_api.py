"""
Unit test suite for Project Undercurrent routes and services.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.routes import health, lakes, reservoirs, exposure, maps, alerts, analysis
from backend.app.schemas.models import NDWICalculationRequest

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
    assert raster_pre["lake_isolated_water_pixels"] == 16661
    assert abs(raster_pre["physical_area_km2"] - 1.666) < 0.01
    assert raster_pre["crs"] == "EPSG:32645"

    raster_post = analysis.get_physical_raster_analysis(date="2023-10-09")
    assert raster_post["lake_isolated_water_pixels"] == 10023
    assert abs(raster_post["physical_area_km2"] - 1.003) < 0.01

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

    print("ALL API & VALIDATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_undercurrent()
