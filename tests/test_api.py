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

    print("Testing /api/exposure/SA-TEESTA-01/assets...")
    asts = exposure.get_corridor_assets("SA-TEESTA-01")
    assert asts["total_assets"] >= 5

    print("Testing /api/map/layers...")
    layers = maps.get_map_layers()
    assert len(layers["layers"]) >= 4

    print("Testing /api/map/geojson/south_lhonak...")
    gj = maps.get_layer_geojson("south_lhonak")
    assert gj["type"] == "FeatureCollection"

    print("Testing /api/alerts...")
    al = alerts.get_alert_flags()
    assert len(al) >= 2

    print("Testing /api/analysis/ndwi...")
    ndwi_req = NDWICalculationRequest(lake_id="south-lhonak-post", threshold=0.14, grid_size=24)
    ndwi_res = analysis.calculate_ndwi(ndwi_req)
    assert ndwi_res.water_pixel_count > 0
    assert ndwi_res.calculated_area_km2 > 0

    print("ALL 12 TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_undercurrent()
