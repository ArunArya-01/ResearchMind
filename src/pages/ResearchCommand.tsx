import { useState, useEffect } from "react";
import FloatingPanel from "../components/FloatingPanel";
import ParallaxContainer from "../components/ParallaxContainer";
import RadialGauge from "../components/RadialGauge";
import { BookOpen } from "lucide-react";

const ResearchCommand = () => {
  const [recentUploads, setRecentUploads] = useState<any[]>([]);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem("recent_analysis") || "[]");
      setRecentUploads(stored);
    } catch (e) {
      setRecentUploads([]);
    }
  }, []);

  const papersProcessed = recentUploads.length;
  const connectionsFound = recentUploads.reduce((sum, u) => sum + (u.keywords || 0), 0);
  const totalElements = recentUploads.reduce((sum, u) => sum + (u.elements || 0), 0);
  const discoveryScore = (papersProcessed * 10) + (totalElements * 0.5);

  const statsConfig = [
    { label: "Active Threads", value: papersProcessed > 0 ? "1" : "0" },
    { label: "Papers Processed", value: papersProcessed.toString() },
    { label: "Connections Found", value: connectionsFound.toString() },
    { label: "Discovery Score", value: discoveryScore.toFixed(1) },
  ];

  return (
    <div className="min-h-screen pt-24 px-6 pb-12">
      <ParallaxContainer>
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div
            className="mb-12 text-center"
          >
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
            {recentUploads.length === 0 ? (
              <div className="glass-panel p-5 col-span-1 md:col-span-2 lg:col-span-4 text-center">
                <h3 className="text-crimson font-display font-semibold text-lg flex justify-center items-center h-full">
                  Ready for Ingestion - No papers processed yet.
                </h3>
              </div>
            ) : (
              recentUploads.map((disc, idx) => {
                const Icon = BookOpen;
                return (
                  <div
                    key={idx}
                    className="glass-panel p-5 cursor-pointer group relative overflow-hidden"
                    style={{ transformStyle: "preserve-3d", transform: "translateZ(50px)" }}
                  >
                    <div className="flex items-start justify-between mb-4 relative z-10">
                      <div className="p-2 rounded-xl bg-background">
                        <Icon className="w-5 h-5 text-crimson" />
                      </div>
                      <RadialGauge progress={disc.progress} size={56} />
                    </div>

                    <h3 className="text-pure-black font-display font-semibold text-sm mb-1 leading-tight relative z-10 truncate" title={disc.title}>
                      {disc.title}
                    </h3>
                    <p className="text-pure-black/40 font-mono text-xs mb-3 relative z-10">{disc.domain}</p>

                    <div className="flex flex-col gap-2 relative z-10 mt-2">
                      <div className="flex items-center justify-between">
                        <span className="text-pure-black/30 font-mono text-xs">
                          {disc.elements} elements
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-crimson font-mono text-[10px] font-bold">Safety Risk: {((disc.elements * 7) % 60) + 20}%</span>
                          <div className="w-2 h-2 rounded-full bg-crimson animate-pulse" />
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
