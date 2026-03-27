import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
from typing import List
from tools.pdf_parser import parse_pdf
from agents.swarm import SwarmOrchestrator

router = APIRouter()

PROCESSED_DATA = {}

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
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("command") == "start":
                topic = msg.get("topic", "General Research")
                
                # Run real orchestrator
                text_context = PROCESSED_DATA.get("text", "")
                
                if not text_context:
                    await websocket.send_json({"agent": "System", "message": "Error: No manuscript data found. Please upload a PDF first."})
                    continue
                
                async def log_adapter(msg_str: str):
                    await manager.broadcast(json.loads(msg_str))
                    
                orchestrator = SwarmOrchestrator(log_callback=log_adapter)
                report = await orchestrator.run_swarm(discovery_gap_data={"context": text_context}, topic=topic)
                
                # 3. SEND THE FINAL MANUSCRIPT (The Output)
                await manager.broadcast({
                    "type": "final_report",
                    "agent": "System",
                    "content": report
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    
    import os
    os.makedirs('data', exist_ok=True)
    with open(f'data/{file.filename}', 'wb') as f:
        f.write(contents)
        
    # This triggers your tool/pdf_parser.py
    json_result = parse_pdf(contents)
    PROCESSED_DATA["text"] = json_result.get("text", "")
    
    return {"status": "success", "data": json_result}