import { useState, useEffect } from "react";
import FloatingPanel from "../components/FloatingPanel";
import ParallaxContainer from "../components/ParallaxContainer";
import RadialGauge from "../components/RadialGauge";
import { BookOpen } from "lucide-react";

const ResearchCommand = () => {
  const [papers, setPapers] = useState<any[]>([]);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem("processedPapers") || "[]");
      setPapers(stored.reverse());
    } catch (e) {
      setPapers([]);
    }
  }, []);

  const papersProcessed = papers.length;
  const averageScore = papersProcessed > 0 ? papers.reduce((sum, p) => sum + (p.score || 0), 0) / papersProcessed : 0;
  const discoveryScore = (papersProcessed * 10) + (averageScore * 5);

  const statsConfig = [
    { label: "Active Threads", value: papersProcessed > 0 ? "1" : "0" },
    { label: "Papers Processed", value: papersProcessed.toString() },
    { label: "Average Risk (\u0393)", value: averageScore.toFixed(1) },
    { label: "Discovery Index", value: discoveryScore.toFixed(1) },
  ];

  return (
    <div className="min-h-screen pt-24 px-6 pb-12">
      <ParallaxContainer>
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-12 text-center">
            <h1 className="text-bone font-display text-5xl font-bold tracking-tight mb-3">
              Research <span className="text-crimson">Command</span>
            </h1>
            <p className="text-bone/40 font-mono text-sm">
              Live Synthesis Tracking · Reacting to Ingestion Streams
            </p>
          </div>

          {/* Stats Bar */}
          <FloatingPanel z={40} className="mb-10 p-4 flex items-center justify-between">
            <div className="flex items-center gap-8">
              {statsConfig.map((stat) => (
                <div key={stat.label} className="text-center">
                  <p className="text-pure-black font-display text-2xl font-bold">{stat.value}</p>
                  <p className="text-pure-black/40 font-mono text-xs">{stat.label}</p>
                </div>
              ))}
            </div>
          </FloatingPanel>

          {/* Discovery Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {papers.length === 0 ? (
              <div className="glass-panel p-5 col-span-1 md:col-span-2 lg:col-span-4 text-center">
                <h3 className="text-crimson font-display font-semibold text-lg flex justify-center items-center h-full">
                  Ready for Ingestion - No papers processed yet.
                </h3>
              </div>
            ) : (
              papers.map((p, idx) => {
                const Icon = BookOpen;
                const score = p.score || 0;
                let scoreColor = "text-cyan-500";
                let badgeBg = "bg-cyan-500/20";
                let dotBg = "bg-cyan-500";
                
                if (score > 7.5) {
                  scoreColor = "text-red-500";
                  badgeBg = "bg-red-500/20";
                  dotBg = "bg-red-500";
                } else if (score > 4.0) {
                  scoreColor = "text-yellow-500";
                  badgeBg = "bg-yellow-500/20";
                  dotBg = "bg-yellow-500";
                }

                return (
                  <div
                    key={`${p.id}-${idx}`}
                    className="glass-panel p-5 cursor-pointer group relative overflow-hidden flex flex-col justify-between"
                    style={{ transformStyle: "preserve-3d", transform: "translateZ(50px)" }}
                  >
                    <div>
                      <div className="flex items-start justify-between mb-4 relative z-10">
                        <div className={`p-2 rounded-xl ${badgeBg}`}>
                          <Icon className={`w-5 h-5 ${scoreColor}`} />
                        </div>
                        <RadialGauge progress={(score / 10) * 100} size={56} />
                      </div>

                      <h3 className="text-pure-black font-display font-semibold text-sm mb-1 leading-tight relative z-10 truncate" title={p.title}>
                        {p.title}
                      </h3>
                      <p className="text-pure-black/40 font-mono text-xs mb-3 relative z-10">Analyzed: {p.date}</p>
                    </div>

                    <div className="flex flex-col gap-2 relative z-10 mt-2">
                      <div className="flex items-center justify-between">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${badgeBg} ${scoreColor}`}>
                          {p.status}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className={`font-mono text-[10px] font-bold uppercase ${scoreColor}`}>
                             \u0393 Score: {score.toFixed(1)}
                          </span>
                          <div className={`w-2 h-2 rounded-full animate-pulse ${dotBg}`} />
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </ParallaxContainer>
    </div>
  );
};

export default ResearchCommand;
