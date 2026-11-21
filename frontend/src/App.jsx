import React, { useState, useEffect } from 'react';
import { UndercurrentAPI } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [health, setHealth] = useState(null);
  const [lakes, setLakes] = useState([]);
  const [reservoirs, setReservoirs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    UndercurrentAPI.getHealth().then(setHealth).catch(console.error);
    UndercurrentAPI.getLakes().then(setLakes).catch(console.error);
    UndercurrentAPI.getReservoirs().then(setReservoirs).catch(console.error);
    UndercurrentAPI.getAlerts().then(setAlerts).catch(console.error);

    const handleFsChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFsChange);
    return () => document.removeEventListener('fullscreenchange', handleFsChange);
  }, []);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(console.error);
    } else {
      if (document.exitFullscreen) document.exitFullscreen();
    }
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
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-sky-950 border border-sky-800 text-sky-400">ASTRA 2026</span>
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

        {/* Navigation Tabs (Full Width) */}
        <div className="w-full px-4 sm:px-6 lg:px-8 flex space-x-2 py-2 overflow-x-auto text-sm">
          {[
            { id: 'overview', label: 'Basin Overview' },
            { id: 'lakes', label: 'Glacial Lake Monitor' },
            { id: 'reservoirs', label: 'Reservoir Water Spread' },
            { id: 'exposure', label: 'Exposure Screening' },
            { id: 'methodology', label: 'Methodology & Data' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-1.5 rounded-lg font-medium transition ${
                activeTab === tab.id
                  ? 'bg-sky-950 border border-sky-800 text-sky-400'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Content - Expanded 16:9 Grid */}
      <main className="flex-1 w-full px-4 sm:px-6 lg:px-8 py-5 space-y-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">System Status</div>
                <div className="text-lg font-bold text-emerald-400 mt-1">{health?.status ? 'Online & Monitored' : 'Connecting...'}</div>
                <div className="text-xs text-slate-500 mt-0.5">Teesta River Basin</div>
              </div>
              <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Glacial Lake Target</div>
                <div className="text-lg font-bold text-white mt-1">South Lhonak Lake</div>
                <div className="text-xs text-rose-400 mt-0.5">-38.7% Breached Oct 2023</div>
              </div>
              <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Downstream Reservoir</div>
                <div className="text-lg font-bold text-white mt-1">Chungthang (Teesta-III)</div>
                <div className="text-xs text-amber-400 mt-0.5">Dam Breached Oct 2023</div>
              </div>
              <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                <div className="text-xs text-slate-400">Screening Corridor</div>
                <div className="text-lg font-bold text-sky-400 mt-1">112.4 km</div>
                <div className="text-xs text-slate-400 mt-0.5">8 Downstream Assets</div>
              </div>
            </div>

            <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-2xl space-y-4">
              <h2 className="text-lg font-bold text-white">Active Rule-Based Screening Flags</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {alerts.map(a => (
                  <div key={a.alert_id} className="p-4 bg-slate-950 rounded-xl border border-rose-900/40 space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="px-2 py-0.5 rounded bg-rose-900/80 text-rose-300 font-bold">{a.level}</span>
                      <span className="text-slate-400 font-mono">{a.observation_date}</span>
                    </div>
                    <div className="text-sm font-semibold text-slate-200">{a.summary}</div>
                    <div className="text-xs text-slate-400 font-mono">Rule: {a.rule_applied}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab !== 'overview' && (
          <div className="p-8 bg-slate-900/80 border border-slate-800 rounded-2xl text-center space-y-4">
            <h3 className="text-lg font-bold text-slate-200">Interactive 16:9 View Ready</h3>
            <p className="text-sm text-slate-400">
              The full geospatial dashboard with Leaflet GIS map, NDWI threshold slider, DEM elevation profile, and multi-date analysis is served at the root URL (<code>/</code>) via FastAPI.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
