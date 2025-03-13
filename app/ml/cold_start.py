from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Post

class ColdStartHandler:
    def __init__(self):
        self.db = next(get_db())
        
    def get_fallback_recommendations(self, user_id: int, category: int = None):
        """Hybrid fallback strategy"""
        query = self.db.query(Post)
        
        # Filter by category if specified
        if category:
            query = query.filter(Post.category_id == category)
            
        # Get popular posts (combination of likes and recency)
        popular = query.order_by(
            (Post.likes * 0.7 + Post.views * 0.3) * 
            (1 / (Post.created_at - datetime.now()).days)
        ).limit(100).all()
        
        # Get trending content (recent engagement)
        trending = query.order_by(
            Post.created_at.desc() * 
            (Post.likes_last_24h + Post.comments_last_24h)
        ).limit(50).all()
        
        # Combine and deduplicate
        combined = {p.id: p for p in popular + trending}.values()
        return sorted(combined, key=lambda x: x.engagement_score, reverse=True)[:100]

    def handle_new_user(self, mood: str = None):
        """Mood-based initial recommendations"""
        mood_mapping = {
            'happy': [5, 7, 12],  # Example category IDs
            'serious': [3, 9],
            'creative': [2, 8]
        }
        
        categories = mood_mapping.get(mood, [5, 3, 2])  # Default categories
        return self.get_fallback_recommendations(None, category=random.choice(categories))