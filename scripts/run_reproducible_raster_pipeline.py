"""
Executes the reproducible two-date physical raster pipeline per Action P0.
Saves execution logs, metadata, CRS, valid-data fractions, and exported water classification GeoTIFFs.
"""

import os
import sys
import json
import rasterio
import numpy as np
from datetime import datetime, timezone
from rasterio.warp import transform_geom
from rasterio.features import rasterize

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.ndwi_engine import (
    process_real_satellite_raster,
    find_satellite_band_file,
    load_georeferenced_lake_aoi
)


def run_pipeline():
    output_dir = os.path.join("data", "processed")
    os.makedirs(output_dir, exist_ok=True)

    log_file = os.path.join(output_dir, "raster_execution_log.json")
    execution_record = {
        "execution_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "processor": "Project Undercurrent Symmetric Raster Engine",
        "dates_processed": ["2023-09-26", "2023-10-09"],
        "runs": {}
    }

    aoi_poly = load_georeferenced_lake_aoi()

    for dt, th in [("2023-09-26", 0.20), ("2023-10-09", 0.265)]:
        print(f"Processing {dt}...")
        res = process_real_satellite_raster(dt, threshold=th)
        execution_record["runs"][dt] = res

        # Export classified GeoTIFF mask for desktop GIS (QGIS) verification
        b03_file = find_satellite_band_file(dt, "B03")
        b08_file = find_satellite_band_file(dt, "B08")
        out_tif = os.path.join(output_dir, f"classified_lake_water_{dt}.tif")

        with rasterio.open(b03_file) as s_g, rasterio.open(b08_file) as s_n:
            b03 = s_g.read(1).astype(float)
            b08 = s_n.read(1).astype(float)
            poly_crs = transform_geom("EPSG:4326", s_g.crs, aoi_poly)
            aoi_mask = rasterize([poly_crs], out_shape=s_g.shape, transform=s_g.transform, fill=0, default_value=1, dtype=np.uint8)

            ndwi = (b03 - b08) / np.maximum(b03 + b08, 1e-6)
            water = ((ndwi > th) & (aoi_mask == 1) & (b03 > 0) & (b08 > 0)).astype(np.uint8)

            with rasterio.open(
                out_tif,
                "w",
                driver="GTiff",
                height=s_g.height,
                width=s_g.width,
                count=1,
                dtype=np.uint8,
                crs=s_g.crs,
                transform=s_g.transform,
                nodata=0
            ) as dst:
                dst.write(water, 1)

            print(f"Saved verified water mask to {out_tif}")

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(execution_record, f, indent=2)

    print(f"Saved complete execution log to {log_file}")


if __name__ == "__main__":
    run_pipeline()
