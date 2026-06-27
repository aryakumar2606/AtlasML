from fastapi import FastAPI
from backend.api.upload import router as upload_router

app = FastAPI(
    title="AtlasML",
    description="Autonomous Machine Learning Research Scientist",
    version="1.0.0"
)

app.include_router(upload_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to AtlasML 🚀"
    }

@app.get("/health")
def health():
    return {
        "status": "running",
        "version": "1.0.0"
    }