import asyncio
import json
import re
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google import genai
import os
from typing import List
try:
    # Works when running from backend/ (api as top-level package)
    from tools.pdf_parser import parse_pdf
    from agents.swarm import SwarmOrchestrator
    from tools.ieee_builder import build_ieee_pdf
except ModuleNotFoundError:
    # Works when running from repo root (backend as top-level package)
    from backend.tools.pdf_parser import parse_pdf
    from backend.agents.swarm import SwarmOrchestrator
    from backend.tools.ieee_builder import build_ieee_pdf
from reportlab.lib.pagesizes import letter
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import pandas as pd
import io

router = APIRouter()

@router.get("/nodes")
async def get_nodes():
    try:
        nodes = []
        links = []
        import math, random
        count = 100
        for i in range(count):
            angle = (i / count) * math.pi * 2 + random.random() * 0.5
            radius = 120 + random.random() * 280
            nodes.append({
                "id": i,
                "x": 400 + math.cos(angle) * radius + (random.random() - 0.5) * 60,
                "y": 300 + math.sin(angle) * radius + (random.random() - 0.5) * 60,
                "size": 2 + random.random() * 4,
                "connections": []
            })
        for i in range(count):
            num_conns = 1 + math.floor(random.random() * 3)
            for j in range(num_conns):
                target = math.floor(random.random() * count)
                if target != i:
                    nodes[i]["connections"].append(target)
                    links.append({"source": i, "target": target})
        return {"nodes": nodes, "links": links}
    except Exception as e:
        return JSONResponse(status_code=200, content={"nodes": [], "links": [], "error": str(e)})

import chromadb
chroma_client = chromadb.PersistentClient(path="./chroma_db")
try:
    collection = chroma_client.get_or_create_collection(name="research_papers")
except Exception:
    collection = chroma_client.create_collection(name="research_papers")

PROCESSED_DATA = {"text": "", "keywords": [], "docs": {}, "images": []}

@router.post("/reset")
async def reset_data():
    global PROCESSED_DATA
    PROCESSED_DATA = {"text": "", "keywords": [], "docs": {}, "images": []}
    
    try:
        chroma_client.delete_collection(name="research_papers")
        global collection
        collection = chroma_client.create_collection(name="research_papers")
    except Exception:
        pass
        
    return {"status": "cleared"}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # We now send JSON objects so the UI can distinguish between agents
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass
                
manager = ConnectionManager()

@router.websocket("/ws/swarm")
async def websocket_swarm_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({"agent": "System", "message": "Neural Swarm Initialized..."})
        
        active_orchestrator = None
        
        async def run_swarm_task(topic, text_context, dataset_summary):
            nonlocal active_orchestrator
            async def log_adapter(msg_str: str):
                await manager.broadcast(json.loads(msg_str))
                
            active_orchestrator = SwarmOrchestrator(log_callback=log_adapter)
            try:
                report_data = await active_orchestrator.run_swarm(discovery_gap_data={"context": text_context}, topic=topic, dataset_summary=dataset_summary)
                await manager.broadcast({
                    "type": "final_report",
                    "agent": "System",
                    "content": report_data.get("discovery_report", ""),
                    "discovery_report": report_data.get("discovery_report", ""),
                    "ieee_manuscript": report_data.get("ieee_manuscript", ""),
                    "gamma_score": report_data.get("gamma_score", 0.0)
                })
            except Exception as e:
                err_msg = str(e)
                if "[FUSION_TERMINATED]" in err_msg:
                    await manager.broadcast({
                        "status": "error",
                        "agent": "System",
                        "message": "FUSION TERMINATED: Spurious correlation detected. The uploaded dataset lacks a scientific causal link to benchmark the provided theory."
                    })
                else:
                    await manager.broadcast({"agent": "System", "message": f"Swarm Generator Error: {err_msg}"})
            finally:
                active_orchestrator = None

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("type") == "start":
                topic = msg.get("topic", "the provided research document")
                dataset_summary = msg.get("dataset_summary", "")
                text_context = PROCESSED_DATA.get("text", "")
                
                if not text_context and not dataset_summary:
                    await websocket.send_json({"agent": "System", "message": "Please upload a file or dataset first."})
                    continue
                
                # Mount the swarm engine fully asynchronously in the background
                asyncio.create_task(run_swarm_task(topic, text_context, dataset_summary))
                
            elif msg.get("type") == "director_override":
                cmd = msg.get("command", "")
                if active_orchestrator and cmd:
                    active_orchestrator.inject_override(cmd)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/upload/pdf")
