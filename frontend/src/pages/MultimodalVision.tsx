import { useState, useRef, useEffect } from "react";
import FloatingPanel from "../components/FloatingPanel";
import { ScanLine, ZoomIn, FileText, BarChart3, Image as ImageIcon, UploadCloud, CheckCircle, Trash2 } from "lucide-react";

const STORED_API_BASE_URL =
  typeof window !== "undefined" ? window.localStorage.getItem("active_api_base") : null;
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? STORED_API_BASE_URL ?? `http://${window.location.hostname}:8001`;
const API_FALLBACK_URL = `http://${window.location.hostname}:8000`;
const API_BASE_CANDIDATES = Array.from(new Set([API_BASE_URL, API_FALLBACK_URL]));

const postWithFallback = async (path: string, init?: RequestInit) => {
  let lastNetworkError: unknown = null;
  let lastResponse: Response | null = null;

  for (const baseUrl of API_BASE_CANDIDATES) {
    try {
      const response = await fetch(`${baseUrl}${path}`, init);
      if (response.ok) {
        return { response, baseUrl };
      }
      lastResponse = response;
    } catch (error) {
      lastNetworkError = error;
    }
  }

  if (lastResponse) {
    return { response: lastResponse, baseUrl: API_BASE_CANDIDATES[0] };
  }
  throw lastNetworkError ?? new Error("All API candidates failed");
};

interface BoundingBox {
  top: number;
  left: number;
  width: number;
  height: number;
  type: string;
  label: string;
}

