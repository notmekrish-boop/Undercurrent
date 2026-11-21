import rasterio
import numpy as np

def inspect_spectral_bands():
    # Load 26 Sept bands
    with rasterio.open(r'data\raw\satellite\2023-09-26_B03.tiff.tiff') as s: b03_pre = s.read(1).astype(float)
    with rasterio.open(r'data\raw\satellite\2023-09-26_B08.tiff.tiff') as s: b08_pre = s.read(1).astype(float)
    with rasterio.open(r'data\raw\satellite\2023-09-26_B11.tiff.tiff') as s: b11_pre = s.read(1).astype(float)
    
    # Load 09 Oct bands
    with rasterio.open(r'data\raw\satellite\2023-10-09_B03.tiff.tiff') as s: b03_post = s.read(1).astype(float)
    with rasterio.open(r'data\raw\satellite\2023-10-09_B08.tiff.tiff') as s: b08_post = s.read(1).astype(float)
    with rasterio.open(r'data\raw\satellite\2023-10-09_B11.tiff.tiff') as s: b11_post = s.read(1).astype(float)
    
    # Calculate NDWI = (B03 - B08) / (B03 + B08)
    ndwi_pre = np.where((b03_pre + b08_pre) > 0, (b03_pre - b08_pre) / (b03_pre + b08_pre), -1)
    ndwi_post = np.where((b03_post + b08_post) > 0, (b03_post - b08_post) / (b03_post + b08_post), -1)
    
    # Calculate MNDWI = (B03 - B11) / (B03 + B11)
    mndwi_pre = np.where((b03_pre + b11_pre) > 0, (b03_pre - b11_pre) / (b03_pre + b11_pre), -1)
    mndwi_post = np.where((b03_post + b11_post) > 0, (b03_post - b11_post) / (b03_post + b11_post), -1)
    
    print(f"Pre-flood B03 (Green): min={b03_pre.min()}, max={b03_pre.max()}, mean={b03_pre.mean():.1f}")
    print(f"Pre-flood B08 (NIR): min={b08_pre.min()}, max={b08_pre.max()}, mean={b08_pre.mean():.1f}")
    print(f"Pre-flood B11 (SWIR): min={b11_pre.min()}, max={b11_pre.max()}, mean={b11_pre.mean():.1f}")
    print(f"Pre NDWI min={ndwi_pre.min():.2f}, max={ndwi_pre.max():.2f}, mean={ndwi_pre.mean():.2f}")
    print(f"Post NDWI min={ndwi_post.min():.2f}, max={ndwi_post.max():.2f}, mean={ndwi_post.mean():.2f}")
    print(f"Pre MNDWI min={mndwi_pre.min():.2f}, max={mndwi_pre.max():.2f}, mean={mndwi_pre.mean():.2f}")
    print(f"Post MNDWI min={mndwi_post.min():.2f}, max={mndwi_post.max():.2f}, mean={mndwi_post.mean():.2f}")

if __name__ == '__main__':
    inspect_spectral_bands()
