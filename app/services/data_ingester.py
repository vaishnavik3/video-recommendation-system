import requests
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.config import settings
from app.models import User, Post, Interaction

class DataIngester:
    def __init__(self, db: Session):
        self.db = db
        self.headers = {"Flic-Token": settings.FLIC_TOKEN}
        
    def _fetch_paginated_data(self, url):
        results = []
        page = 1
        while True:
            response = requests.get(
                f"{url}&page={page}", 
                headers=self.headers
            )
            if response.status_code != 200:
                break
            results.extend(response.json()['posts'])
            if len(response.json()['posts']) < 1000:
                break
            page += 1
        return results
    
    def _update_users(self, users_data):
        for user in users_data:
            db_user = self.db.query(User).filter(User.id == user['id']).first()
            if not db_user:
                db_user = User(**user)
                self.db.add(db_user)
    
    def _update_posts(self, posts_data):
        for post in posts_data:
            db_post = self.db.query(Post).filter(Post.id == post['id']).first()
            if not db_post:
                db_post = Post(**post)
                self.db.add(db_post)
    
    def ingest_all(self):
        # Ingest users
        users_data = self._fetch_paginated_data(settings.USERS_GET_ALL_URL)
        self._update_users(users_data)
        
        # Ingest posts and interactions
        for endpoint in ['viewed', 'liked', 'inspired', 'rated']:
            posts = self._fetch_paginated_data(
                getattr(settings, f"POSTS_{endpoint.upper()}_URL")
            )
            self._update_posts(posts)
            
            # Create interactions
            for post in posts:
                interaction = Interaction(
                    user_id=post['user_id'],
                    post_id=post['id'],
                    interaction_type=endpoint,
                    timestamp=datetime.now(),
                    weight=post.get('rating', 1.0)
                )
                self.db.add(interaction)
        
        self.db.commit()