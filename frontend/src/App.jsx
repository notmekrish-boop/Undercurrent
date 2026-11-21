import React, { useState, useEffect, useRef } from 'react';
import { UndercurrentAPI } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [health, setHealth] = useState(null);
  const [lakes, setLakes] = useState([]);
  const [lakeHistory, setLakeHistory] = useState([]);
  const [selectedLakeDate, setSelectedLakeDate] = useState('2023-10-09');
  const [ndwiThreshold, setNdwiThreshold] = useState(0.14);
  const [reservoirs, setReservoirs] = useState([]);
  const [selectedResId, setSelectedResId] = useState('RES-TK-01');
  const [resHistory, setResHistory] = useState([]);
  const [exposureSummary, setExposureSummary] = useState(null);
  const [elevationProfile, setElevationProfile] = useState([]);
  const [assets, setAssets] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [activePopover, setActivePopover] = useState(null);
  const [showPalette, setShowPalette] = useState(false);
  const [paletteQuery, setPaletteQuery] = useState('');

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
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setShowPalette(prev => !prev);
      }
      if (e.key === 'Escape') {
        setActivePopover(null);
        setShowPalette(false);
      }
    };
    const handleClickOutside = () => {
      setActivePopover(null);
    };

    document.addEventListener('fullscreenchange', handleFsChange);
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('fullscreenchange', handleFsChange);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('click', handleClickOutside);
    };
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
    area_km2: 1.003,
    sensor: 'Sentinel-2 MSI Level-2A',
    quality_flag: 'Valid (Calibrated Outburst Drainage)',
    area_change_km2: -0.664,
    area_change_pct: -39.84
  };

  return (
    <div className="min-h-screen w-full bg-[#090a0d] text-[#f1f3f7] flex flex-col font-sans">
      {/* Top Unified Header - Matching Reference Command HUD Exactly */}
      <header className="border-b border-white/10 bg-[#0c0e14]/95 backdrop-blur-2xl sticky top-0 z-50 w-full shadow-2xl">
        <div className="w-full px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16 gap-3">
          
          {/* Left: Negative-Space Mountain Logo & Wordmark (Inspired by Gorilla Logo Style) */}
          <div className="flex items-center gap-3 min-w-0">
            {/* Mountain Emblem Badge */}
            <div 
              onClick={() => setActiveTab('overview')} 
              className="w-10 h-10 rounded-xl bg-gradient-to-b from-white/15 to-white/5 border border-white/20 hover:border-cyan-400/60 hover:shadow-[0_0_20px_rgba(56,189,248,0.35)] flex items-center justify-center text-white shadow-inner flex-shrink-0 transition-all cursor-pointer select-none relative overflow-hidden" 
              title="Undercurrent Home"
            >
              <svg width="28" height="28" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                <polygon points="14,26 23,10 32,26" fill="#0284c7" opacity="0.65" />
                <polygon points="23,10 32,26 23,26" fill="#0369a1" opacity="0.85" />
                <polygon points="4,26 15,6 25,26" fill="#ffffff" />
                <polygon points="15,6 25,26 15,26" fill="#475569" />
                <polygon points="15,6 12,12 15,14 18,12" fill="#38bdf8" />
                <polygon points="23,10 21,14 23,15.5 25,14" fill="#7dd3fc" />
                <path d="M2 26 C 7 24, 12 28, 18 26 C 24 24, 28 27, 34 25" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" fill="none" />
                <path d="M5 30 C 10 28, 15 31, 20 29 C 25 28, 29 30, 32 29" stroke="#0ea5e9" strokeWidth="1.4" strokeLinecap="round" fill="none" opacity="0.8" />
              </svg>
            </div>

            {/* Wordmark with Integrated Mountain Silhouette */}
            <div onClick={() => setActiveTab('overview')} className="hidden sm:flex flex-col justify-center cursor-pointer select-none">
              <div className="flex items-center gap-2 leading-none">
                <span className="text-base lg:text-lg font-black tracking-tight text-white flex items-center font-sans">
                  <span>UNDER</span>
                  <span className="inline-flex items-center justify-center mx-0.5 px-0.5">
                    <svg className="w-4 h-4 text-cyan-400 inline-block -mt-0.5 drop-shadow-[0_0_8px_rgba(56,189,248,0.5)]" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2 L2 20 L22 20 Z" fill="#ffffff" />
                      <path d="M12 2 L22 20 L12 20 Z" fill="#0284c7" />
                      <path d="M12 2 L9 9 L12 11 L15 9 Z" fill="#38bdf8" />
                      <path d="M2 22 Q 7 20 12 22 T 22 22" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                  </span>
                  <span className="text-cyan-400">CURRENT</span>
                </span>
                <span className="px-2 py-0.5 text-[10px] font-semibold rounded-full bg-emerald-950/80 border border-emerald-800/80 text-emerald-400 flex items-center gap-1 font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span> Research Prototype
                </span>
              </div>
              <span className="text-[9px] font-mono tracking-widest text-slate-400 uppercase mt-0.5 hidden lg:block">
                Himalayan Water Intelligence
              </span>
            </div>

            <div className="hidden lg:block h-6 w-px bg-white/10 mx-1"></div>

            {/* Navigation Tabs (Directly in Header, matching reference) */}
            <nav className="flex items-center gap-1 overflow-x-auto custom-scrollbar py-1">
              {[
                { id: 'overview', label: 'Live Command' },
                { id: 'lakes', label: 'Lake Monitor' },
                { id: 'reservoirs', label: 'Reservoirs' },
                { id: 'exposure', label: 'Exposure' },
                { id: 'gis-map', label: 'GIS Map' },
                { id: 'methodology', label: 'Methodology' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition cursor-pointer select-none ${
                    activeTab === tab.id
                      ? 'bg-white/15 border border-white/30 text-white shadow-sm'
                      : 'border border-transparent text-slate-400 hover:text-white'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Right: System Info & Interactive Popovers (Zero Browser Subtitles) */}
          <div className="relative flex items-center gap-2.5 flex-shrink-0 text-xs" onClick={(e) => e.stopPropagation()}>
            {/* Search Input / Command Palette Trigger */}
            <div 
              onClick={() => setShowPalette(true)}
              className="hidden xl:flex items-center gap-2 bg-white/5 border border-white/10 hover:border-cyan-400/40 hover:bg-white/10 rounded-full px-3 py-1.5 text-xs text-slate-400 transition cursor-pointer select-none"
            >
              <span className="text-slate-300 w-36 font-normal text-xs">Search target (Ctrl+K)...</span>
            </div>

            {/* Prototype Popover Trigger */}
            <div className="relative">
              <button
                onClick={(e) => { e.stopPropagation(); setActivePopover(activePopover === 'prototype' ? null : 'prototype'); }}
                className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-950/40 border border-amber-500/30 hover:border-amber-400 text-[11px] font-mono text-amber-300 transition cursor-pointer select-none"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span> Prototype
              </button>

              {activePopover === 'prototype' && (
                <div 
                  style={{ background: 'linear-gradient(165deg, rgba(16, 20, 28, 0.96) 0%, rgba(10, 12, 18, 0.97) 100%)', backdropFilter: 'blur(28px) saturate(200%)', WebkitBackdropFilter: 'blur(28px) saturate(200%)' }}
                  className="absolute right-0 top-11 z-50 w-80 sm:w-96 rounded-2xl p-4 border border-amber-500/40 shadow-2xl text-left"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-white/10">
                    <div className="text-xs font-bold text-amber-300 uppercase tracking-wider font-mono">Research Prototype Notice</div>
                    <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300">V1.0</span>
                  </div>
                  <div className="py-3 text-xs text-slate-300 space-y-2">
                    <p>
                      <strong className="text-white">Project Undercurrent</strong> is an academic geospatial intelligence prototype engineered to demonstrate satellite multi-spectral monitoring of glacial lake area dynamics and downstream preliminary exposure screening.
                    </p>
                    <div className="p-2.5 rounded-xl border border-amber-500/30 text-[11px] text-amber-200 leading-normal" style={{ backgroundColor: 'rgba(69, 26, 3, 0.5)' }}>
                      This is a research prototype. It is <strong>not</strong> an operational government GLOF early warning system (EWS) or hydrodynamic flood dispatch model.
                    </div>
                  </div>
                  <div className="pt-2.5 border-t border-white/10 flex items-center justify-between">
                    <button onClick={() => { setActiveTab('methodology'); setActivePopover(null); }} className="text-[11px] text-cyan-400 hover:text-cyan-300 font-mono">
                      Read Methodology &rarr;
                    </button>
                    <button onClick={() => setActivePopover(null)} className="px-2.5 py-1 rounded-lg hover:bg-white/15 text-slate-300 text-[11px]" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                      Dismiss
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Sensors Popover Trigger */}
            <div className="relative">
              <button
                onClick={(e) => { e.stopPropagation(); setActivePopover(activePopover === 'sensors' ? null : 'sensors'); }}
                className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/40 border border-emerald-500/30 hover:border-emerald-400 text-[10px] font-mono text-emerald-300 transition cursor-pointer select-none"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Sensors
              </button>

              {activePopover === 'sensors' && (
                <div 
                  style={{ background: 'linear-gradient(165deg, rgba(16, 20, 28, 0.96) 0%, rgba(10, 12, 18, 0.97) 100%)', backdropFilter: 'blur(28px) saturate(200%)', WebkitBackdropFilter: 'blur(28px) saturate(200%)' }}
                  className="absolute right-0 top-11 z-50 w-80 sm:w-96 rounded-2xl p-4 border border-emerald-500/40 shadow-2xl text-left"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-white/10">
                    <div className="text-xs font-bold text-emerald-300 uppercase tracking-wider font-mono">Earth Observation Feeds</div>
                    <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300">S2 MSI + CartoDEM</span>
                  </div>
                  <div className="py-3 space-y-2 text-xs">
                    <div className="p-2 rounded-xl border border-white/10 flex justify-between" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                      <div>
                        <div className="font-bold text-white text-[11px]">ISRO CartoDEM / Bhuvan</div>
                        <div className="text-[10px] text-slate-400">30m DEM • EPSG:32645</div>
                      </div>
                      <span className="text-emerald-400 font-mono text-[10px] font-bold">Online</span>
                    </div>
                    <div className="p-2 rounded-xl border border-white/10 flex justify-between" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                      <div>
                        <div className="font-bold text-white text-[11px]">ESA Copernicus Sentinel-2</div>
                        <div className="text-[10px] text-slate-400">10m MSI • Green/NIR</div>
                      </div>
                      <span className="text-emerald-400 font-mono text-[10px] font-bold">Active</span>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-white/10 flex justify-end">
                    <button onClick={() => setActivePopover(null)} className="px-2.5 py-1 rounded-lg hover:bg-white/15 text-slate-300 text-[11px]" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                      Close
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Notification Bell with Badge */}
            <div className="relative">
              <button
                onClick={(e) => { e.stopPropagation(); setActivePopover(activePopover === 'alerts' ? null : 'alerts'); }}
                className="w-8 h-8 rounded-full bg-white/5 border border-white/10 hover:border-rose-500/50 flex items-center justify-center text-slate-300 relative transition cursor-pointer"
              >
                <span>🔔</span>
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-rose-500 text-white font-mono text-[9px] font-black flex items-center justify-center">1</span>
              </button>

              {activePopover === 'alerts' && (
                <div 
                  style={{ background: 'linear-gradient(165deg, rgba(16, 20, 28, 0.96) 0%, rgba(10, 12, 18, 0.97) 100%)', backdropFilter: 'blur(28px) saturate(200%)', WebkitBackdropFilter: 'blur(28px) saturate(200%)' }}
                  className="absolute right-0 top-11 z-50 w-80 sm:w-96 rounded-2xl p-4 border border-rose-500/40 shadow-2xl text-left"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-white/10">
                    <div className="text-xs font-bold text-rose-300 uppercase tracking-wider font-mono">Basin Alerts Feed</div>
                    <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 font-bold uppercase">Critical</span>
                  </div>
                  <div className="py-3 text-xs space-y-2">
                    <div className="p-3 rounded-xl border border-rose-500/30 space-y-1" style={{ backgroundColor: 'rgba(76, 5, 25, 0.45)' }}>
                      <div className="font-bold text-white flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span> South Lhonak Moraine Breach
                      </div>
                      <div className="text-[11px] text-slate-300">-0.690 km² (-41.4%) planar surface contraction detected between 26 Sep and 09 Oct 2023. Optical screening; bathymetry required for volume calculation.</div>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-white/10 flex justify-between">
                    <button onClick={() => { setActiveTab('exposure'); setActivePopover(null); }} className="text-[11px] text-cyan-400 hover:text-cyan-300 font-mono">
                      Corridor Exposure &rarr;
                    </button>
                    <button onClick={() => setActivePopover(null)} className="px-2.5 py-1 rounded-lg hover:bg-white/15 text-slate-300 text-[11px]" style={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }}>
                      Acknowledge
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* 16:9 Toggle */}
            <button
              onClick={toggleFullscreen}
              className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-slate-200 hover:text-white transition flex items-center gap-1.5"
            >
              <span>{isFullscreen ? 'Exit' : '16:9'}</span>
            </button>

            {/* Operator Avatar Popover Trigger */}
            <div className="relative">
              <button
                onClick={(e) => { e.stopPropagation(); setActivePopover(activePopover === 'operator' ? null : 'operator'); }}
                className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-600 to-sky-400 border border-white/20 hover:border-cyan-400 flex items-center justify-center text-white font-mono font-bold text-[11px] shadow-sm flex-shrink-0 cursor-pointer transition select-none"
              >
                OP
              </button>

              {activePopover === 'operator' && (
                <div 
                  style={{ background: 'linear-gradient(165deg, rgba(16, 20, 28, 0.96) 0%, rgba(10, 12, 18, 0.97) 100%)', backdropFilter: 'blur(28px) saturate(200%)', WebkitBackdropFilter: 'blur(28px) saturate(200%)' }}
                  className="absolute right-0 top-11 z-50 w-80 rounded-2xl p-4 border border-cyan-500/40 shadow-2xl text-left"
                >
                  <div className="flex items-center gap-3 pb-3 border-b border-white/10">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-600 to-sky-400 border-2 border-cyan-400 flex items-center justify-center text-white font-mono font-bold text-sm">
                      OP
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">Teesta Basin Dispatcher</div>
                      <div className="text-[10px] text-slate-400 font-mono">Analyst ID #OP-01</div>
                    </div>
                  </div>
                  <div className="py-3 space-y-1.5 font-mono text-[11px]">
                    <div className="flex justify-between py-1 border-b border-white/5 text-slate-400">
                      <span>Station:</span>
                      <span className="text-slate-200">Gangtok Operations</span>
                    </div>
                    <div className="flex justify-between py-1 text-slate-400">
                      <span>State:</span>
                      <span className="text-emerald-400 font-bold">100% Online</span>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-white/10">
                    <a href="/api/docs" target="_blank" className="w-full block py-1.5 text-center rounded-lg hover:bg-white/10 text-cyan-300 text-xs transition" style={{ backgroundColor: 'rgba(255, 255, 255, 0.06)' }}>
                      Open API Docs (/api/docs)
                    </a>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Multi-Tab Views */}
      <main className="flex-1 w-full px-4 sm:px-6 lg:px-8 py-5 space-y-6">

        {/* TAB 1: OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-[#161a24]/90 border border-white/10 rounded-2xl shadow-xl">
                <div className="text-xs text-slate-400 font-medium">Monitored Basin</div>
                <div className="text-lg font-bold text-white mt-1">Teesta River, Sikkim</div>
                <div className="text-xs text-cyan-400 mt-0.5 font-mono">5,200m &rarr; 280m ASL</div>
              </div>
              <div className="p-4 bg-[#161a24]/90 border border-white/10 rounded-2xl shadow-xl">
                <div className="text-xs text-slate-400 font-medium">Glacial Lake Target</div>
                <div className="text-lg font-bold text-white mt-1">South Lhonak Lake</div>
                <div className="text-xs text-rose-400 mt-0.5 font-mono">-38.7% Breached Oct 2023</div>
              </div>
              <div className="p-4 bg-[#161a24]/90 border border-white/10 rounded-2xl shadow-xl">
                <div className="text-xs text-slate-400 font-medium">Downstream Reservoir</div>
                <div className="text-lg font-bold text-white mt-1">Chungthang (Teesta-III)</div>
                <div className="text-xs text-amber-400 mt-0.5 font-mono">Water-spread: 0.241 km²</div>
              </div>
              <div className="p-4 bg-[#161a24]/90 border border-white/10 rounded-2xl shadow-xl">
                <div className="text-xs text-slate-400 font-medium">Screening Corridor</div>
                <div className="text-lg font-bold text-cyan-400 mt-1">112.4 km Hydraulic Reach</div>
                <div className="text-xs text-emerald-400 mt-0.5 font-mono">8 Downstream Assets</div>
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
              <div className="xl:col-span-8 space-y-6">
                <div className="bg-[#12141b]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
                  <h2 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span>
                    Core Operational Modules
                  </h2>
                  <p className="text-sm text-slate-400 mb-6">Click any module below to inspect full satellite observations:</p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div onClick={() => setActiveTab('lakes')} className="cursor-pointer p-4 rounded-xl bg-[#161a24]/90 border border-white/10 hover:border-cyan-400 transition-all hover:-translate-y-0.5">
                      <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-1 font-mono">Module 01</div>
                      <h3 className="text-sm font-bold text-white">Glacial Lake Review</h3>
                      <p className="text-xs text-slate-400 mt-1">NDWI calculation, multi-date area comparison, and moraine breach detection.</p>
                      <div className="mt-3 text-xs text-cyan-400 font-medium">Launch &rarr;</div>
                    </div>

                    <div onClick={() => setActiveTab('reservoirs')} className="cursor-pointer p-4 rounded-xl bg-[#161a24]/90 border border-white/10 hover:border-blue-400 transition-all hover:-translate-y-0.5">
                      <div className="text-xs font-semibold text-blue-400 uppercase tracking-wider mb-1 font-mono">Module 02</div>
                      <h3 className="text-sm font-bold text-white">Reservoir Water-Spread</h3>
                      <p className="text-xs text-slate-400 mt-1">Seasonal water-spread tracking with area vs volume distinction.</p>
                      <div className="mt-3 text-xs text-blue-400 font-medium">Inspect &rarr;</div>
                    </div>

                    <div onClick={() => setActiveTab('exposure')} className="cursor-pointer p-4 rounded-xl bg-[#161a24]/90 border border-white/10 hover:border-rose-400 transition-all hover:-translate-y-0.5">
                      <div className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-1 font-mono">Module 03</div>
                      <h3 className="text-sm font-bold text-white">Exposure Screening</h3>
                      <p className="text-xs text-slate-400 mt-1">DEM slope, valley elevation profile, and settlement intersections.</p>
                      <div className="mt-3 text-xs text-rose-400 font-medium">Screen &rarr;</div>
                    </div>
                  </div>
                </div>

                <div className="bg-[#12141b]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
                  <h2 className="text-lg font-bold text-white mb-2">Teesta River Basin Context (Sikkim)</h2>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    In October 2023, the sudden outburst of South Lhonak Glacial Lake (~5,200m altitude) cascaded through the steep Lhonak and Zemu Chu gorges, severely overtopping and breaching the 1,200 MW Chungthang Dam (Teesta-III) and damaging bridges and highways down to Singtam and Rangpo.
                  </p>
                </div>
              </div>

              <div className="xl:col-span-4 space-y-6">
                <div className="bg-[#2d1216]/80 backdrop-blur-xl border border-rose-500/30 rounded-2xl p-6 shadow-2xl">
                  <h2 className="text-md font-bold text-white mb-3 flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block pulse-dot"></span>
                    Active Basin Hazards
                  </h2>
                  <div className="space-y-3">
                    {alerts.map(a => (
                      <div key={a.alert_id} className="p-3.5 bg-black/40 rounded-xl border border-rose-500/30 space-y-2">
                        <div className="flex justify-between items-center text-xs">
                          <span className="px-2 py-0.5 rounded-full bg-rose-950/80 border border-rose-800 text-rose-300 font-bold">{a.level}</span>
                          <span className="text-slate-400 font-mono">{a.observation_date}</span>
                        </div>
                        <div className="text-sm font-semibold text-slate-100">{a.target_name}</div>
                        <p className="text-xs text-slate-300">{a.summary}</p>
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
          <div className="bg-[#12141b]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 space-y-6 shadow-2xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-white/10 gap-4">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span>
                  South Lhonak Glacial Lake Review
                </h2>
                <p className="text-xs text-slate-400 font-mono mt-1">Lat: 27.9128° N | Lon: 88.2045° E | Altitude: 5,200 m ASL | CRS: EPSG:32645</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 font-semibold uppercase">Epoch:</span>
                <select
                  value={selectedLakeDate}
                  onChange={(e) => setSelectedLakeDate(e.target.value)}
                  className="bg-[#131722] border border-white/10 text-slate-200 text-xs rounded-full px-3 py-1.5 font-mono focus:outline-none focus:border-cyan-400"
                >
                  {lakeHistory && lakeHistory.length > 0 ? (
                    lakeHistory.map(obs => (
                      <option key={obs.date} value={obs.date}>
                        {obs.date} ({obs.period || obs.phase || 'Observation'} - {obs.area_km2} km&sup2;)
                      </option>
                    ))
                  ) : (
                    <>
                      <option value="2023-10-09">2023-10-09 (Post-Burst Calibrated - 1.003 km&sup2; / Sentinel-2)</option>
                      <option value="2023-09-26">2023-09-26 (Pre-Burst Baseline - 1.666 km&sup2; / Sentinel-2)</option>
                      <option value="2023-10-04">2023-10-04 (Post-Outburst Breach - 1.031 km&sup2;)</option>
                      <option value="2023-09-17">2023-09-17 (Pre-Event Peak - 1.682 km&sup2;)</option>
                    </>
                  )}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 bg-[#161a24]/90 border border-white/10 rounded-xl">
                <div className="text-xs text-slate-400">Surface Area</div>
                <div className="text-2xl font-black text-cyan-400 mt-1 font-mono">{currentLakeObs.area_km2} km²</div>
              </div>
              <div className="p-4 bg-[#161a24]/90 border border-white/10 rounded-xl">
                <div className="text-xs text-slate-400">Area Delta</div>
                <div className="text-2xl font-black text-rose-400 mt-1 font-mono">{currentLakeObs.area_change_km2 || '0.00'} km²</div>
                <div className="text-xs text-rose-400 font-mono">{currentLakeObs.area_change_pct ? `${currentLakeObs.area_change_pct}%` : 'Baseline'}</div>
              </div>
              <div className="p-4 bg-[#161a24]/90 border border-white/10 rounded-xl">
                <div className="text-xs text-slate-400">Sensor</div>
                <div className="text-sm font-bold text-slate-200 mt-1">{currentLakeObs.sensor}</div>
              </div>
              <div className="p-4 bg-[#161a24]/90 border border-white/10 rounded-xl">
                <div className="text-xs text-slate-400">Method</div>
                <div className="text-sm font-bold text-cyan-200 mt-1 font-mono">NDWI &ge; {ndwiThreshold}</div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-5 bg-[#161a24]/90 border border-white/10 rounded-xl p-5 space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-sm font-bold text-white">NDWI Spectral Simulator (Calibrated Schematic)</h3>
                  <span className="text-xs font-mono bg-cyan-950/80 border border-cyan-800/80 text-cyan-300 px-2.5 py-0.5 rounded-full">
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
                  className="w-full accent-cyan-400 cursor-pointer"
                />
                <div className="flex justify-center p-3 bg-[#0b0e14] border border-white/10 rounded-xl shadow-inner">
                  <canvas ref={canvasRef} width="320" height="320" className="rounded-lg" />
                </div>
              </div>

              <div className="lg:col-span-7 bg-[#161a24]/90 border border-white/10 rounded-xl p-5 space-y-3">
                <h3 className="text-sm font-bold text-white">Multi-Date Historical Observations</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-slate-300">
                    <thead className="bg-white/5 text-slate-300 border-b border-white/10 font-mono text-[11px] uppercase">
                      <tr>
                        <th className="py-2.5 px-3">Date</th>
                        <th className="py-2.5 px-3">Sensor</th>
                        <th className="py-2.5 px-3">Area (km²)</th>
                        <th className="py-2.5 px-3">Quality</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {lakeHistory.map(obs => (
                        <tr key={obs.observation_id} className="hover:bg-white/5">
                          <td className="py-2.5 px-3 font-mono">{obs.date}</td>
                          <td className="py-2.5 px-3">{obs.sensor}</td>
                          <td className="py-2.5 px-3 font-mono font-bold text-cyan-400">{obs.area_km2}</td>
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
          <div className="bg-[#12141b]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 space-y-6 shadow-2xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-white/10 gap-4">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span>
                  Downstream Reservoir Water-Spread Variations
                </h2>
                <p className="text-xs text-slate-400 font-mono mt-1">Monitoring Teesta-III Chungthang Dam & Teesta-V Dam (Dikchu)</p>
              </div>
              <select
                value={selectedResId}
                onChange={(e) => handleReservoirChange(e.target.value)}
                className="bg-[#131722] border border-white/10 text-slate-200 text-xs rounded-full px-3 py-1.5 font-mono focus:outline-none focus:border-cyan-400"
              >
                <option value="RES-TK-01">Teesta-III Chungthang Dam (Breached Oct 2023)</option>
                <option value="RES-TK-02">Teesta-V Dikchu Dam (NHPC)</option>
              </select>
            </div>

            <div className="p-4.5 rounded-xl bg-gradient-to-r from-rose-950/40 to-slate-900/60 border border-rose-500/30 text-xs text-slate-300 leading-relaxed shadow-sm">
              <strong className="text-rose-300">Scientific Distinction: Water-Spread vs Storage Volume:</strong> Optical imagery measures water-spread surface area, which is <strong>NOT direct volumetric storage capacity</strong>. Undercurrent reports water-spread only to preserve rigorous scientific defensibility.
            </div>

            <div className="bg-[#161a24]/90 border border-white/10 rounded-xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-white">Multi-Date Water-Spread History</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-white/5 text-slate-300 border-b border-white/10 font-mono text-[11px] uppercase">
                    <tr>
                      <th className="py-2.5 px-3">Date</th>
                      <th className="py-2.5 px-3">Season / Context</th>
                      <th className="py-2.5 px-3">Water Spread</th>
                      <th className="py-2.5 px-3">Quality Note</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {resHistory.map(obs => (
                      <tr key={obs.observation_id} className="hover:bg-white/5">
                        <td className="py-2.5 px-3 font-mono">{obs.date}</td>
                        <td className="py-2.5 px-3">{obs.season}</td>
                        <td className="py-2.5 px-3 font-mono font-bold text-cyan-400">{obs.water_spread_area_km2} km²</td>
                        <td className="py-2.5 px-3 text-slate-400 font-mono">{obs.quality_flag}</td>
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
          <div className="bg-[#12141b]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 space-y-6 shadow-2xl">
            <div className="flex justify-between items-center pb-4 border-b border-white/10">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block"></span>
                  Downstream Exposure Screening
                </h2>
                <p className="text-xs text-slate-400 font-mono mt-1">112.4 km corridor from South Lhonak (5,200m) to Rangpo (280m)</p>
              </div>
              <span className="px-3.5 py-1.5 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-full font-mono font-bold">
                Elevation Drop: 4,920 m (Avg Slope 4.4%)
              </span>
            </div>

            <div className="bg-[#161a24]/90 border border-white/10 rounded-xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-white">Valley DEM Elevation Profile (5,200m &rarr; 280m)</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-white/5 text-slate-300 border-b border-white/10 font-mono text-[11px] uppercase">
                    <tr>
                      <th className="py-2.5 px-3">Distance (km)</th>
                      <th className="py-2.5 px-3">Elevation (m ASL)</th>
                      <th className="py-2.5 px-3">Slope</th>
                      <th className="py-2.5 px-3">Landmark Point</th>
                      <th className="py-2.5 px-3">Zone Classification</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {elevationProfile.map((pt, idx) => (
                      <tr key={idx} className="hover:bg-white/5">
                        <td className="py-2.5 px-3 font-mono">{pt.distance_km} km</td>
                        <td className="py-2.5 px-3 font-mono text-cyan-400 font-bold">{pt.elevation_m} m</td>
                        <td className="py-2.5 px-3 font-mono">{pt.slope_deg}°</td>
                        <td className="py-2.5 px-3 font-semibold text-slate-100">{pt.landmark}</td>
                        <td className="py-2.5 px-3 text-slate-400">{pt.zone}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-[#161a24]/90 border border-white/10 rounded-xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-white">Screened Assets & Settlements</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-white/5 text-slate-300 border-b border-white/10 font-mono text-[11px] uppercase">
                    <tr>
                      <th className="py-2.5 px-3">Asset</th>
                      <th className="py-2.5 px-3">Category</th>
                      <th className="py-2.5 px-3">Dist from Lake</th>
                      <th className="py-2.5 px-3">Rating</th>
                      <th className="py-2.5 px-3">Vulnerability Context</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {assets.map(a => (
                      <tr key={a.id} className="hover:bg-white/5">
                        <td className="py-2.5 px-3 font-semibold text-slate-100">{a.name}</td>
                        <td className="py-2.5 px-3 text-slate-400">{a.category}</td>
                        <td className="py-2.5 px-3 font-mono text-cyan-300">{a.distance_from_lake_km} km</td>
                        <td className="py-2.5 px-3">
                          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${
                            a.exposure_rating === 'Critical' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                          }`}>
                            {a.exposure_rating}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">{a.key_vulnerability}</td>
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
          <div className="bg-[#12141b]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-3 border-b border-white/10">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span>
                Interactive Tactical GIS Map Explorer
              </h2>
              <span className="text-xs text-cyan-400 font-mono">Teesta Basin GIS &bull; 112.4 km Corridor</span>
            </div>
            <div className="w-full h-[640px] rounded-xl overflow-hidden border border-white/10 bg-[#090a0d]">
              <iframe src="/#gis-map" className="w-full h-full border-0" title="Undercurrent GIS Map" />
            </div>
          </div>
        )}

        {/* TAB 6: DATA & PROVENANCE */}
        {activeTab === 'methodology' && (
          <div className="bg-[#12141b]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 space-y-6 shadow-2xl">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span>
              Scientific Methodology & Space Data Provenance
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-5 bg-[#161a24]/90 border border-white/10 rounded-xl space-y-2">
                <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono">Formula 1: NDWI Water Index</div>
                <div className="p-3 bg-black/50 rounded-lg font-mono text-sm text-cyan-300 border border-white/10 shadow-inner">NDWI = (Green - NIR) / (Green + NIR)</div>
                <p className="text-xs text-slate-400 font-mono">Sentinel-2 Band 3 (560nm) and Band 8 (842nm) at 10m spatial resolution.</p>
              </div>
              <div className="p-5 bg-[#161a24]/90 border border-white/10 rounded-xl space-y-2">
                <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider font-mono">Formula 2: Percentage Area Change</div>
                <div className="p-3 bg-black/50 rounded-lg font-mono text-sm text-cyan-300 border border-white/10 shadow-inner">% Change = ((A_later - A_earlier) / A_earlier) &times; 100</div>
                <p className="text-xs text-slate-400 font-mono">Projected in UTM Zone 45N (EPSG:32645) planar coordinate system.</p>
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

      {/* Command Palette Modal */}
      {showPalette && (
        <div 
          onClick={() => setShowPalette(false)}
          className="fixed inset-0 z-[100] flex items-start justify-center pt-24 px-4 bg-black/75 backdrop-blur-md"
        >
          <div 
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-xl rounded-2xl bg-[#0c0e14]/98 border border-white/20 shadow-2xl overflow-hidden"
          >
            <div className="flex items-center px-4 py-3.5 border-b border-white/10 gap-3 bg-white/5">
              <span className="text-cyan-400 font-mono">🔍</span>
              <input 
                type="text" 
                value={paletteQuery} 
                onChange={(e) => setPaletteQuery(e.target.value)} 
                placeholder="Search basin targets, dams, corridors..." 
                className="flex-1 bg-transparent text-white placeholder-slate-500 focus:outline-none text-sm font-sans" 
                autoFocus 
              />
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-slate-400">ESC to exit</span>
            </div>
            <div className="max-h-80 overflow-y-auto p-2 space-y-1 text-xs">
              {[
                { title: 'South Lhonak Glacial Lake (GL-SK-01)', sub: 'Breached Moraine • Elev: 5,200m ASL', cat: 'Glacial Lake', tab: 'lakes' },
                { title: 'Teesta-III Chungthang Dam (RES-TK-01)', sub: 'Dam Wall Lost • 1,200 MW Hydro Project', cat: 'Reservoir', tab: 'reservoirs' },
                { title: 'Dikchu Dam / NHPC Teesta-V (RES-TK-02)', sub: 'Heavy Silt Influx & Turbidity Spike', cat: 'Reservoir', tab: 'reservoirs' },
                { title: 'Teesta River 112km Downstream Exposure Reach', sub: 'Elevation Drop 5,200m → 280m', cat: 'Corridor', tab: 'exposure' },
                { title: 'Interactive Multi-Layer Leaflet GIS Map', sub: 'Satellite + Topo + Contours', cat: 'GIS Map', tab: 'gis-map' },
                { title: 'Scientific Methodology & Provenance', sub: 'Formulae & Space Lineage', cat: 'Methodology', tab: 'methodology' }
              ]
                .filter(item => !paletteQuery || item.title.toLowerCase().includes(paletteQuery.toLowerCase()) || item.cat.toLowerCase().includes(paletteQuery.toLowerCase()))
                .map((item, i) => (
                  <div 
                    key={i} 
                    onClick={() => { setActiveTab(item.tab); setShowPalette(false); }}
                    className="p-2.5 rounded-xl bg-white/5 hover:bg-cyan-500/15 border border-white/5 hover:border-cyan-400/30 flex items-center justify-between cursor-pointer transition select-none"
                  >
                    <div>
                      <div className="font-bold text-white text-xs">{item.title}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{item.sub}</div>
                    </div>
                    <span className="px-2 py-0.5 rounded-full bg-white/10 text-[10px] font-mono text-cyan-300">{item.cat}</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
