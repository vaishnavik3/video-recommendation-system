from sqlalchemy import Column, String, Integer, ARRAY, Float
from .base import Base

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(String(50), primary_key=True)
    title = Column(String(200))
    category_id = Column(Integer)
    embeddings = Column(ARRAY(Float))