async def upload_pdf(files: List[UploadFile] = File(...)):
    global PROCESSED_DATA
    PROCESSED_DATA = {"text": "", "keywords": [], "docs": {}, "images": []}
    
    # reset collection on new batch upload
    try:
        chroma_client.delete_collection(name="research_papers")
        global collection
        collection = chroma_client.create_collection(name="research_papers")
    except Exception:
        pass
        
    import os
    os.makedirs('data', exist_ok=True)
    
    all_text = ""
    all_keywords = set()
    all_docs = {}
    all_images = []
    total_pages = 0
    total_refs = 0
    
    for file in files:
        contents = await file.read()
        filename = file.filename
        
        with open(f'data/{filename}', 'wb') as f:
            f.write(contents)
            
        json_result = parse_pdf(contents)
        doc_text = json_result.get("text", "")
        doc_keywords = json_result.get("keywords", [])
        doc_images = json_result.get("images", [])
        
        all_text += f"\n\n=== {filename} ===\n\n{doc_text}"
        all_keywords.update(doc_keywords)
        all_docs[filename] = doc_keywords
        all_images.extend(doc_images)
        
        elements = json_result.get("elements", {})
        total_pages += elements.get("pages", 0)
        total_refs += elements.get("references", 0)
        
        chunks = [doc_text[i:i+1000] for i in range(0, len(doc_text), 1000) if len(doc_text[i:i+1000].strip()) > 50]
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source_doc": filename} for _ in chunks]
        
        if chunks:
            collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
    aggregated_keywords = list(all_keywords)[:15]
    PROCESSED_DATA["text"] = all_text
    PROCESSED_DATA["keywords"] = aggregated_keywords
    PROCESSED_DATA["docs"] = all_docs
    PROCESSED_DATA["images"] = all_images
    
    return {
        "status": "success", 
        "data": {
            "text": all_text,
            "keywords": aggregated_keywords,
            "docs": all_docs,
            "images": all_images,
            "elements": {
                "pages": total_pages,
                "references": total_refs
            }
        }
    }

class PDFRequest(BaseModel):
    markdown_content: str

@router.post("/upload-dataset")
async def upload_dataset(files: List[UploadFile] = File(...)):
    summaries = []
    for file in files:
        contents = await file.read()
        try:
            df = pd.read_csv(io.BytesIO(contents))
            summary_str = f"Dataset: {file.filename}\\nRows: {df.shape[0]}, Columns: {df.shape[1]}\\n"
            summary_str += "Columns: " + ", ".join(df.columns.tolist()) + "\\n"
            summary_str += df.describe().to_string()
            summaries.append(summary_str)
        except Exception as e:
            summaries.append(f"Failed to parse {file.filename}: {e}")
            
    return {"status": "success", "summary": "\\n\\n".join(summaries)}

@router.post("/download/discovery-report")
async def generate_discovery_report(req: PDFRequest):
    return Response(
        content=req.markdown_content.encode('utf-8'),
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=Discovery_Report.md"}
    )


