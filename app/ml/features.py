import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User, Post, Interaction

class FeatureEngineer:
    def __init__(self):
        self.user_scaler = StandardScaler()
        self.post_scaler = StandardScaler()
        self.category_encoder = OneHotEncoder()
        self.imputer = SimpleImputer(strategy='mean')
        
    def get_user_features(self, user_id: int, db: Session):
        """Combines user metadata and interaction history"""
        user = db.query(User).filter(User.id == user_id).first()
        interactions = db.query(Interaction).filter(Interaction.user_id == user_id)
        
        # Basic features
        features = {
            'account_age_days': (pd.Timestamp.now() - user.created_at).days,
            'avg_rating': self.imputer.fit_transform([[interaction.weight] 
                            for interaction in interactions]).mean(),
            'total_interactions': interactions.count()
        }
        
        # Normalize numerical features
        numerical = np.array([features['account_age_days'], 
                             features['avg_rating']]).reshape(1, -1)
        features['normalized'] = self.user_scaler.fit_transform(numerical)[0]
        
        return features

    def get_post_features(self, post_id: str, db: Session):
        """Combines content features and engagement metrics"""
        post = db.query(Post).filter(Post.id == post_id).first()
        interactions = db.query(Interaction).filter(Interaction.post_id == post_id)
        
        features = {
            'category_id': post.category_id,
            'days_since_posted': (pd.Timestamp.now() - post.created_at).days,
            'avg_rating': self.imputer.fit_transform([[i.weight] 
                            for i in interactions]).mean(),
            'engagement_score': interactions.count() * 0.5 + 
                              post.likes * 0.3 + post.views * 0.2
        }
        
        # Encode categorical features
        category_encoded = self.category_encoder.fit_transform(
            [[features['category_id']]).toarray()[0]
        
        return np.concatenate([
            [features['days_since_posted']],
            category_encoded,
            [features['engagement_score']]
        ])