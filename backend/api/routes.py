import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
from tools.pdf_parser import parse_pdf
from agents.swarm import SwarmOrchestrator

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
        
        async def run_swarm_task(topic, text_context):
            nonlocal active_orchestrator
            async def log_adapter(msg_str: str):
                await manager.broadcast(json.loads(msg_str))
                
            active_orchestrator = SwarmOrchestrator(log_callback=log_adapter)
            try:
                report, gamma_score = await active_orchestrator.run_swarm(discovery_gap_data={"context": text_context}, topic=topic)
                await manager.broadcast({
                    "type": "final_report",
                    "agent": "System",
                    "content": report,
                    "gamma_score": gamma_score
                })
            except Exception as e:
                await manager.broadcast({"agent": "System", "message": f"Swarm Generator Error: {str(e)}"})
            finally:
                active_orchestrator = None

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("type") == "start":
                topic = msg.get("topic", "the provided research document")
                text_context = PROCESSED_DATA.get("text", "")
                
                if not text_context:
                    await websocket.send_json({"agent": "System", "message": "Please upload a file first."})
                    continue
                
                # Mount the swarm engine fully asynchronously in the background
                asyncio.create_task(run_swarm_task(topic, text_context))
                
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