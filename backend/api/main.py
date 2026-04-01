import os
from dotenv import load_dotenv

load_dotenv()
print(f"API Key Loaded: {bool(os.getenv('GOOGLE_API_KEY'))}")
if not os.getenv('GOOGLE_API_KEY'):
    print("ERROR: GOOGLE_API_KEY not detected in environment.")

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

os.makedirs("data/crops", exist_ok=True)

from api.routes import router

app = FastAPI(
    title="ResearchMind Backend",
    description="High-performance backend supporting Multimodal Agentic Swarm",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

app.mount("/crops", StaticFiles(directory="data/crops"), name="crops")

@app.get("/")
async def root():
    return {"status": "ok", "message": "ResearchMind Swarm Backend Active"}
