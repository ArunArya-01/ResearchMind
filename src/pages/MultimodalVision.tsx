import { useState, useRef, useEffect } from "react";
import FloatingPanel from "../components/FloatingPanel";
import { ScanLine, ZoomIn, FileText, BarChart3, Image as ImageIcon, UploadCloud } from "lucide-react";

const MultimodalVision = () => {
  const [extractedText, setExtractedText] = useState<string>("");
  const [currentBoxes, setCurrentBoxes] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const [visibleLogs, setVisibleLogs] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [extractionLogs, setExtractionLogs] = useState<{ time: string; msg: string }[]>([]);
  const [elementsFound, setElementsFound] = useState<{ label: string; count: number }[]>([
    { label: "Charts", count: 0 },
    { label: "Tables", count: 0 },
    { label: "Graphs", count: 0 },
    { label: "Total Elements", count: 0 },
    { label: "Pages Scanned", count: 0 },
    { label: "References", count: 0 },
  ]);

  useEffect(() => {
    if (isScanning) {
      const interval = setInterval(() => {
        setVisibleLogs((prev) => Math.min(prev + 1, extractionLogs.length));
      }, 1200);
      return () => clearInterval(interval);
    } else {
      setVisibleLogs(0);
    }
  }, [isScanning, extractionLogs.length]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) await uploadFile(droppedFile);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) await uploadFile(selectedFile);
  };

  const uploadFile = async (selectedFile: File) => {
    if (selectedFile.type !== "application/pdf") {
      alert("Please upload a PDF file.");
      return;
    }

    setFile(selectedFile);
    setIsUploading(true);
    setExtractedText(""); // Clear old text right away
    setCurrentBoxes([]); // Clear old bounding boxes

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch("http://localhost:8000/upload/pdf", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        setIsScanning(true);
        localStorage.setItem("pdf_active", "true");
        try {
          const resData = await res.json();
          let parsedArray: any[] = [];
          if (resData.data?.elements && Array.isArray(resData.data.elements)) {
            parsedArray = resData.data.elements;
          } else if (resData.data && Array.isArray(resData.data)) {
            parsedArray = resData.data;
          }
          const documentText = resData.data?.text || "";

          let charts = 0;
          let tables = 0;
          let graphs = 0;
          const newLogs = [
            { time: "00:01.2", msg: `File ${selectedFile.name} parsed` },
            { time: "00:02.8", msg: "Visual elements extracted" }
          ];

          let customKeywords: string[] = [];
          const newBoxes: any[] = [];

          if (Array.isArray(parsedArray)) {
            parsedArray.forEach((item, idx) => {
              if (item.type === "chart") charts++;
              if (item.type === "table") tables++;
              if (item.type === "graph") graphs++;

              if (item.coordinates) {
                newBoxes.push({
                   top: `${item.coordinates.y * 100}%`,
                   left: `${item.coordinates.x * 100}%`,
                   width: `${item.coordinates.width * 100}%`,
                   height: `${item.coordinates.height * 100}%`,
                   label: `${item.type} Detected`,
                   type: item.type
                });
              }

              newLogs.push({ time: `00:0${3 + idx}.1`, msg: `Found ${item.type} on page ${item.page || 1}` });
            });

            const words = parsedArray.map((i: any) => i.description || i.title || "").join(" ").split(" ").filter((w: string) => w && w.length > 3);
            if (words.length > 0) {
              customKeywords = Array.from(new Set(words)).slice(0, 10);
            }
          }

          if (customKeywords.length > 0) {
             localStorage.setItem("pdf_keywords", JSON.stringify(customKeywords));
          } else {
             localStorage.setItem("pdf_keywords", JSON.stringify([]));
          }
          
          localStorage.setItem("pdf_upload_time", Date.now().toString());

          setExtractedText(documentText);
          setCurrentBoxes(newBoxes);

          newLogs.push({ time: `00:10.0`, msg: "Multimodal extraction complete" });
          setExtractionLogs(newLogs);

          setElementsFound([
            { label: "Charts", count: charts },
            { label: "Tables", count: tables },
            { label: "Graphs", count: graphs },
            { label: "Total Elements", count: parsedArray.length || 0 },
            { label: "Pages Scanned", count: parsedArray.length > 0 ? (parsedArray[parsedArray.length - 1].page || 1) : 1 },
            { label: "References", count: 0 },
          ]);

        } catch (e) {
          localStorage.setItem("pdf_keywords", JSON.stringify([]));
          setExtractedText("");
        }
      } else {
        console.error("Upload failed");
        setFile(null);
      }
    } catch (err) {
      console.error("Upload error", err);
      setFile(null);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-obsidian pt-24 px-6 pb-12">
      <div className="max-w-6xl mx-auto">
        <div className="mb-10 text-center">
          <h1 className="text-crimson font-display text-5xl font-bold tracking-tight mb-3">
            Multimodal Vision
          </h1>
          <p className="text-bone/40 font-mono text-sm">
            Laser-scanning documents · Extracting visual elements · Building connections
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* PDF Viewer - Center */}
          <div className="lg:col-span-2">
            <FloatingPanel z={50} className="relative overflow-hidden border border-crimson">
              {!isScanning && !file ? (
                <>
                  <input
                    type="file"
                    accept=".pdf"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <div
                    className={`relative p-12 min-h-[500px] flex flex-col items-center justify-center transition-colors cursor-pointer ${
                      isDragActive ? "bg-crimson/10 border-2 border-dashed border-crimson" : "bg-transparent border-2 border-dashed border-crimson/30 hover:bg-black/5"
                    }`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <UploadCloud className={`w-12 h-12 mb-4 ${isDragActive ? "text-crimson" : "text-crimson/60"}`} />
                    <h3 className="text-pure-black font-display text-xl font-bold mb-2">
                      {isUploading ? "Uploading..." : isDragActive ? "Drop PDF here" : "Upload Manuscript"}
                    </h3>
                    <p className="text-pure-black/60 font-mono text-xs text-center">
                      Drag and drop your PDF here to begin multimodal synthesis.
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="p-4 border-b border-crimson/20 flex items-center gap-3 relative z-10">
                    <FileText className="w-4 h-4 text-pure-black/50" />
                    <span className="text-pure-black font-mono text-xs">{file?.name || "multi_modal_synthesis_2024.pdf"}</span>
                    <div className="ml-auto flex items-center gap-2">
                      <ScanLine className={`w-4 h-4 text-crimson ${isScanning ? "animate-pulse" : ""}`} />
                      <span className="text-crimson font-mono text-xs">{isScanning ? "Scanning..." : "Processing..."}</span>
                    </div>
                  </div>

                  <div className="relative p-6 min-h-[500px] font-mono text-xs leading-relaxed text-pure-black/70">
                    {/* Laser scan line */}
                    {isScanning && (
                      <div className="laser-line animate-[scan_4s_linear_infinite]" />
                    )}

                    {/* PDF Content */}
                    {!extractedText && !isScanning ? (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-crimson/50 font-mono text-sm tracking-wider">No Data Ingested</span>
                      </div>
                    ) : (
                      <div className="relative z-10 whitespace-pre-wrap">
                        {extractedText}
                      </div>
                    )}

                    {/* Bounding Boxes */}
                    {currentBoxes.map((box, i) => (
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
                        <div className="absolute -top-6 left-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap bg-obsidian border border-crimson/30 px-2 py-1 rounded">
                          {box.type === "chart" || box.type === "table" ? (
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
                </>
              )}
            </FloatingPanel>
          </div>

          {/* Extraction Panel - Right */}
          <div className="space-y-5">
            <FloatingPanel z={40} className="p-5 border border-crimson">
              <h3 className="text-pure-black font-display font-semibold text-sm mb-3 flex items-center gap-2">
                <ZoomIn className="w-4 h-4 text-crimson" />
                Extraction Log
              </h3>
              <div className="space-y-2 font-mono text-xs">
                {extractionLogs.length === 0 ? (
                  <div className="text-crimson/50 text-center py-4">No Data Ingested</div>
                ) : (
                  extractionLogs.map((log, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2"
                    >
                      <span className="text-pure-black/50">{log.time}</span>
                      <span className="text-pure-black/80">{log.msg}</span>
                      <span className={`ml-auto ${i < visibleLogs ? "text-graph-green font-bold" : "text-crimson animate-pulse"}`}>
                        {i < visibleLogs ? "✓" : "⟳"}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </FloatingPanel>

            <FloatingPanel z={35} className="p-5 border border-crimson">
              <h3 className="text-pure-black font-display font-semibold text-sm mb-3">
                Elements Found
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {elementsFound.map((el) => (
                  <div key={el.label} className="text-center p-2 rounded-xl bg-background/5 border border-crimson/30">
                    <p className="text-pure-black font-display text-lg font-bold">{el.count}</p>
                    <p className="text-pure-black/50 font-mono text-[10px]">{el.label}</p>
                  </div>
                ))}
              </div>
            </FloatingPanel>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MultimodalVision;
