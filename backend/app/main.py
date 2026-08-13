from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router

app = FastAPI(
    title="DevMatch AI Backend",
    description="Intelligent Developer Allocation & Client Management Platform API",
    version="0.1.0",
)

app.include_router(api_router)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "app": "DevMatch AI API",
        "version": "0.1.0",
        "status": "online",
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    # Basic check to verify service is running
    return {
        "status": "healthy"
    }