@router.post("/download/ieee-pdf")
async def generate_ieee_pdf(req: PDFRequest):
    try:
        # STEP 1: GHOSTWRITE THE ACADEMIC PAPER
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        prompt = f"""
        You are a PhD-level academic ghostwriter. 
        I will provide you with a raw 'Discovery Report' containing a hypothesis generated by an AI Swarm.
        
        Your task: Write a highly formal, strictly formatted academic research paper based on the Swarm's findings. Ensure the content is novel, deeply technical, and avoids generic filler.
        
        You MUST format the output EXACTLY like this using Markdown:
        
        # [Insert a highly academic, professional Title]
        
        **Abstract**—[Write a 200-word comprehensive abstract summarizing the problem, proposed methodology, and expected impact. Start exactly with the bold word 'Abstract' followed by an em-dash.]
        
        ## I. INTRODUCTION
        [Write the introduction...]
        
        ## II. PROBLEM STATEMENT
        [Detail the core problem and limitations of current approaches...]
        
        ## III. OBJECTIVES
        [List the primary objectives of this proposed research...]
        
        ## IV. LITERATURE REVIEW
        [Synthesize a theoretical background based on the domains discussed in the report...]
        
        ## V. METHODOLOGY
        [Detail the theoretical or empirical methodology proposed to test the hypothesis...]
        
        ## VI. IMPLEMENTATION
        [Describe the technical architecture, algorithms, or physical setup required...]
        
        ## VII. CONCLUSION
        [Summarize the findings and future scope...]
        
        ## VIII. REFERENCES
        [Generate 3 to 5 plausible, highly relevant academic references formatted strictly in IEEE citation style (e.g., [1] A. Smith, "Title", Journal, Year.)]
        
        Here is the raw Discovery Report to base the paper on:
        {req.markdown_content}
        """
        
        response = await client.aio.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        academic_paper_text = response.text
        
        # STEP 2: FORMAT INTO 2-COLUMN IEEE PDF
        buffer = io.BytesIO()
        doc = BaseDocTemplate(buffer, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
        frameWidth = (doc.width / 2.0) - 0.125*inch
        left_frame = Frame(doc.leftMargin, doc.bottomMargin, frameWidth, doc.height, id='left')
        right_frame = Frame(doc.leftMargin + frameWidth + 0.25*inch, doc.bottomMargin, frameWidth, doc.height, id='right')
        doc.addPageTemplates([PageTemplate(id='TwoCol', frames=[left_frame, right_frame])])

        # --- REPORTLAB STYLING ---
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('IEEETitle', parent=styles['Normal'], fontName='Times-Bold', fontSize=16, leading=20, spaceAfter=24, alignment=1) # Centered, large
        abstract_style = ParagraphStyle('IEEEAbstract', parent=styles['Normal'], fontName='Times-BoldItalic', fontSize=9, leading=11, spaceAfter=14, alignment=4, leftIndent=0.1*inch, rightIndent=0.1*inch)
        h1_style = ParagraphStyle('IEEEH1', parent=styles['Normal'], fontName='Times-Bold', fontSize=10, leading=12, spaceBefore=12, spaceAfter=6, alignment=1, textTransform='uppercase')
        body_style = ParagraphStyle('IEEEBody', parent=styles['Normal'], fontName='Times-Roman', fontSize=10, leading=12, spaceAfter=8, alignment=4, firstLineIndent=0.15*inch)
        ref_style = ParagraphStyle('IEEERef', parent=styles['Normal'], fontName='Times-Roman', fontSize=9, leading=11, spaceAfter=4, alignment=4)

        story = []
        lines = academic_paper_text.split('\n')
        
        # --- REPORTLAB PARSING ---
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Convert bold text for ReportLab
            clean_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            
            if clean_line.startswith('# '):
                story.append(Paragraph(clean_line.replace('# ', ''), title_style))
            elif clean_line.startswith('<b>Abstract</b>') or clean_line.startswith('**Abstract**'):
                story.append(Paragraph(clean_line, abstract_style))
            elif clean_line.startswith('## '):
                story.append(Paragraph(clean_line.replace('## ', ''), h1_style))
            elif clean_line.startswith('[') and ']' in clean_line[:5]: 
                # Catch references like [1], [2]
                story.append(Paragraph(clean_line, ref_style))
            elif clean_line.startswith('- ') or clean_line.startswith('* '):
                story.append(Paragraph(clean_line, body_style))
            elif not clean_line.startswith('```') and not clean_line.startswith('graph'):
                story.append(Paragraph(clean_line, body_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=IEEE_Manuscript.pdf"}
        )
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
