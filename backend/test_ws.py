import asyncio
import websockets
import json

async def test_swarm_websocket():
    uri = "ws://localhost:8000/ws/swarm"
    try:
        async with websockets.connect(uri) as websocket:
            # Receive initial connection message
            response = await websocket.recv()
            print(f"Initial: {response}")
            
            # Send start command
            cmd = {
                "command": "start",
                "topic": "Quantum Machine Learning",
                "gap_data": {"red_anomalies": [{"id": "n1", "data": "Isolation detected in Tensor Networks"}]}
            }
            await websocket.send(json.dumps(cmd))
            
            # Receive streamed logs
            for _ in range(5):
                response = await websocket.recv()
                print(f"Log: {response}")
                
    except Exception as e:
        print(f"WebSocket test exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_swarm_websocket())
