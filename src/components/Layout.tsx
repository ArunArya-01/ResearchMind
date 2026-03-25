import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  
  return (
    <div className="min-h-screen">
      {/* TopNavBar */}
      <nav className="fixed top-0 w-full z-50 glass-panel border-b border-white/30 flex justify-between items-center px-8 h-16">
        <div className="flex items-center gap-8">
          <span className="text-xl font-bold tracking-tighter text-on-surface font-display">Luxury Digital Lab</span>
          <div className="hidden md:flex items-center gap-6">
            <Link to="/" className={`font-bold font-mono text-sm tracking-tight transition-all duration-300 ${location.pathname === '/' ? 'text-on-surface border-b-2 border-on-surface pb-1' : 'text-on-surface-variant hover:bg-white/30 hover:backdrop-blur-xl px-2 py-1 rounded'}`}>Dashboard</Link>
            <Link to="/analysis" className={`font-medium font-mono text-sm tracking-tight transition-all duration-300 ${location.pathname === '/analysis' ? 'text-on-surface border-b-2 border-on-surface pb-1' : 'text-on-surface-variant hover:bg-white/30 hover:backdrop-blur-xl px-2 py-1 rounded'}`}>Analysis</Link>
            <Link to="/report" className={`font-medium font-mono text-sm tracking-tight transition-all duration-300 ${location.pathname === '/report' ? 'text-on-surface border-b-2 border-on-surface pb-1' : 'text-on-surface-variant hover:bg-white/30 hover:backdrop-blur-xl px-2 py-1 rounded'}`}>Synthesis</Link>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-[#1a1c1c]/5 px-3 py-1.5 rounded-full border border-white/20">
            <span className="w-2 h-2 rounded-full bg-secondary-container shadow-[0_0_12px_#b6f48a] animate-pulse"></span>
            <span className="font-mono text-[10px] uppercase tracking-widest text-on-surface-variant font-bold">Swarm Status: Active</span>
          </div>
          <button className="material-symbols-outlined text-on-surface scale-95 active:scale-90 transition-transform">sensors</button>
          <button className="material-symbols-outlined text-on-surface scale-95 active:scale-90 transition-transform">terminal</button>
          <div className="w-8 h-8 rounded-lg overflow-hidden border border-white/40 bg-surface-container">
            <img alt="User" className="w-full h-full object-cover" src="https://ui-avatars.com/api/?name=Research+Lead&background=271310&color=fff" />
          </div>
        </div>
      </nav>

      {/* SideNavBar */}
      <aside className="fixed left-0 top-0 h-screen w-64 border-r border-white/30 bg-white/10 backdrop-blur-[40px] pt-20 flex-col py-6 hidden lg:flex">
        <div className="px-6 mb-8">
          <h2 className="text-lg font-black text-on-surface font-display">Swarm Status</h2>
          <p className="font-mono text-[11px] text-on-surface-variant">Active: Pulse 0.8Hz</p>
        </div>
        <nav className="flex-1 space-y-1">
          <Link to="/" className={`mx-2 px-4 py-3 flex items-center gap-3 transition-colors duration-200 rounded-md ${location.pathname === '/' ? 'bg-primary text-white shadow-[0_10px_20px_rgba(39,19,16,0.15)]' : 'text-on-surface-variant hover:bg-white/20 hover:backdrop-blur-md'}`}>
            <span className="material-symbols-outlined">dashboard</span>
            <span className="font-display font-medium text-sm">Command</span>
          </Link>
          <Link to="/analysis" className={`mx-2 px-4 py-3 flex items-center gap-3 transition-colors duration-200 rounded-md ${location.pathname === '/analysis' ? 'bg-primary text-white shadow-[0_10px_20px_rgba(39,19,16,0.15)]' : 'text-on-surface-variant hover:bg-white/20 hover:backdrop-blur-md'}`}>
            <span className="material-symbols-outlined">biotech</span>
            <span className="font-display font-medium text-sm">Vision</span>
          </Link>
          <Link to="/report" className={`mx-2 px-4 py-3 flex items-center gap-3 transition-colors duration-200 rounded-md ${location.pathname === '/report' ? 'bg-primary text-white shadow-[0_10px_20px_rgba(39,19,16,0.15)]' : 'text-on-surface-variant hover:bg-white/20 hover:backdrop-blur-md'}`}>
            <span className="material-symbols-outlined">hub</span>
            <span className="font-display font-medium text-sm">Swarm</span>
          </Link>
        </nav>
        <div className="px-4 mb-6">
          <button className="w-full bg-primary text-white py-3 rounded-md font-display font-bold text-sm flex items-center justify-center gap-2 shadow-[0_10px_20px_rgba(39,19,16,0.15)] hover:bg-primary-container transition-colors">
            Initiate Synthesis
          </button>
        </div>
      </aside>

      {/* Main Content Canvas */}
      <main className="lg:pl-64 pt-16 min-h-screen">
        {children}
      </main>

      {/* Status Terminal */}
      <div className="fixed bottom-6 right-6 z-40">
        <div className="bg-on-surface/90 backdrop-blur-md px-4 py-2 rounded border border-white/10 flex flex-col gap-1 shadow-2xl">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
            <span className="font-mono text-[10px] text-white/60 tracking-tighter">NODE_77_STABLE</span>
          </div>
          <div className="flex justify-between gap-8">
            <span className="font-mono text-[9px] text-white/40">COORD: 40.7128° N, 74.0060° W</span>
            <span className="font-mono text-[9px] text-white/40">12:44:02:009</span>
          </div>
        </div>
      </div>

    </div>
  );
}
