import rasterio
import numpy as np
from scipy import ndimage

def analyze_post_lake():
    # Read pre and post bands in the lake bounding box
    r1, r2 = 320, 450
    c1, c2 = 310, 620
    
    with rasterio.open(r'data\raw\satellite\2023-09-26_B03.tiff.tiff') as s: b03_pre = s.read(1)[r1:r2, c1:c2].astype(float)
    with rasterio.open(r'data\raw\satellite\2023-09-26_B08.tiff.tiff') as s: b08_pre = s.read(1)[r1:r2, c1:c2].astype(float)
    with rasterio.open(r'data\raw\satellite\2023-09-26_B11.tiff.tiff') as s: b11_pre = s.read(1)[r1:r2, c1:c2].astype(float)
    
    with rasterio.open(r'data\raw\satellite\2023-10-09_B03.tiff.tiff') as s: b03_post = s.read(1)[r1:r2, c1:c2].astype(float)
    with rasterio.open(r'data\raw\satellite\2023-10-09_B08.tiff.tiff') as s: b08_post = s.read(1)[r1:r2, c1:c2].astype(float)
    with rasterio.open(r'data\raw\satellite\2023-10-09_B11.tiff.tiff') as s: b11_post = s.read(1)[r1:r2, c1:c2].astype(float)
    
    # NDWI = (B03 - B08) / (B03 + B08)
    ndwi_pre = (b03_pre - b08_pre) / np.maximum(b03_pre + b08_pre, 1e-6)
    ndwi_post = (b03_post - b08_post) / np.maximum(b03_post + b08_post, 1e-6)
    
    # MNDWI = (B03 - B11) / (B03 + B11)
    mndwi_pre = (b03_pre - b11_pre) / np.maximum(b03_pre + b11_pre, 1e-6)
    mndwi_post = (b03_post - b11_post) / np.maximum(b03_post + b11_post, 1e-6)
    
    # Also read the QGIS water masks in the same box
    with rasterio.open(r'data\raw\satellite\Water_2023-09-26.tiff') as s: w_pre = s.read(1)[r1:r2, c1:c2]
    with rasterio.open(r'data\raw\satellite\Water_2023-10-09.tiff') as s: w_post = s.read(1)[r1:r2, c1:c2]
    
    print(f"Lake Window size: {r2-r1} rows x {c2-c1} cols = {(r2-r1)*(c2-c1)} pixels")
    print(f"Pre-flood Water mask pixels in lake box: {(w_pre == 1).sum()}")
    print(f"Post-flood Water mask pixels in lake box: {(w_post == 1).sum()}")
    
    # Let's test different NDWI thresholds for Post-flood
    print("\nPost-flood pixels at different NDWI thresholds:")
    for t in [0.0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]:
        count = (ndwi_post > t).sum()
        area_km2 = count * 100.02 / 1e6
        print(f"  NDWI > {t:.2f}: {count} pixels ({area_km2:.3f} km²)")
        
    print("\nPost-flood pixels at different MNDWI thresholds:")
    for t in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        count = (mndwi_post > t).sum()
        area_km2 = count * 100.02 / 1e6
        print(f"  MNDWI > {t:.2f}: {count} pixels ({area_km2:.3f} km²)")
        
    # Analyze the difference: where was water on 26 Sep that is NOT water on 09 Oct?
    # Or where did NDWI drop?
    ndwi_drop = ndwi_pre - ndwi_post
    print(f"\nAverage NDWI in pre-lake area on 26 Sep: {ndwi_pre[w_pre == 1].mean():.3f}")
    print(f"Average NDWI in pre-lake area on 09 Oct: {ndwi_post[w_pre == 1].mean():.3f}")
    print(f"Average MNDWI in pre-lake area on 26 Sep: {mndwi_pre[w_pre == 1].mean():.3f}")
    print(f"Average MNDWI in pre-lake area on 09 Oct: {mndwi_post[w_pre == 1].mean():.3f}")

if __name__ == '__main__':
    analyze_post_lake()
