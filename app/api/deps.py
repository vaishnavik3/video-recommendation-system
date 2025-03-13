from fastapi import Depends, HTTPException, Header
from app.core.database import get_db
from app.services.recommender import NeuralRecommender
from app.services.data_ingester import DataIngester
from sqlalchemy.orm import Session

# Database dependency
def get_database(session: Session = Depends(get_db)):
    return session

# Authentication dependency
async def verify_token(flic_token: str = Header(...)):
    if flic_token != os.getenv("FLIC_TOKEN"):
        raise HTTPException(status_code=403, detail="Invalid authentication token")
    return flic_token

# Recommender service dependency
def get_recommender():
    return NeuralRecommender()

# Data ingester dependency
def get_ingester():
    return DataIngester()