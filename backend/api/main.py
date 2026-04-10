import os
from dotenv import load_dotenv

def _load_project_env() -> None:
    # Load local cwd env first, then walk upward from this file to find repo-level .env
    load_dotenv()
    current = os.path.abspath(os.path.dirname(__file__))
    for _ in range(4):
        env_path = os.path.join(current, ".env")
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path, override=False)
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

_load_project_env()
print(f"API Key Loaded: {bool(os.getenv('GROQ_API_KEY'))}")
print(f"GOOGLE_API_KEY Loaded: {bool(os.getenv('GOOGLE_API_KEY'))}")
if not os.getenv('GROQ_API_KEY'):
    print("ERROR: GROQ_API_KEY not detected in environment.")
if not os.getenv('GOOGLE_API_KEY'):
    print("ERROR: GOOGLE_API_KEY not detected in environment.")

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

os.makedirs("data/crops", exist_ok=True)

try:
    # Works when running from backend/ with: uvicorn api.main:app
    from api.routes import router
except ModuleNotFoundError:
    # Works when running from repo root with: uvicorn backend.api.main:app
    from backend.api.routes import router

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
