

export default function Analysis() {
  return (
    <div className="max-w-7xl mx-auto px-8 py-12 relative overflow-hidden">
      <div className="grid grid-cols-12 gap-8">
        
        {/* Header Section */}
        <div className="col-span-12 mb-8">
          <h1 className="font-display text-5xl font-extrabold text-on-surface tracking-tighter mb-2">MULTIMODAL ANALYSIS</h1>
          <p className="font-body text-on-surface-variant max-w-2xl text-lg leading-relaxed">
            Synthetic vision protocols for deep-tissue structural verification and recursive data validation.
          </p>
        </div>

        {/* Left: The Scan (Digital PDF View) */}
        <div className="col-span-12 xl:col-span-8 flex flex-col gap-6">
          <div className="glass-panel rounded-xl overflow-hidden relative shadow-[0_20px_40px_rgba(62,39,35,0.08)] bg-white/40 group border border-white/40">
            <div className="h-12 border-b border-white/20 flex items-center px-6 justify-between bg-white/20">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-outline text-sm">description</span>
                <span className="font-mono text-[11px] uppercase tracking-widest font-bold text-outline">structural_report_v9.pdf</span>
              </div>
              <div className="flex gap-4">
                <span className="material-symbols-outlined text-outline text-sm cursor-pointer hover:text-on-surface transition-colors">zoom_in</span>
                <span className="material-symbols-outlined text-outline text-sm cursor-pointer hover:text-on-surface transition-colors">print</span>
                <span className="material-symbols-outlined text-outline text-sm cursor-pointer hover:text-on-surface transition-colors">more_vert</span>
              </div>
            </div>
            
            <div className="aspect-[1.4/1] bg-white p-12 relative overflow-hidden flex flex-col items-center">
              {/* AI Vision Overlays */}
              <div className="absolute inset-0 pointer-events-none z-10 p-12">
                {/* Bounding Boxes */}
                <div className="absolute border border-cyan-400 bg-cyan-400/5 w-48 h-32 top-32 left-40 flex flex-col justify-end p-1">
                  <span className="text-[8px] font-mono text-cyan-400 uppercase bg-black/80 px-1 w-max">TISSUE_DENSITY: 0.982</span>
                </div>
                <div className="absolute border border-cyan-400 bg-cyan-400/5 w-64 h-24 top-72 right-48 flex flex-col justify-end p-1">
                  <span className="text-[8px] font-mono text-cyan-400 uppercase bg-black/80 px-1 w-max">ANOMALY_INDEX: 0.002</span>
                </div>
                {/* Laser Scan Line */}
                <div className="absolute top-1/2 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-60 animate-pulse"></div>
                
                {/* Label */}
                <div className="absolute top-6 right-6 font-mono text-[10px] text-white bg-primary px-3 py-1 rounded-sm flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
                  [AI_VISION_KERNEL_V9]
                </div>
              </div>

              {/* PDF Content Placeholder */}
              <div className="w-full h-full max-w-3xl flex flex-col gap-8 opacity-80 filter grayscale hover:grayscale-0 transition-all duration-700">
                <div className="w-full h-4 bg-stone-200 rounded-sm"></div>
                <div className="grid grid-cols-2 gap-8 h-full">
                  <div className="space-y-4">
                    <div className="w-3/4 h-3 bg-stone-100 rounded-sm"></div>
                    <div className="w-full h-3 bg-stone-100 rounded-sm"></div>
                    <div className="w-1/2 h-3 bg-stone-100 rounded-sm"></div>
                    <div className="aspect-square bg-stone-50 border border-stone-200 flex items-center justify-center overflow-hidden">
                      <img alt="Scientific Chart Image" className="w-full h-full object-cover" src="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=800"/>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="aspect-video bg-stone-50 border border-stone-200 overflow-hidden">
                      <img alt="Data Chart" className="w-full h-full object-cover" src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800"/>
                    </div>
                    <div className="w-full h-3 bg-stone-100 rounded-sm"></div>
                    <div className="w-3/4 h-3 bg-stone-100 rounded-sm"></div>
                    <div className="w-full h-48 bg-stone-50 rounded-sm border border-stone-200 p-4"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Technical Analytics Bar */}
          <div className="grid grid-cols-3 gap-6">
            <div className="glass-panel p-6 rounded-xl border border-white/40 group hover:bg-white/40 transition-all duration-300">
              <div className="font-mono text-[10px] text-on-surface-variant uppercase tracking-widest mb-1">Processing Load</div>
              <div className="text-2xl font-display font-bold text-on-surface">12.4 GFLOPS</div>
              <div className="w-full bg-white/50 h-1 mt-3 rounded-full overflow-hidden">
                <div className="bg-primary h-full w-[40%]"></div>
              </div>
            </div>
            <div className="glass-panel p-6 rounded-xl border border-white/40 group hover:bg-white/40 transition-all duration-300">
              <div className="font-mono text-[10px] text-on-surface-variant uppercase tracking-widest mb-1">Latency Delta</div>
              <div className="text-2xl font-display font-bold text-on-surface">2.4ms</div>
              <div className="w-full bg-white/50 h-1 mt-3 rounded-full overflow-hidden">
                <div className="bg-green-500 h-full w-[15%]"></div>
              </div>
            </div>
            <div className="glass-panel p-6 rounded-xl border border-white/40 group hover:bg-white/40 transition-all duration-300">
              <div className="font-mono text-[10px] text-on-surface-variant uppercase tracking-widest mb-1">Vision Confidence</div>
              <div className="text-2xl font-display font-bold text-on-surface">99.87%</div>
              <div className="w-full bg-white/50 h-1 mt-3 rounded-full overflow-hidden">
                <div className="bg-primary h-full w-[98%]"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Verification Math Sandbox Side Pane */}
        <div className="col-span-12 xl:col-span-4 space-y-6">
          <div className="glass-panel rounded-xl flex flex-col shadow-[0_20px_40px_rgba(62,39,35,0.08)] h-[600px] border border-white/40">
            <div className="p-6 border-b border-white/20">
              <div className="flex justify-between items-center mb-1">
                <h2 className="font-display text-xl font-bold text-on-surface">Math Sandbox</h2>
                <span className="material-symbols-outlined text-outline">terminal</span>
              </div>
              <p className="font-body text-xs text-on-surface-variant">Recursive validation logs for synthesis alignment.</p>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 font-mono text-[11px] leading-relaxed bg-black/5 text-on-surface">
              <div className="space-y-3">
                <div className="text-on-surface-variant"># Initializing Vision Verification Loop</div>
                <div className="flex gap-2"><span className="text-green-600">[PASSED]</span><span>kernel.initialize(mode='multimodal')</span></div>
                <div className="flex gap-2"><span className="text-green-600">[PASSED]</span><span>tensor_stream.sync(delta=2.4)</span></div>
                
                <div className="pl-4 border-l border-on-surface/20 ml-2 py-1 space-y-1">
                  <div className="text-on-surface-variant opacity-80">import numpy as np</div>
                  <div>def calculate_tissue_variance(data):</div>
                  <div className="pl-4">return np.std(data) / np.mean(data)</div>
                </div>
                
                <div className="flex gap-2"><span className="text-green-600">[PASSED]</span><span>calc_variance(stream_09) -&gt; 0.002</span></div>
                
                <div className="text-on-surface-variant mt-4"># Recursive Bounding Box Logic</div>
                <div className="flex gap-2"><span className="text-green-600">[PASSED]</span><span>cv2.rectangle(img, pt1, pt2, (0, 242, 255))</span></div>
                <div className="flex gap-2"><span className="text-green-600">[PASSED]</span><span>validation_matrix.align(target='report_v9')</span></div>
                
                <div className="text-on-surface-variant mt-4"># Exporting Synthesis Meta-Data</div>
                <div className="flex gap-2"><span className="text-green-600">[PASSED]</span><span>synthesis_engine.push(buffer=verified_0x)</span></div>
                <div className="animate-pulse text-on-surface-variant">_</div>
              </div>
            </div>
            
            <div className="p-4 border-t border-white/20 bg-white/30 backdrop-blur-md">
              <div className="flex items-center justify-between mt-auto">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  <span className="text-[10px] font-mono uppercase text-on-surface-variant">Sync Complete</span>
                </div>
                <button className="text-[10px] font-mono font-bold uppercase tracking-widest text-primary hover:underline transition-all">Download Logs</button>
              </div>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-xl border-l-[4px] border-l-primary shadow-[0_10px_20px_rgba(62,39,35,0.05)] bg-white/40">
            <div className="font-display font-bold text-lg text-on-surface mb-2">Synthesis Readiness</div>
            <p className="font-body text-sm text-on-surface-variant mb-4 leading-relaxed">
              All structural parameters have been verified through recursive vision loops. System is ready for Stage 3: Molecular Synthesis.
            </p>
            <div className="flex flex-wrap gap-2">
              <span className="bg-surface-variant text-on-surface-variant text-[10px] font-mono px-3 py-1 rounded-full uppercase tracking-tighter shadow-sm border border-white/50">VERIFIED_01</span>
              <span className="bg-surface-variant text-on-surface-variant text-[10px] font-mono px-3 py-1 rounded-full uppercase tracking-tighter shadow-sm border border-white/50">STRUCTURAL_ALIGNED</span>
              <span className="bg-surface-variant text-on-surface-variant text-[10px] font-mono px-3 py-1 rounded-full uppercase tracking-tighter shadow-sm border border-white/50">V9_COMPLIANT</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
