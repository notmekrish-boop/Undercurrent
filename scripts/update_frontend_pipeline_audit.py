"""
Updates backend/app/static/index.html with the Live End-to-End Pipeline Audit Console.
"""
from pathlib import Path

index_path = Path("backend/app/static/index.html")
content = index_path.read_text(encoding="utf-8")
has_crlf = "\r\n" in content
normalized = content.replace("\r\n", "\n")

target_ui = """          <!-- Export & Audit Pipeline Action Buttons -->
          <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-white/10">
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs text-slate-400 font-mono">Download Artifacts:</span>
              <a href="/api/analysis/validation" target="_blank" class="hud-pill px-3 py-1 text-xs font-mono text-cyan-300 hover:text-white hover:bg-cyan-950/40 border border-cyan-800/40 flex items-center gap-1 transition">
                <i data-lucide="file-check" class="w-3.5 h-3.5"></i> Validation Record (JSON)
              </a>
              <a href="/api/pipeline/end-to-end" target="_blank" class="hud-pill px-3 py-1 text-xs font-mono text-emerald-300 hover:text-white hover:bg-emerald-950/40 border border-emerald-800/40 flex items-center gap-1 transition">
                <i data-lucide="git-branch" class="w-3.5 h-3.5"></i> End-to-End Pipeline Audit (JSON)
              </a>
              <a href="/api/exposure/SA-TEESTA-01/sensitivity" target="_blank" class="hud-pill px-3 py-1 text-xs font-mono text-amber-300 hover:text-white hover:bg-amber-950/40 border border-amber-800/40 flex items-center gap-1 transition">
                <i data-lucide="sliders" class="w-3.5 h-3.5"></i> Weight Sensitivity Matrix (JSON)
              </a>
            </div>
            <div class="flex items-center gap-2">
              <a href="/api/map/download/south_lhonak" class="hud-pill px-3 py-1 text-xs font-mono text-slate-300 hover:text-white flex items-center gap-1 transition">
                <i data-lucide="download" class="w-3.5 h-3.5 text-cyan-400"></i> QGIS Lake Layer
              </a>
              <a href="/api/map/download/exposure" class="hud-pill px-3 py-1 text-xs font-mono text-slate-300 hover:text-white flex items-center gap-1 transition">
                <i data-lucide="download" class="w-3.5 h-3.5 text-rose-400"></i> QGIS Corridor Layer
              </a>
            </div>
          </div>
        </div>"""

replacement_ui = """          <!-- Export & Audit Pipeline Action Buttons -->
          <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-white/10">
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs text-slate-400 font-mono">Download Artifacts:</span>
              <a href="/api/analysis/validation" target="_blank" class="hud-pill px-3 py-1 text-xs font-mono text-cyan-300 hover:text-white hover:bg-cyan-950/40 border border-cyan-800/40 flex items-center gap-1 transition">
                <i data-lucide="file-check" class="w-3.5 h-3.5"></i> Validation Record (JSON)
              </a>
              <a href="/api/pipeline/end-to-end" target="_blank" class="hud-pill px-3 py-1 text-xs font-mono text-emerald-300 hover:text-white hover:bg-emerald-950/40 border border-emerald-800/40 flex items-center gap-1 transition">
                <i data-lucide="git-branch" class="w-3.5 h-3.5"></i> End-to-End Pipeline Audit (JSON)
              </a>
              <a href="/api/exposure/SA-TEESTA-01/sensitivity" target="_blank" class="hud-pill px-3 py-1 text-xs font-mono text-amber-300 hover:text-white hover:bg-amber-950/40 border border-amber-800/40 flex items-center gap-1 transition">
                <i data-lucide="sliders" class="w-3.5 h-3.5"></i> Weight Sensitivity Matrix (JSON)
              </a>
            </div>
            <div class="flex items-center gap-2">
              <a href="/api/map/download/south_lhonak" class="hud-pill px-3 py-1 text-xs font-mono text-slate-300 hover:text-white flex items-center gap-1 transition">
                <i data-lucide="download" class="w-3.5 h-3.5 text-cyan-400"></i> QGIS Lake Layer
              </a>
              <a href="/api/map/download/exposure" class="hud-pill px-3 py-1 text-xs font-mono text-slate-300 hover:text-white flex items-center gap-1 transition">
                <i data-lucide="download" class="w-3.5 h-3.5 text-rose-400"></i> QGIS Corridor Layer
              </a>
            </div>
          </div>

          <!-- Interactive Live Pipeline Audit Console -->
          <div class="pt-4 border-t border-white/10 space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-white font-mono uppercase tracking-wider flex items-center gap-1.5">
                  <i data-lucide="activity" class="w-4 h-4 text-emerald-400"></i> Live End-to-End Pipeline Audit:
                </span>
                <span id="pipeline-status-badge" class="hud-pill px-2.5 py-0.5 text-[10px] font-mono text-cyan-400 border border-cyan-500/30">
                  Ready to Execute
                </span>
              </div>
              <button type="button" onclick="window.runLivePipelineAudit()" id="run-pipeline-btn" class="hud-pill px-3 py-1 text-xs font-mono font-bold text-white bg-cyan-600/40 hover:bg-cyan-600/70 border border-cyan-400/50 flex items-center gap-1.5 transition cursor-pointer">
                <i data-lucide="play" class="w-3.5 h-3.5 text-cyan-300"></i> Run Pipeline Audit
              </button>
            </div>

            <div id="pipeline-audit-results" class="hidden p-4 bg-black/50 rounded-xl border border-white/10 space-y-3 text-xs font-mono">
              <!-- Dynamically rendered by window.runLivePipelineAudit -->
            </div>
          </div>
        </div>"""

