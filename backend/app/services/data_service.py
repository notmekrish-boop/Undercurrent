"""
Data Service layer for Project Undercurrent.
Loads GeoJSON datasets, profiles, catalogues, and provides indexed access.
"""

import json
import os
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
METADATA_DIR = os.path.join(DATA_DIR, "metadata")

class DataService:
    def __init__(self):
        self._lakes_geojson: Optional[Dict[str, Any]] = None
        self._reservoirs_chungthang: Optional[Dict[str, Any]] = None
        self._reservoirs_teesta_v: Optional[Dict[str, Any]] = None
        self._drainage_geojson: Optional[Dict[str, Any]] = None
        self._exposure_geojson: Optional[Dict[str, Any]] = None
        self._assets_geojson: Optional[Dict[str, Any]] = None
        self._elevation_profile: Optional[Dict[str, Any]] = None
        self._catalogue: Optional[Dict[str, Any]] = None
        self.load_all()

    def _read_json(self, rel_path: str) -> Dict[str, Any]:
        full_path = os.path.normpath(os.path.join(DATA_DIR, rel_path))
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def load_all(self):
        self._lakes_geojson = self._read_json("processed/south_lhonak_boundaries.geojson")
        self._reservoirs_chungthang = self._read_json("processed/chungthang_reservoir.geojson")
        self._reservoirs_teesta_v = self._read_json("processed/teesta_v_reservoir.geojson")
        self._drainage_geojson = self._read_json("processed/teesta_river_drainage.geojson")
        self._exposure_geojson = self._read_json("processed/teesta_exposure_corridor.geojson")
        self._assets_geojson = self._read_json("processed/downstream_assets.geojson")
        self._elevation_profile = self._read_json("processed/elevation_profile.json")
        self._catalogue = self._read_json("metadata/data_catalogue.json")

    def get_study_area(self) -> Dict[str, Any]:
        return {
            "id": "SA-TEESTA-01",
            "name": "Teesta River Basin (Upper & Middle Reach)",
            "basin": "Teesta River Basin",
            "region": "Sikkim Himalaya, India",
            "bbox": [88.15, 27.10, 88.75, 27.98],
            "projected_crs": "EPSG:32645 (WGS 84 / UTM Zone 45N)",
            "elevation_range_m": [280, 5200],
            "description": "Critical transnational Himalayan basin covering South Lhonak Glacial Lake, Chungthang Dam, Singtam, and Rangpo corridor."
        }

    def get_glacial_lakes(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "GL-SK-01",
                "name": "South Lhonak Glacial Lake",
                "type": "glacial_lake",
                "study_area_id": "SA-TEESTA-01",
                "latitude": 27.9128,
                "longitude": 88.2045,
                "elevation_m": 5200,
                "latest_area_km2": 1.003, # Validated empirical Sentinel-2 MSI Level-2A measurement (09 Oct 2023)
                "pre_event_area_km2": 1.666, # Validated empirical Sentinel-2 MSI Level-2A baseline (26 Sep 2023)
                "area_change_km2": -0.664,
                "area_change_pct": -39.84,
                "cross_reference_nrsc_reports": {
                    "pre_event_17_sep_km2": 1.682,
                    "post_event_04_oct_km2": 1.031
                },
                "status": "Monitored (Post-Outburst Stabilisation)",
                "observations_count": len(self._lakes_geojson.get("features", [])) if self._lakes_geojson else 7,
                "data_sources": ["Sentinel-2 MSI Level-2A (ESA Copernicus)", "ISRO NRSC Rapid Reports", "Landsat-8 OLI", "CartoDEM"]
            }
        ]

    def get_lake_history(self, lake_id: str) -> List[Dict[str, Any]]:
        if not self._lakes_geojson:
            return []
        obs_list = []
        for feat in self._lakes_geojson.get("features", []):
            props = feat.get("properties", {})
            if props.get("water_body_id") == lake_id or lake_id in ("GL-SK-01", "south-lhonak"):
                obs_list.append(props)
        # Sort by date ascending
        obs_list.sort(key=lambda x: x.get("date", ""))
        return obs_list

    def get_reservoirs(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "RES-TK-01",
                "name": "Teesta-III Chungthang Dam Reservoir",
                "type": "reservoir",
                "study_area_id": "SA-TEESTA-01",
                "latitude": 27.6040,
                "longitude": 88.6485,
                "elevation_m": 1560,
                "latest_area_km2": 0.241,
                "peak_monsoon_area_km2": 0.512,
                "status": "Breached Oct 2023 / Bypass Reconstruction Flow",
                "observations_count": len(self._reservoirs_chungthang.get("features", [])) if self._reservoirs_chungthang else 4,
                "data_sources": ["Sentinel-2 MSI", "ISRO Cartosat-2", "CWC Station Reports"]
            },
            {
                "id": "RES-TK-02",
                "name": "Teesta-V NHPC Dam Reservoir (Dikchu)",
                "type": "reservoir",
                "study_area_id": "SA-TEESTA-01",
                "latitude": 27.4220,
                "longitude": 88.5200,
                "elevation_m": 650,
                "latest_area_km2": 0.385,
                "peak_monsoon_area_km2": 0.385,
                "status": "Operational / Post-desiltation",
                "observations_count": len(self._reservoirs_teesta_v.get("features", [])) if self._reservoirs_teesta_v else 1,
                "data_sources": ["Sentinel-2 MSI", "Bhoonidhi ISRO"]
            }
        ]

    def get_reservoir_history(self, res_id: str) -> List[Dict[str, Any]]:
        source = self._reservoirs_chungthang if "01" in res_id or "chungthang" in res_id.lower() else self._reservoirs_teesta_v
        if not source:
            return []
        items = [f.get("properties", {}) for f in source.get("features", [])]
        items.sort(key=lambda x: x.get("date", ""))
        return items

    def get_assets(self) -> List[Dict[str, Any]]:
        if not self._assets_geojson:
            return []
        return [f.get("properties", {}) for f in self._assets_geojson.get("features", [])]

    def get_elevation_profile(self) -> List[Dict[str, Any]]:
        if not self._elevation_profile:
            return []
        return self._elevation_profile.get("profile", [])

    def get_geojson(self, layer_name: str) -> Optional[Dict[str, Any]]:
        mapping = {
            "lakes": self._lakes_geojson,
            "south_lhonak": self._lakes_geojson,
            "reservoirs": self._reservoirs_chungthang,
            "chungthang": self._reservoirs_chungthang,
            "teesta_v": self._reservoirs_teesta_v,
            "drainage": self._drainage_geojson,
            "river": self._drainage_geojson,
            "exposure": self._exposure_geojson,
            "corridor": self._exposure_geojson,
            "assets": self._assets_geojson
        }
        return mapping.get(layer_name.lower())

    def get_catalogue(self) -> Dict[str, Any]:
        return self._catalogue or {}

data_service = DataService()
