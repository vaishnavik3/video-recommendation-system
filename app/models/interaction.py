from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(String(50), ForeignKey("posts.id"))
    interaction_type = Column(String(20))
    timestamp = Column(DateTime)
    weight = Column(Float)