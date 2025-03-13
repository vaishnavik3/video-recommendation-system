# main.py (root directory)
from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis
from app.core.config import settings
from app.api.endpoints import feed, health
from app.services.data_ingester import DataIngester
from app.models.base import Base
from app.core.database import engine

# Create database tables (for development only)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SocialVerse Recommendation Engine",
    description="Hybrid recommendation system combining rules and DNN",
    version="2.0"
)

# Include API routers
app.include_router(feed.router, prefix="/api/v1")
app.include_router(health.router)

@app.on_event("startup")
async def startup_event():
    # Initialize Redis cache
    redis_client = redis.from_url(settings.redis_url)
    FastAPICache.init(RedisBackend(redis_client), prefix="sv-recommendations")
    
    # Initial data ingestion (for demonstration)
    # In production, use a proper scheduler like Celery
    try:
        ingester = DataIngester()
        ingester.ingest_all()
    except Exception as e:
        print(f"Initial data ingestion failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "SocialVerse Recommendation API",
        "documentation": "/docs",
        "status": "operational"
    }