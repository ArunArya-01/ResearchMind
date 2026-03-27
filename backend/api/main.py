import os
from dotenv import load_dotenv

load_dotenv()
print(f"API Key Loaded: {bool(os.getenv('GOOGLE_API_KEY'))}")
if not os.getenv('GOOGLE_API_KEY'):
    print("ERROR: GOOGLE_API_KEY not detected in environment.")

from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="ResearchMind Backend",
    description="High-performance backend supporting Multimodal Agentic Swarm",
    version="1.0.0"
)

# CORSMiddleware removed to allow Go Gateway to handle CORS headers

app.include_router(router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "ResearchMind Swarm Backend Active"}
