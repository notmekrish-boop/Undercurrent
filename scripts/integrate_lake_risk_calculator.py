"""
Integrates the Multi-Temporal Glacier Lake Risk Calculator and cleans up unsupported frontend claims
in backend/app/static/index.html per Page 5 (Section 12) & Page 6 of the Technical Review.
"""
from pathlib import Path

index_path = Path("backend/app/static/index.html")
content = index_path.read_text(encoding="utf-8")
has_crlf = "\r\n" in content
norm = content.replace("\r\n", "\n")

# 1. Clean up unsupported claims in header and pills
replacements = [
    (
        '<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 pulse-dot"></span> Live Track',
        '<span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span> Research Prototype'
    ),
    (
        '<i data-lucide="layout-dashboard" class="w-3.5 h-3.5"></i> Live Command',
        '<i data-lucide="layout-dashboard" class="w-3.5 h-3.5"></i> Basin Overview'
    ),
    (
        '<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 pulse-dot"></span> All Synced',
        '<span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span> S2 MSI + CartoDEM'
    ),
    (
        'Sudden moraine failure drained <strong class="text-rose-300">~45.2M m³</strong> of water in under 4 hours. Lake surface area plunged by <strong class="text-rose-300">-38.7%</strong> (1.68 km² &rarr; 1.03 km²).',
        'Sudden moraine failure drained <strong class="text-rose-300">~0.690 km²</strong> of lake surface spread (-41.4%). Measured 10m Sentinel-2 Level-2A area contracted from 1.666 km² to 0.976 km².'
    ),
    (
        '<span class="text-emerald-300">Live Telemetry Monitoring</span>',
        '<span class="text-emerald-300">Geospatial Analysis Session</span>'
    ),
    (
        '<span class="text-emerald-400 font-bold">100% Online (12/12 APIs)</span>',
        '<span class="text-emerald-400 font-bold">Active Services (13 Endpoints)</span>'
    ),
    (
        '<span class="w-2 h-2 rounded-full bg-emerald-400 pulse-dot"></span> Online Track',
        '<span class="w-2 h-2 rounded-full bg-cyan-400"></span> Basin Targets'
    ),
    (
        '<div class="font-bold text-rose-300 text-xs mt-0.5">~45.2M m³ Moraine Drainage</div>',
        '<div class="font-bold text-rose-300 text-xs mt-0.5">-0.690 km² Moraine Outflow</div>'
    ),
    (
        'All 5 Stages Verified (Success)',
        'Pipeline Completed (5 Stages Executed)'
    ),
    (
        '<span class="text-slate-400">Estimated Water Area:</span>',
        '<span class="text-slate-400">Estimated Water Area (24x24 Simulator):</span>'
    )
]

for old, new in replacements:
    if old in norm:
        norm = norm.replace(old, new, 1)
        print(f"Replaced: {old[:40]}...")
    else:
        print(f"Warning: Not found: {old[:40]}...")

