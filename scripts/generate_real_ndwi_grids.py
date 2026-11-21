import rasterio
import numpy as np

def generate_real_ndwi_grids():
    r1, r2 = 330, 445
    c1, c2 = 320, 605
    
    with rasterio.open(r'data\raw\satellite\NDWI_2023-09-26.tif') as s:
        ndwi_pre = s.read(1)[r1:r2, c1:c2]
        
    with rasterio.open(r'data\raw\satellite\NDWI_2023-10-09.tiff') as s:
        ndwi_post = s.read(1)[r1:r2, c1:c2]
        
    # Resample to 24x24 using area block averaging
    grid_size = 24
    h, w = ndwi_pre.shape
    bh = h // grid_size
    bw = w // grid_size
    
    grid_pre = np.zeros((grid_size, grid_size), dtype=float)
    grid_post = np.zeros((grid_size, grid_size), dtype=float)
    
    for i in range(grid_size):
        for j in range(grid_size):
            block_pre = ndwi_pre[i*bh:(i+1)*bh, j*bw:(j+1)*bw]
            block_post = ndwi_post[i*bh:(i+1)*bh, j*bw:(j+1)*bw]
            grid_pre[i, j] = float(np.nanmean(block_pre))
            grid_post[i, j] = float(np.nanmean(block_post))
            
    print("Real Sentinel-2 24x24 NDWI grid (Pre-flood, 26 Sep 2023):")
    print(f"  Shape: {grid_pre.shape}, Min: {grid_pre.min():.3f}, Max: {grid_pre.max():.3f}, Mean: {grid_pre.mean():.3f}")
    print("Real Sentinel-2 24x24 NDWI grid (Post-flood, 09 Oct 2023):")
    print(f"  Shape: {grid_post.shape}, Min: {grid_post.min():.3f}, Max: {grid_post.max():.3f}, Mean: {grid_post.mean():.3f}")
    
    # Save as JSON for backend engine
    data = {
        "metadata": {
            "source": "Sentinel-2 MSI Level-2A (ESA Copernicus)",
            "pre_date": "2023-09-26",
            "post_date": "2023-10-09",
            "grid_size": grid_size,
            "crs": "EPSG:32645",
            "aoi": "South Lhonak Lake (27.9128°N, 88.2045°E)",
            "description": "Block-averaged 24x24 real Sentinel-2 multi-spectral NDWI matrix"
        },
        "pre_matrix": np.round(grid_pre, 3).tolist(),
        "post_matrix": np.round(grid_post, 3).tolist()
    }
    
    out_file = r'data\processed\sentinel2_real_ndwi_grids.json'
    import json
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved real satellite NDWI grids to {out_file}!")

if __name__ == '__main__':
    generate_real_ndwi_grids()
