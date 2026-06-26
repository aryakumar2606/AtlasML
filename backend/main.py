from fastapi import FastAPI

app = FastAPI(
    title="AtlasML",
    description="Autonomous Machine Learning Research Scientist",
    version="1.0.0"
)

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