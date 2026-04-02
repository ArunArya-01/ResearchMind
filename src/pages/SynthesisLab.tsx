import { useState, useMemo, useCallback, useEffect, useRef } from "react";
import FloatingPanel from "../components/FloatingPanel";
import { Rocket, ShieldAlert, FileText, Play, Loader2, RefreshCw, Terminal } from "lucide-react";
import { motion } from "framer-motion";

const resolveApiBaseCandidates = () => {
  const envBase = import.meta.env.VITE_API_BASE_URL as string | undefined;
  const storedBase =
    typeof window !== "undefined" ? window.localStorage.getItem("active_api_base") : null;
  const fallback8001 = `http://${window.location.hostname}:8001`;
  const fallback8000 = `http://${window.location.hostname}:8000`;
  return Array.from(new Set([envBase, storedBase, fallback8001, fallback8000].filter(Boolean) as string[]));
};

const toWsBase = (httpBase: string) => httpBase.replace(/^http/i, "ws");

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
  const [directorLogs, setDirectorLogs] = useState<{ time: string; msg: string }[]>([]);
  const [directorInput, setDirectorInput] = useState("");
  const [finalReportContent, setFinalReportContent] = useState<string | null>(null);
  const [gammaScore, setGammaScore] = useState<number | null>(null);
  const [hasActiveScan, setHasActiveScan] = useState(false);
  const [isDebating, setIsDebating] = useState(false);
  const [pdfKeywords, setPdfKeywords] = useState<string[]>([]);
  const [pdfDocs, setPdfDocs] = useState<Record<string, string[]>>({});
  const [pdfImages, setPdfImages] = useState<any[]>([]);
  const [conflictingKeywords, setConflictingKeywords] = useState<string[]>([]);
  const [hoveredNode, setHoveredNode] = useState<{keyword: string, imgPath: string} | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const lastUploadTimeRef = useRef<string | null>(null);
  
  useEffect(() => {
    try {
      const activeStr = localStorage.getItem("active_keywords");
      if (activeStr) {
        const parsed = JSON.parse(activeStr);
        if (parsed && parsed.length > 0) {
          setPdfKeywords(parsed);
          setHasActiveScan(true);
        }
      }
      const activeDocsStr = localStorage.getItem("active_docs");
      if (activeDocsStr) {
        setPdfDocs(JSON.parse(activeDocsStr));
      }
      const activeImagesStr = localStorage.getItem("active_images");
      if (activeImagesStr) {
        setPdfImages(JSON.parse(activeImagesStr));
      }
      const currentUploadTime = localStorage.getItem("pdf_upload_time");
      if (currentUploadTime) {
        lastUploadTimeRef.current = currentUploadTime;
      }
    } catch (e) {
      console.error(e);
    }
  }, []);

  const visionaryEndRef = useRef<HTMLDivElement>(null);
  const skepticEndRef = useRef<HTMLDivElement>(null);
  const directorEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (visionaryLogs.length > 1) {
      visionaryEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [visionaryLogs]);

  useEffect(() => {
    if (skepticLogs.length > 1) {
      skepticEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [skepticLogs]);

  useEffect(() => {
    directorEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [directorLogs]);

  const handleDirectorSubmit = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && directorInput.trim() && socketRef.current) {
        socketRef.current.send(JSON.stringify({ type: 'director_override', command: directorInput }));
        setDirectorLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), msg: `OVERRIDE: ${directorInput}` }]);
        setDirectorInput("");
    }
  };

  const fetchNodes = useCallback(async () => {
    setNodes(null);
    for (const base of resolveApiBaseCandidates()) {
      try {
        const res = await fetch(`${base}/nodes`);
        if (!res.ok) {
          continue;
        }
        localStorage.setItem("active_api_base", base);
        const data = await res.json();
        if (Array.isArray(data)) {
          setNodes(data);
        } else {
          setNodes(data.nodes || []);
        }
        return;
      } catch (_e) {
        // Try next base candidate.
      }
    }
    console.error("Backend nodes error: unable to reach any API base");
    setNodes([]);
  }, []);

  useEffect(() => {
    const checkStorage = () => {
      const currentUploadTime = localStorage.getItem("pdf_upload_time");
      if (currentUploadTime && currentUploadTime !== lastUploadTimeRef.current) {
         // Only reset when a *new* upload arrives after initial hydration.
         if (lastUploadTimeRef.current !== null) {
           setVisionaryLogs([{ time: "T+0.00s", msg: "System Ready" }]);
           setSkepticLogs([{ time: "T+0.00s", msg: "System Ready" }]);
           setIsDebating(false);
           setFinalReportContent(null);
         }
         lastUploadTimeRef.current = currentUploadTime;
      }

      try {
        const activeStr = localStorage.getItem("active_keywords");
        if (activeStr) {
          const parsed = JSON.parse(activeStr);
          if (parsed && parsed.length > 0) {
            setPdfKeywords(parsed);
            setHasActiveScan(true);
          } else {
            setPdfKeywords([]);
            setHasActiveScan(false);
          }
        }
        const activeDocsStr = localStorage.getItem("active_docs");
        if (activeDocsStr) {
          setPdfDocs(JSON.parse(activeDocsStr));
        }
        const activeImagesStr = localStorage.getItem("active_images");
        if (activeImagesStr) {
          setPdfImages(JSON.parse(activeImagesStr));
        }
      } catch (e) {
        setPdfKeywords([]);
        setHasActiveScan(false);
      }
    };

    checkStorage();
    const interval = setInterval(checkStorage, 500);

    fetchNodes();

    return () => clearInterval(interval);
  }, [fetchNodes]);

  const handleStartDiscovery = useCallback(() => {
    if (!hasActiveScan) {
      alert("Please upload a manuscript first.");
      return;
    }

    setZoomedIn(true);
    setTimeout(() => setZoomedIn(false), 4000);

    setIsDebating(true);
    setVisionaryLogs([{ time: "T+0.00s", msg: "Analyzing..." }]);
    setSkepticLogs([{ time: "T+0.00s", msg: "Analyzing..." }]);
    setFinalReportContent(null);
    setGammaScore(null);
    setConflictingKeywords([]);

    const startPayload = JSON.stringify({
      type: "start",
      topic: "Aircraft Engine RUL"
    });

    const wsBases = resolveApiBaseCandidates().map(toWsBase);
    const tried = new Set<string>();

    const connectWs = (index: number) => {
      const wsBase = wsBases[index];
      if (!wsBase || tried.has(wsBase)) {
        setIsDebating(false);
        setVisionaryLogs(prev => [...prev, { time: `T+${(performance.now() / 1000).toFixed(2)}s`, msg: "[SYSTEM] Unable to connect to swarm backend." }]);
        setSkepticLogs(prev => [...prev, { time: `T+${(performance.now() / 1000).toFixed(2)}s`, msg: "[SYSTEM] Unable to connect to swarm backend." }]);
        return;
      }
      tried.add(wsBase);

      const ws = new WebSocket(`${wsBase}/ws/swarm`);
      socketRef.current = ws;
      let opened = false;

      ws.onopen = () => {
        opened = true;
        localStorage.setItem("active_api_base", wsBase.replace(/^ws/i, "http"));
        console.log("WebSocket connection opened");
        ws.send(startPayload);
      };

      ws.onmessage = (event) => {
      console.log("WebSocket message received:", event.data);
      try {
        const data = JSON.parse(event.data);
        console.log("Parsed WebSocket data:", data);
        if (data.type === 'final_report') {
          const rawScore = data.gamma_score ?? 0;
          setFinalReportContent(data.content || data.message);
          setGammaScore(rawScore);
          
          try {
              const currentFileName = localStorage.getItem("pdf_title") || "Untitled Research";
              const saved = JSON.parse(localStorage.getItem('processedPapers') || '[]');
              saved.push({ id: Date.now(), title: currentFileName, score: rawScore, date: new Date().toLocaleDateString(), status: 'Analyzed' });
              localStorage.setItem('processedPapers', JSON.stringify(saved));
          } catch(e) {}
          
          setIsDebating(false);
          return;
        }
        const logEntry = {
          time: `T+${(performance.now() / 1000).toFixed(2)}s`,
          msg: data.message || data.content || ""
        };
        if (data.agent === "Visionary") {
          setVisionaryLogs(prev => [...prev, logEntry]);
        } else if (data.agent === "Skeptic") {
          const msgUpper = (data.message || data.content || "").toUpperCase();
          if (msgUpper.includes("CONTRADICT") || msgUpper.includes("CONFLICT") || msgUpper.includes("WEAKNESS") || msgUpper.includes("SAFETY")) {
             pdfKeywords.forEach(kw => {
                if (msgUpper.includes(kw.toUpperCase())) {
                   setConflictingKeywords(prev => Array.from(new Set([...prev, kw])));
                }
             });
          }
          setSkepticLogs(prev => [...prev, logEntry]);
        } else if (data.agent === "System" && logEntry.msg) {
          setVisionaryLogs(prev => [...prev, { ...logEntry, msg: `[SYSTEM] ${logEntry.msg}` }]);
          setSkepticLogs(prev => [...prev, { ...logEntry, msg: `[SYSTEM] ${logEntry.msg}` }]);
          if (logEntry.msg.toLowerCase().includes("please upload a file first")) {
            setIsDebating(false);
          }
        }
      } catch (e) {
        console.error("WebSocket message parse error", e);
      }
      };
      
      ws.onclose = (event) => {
        console.log("WebSocket connection closed", event);
        if (!opened) {
          connectWs(index + 1);
          return;
        }
        if (!finalReportContent) {
          setIsDebating(false);
        }
      };
      
      ws.onerror = (error) => {
        console.log("WebSocket error", error);
        if (!opened) {
          ws.close();
        }
      };
    };

    connectWs(0);

    }, [hasActiveScan, pdfKeywords, finalReportContent]);

  const getGammaColor = (score: number) => {
    if (score > 7.5) return "text-red-500 stroke-red-500";
    if (score > 4.0) return "text-yellow-400 stroke-yellow-400";
    return "text-cyan-400 stroke-cyan-400";
  };

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
            disabled={!hasActiveScan}
            className={`px-6 py-3 rounded-xl font-display font-semibold text-sm flex items-center gap-2 mx-auto transition-all duration-300 ${hasActiveScan ? "bg-crimson text-white shadow-[0_0_15px_hsl(354_96%_43%_/_0.4)] hover:shadow-[0_0_30px_hsl(354_96%_43%_/_0.8)] hover:-translate-y-0.5" : "bg-obsidian border border-crimson/30 text-crimson/50 cursor-not-allowed"}`}
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
          <div className="relative min-h-[400px] bg-obsidian overflow-hidden" onPointerMove={(e) => setMousePos({ x: e.clientX, y: e.clientY })}>

            {!nodes ? (
              <div className="flex flex-col items-center justify-center h-[400px] text-bone/50">
                <Loader2 className="w-8 h-8 animate-spin mb-4 text-crimson" />
                <span className="font-mono text-sm">Initializing Knowledge Graph...</span>
              </div>
            ) : (
              <svg width="100%" viewBox="0 0 800 600" className="h-[400px]">
                {/* Connections - ultra-thin white */}
                {nodes?.map((node, i) =>
                  node?.connections?.map((target, ci) => {
                    const isNodeConflicting = hasActiveScan && i < 10 && i < pdfKeywords.length && conflictingKeywords.includes(pdfKeywords[i]);
                    const isTargetConflicting = hasActiveScan && target < 10 && target < pdfKeywords.length && conflictingKeywords.includes(pdfKeywords[target]);
                    const isConflictLine = isNodeConflicting || isTargetConflicting;
                    
                    return (
                    <motion.line
                      key={`${node.id}-${ci}`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: pdfKeywords.length > 0 ? 1 : 0 }}
                      transition={{ duration: 1, delay: 1.5 }}
                      x1={node?.x ?? 0}
                      y1={node?.y ?? 0}
                      x2={nodes[target]?.x ?? 0}
                      y2={nodes[target]?.y ?? 0}
                      stroke={isConflictLine ? "hsl(354 96% 43% / 0.9)" : (hasActiveScan ? "hsl(354 96% 43% / 0.2)" : "hsl(0 0% 100% / 0.08)")}
                      strokeWidth={isConflictLine ? 3 : (hasActiveScan ? 1 : 0.5)}
                      className={isConflictLine ? "animate-[pulse_1s_ease-in-out_infinite] drop-shadow-[0_0_5px_rgba(217,4,41,0.8)]" : (hasActiveScan ? "animate-[pulse_2s_ease-in-out_infinite] drop-shadow-[0_0_2px_rgba(217,4,41,0.5)]" : "")}
                    />
                    );
                  })
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
              <g>
                <circle cx={400} cy={300} r={20} fill="hsl(354 96% 43% / 0.8)" className="animate-[pulse_2s_ease-in-out_infinite] drop-shadow-[0_0_15px_rgba(217,4,41,0.9)]" />
                <text x={400} y={345} textAnchor="middle" className="fill-crimson/50 font-mono text-xs tracking-widest animate-pulse font-bold transition-all duration-500">
                  {isDebating ? "SWARM DEBATE IN PROGRESS" : (hasActiveScan ? "" : "AWAITING DATA INPUT")}
                </text>
              </g>

              {/* Nodes - dynamic */}
              {nodes?.map((node, i) => {
                const isKeywordNode = hasActiveScan && i < 10 && i < pdfKeywords.length;
                const keywordText = isKeywordNode ? pdfKeywords[i] : null;
                const targetR = isKeywordNode ? (node.size * 2) : node.size;
                
                let nodeFill = "hsl(0 0% 100% / 0.8)";
                let nodeClass = "";
                
                if (isKeywordNode && keywordText) {
                    const docKeys = Object.keys(pdfDocs);
                    const inDocs = docKeys.filter(d => pdfDocs[d].includes(keywordText));
                    
                    const isConflicting = inDocs.length > 1 && conflictingKeywords.includes(keywordText);
                    
                    if (isConflicting) {
                        nodeFill = "hsl(300 100% 50% / 0.9)"; // Magenta
                        nodeClass = "animate-[pulse_1s_ease-in-out_infinite] drop-shadow-[0_0_15px_rgba(255,0,255,1)]";
                    } else if (inDocs.length > 0) {
                        const primaryDocIndex = docKeys.indexOf(inDocs[0]);
                        if (primaryDocIndex === 0) {
                            nodeFill = "hsl(180 100% 50% / 0.8)"; // Cyan
                            nodeClass = "drop-shadow-[0_0_12px_rgba(0,255,255,0.8)]";
                        } else {
                            nodeFill = "hsl(30 100% 50% / 0.8)"; // Orange
                            nodeClass = "drop-shadow-[0_0_12px_rgba(255,165,0,0.8)]";
                        }
                    } else {
                        nodeClass = "drop-shadow-[0_0_12px_rgba(217,4,41,1)]";
                    }
                } else if (hasActiveScan) {
                    nodeClass = "animate-[pulse_3s_ease-in-out_infinite] drop-shadow-[0_0_8px_rgba(217,4,41,0.8)]";
                } else {
                    nodeClass = "drop-shadow-[0_0_5px_rgba(253,253,253,0.8)]";
                }
                
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
                      fill={nodeFill}
                      style={{ cursor: 'pointer', pointerEvents: 'auto' }}
                      className={`cursor-pointer overflow-visible hover:fill-bone/50 ${nodeClass}`}
                      onMouseEnter={(e: any) => {
                        const target = e.target as SVGCircleElement;
                        target.setAttribute("r", (targetR * 1.5).toString());
                        
                        if (isKeywordNode && keywordText) {
                           const matchedImg = pdfImages.find(img => img.keyword === keywordText);
                           if (matchedImg) {
                               setHoveredNode({
                                  keyword: keywordText,
                                  imgPath: matchedImg.citation_img
                               });
                           }
                        }
                      }}
                      onMouseLeave={(e: any) => {
                        const target = e.target as SVGCircleElement;
                        target.setAttribute("r", targetR.toString());
                        setHoveredNode(null);
                      }}
                      onClick={() => {
                        if (keywordText) {
                          localStorage.setItem("highlight_keyword", keywordText);
                          window.dispatchEvent(new Event("storage"));
                        }
                      }}
                    />
                    {isKeywordNode && pdfKeywords.length > 0 && (
                      <motion.text
                        initial={{ opacity: 0, x: 400, y: 300 }}
                        animate={{ 
                          opacity: 1, 
                          x: [400, 400 + (node.x - 400) * 1.2 + targetR + 5, node.x + targetR + 6], 
                          y: [300, 300 + (node.y - 300) * 1.2 + 3, node.y + 3] 
                        }}
                        transition={{ 
                          duration: 2,
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
                <div className="w-2 h-2 rounded-full bg-crimson animate-pulse shadow-[0_0_8px_rgba(217,4,41,0.8)]" />
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
                      <span className="text-red-400/80">{msg.time}</span>
                      <p className={`text-bone mt-0.5 ${msg.msg.startsWith("WARNING") || msg.msg.startsWith("CHALLENGE") ? "text-red-500 font-bold" : ""}`}>
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

        {/* DIRECTOR TERMINAL */}
        <FloatingPanel z={40} className="w-full mb-8 !bg-transparent !border-0 !shadow-none">
          <div className="p-5 bg-obsidian border border-bone/20 rounded-xl shadow-[0_8px_40px_-8px_hsl(0_0%_0%_/_0.8)] backdrop-blur transition-colors focus-within:border-green-400">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-bone/20">
              <Terminal className="w-4 h-4 text-green-400" />
              <span className="text-bone font-mono font-bold text-sm">DIRECTOR TERMINAL</span>
              <span className="text-bone/40 font-mono text-xs ml-auto">Human in the Loop</span>
            </div>
            <div className="space-y-3 font-mono text-xs max-h-[150px] overflow-y-auto mb-4">
              {directorLogs.length === 0 ? (
                <div className="text-bone/30 text-center py-4">Awaiting Override Directives</div>
              ) : (
                directorLogs.map((msg, i) => (
                  <div key={i}>
                    <span className="text-green-500/80">{msg.time}</span>
                    <p className="text-green-400 mt-0.5 font-bold">
                      {msg.msg}
                    </p>
                  </div>
                ))
              )}
              <div ref={directorEndRef} />
            </div>
            <input 
              type="text" 
              value={directorInput}
              onChange={(e) => setDirectorInput(e.target.value)}
              onKeyDown={handleDirectorSubmit}
              placeholder="> Inject real-time system directive... (Press Enter)"
              className="w-full bg-pure-black border border-green-500/30 text-green-400 font-mono text-xs p-2.5 rounded focus:outline-none focus:border-green-400 transition-colors placeholder:text-green-900/50"
            />
          </div>
        </FloatingPanel>

        {/* Final Manuscript */}
        {finalReportContent && (
          <FloatingPanel z={60} className="max-w-2xl mx-auto p-10 relative overflow-hidden border border-crimson min-h-[400px] overflow-y-auto max-h-[600px]">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8 relative z-10 border-b border-crimson/20 pb-6">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-pure-black/50" />
                <span className="text-pure-black font-display font-semibold text-xl">Final Manuscript</span>
              </div>
              
              {gammaScore !== null && (
                <div className="flex items-center gap-4 bg-obsidian p-3 rounded-xl border border-bone/20 shadow-lg shrink-0">
                   <div className="relative w-16 h-16">
                       <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                           <circle cx="50" cy="50" r="40" className="stroke-bone/10" strokeWidth="8" fill="none" />
                           <motion.circle 
                               cx="50" cy="50" r="40" 
                               className={getGammaColor(gammaScore)} 
                               strokeWidth="8" fill="none" strokeLinecap="round"
                               initial={{ strokeDasharray: "251 251", strokeDashoffset: 251 }}
                               animate={{ strokeDashoffset: 251 - (251 * Math.min(gammaScore, 10)) / 10 }}
                               transition={{ duration: 1.5, ease: "easeOut" }}
                           />
                       </svg>
                       <div className="absolute inset-0 flex items-center justify-center flex-col">
                           <span className={`text-sm font-bold font-mono ${getGammaColor(gammaScore).split(' ')[0]}`}>{gammaScore.toFixed(1)}</span>
                       </div>
                   </div>
                   <div>
                       <p className="text-bone/50 font-mono text-[10px] tracking-wider uppercase mb-1">Criticality Index</p>
                       <p className={`font-display font-bold text-sm tracking-wide ${getGammaColor(gammaScore).split(' ')[0]}`}>
                           {gammaScore > 7.5 ? "SEVERE RISK" : gammaScore > 4.0 ? "ELEVATED" : "NOMINAL"}
                       </p>
                   </div>
                </div>
              )}
            </div>
            
            <div className="font-mono text-xs leading-relaxed text-pure-black/70 space-y-0.5 relative z-10">
              <div className="whitespace-pre-wrap">{finalReportContent}</div>
            </div>
          </FloatingPanel>
        )}
      </div>

      {/* Root Level Hover Tooltip */}
      {hoveredNode && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          style={{ position: 'fixed', top: mousePos.y + 15, left: mousePos.x + 15, zIndex: 999999, pointerEvents: 'none' }}
          className="w-72 bg-pure-black/95 backdrop-blur-xl border border-bone/30 p-3 shadow-[0_4px_30px_rgba(0,0,0,1)]"
        >
          <div className="flex items-center gap-2 mb-2 pb-2 border-b border-bone/10">
            <div className="w-1.5 h-1.5 rounded-full bg-bone animate-pulse" />
            <span className="text-bone font-mono text-[10px] uppercase tracking-wider">Multimodal Extraction: {hoveredNode.keyword}</span>
          </div>
          <div className="border border-bone/20 bg-pure-black overflow-hidden relative flex items-center justify-center p-2 mt-2 rounded-md" style={{aspectRatio: '4/3'}}>
             <img src={`${(localStorage.getItem("active_api_base") || resolveApiBaseCandidates()[0])}${hoveredNode.imgPath}`} alt={hoveredNode.keyword} style={{maxWidth: '250px'}} className="w-full h-full object-contain filter contrast-125" />
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default SynthesisLab;
