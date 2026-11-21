"""
Photo and Satellite Image Processing Service for Glacial Lake Area Extraction.
Project Undercurrent: Enables users to upload optical photographs, drone surveys,
or satellite imagery to classify water pixels, calculate lake surface area in km²,
and feed observations directly into the multi-temporal risk engine.

Supports:
1. Standard optical photos (PNG, JPG, JPEG, WebP) via Optical Water Index (OWI).
2. Grayscale & single-band rasters via low-reflectance / absorption segmentation.
3. GeoTIFF satellite rasters (single-band SWIR/NIR B11/B08, NDWI, or 3-band TrueColor)
   via Rasterio with automated CRS and pixel GSD detection.
4. Auto-matching of known Sentinel-2 observation dates (e.g. 2023-09-26, 2023-10-09)
   with companion multi-spectral Level-2A bands in the local catalog.
"""

import io
import re
import os
import base64
import numpy as np
from PIL import Image
from scipy import ndimage
import rasterio
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom
from rasterio.features import rasterize
from typing import Dict, Any, Tuple, Optional

from ..schemas.models import LakePhotoAnalysisRequest, LakePhotoAnalysisResult
from .ndwi_engine import (
    load_georeferenced_lake_aoi,
    find_satellite_band_file,
    process_real_satellite_raster,
    RAW_SATELLITE_DIR
)


def extract_raw_bytes(b64_string: str) -> bytes:
    """Decodes a base64 encoded image string, handling data URI prefixes."""
    raw_str = b64_string.strip()
    if "," in raw_str and "base64" in raw_str:
        _, raw_str = raw_str.split(",", 1)
    return base64.b64decode(raw_str)


