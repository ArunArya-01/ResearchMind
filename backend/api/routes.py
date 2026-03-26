import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
import json
import math
import random
from typing import List, Any
from tools.pdf_parser import parse_pdf
from agents.swarm import SwarmOrchestrator

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass
                
manager = ConnectionManager()

@router.websocket("/ws/swarm")
async def websocket_swarm_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({"agent": "System", "message": "Connected to Swarm."}))
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("command") == "start":
                    topic = msg.get("topic", "Unknown Topic")
                    gap_data = msg.get("gap_data", {"red_anomalies": [{"id": "mock", "data": "mock_data"}]})
                    
                    orchestrator = SwarmOrchestrator(log_callback=manager.broadcast)
                    asyncio.create_task(orchestrator.run_swarm(gap_data, topic))
                else:
                    await manager.broadcast(json.dumps({"agent": "System", "message": f"Unknown command: {msg.get('command')}"}))
            except json.JSONDecodeError:
                await manager.broadcast(json.dumps({"agent": "System", "message": f"Echo: {data}"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    json_result = parse_pdf(contents)
    return {"status": "success", "data": json_result}

@router.get("/nodes")
async def get_nodes():
    count = 200
    nodes: List[dict[str, Any]] = []
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
    return nodes
