from fastapi import APIRouter
from redis import Redis
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    try:
        # Test Redis connection
        redis_client = Redis.from_url(settings.redis_url)
        redis_client.ping()
        
        # Test DB connection
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        
        return {"status": "healthy", "services": ["redis", "postgres"]}
    
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}