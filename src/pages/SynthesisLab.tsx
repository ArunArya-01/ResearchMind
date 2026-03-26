import { useState, useMemo, useCallback, useEffect } from "react";
import { motion } from "framer-motion";
import FloatingPanel from "../components/FloatingPanel";
import ParallaxContainer from "../components/ParallaxContainer";
import { Rocket, ShieldAlert, FileText, Play, Loader2 } from "lucide-react";

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

const visionaryMessages = [
  { time: "T+0.00s", msg: "Initializing visionary analysis..." },
  { time: "T+1.23s", msg: "Hypothesis: Quantum coherence may extend beyond photosynthetic systems to neural microtubules." },
  { time: "T+3.45s", msg: "Cross-referencing 142 papers on biological quantum effects..." },
  { time: "T+5.67s", msg: "INSIGHT: 3 papers from 2023 suggest room-temperature coherence in protein scaffolds." },
  { time: "T+7.89s", msg: "Proposing novel pathway: Quantum → Neural → Consciousness bridge." },
  { time: "T+9.12s", msg: "Confidence: HIGH. Supporting evidence from 12 independent labs." },
];

const skepticMessages = [
  { time: "T+0.50s", msg: "Running adversarial checks..." },
  { time: "T+2.34s", msg: "WARNING: Decoherence timescales in warm biology are 10^-13s. Too short for neural effects." },
  { time: "T+4.56s", msg: "Counter-evidence: Tegmark (2000) showed thermal noise destroys coherence." },
  { time: "T+6.78s", msg: "CHALLENGE: 8 of 12 cited labs used cryo conditions. Not applicable in vivo." },
  { time: "T+8.90s", msg: "Replication crisis: Only 2 studies independently replicated." },
  { time: "T+10.1s", msg: "Verdict: INSUFFICIENT EVIDENCE. Need room-temp replication." },
];

const manuscriptLines = [
  "SYNTHESIS REPORT",
  "═══════════════════════════════════",
  "",
  "Title: Quantum Coherence in Biological Systems:",
  "       A Critical Assessment of Current Evidence",
  "",
  "Authors: ResearchMind Synthesis Engine v2.4",
  "Date: March 2026",
  "",
  "ABSTRACT",
  "───────────────────────────────────",
  "This synthesis examines the evidence for quantum",
  "coherence in biological systems, with particular",
  "focus on photosynthetic complexes and proposed",
  "extensions to neural architectures. Through analysis",
  "of 142 papers and adversarial debate, we identify",
  "a critical discovery gap in room-temperature",
  "replication studies.",
  "",
  "KEY FINDINGS",
  "───────────────────────────────────",
  "1. Strong evidence for quantum effects in",
  "   photosynthesis at cryogenic temperatures",
  "2. Limited evidence at biological temperatures",
  "3. Discovery gap identified: need for in-vivo",
  "   room-temperature coherence measurements",
  "",
  "CONFIDENCE: MODERATE (67.3%)",
  "NOVELTY SCORE: HIGH (89.1%)",
];

