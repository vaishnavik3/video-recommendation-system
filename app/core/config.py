from pydantic import BaseSettings

class Settings(BaseSettings):
    flic_token: str
    api_base_url: str
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"

settings = Settings()