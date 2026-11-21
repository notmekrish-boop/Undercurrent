import rasterio
import rasterio.features
import rasterio.warp
from rasterio.crs import CRS
import numpy as np
from scipy import ndimage
import json

def extract_lake_geojson():
    # Load 26 Sep pre-flood
    with rasterio.open(r'data\raw\satellite\Water_2023-09-26.tiff') as src_pre:
        pre_water = src_pre.read(1)
        transform_pre = src_pre.transform
        crs_pre = src_pre.crs
        
    # Isolate South Lhonak Lake component (row 375, col 556)
    lbl_pre, _ = ndimage.label(pre_water == 1)
    target_pre = lbl_pre[375, 556]
    mask_pre = (lbl_pre == target_pre).astype(np.uint8)
    
    # Load 09 Oct post-flood bands to compute refined post-burst lake boundary
    r1, r2 = 320, 450
    c1, c2 = 310, 620
    with rasterio.open(r'data\raw\satellite\2023-10-09_B03.tiff.tiff') as s: b03 = s.read(1).astype(float)
    with rasterio.open(r'data\raw\satellite\2023-10-09_B08.tiff.tiff') as s: b08 = s.read(1).astype(float)
    
    ndwi_post = (b03 - b08) / np.maximum(b03 + b08, 1e-6)
    
    # Post-burst water mask: within lake AOI, NDWI > 0.265 (separating open water from exposed mud)
    post_water_raw = np.zeros_like(ndwi_post, dtype=np.uint8)
    post_water_raw[r1:r2, c1:c2] = (ndwi_post[r1:r2, c1:c2] > 0.265).astype(np.uint8)
    
    # Keep largest connected component in lake area
    lbl_post, _ = ndimage.label(post_water_raw == 1)
    target_post = lbl_post[375, 556]
    if target_post == 0:
        patch = lbl_post[375-15:375+15, 556-15:556+15]
        target_post = np.bincount(patch[patch > 0]).argmax()
    mask_post = (lbl_post == target_post).astype(np.uint8)
    
    print(f"Pre-flood mask pixels: {mask_pre.sum()} ({mask_pre.sum() * 100.02 / 1e6:.3f} km²)")
    print(f"Post-flood mask pixels: {mask_post.sum()} ({mask_post.sum() * 100.02 / 1e6:.3f} km²)")
    
    # Extract polygon shapes
    def get_polygons(mask, transform):
        shapes_gen = rasterio.features.shapes(mask, mask=(mask == 1), transform=transform)
        polys = []
        for geom, val in shapes_gen:
            if val == 1:
                # Transform coordinates from EPSG:32645 to EPSG:4326 (WGS84 lon, lat)
                coords_wgs84 = []
                for ring in geom['coordinates']:
                    xs = [pt[0] for pt in ring]
                    ys = [pt[1] for pt in ring]
                    lons, lats = rasterio.warp.transform(CRS.from_epsg(32645), CRS.from_epsg(4326), xs, ys)
                    ring_wgs = [[round(lon, 6), round(lat, 6)] for lon, lat in zip(lons, lats)]
                    coords_wgs84.append(ring_wgs)
                polys.append({
                    "type": geom['type'],
                    "coordinates": coords_wgs84
                })
        return polys

    polys_pre = get_polygons(mask_pre, transform_pre)
    polys_post = get_polygons(mask_post, transform_pre)
    
    print(f"Extracted {len(polys_pre)} pre-flood polygon(s), {len(polys_post)} post-flood polygon(s)")
    
    # Build complete valid GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "lake_id": "GL-SK-01",
            "lake_name": "South Lhonak Glacial Lake",
            "country": "India",
            "state": "Sikkim",
            "district": "Mangan (North Sikkim)",
            "elevation_m": 5200,
            "center": [88.2045, 27.9128],
            "methodology": "Sentinel-2 MSI Level-2A Multi-Spectral NDWI & AOI Lake Boundary Extraction",
            "spatial_reference": "WGS 84 / UTM zone 45N (EPSG:32645) reprojected to EPSG:4326",
            "pre_burst": {
                "observation_date": "2023-09-26",
                "sensor": "Sentinel-2 MSI (ESA Copernicus)",
                "bands": "B03 (Green), B08 (NIR)",
                "resolution_m": 10.0,
                "pixel_count": int(mask_pre.sum()),
                "water_area_m2": round(float(mask_pre.sum() * 100.0211), 2),
                "water_area_km2": round(float(mask_pre.sum() * 100.0211 / 1e6), 3),
                "water_area_ha": round(float(mask_pre.sum() * 100.0211 / 1e4), 2),
                "status": "Maximum pre-burst glacial lake extent"
            },
            "post_burst": {
                "observation_date": "2023-10-09",
                "sensor": "Sentinel-2 MSI (ESA Copernicus)",
                "bands": "B03 (Green), B08 (NIR)",
                "resolution_m": 10.0,
                "pixel_count": int(mask_post.sum()),
                "water_area_m2": round(float(mask_post.sum() * 100.0211), 2),
                "water_area_km2": round(float(mask_post.sum() * 100.0211 / 1e6), 3),
                "water_area_ha": round(float(mask_post.sum() * 100.0211 / 1e4), 2),
                "status": "Post-outburst moraine drainage scar"
            },
            "change_metrics": {
                "area_change_km2": round(float((mask_post.sum() - mask_pre.sum()) * 100.0211 / 1e6), 3),
                "area_change_ha": round(float((mask_post.sum() - mask_pre.sum()) * 100.0211 / 1e4), 2),
                "percentage_change": round(float((mask_post.sum() - mask_pre.sum()) / mask_pre.sum() * 100), 2),
                "breach_event": "Catastrophic Moraine Failure (04 October 2023 GLOF)"
            }
        },
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "phase": "pre_burst",
                    "date": "2023-09-26",
                    "label": "Pre-Burst Extent (26 Sep 2023)",
                    "sensor": "Sentinel-2 MSI (10m)",
                    "area_km2": round(float(mask_pre.sum() * 100.0211 / 1e6), 3),
                    "area_ha": round(float(mask_pre.sum() * 100.0211 / 1e4), 2),
                    "stroke": "#38bdf8",
                    "stroke-width": 2.5,
                    "fill": "#0284c7",
                    "fill-opacity": 0.35
                },
                "geometry": polys_pre[0]
            },
            {
                "type": "Feature",
                "properties": {
                    "phase": "post_burst",
                    "date": "2023-10-09",
                    "label": "Post-Burst Extent (09 Oct 2023)",
                    "sensor": "Sentinel-2 MSI (10m)",
                    "area_km2": round(float(mask_post.sum() * 100.0211 / 1e6), 3),
                    "area_ha": round(float(mask_post.sum() * 100.0211 / 1e4), 2),
                    "stroke": "#f43f5e",
                    "stroke-width": 2.5,
                    "fill": "#e11d48",
                    "fill-opacity": 0.45
                },
                "geometry": polys_post[0]
            }
        ]
    }
    
    out_path = r'data\processed\south_lhonak_boundaries.geojson'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2)
    print(f"Saved real satellite-derived GeoJSON to {out_path}!")

if __name__ == '__main__':
    extract_lake_geojson()