const SynthesisLab = () => {
  const [zoomedIn, setZoomedIn] = useState(false);
  const [nodes, setNodes] = useState<{ id: number; x: number; y: number; size: number; connections: number[] }[] | null>(null);
  const [visionaryLogs, setVisionaryLogs] = useState<{ time: string; msg: string }[]>([]);
  const [skepticLogs, setSkepticLogs] = useState<{ time: string; msg: string }[]>([]);

  useEffect(() => {
    fetch(`http://${window.location.hostname}:8000/nodes`)
      .then(res => res.json())
      .then(data => setNodes(data))
      .catch(console.error);
  }, []);

  const handleStartDiscovery = useCallback(() => {
    setZoomedIn(true);
    setTimeout(() => setZoomedIn(false), 4000);

    const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws/swarm`);
    ws.onopen = () => {
      ws.send(JSON.stringify({
        command: "start",
        topic: "Quantum Coherence in Biological Systems",
        gap_data: { red_anomalies: [] }
      }));
    };
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const logEntry = {
          time: `T+${(performance.now() / 1000).toFixed(2)}s`,
          msg: data.message
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
  }, []);

  return (
    <div className="min-h-screen pt-24 px-6 pb-12">
      <ParallaxContainer intensity={2}>
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 text-center"
          >
            <h1 className="text-bone font-display text-5xl font-bold tracking-tight mb-3">
              Synthesis <span className="text-crimson">Lab</span>
            </h1>
            <p className="text-bone/40 font-mono text-sm mb-6">
              Knowledge graph · Swarm debate · Final manuscript
            </p>
            <motion.button
              onClick={handleStartDiscovery}
              whileHover={{ scale: 1.03, boxShadow: "0 0 30px hsl(354 96% 43% / 0.5)" }}
              whileTap={{ scale: 0.97 }}
              className="px-6 py-3 rounded-xl bg-crimson text-white font-display font-semibold text-sm flex items-center gap-2 mx-auto transition-shadow"
            >
              <Play className="w-4 h-4" />
              Start Discovery
            </motion.button>
          </motion.div>

          {/* Knowledge Graph */}
          <FloatingPanel z={50} className="mb-8 overflow-hidden" dark delay={0.1}>
            <div className="p-4 border-b border-border flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-bone animate-pulse" />
              <span className="text-bone font-mono text-xs">Knowledge Graph · {nodes?.length ?? 0} nodes</span>
            </div>
            <motion.div
              animate={zoomedIn ? { scale: 2.5, x: -200, y: -100 } : { scale: 1, x: 0, y: 0 }}
              transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
              className="relative min-h-[400px]"
            >
              {!nodes ? (
                <div className="flex flex-col items-center justify-center h-[400px] text-bone/50">
                  <Loader2 className="w-8 h-8 animate-spin mb-4" />
                  <span className="font-mono text-sm">Initializing Knowledge Graph...</span>
                </div>
              ) : (
                <svg width="100%" viewBox="0 0 800 600" className="h-[400px]">
                  {/* Connections - ultra-thin white */}
                  {nodes?.map((node) =>
                    node?.connections?.map((target, ci) => (
                      <line
                        key={`${node.id}-${ci}`}
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

                {/* Nodes - bright white */}
                {nodes?.map((node) => (
                  <motion.circle
                    key={node.id}
                    cx={node?.x ?? 0}
                    cy={node?.y ?? 0}
                    r={node?.size ?? 0}
                    fill="hsl(0 0% 100% / 0.8)"
                    initial={{ opacity: 0 }}
                    animate={{
                      opacity: [0.4, 0.9, 0.4],
                      cx: (node?.x ?? 0) + (Math.random() - 0.5) * 4,
                      cy: (node?.y ?? 0) + (Math.random() - 0.5) * 4,
                    }}
                    transition={{
                      opacity: { duration: 2 + Math.random() * 3, repeat: Infinity },
                      cx: { duration: 6 + Math.random() * 4, repeat: Infinity, repeatType: "reverse" },
                      cy: { duration: 6 + Math.random() * 4, repeat: Infinity, repeatType: "reverse" },
                    }}
                  />
                ))}

                {/* Discovery Gap - Deep Red Pulsing Orb */}
                <motion.circle
                  cx={400}
                  cy={300}
                  r={22}
                  fill="hsl(0 80% 30%)"
                  animate={{
                    r: [18, 24, 18],
                    opacity: [0.8, 1, 0.8],
                  }}
                  transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                />
                <motion.circle
                  cx={400}
                  cy={300}
                  r={35}
                  fill="none"
                  stroke="hsl(354 96% 43% / 0.4)"
                  strokeWidth={1}
                  animate={{
                    r: [30, 40, 30],
                    opacity: [0.3, 0.7, 0.3],
                  }}
                  transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                />
                <motion.circle
                  cx={400}
                  cy={300}
                  r={50}
                  fill="none"
                  stroke="hsl(354 96% 43% / 0.15)"
                  strokeWidth={0.5}
                  animate={{
                    r: [45, 58, 45],
                    opacity: [0.2, 0.5, 0.2],
                  }}
                  transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
                />
                <text x={400} y={355} textAnchor="middle" fill="hsl(354 96% 60%)" fontSize={9} fontFamily="var(--font-mono)">
                  DISCOVERY GAP
                </text>
              </svg>
              )}
            </motion.div>
          </FloatingPanel>

          {/* Swarm Debate */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Visionary */}
            <FloatingPanel z={40} className="!bg-transparent !border-0 !shadow-none" delay={0.3}>
              <div className="terminal-visionary p-5">
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border">
                  <Rocket className="w-4 h-4 text-sky-blue" />
                  <span className="text-bone font-mono font-bold text-sm">VISIONARY</span>
                  <span className="text-bone/20 font-mono text-xs ml-auto">Agent Alpha</span>
                </div>
                <div className="space-y-3 font-mono text-xs max-h-[250px] overflow-y-auto">
                  {visionaryLogs.map((msg, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 }}
                    >
                      <span className="text-sky-blue/40">{msg.time}</span>
                      <p className={`text-bone/70 mt-0.5 ${msg.msg.startsWith("INSIGHT") ? "text-sky-blue font-semibold" : ""}`}>
                        {msg.msg}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </FloatingPanel>

            {/* Skeptic */}
            <FloatingPanel z={40} className="!bg-transparent !border-0 !shadow-none" delay={0.4}>
              <div className="terminal-skeptic p-5">
                <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border">
                  <ShieldAlert className="w-4 h-4 text-crimson" />
                  <span className="text-bone font-mono font-bold text-sm">SKEPTIC</span>
                  <span className="text-bone/20 font-mono text-xs ml-auto">Agent Beta</span>
                </div>
                <div className="space-y-3 font-mono text-xs max-h-[250px] overflow-y-auto">
                  {skepticLogs.map((msg, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 }}
                    >
                      <span className="text-crimson/40">{msg.time}</span>
                      <p className={`text-bone/70 mt-0.5 ${msg.msg.startsWith("WARNING") || msg.msg.startsWith("CHALLENGE") ? "text-crimson font-semibold" : ""}`}>
                        {msg.msg}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </FloatingPanel>
          </div>

          {/* Final Manuscript */}
          <motion.div
            initial={{ opacity: 0, y: 60 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <FloatingPanel z={60} className="max-w-2xl mx-auto p-10 relative overflow-hidden" delay={0.6}>
              <div className="flex items-center gap-2 mb-6 relative z-10">
                <FileText className="w-5 h-5 text-pure-black/50" />
                <span className="text-pure-black font-display font-semibold text-sm">Final Manuscript</span>
              </div>
              <div className="font-mono text-xs leading-relaxed text-pure-black/70 space-y-0.5 relative z-10">
                {manuscriptLines.map((line, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.03 }}
                    className={`${
                      line === "SYNTHESIS REPORT" ? "text-pure-black font-bold text-lg font-display" : ""
                    } ${line.startsWith("═") || line.startsWith("───") ? "text-border" : ""} ${
                      line.startsWith("KEY") || line.startsWith("ABSTRACT") ? "text-pure-black font-bold mt-2" : ""
                    } ${line.startsWith("CONFIDENCE") || line.startsWith("NOVELTY") ? "text-crimson font-semibold" : ""}`}
                  >
                    {line || <br />}
                  </motion.div>
                ))}
              </div>
            </FloatingPanel>
          </motion.div>
        </div>
      </ParallaxContainer>
    </div>
  );
};

export default SynthesisLab;