def make_preview_base64(proc_rgb: np.ndarray, lake_mask: np.ndarray) -> str:
    """Generates an annotated preview image: dim non-water background and tint lake pixels vibrant cyan."""
    preview_arr = proc_rgb.copy()
    dimmed_bg = (preview_arr.astype(np.float32) * 0.60).astype(np.uint8)
    cyan_tint = np.array([6, 182, 212], dtype=np.uint8)
    for c in range(3):
        dimmed_bg[:, :, c] = np.where(
            lake_mask,
            np.clip(preview_arr[:, :, c] * 0.25 + cyan_tint[c] * 0.75, 0, 255),
            dimmed_bg[:, :, c]
        )

    preview_img = Image.fromarray(dimmed_bg)
    max_preview_dim = 600
    pw, ph = preview_img.size
    if max(pw, ph) > max_preview_dim:
        p_scale = max_preview_dim / max(pw, ph)
        preview_img = preview_img.resize((int(pw * p_scale), int(ph * p_scale)), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    preview_img.save(buf, format="PNG", optimize=True)
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"


def analyze_uploaded_lake_photo(req: LakePhotoAnalysisRequest) -> LakePhotoAnalysisResult:
    """
    Analyzes an uploaded photo or satellite image:
    1. Checks if the file matches known Sentinel-2 dates with local multi-spectral bands.
    2. Opens GeoTIFFs (single-band SWIR/NIR or 3-band TrueColor) with Rasterio.
    3. Handles standard RGB and grayscale photographs with Optical Water Index (OWI).
    4. Segments lake water body using morphological connected component filtering.
    5. Computes physical lake surface area in km² and m² based on pixel resolution.
    6. Generates a highlighted segmented preview image with cyan water mask.
    """
    img_bytes = extract_raw_bytes(req.photo_base64)
    file_name = req.file_name or ""
    date_str = req.observation_date or "2024-10-15"
    lake_name_str = req.lake_name or "South Lhonak Glacial Lake"

    # 1. Check if filename or observation date matches known Sentinel-2 catalog dates
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", file_name) or re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
    matched_date = date_match.group(1) if date_match else None

    if matched_date and matched_date in ["2023-09-26", "2023-10-09"]:
        try:
            # Calibrated satellite NDWI thresholds: 0.20 pre-flood, 0.265 post-flood
            calibrated_default_th = 0.20 if matched_date == "2023-09-26" else 0.265
            user_th = req.sensitivity_threshold
            # If user left slider at optical default 0.04, use the calibrated satellite threshold
            if user_th is None or abs(user_th - 0.04) < 1e-4:
                th = calibrated_default_th
            else:
                th = float(user_th)

            raster_res = process_real_satellite_raster(matched_date, threshold=th)

            # Load B03 and classified water mask for visual preview
            b03_path = find_satellite_band_file(matched_date, "B03")
            out_tif = os.path.join("data", "processed", f"classified_lake_water_{matched_date}.tif")

            with rasterio.open(b03_path) as s_g:
                b03 = s_g.read(1)
                valid = b03[b03 > 0]
                p2, p98 = np.percentile(valid, (2, 98))
                gray = np.clip((b03 - p2) / (p98 - p2 + 1e-6) * 255.0, 0, 255).astype(np.uint8)
                proc_rgb = np.stack([gray, gray, gray], axis=-1)

            if os.path.exists(out_tif):
                with rasterio.open(out_tif) as s_w:
                    lake_mask = s_w.read(1) == 1
            else:
                lake_mask = np.zeros(b03.shape, dtype=bool)

            preview_b64 = make_preview_base64(proc_rgb, lake_mask)
            w_px = int(raster_res["lake_isolated_water_pixels"])
            tot_px = b03.shape[0] * b03.shape[1]
            w_ratio = round((w_px / tot_px) * 100.0, 2)
            gsd = float(raster_res["spatial_resolution_m"])
            area_sqm = float(raster_res["physical_area_m2"])
            area_km2 = float(raster_res["physical_area_km2"])

            return LakePhotoAnalysisResult(
                lake_name=lake_name_str,
                observation_date=matched_date,
                image_width=b03.shape[1],
                image_height=b03.shape[0],
                total_pixels=tot_px,
                water_pixels=w_px,
                water_ratio_pct=w_ratio,
                pixel_resolution_m=gsd,
                calculated_area_sqm=area_sqm,
                calculated_area_km2=area_km2,
                method_used=f"Symmetric Multi-spectral Sentinel-2 MSI Level-2A NDWI Engine (Companion B03+B08 matched for {matched_date})",
                segmented_preview_base64=preview_b64,
                risk_input_ready={
                    "date": matched_date,
                    "area_km2": area_km2,
                    "sensor": "Sentinel-2 MSI Level-2A (10m)",
                    "source": f"Matched Copernicus S2 MSI ({matched_date})",
                    "water_pixel_count": w_px
                },
                scientific_disclaimer=(
                    "Processed using authoritative Copernicus Sentinel-2 MSI Level-2A surface reflectance data "
                    "with georeferenced AOI boundary and connected-component lake isolation. 2D planar extent only."
                )
            )
        except Exception as e:
            print(f"[Undercurrent] Fallback from catalog match to standalone raster analysis: {e}")

    # 2. Try opening as GeoTIFF via rasterio.MemoryFile
    try:
        with MemoryFile(img_bytes) as mem:
            with mem.open() as src:
                orig_w, orig_h = src.width, src.height
                tot_px = orig_w * orig_h
                count = src.count
                res = src.res
                crs = src.crs
                transform = src.transform
                gsd_m = round(float(res[0]), 2) if (res and res[0] > 0.05 and res[0] < 500) else (req.pixel_resolution_m or 10.0)

                # Georeferenced AOI mask if CRS is present
                aoi_mask = None
                if crs:
                    try:
                        aoi = load_georeferenced_lake_aoi()
                        poly_crs = transform_geom("EPSG:4326", crs, aoi)
                        aoi_mask = rasterize([poly_crs], out_shape=src.shape, transform=transform, fill=0, default_value=1, dtype=np.uint8)
                    except Exception:
                        aoi_mask = None

                if count >= 3:
                    # Multi-band TrueColor or composite GeoTIFF
                    r = src.read(1).astype(np.float32)
                    g = src.read(2).astype(np.float32)
                    b = src.read(3).astype(np.float32)

                    # Contrast stretch to 0-255 uint8
                    all_vals = np.stack([r, g, b], axis=-1)
                    p2, p98 = np.percentile(all_vals[all_vals > 0], (2, 98))
                    proc_rgb = np.clip((all_vals - p2) / (p98 - p2 + 1e-6) * 255.0, 0, 255).astype(np.uint8)

                    # Optical Water Index
                    owi = ((g + b) - 2.0 * r) / ((g + b) + 2.0 * r + 1e-5)
                    th = req.sensitivity_threshold if req.sensitivity_threshold is not None else 0.04
                    raw_water = (owi >= th)
                    if aoi_mask is not None and np.sum(aoi_mask) > 0:
                        raw_water = raw_water & (aoi_mask == 1)
                    method = "GeoTIFF True-Color Multi-band Optical Water Index (OWI)"
                else:
                    # Single-band GeoTIFF (SWIR B11, NIR B08, NDWI, or Water mask)
                    band = src.read(1).astype(np.float32)
                    valid = band[band > 0]
                    if len(valid) == 0:
                        valid = band
                    p2, p98 = np.percentile(valid, (2, 98)) if len(valid) > 0 else (0, 1)
                    gray = np.clip((band - p2) / (p98 - p2 + 1e-6) * 255.0, 0, 255).astype(np.uint8)
                    proc_rgb = np.stack([gray, gray, gray], axis=-1)

                    # Check if binary water mask
                    if np.all(np.isin(np.unique(band), [0, 1, -3.4028234663852886e+38])):
                        raw_water = (band == 1)
                        method = "Pre-classified GeoTIFF Binary Water Mask"
                    elif np.nanmax(band) <= 1.0 and np.nanmin(band) >= -1.0 and np.nanmean(band) < 0.1:
                        # NDWI raster
                        th = req.sensitivity_threshold if req.sensitivity_threshold is not None else 0.20
                        raw_water = (band >= th)
                        method = "Sentinel-2 Physical NDWI Raster Classification"
                    else:
                        # SWIR / NIR single band: water is dark absorption
                        th = req.sensitivity_threshold if (req.sensitivity_threshold and req.sensitivity_threshold > 0) else 0.04
                        raw_water = (band > 0.0) & (band <= th)
                        if aoi_mask is not None and np.sum(aoi_mask) > 0:
                            raw_water = raw_water & (aoi_mask == 1)
                        method = "Sentinel-2 Single-Band Infrared Absorption Segmentation (B11/SWIR)"

                # Morphological filtering & component isolation
                struct = ndimage.generate_binary_structure(2, 2)
                cleaned = ndimage.binary_opening(raw_water, structure=struct, iterations=1)
                labeled, num = ndimage.label(cleaned, structure=struct)
                if num > 0:
                    sizes = ndimage.sum(cleaned, labeled, range(1, num + 1))
                    max_idx = np.argmax(sizes) + 1
                    lake_mask = (labeled == max_idx)
                else:
                    lake_mask = raw_water

                w_px = int(np.sum(lake_mask))
                area_sqm = round(w_px * (gsd_m ** 2), 1)
                area_km2 = round(area_sqm / 1e6, 4)
                w_ratio = round((w_px / tot_px) * 100.0, 2)
                preview_b64 = make_preview_base64(proc_rgb, lake_mask)

                return LakePhotoAnalysisResult(
                    lake_name=lake_name_str,
                    observation_date=date_str,
                    image_width=orig_w,
                    image_height=orig_h,
                    total_pixels=tot_px,
                    water_pixels=w_px,
                    water_ratio_pct=w_ratio,
                    pixel_resolution_m=gsd_m,
                    calculated_area_sqm=area_sqm,
                    calculated_area_km2=area_km2,
                    method_used=method,
                    segmented_preview_base64=preview_b64,
                    risk_input_ready={
                        "date": date_str,
                        "area_km2": area_km2,
                        "sensor": f"GeoTIFF Raster ({gsd_m}m)",
                        "source": "GeoTIFF Ingestion",
                        "water_pixel_count": w_px
                    },
                    scientific_disclaimer=(
                        "Calculated from ingested satellite GeoTIFF raster using calibrated sensor ground resolution. "
                        "Planar 2D surface area does not account for 3D sub-surface bathymetry."
                    )
                )
    except Exception:
        pass  # Fall through to PIL standard image handler

    # 3. Standard Optical Photograph (JPEG, PNG, WEBP)
    img = Image.open(io.BytesIO(img_bytes))
    orig_w, orig_h = img.size
    tot_px = orig_w * orig_h

    # Convert to RGB
    img_rgb = img.convert("RGB")
    max_dim = 1200
    scale_factor = 1.0
    if max(orig_w, orig_h) > max_dim:
        scale_factor = max_dim / max(orig_w, orig_h)
        new_w, new_h = int(orig_w * scale_factor), int(orig_h * scale_factor)
        proc_img = img_rgb.resize((new_w, new_h), Image.Resampling.BILINEAR)
    else:
        proc_img = img_rgb

    arr = np.array(proc_img).astype(np.float32)
    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    # Check if image is grayscale (R == G == B)
    is_grayscale = np.mean(np.abs(r - g)) < 1.0 and np.mean(np.abs(g - b)) < 1.0

    if is_grayscale:
        # In grayscale photo, water is darker than surrounding rocky terrain
        brightness = (r + g + b) / 3.0
        p15 = np.percentile(brightness, 15)
        raw_water_mask = (brightness <= p15) & (brightness > 5.0)
        method = "Grayscale Contrast & Low-Reflectance Dark Basin Extraction"
    else:
        # Optical Water Index (OWI): ((G + B) - 2R) / ((G + B) + 2R)
        owi = ((g + b) - 2.0 * r) / ((g + b) + 2.0 * r + 1e-5)
        brightness = (r + g + b) / 3.0
        th = req.sensitivity_threshold if req.sensitivity_threshold is not None else 0.04
        raw_water_mask = (owi >= th) & (brightness < 240.0)
        method = "Optical Spectral Water Segmentation + Blue-Green Excess"

    # Morphological component isolation
    struct = ndimage.generate_binary_structure(2, 2)
    cleaned = ndimage.binary_opening(raw_water_mask, structure=struct, iterations=1)
    labeled, num = ndimage.label(cleaned, structure=struct)
    if num > 0:
        sizes = ndimage.sum(cleaned, labeled, range(1, num + 1))
        max_size = np.max(sizes)
        min_cutoff = max(10, int(max_size * 0.005))
        keep_labels = [i + 1 for i, sz in enumerate(sizes) if sz >= min_cutoff]
        lake_mask = np.isin(labeled, keep_labels)
    else:
        lake_mask = raw_water_mask

    proc_water = int(np.sum(lake_mask))
    w_px = int(round(proc_water / (scale_factor ** 2))) if scale_factor < 1.0 else proc_water
    w_ratio = round((w_px / tot_px) * 100.0, 2) if tot_px > 0 else 0.0
    gsd_m = req.pixel_resolution_m if (req.pixel_resolution_m and req.pixel_resolution_m > 0) else 10.0

    if req.known_reference_area_km2 and req.known_reference_area_km2 > 0 and w_px > 0:
        target_sqm = req.known_reference_area_km2 * 1_000_000.0
        gsd_m = round(float(np.sqrt(target_sqm / w_px)), 2)

    area_sqm = round(w_px * (gsd_m ** 2), 1)
    area_km2 = round(area_sqm / 1_000_000.0, 4)

    preview_b64 = make_preview_base64(np.array(proc_img), lake_mask)

    return LakePhotoAnalysisResult(
        lake_name=lake_name_str,
        observation_date=date_str,
        image_width=orig_w,
        image_height=orig_h,
        total_pixels=tot_px,
        water_pixels=w_px,
        water_ratio_pct=w_ratio,
        pixel_resolution_m=gsd_m,
        calculated_area_sqm=area_sqm,
        calculated_area_km2=area_km2,
        method_used=method,
        segmented_preview_base64=preview_b64,
        risk_input_ready={
            "date": date_str,
            "area_km2": area_km2,
            "sensor": f"Uploaded Optical Photo ({gsd_m}m GSD)",
            "source": "Optical Ingestion",
            "water_pixel_count": w_px
        },
        scientific_disclaimer=(
            "Calculated area is 2D planar water-spread extent based on user-provided or calibrated pixel resolution. "
            "Optical photo segmentation identifies surface standing water and does not determine 3D depth or bathymetry."
        )
    )
