from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.routes import api
from app.database.neo4j_conn import driver
from app.services.ingestion import ingest_all

app = FastAPI(title="Graph Query System", version="1.0.0")

# ========== CORS (Allow frontend connection) ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== LOAD ENV ==========
load_dotenv()

# ========== ROUTES ==========
app.include_router(api.router, prefix="/api", tags=["chat"])

# ========== HEALTH CHECK ==========
@app.get("/")
def home():
    return {
        "message": "Graph Query System API",
        "docs": "/docs",
        "endpoints": {
            "chat": "POST /api/chat",
            "graph": "GET /api/graph",
            "init": "POST /api/init"
        }
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/init")
def initialize_graph():
    """Initialize graph with data from JSONL files"""
    try:
        print("🚀 Starting data ingestion...")
        ingest_all()
        return {"status": "success", "message": "Graph initialized with data"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
