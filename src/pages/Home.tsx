

const cards = [
  { phase: 'Phase 01', title: 'Neural Lattice\nOptimization', stat: '82%', detail1: '4.2TB Processed', detail2: 'Node Cluster: Active', icon1: 'database', icon2: 'hub' },
  { phase: 'Phase 03', title: 'Synthetic\nBiometrics', stat: '45%', detail1: 'Gen-4 Sequencing', detail2: 'ETA: 14 Days', icon1: 'biotech', icon2: 'timer' },
  { phase: 'Experimental', title: 'Quantum\nEntanglement', stat: '94%', detail1: '128 Qubits Stable', detail2: 'Encryption Verified', icon1: 'memory', icon2: 'shield' },
  { phase: 'Monitoring', title: 'Atmospheric\nPulse Lab', stat: '62%', detail1: 'Pressure: 101.3kPa', detail2: 'Vapor Density: 0.44', icon1: 'air', icon2: 'cloud' },
  { phase: 'Ideation', title: 'Autonomous\nSwarm Ethics', stat: '22%', detail1: 'Legal Review Pending', detail2: 'Ethical Model v0.4', icon1: 'policy', icon2: 'psychology' },
];

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-8 py-12">
      <header className="mb-16">
        <h1 className="font-display text-5xl font-bold tracking-tighter text-on-surface mb-8 max-w-2xl leading-[1.1]">
          RESEARCH <br/>COMMAND CENTER
        </h1>
        <div className="relative w-full max-w-3xl group">
          <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
            <span className="material-symbols-outlined text-outline">search</span>
          </div>
          <input 
            className="w-full glass-panel border border-white/30 rounded-xl py-5 pl-14 pr-6 text-lg font-display text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary/10 hover:bg-white/30 transition-all shadow-[0_10px_30px_rgba(0,0,0,0.03)]"
            placeholder="Execute Cross-Domain Synthesis..." 
            type="text"
          />
          <div className="absolute inset-y-0 right-4 flex items-center gap-2">
            <kbd className="font-mono text-[10px] px-2 py-1 bg-on-surface/5 text-on-surface-variant rounded border border-white/20">
              CMD + K
            </kbd>
          </div>
        </div>
      </header>
      
      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
        {cards.map((card, i) => (
          <div key={i} className="glass-panel p-8 rounded-xl group hover:translate-y-[-4px] transition-all duration-300">
            <div className="flex justify-between items-start mb-12">
              <div>
                <span className="font-mono text-[10px] uppercase tracking-widest text-on-surface-variant font-bold px-2 py-1 bg-surface-container rounded-full">{card.phase}</span>
                <h3 className="font-display text-2xl font-bold text-on-surface mt-4 leading-tight whitespace-pre-line">{card.title}</h3>
              </div>
              <div className="relative w-16 h-16 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle className="text-white/20" cx="32" cy="32" fill="transparent" r="28" stroke="currentColor" strokeWidth="4"></circle>
                  <circle cx="32" cy="32" fill="transparent" r="28" stroke="url(#grad1)" strokeDasharray="175" strokeDashoffset={175 - (175 * parseInt(card.stat) / 100)} strokeLinecap="round" strokeWidth="4"></circle>
                  <defs>
                    <linearGradient id="grad1" x1="0%" x2="100%" y1="0%" y2="0%">
                      <stop offset="0%" stopColor="#3b82f6"></stop>
                      <stop offset="100%" stopColor="#ef4444"></stop>
                    </linearGradient>
                  </defs>
                </svg>
                <span className="absolute font-mono text-[10px] font-bold">{card.stat}</span>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-on-surface-variant">
                <span className="material-symbols-outlined text-sm">{card.icon1}</span>
                <span className="font-mono text-[11px]">{card.detail1}</span>
              </div>
              <div className="flex items-center gap-3 text-on-surface-variant">
                <span className="material-symbols-outlined text-sm">{card.icon2}</span>
                <span className="font-mono text-[11px]">{card.detail2}</span>
              </div>
            </div>
          </div>
        ))}

        {/* Focus State Card */}
        <div className="glass-panel p-8 rounded-xl border-primary-container/20 group hover:translate-y-[-4px] transition-all duration-300 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-bl-full pointer-events-none"></div>
          <div className="flex justify-between items-start mb-12">
            <div>
              <span className="font-mono text-[10px] uppercase tracking-widest text-white font-bold px-2 py-1 bg-on-surface rounded-full">Critical</span>
              <h3 className="font-display text-2xl font-bold text-on-surface mt-4 leading-tight whitespace-pre-line">Kinetic Energy<br/>Capture</h3>
            </div>
            <div className="relative w-16 h-16 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90">
                <circle className="text-white/20" cx="32" cy="32" fill="transparent" r="28" stroke="currentColor" strokeWidth="4"></circle>
                <circle cx="32" cy="32" fill="transparent" r="28" stroke="url(#grad2)" strokeDasharray="175" strokeDashoffset="40" strokeLinecap="round" strokeWidth="4"></circle>
                <defs>
                  <linearGradient id="grad2" x1="0%" x2="100%" y1="0%" y2="0%">
                    <stop offset="0%" stopColor="#3b82f6"></stop>
                    <stop offset="100%" stopColor="#ef4444"></stop>
                  </linearGradient>
                </defs>
              </svg>
              <span className="absolute font-mono text-[10px] font-bold">78%</span>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-3 text-on-surface-variant">
              <span className="material-symbols-outlined text-sm">bolt</span>
              <span className="font-mono text-[11px]">Efficiency: 92.4%</span>
            </div>
            <div className="flex items-center gap-3 text-on-surface-variant">
              <span className="material-symbols-outlined text-sm">precision_manufacturing</span>
              <span className="font-mono text-[11px]">Testing: Live</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
