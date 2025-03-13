from fastapi import Depends
from fastapi_cache.decorator import cache
from app.core.database import get_db
from app.ml.model import RecSysNN
from app.ml.cold_start import ColdStartHandler
from app.ml.features import FeatureEngineer

class NeuralRecommender:
    def __init__(self):
        self.model = RecSysNN()
        self.model.load_state_dict(torch.load("recsys_dnn.pth"))
        self.model.eval()
        self.fe = FeatureEngineer()
        self.cold_start = ColdStartHandler()
    
    @cache(expire=3600)
    async def get_recommendations(self, user_id: int, category: int = None):
        db = next(get_db())
        
        # Check cold start condition
        interactions = db.query(Interaction).filter(Interaction.user_id == user_id).count()
        if interactions < 5:
            return self.cold_start.handle_new_user()
        
        # Get candidate posts
        query = db.query(Post)
        if category:
            query = query.filter(Post.category_id == category)
        candidates = query.limit(1000).all()
        
        # Batch predict
        with torch.no_grad():
            user_feats = self.fe.get_user_features(user_id, db)
            scores = []
            
            for post in candidates:
                post_feats = self.fe.get_post_features(post.id, db)
                score = self.model(
                    torch.FloatTensor(user_feats),
                    torch.FloatTensor(post_feats)
                )
                scores.append((post, score.item()))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)[:100]