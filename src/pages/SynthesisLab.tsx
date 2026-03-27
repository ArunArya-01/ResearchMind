import { useState, useMemo, useCallback, useEffect, useRef } from "react";
import FloatingPanel from "../components/FloatingPanel";
import { Rocket, ShieldAlert, FileText, Play, Loader2, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? `http://${window.location.hostname}:8000`;

const generateNodes = (count: number) => {
  const nodes: { id: number; x: number; y: number; size: number; connections: number[] }[] = [];
  for (let i = 0; i < count; i++) {
    const angle = (i / count) * Math.PI * 2 + Math.random() * 0.5;
    const radius = 120 + Math.random() * 280;
    nodes.push({
      id: i,
      x: 400 + Math.cos(angle) * radius + (Math.random() - 0.5) * 60,
      y: 300 + Math.sin(angle) * radius + (Math.random() - 0.5) * 60,
      size: 2 + Math.random() * 4,
      connections: [],
    });
  }
  for (let i = 0; i < count; i++) {
    const numConns = 1 + Math.floor(Math.random() * 3);
    for (let j = 0; j < numConns; j++) {
      const target = Math.floor(Math.random() * count);
      if (target !== i) nodes[i].connections.push(target);
    }
  }
  return nodes;
};

// Mock data removed in favor of dynamic WebSocket stream

const SynthesisLab = () => {
  const [zoomedIn, setZoomedIn] = useState(false);
  const [nodes, setNodes] = useState<{ id: number; x: number; y: number; size: number; connections: number[] }[] | null>([]);
  const [visionaryLogs, setVisionaryLogs] = useState<{ time: string; msg: string }[]>([{ time: "T+0.00s", msg: "System Ready" }]);
  const [skepticLogs, setSkepticLogs] = useState<{ time: string; msg: string }[]>([{ time: "T+0.00s", msg: "System Ready" }]);
  const [finalReportContent, setFinalReportContent] = useState<string | null>(null);
  const [pdfActive, setPdfActive] = useState(false);
  const [pdfKeywords, setPdfKeywords] = useState<string[]>([]);
  const [lastUploadTime, setLastUploadTime] = useState<string | null>(null);

  const visionaryEndRef = useRef<HTMLDivElement>(null);
  const skepticEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    visionaryEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [visionaryLogs]);

  useEffect(() => {
    skepticEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [skepticLogs]);

  const fetchNodes = useCallback(() => {
    setNodes(null);
    fetch(`${API_BASE_URL}/nodes`)
      .then(res => {
        if (!res.ok) throw new Error("Failed");
        return res.json();
      })
      .then(data => setNodes(data))
      .catch(() => {
        setNodes(generateNodes(200));
      });
  }, []);

  useEffect(() => {
    const checkStorage = () => {
      setPdfActive(localStorage.getItem("pdf_active") === "true");
      
      const currentUploadTime = localStorage.getItem("pdf_upload_time");
      if (currentUploadTime && currentUploadTime !== lastUploadTime) {
         setLastUploadTime(currentUploadTime);
         setVisionaryLogs([{ time: "T+0.00s", msg: "System Ready" }]);
         setSkepticLogs([{ time: "T+0.00s", msg: "System Ready" }]);
         setFinalReportContent(null);
      }

      try {
        const storedKeywords = JSON.parse(localStorage.getItem("pdf_keywords") || "[]");
        if (storedKeywords.length > 0) {
          setPdfKeywords(storedKeywords);
        } else {
          setPdfKeywords([]);
        }
      } catch (e) {
        setPdfKeywords([]);
      }
    };

    checkStorage();
    const interval = setInterval(checkStorage, 500);

    fetchNodes();

    return () => clearInterval(interval);
  }, [fetchNodes]);

  const handleStartDiscovery = useCallback(() => {
    if (!pdfActive) {
      alert("Please upload a manuscript first.");
      return;
    }

    setZoomedIn(true);
    setTimeout(() => setZoomedIn(false), 4000);

    setVisionaryLogs([{ time: "T+0.00s", msg: "Analyzing..." }]);
    setSkepticLogs([{ time: "T+0.00s", msg: "Analyzing..." }]);
    setFinalReportContent(null);

    const ws = new WebSocket("ws://localhost:8000/ws/swarm");
    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: "start",
        topic: "Aircraft Engine RUL"
      }));
    };
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'final_report') {
          setFinalReportContent(data.content || data.message);
          return;
        }
        const logEntry = {
          time: `T+${(performance.now() / 1000).toFixed(2)}s`,
          msg: data.message || data.content || ""
        };
        if (data.agent === "Visionary") {
          setVisionaryLogs(prev => [...prev, logEntry]);
        } else if (data.agent === "Skeptic") {
          setSkepticLogs(prev => [...prev, logEntry]);
        }
      } catch (e) {
        console.error("WebSocket message parse error", e);
      }
    };
  }, [pdfActive, pdfKeywords]);

  return (
    <div className="min-h-screen bg-obsidian pt-24 px-6 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-crimson font-display text-5xl font-bold tracking-tight mb-3">
            Synthesis Lab
          </h1>
          <p className="text-bone/40 font-mono text-sm mb-6">
            Knowledge graph · Swarm debate · Final manuscript
          </p>
          <button
            onClick={handleStartDiscovery}
            disabled={!pdfActive}
            className={`px-6 py-3 rounded-xl font-display font-semibold text-sm flex items-center gap-2 mx-auto transition-shadow ${pdfActive ? "bg-crimson text-white hover:shadow-[0_0_30px_hsl(354_96%_43%_/_0.5)]" : "bg-obsidian border border-crimson/30 text-crimson/50 cursor-not-allowed"}`}
          >
            <Play className="w-4 h-4" />
            Start Discovery
          </button>
        </div>

        {/* Knowledge Graph */}
        <FloatingPanel z={50} className="mb-8 overflow-hidden border border-crimson">
          <div className="p-4 border-b border-crimson flex items-center gap-2 bg-obsidian">
            <div className="w-2 h-2 rounded-full bg-crimson animate-pulse" />
            <span className="text-bone font-mono text-xs">Knowledge Graph · {nodes?.length ?? 0} nodes</span>
            <button 
              onClick={fetchNodes}
              className="ml-auto px-3 py-1.5 flex items-center gap-2 text-xs font-mono text-crimson border border-crimson/50 rounded hover:bg-crimson/10 transition-colors"
            >
              <RefreshCw className="w-3 h-3" /> Sync
            </button>
          </div>
          <div className="relative min-h-[400px] bg-obsidian">
            {!nodes ? (
              <div className="flex flex-col items-center justify-center h-[400px] text-bone/50">
                <Loader2 className="w-8 h-8 animate-spin mb-4 text-crimson" />
                <span className="font-mono text-sm">Initializing Knowledge Graph...</span>
              </div>
            ) : (
              <svg width="100%" viewBox="0 0 800 600" className="h-[400px]">
                {/* Connections - ultra-thin white */}
                {nodes?.map((node) =>
                  node?.connections?.map((target, ci) => (
                    <motion.line
                      key={`${node.id}-${ci}`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 1, delay: 1.5 }}
                      x1={node?.x ?? 0}
                      y1={node?.y ?? 0}
                      x2={nodes[target]?.x ?? 0}
                      y2={nodes[target]?.y ?? 0}
                      stroke="hsl(0 0% 100% / 0.08)"
                      strokeWidth={0.5}
                    />
                  ))
                )}

              {/* Red glow from Discovery Gap */}
              <defs>
                <radialGradient id="redGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="hsl(354 96% 43% / 0.3)" />
                  <stop offset="50%" stopColor="hsl(354 96% 43% / 0.1)" />
                  <stop offset="100%" stopColor="transparent" />
                </radialGradient>
              </defs>
              <circle cx={400} cy={300} r={80} fill="url(#redGlow)" />

              {/* Nodes - dynamic */}
              {nodes?.map((node, i) => {
                const isKeywordNode = pdfActive && i < 10 && i < pdfKeywords.length;
                const keywordText = isKeywordNode ? pdfKeywords[i] : null;
                const targetR = isKeywordNode ? (node.size * 2) : node.size;
                
                return (
                  <g key={node.id}>
                    <motion.circle
                      initial={{ 
                        cx: 400, 
                        cy: 300, 
                        r: 0 
                      }}
                      animate={{ 
                        cx: [400, 400 + (node.x - 400) * 1.2, node.x], 
                        cy: [300, 300 + (node.y - 300) * 1.2, node.y], 
                        r: [0, targetR * 1.5, targetR] 
                      }}
                      transition={{ 
                        duration: 1.5,
                        ease: "easeOut",
                        times: [0, 0.6, 1],
                        delay: Math.random() * 0.2
                      }}
                      fill={pdfActive ? "hsl(354 96% 43% / 0.9)" : "hsl(0 0% 100% / 0.8)"}
                      className={`cursor-pointer overflow-visible hover:fill-bone/50 ${
                        isKeywordNode 
                          ? "drop-shadow-[0_0_12px_rgba(217,4,41,1)]" 
                          : pdfActive 
                            ? "animate-[pulse_3s_ease-in-out_infinite] drop-shadow-[0_0_8px_rgba(217,4,41,0.8)]" 
                            : "drop-shadow-[0_0_5px_rgba(253,253,253,0.8)]"
                      }`}
                      onMouseEnter={(e: any) => {
                        const target = e.target as SVGCircleElement;
                        target.setAttribute("r", (targetR * 1.5).toString());
                      }}
                      onMouseLeave={(e: any) => {
                        const target = e.target as SVGCircleElement;
                        target.setAttribute("r", targetR.toString());
                      }}
                    />
                    {isKeywordNode && (
                      <motion.text
                        initial={{ opacity: 0, x: 400, y: 300 }}
                        animate={{ 
                          opacity: 1, 
                          x: [400, 400 + (node.x - 400) * 1.2 + targetR + 5, node.x + targetR + 6], 
                          y: [300, 300 + (node.y - 300) * 1.2 + 3, node.y + 3] 
                        }}
                        transition={{ 
                          duration: 1.5,
                          ease: "easeOut",
                          times: [0, 0.6, 1],
                          delay: 0.5 + Math.random() * 0.3 
                        }}
                        fill="hsl(0 0% 100% / 0.9)"
                        fontSize={10}
                        fontFamily="var(--font-mono)"
                        className="pointer-events-none drop-shadow-[0_0_4px_rgba(0,0,0,0.8)]"
                      >
                        {keywordText}
                      </motion.text>
                    )}
                  </g>
                );
              })}

              {/* Discovery Gap - Deep Red Pulsing Orb */}
              <circle
                cx={400}
                cy={300}
                r={22}
                fill="hsl(0 80% 30%)"
                className="animate-pulse"
              />
              <circle
                cx={400}
                cy={300}
                r={35}
                fill="none"
                stroke="hsl(354 96% 43% / 0.4)"
                strokeWidth={1}
                className="animate-[pulse_2s_ease-in-out_infinite]"
              />
              <circle
                cx={400}
                cy={300}
                r={50}
                fill="none"
                stroke="hsl(354 96% 43% / 0.15)"
                strokeWidth={0.5}
                className="animate-[pulse_2.5s_ease-in-out_infinite]"
              />
              <text x={400} y={355} textAnchor="middle" fill="hsl(354 96% 60%)" fontSize={9} fontFamily="var(--font-mono)">
                DISCOVERY GAP
              </text>
            </svg>
            )}
          </div>
        </FloatingPanel>

        {/* Swarm Debate */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Visionary */}
          <FloatingPanel z={40} className="!bg-transparent !border-0 !shadow-none">
            <div className="p-5 bg-obsidian border border-crimson/50 rounded-xl shadow-[0_8px_40px_-8px_hsl(0_0%_0%_/_0.8)] backdrop-blur">
              <div className="flex items-center gap-2 mb-4 pb-3 border-b border-crimson/20">
                <Rocket className="w-4 h-4 text-sky-blue" />
                <span className="text-bone font-mono font-bold text-sm">VISIONARY</span>
                <span className="text-bone/40 font-mono text-xs ml-auto">Agent Alpha</span>
              </div>
              <div className="space-y-3 font-mono text-xs max-h-[250px] overflow-y-auto">
                {visionaryLogs.length === 0 ? (
                  <div className="text-crimson/50 text-center py-6">No Data Ingested</div>
                ) : (
                  visionaryLogs.map((msg, i) => (
                    <div key={i}>
                      <span className="text-bone/40">{msg.time}</span>
                      <p className={`text-bone mt-0.5 ${msg.msg.startsWith("INSIGHT") ? "text-sky-blue font-bold" : ""}`}>
                        {msg.msg}
                      </p>
                    </div>
                  ))
                )}
                <div ref={visionaryEndRef} />
              </div>
            </div>
          </FloatingPanel>

          {/* Skeptic */}
          <FloatingPanel z={40} className="!bg-transparent !border-0 !shadow-none">
            <div className="p-5 bg-obsidian border border-crimson/50 rounded-xl shadow-[0_8px_40px_-8px_hsl(0_0%_0%_/_0.8)] backdrop-blur">
              <div className="flex items-center gap-2 mb-4 pb-3 border-b border-crimson/20">
                <ShieldAlert className="w-4 h-4 text-crimson" />
                <span className="text-bone font-mono font-bold text-sm">SKEPTIC</span>
                <span className="text-bone/40 font-mono text-xs ml-auto">Agent Beta</span>
              </div>
              <div className="space-y-3 font-mono text-xs max-h-[250px] overflow-y-auto">
                {skepticLogs.length === 0 ? (
                  <div className="text-crimson/50 text-center py-6">No Data Ingested</div>
                ) : (
                  skepticLogs.map((msg, i) => (
                    <div key={i}>
                      <span className="text-crimson/60">{msg.time}</span>
                      <p className={`text-bone mt-0.5 ${msg.msg.startsWith("WARNING") || msg.msg.startsWith("CHALLENGE") ? "text-crimson font-bold" : ""}`}>
                        {msg.msg}
                      </p>
                    </div>
                  ))
                )}
                <div ref={skepticEndRef} />
              </div>
            </div>
          </FloatingPanel>
        </div>

        {/* Final Manuscript */}
        {finalReportContent && (
          <FloatingPanel z={60} className="max-w-2xl mx-auto p-10 relative overflow-hidden border border-crimson min-h-[400px] overflow-y-auto max-h-[600px]">
            <div className="flex items-center gap-2 mb-6 relative z-10">
              <FileText className="w-5 h-5 text-pure-black/50" />
              <span className="text-pure-black font-display font-semibold text-sm">Final Manuscript</span>
            </div>
            <div className="font-mono text-xs leading-relaxed text-pure-black/70 space-y-0.5 relative z-10">
              <div className="whitespace-pre-wrap">{finalReportContent}</div>
            </div>
          </FloatingPanel>
        )}
      </div>
    </div>
  );
};

export default SynthesisLab;
