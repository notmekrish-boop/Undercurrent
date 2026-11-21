/**
 * API Client service for Project Undercurrent.
 * Connects React frontend to FastAPI backend.
 */

const API_BASE = '/api';

export const UndercurrentAPI = {
  getHealth: async () => {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },
  getStudyArea: async () => {
    const res = await fetch(`${API_BASE}/study-area`);
    return res.json();
  },
  getLakes: async () => {
    const res = await fetch(`${API_BASE}/lakes`);
    return res.json();
  },
  getLakeHistory: async (lakeId = 'GL-SK-01') => {
    const res = await fetch(`${API_BASE}/lakes/${lakeId}/history`);
    return res.json();
  },
  compareLakeDates: async (lakeId, date1, date2) => {
    const res = await fetch(`${API_BASE}/lakes/${lakeId}/compare?date1=${date1}&date2=${date2}`);
    return res.json();
  },
  getReservoirs: async () => {
    const res = await fetch(`${API_BASE}/reservoirs`);
    return res.json();
  },
  getReservoirHistory: async (resId = 'RES-TK-01') => {
    const res = await fetch(`${API_BASE}/reservoirs/${resId}/history`);
    return res.json();
  },
  getExposureSummary: async (studyAreaId = 'SA-TEESTA-01') => {
    const res = await fetch(`${API_BASE}/exposure/${studyAreaId}`);
    return res.json();
  },
  getElevationProfile: async (studyAreaId = 'SA-TEESTA-01') => {
    const res = await fetch(`${API_BASE}/exposure/${studyAreaId}/profile`);
    return res.json();
  },
  getExposedAssets: async (studyAreaId = 'SA-TEESTA-01') => {
    const res = await fetch(`${API_BASE}/exposure/${studyAreaId}/assets`);
    return res.json();
  },
  getMapLayers: async () => {
    const res = await fetch(`${API_BASE}/map/layers`);
    return res.json();
  },
  getLayerGeoJSON: async (layerName) => {
    const res = await fetch(`${API_BASE}/map/geojson/${layerName}`);
    return res.json();
  },
  getAlerts: async () => {
    const res = await fetch(`${API_BASE}/alerts`);
    return res.json();
  },
  calculateNDWI: async (payload) => {
    const res = await fetch(`${API_BASE}/analysis/ndwi`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return res.json();
  }
};
