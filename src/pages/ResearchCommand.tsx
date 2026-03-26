import { motion } from "framer-motion";
import FloatingPanel from "../components/FloatingPanel";
import ParallaxContainer from "../components/ParallaxContainer";
import RadialGauge from "../components/RadialGauge";
import { Atom, BookOpen, Database, FileSearch, Globe, Layers, Microscope, Zap } from "lucide-react";

const discoveries = [
  { title: "Quantum Coherence in Photosynthesis", domain: "Biophysics", progress: 87, icon: Atom, papers: 142 },
  { title: "Neural Scaling Laws", domain: "Machine Learning", progress: 63, icon: Layers, papers: 89 },
  { title: "CRISPR Off-Target Effects", domain: "Genomics", progress: 45, icon: Microscope, papers: 234 },
  { title: "Dark Matter Candidates", domain: "Astrophysics", progress: 72, icon: Globe, papers: 312 },
  { title: "Topological Insulators", domain: "Condensed Matter", progress: 91, icon: Zap, papers: 178 },
  { title: "Protein Folding Dynamics", domain: "Structural Biology", progress: 58, icon: Database, papers: 201 },
  { title: "LLM Reasoning Gaps", domain: "AI Safety", progress: 34, icon: FileSearch, papers: 67 },
  { title: "mRNA Stability Patterns", domain: "Molecular Bio", progress: 79, icon: BookOpen, papers: 156 },
];

const ResearchCommand = () => {
  return (
    <div className="min-h-screen pt-24 px-6 pb-12">
      <ParallaxContainer intensity={4}>
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12 text-center"
          >
            <h1 className="text-bone font-display text-5xl font-bold tracking-tight mb-3">
              Research <span className="text-crimson">Command</span>
            </h1>
            <p className="text-bone/40 font-mono text-sm">
              8 active discoveries · 1,379 papers indexed · 3 synthesis complete
            </p>
          </motion.div>

          {/* Stats Bar */}
          <FloatingPanel z={40} className="mb-10 p-4 flex items-center justify-between" delay={0.1}>
            <div className="flex items-center gap-8">
              {[
                { label: "Active Threads", value: "8" },
                { label: "Papers Processed", value: "1,379" },
                { label: "Connections Found", value: "2,847" },
                { label: "Discovery Score", value: "94.2" },
              ].map((stat) => (
                <div key={stat.label} className="text-center">
                  <p className="text-pure-black font-display text-2xl font-bold">{stat.value}</p>
                  <p className="text-pure-black/40 font-mono text-xs">{stat.label}</p>
                </div>
              ))}
            </div>
          </FloatingPanel>

          {/* Discovery Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {discoveries.map((disc, i) => {
              const Icon = disc.icon;
              return (
                <motion.div
                  key={disc.title}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.15 + i * 0.07 }}
                  whileHover={{
                    y: -12,
                    scale: 1.02,
                    boxShadow: "0 50px 100px -20px hsl(0 0% 0% / 0.9)",
                    transition: { duration: 0.25 },
                  }}
                  className="glass-panel p-5 cursor-pointer group relative overflow-hidden"
                  style={{ transformStyle: "preserve-3d", transform: "translateZ(50px)" }}
                >
                  <div className="flex items-start justify-between mb-4 relative z-10">
                    <div className="p-2 rounded-xl bg-background">
                      <Icon className="w-5 h-5 text-crimson" />
                    </div>
                    <RadialGauge progress={disc.progress} size={56} />
                  </div>

                  <h3 className="text-pure-black font-display font-semibold text-sm mb-1 leading-tight relative z-10">
                    {disc.title}
                  </h3>
                  <p className="text-pure-black/40 font-mono text-xs mb-3 relative z-10">{disc.domain}</p>

                  <div className="flex items-center justify-between relative z-10">
                    <span className="text-pure-black/30 font-mono text-xs">
                      {disc.papers} papers
                    </span>
                    <motion.div
                      className="w-2 h-2 rounded-full bg-crimson"
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </ParallaxContainer>
    </div>
  );
};

export default ResearchCommand;