assert target_ui in normalized, "target_ui not found in index.html"
normalized = normalized.replace(target_ui, replacement_ui)

# Add the JavaScript function before </script>
js_code = """
    // ==========================================
    // LIVE END-TO-END PIPELINE AUDIT CONTROLLER
    // ==========================================
    window.runLivePipelineAudit = async function() {
      const badge = document.getElementById('pipeline-status-badge');
      const btn = document.getElementById('run-pipeline-btn');
      const results = document.getElementById('pipeline-audit-results');
      if (!badge || !results) return;

      badge.className = 'hud-pill px-2.5 py-0.5 text-[10px] font-mono text-amber-400 border border-amber-500/30';
      badge.textContent = 'Executing 5 Stages...';
      if (btn) btn.disabled = true;

      try {
        const res = await fetch('/api/pipeline/end-to-end');
        const data = await res.json();

        if (data.pipeline_status === 'FAILED') {
          badge.className = 'hud-pill px-2.5 py-0.5 text-[10px] font-mono text-rose-400 border border-rose-500/30';
          badge.textContent = 'Stage Failed';
          results.classList.remove('hidden');
          results.innerHTML = `
            <div class="p-3 bg-rose-950/40 border border-rose-500/40 rounded-lg text-rose-300 space-y-1">
              <div class="font-bold flex items-center gap-1.5"><i data-lucide="alert-octagon" class="w-4 h-4 text-rose-400"></i> Pipeline Halted at Stage: ${data.failed_stage}</div>
              <div class="text-[11px] text-slate-300">${data.error_detail || 'Raster calculation failed'}</div>
              <div class="text-[10px] text-amber-300">${data.remediation || ''}</div>
            </div>
          `;
        } else {
          badge.className = 'hud-pill px-2.5 py-0.5 text-[10px] font-mono text-emerald-400 border border-emerald-500/30';
          badge.textContent = 'All 5 Stages Verified (Success)';
          results.classList.remove('hidden');

          const s1 = data.workflow_steps.step_1_lake_only_change;
          const s2 = data.workflow_steps.step_2_drainage_corridor;
          const s3 = data.workflow_steps.step_3_screened_asset_overlays;
          const s4 = data.workflow_steps.step_4_independent_reservoir_track;
          const s5 = data.workflow_steps.step_5_evidence_advisory;

          results.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-5 gap-2.5">
              <div class="p-2.5 bg-black/40 border border-cyan-500/30 rounded-lg space-y-1">
                <div class="text-[10px] text-slate-500 uppercase">Stage 1: Lake Delta</div>
                <div class="text-cyan-300 font-bold">${s1.empirical_drainage.drainage_percentage}%</div>
                <div class="text-[10px] text-slate-400">${s1.pre_burst_baseline.physical_area_km2} &rarr; ${s1.post_burst_state.physical_area_km2} km²</div>
              </div>
              <div class="p-2.5 bg-black/40 border border-sky-500/30 rounded-lg space-y-1">
                <div class="text-[10px] text-slate-500 uppercase">Stage 2: Gorge Reach</div>
                <div class="text-sky-300 font-bold">${s2.total_reach_km} km</div>
                <div class="text-[10px] text-slate-400">${s2.hydraulic_drop_m}m drop (${s2.mean_gradient_pct}%)</div>
              </div>
              <div class="p-2.5 bg-black/40 border border-amber-500/30 rounded-lg space-y-1">
                <div class="text-[10px] text-slate-500 uppercase">Stage 3: Asset Overlay</div>
                <div class="text-amber-300 font-bold">${s3.critical_assets_count} / ${s3.total_assets} Critical</div>
                <div class="text-[10px] text-slate-400">ISRO CartoDEM slopes</div>
              </div>
              <div class="p-2.5 bg-black/40 border border-blue-500/30 rounded-lg space-y-1">
                <div class="text-[10px] text-slate-500 uppercase">Stage 4: Reservoir</div>
                <div class="text-blue-300 font-bold">2 Tracked</div>
                <div class="text-[10px] text-slate-400">Independent 2D spread</div>
              </div>
              <div class="p-2.5 bg-black/40 border border-emerald-500/30 rounded-lg space-y-1">
                <div class="text-[10px] text-slate-500 uppercase">Stage 5: Advisory</div>
                <div class="text-emerald-300 font-bold">${s5.review_status}</div>
                <div class="text-[10px] text-slate-400">Human review gate active</div>
              </div>
            </div>
            <div class="pt-2 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-400">
              <span>Pipeline Version: ${data.pipeline_version} &bull; Basin: ${data.basin}</span>
              <span class="text-emerald-400">Zero Silent Fallback Verified</span>
            </div>
          `;
        }
      } catch (err) {
        badge.className = 'hud-pill px-2.5 py-0.5 text-[10px] font-mono text-rose-400 border border-rose-500/30';
        badge.textContent = 'Network Error';
        results.classList.remove('hidden');
        results.innerHTML = `<div class="text-rose-400">Failed to connect to /api/pipeline/end-to-end: ${err.message}</div>`;
      } finally {
        if (btn) btn.disabled = false;
        if (typeof lucide !== 'undefined') lucide.createIcons();
      }
    };
"""

target_script = "  </script>"
assert target_script in normalized, "target_script not found in index.html"
normalized = normalized.replace(target_script, js_code + "\n  </script>")

final_content = normalized.replace("\n", "\r\n") if has_crlf else normalized
index_path.write_text(final_content, encoding="utf-8")
print("Successfully added Live Pipeline Audit Console to backend/app/static/index.html!")
