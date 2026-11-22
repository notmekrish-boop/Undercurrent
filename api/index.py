"""
Vercel Serverless Function entrypoint for Project Undercurrent.
Imports the FastAPI instance 'app' from backend.app.main.
"""

import os
import sys

# Ensure repository root is on sys.path for serverless resolution
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.main import app
