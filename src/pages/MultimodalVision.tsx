import FloatingPanel from "../components/FloatingPanel";
import ParallaxContainer from "../components/ParallaxContainer";
import { ScanLine, ZoomIn, FileText, BarChart3, Image as ImageIcon } from "lucide-react";

const pdfLines = [
  "Abstract: We present a novel framework for multi-modal",
  "analysis of scientific literature using large language",
  "models combined with computer vision techniques...",
  "",
  "1. Introduction",
  "The exponential growth of scientific publications has",
  "created an unprecedented need for automated tools",
  "capable of extracting, synthesizing, and connecting",
  "knowledge across disciplines. Traditional approaches",
  "rely heavily on text-only analysis, missing critical",
  "information embedded in figures, charts, and tables.",
  "",
  "Our approach leverages a multi-modal architecture",
  "that processes both textual and visual elements...",
  "",
  "2. Methodology",
  "We employ a three-stage pipeline:",
  "  2.1 Document Decomposition",
  "  2.2 Visual Element Extraction",
  "  2.3 Cross-Modal Synthesis",
  "",
  "Figure 1: Architecture Overview",
  "[CHART: Model Performance vs Baseline]",
  "",
  "3. Results",
  "Our system achieves 94.2% accuracy on the",
  "SciDoc benchmark, outperforming previous",
  "state-of-the-art by 12.7 percentage points.",
  "",
  "Table 1: Comparative Analysis",
  "| Model      | Accuracy | F1    |",
  "| Baseline   | 81.5%    | 0.79  |",
  "| Ours       | 94.2%    | 0.93  |",
];

const boundingBoxes = [
  { top: "52%", left: "10%", width: "80%", height: "8%", label: "Chart Detected", type: "chart" },
  { top: "72%", left: "10%", width: "70%", height: "12%", label: "Table Detected", type: "table" },
];

const MultimodalVision = () => {
  return (
    <div className="min-h-screen pt-24 px-6 pb-12">
      <ParallaxContainer>
        <div className="max-w-6xl mx-auto">
          <div
            className="mb-10 text-center"
          >
            <h1 className="text-bone font-display text-5xl font-bold tracking-tight mb-3">
              Multimodal <span className="text-crimson">Vision</span>
            </h1>
            <p className="text-bone/40 font-mono text-sm">
              Laser-scanning documents · Extracting visual elements · Building connections
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* PDF Viewer - Center */}
            <div className="lg:col-span-2">
              <FloatingPanel z={50} className="relative overflow-hidden">
                <div className="p-4 border-b border-pure-black/10 flex items-center gap-3 relative z-10">
                  <FileText className="w-4 h-4 text-pure-black/50" />
                  <span className="text-pure-black font-mono text-xs">multi_modal_synthesis_2024.pdf</span>
                  <div className="ml-auto flex items-center gap-2">
                    <ScanLine className="w-4 h-4 text-crimson animate-pulse" />
                    <span className="text-crimson font-mono text-xs">Scanning...</span>
                  </div>
                </div>

                <div className="relative p-6 min-h-[500px] font-mono text-xs leading-relaxed text-pure-black/70">
                  {/* Laser scan line */}
                  <div
                    className="laser-line animate-[scan_4s_linear_infinite]"
                  />

                  {/* PDF Content */}
                  {pdfLines.map((line, i) => (
                    <div
                      key={i}
                      className={`relative z-10 ${
                        line.startsWith("[") ? "text-crimson/70 font-semibold" : ""
                      } ${line.startsWith("|") ? "text-pure-black/50" : ""} ${
                        /^\d\./.test(line) ? "font-semibold text-pure-black mt-2" : ""
                      }`}
                    >
                      {line || <br />}
                    </div>
                  ))}

                  {/* Bounding Boxes */}
                  {boundingBoxes.map((box, i) => (
                    <div
                      key={i}
                      className="absolute border border-crimson/40 rounded-xl cursor-pointer group z-10"
                      style={{
                        top: box.top,
                        left: box.left,
                        width: box.width,
                        height: box.height,
                      }}
                    >
                      <div className="absolute -top-6 left-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {box.type === "chart" ? (
                          <BarChart3 className="w-3 h-3 text-crimson" />
                        ) : (
                          <ImageIcon className="w-3 h-3 text-crimson" />
                        )}
                        <span className="text-crimson font-mono text-[10px]">{box.label}</span>
                      </div>
                      <div className="absolute inset-0 bg-crimson/5 group-hover:bg-crimson/8 rounded-xl transition-colors" />
                    </div>
                  ))}
                </div>
              </FloatingPanel>
            </div>

            {/* Extraction Panel - Right */}
            <div className="space-y-5">
              <FloatingPanel z={40} className="p-5" dark>
                <h3 className="text-bone font-display font-semibold text-sm mb-3 flex items-center gap-2">
                  <ZoomIn className="w-4 h-4 text-crimson" />
                  Extraction Log
                </h3>
                <div className="space-y-2 font-mono text-xs">
                  {[
                    { time: "00:01.2", msg: "Document parsed", status: "ok" },
                    { time: "00:02.8", msg: "Text extracted (34 blocks)", status: "ok" },
                    { time: "00:04.1", msg: "Figure 1 detected", status: "ok" },
                    { time: "00:05.3", msg: "Chart data extracted", status: "ok" },
                    { time: "00:06.7", msg: "Table 1 parsed (2×3)", status: "ok" },
                    { time: "00:08.2", msg: "Cross-references linked", status: "ok" },
                    { time: "00:09.5", msg: "Embedding generated", status: "processing" },
                  ].map((log, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2"
                    >
                      <span className="text-bone/25">{log.time}</span>
                      <span className="text-bone/60">{log.msg}</span>
                      <span className={`ml-auto ${log.status === "ok" ? "text-graph-green" : "text-crimson animate-pulse"}`}>
                        {log.status === "ok" ? "✓" : "⟳"}
                      </span>
                    </div>
                  ))}
                </div>
              </FloatingPanel>

              <FloatingPanel z={35} className="p-5" dark>
                <h3 className="text-bone font-display font-semibold text-sm mb-3">
                  Elements Found
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: "Text Blocks", count: 34 },
                    { label: "Figures", count: 1 },
                    { label: "Tables", count: 1 },
                    { label: "Equations", count: 3 },
                    { label: "References", count: 28 },
                    { label: "Entities", count: 47 },
                  ].map((el) => (
                    <div key={el.label} className="text-center p-2 rounded-xl bg-background/30 border border-border">
                      <p className="text-bone font-display text-lg font-bold">{el.count}</p>
                      <p className="text-bone/30 font-mono text-[10px]">{el.label}</p>
                    </div>
                  ))}
                </div>
              </FloatingPanel>
            </div>
          </div>
        </div>
      </ParallaxContainer>
    </div>
  );
};

export default MultimodalVision;
