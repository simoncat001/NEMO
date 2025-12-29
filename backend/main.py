"""
NEMO FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="NEMO Laboratory Logistics Management System API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    # For local preview, allow the Vite dev server.
    # You can tighten this in production via BACKEND_CORS_ORIGINS.
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "NEMO FastAPI Backend",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