# 2. Add Glacier Lake Risk Calculator inside Tab 2 (Glacial Lake Monitor)
lake_risk_calculator_html = """
        <!-- 2B. INTERACTIVE GLACIAL LAKE MULTI-TEMPORAL RISK CALCULATOR -->
        <div class="mt-6 hud-panel-subtle p-5 space-y-5 rounded-2xl border border-white/10">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-white/10">
            <div>
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-cyan-400 pulse-dot"></span>
                <h3 class="text-sm font-bold text-white flex items-center gap-2 font-mono uppercase tracking-wider">
                  <i data-lucide="calculator" class="w-4 h-4 text-cyan-400"></i> Multi-Temporal Glacier Lake Risk Calculator
                </h3>
              </div>
              <p class="text-[11px] text-slate-400 mt-0.5 font-mono">
                Insert multi-date satellite observations for any glacier lake to compute expansion velocity, breach outflow, and downstream GLOF risk score.
              </p>
            </div>
            <!-- Preset Selector -->
            <div class="flex items-center gap-2">
              <span class="text-[11px] text-slate-400 font-mono uppercase">Quick Presets:</span>
              <div class="hud-pill px-3 py-1 bg-[#131722]/80 border border-white/10 shadow-inner">
                <select id="risk-preset-select" onchange="window.selectLakePreset(this.value)" class="bg-transparent text-cyan-300 text-xs font-mono focus:outline-none cursor-pointer">
                  <option value="preset-south-lhonak-breach" selected>South Lhonak 2023 Breach Outflow (-41.4%)</option>
                  <option value="preset-south-lhonak-growth">South Lhonak 2013-2021 Growth (+29.5%)</option>
                  <option value="preset-imja-tsho">Imja Tsho Rapid Expansion (+42.1%)</option>
                  <option value="custom">-- Custom Glacier Lake Input --</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Input Grid Form -->
          <form id="glacier-risk-form" onsubmit="event.preventDefault(); window.calculateGlacierRisk();" class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs font-mono">
              <div class="space-y-1">
                <label class="text-slate-400 text-[10px] uppercase block">Lake Name / ID:</label>
                <input type="text" id="risk-lake-name" value="South Lhonak Glacial Lake" required class="w-full bg-black/60 border border-white/15 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-400 text-xs" />
              </div>
              <div class="space-y-1">
                <label class="text-slate-400 text-[10px] uppercase block">Basin / Region:</label>
                <input type="text" id="risk-lake-basin" value="Teesta River Basin, Sikkim" class="w-full bg-black/60 border border-white/15 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-400 text-xs" />
              </div>
              <div class="space-y-1">
                <label class="text-slate-400 text-[10px] uppercase block">Lake Altitude (m ASL):</label>
                <input type="number" id="risk-lake-elev" value="5200" step="10" min="1000" max="8500" class="w-full bg-black/60 border border-white/15 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-cyan-400 text-xs" />
              </div>
              <div class="space-y-1">
                <label class="text-slate-400 text-[10px] uppercase block">Dam Structure Type:</label>
                <select id="risk-dam-type" class="w-full bg-black/60 border border-white/15 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-400 text-xs">
                  <option value="Moraine-dammed" selected>Moraine-dammed (High Hazard)</option>
                  <option value="Ice-cored moraine">Ice-cored moraine (Thermokarst Risk)</option>
                  <option value="Bedrock-dammed">Bedrock-dammed (Stable)</option>
                </select>
              </div>
            </div>

            <!-- Date 1 & Date 2 Observation Pair -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs font-mono pt-1">
              <div class="p-3 bg-black/40 border border-cyan-500/20 rounded-xl space-y-1.5">
                <span class="text-cyan-400 text-[10px] uppercase font-bold block flex items-center gap-1">
                  <i data-lucide="calendar" class="w-3 h-3"></i> Observation 1 (Baseline Date)
                </span>
                <input type="date" id="risk-date-1" value="2023-09-26" required class="w-full bg-black/60 border border-white/15 rounded px-2.5 py-1 text-white text-xs focus:border-cyan-400 focus:outline-none" />
                <div class="flex items-center gap-2 pt-1">
                  <span class="text-slate-400 text-[10px]">Area:</span>
                  <input type="number" id="risk-area-1" value="1.6664" step="0.0001" min="0.01" required class="flex-1 bg-black/60 border border-white/15 rounded px-2 py-0.5 text-cyan-300 font-bold text-xs focus:border-cyan-400 focus:outline-none" />
                  <span class="text-slate-500 text-[10px]">km²</span>
                </div>
              </div>

              <div class="p-3 bg-black/40 border border-rose-500/20 rounded-xl space-y-1.5">
                <span class="text-rose-400 text-[10px] uppercase font-bold block flex items-center gap-1">
                  <i data-lucide="calendar" class="w-3 h-3"></i> Observation 2 (Assessment Date)
                </span>
                <input type="date" id="risk-date-2" value="2023-10-09" required class="w-full bg-black/60 border border-white/15 rounded px-2.5 py-1 text-white text-xs focus:border-rose-400 focus:outline-none" />
                <div class="flex items-center gap-2 pt-1">
                  <span class="text-slate-400 text-[10px]">Area:</span>
                  <input type="number" id="risk-area-2" value="0.9764" step="0.0001" min="0.01" required class="flex-1 bg-black/60 border border-white/15 rounded px-2 py-0.5 text-rose-300 font-bold text-xs focus:border-rose-400 focus:outline-none" />
                  <span class="text-slate-500 text-[10px]">km²</span>
                </div>
              </div>

              <div class="p-3 bg-black/40 border border-amber-500/20 rounded-xl space-y-1.5">
                <span class="text-amber-400 text-[10px] uppercase font-bold block flex items-center gap-1">
                  <i data-lucide="navigation" class="w-3 h-3"></i> Downstream Reach (km)
                </span>
                <input type="number" id="risk-dist-km" value="68.0" step="0.5" min="1" max="300" class="w-full bg-black/60 border border-white/15 rounded px-2.5 py-1 text-white text-xs focus:border-amber-400 focus:outline-none" />
                <span class="text-[10px] text-slate-500 block">Distance to nearest downstream dam/settlement</span>
              </div>

              <div class="p-3 bg-black/40 border border-purple-500/20 rounded-xl space-y-1.5 flex flex-col justify-between">
                <div>
                  <span class="text-purple-400 text-[10px] uppercase font-bold block flex items-center gap-1">
                    <i data-lucide="trending-down" class="w-3 h-3"></i> Channel Slope (deg)
                  </span>
                  <input type="number" id="risk-slope-deg" value="22.0" step="0.5" min="1" max="60" class="w-full bg-black/60 border border-white/15 rounded px-2.5 py-1 text-white text-xs focus:border-purple-400 focus:outline-none mt-1" />
                  <span class="text-[10px] text-slate-500 block">DEM valley confinement gradient</span>
                </div>
                <button type="submit" id="btn-calc-glacier-risk" class="w-full py-2 px-3 rounded-lg font-bold text-xs text-white bg-cyan-600 hover:bg-cyan-500 transition shadow-lg flex items-center justify-center gap-1.5 cursor-pointer mt-1">
                  <i data-lucide="play" class="w-3.5 h-3.5"></i> Calculate Risk Assessment
                </button>
              </div>
            </div>
          </form>

          <!-- Dynamic Assessment Result Display (Hidden initially, shown after calculation) -->
          <div id="glacier-risk-results" class="hidden p-4 rounded-xl bg-black/60 border border-white/15 space-y-4 font-mono text-xs">
            <!-- Rendered by window.calculateGlacierRisk() -->
          </div>
        </div>
"""