const MultimodalVision = () => {
  const [extractedText, setExtractedText] = useState<string>("");
  const [currentBoxes, setCurrentBoxes] = useState<BoundingBox[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const [visibleLogs, setVisibleLogs] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const csvInputRef = useRef<HTMLInputElement>(null);
  const [highlightWord, setHighlightWord] = useState<string>("");
  const [isPdfUploaded, setIsPdfUploaded] = useState(false);
  const [isCsvUploaded, setIsCsvUploaded] = useState(false);

  useEffect(() => {
    const handleStorage = () => {
      const hw = localStorage.getItem("highlight_keyword") || "";
      setHighlightWord(hw);
    };
    window.addEventListener("storage", handleStorage);
    const interval = setInterval(handleStorage, 1000);
    return () => {
      window.removeEventListener("storage", handleStorage);
      clearInterval(interval);
    };
  }, []);

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
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length > 0) await uploadFiles(droppedFiles);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await uploadFiles(Array.from(e.target.files));
    }
  };

  const handleCsvSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const validFiles = Array.from(e.target.files).filter(f => f.name.toLowerCase().endsWith(".csv"));
      if (validFiles.length === 0) {
        alert("Please upload CSV files.");
        return;
      }
      setIsUploading(true);
      const formData = new FormData();
      validFiles.forEach(file => formData.append("files", file));
      try {
        const { response: res } = await postWithFallback("/upload-dataset", {
          method: "POST",
          body: formData,
        });
        if (res.ok) {
          const resData = await res.json();
          localStorage.setItem("dataset_summary", resData.summary || "");
          localStorage.setItem("hasActiveScan", "true");
          setIsCsvUploaded(true);
        } else {
          alert("Failed to process CSV dataset.");
        }
      } catch(err) {
        console.error(err);
        alert("Upload error for CSV.");
      } finally {
        setIsUploading(false);
      }
    }
  };

  const uploadFiles = async (selectedFiles: File[]) => {
    const validFiles = selectedFiles.filter((f) => {
      const isPdfMime = f.type === "application/pdf";
      const isPdfExtension = f.name.toLowerCase().endsWith(".pdf");
      return isPdfMime || isPdfExtension;
    });
    if (validFiles.length === 0) {
      alert("Please upload PDF files.");
      return;
    }

    setFiles(validFiles);
    setIsUploading(true);
    setExtractedText(""); 
    setCurrentBoxes([]); 
    localStorage.setItem("hasActiveScan", "false");
    localStorage.setItem("active_keywords", JSON.stringify([]));
    localStorage.setItem("active_docs", JSON.stringify({}));
    localStorage.setItem("active_images", JSON.stringify([]));
    postWithFallback("/reset", { method: "POST" }).catch(() => console.log("Memory flush skipped"));

    const formData = new FormData();
    validFiles.forEach(file => formData.append("files", file));

    try {
      const { response: res, baseUrl } = await postWithFallback("/upload/pdf", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        localStorage.setItem("active_api_base", baseUrl);
        setIsScanning(true);
        localStorage.setItem("hasActiveScan", "true");
        try {
          const resData = await res.json();
          const documentText = resData.data?.text || "";
          const elementsInfo = resData.data?.elements || { pages: 0, references: 0 };
          const backendKeywords = resData.data?.keywords || [];
          const backendDocs = resData.data?.docs || {};
          const backendImages = resData.data?.images || [];

          const newLogs = [
            { time: "00:01.2", msg: `Files [${validFiles.map(f=>f.name).join(", ")}] parsed` },
            { time: "00:02.8", msg: "Text structure extracted via PyMuPDF" },
            { time: "00:03.5", msg: "Semantic Fusion: Vectorizing chunks in ChromaDB..." }
          ];

          if (backendKeywords.length > 0) {
             localStorage.setItem("active_keywords", JSON.stringify(backendKeywords));
             localStorage.setItem("active_docs", JSON.stringify(backendDocs));
             localStorage.setItem("active_images", JSON.stringify(backendImages));
          } else {
             localStorage.setItem("active_keywords", JSON.stringify([]));
             localStorage.setItem("active_docs", JSON.stringify({}));
             localStorage.setItem("active_images", JSON.stringify([]));
          }
          
          localStorage.setItem("pdf_upload_time", Date.now().toString());
          if (validFiles.length > 0) {
             localStorage.setItem("pdf_title", validFiles[0].name);
          }

          setExtractedText(documentText);
          setCurrentBoxes([]);

          newLogs.push({ time: `00:05.1`, msg: `Found ${elementsInfo.pages} pages and ${elementsInfo.references} references` });
          newLogs.push({ time: `00:10.0`, msg: "Multimodal extraction & Semantic Fusion complete" });
          setExtractionLogs(newLogs);

          setElementsFound([
            { label: "Charts", count: 0 },
            { label: "Tables", count: 0 },
            { label: "Graphs", count: 0 },
            { label: "Total Elements", count: (elementsInfo.pages || 0) + (elementsInfo.references || 0) },
            { label: "Pages Scanned", count: elementsInfo.pages || 0 },
            { label: "References", count: elementsInfo.references || 0 },
          ]);
          setIsPdfUploaded(true);

          try {
            const existingUploads = JSON.parse(localStorage.getItem("recent_uploads") || "[]");
            const totalElements = (elementsInfo.pages || 0) + (elementsInfo.references || 0);
            const newUpload = {
              title: validFiles.length > 1 ? `${validFiles.length} Documents Segmented` : validFiles[0].name,
              domain: backendKeywords.length > 0 ? backendKeywords[0] : "General Analysis",
              elements: totalElements,
              references: elementsInfo.references || 0,
              progress: Math.min(Math.round((totalElements / 50) * 100), 100),
              papers: validFiles.length
            };
            localStorage.setItem("recent_uploads", JSON.stringify([...existingUploads, newUpload]));
          } catch(e) {
            console.error("Storage Error", e);
          }

        } catch (e) {
          localStorage.setItem("pdf_keywords", JSON.stringify([]));
          setExtractedText("");
        }
      } else {
        const errorText = await res.text().catch(() => "");
        console.error("Upload failed", res.status, errorText);
        alert(`Upload failed (${res.status}). Check backend server and try again.`);
        setFiles([]);
      }
    } catch (err) {
      console.error("Upload error", err);
      alert("Upload request failed. Ensure backend is running on port 8001 or 8000.");
      setFiles([]);
    } finally {
      setIsUploading(false);
    }
  };

  const flushDrive = async () => {
    localStorage.removeItem("dataset_summary");
    localStorage.removeItem("hasActiveScan");
    localStorage.removeItem("active_keywords");
    localStorage.removeItem("active_docs");
    localStorage.removeItem("active_images");
    localStorage.removeItem("pdf_upload_time");
    setIsPdfUploaded(false);
    setIsCsvUploaded(false);
    setIsScanning(false);
    setFiles([]);
    setExtractedText("");
    setCurrentBoxes([]);
    setElementsFound([{ label: "Total Elements", count: 0 }]);
    setExtractionLogs([]);
    try {
      await postWithFallback("/reset", { method: "POST" });
      alert("Reactor Core Flushed. Data streams purged.");
    } catch(e) {
      alert("Backend flush failed.");
    }
  };

  return (
    <div className="min-h-screen bg-obsidian pt-24 px-6 pb-12">
      <div className="max-w-6xl mx-auto">
        <div className="mb-10 text-center relative">
          <h1 className="text-crimson font-display text-5xl font-bold tracking-tight mb-3">
            Multimodal Vision
          </h1>
          <p className="text-bone/40 font-mono text-sm">
            Laser-scanning documents · Extracting visual elements · Building connections
          </p>
          <button onClick={flushDrive} className="absolute top-0 right-0 p-2 border border-crimson/50 text-crimson hover:bg-crimson/10 rounded font-mono text-xs flex items-center gap-2 transition-colors">
            <Trash2 className="w-4 h-4" />
            Purge Reactor Memory
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* PDF Viewer - Center */}
          <div className="lg:col-span-2">
            <FloatingPanel z={50} className="relative overflow-hidden border border-crimson">
              <input
                type="file"
                accept=".pdf"
                multiple
                ref={fileInputRef}
                onChange={handleFileSelect}
                className="hidden"
              />
              <input
                type="file"
                accept=".csv"
                multiple
                ref={csvInputRef}
                onChange={handleCsvSelect}
                className="hidden"
              />
              
              <div className="flex w-full border-b border-crimson/20">
                <div
                  className={`flex-1 p-6 flex flex-col items-center justify-center transition-colors cursor-pointer border-r border-crimson/30 hover:bg-black/5 ${isPdfUploaded ? 'bg-black/5' : ''}`}
                  onClick={() => !isPdfUploaded && !isUploading && fileInputRef.current?.click()}
                >
                  {isPdfUploaded ? (
                    <>
                      <CheckCircle className="w-8 h-8 mb-2 text-crimson" />
                      <h3 className="text-pure-black font-display text-lg font-bold mb-1 text-center">✅ PDF Uploaded</h3>
                    </>
                  ) : (
                    <>
                      <UploadCloud className="w-8 h-8 mb-2 text-crimson" />
                      <h3 className="text-pure-black font-display text-lg font-bold mb-1 text-center">Upload Literature (PDF)</h3>
                      <p className="text-pure-black/60 font-mono text-[10px] text-center">Extract qualitative data.</p>
                    </>
                  )}
                </div>
                <div
                  className={`flex-1 p-6 flex flex-col items-center justify-center transition-colors cursor-pointer hover:bg-black/5 ${isCsvUploaded ? 'bg-black/5' : ''}`}
                  onClick={() => !isCsvUploaded && !isUploading && csvInputRef.current?.click()}
                >
                  {isCsvUploaded ? (
                    <>
                      <CheckCircle className="w-8 h-8 mb-2 text-cyan-400" />
                      <h3 className="text-pure-black font-display text-lg font-bold mb-1 text-center">✅ CSV Uploaded</h3>
                    </>
                  ) : (
                    <>
                      <UploadCloud className="w-8 h-8 mb-2 text-cyan-400" />
                      <h3 className="text-pure-black font-display text-lg font-bold mb-1 text-center">Upload Dataset (CSV)</h3>
                      <p className="text-pure-black/60 font-mono text-[10px] text-center">Extract quantitative empirical data.</p>
                    </>
                  )}
                </div>
              </div>

              {isPdfUploaded && (
                <div className="p-4 border-b border-crimson/20 flex items-center gap-3 relative z-10 bg-black/5">
                  <FileText className="w-4 h-4 text-pure-black/50" />
                  <span className="text-pure-black font-mono text-xs">{files.map(f => f.name).join(", ") || "multi_modal_synthesis_2024.pdf"}</span>
                  <div className="ml-auto flex items-center gap-2">
                    <ScanLine className={`w-4 h-4 text-crimson ${isScanning ? "animate-pulse" : ""}`} />
                    <span className="text-crimson font-mono text-xs">{isScanning ? "Scanning..." : "Processing..."}</span>
                  </div>
                </div>
              )}

              <div className="relative p-6 min-h-[400px] font-mono text-xs leading-relaxed text-pure-black/70">
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
                        {highlightWord && extractedText.toLowerCase().includes(highlightWord.toLowerCase()) 
                          ? extractedText.split(new RegExp(`(${highlightWord})`, 'gi')).map((part, i) => 
                              part.toLowerCase() === highlightWord.toLowerCase() 
                                ? <mark key={i} className="bg-crimson/30 text-crimson font-bold rounded px-1">{part}</mark> 
                                : part
                            ) 
                          : extractedText}
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
{/* REMOVED UNBALANCED TAGS */}
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
