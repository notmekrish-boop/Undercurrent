import rasterio
import rasterio.warp
from rasterio.crs import CRS
import numpy as np
from scipy import ndimage
import json

def analyze_satellite_data():
    path_pre = r'data\raw\satellite\Water_2023-09-26.tiff'
    path_post = r'data\raw\satellite\Water_2023-10-09.tiff'
    
    with rasterio.open(path_pre) as src_pre:
        pre_water = src_pre.read(1)
        transform_pre = src_pre.transform
        crs_pre = src_pre.crs
        res_pre = src_pre.res
        bounds_pre = src_pre.bounds
        
        # South Lhonak coordinates in WGS84
        lhonak_lon, lhonak_lat = 88.2045, 27.9128
        
        # Reproject from WGS84 to EPSG:32645
        xs, ys = rasterio.warp.transform(CRS.from_epsg(4326), CRS.from_epsg(32645), [lhonak_lon], [lhonak_lat])
        lhonak_x, lhonak_y = xs[0], ys[0]
        
        row_pre, col_pre = src_pre.index(lhonak_x, lhonak_y)
        print(f"South Lhonak WGS84: ({lhonak_lon}, {lhonak_lat}) -> UTM 45N: ({lhonak_x:.2f}, {lhonak_y:.2f})")
        print(f"Raster Grid Row: {row_pre}, Col: {col_pre}")
        
    with rasterio.open(path_post) as src_post:
        post_water = src_post.read(1)
        transform_post = src_post.transform
        
    pixel_area_m2 = res_pre[0] * res_pre[1]
    print(f"Pixel Resolution: {res_pre[0]:.4f}m x {res_pre[1]:.4f}m = {pixel_area_m2:.4f} m² per pixel")
    
    # Connected component analysis for Pre-flood
    lbl_pre, n_pre = ndimage.label(pre_water == 1)
    target_label_pre = lbl_pre[row_pre, col_pre]
    
    # If exact center pixel isn't 1, search 15-pixel radius
    if target_label_pre == 0:
        patch = lbl_pre[max(0, row_pre-15):row_pre+15, max(0, col_pre-15):col_pre+15]
        nonzeros = patch[patch > 0]
        if len(nonzeros) > 0:
            target_label_pre = np.bincount(nonzeros).argmax()
            
    print(f"\n--- PRE-FLOOD (2023-09-26) ---")
    print(f"Total scene water pixels: {(pre_water == 1).sum()} ({((pre_water == 1).sum() * pixel_area_m2)/1e6:.3f} km²)")
    print(f"South Lhonak Lake component label: {target_label_pre}")
    
    lake_pixels_pre = (lbl_pre == target_label_pre).sum()
    lake_area_pre_m2 = lake_pixels_pre * pixel_area_m2
    lake_area_pre_km2 = lake_area_pre_m2 / 1e6
    lake_area_pre_ha = lake_area_pre_m2 / 1e4
    print(f"South Lhonak Lake (Pre): {lake_pixels_pre} pixels = {lake_area_pre_m2:,.2f} m² = {lake_area_pre_ha:.2f} ha = {lake_area_pre_km2:.3f} km²")
    
    # Connected component analysis for Post-flood
    lbl_post, n_post = ndimage.label(post_water == 1)
    target_label_post = lbl_post[row_pre, col_pre]
    if target_label_post == 0:
        patch = lbl_post[max(0, row_pre-15):row_pre+15, max(0, col_pre-15):col_pre+15]
        nonzeros = patch[patch > 0]
        if len(nonzeros) > 0:
            target_label_post = np.bincount(nonzeros).argmax()
            
    print(f"\n--- POST-FLOOD (2023-10-09) ---")
    print(f"Total scene water pixels: {(post_water == 1).sum()} ({((post_water == 1).sum() * pixel_area_m2)/1e6:.3f} km²)")
    print(f"South Lhonak Lake component label: {target_label_post}")
    
    lake_pixels_post = (lbl_post == target_label_post).sum()
    lake_area_post_m2 = lake_pixels_post * pixel_area_m2
    lake_area_post_km2 = lake_area_post_m2 / 1e6
    lake_area_post_ha = lake_area_post_m2 / 1e4
    print(f"South Lhonak Lake (Post): {lake_pixels_post} pixels = {lake_area_post_m2:,.2f} m² = {lake_area_post_ha:.2f} ha = {lake_area_post_km2:.3f} km²")
    
    diff_pixels = lake_pixels_post - lake_pixels_pre
    diff_area_m2 = lake_area_post_m2 - lake_area_pre_m2
    diff_area_ha = lake_area_post_ha - lake_area_pre_ha
    pct_change = (diff_area_m2 / lake_area_pre_m2) * 100
    
    print(f"\n--- CHANGE ANALYSIS (Lake-Only Clipped) ---")
    print(f"Delta pixels: {diff_pixels:+d}")
    print(f"Delta area: {diff_area_m2:+,.2f} m² ({diff_area_ha:+.2f} ha, {diff_area_m2/1e6:+.3f} km²)")
    print(f"Percentage Change: {pct_change:+.2f}%")

if __name__ == '__main__':
    analyze_satellite_data()
