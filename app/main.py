from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, entities, chat  # ✅ Changed tasks → entities
from app.config import settings

app = FastAPI(
    title="AI Personal Mentor API",
    version="2.0.0", 
    description="Backend for AI Personal Mentor application"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(entities.router, prefix="/api/v1")  # ✅ Changed
app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "AI Personal Mentor API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}