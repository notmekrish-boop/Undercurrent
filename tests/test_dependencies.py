"""
Clean installation and dependency import verification test for Project Undercurrent.
Validates that all packages specified in backend/requirements.txt are installed,
importable, and functional in the Python runtime environment without requiring pytest.
"""
import sys

def test_core_dependencies_importable():
    # FastAPI & web server
    import fastapi
    import uvicorn
    import pydantic
    assert fastapi.__version__ is not None
    assert uvicorn.__version__ is not None
    assert pydantic.__version__ is not None

def test_data_science_dependencies():
    import numpy as np
    import pandas as pd
    import requests
    assert np.__version__ is not None
    assert pd.__version__ is not None
    assert requests.__version__ is not None

def test_geospatial_rasterio_dependency():
    import rasterio
    from rasterio.warp import transform_geom
    from rasterio.features import rasterize
    assert rasterio.__version__ is not None

def test_scipy_ndimage_dependency():
    import numpy as np
    import scipy
    from scipy import ndimage
    assert scipy.__version__ is not None
    
    # Verify morphological labeling function used for lake isolation
    test_arr = np.array([[0, 1, 1], [0, 1, 0], [0, 0, 0]], dtype=np.uint8)
    lbl, num = ndimage.label(test_arr)
    assert num == 1
    assert lbl[0, 1] == 1

if __name__ == "__main__":
    test_core_dependencies_importable()
    test_data_science_dependencies()
    test_geospatial_rasterio_dependency()
    test_scipy_ndimage_dependency()
    print("ALL DEPENDENCY IMPORT & FUNCTIONALITY TESTS PASSED!")
