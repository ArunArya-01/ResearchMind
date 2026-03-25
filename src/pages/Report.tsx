

const traces = [
  { type: 'VISIONARY_LOG', color: 'text-[#0ea5e9]', border: 'border-[#0ea5e9]', time: '14:02:31:002', text: 'Hypothesis: Neural mesh synchronization exceeds predicted coherence limits. Proposing 12% increase in node density at the core.' },
  { type: 'SKEPTIC_LOG', color: 'text-[#ba1a1a]', border: 'border-[#ba1a1a]', time: '14:02:33:419', text: 'Warning: Increased density correlates with entropy spikes in sector 7. Discovery gap widening. Correlation is not causation.' },
  { type: 'VISIONARY_LOG', color: 'text-[#0ea5e9]', border: 'border-[#0ea5e9]', time: '14:02:40:112', text: 'Bypassing entropy constraints. Initializing quantum annealing sequence for the Discovery Gap.' },
  { type: 'SKEPTIC_LOG', color: 'text-[#ba1a1a]', border: 'border-[#ba1a1a]', time: '14:02:45:982', text: 'Synthesis failure imminent if local feedback loops are not stabilized. Probability of insight collapse: 44%.' }
];

export default function Report() {
  return (
    <div className="bg-primary-container min-h-[calc(100vh-4rem)] p-8 lg:p-12 text-white overflow-hidden relative">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-full">
        {/* Left: Adversarial Trace */}
        <section className="col-span-1 lg:col-span-3 flex flex-col gap-6 h-[600px] lg:h-auto">
          <div className="glass-panel rounded-xl p-4 h-full flex flex-col bg-white/5 border-white/10">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-white/10">
              <span className="font-mono text-[10px] text-white/50 font-bold uppercase tracking-tighter">Adversarial Trace</span>
              <span className="font-mono text-[10px] text-white/40">0.98 Confidence</span>
            </div>
            <div className="flex-1 space-y-4 overflow-y-auto pr-2">
              {traces.map((trace, i) => (
                <div key={i} className={`border-l-2 ${trace.border} pl-3 py-1`}>
                  <div className="flex justify-between items-center mb-1">
                    <span className={`font-mono text-[9px] ${trace.color} font-bold`}>[{trace.type}]</span>
                    <span className="font-mono text-[8px] text-white/40">{trace.time}</span>
                  </div>
                  <p className={`font-mono text-[11px] ${trace.color} leading-relaxed opacity-90`}>{trace.text}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Center: Neural Nexus */}
        <section className="col-span-1 lg:col-span-5 relative flex items-center justify-center min-h-[400px]">
          <div className="w-full h-full rounded-2xl relative shadow-2xl flex items-center justify-center bg-white/5 backdrop-blur-[60px] border border-white/10 overflow-hidden">
            <div className="absolute inset-0 opacity-20 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at center, rgba(255,255,255,0.1) 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
            
            <div className="absolute top-12 left-12 font-mono text-[8px] opacity-30">∫ exp(-x²) dx = √π</div>
            <div className="absolute top-1/3 right-12 font-mono text-[8px] opacity-30">E = mc² [δψ/δt]</div>
            
            <div className="absolute top-10 left-1/2 -translate-x-1/2 font-mono text-[8px] text-white/30 uppercase tracking-[0.5em]">S-7 NEURAL TOPOGRAPHY</div>
            
            {/* Simplified Vortex */}
            <div className="relative flex items-center justify-center animate-pulse">
              <div className="w-32 h-32 rounded-full border border-red-500/50 shadow-[0_0_30px_rgba(220,38,38,0.5)]"></div>
              <div className="absolute w-2 h-2 rounded-full bg-red-500 shadow-[0_0_10px_rgba(220,38,38,1)]"></div>
              <span className="absolute -bottom-8 font-mono text-[10px] text-red-500 font-bold">[CRITICAL_ANOMALY_742]</span>
            </div>

            <div className="absolute top-6 right-6 bg-black/70 backdrop-blur-md px-4 py-3 rounded shadow-2xl flex flex-col gap-2 min-w-[140px] border border-white/20">
              <div className="flex justify-between items-center border-b border-white/20 pb-2">
                <span className="font-mono text-[9px] font-bold tracking-widest uppercase text-white">HUD_V.2.0</span>
                <span className="w-1.5 h-1.5 rounded-full bg-[#84cc1c] animate-pulse"></span>
              </div>
              <div className="font-mono text-[10px] space-y-1 text-white">
                <div className="flex justify-between"><span className="opacity-50">LATENCY</span><span>4.02ms</span></div>
                <div className="flex justify-between"><span className="opacity-50">CORE_T</span><span>32.1°C</span></div>
              </div>
            </div>
          </div>
        </section>

        {/* Right: Manuscript */}
        <section className="col-span-1 lg:col-span-4 flex items-start justify-end">
          <div className="w-full max-w-sm rounded-xl p-2 shadow-2xl glass-panel bg-white/10">
            <div className="bg-[#F5F5F5] h-full rounded-lg shadow-inner p-10 relative overflow-hidden text-on-surface">
              <header className="mb-8">
                <h2 className="text-2xl font-serif font-medium italic border-b border-stone-200 pb-2">Swarm Synthesis Report</h2>
                <p className="text-[10px] uppercase tracking-widest text-stone-400 mt-2 font-mono">Experiment ID: ALCH-77-B</p>
              </header>
              <div className="space-y-6 text-sm leading-relaxed font-serif">
                <p className="first-letter:text-4xl first-letter:font-bold first-letter:float-left first-letter:mr-2">
                  In the pursuit of non-linear knowledge structures, the Swarm Engine has identified a profound divergence between traditional linear synthesis and the emergent patterns of adversarial discourse. 
                </p>
                <p>
                  The "Discovery Gap," localized in the tertiary quadrant, indicates a void in current empirical understanding where qualitative anomalies resist quantification.
                </p>
                <div className="italic border-l-2 border-stone-300 pl-4 py-2 text-stone-600">
                  "The beauty of the digital lab lies not in the answers it provides, but in the precision with which it identifies the unknown."
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
