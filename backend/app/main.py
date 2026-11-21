"""
Main application entry point for Project Undercurrent.
Undercurrent: Himalayan Water Intelligence & Glacial Risk Monitoring System
ASTRA 2026 Space Hackathon Prototype
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes import health, lakes, reservoirs, exposure, maps, alerts, analysis
from .services.data_service import data_service

app = FastAPI(
    title="Undercurrent - Himalayan Water Intelligence & Glacial Risk Monitoring System",
    description="Satellite-data-driven geospatial intelligence platform connecting upstream glacial-lake change monitoring, downstream exposure screening, and reservoir water-spread monitoring.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Enable CORS for local dev servers (e.g. Vite on port 5173 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health.router, prefix="/api")
app.include_router(lakes.router, prefix="/api")
app.include_router(reservoirs.router, prefix="/api")
app.include_router(exposure.router, prefix="/api")
app.include_router(maps.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")

@app.get("/api/study-area", tags=["Study Area"])
def get_study_area():
    return data_service.get_study_area()

@app.get("/api/catalogue", tags=["Data Provenance"])
def get_catalogue():
    return data_service.get_catalogue()

# Static files for frontend dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def serve_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "project": "Undercurrent",
        "description": "Himalayan Water Intelligence & Glacial Risk Monitoring System",
        "api_docs": "/api/docs",
        "health_check": "/api/health"
    }
