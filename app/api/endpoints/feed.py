from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from fastapi_cache.decorator import cache
from app.services.recommender import NeuralRecommender
from app.core.dependencies import get_recommender, get_user_data

router = APIRouter()

@router.get("/feed")
@cache(expire=300)
async def get_feed(
    username: str = Query(...),
    category_id: Optional[str] = Query(None),
    limit: int = Query(5, ge=1, le=50),
    page: int = Query(1, ge=1),
    user_data: dict = Depends(get_user_data)
):
    try:
        # Original recommendation logic
        viewed = user_data.get("viewed", {}).get("posts", [])
        liked = user_data.get("liked", {}).get("posts", [])
        
        combined = viewed + liked
        filtered = [p for p in combined if not category_id or p.get("category_id") == category_id]
        
        return {
            "username": username,
            "recommendations": filtered[(page-1)*limit : page*limit],
            "total": len(filtered)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Recommendation failed: {str(e)}")

@router.get("/feed/ml")
async def get_ml_feed(
    username: str = Query(...),
    category_id: Optional[str] = None,
    use_fallback: bool = Query(False),
    recommender: NeuralRecommender = Depends(get_recommender)
):
    try:
        if use_fallback:
            return await get_feed(username, category_id)
            
        # ML-based recommendations
        recommendations = await recommender.get_recommendations(
            username=username,
            category=category_id
        )
        
        return {
            "user": username,
            "recommendations": recommendations,
            "model": "dnn-v1"
        }
    
    except Exception as e:
        return await get_feed(username, category_id)