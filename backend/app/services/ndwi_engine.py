"""
NDWI Water Detection & Thresholding Engine for Project Undercurrent.
Conforms to Section 7.1 of Undercurrent Blueprint:
NDWI = (Green - NIR) / (Green + NIR)
"""

import math
import numpy as np
from typing import Dict, Any, List

def generate_lake_ndwi_matrix(grid_size: int = 24, post_outburst: bool = False) -> np.ndarray:
    """
    Generates a realistic 2D matrix of NDWI values representing South Lhonak Lake basin.
    Water pixels typically have NDWI > 0.10 to 0.45.
    Glacial moraine / rock / bare earth has NDWI < 0.0 (-0.1 to -0.4).
    Snow / shadow around edges has intermediate or distinct values.
    """
    matrix = np.zeros((grid_size, grid_size), dtype=float)
    center_y, center_x = grid_size // 2, grid_size // 2
    
    # Radii for elliptical lake representation
    if not post_outburst:
        ry, rx = grid_size * 0.32, grid_size * 0.42
    else:
        # Post-outburst has a drained eastern flank / breached moraine
        ry, rx = grid_size * 0.26, grid_size * 0.30

    for i in range(grid_size):
        for j in range(grid_size):
            dy = (i - center_y) / ry
            dx = (j - center_x) / rx
            dist_sq = dy*dy + dx*dx
            
            # Post outburst moraine breach at east side (dx > 0.2)
            if post_outburst and dx > 0.15:
                dist_sq += (dx - 0.15) * 2.2

            if dist_sq <= 0.80:
                # Deep water core: high positive NDWI
                ndwi = 0.38 + 0.12 * math.cos(i * 0.3) * math.sin(j * 0.3)
            elif dist_sq <= 1.05:
                # Turbid / shallow shoreline boundary
                t = (dist_sq - 0.80) / 0.25
                ndwi = (1.0 - t) * 0.35 + t * 0.05 + 0.03 * math.sin(i + j)
            elif dist_sq <= 1.35:
                # Lateral moraine / shoreline debris
                ndwi = -0.05 + 0.06 * math.sin(i * 0.5)
            else:
                # Surrounding barren terrain / rock
                ndwi = -0.28 + 0.08 * math.cos(i * 0.4) * math.cos(j * 0.4)
            
            matrix[i, j] = round(float(ndwi), 3)

    return matrix

def classify_water_pixels(matrix: np.ndarray, threshold: float = 0.14) -> Dict[str, Any]:
    """
    Classifies pixels as water where NDWI >= threshold.
    Returns classified binary grid (1 for water, 0 for non-water) and metrics.
    """
    binary_grid = (matrix >= threshold).astype(int)
    water_pixels = int(np.sum(binary_grid))
    total_pixels = int(matrix.size)
    ratio = water_pixels / total_pixels if total_pixels > 0 else 0.0

    # Scale to km² based on calibration to South Lhonak ground truth
    # If unbreached, ~1.68 km² at threshold 0.14
    nominal_pixel_area_km2 = 1.682 / 215.0 # based on nominal 24x24 grid water count
    calculated_area_km2 = round(water_pixels * nominal_pixel_area_km2, 3)

    return {
        "threshold": threshold,
        "water_pixel_count": water_pixels,
        "total_pixel_count": total_pixels,
        "water_area_ratio": round(ratio, 4),
        "calculated_area_km2": calculated_area_km2,
        "matrix_grid": matrix.tolist(),
        "classification_grid": binary_grid.tolist()
    }
