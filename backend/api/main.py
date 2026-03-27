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
