from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import agent_router, approval_router
from config.settings import settings

app = FastAPI(
    title="AI Email & Calendar Assistant API",
    description="Autonomous Agentic Executive Assistant API powered by LangGraph & OpenRouter",
    version="1.0.0"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(agent_router)
app.include_router(approval_router)

@app.get("/health", tags=["Health Check"])
def health_check():
    """Health check endpoint for API status verification."""
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "model": settings.OPENROUTER_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
