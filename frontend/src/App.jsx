import React, { useState, useEffect, useRef } from 'react';
import { UndercurrentAPI } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [health, setHealth] = useState(null);
  const [lakes, setLakes] = useState([]);
  const [lakeHistory, setLakeHistory] = useState([]);
  const [selectedLakeDate, setSelectedLakeDate] = useState('2023-10-04');
  const [ndwiThreshold, setNdwiThreshold] = useState(0.14);
  const [reservoirs, setReservoirs] = useState([]);
  const [selectedResId, setSelectedResId] = useState('RES-TK-01');
  const [resHistory, setResHistory] = useState([]);
  const [exposureSummary, setExposureSummary] = useState(null);
  const [elevationProfile, setElevationProfile] = useState([]);
  const [assets, setAssets] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const canvasRef = useRef(null);

  useEffect(() => {
    UndercurrentAPI.getHealth().then(setHealth).catch(console.error);
    UndercurrentAPI.getLakes().then(setLakes).catch(console.error);
    UndercurrentAPI.getLakeHistory('GL-SK-01').then(data => setLakeHistory(data.history || [])).catch(console.error);
    UndercurrentAPI.getReservoirs().then(setReservoirs).catch(console.error);
    UndercurrentAPI.getReservoirHistory('RES-TK-01').then(data => setResHistory(data.history || [])).catch(console.error);
    UndercurrentAPI.getExposureSummary('SA-TEESTA-01').then(setExposureSummary).catch(console.error);
    UndercurrentAPI.getElevationProfile('SA-TEESTA-01').then(data => setElevationProfile(data.profile || [])).catch(console.error);
    UndercurrentAPI.getExposedAssets('SA-TEESTA-01').then(data => setAssets(data.assets || [])).catch(console.error);
    UndercurrentAPI.getAlerts().then(setAlerts).catch(console.error);

    const handleFsChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFsChange);
    return () => document.removeEventListener('fullscreenchange', handleFsChange);
  }, []);

  // Update reservoir history when selector changes
  const handleReservoirChange = (resId) => {
    setSelectedResId(resId);
    UndercurrentAPI.getReservoirHistory(resId).then(data => setResHistory(data.history || [])).catch(console.error);
  };

  // Draw NDWI Simulation Canvas
  useEffect(() => {
    if (activeTab === 'lakes' && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      const size = 24;
      const pxSize = canvas.width / size;
      const isPost = selectedLakeDate.includes('2023-10');

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const cy = size / 2;
      const cx = size / 2;
      const ry = isPost ? size * 0.26 : size * 0.32;
      const rx = isPost ? size * 0.30 : size * 0.42;

      for (let i = 0; i < size; i++) {
        for (let j = 0; j < size; j++) {
          const dy = (i - cy) / ry;
          const dx = (j - cx) / rx;
          let distSq = dy * dy + dx * dx;
          if (isPost && dx > 0.15) {
            distSq += (dx - 0.15) * 2.2;
          }

          let ndwi = 0;
          if (distSq <= 0.80) {
            ndwi = 0.38 + 0.12 * Math.cos(i * 0.3) * Math.sin(j * 0.3);
          } else if (distSq <= 1.05) {
            let t = (distSq - 0.80) / 0.25;
            ndwi = (1.0 - t) * 0.35 + t * 0.05;
          } else if (distSq <= 1.35) {
            ndwi = -0.05;
          } else {
            ndwi = -0.28;
          }

          if (ndwi >= ndwiThreshold) {
            ctx.fillStyle = '#0ea5e9';
          } else if (isPost && dx > 0.15 && distSq <= 1.4) {
            ctx.fillStyle = '#b45309';
          } else if (distSq <= 1.3) {
            ctx.fillStyle = '#334155';
          } else {
            ctx.fillStyle = '#1e293b';
          }

          ctx.fillRect(j * pxSize, i * pxSize, pxSize - 1, pxSize - 1);
        }
      }
    }
  }, [activeTab, selectedLakeDate, ndwiThreshold]);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(console.error);
    } else {
      if (document.exitFullscreen) document.exitFullscreen();
    }
  };

  const currentLakeObs = lakeHistory.find(d => d.date === selectedLakeDate) || lakeHistory[0] || {
    area_km2: 1.031,
    sensor: 'Sentinel-2 MSI',
    quality_flag: 'Valid',
    area_change_km2: -0.651,
    area_change_pct: -38.7
  };

  return (
    <div className="min-h-screen w-full bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Header - Widescreen 16:9 */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50 w-full">
        <div className="w-full px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 via-cyan-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-sky-500/20 font-bold text-white text-lg">
              U
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-sky-400 via-cyan-300 to-blue-200 bg-clip-text text-transparent">UNDERCURRENT</span>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-sky-950 border border-sky-800 text-sky-400">Geospatial Intelligence</span>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-950 border border-indigo-800 text-indigo-300 font-mono">16:9 Fullscreen</span>
              </div>
              <p className="text-xs text-slate-400">Himalayan Water Intelligence & Glacial Risk Monitoring System</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <span className="hidden sm:inline px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300">
              Basin: <strong className="text-sky-400">Teesta River (Sikkim)</strong>
            </span>
            <button
              onClick={toggleFullscreen}
              className="px-3 py-1.5 rounded-lg bg-sky-950 border border-sky-800 text-sky-300 hover:bg-sky-900 transition flex items-center gap-1.5"
            >
              <span>{isFullscreen ? 'Exit Fullscreen' : '16:9 Fullscreen'}</span>
            </button>
            <a href="/api/docs" target="_blank" className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition">
              FastAPI Swagger
            </a>
          </div>
        </div>

        {/* Prototype Disclaimer */}
        <div className="bg-amber-950/60 border-t border-b border-amber-500/20 px-4 py-1.5 text-center text-xs text-amber-200">
          <strong>Important Positioning:</strong> Undercurrent is a prototype for monitoring and preliminary exposure screening. It is not an operational GLOF early-warning system or substitute for official disaster-management authorities.
        </div>

        {/* Navigation Tabs (Full Width, Fully Clickable) */}
        <div className="w-full px-4 sm:px-6 lg:px-8 flex space-x-1 py-1.5 overflow-x-auto text-sm border-b border-slate-800/50 bg-slate-900/40">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'lakes', label: 'Glacial Lake Monitor' },
            { id: 'reservoirs', label: 'Reservoir Water Spread' },
            { id: 'exposure', label: 'Downstream Exposure' },
            { id: 'gis-map', label: 'Interactive GIS Map' },
            { id: 'methodology', label: 'Data & Provenance' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-1.5 rounded-lg font-medium transition cursor-pointer select-none ${
                activeTab === tab.id
                  ? 'bg-sky-950/80 border border-sky-800 text-sky-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Content - Multi-Tab Views */}
      <main className="flex-1 w-full px-4 sm:px-6 lg:px-8 py-5 space-y-6">

        {/* TAB 1: OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Monitored Basin</div>
                <div className="text-lg font-bold text-white mt-1">Teesta River, Sikkim</div>
                <div className="text-xs text-sky-400 mt-0.5">5,200m &rarr; 280m ASL</div>
              </div>
              <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Glacial Lake Target</div>
                <div className="text-lg font-bold text-white mt-1">South Lhonak Lake</div>
                <div className="text-xs text-rose-400 mt-0.5">-38.7% Breached Oct 2023</div>
              </div>
              <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Downstream Reservoir</div>
                <div className="text-lg font-bold text-white mt-1">Chungthang (Teesta-III)</div>
                <div className="text-xs text-amber-400 mt-0.5">Water-spread: 0.241 km²</div>
              </div>
              <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Screening Corridor</div>
                <div className="text-lg font-bold text-sky-400 mt-1">112.4 km</div>
                <div className="text-xs text-emerald-400 mt-0.5">8 Downstream Assets</div>
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
              <div className="xl:col-span-8 space-y-6">
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                  <h2 className="text-lg font-bold text-white mb-2">Core User Journeys</h2>
                  <p className="text-sm text-slate-400 mb-6">Click any journey below to navigate directly into that module:</p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div onClick={() => setActiveTab('lakes')} className="cursor-pointer p-4 rounded-xl bg-slate-950 border border-slate-800 hover:border-sky-500 transition">
                      <div className="text-xs font-semibold text-sky-400 uppercase tracking-wider mb-1">Journey A</div>
                      <h3 className="text-sm font-bold text-white">Glacial Lake Review</h3>
                      <p className="text-xs text-slate-400 mt-1">NDWI calculation, multi-date area comparison, and moraine breach detection.</p>
                      <div className="mt-3 text-xs text-sky-400 font-medium">Launch &rarr;</div>
                    </div>

                    <div onClick={() => setActiveTab('reservoirs')} className="cursor-pointer p-4 rounded-xl bg-slate-950 border border-slate-800 hover:border-cyan-500 transition">
                      <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-1">Journey B</div>
                      <h3 className="text-sm font-bold text-white">Reservoir Water-Spread</h3>
                      <p className="text-xs text-slate-400 mt-1">Seasonal water-spread tracking with area vs volume distinction.</p>
                      <div className="mt-3 text-xs text-cyan-400 font-medium">Inspect &rarr;</div>
                    </div>

                    <div onClick={() => setActiveTab('exposure')} className="cursor-pointer p-4 rounded-xl bg-slate-950 border border-slate-800 hover:border-rose-500 transition">
                      <div className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-1">Journey C</div>
                      <h3 className="text-sm font-bold text-white">Exposure Screening</h3>
                      <p className="text-xs text-slate-400 mt-1">DEM slope, valley elevation profile, and settlement intersections.</p>
                      <div className="mt-3 text-xs text-rose-400 font-medium">Screen &rarr;</div>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                  <h2 className="text-lg font-bold text-white mb-2">Teesta River Basin Context (Sikkim)</h2>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    In October 2023, the sudden outburst of South Lhonak Glacial Lake (~5,200m altitude) cascaded through the steep Lhonak and Zemu Chu gorges, severely overtopping and breaching the 1,200 MW Chungthang Dam (Teesta-III) and damaging bridges and highways down to Singtam and Rangpo.
                  </p>
                </div>
              </div>

              <div className="xl:col-span-4 space-y-6">
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                  <h2 className="text-md font-bold text-white mb-3">Active Anomaly Flags</h2>
                  <div className="space-y-3">
                    {alerts.map(a => (
                      <div key={a.alert_id} className="p-3.5 bg-slate-950 rounded-xl border border-rose-900/50 space-y-2">
                        <div className="flex justify-between items-center text-xs">
                          <span className="px-2 py-0.5 rounded bg-rose-900/80 text-rose-300 font-bold">{a.level}</span>
                          <span className="text-slate-400 font-mono">{a.observation_date}</span>
                        </div>
                        <div className="text-sm font-semibold text-slate-200">{a.target_name}</div>
                        <p className="text-xs text-slate-400">{a.summary}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: GLACIAL LAKE MONITOR */}
        {activeTab === 'lakes' && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
              <div>
                <h2 className="text-xl font-bold text-white">South Lhonak Glacial Lake Review</h2>
                <p className="text-xs text-slate-400">Lat: 27.9128° N | Lon: 88.2045° E | Altitude: 5,200 m ASL | CRS: EPSG:32645</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Date:</span>
                <select
                  value={selectedLakeDate}
                  onChange={(e) => setSelectedLakeDate(e.target.value)}
                  className="bg-slate-950 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 font-mono"
                >
                  <option value="2023-09-17">2023-09-17 (Pre-Event Peak - 1.68 km²)</option>
                  <option value="2023-10-04">2023-10-04 (Post-Outburst Breach - 1.03 km²)</option>
                  <option value="2021-10-12">2021-10-12 (Baseline - 1.49 km²)</option>
                  <option value="2019-10-05">2019-10-05 (Baseline - 1.35 km²)</option>
                  <option value="2013-10-18">2013-10-18 (Landsat - 0.98 km²)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Surface Area</div>
                <div className="text-2xl font-bold text-sky-400 mt-1 font-mono">{currentLakeObs.area_km2} km²</div>
              </div>
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Area Delta</div>
                <div className="text-2xl font-bold text-rose-400 mt-1 font-mono">{currentLakeObs.area_change_km2 || '0.00'} km²</div>
                <div className="text-xs text-rose-400">{currentLakeObs.area_change_pct ? `${currentLakeObs.area_change_pct}%` : 'Baseline'}</div>
              </div>
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Sensor</div>
                <div className="text-sm font-bold text-slate-200 mt-1">{currentLakeObs.sensor}</div>
              </div>
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Method</div>
                <div className="text-sm font-bold text-slate-200 mt-1">NDWI &ge; {ndwiThreshold}</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-5 bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-sm font-bold text-white">NDWI Water Classification Grid</h3>
                  <span className="text-xs font-mono bg-sky-950 border border-sky-800 text-sky-300 px-2 py-0.5 rounded">
                    Cutoff: {ndwiThreshold.toFixed(2)}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.25"
                  step="0.01"
                  value={ndwiThreshold}
                  onChange={(e) => setNdwiThreshold(parseFloat(e.target.value))}
                  className="w-full accent-sky-500 cursor-pointer"
                />
                <div className="flex justify-center p-2 bg-slate-900 border border-slate-800 rounded-lg">
                  <canvas ref={canvasRef} width="320" height="320" className="rounded" />
                </div>
              </div>

              <div className="lg:col-span-7 bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3">
                <h3 className="text-sm font-bold text-white">Multi-Date Historical Observations</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-slate-300">
                    <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                      <tr>
                        <th className="py-2.5 px-3">Date</th>
                        <th className="py-2.5 px-3">Sensor</th>
                        <th className="py-2.5 px-3">Area (km²)</th>
                        <th className="py-2.5 px-3">Quality</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {lakeHistory.map(obs => (
                        <tr key={obs.observation_id} className="hover:bg-slate-900/50">
                          <td className="py-2.5 px-3 font-mono">{obs.date}</td>
                          <td className="py-2.5 px-3">{obs.sensor}</td>
                          <td className="py-2.5 px-3 font-mono font-bold text-sky-400">{obs.area_km2}</td>
                          <td className="py-2.5 px-3 text-emerald-400">{obs.quality_flag}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: RESERVOIR MONITOR */}
        {activeTab === 'reservoirs' && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
              <div>
                <h2 className="text-xl font-bold text-white">Downstream Reservoir Water-Spread Variations</h2>
                <p className="text-xs text-slate-400">Monitoring Teesta-III Chungthang Dam & Teesta-V Dam (Dikchu)</p>
              </div>
              <select
                value={selectedResId}
                onChange={(e) => handleReservoirChange(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 font-mono"
              >
                <option value="RES-TK-01">Teesta-III Chungthang Dam (Breached Oct 2023)</option>
                <option value="RES-TK-02">Teesta-V Dikchu Dam (NHPC)</option>
              </select>
            </div>

            <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-800/50 text-xs text-slate-300">
              <strong>Scientific Distinction: Water-Spread vs Storage Volume:</strong> Optical imagery measures water-spread surface area, which is <strong>NOT direct storage volume</strong>. Undercurrent reports water-spread to maintain scientific defensibility.
            </div>

            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-white">Multi-Date Water-Spread History</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Date</th>
                      <th className="py-2.5 px-3">Season / Context</th>
                      <th className="py-2.5 px-3">Water Spread</th>
                      <th className="py-2.5 px-3">Quality Note</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {resHistory.map(obs => (
                      <tr key={obs.observation_id} className="hover:bg-slate-900/50">
                        <td className="py-2.5 px-3 font-mono">{obs.date}</td>
                        <td className="py-2.5 px-3">{obs.season}</td>
                        <td className="py-2.5 px-3 font-mono font-bold text-cyan-400">{obs.water_spread_area_km2} km²</td>
                        <td className="py-2.5 px-3 text-slate-400">{obs.quality_flag}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: EXPOSURE SCREENING */}
        {activeTab === 'exposure' && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div className="flex justify-between items-center pb-4 border-b border-slate-800">
              <div>
                <h2 className="text-xl font-bold text-white">Downstream Exposure Screening</h2>
                <p className="text-xs text-slate-400">112.4 km corridor from South Lhonak (5,200m) to Rangpo (280m)</p>
              </div>
              <span className="px-3 py-1 bg-rose-950 border border-rose-800 text-rose-300 text-xs rounded-lg font-mono font-bold">
                Elevation Drop: 4,920 m
              </span>
            </div>

            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-white">Valley DEM Elevation Profile (5,200m &rarr; 280m)</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Distance (km)</th>
                      <th className="py-2.5 px-3">Elevation (m ASL)</th>
                      <th className="py-2.5 px-3">Slope</th>
                      <th className="py-2.5 px-3">Landmark Point</th>
                      <th className="py-2.5 px-3">Zone Classification</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {elevationProfile.map((pt, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/50">
                        <td className="py-2.5 px-3 font-mono">{pt.distance_km} km</td>
                        <td className="py-2.5 px-3 font-mono text-sky-400 font-bold">{pt.elevation_m} m</td>
                        <td className="py-2.5 px-3 font-mono">{pt.slope_deg}°</td>
                        <td className="py-2.5 px-3 font-semibold text-slate-100">{pt.landmark}</td>
                        <td className="py-2.5 px-3 text-slate-400">{pt.zone}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-white">Screened Assets & Settlements</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-900 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Asset</th>
                      <th className="py-2.5 px-3">Category</th>
                      <th className="py-2.5 px-3">Dist from Lake</th>
                      <th className="py-2.5 px-3">Rating</th>
                      <th className="py-2.5 px-3">Vulnerability Context</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {assets.map(a => (
                      <tr key={a.id} className="hover:bg-slate-900/50">
                        <td className="py-2.5 px-3 font-semibold text-slate-100">{a.name}</td>
                        <td className="py-2.5 px-3 text-slate-400">{a.category}</td>
                        <td className="py-2.5 px-3 font-mono">{a.distance_from_lake_km} km</td>
                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${
                            a.exposure_rating === 'Critical' ? 'bg-rose-950 text-rose-300 border-rose-800' : 'bg-amber-950 text-amber-300 border-amber-800'
                          }`}>
                            {a.exposure_rating}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-400">{a.key_vulnerability}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: INTERACTIVE GIS MAP */}
        {activeTab === 'gis-map' && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <h2 className="text-xl font-bold text-white">Interactive GIS Map & Geospatial Layers</h2>
              <span className="text-xs text-sky-400 font-mono">Teesta Basin GIS</span>
            </div>
            <div className="w-full h-[600px] rounded-xl overflow-hidden border border-slate-800 bg-slate-950">
              <iframe src="/#gis-map" className="w-full h-full border-0" title="Undercurrent GIS Map" />
            </div>
          </div>
        )}

        {/* TAB 6: DATA & PROVENANCE */}
        {activeTab === 'methodology' && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6">
            <h2 className="text-xl font-bold text-white">Scientific Methodology & Data Sources</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <div className="text-xs font-bold text-sky-400">NDWI Formula</div>
                <div className="p-3 bg-slate-900 rounded font-mono text-sm text-sky-200">NDWI = (Green - NIR) / (Green + NIR)</div>
                <p className="text-xs text-slate-400">Sentinel-2 Band 3 (560nm) and Band 8 (842nm) at 10m spatial resolution.</p>
              </div>
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <div className="text-xs font-bold text-sky-400">Percentage Area Change</div>
                <div className="p-3 bg-slate-900 rounded font-mono text-sm text-sky-200">% Change = ((A_later - A_earlier) / A_earlier) &times; 100</div>
                <p className="text-xs text-slate-400">Projected in UTM Zone 45N (EPSG:32645) planar coordinate system.</p>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 py-4 text-center text-xs text-slate-500 w-full">
        <div className="w-full px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Project Undercurrent &bull; Himalayan Water Intelligence & Glacial Risk Monitoring</span>
          <span>Teesta River Basin (Sikkim) &bull; ISRO Bhuvan & Copernicus Space Data</span>
        </div>
      </footer>
    </div>
  );
}