# Place lake_risk_calculator_html right before the closing tag of tab-lakes
target_tab_lakes_end = """            <div class="text-xs text-slate-400 border-t border-white/5 pt-3 flex items-center justify-between font-mono">
              <span>Baseline Expansion: <strong class="text-emerald-400">+51.6%</strong> (2013-2021)</span>
              <span class="text-rose-400 font-semibold">Breach Drainage: -38.7% (Oct 2023)</span>
            </div>
          </div>
        </div>
      </div>
    </div>"""

assert target_tab_lakes_end in norm, "target_tab_lakes_end not found"
norm = norm.replace(
    target_tab_lakes_end,
    """            <div class="text-xs text-slate-400 border-t border-white/5 pt-3 flex items-center justify-between font-mono">
              <span>Baseline Expansion: <strong class="text-emerald-400">+51.6%</strong> (2013-2021)</span>
              <span class="text-rose-400 font-semibold">Breach Drainage: -38.7% (Oct 2023)</span>
            </div>
          </div>
        </div>""" + lake_risk_calculator_html + "\n      </div>\n    </div>"
)

# Add JavaScript for preset selection and risk calculation
risk_js = """
    // ==========================================
    // GLACIER LAKE RISK CALCULATOR CONTROLLER
    // ==========================================
    window.selectLakePreset = function(presetId) {
      const presets = {
        'preset-south-lhonak-breach': {
          name: 'South Lhonak Glacial Lake',
          basin: 'Teesta River Basin, Sikkim',
          elev: 5200,
          damType: 'Moraine-dammed',
          d1: '2023-09-26', a1: 1.6664,
          d2: '2023-10-09', a2: 0.9764,
          dist: 68.0, slope: 22.0
        },
        'preset-south-lhonak-growth': {
          name: 'South Lhonak Glacial Lake',
          basin: 'Teesta River Basin, Sikkim',
          elev: 5200,
          damType: 'Moraine-dammed',
          d1: '2013-10-15', a1: 1.22,
          d2: '2021-10-05', a2: 1.58,
          dist: 68.0, slope: 22.0
        },
        'preset-imja-tsho': {
          name: 'Imja Tsho Glacial Lake',
          basin: 'Dudh Koshi Basin, Nepal Himalaya',
          elev: 5010,
          damType: 'Ice-cored moraine',
          d1: '2018-10-01', a1: 0.95,
          d2: '2023-10-01', a2: 1.35,
          dist: 45.0, slope: 18.0
        }
      };

      if (presets[presetId]) {
        const p = presets[presetId];
        document.getElementById('risk-lake-name').value = p.name;
        document.getElementById('risk-lake-basin').value = p.basin;
        document.getElementById('risk-lake-elev').value = p.elev;
        document.getElementById('risk-dam-type').value = p.damType;
        document.getElementById('risk-date-1').value = p.d1;
        document.getElementById('risk-area-1').value = p.a1;
        document.getElementById('risk-date-2').value = p.d2;
        document.getElementById('risk-area-2').value = p.a2;
        document.getElementById('risk-dist-km').value = p.dist;
        document.getElementById('risk-slope-deg').value = p.slope;
      }
    };

    window.calculateGlacierRisk = async function() {
      const btn = document.getElementById('btn-calc-glacier-risk');
      const results = document.getElementById('glacier-risk-results');
      if (!results) return;

      if (btn) btn.disabled = true;
      results.classList.remove('hidden');
      results.innerHTML = `
        <div class="flex items-center gap-2 text-cyan-400 py-3">
          <span class="w-2 h-2 rounded-full bg-cyan-400 pulse-dot"></span>
          <span>Computing multi-temporal area velocity & downvalley hazard screening...</span>
        </div>
      `;

      const payload = {
        lake_name: document.getElementById('risk-lake-name').value,
        basin: document.getElementById('risk-lake-basin').value,
        elevation_masl: parseFloat(document.getElementById('risk-lake-elev').value),
        dam_type: document.getElementById('risk-dam-type').value,
        downstream_distance_km: parseFloat(document.getElementById('risk-dist-km').value),
        channel_slope_deg: parseFloat(document.getElementById('risk-slope-deg').value),
        observations: [
          { date: document.getElementById('risk-date-1').value, area_km2: parseFloat(document.getElementById('risk-area-1').value) },
          { date: document.getElementById('risk-date-2').value, area_km2: parseFloat(document.getElementById('risk-area-2').value) }
        ]
      };

      try {
        const res = await fetch('/api/lakes/assess-risk', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.detail || 'Calculation failed');
        }

        const h = data.hazard_classification;
        const m = data.temporal_metrics;
        const s = data.downstream_screening;

        let badgeBg = 'bg-rose-950/80 border-rose-500/50 text-rose-300';
        let barBg = 'bg-rose-500';
        if (h.risk_tier === 'HIGH') {
          badgeBg = 'bg-amber-950/80 border-amber-500/50 text-amber-300';
          barBg = 'bg-amber-500';
        } else if (h.risk_tier === 'MODERATE') {
          badgeBg = 'bg-yellow-950/80 border-yellow-500/50 text-yellow-300';
          barBg = 'bg-yellow-500';
        } else if (h.risk_tier === 'LOW') {
          badgeBg = 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300';
          barBg = 'bg-emerald-500';
        }

        results.innerHTML = `
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-white/10">
            <div class="space-y-1">
              <span class="text-[10px] text-slate-500 uppercase tracking-widest block">Automated Hazard Assessment Result</span>
              <div class="text-white font-bold text-base flex items-center gap-2">
                <span>${data.lake_name}</span>
                <span class="text-xs text-slate-400 font-normal">(${data.basin} &bull; ${data.elevation_masl}m ASL)</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <div class="hud-pill px-3 py-1 border ${badgeBg} font-bold text-xs flex items-center gap-1.5 shadow-lg">
                <span class="w-2 h-2 rounded-full ${h.risk_tier === 'CRITICAL' ? 'bg-rose-400 pulse-dot' : 'bg-current'}"></span>
                <span>${h.risk_tier} RISK &bull; ${h.hazard_label}</span>
              </div>
            </div>
          </div>

          <!-- Risk Score Meter -->
          <div class="space-y-1.5">
            <div class="flex justify-between text-xs">
              <span class="text-slate-400">Composite Hazard Score:</span>
              <span class="font-bold text-white">${h.hazard_score_0_to_100} / 100</span>
            </div>
            <div class="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-white/10">
              <div class="h-2.5 ${barBg} transition-all duration-500" style="width: ${Math.min(100, h.hazard_score_0_to_100)}%"></div>
            </div>
          </div>

          <!-- 4 Calculated Metric Tiles -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5 pt-1">
            <div class="p-2.5 bg-black/40 border border-white/10 rounded-lg space-y-0.5">
              <span class="text-[10px] text-slate-500 uppercase block">Surface Area Delta</span>
              <div class="${m.percentage_change < 0 ? 'text-rose-400' : 'text-emerald-400'} font-bold text-sm">
                ${m.percentage_change > 0 ? '+' : ''}${m.percentage_change}%
              </div>
              <span class="text-[10px] text-slate-400 block">${m.delta_area_km2 > 0 ? '+' : ''}${m.delta_area_km2} km²</span>
            </div>

            <div class="p-2.5 bg-black/40 border border-white/10 rounded-lg space-y-0.5">
              <span class="text-[10px] text-slate-500 uppercase block">Elapsed Time</span>
              <div class="text-white font-bold text-sm">${m.elapsed_days} Days</div>
              <span class="text-[10px] text-slate-400 block">${m.baseline_observation.date} &rarr; ${m.latest_observation.date}</span>
            </div>

            <div class="p-2.5 bg-black/40 border border-white/10 rounded-lg space-y-0.5">
              <span class="text-[10px] text-slate-500 uppercase block">Annualized Velocity</span>
              <div class="text-cyan-300 font-bold text-sm">${m.annualized_rate_pct_per_year > 0 ? '+' : ''}${m.annualized_rate_pct_per_year}% / yr</div>
              <span class="text-[10px] text-slate-400 block">Expansion rate</span>
            </div>

            <div class="p-2.5 bg-black/40 border border-white/10 rounded-lg space-y-0.5">
              <span class="text-[10px] text-slate-500 uppercase block">Downvalley Reach</span>
              <div class="text-amber-300 font-bold text-sm">${s.downstream_distance_km} km</div>
              <span class="text-[10px] text-slate-400 block">${s.channel_slope_deg}&deg; valley gradient</span>
            </div>
          </div>

          <!-- Primary Trigger & Operational Directive -->
          <div class="p-3 bg-black/50 border border-white/10 rounded-xl space-y-2">
            <div class="text-[11px] text-slate-300 leading-relaxed">
              <strong class="text-cyan-400 uppercase tracking-wider text-[10px] block">Primary Hazard Trigger:</strong>
              ${h.primary_trigger}
            </div>
            <div class="text-[11px] text-amber-200 leading-relaxed pt-1 border-t border-white/10">
              <strong class="text-amber-400 uppercase tracking-wider text-[10px] block">Recommended Operational Action:</strong>
              ${data.recommended_response}
            </div>
          </div>

          <!-- Scientific Safeguards Disclaimer -->
          <div class="text-[10px] text-slate-500 pt-1 border-t border-white/5 leading-relaxed">
            <strong>Scientific Safeguards:</strong> ${data.scientific_safeguards}
          </div>
        `;
      } catch (err) {
        results.innerHTML = `
          <div class="p-3 bg-rose-950/60 border border-rose-500/50 rounded-lg text-rose-300 space-y-1">
            <div class="font-bold flex items-center gap-1.5"><i data-lucide="alert-octagon" class="w-4 h-4 text-rose-400"></i> Risk Assessment Error</div>
            <div class="text-xs">${err.message}</div>
          </div>
        `;
      } finally {
        if (btn) btn.disabled = false;
        if (typeof lucide !== 'undefined') lucide.createIcons();
      }
    };
"""

target_script = "  </script>"
assert target_script in norm, "target_script not found"
norm = norm.replace(target_script, risk_js + "\n  </script>")

final_text = norm.replace("\n", "\r\n") if has_crlf else norm
index_path.write_text(final_text, encoding="utf-8")
print("Successfully integrated Glacier Lake Risk Calculator into index.html!")
